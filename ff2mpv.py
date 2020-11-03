#!/usr/bin/env python3

import json
import platform
import struct
import sys
from subprocess import Popen, CREATE_BREAKAWAY_FROM_JOB


def main():
    message = get_message()
    url = message.get("url")

    args = ["mpv", "--no-terminal", "--", url]
    kwargs = {}
    if platform.system() == "Windows":
        kwargs["creationflags"] = CREATE_BREAKAWAY_FROM_JOB

    Popen(args, **kwargs)

    if url:
        send_message(url)


# https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging#App_side
def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return {}
    length = struct.unpack("@I", raw_length)[0]
    message = sys.stdin.buffer.read(length).decode("utf-8")
    return json.loads(message)


def send_message(message):
    content = json.dumps(message).encode("utf-8")
    length = struct.pack("@I", len(content))
    sys.stdout.buffer.write(length)
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
