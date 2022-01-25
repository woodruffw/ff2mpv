#!/usr/bin/env bash

set -x

function installed {
  cmd=$(command -v "${1}")
  [[ -n "${cmd}" ]] && [[ -f "${cmd}" ]]
  return ${?}
}

cd "${0%/*}" || exit 1

if installed "$1" ; then
  browser="$1"
elif installed chromium ; then
  browser=chromium
elif installed google-chrome ; then
  browser=google-chrome
elif installed brave ; then
  browser=brave
else
  >&2 echo "I need a copy of Google Chrome or Chromium to package with. Use it as ./package-chromium.sh executable-name"
  exit 1
fi

rm -rf dist.crx dist/
mkdir -p dist/
while read -r file; do
  cp -r "$file" dist/
done < dist.files

# chromium generates dist.pem on first use
if [ -f dist.pem ]; then
  "${browser}" --pack-extension=dist --pack-extension-key=dist.pem
else
  "${browser}" --pack-extension=dist
fi
