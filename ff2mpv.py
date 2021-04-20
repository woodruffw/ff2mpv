#!/usr/bin/env python3

import json
import os
import os.path
import platform
import re
import struct
import subprocess
import sys
import tempfile


def main():
    message = get_message()

    url = message.get('url')
    ytdloptions = {}
    additional_mpv_args = []

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

    if "cookies" in message and is_whitelisted(url, get_whitelist()):
        cookies_fname = create_cookiefile(message.get("cookies"));
        ytdloptions["cookies"] = cookies_fname
        additional_mpv_args += ['--cookies', '--cookies-file={}'.format(cookies_fname)]

    mpv_ytdloptions = '--ytdl-raw-options={}'.format(
        ",".join("{}={}".format(k,v) for k,v in ytdloptions.items()))

    args = ['mpv', '--no-terminal', mpv_ytdloptions] + additional_mpv_args + ["--", url]

    subprocess.Popen(args, **kwargs)

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


def get_whitelist():
    path = os.path.join(os.getenv('XDG_CONFIG_HOME'), 'ff2mpv/whitelist.txt')
    if not os.path.isfile(path):
        path = os.path.join(os.getenv('HOME'),  '.config/ff2mpv/whitelist.txt')
        if not os.path.isfile(path):
            return ['a^'] # impossible regex
    file = open(path, 'r')
    return [line[:-1] for line in file.readlines()] # strip newline characters


def is_whitelisted(url, whitelist):
    for entry in whitelist:
        pattern = re.compile(entry)
        if pattern.match(url):
            return True
    return False


def send_message(message):
    content = json.dumps(message).encode("utf-8")
    length = struct.pack("@I", len(content))
    sys.stdout.buffer.write(length)
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
