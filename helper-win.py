#!/usr/bin/env python3
"""
A Python script that attempts to check that the configuration of your
nativeMessaging app is set up correctly

Currently requires Python 3.

If you find more issues with setting this up, let's see if we can add to this
script.
"""
import json
import os
import winreg
import subprocess


def main():
    # Menu
    while True:
        try:
            choice = input(
                "1 - Check\n2 - Install/Update Registry\n3 - Uninstall Registry\nExit with Ctrl + C\nChoice [1-3]: ")
        except KeyboardInterrupt:
            print("\nExit.")
            return
        if choice == "1" or choice == "2" or choice == "3":
            break

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
        if choice == "2":
            # The intermediate missing key are also created.
            key_open = winreg.CreateKey(
                hkeys["HKEY_CURRENT_USER"], ff2mpv_key)
            print("Key created.")

    if choice != "3":
        ff2mpv_value = winreg.QueryValue(key_open, "")
        if choice == "2":
            if ff2mpv_value != ff2mpv_json:
                winreg.SetValue(hkeys["HKEY_CURRENT_USER"],
                                ff2mpv_key, winreg.REG_SZ, ff2mpv_json)
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
                        print(
                            f"error: Is {os.path.basename(ff2mpv_value)} a JSON file?")
                except FileNotFoundError:
                    print("error: The file does not exist.")
                    error = True
            else:
                print("Empty value in the key.")

        print("- Environment variable \"Path\":")
        try:
            subprocess.run("mpv --version")
        except FileNotFoundError:
            print("error: Path for mpv missing.\n\nPress Win + R, then type or copy/past \"rundll32.exe sysdm.cpl,EditEnvironmentVariables\".\nAdd the mpv folder into system or user variable \"Path\".\nRestart Firefox if it was running.\n")
            error = True
        else:
            print("mpv OK.")

    else:
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
