# JFPatch as a service examples

## Introduction

This repository contains some examples of how the JFPatch tool works, and an example
command line tool to use it. The JFPatch service, at https://jfpatch.riscos.online/,
provides a JSON API and a WebSockets API to perform builds.

## Documentation

The API documentation can be found at https://jfpatch.riscos.online/api.html.

The JFPatch file format documentation cen be found at https://jfpatch.riscos.online/fileformat.html.

## Example code (jfpatch-files)

Within this repository there are some example JFPatch files which give examples of how the format works
in the form of commands and tools that I wrote some 20 years ago or so. The file type number for JFPatch files is &13C, so all files will have this trailing suffix.

Note: At the current time, the JFPatch tool doesn't actually generate 32bit code, and some of this code
won't be 32bit safe. I just haven't got around to that, what with trying to implement the service and
the general anxiety over doing anything publically and the end of the world. I hope that I'll get the
back end JFPatch updated to create 32bit modules at some point soon.

* `hello-world,13c` - A simple 'hello world' utility.
* `base64,13c` - A simple example module that decodes a Base64 encoded block.
* `batnball,13c` - A sub-256 byte utility to bounce a ball and hit it with a bat.
* `ddeutils,13c` - My implementation of DDEUtils, which I wrote because otherwise you couldn't use throwback or prefixing without buying the Desktop Development Environment.
* `djf,13c` - A tool for playing David's Jingle Format tunes (which apparently only exists on google in reference to software that I wrote).
* `extedit,13c` - A command line tool that can launch an External Editor on a file from within a Taskwindow.
* `extedit-for-c,13c` - An AOF linkable version of the tool (which was used in GMail).
* `nocoverib,13c` - A tool to ensure that windows never cover the iconbar, completing what looks like a feature of the Wimp that never quite worked as I expected.
* `taskkiller,13c` - A tool to allow killing of tasks that wouldn't exit. It worked ok on RISC OS 3.1, thought I have no idea if it worked on later machines. Ugly uses of mode selection means that it's not
going to work on a 32bit system. Plus it probably does some ugly stuff as well.
* `tonedial,13c` - Give it a phone number and it'll play the tones necessary to call it.
* `serialtcp,13c` - Claims to be a way to replace the serial operations with a TCP connection. I have a recollection of playing something like Chocks Away with it, but honestly that could be my memory playing
tricks on me. There's a very real possibility that I wrote it and never got it to work reliably.
* `patching.zip` - A zip of the 'patching' directory which demonstrates patching a binary.


## Clients


### JSON client example

The JSON service can be triggered by a simple request submitted to the server with the `curl` tool (or
any other tool - this example just shows that it's possible with the `curl` tool). It is necessary to
remove the `,` suffix from the filename when invoking from `curl` because parameters are separated by
them.

Example usage:

    curl -i -F 'source=@djf-source'  http://jfpatch.riscos.online/build/json

Example output:
```
HTTP/1.1 100 Continue

HTTP/1.1 200 OK
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
Server: Werkzeug/1.0.0 Python/2.7.17
Date: Sun, 29 Mar 2020 23:08:16 GMT
X-Cache: Miss from cloudfront
Via: 1.1 67ef3abac0a476e3c8690ff0f09febb8.cloudfront.net (CloudFront)
X-Amz-Cf-Pop: LHR62-C3
X-Amz-Cf-Id: uXBMcPw9hkYlVFSBSKucwBLHQ3ms8_owGMFSbmC_nekXDFapbJvrLw==

{
  "data": "P0At6QFQoOHAAQTvAgug48UBBO8AANXlIABQ47pQj7IAgKDjASDV5CAAUuMgAAC6g0CP4lswj+IBEPTlAAAx4wIAMRH7//8aA0BE4AQxhOADMaDhAzKD4AQwg+ABQNXkIABU4xIAALowQFTi7P//ShdAhAIRAFTjB0BEogRxhOCEQKDhAUBE4gAQoONfADLjBQAAChwgn+UEOIPgCACg4cEBBO8AADDj+///ugeAiODb///qP4C96AEA8f9henN4Y2Z2Z2Juam1rLGwucTJ3M2VyNXQ2eTd1aTlvMHAALjN3NmUydzIuMjI2LDZxNncycTIsMi4zLDJtNAB1",
  "filetype": 4092,
  "messages": [
    "Build tool selected: JFPatch",
    "Return code: 0"
  ],
  "output": [
    "JFPatch ARM assembler v2.56\u00df (02 Mar 2020) [Justin Fletcher]\r\n",
    "Pre-processing...\r\n",
    "Assembling...\r\n"
  ],
  "rc": 0,
  "throwback": []
}
```

## WebSockets client example

The WebSockets interface can be accessed with the Python WebSocket-client library. This can be installed in
your Python environment with the supplied `requirements.txt`.

Example usage:

    python wsclient.py --source ../jfpatch-files/djf,13c

Example output:

```
welcome: u'Linking over Internet with RISCOS Pyromaniac Agent version 1.04'
response: u'Source loaded'
response: u'Started build'
message: u'Build tool selected: JFPatch'
output: u'JFPatch ARM assembler v2.56\xdf (02 Mar 2020) [Justin Fletcher]\r\n'
output: u'Pre-processing...\r\n'
output: u'Assembling...\r\n'
clipboard: {u'filetype': 4092, u'data': u'P0At6QFQoOHAAQTvAgug48UBBO8AANXlIABQ47pQj7IAgKDjASDV5CAAUuMgAAC6g0CP4lswj+IBEPTlAAAx4wIAMRH7//8aA0BE4AQxhOADMaDhAzKD4AQwg+ABQNXkIABU4xIAALowQFTi7P//ShdAhAIRAFTjB0BEogRxhOCEQKDhAUBE4gAQoONfADLjBQAAChwgn+UEOIPgCACg4cEBBO8AADDj+///ugeAiODb///qP4C96AEA8f9henN4Y2Z2Z2Juam1rLGwucTJ3M2VyNXQ2eTd1aTlvMHAALjN3NmUydzIuMjI2LDZxNncycTIsMi4zLDJtNAB1'}
rc: 0
message: u'Return code: 0'
complete: True
```

The tool writes the built binary to the current directory as `built,xxx` unless the `--output-base` option
is supplied (which builds the prefix before the `,xxx` which is always appended).
