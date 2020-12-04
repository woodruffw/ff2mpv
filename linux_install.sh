#!/usr/bin/env bash

# Some environment path variables
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
case "$(uname)" in
    Linux*)
        MOZ_DEST="$HOME/.mozilla"
        JSON_DEST="$MOZ_DEST/native-messaging-hosts"
        ;;
    Darwin*)
        MOZ_DEST="$HOME/Library/Application Support/Mozilla"
        JSON_DEST="$MOZ_DEST/NativeMessagingHosts"
        ;;
    *)
    echo "Unsupported OS, please follow the manual instructions in the wiki"
    exit 1
esac
OLD_PATH="/home/william/scripts/ff2mpv"

# Copying the JSON
if [[ -d "$MOZ_DEST" ]]; then
  mkdir -p "$JSON_DEST"
  # Replace the placeholder path in the JSON file and install it
  sed -e "s|$OLD_PATH|$CURRENT_DIR/ff2mpv.py|g" ff2mpv.json > "$JSON_DEST"/ff2mpv.json
else
  echo "Please initialize the .mozilla folder by running Firefox at least once"
  exit 1
fi
echo "Install successful!"
