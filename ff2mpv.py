#!/usr/bin/env python3

import sys
import struct
import json
from subprocess import Popen, DEVNULL


def main():
    message = get_message()
    url = message.get("url")
    args = ["mpv", "--no-terminal", "--", url]
    Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    # Need to respond something to avoid "Error: An unexpected error occurred"
    # in Browser Console.
    send_message("ok")


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
