#!/usr/bin/env bash
# Cloudflare Pages build: copies the deployable site into dist/ (everything except tools/,
# functions/, downloads/, README and dotfiles), then runs IndexNow against the built sitemap.
# Installers are not deployed from the repo: /downloads/* streams from the R2 bucket bound as
# DOWNLOADS (functions/_middleware.js), so Pages' 25 MiB file limit never applies.
set -euo pipefail
rm -rf dist && mkdir dist
for f in * ; do
  case "$f" in dist|tools|functions|downloads|README.md) continue ;; esac
  cp -R "$f" dist/
done
cp _headers _redirects dist/
node tools/indexnow.mjs dist/sitemap.xml dist --lastmod
