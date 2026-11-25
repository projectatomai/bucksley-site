#!/bin/bash
# Usage: tools/set-release.sh VERSION BUILD SHA256 BYTES
# Points the whole site at downloads/Bucksley-VERSION.dmg: the first run switches every page from
# "Coming soon" to the real Mac download. It regenerates the pages and llms.txt with
# tools/build-site.py --release (download page, home page, header, help, privacy, and the JSON-LD
# softwareVersion, downloadUrl and InStock offer on every page). Run by bucksley/scripts/release-mac.sh
# after it copies the DMG to downloads/ and the feed to appcast.xml. SHA256 and BYTES may be
# "pending" for a placeholder; otherwise the staged DMG must exist and match both.
#
# The DMG itself is served from the R2 bucket bucksley-downloads, not from git. Upload it before
# pushing (see README):
#   npx wrangler r2 object put bucksley-downloads/Bucksley-VERSION.dmg --file downloads/Bucksley-VERSION.dmg --remote --content-type application/x-apple-diskimage
set -euo pipefail
usage='Usage: tools/set-release.sh VERSION BUILD SHA256 BYTES'
version="${1:?$usage}" build="${2:?$usage}" sha="${3:?$usage}" bytes="${4:?$usage}"
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo 'VERSION must look like 1.2.3.' >&2; exit 1; }
[[ "$build" =~ ^[0-9]+$ ]] || { echo 'BUILD must be a whole number.' >&2; exit 1; }
[[ "$sha" =~ ^[0-9a-f]{64}$ || "$sha" == pending ]] || { echo 'Pass the 64-character SHA-256 of the DMG, or "pending".' >&2; exit 1; }
[[ "$bytes" =~ ^[0-9]+$ || "$bytes" == pending ]] || { echo 'BYTES must be the DMG size in bytes, or "pending".' >&2; exit 1; }
cd "$(dirname "$0")/.."

dmg="downloads/Bucksley-$version.dmg"
if [[ "$sha" != pending ]]; then
  [[ -f "$dmg" ]] || { echo "Stage $dmg first." >&2; exit 1; }
  [[ "$(shasum -a 256 "$dmg" | cut -d' ' -f1)" == "$sha" ]] || { echo "Checksum does not match $dmg." >&2; exit 1; }
fi
if [[ "$bytes" != pending && -f "$dmg" ]]; then
  [[ "$(stat -f %z "$dmg" 2>/dev/null || stat -c %s "$dmg")" == "$bytes" ]] || { echo "Size does not match $dmg." >&2; exit 1; }
fi

# Size as Finder shows it (decimal megabytes).
if [[ "$bytes" == pending ]]; then size='Size pending'; else size="$(awk -v b="$bytes" 'BEGIN { printf "%.1f MB", b / 1000000 }')"; fi

python3 tools/build-site.py --release "$version" "$build" "$sha" "$size"

grep -q "Bucksley-$version.dmg" download/index.html || { echo 'The download page has no link to the DMG.' >&2; exit 1; }
echo "Site points at $dmg (version $version, build $build, $size, SHA-256 $sha)."
grep -n "data-release=\"\(version\|build\|size\|sha\)\"" download/index.html | sed -E 's/^([0-9]+):.*(data-release="[a-z]+">[^<]*).*/  download\/index.html:\1 \2/'
grep -n '^- Current release' llms.txt
