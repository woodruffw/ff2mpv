#!/usr/bin/env python3

import fnmatch
import json
import os
import os.path
import platform
import struct
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def main():
    message = get_message()

    url = message.get("url")
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

    if "cookies" in message and cookies_allowed(url):
        with create_cookiefile(message.get("cookies")) as cookie_path:
            ytdloptions["cookies"] = cookie_path
            additional_mpv_args += [
                "--cookies",
                "--cookies-file={}".format(cookie_path),
            ]

    mpv_ytdloptions = "--ytdl-raw-options-append={}".format(
        ",".join("{}={}".format(k, v) for k, v in ytdloptions.items())
    )

    args = ["mpv", "--no-terminal", mpv_ytdloptions] + additional_mpv_args + ["--", url]

    subprocess.Popen(args, **kwargs)

    # Need to respond something to avoid "Error: An unexpected error occurred"
    # in Browser Console.
    send_message("ok")


def create_cookiefile(cookies):
    """
    Create a temporary file in Netscape cookie format and yield its path
    """
    with tempfile.NamedTemporaryFile() as io:
        print(
            textwrap.dedent(
                """
                # Netscape HTTP Cookie File
                # http://curl.haxx.se/rfc/cookie_spec.html
                # This is a generated file!  Do not edit.
                """
            ),
            file=io,
        )

        for cookie in cookies:
            tokens = [
                cookie["domain"],
                str(cookie["domain"].startswith(".")).upper(),
                cookie["path"],
                str(cookie["secure"]).upper(),
                str(cookie.get("expirationDate", 0)),
                cookie["name"],
                cookie["value"],
            ]
            line = "\t".join(tokens)
            print(line, file=io)

        yield io.name


# https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging#App_side
def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return {}
    length = struct.unpack("@I", raw_length)[0]
    message = sys.stdin.buffer.read(length).decode("utf-8")
    return json.loads(message)


def config_root():
    config_home = os.getenv("XDG_CONFIG_HOME")
    if config_home is None:
        return Path("~/.config/ff2mpv").expanduser()
    else:
        return Path(config_home) / "ff2mpv"


def get_allowlist():
    allowlist = config_root() / "allowlist"
    if not allowlist.is_file():
        return []

    with allowlist.open() as io:
        return [line.rstrip() for line in io]


def cookies_allowed(url):
    return any(fnmatch.fnmatch(url, pattern) for pattern in get_allowlist())


def send_message(message):
    content = json.dumps(message).encode("utf-8")
    length = struct.pack("@I", len(content))
    sys.stdout.buffer.write(length)
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
