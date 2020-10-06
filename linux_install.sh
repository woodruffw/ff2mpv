#!/bin/bash

# Some environment path variables
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MOZ_DEST="$HOME/.mozilla"
JSON_DEST="$MOZ_DEST/native-messaging-hosts"
OLD_PATH="/home/william/scripts/ff2mpv"

# Case by case copying the JSON
if [ -d "$JSON_DEST" ]; then
  cp ff2mpv.json $JSON_DEST
elif [ -d "$MOZ_DEST" ]; then
  mkdir $JSON_DEST
  cp ff2mpv.json $JSON_DEST
else
  echo "Please initialize the .mozilla folder"\
  "by running Firefox at least once"
fi

# Replace the path in the copied JSON file
sed -i "s|$OLD_PATH|$CURRENT_DIR|g" $JSON_DEST/ff2mpv.json
