#!/usr/bin/env bash

# Select browser
if [[ -n $1 ]]; then
  browser=$1
else
  # does not default; users need to specify the browser
  :
fi

# Common variables
LINUX_NMH_DIR="NativeMessagingHosts"
JSON_FILE="ff2mpv-chromium.json"

select_browser() {
  trap 'echo; exit 1' INT
  case $browser in
  # https://developer.chrome.com/docs/apps/nativeMessaging/#native-messaging-host-location
  chromium)
    linux_path="$HOME/.config/chromium"
    mac_path="$HOME/Library/Application Support/Chromium"
    ;;
  chrome)
    linux_path="$HOME/.config/google-chrome"
    mac_path="$HOME/Library/Application Support/Google/Chrome"
    ;;
  brave)
    linux_path="$HOME/.config/BraveSoftware/Brave-Browser"
    mac_path="$HOME/Library/Application Support/BraveSoftware/Brave-Browser"
    ;;
  edge)
    # https://docs.microsoft.com/en-us/microsoft-edge/extensions-chromium/developer-guide/native-messaging#step-3---copy-the-native-messaging-host-manifest-file-to-your-system
    linux_path="$HOME/.config/microsoft-edge"
    mac_path="$HOME/Library/Application Support/Microsoft Edge"
    ;;
  firefox)
    linux_path="$HOME/.mozilla"
    mac_path="$HOME/Library/Application Support/Mozilla"
    LINUX_NMH_DIR="native-messaging-hosts"
    JSON_FILE="ff2mpv.json"
    ;;
  custom-chromium)
    if (($# == 2)); then
      linux_path="$2" mac_path="$2"
    else
      printf "path: " && read -r linux_path
      mac_path="$linux_path"
    fi
    ;;
  custom-firefox)
    if (($# == 2)); then
      linux_path="$2" mac_path="$2"
    else
      printf "path: " && read -r linux_path
      mac_path="$linux_path"
    fi
    LINUX_NMH_DIR="native-messaging-hosts"
    JSON_FILE="ff2mpv.json"
    ;;
  *)
    echo >&2 '
Invalid option. Please select a valid browser:
- "chrome"
- "chromium"
- "brave"
- "edge"
- "firefox"
- "custom-chromium"
- "custom-firefox"
'
    printf "browser: " && read -r browser
    select_browser "$@"
    ;;
  esac
}

select_browser "$@"

# Some environment path variables
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
case "$(uname)" in
Linux*)
  BROWSER_DEST="$linux_path"
  JSON_DEST="$BROWSER_DEST/$LINUX_NMH_DIR"
  ;;
FreeBSD*)
  BROWSER_DEST="$linux_path"
  JSON_DEST="$BROWSER_DEST/$LINUX_NMH_DIR"
  ;;
Darwin*)
  BROWSER_DEST="$mac_path"
  JSON_DEST="$BROWSER_DEST/NativeMessagingHosts"
  ;;
*)
  echo "Unsupported OS, please follow the manual instructions in the wiki"
  exit 1
  ;;
esac
OLD_PATH="/home/william/scripts/ff2mpv"

# Copying the JSON
if [[ -d "$BROWSER_DEST" ]]; then
  mkdir -p "$JSON_DEST"
  # Replace the placeholder path in the JSON file and install it
  sed -e "s|$OLD_PATH|$CURRENT_DIR/ff2mpv.py|g" "$JSON_FILE" >"$JSON_DEST"/ff2mpv.json
else
  echo "Please start your browser at least once to generate the required directories"
  exit 1
fi
echo "Install successful!"
