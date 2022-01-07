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

    args = ["mpv", "--", url] # need to remove terminal because it need to capture the output of yt-dlp

    kwargs = {}
    # https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging#Closing_the_native_app
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.CREATE_BREAKAWAY_FROM_JOB

    # HACK(ww): On macOS, graphical applications inherit their path from `launchd`
    # rather than the default path list in `/etc/paths`. `launchd` doesn't include
    # `/usr/local/bin` in its default list, which means that any installations
    # of MPV and/or youtube-dl under that prefix aren't visible when spawning
    # from, say, Firefox. The real fix is to modify `launchd.conf`, but that's
    # invasive and maybe not what users want in the general case.
    # Hence this nasty hack.
    if platform.system() == "Darwin":
        path = os.environ.get("PATH")
        os.environ["PATH"] = f"/usr/local/bin:{path}"

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,**kwargs)
    pOut, pErr = process.communicate() # @see https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
    # Need to respond something to avoid "Error: An unexpected error occurred"
    # in Browser Console.
    if "ERROR" not in str(pOut) :    
        send_message("ok")
    else :
        send_message(pOut.decode("utf-8"))


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
