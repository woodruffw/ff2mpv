#!/usr/bin/env python3

import json
import os
import platform
import struct
import sys
import subprocess


def main():
    message = get_message()
    url = message.get("url")

    new_env = os.environ.copy()
    # HACK: We have to enumerate all possible locations a user may have installed mpv or youtube-dl to on Darwin
    # See https://github.com/woodruffw/ff2mpv/issues/13 for more information
    new_env["PATH"] = f"{new_env['PATH']}:{os.getenv('HOME')}/.nix-profile/bin:/run/current-system/sw/bin:/usr/bin:/usr/local/bin:/opt/bin:/opt/local/bin"

    args = ["mpv", "--no-terminal", "--", url]

    kwargs = {}
    # https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging#Closing_the_native_app
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.CREATE_BREAKAWAY_FROM_JOB

    subprocess.Popen(args, **kwargs, env=new_env)

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
