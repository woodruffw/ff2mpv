#!/usr/bin/env python3
"""
A Python script that attempts to check that the configuration of your
nativeMessaging app is set up correctly

Currently requires Python 3.

If you find more issues with setting this up, let's see if we can add to this
script.
"""
import argparse
import json
import os
import subprocess
import winreg


def main():
    # Command-Line
    parser = argparse.ArgumentParser(
        description='Helper for ff2mpv on windows.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--check", action="store_const", const="1", dest="OPT", help="only checks the installation, no modification")
    group.add_argument("-i", "--install", action='store_const', const="2", dest="OPT", help="installs ff2mpv registry key or updates the path value")
    group.add_argument("-u", "--uninstall", action='store_const', const="3", dest="OPT", help="removes ff2mpv registry key and all it's values")
    args = parser.parse_args()

    error = False
    wdir = os.path.dirname(__file__)
    ff2mpv_json = fr"{wdir}\ff2mpv-windows.json"
    ff2mpv_key = r"Software\Mozilla\NativeMessagingHosts\ff2mpv"
    # Assuming current user overrides local machine.
    hkeys = {"HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
             "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE}
    found_key = False
    print("- Checking Registry:")
    for k in hkeys:
        try:
            print(fr"{k}\{ff2mpv_key} ... ", end="")
            key_open = winreg.OpenKey(hkeys[k], ff2mpv_key)
            hkey_found = hkeys[k]
            print("Found.")
        except FileNotFoundError:
            print("Not found.")
            error = True
            continue
        found_key = True
        error = False
        break

    if not found_key:
        if args.OPT == "2":
            # The intermediate missing key are also created.
            key_open = winreg.CreateKey(hkeys["HKEY_CURRENT_USER"], ff2mpv_key)
            print("Key created.")

    if args.OPT != "3":
        ff2mpv_value = winreg.QueryValue(key_open, "")
        if args.OPT == "2":
            if ff2mpv_value != ff2mpv_json:
                winreg.SetValue(hkeys["HKEY_CURRENT_USER"], ff2mpv_key, winreg.REG_SZ, ff2mpv_json)
                ff2mpv_value = winreg.QueryValue(key_open, "")
                print("Value set/updated.")
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
            winreg.DeleteKey(hkey_found, ff2mpv_key)
            print("Key deleted.")
        else:
            print("Nothing to remove.")

    if not error:
        print("Looks good! Give it a try from Firefox.")


if __name__ == "__main__":
    main()
