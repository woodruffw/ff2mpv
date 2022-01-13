#!/usr/bin/env bash
set -x
cd "${0%/*}" || exit 1

rm -f dist.crx
mkdir -p dist/
while read -r file; do
  cp -r "$file" dist/
done < dist.files

# chromium generates dist.pem on first use
if [ -f dist.pem ]; then
  chromium --pack-extension=dist --pack-extension-key=dist.pem
else
  chromium --pack-extension=dist
fi
