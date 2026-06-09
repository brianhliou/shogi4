#!/bin/sh
set -eu

rm -rf public
mkdir -p public/pieces/dark

cp explorer/index.html \
  explorer/og.png \
  explorer/og.svg \
  explorer/robots.txt \
  explorer/sitemap.xml \
  public/

cp explorer/pieces/*.png \
  explorer/pieces/CREDITS.txt \
  public/pieces/

cp explorer/pieces/dark/*.png public/pieces/dark/
