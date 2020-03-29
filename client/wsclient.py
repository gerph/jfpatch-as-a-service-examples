#!/usr/bin/env python
"""
WebSocket client for the JFPatch build service.

The WebSocket build protocol is based on messages to and from the server. Like the regular HTTP
protocol, it must be supplied with the source in order to build. This tool handles the requests
in a way that allows a very simple command line invocation of the tool and to obtain its binary
output from the clipboard.

Protocol
--------

The server and client communicate through messages. Each message is a JSON encoded list of two
items.

* The first element (the 'action') of the list indicates how the message should be processed.
* The second element (the 'data') contains any clarifying content for the action. Usually this
  is a string, but it may be a data structure for some actions.

When first connected, the server will send a 'welcome' message.
Each message from the client will be responded to with either a 'response' or 'error' message.
The server may send other messages to the client at any time to explain its progress.


Server actions
--------------

* 'welcome': Introduces the server.
    Data is the server name and version number.

* 'response': Sent as a successful response to an action from the client.
    Data is a string giving an indication of how the action was processed.

* 'error': Sent as an unsuccessful response to an action from the client.
    Data is a message describing the failure.

* 'message': Build management message, sent to explain what the system is doing to manage the
    requested build.
    Data is a string explaining the action. All strings are complete statements, without a
    trailing newline.

* 'output': Text produced by the build process itself.
    Data is a string from the build. Each string may contain RISC OS control characters. The
    strings will be delivered in a timely manner, but may have been concatenated in order
    to reduce protocol overheads.

* 'throwback': Information about a throwback event in the build system.
    Data is a dictionary containing the following keys:
        * 'reason': Throwback reason number (see DDEUtils documentation).
        * 'reason_name': Human readable string for the reason number (or a number if the
            reason does not have a name). Usually 'Processing', 'Error' or 'Info'.
        * 'filename': RISC OS filename to which this event applies.
        * 'lineno': The line number in the given filename to which thie event applies.
        * 'severity': Throwback severity number (see DDEUtils documentation).
        * 'severity_name': Human readable string for the severity number (or a number if the
            severity does not have a name). Usually 'Error', 'Warning' or 'Serious Error'.
        * 'url': A 'riscos' scheme URL for the file and line.
        * 'message': Message reported by this event.

* 'clipboard': Built binary content (this is delivered by a clipboard copy operation internally).
    Data is a dictionary containing the following keys:
        * 'filetype': RISC OS filetype number for the content
        * 'data': Base64 encoded binary data

* 'rc': Return code from the system (usually non-0 if a failure occurred)
    Data is a number, usually 0 or 1, but other return codes may be produced by different tools.
    The environment gives a return code of 125 for a failure with an abort.

* 'complete': Declares the build process complete.
    Data is a True value.


Client actions
--------------

* 'source': Supplies the source code that should be built.
    Data is a base64 encoded source to build.

* 'build': Requests that the build starts.
    Data is ignored.
"""

import argparse
import base64
import json
import os
import sys

from websocket import create_connection


def setup_parser():
    parser = argparse.ArgumentParser(usage="%s [<options>]" % (os.path.basename(sys.argv[0]),))
    parser.add_argument('--source', type=str,
                        help="Source file to build")
    parser.add_argument('--server', type=str, default='jfpatch.riscos.online/ws',
                        help="Server to connect to (default: 'jfpatch.riscos.online/ws')")
    parser.add_argument('--output-base', type=str, default='built',
                        help="Base name of the built binary, if any (default: 'built')")

    return parser


parser = setup_parser()
options = parser.parse_args()

ws = create_connection("ws://{}".format(options.server))

STATE_AWAITWELCOME = 0
STATE_SENDBUILD = 1
STATE_RUNNING = 2
STATE_COMPLETE = 3


filename = options.source
with open(filename) as fh:
    source_data = fh.read()

def send(action, data):
    ws.send(json.dumps([action, data]))


state = STATE_AWAITWELCOME
while state != STATE_COMPLETE:
    result = ws.recv()
    action, data = json.loads(result)
    print("{}: {!r}".format(action, data))

    if action == 'error':
        # Cannot continue if we got an error
        break

    if state == STATE_AWAITWELCOME:
        # Now we send the source we're wanting built
        send('source', base64.b64encode(source_data))
        state = STATE_SENDBUILD

    elif state == STATE_SENDBUILD:
        send('build', None)
        state = STATE_RUNNING

    elif state == STATE_RUNNING:
        if action == 'complete':
            break

        if action == 'clipboard':
            # Received a result from the build, so let's save it
            built = base64.b64decode(data['data'])
            filename = '{},{:03x}'.format(options.output_base, data['filetype'] & 0xFFF)
            with open(filename, 'wb') as fh:
                fh.write(built)

ws.close()
