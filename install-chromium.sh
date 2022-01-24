#!/usr/bin/env bash

# Select browser
if [[ -n $1 ]]; then
  browser=$1
else
  # Defaults to chromium
  browser=chromium
fi

case $browser in
  chromium)
    linux_chromium_path=".config/chromium"
    mac_chromium_path="Library/Application Support/Chromium"
    ;;
  chrome)
    linux_chromium_path=".config/google-chrome"
    mac_chromium_path="Library/Application Support/Google/Chrome"
    ;;
  *)
    >&2 echo "Invalid option. Valid options: \"chrome\" and \"chromium\""
    exit 1
esac

# Some environment path variables
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
case "$(uname)" in
    Linux*)
        CHR_DEST="$HOME/$linux_chromium_path"
        JSON_DEST="$CHR_DEST/NativeMessagingHosts"
        ;;
    Darwin*)
        CHR_DEST="$HOME/$mac_chromium_path"
        JSON_DEST="$CHR_DEST/NativeMessagingHosts"
        ;;
    *)
    echo "Unsupported OS, please follow the manual instructions in the wiki"
    exit 1
esac
OLD_PATH="/home/william/scripts/ff2mpv"

# Copying the JSON
if [[ -d "$CHR_DEST" ]]; then
  mkdir -p "$JSON_DEST"
  # Replace the placeholder path in the JSON file and install it
  sed -e "s|$OLD_PATH|$CURRENT_DIR/ff2mpv.py|g" ff2mpv-chromium.json > "$JSON_DEST"/ff2mpv.json
else
  echo "Please start your browser at least once to generate the required directories"
  exit 1
fi
echo "Install successful!"
