#!/usr/bin/env python3
"""
A Python script that attempts to check that the configuration of your
nativeMessaging app is set up correctly

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
parser = argparse.ArgumentParser(
    description='Helper for ff2mpv on windows.')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", "--check", action="store_const", const="1", dest="OPT", help="only checks the installation, no modification")
group.add_argument("-i", "--install", action='store_const', const="2", dest="OPT", help="installs ff2mpv registry key or updates the path value")
group.add_argument("-u", "--uninstall", action='store_const', const="3", dest="OPT", help="removes ff2mpv registry key and all it's values")
args = parser.parse_args()

WDIR = os.path.dirname(__file__)
FF2MPV_JSON = fr"{WDIR}\ff2mpv-windows.json"
FF2MPV_KEY = r"Software\Mozilla\NativeMessagingHosts\ff2mpv"
# Assuming current user overrides local machine.
HKEYS = {"HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
         "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE}
error = False
found_key = False
print("- Checking Registry:")
for k in HKEYS:
    try:
        print(fr"{k}\{FF2MPV_KEY} ... ", end="")
        key_open = winreg.OpenKey(HKEYS[k], FF2MPV_KEY)
        hkey_found = HKEYS[k]
        print("Found.")
    except FileNotFoundError:
        print("Not found.")
        error = True
        continue
    error = False
    found_key = True
    break

if not found_key:
    if args.OPT == "2":
        # The intermediate missing key are also created.
        key_open = winreg.CreateKey(HKEYS["HKEY_CURRENT_USER"], FF2MPV_KEY)
        print("Key created.")

if args.OPT != "3":
    ff2mpv_value = winreg.QueryValue(key_open, "")
    if args.OPT == "2":
        if ff2mpv_value != FF2MPV_JSON:
            winreg.SetValue(HKEYS["HKEY_CURRENT_USER"], FF2MPV_KEY, winreg.REG_SZ, FF2MPV_JSON)
            ff2mpv_value = winreg.QueryValue(key_open, "")
            print("Value set/updated.\nRestart Firefox if it was running.")
        else:
            print("Nothing to update.")

    else:
        if ff2mpv_value != "":
            print("Value of the key is:", ff2mpv_value)
            try:
                os.path.exists(ff2mpv_value)
                try:
                    json.load(open(ff2mpv_value, "r"))
                except json.decoder.JSONDecodeError:
                    print(f"error: Is {os.path.basename(ff2mpv_value)} a JSON file?")
            except FileNotFoundError:
                print("error: The file does not exist.")
                error = True
        else:
            print("Empty value in the key.")

    print("- Environment variable \"Path\":")
    try:
        subprocess.run("mpv --version", check=False)
    except FileNotFoundError:
        print("error: Path for mpv missing.\n\nPress Win + R, then type or copy/past \"rundll32.exe sysdm.cpl,EditEnvironmentVariables\".")
        print("Add the mpv folder into system or user variable \"Path\".\nRestart Firefox if it was running.\n")
        error = True
    else:
        print("mpv OK.")

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
