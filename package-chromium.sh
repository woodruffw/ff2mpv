#!/usr/bin/env bash

set -x

function installed {
  cmd=$(command -v "${1}")

  [[ -n "${cmd}" ]] && [[ -f "${cmd}" ]]
  return ${?}
}

cd "${0%/*}" || exit 1

if installed chromium ; then
  browser=chromium
elif installed google-chrome ; then
  browser=google-chrome
else
  >&2 echo "I need a copy of Google Chrome or Chromium to package with."
  exit 1
fi

rm -f dist.crx
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
