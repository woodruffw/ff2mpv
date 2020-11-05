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

    Error = False
    wdir = os.path.dirname(__file__)
    subkey_json = fr"{wdir}\ff2mpv-windows.json"
    key_path = r"Software\Mozilla\NativeMessagingHosts\ff2mpv"
    # Assuming current user overrides local machine.
    HKEYs = {"HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE}
    found_key = False
    print("- Checking Registry:")
    for k in HKEYs:
        try:
            print(fr"{k}\{key_path} ... ", end="")
            key_open = winreg.OpenKey(HKEYs[k], key_path)
            HKEY = HKEYs[k]
            print("Found.")
        except FileNotFoundError:
            print("Not found.")
            Error = True
            continue
        found_key = True
        Error = False
        break

    if not found_key:
        if choice == "2":
            # The intermediate missing key are also created.
            key_open = winreg.CreateKey(
                HKEYs["HKEY_CURRENT_USER"], key_path)
            print("Key created.")

    if choice != "3":
        key_value = winreg.QueryValue(key_open, "")
        if choice == "2":
            if key_value != subkey_json:
                winreg.SetValue(HKEYs["HKEY_CURRENT_USER"],
                                key_path, winreg.REG_SZ, subkey_json)
                key_value = winreg.QueryValue(key_open, "")
                print("Value set/updated.")
            else:
                print("Nothing to update.")

        else:
            if key_value != "":
                print("Value of the key is:", key_value)
                try:
                    os.path.exists(key_value)
                    try:
                        json.load(open(key_value, "r"))
                    except json.decoder.JSONDecodeError:
                        print(
                            f"Error: Is {os.path.basename(key_value)} a JSON file?")
                except FileNotFoundError:
                    print("Error: The file does not exist.")
                    Error = True
            else:
                print("Empty value in the key.")

        print("- Environment variable \"Path\":")
        try:
            subprocess.run("mpv --version")
        except FileNotFoundError:
            print("Error: Path for mpv missing.\n\nPress Win + R, then type or copy/past \"rundll32.exe sysdm.cpl,EditEnvironmentVariables\".\nAdd the mpv folder into system or user variable \"Path\".\nRestart Firefox if it was running.\n")
            Error = True
        else:
            print("mpv OK.")

    else:
        if found_key:
            winreg.DeleteKey(HKEY, key_path)
            print("Key deleted.")
        else:
            print("Nothing to remove.")

    if not Error:
        print("Looks good! Give it a try from Firefox.")


if __name__ == "__main__":
    main()
