ff2mpv
======

![license](https://raster.shields.io/badge/license-MIT%20with%20restrictions-green.png)

This is a Firefox addon for playing URLs in MPV.

Clicking the little icon in your toolbar will make MPV attempt to play the current URL.

If you want to play a specific URL on a page, right click it and click the "Play in MPV"
context button.

## Cookies

You can enable cookie support for individual sites via a whitelist.
The whitelist supports regular expressions in order to cover subdomains.
Please remember to escape dots (`.`) like so: `\.`.

**Do not use '.*' - it is a big problem for your privacy**

Examples:
```
.*\.youtube\.com/.*
.*\.youtube\.com/playlist.*
.*\.fau\..*/.*
```
The `/playlist` one sends cookies only if the link is a playlist.
This is useful if you want to play private playlists but don't want to send cookies for normal videos.

## Installation

**IMPORTANT**: If you update the addon in your browser, **make sure to update the native host as
well**!

First, install the addon from [AMO](https://addons.mozilla.org/en-US/firefox/addon/ff2mpv/).

Then, follow your system's installation directions on the Wiki:

Linux: https://github.com/woodruffw/ff2mpv/wiki/Installation-on-Linux

macOS: https://github.com/woodruffw/ff2mpv/wiki/Installation-on-macOS

Windows: https://github.com/woodruffw/ff2mpv/wiki/Installation-on-Windows

[A Go version of the native client is also available](https://git.clsr.net/util/ff2mpv-go/).

## License

The source code in this repository is licensed under a *modified* MIT License.

The icons in this repository are licensed by the MPV team under GNU LGPL, version 2.1.
