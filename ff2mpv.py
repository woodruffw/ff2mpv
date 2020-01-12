#!/usr/bin/env python3

import sys
import struct
import json
import tempfile
from subprocess import Popen, DEVNULL


def main():
    message = get_message()

    url = message.get('url')
    ytdloptions = {}
    additional_mpv_args = []

    if "cookies" in message:
        cookies_fname = create_cookiefile(message.get("cookies"));
        ytdloptions["cookies"] = cookies_fname
        additional_mpv_args += ['--cookies', '--cookies-file={}'.format(cookies_fname)]

    mpv_ytdloptions = '--ytdl-raw-options={}'.format(
        ",".join("{}={}".format(k,v) for k,v in ytdloptions.items()))

    args = ['mpv', '--no-terminal', mpv_ytdloptions] + additional_mpv_args + ["--", url]


    Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

    # Need to respond something to avoid "Error: An unexpected error occurred"
    # in Browser Console.
    send_message("ok")


def create_cookiefile(cookies):
    """
    create a temporary file in netscape cookie format and return its path
    """
    cookiefile = tempfile.NamedTemporaryFile(mode="w+", delete=False)
    cookiefile.write("""# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

""")
    for cookie in cookies:
        if "expirationDate" in cookie:
            expdate = str(cookie.get("expirationDate"))
        else:
            expdate = "0"
        tokens = [cookie.get("domain"),
                  str(cookie.get("domain").startswith(".")).upper(),
                  cookie.get("path"), str(cookie.get("secure")).upper(),
                  expdate, cookie.get("name"),
                  cookie.get("value")]
        line = "\t".join(tokens)
        cookiefile.write(line)
        cookiefile.write("\n")
    cookiefile.close()
    return cookiefile.name


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
