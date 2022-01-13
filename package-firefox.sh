#!/usr/bin/env bash
set -x
cd "${0%/*}" || exit 1

rm -f dist.zip
while read -r file; do
  zip -r dist.zip "$file"
done < dist.files
