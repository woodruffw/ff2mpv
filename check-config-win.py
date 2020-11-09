#!/usr/bin/env python3
"""
A Python script that check, install/update or uninstall the configuration
of your NativeMessaging app for ff2mpv.

Currently requires Python 3.6 minimum.

If you find more issues with setting this up, let's see if we can add to this
script.
"""
import argparse
import json
import os
import subprocess
import winreg

# Command-Line
parser = argparse.ArgumentParser(description="Helper for ff2mpv on windows.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "-c",
    "--check",
    action="store_true",
    help="only checks the installation, no modification",
)
group.add_argument(
    "-i",
    "--install",
    action="store_true",
    help="installs ff2mpv registry key or updates the path value",
)
group.add_argument(
    "-u",
    "--uninstall",
    action="store_true",
    help="removes ff2mpv registry key and all it's values",
)
args = parser.parse_args()

WDIR = os.path.dirname(__file__)
FF2MPV_JSON = fr"{WDIR}\ff2mpv-windows.json"
FF2MPV_KEY = r"Software\Mozilla\NativeMessagingHosts\ff2mpv"
# Assuming current user overrides local machine.
HKEYS = {
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
}
error = False
found_key = False
print("- Checking Registry:")
for key_name, reg_key in HKEYS.items():
    try:
        print(fr"{key_name}\{FF2MPV_KEY} ... ", end="")
        key_open = winreg.OpenKey(reg_key, FF2MPV_KEY)
        hkey_found = reg_key
        print("Found.")
    except FileNotFoundError:
        print("Not found.")
        error = True
        continue
    error = False
    found_key = True
    break

if not found_key:
    if args.install:
        # The intermediate missing key are also created.
        key_open = winreg.CreateKey(HKEYS["HKEY_CURRENT_USER"], FF2MPV_KEY)
        print("Key created.")

if not args.uninstall:
    # Install/Update case
    ff2mpv_value = winreg.QueryValue(key_open, "")
    if args.install:
        if ff2mpv_value != FF2MPV_JSON:
            winreg.SetValue(
                HKEYS["HKEY_CURRENT_USER"], FF2MPV_KEY, winreg.REG_SZ, FF2MPV_JSON
            )
            ff2mpv_value = winreg.QueryValue(key_open, "")
            print("Value set/updated.\nRestart Firefox if it was running.")
        else:
            print("Nothing to update.")

    # Check case
    else:
        if ff2mpv_value != "":
            print("Value of the key is:", ff2mpv_value)
            if os.path.exists(ff2mpv_value):
                try:
                    json.load(open(ff2mpv_value, "r"))
                except json.decoder.JSONDecodeError:
                    print(f"error: Is {os.path.basename(ff2mpv_value)} a JSON file?")
            else:
                print("error: The file does not exist.")
                error = True
        else:
            print("Empty value in the key.")

    print('- Environment variable "Path":')
    try:
        subprocess.run("mpv --version", check=False)
    except FileNotFoundError:
        print("error: Path for mpv missing.")
        print(
            '\nPress Win (key between Ctrl and Alt), then type "Environment Variables".'
        )
        print(
            'Add the mpv folder into system or user variable "Path".\nRestart Firefox if it was running.\n'
        )
        error = True
    else:
        print("mpv OK.")

# Uninstall case
else:
    error = True
    if found_key:
        # Remove ff2mpv key and all value under it.
        winreg.DeleteKey(hkey_found, FF2MPV_KEY)
        print("Key deleted.")
    else:
        print("Nothing to remove.")

if not error:
    print("Looks good! Give it a try from Firefox.")
