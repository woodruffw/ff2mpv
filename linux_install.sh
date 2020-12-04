#!/usr/bin/env bash

# Some environment path variables
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MOZ_DEST="$HOME/.mozilla"
JSON_DEST="$MOZ_DEST/native-messaging-hosts"
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
