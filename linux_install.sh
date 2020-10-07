#!/usr/bin/env bash

# Some environment path variables
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MOZ_DEST="$HOME/.mozilla"
JSON_DEST="$MOZ_DEST/native-messaging-hosts"
OLD_PATH="/home/william/scripts/ff2mpv"

# Copying the JSON
if [[ -d "$MOZ_DEST" ]]; then
  mkdir -p "$JSON_DEST"
  cp ff2mpv.json "$JSON_DEST"
else
  echo "Please initialize the .mozilla folder by running Firefox at least once"
  exit 1
fi

# Replace the path in the copied JSON file
sed -i -e "s|$OLD_PATH|$CURRENT_DIR/ff2mpv.py|g" "$JSON_DEST"/ff2mpv.json
echo "Install successful!"
