#!/bin/sh
set -x
DEST="/tmp/errbot"
rm -Rf "${DEST}"
mkdir -p "${DEST}"
cp config.py "${DEST}/"
cp Dockerfile "${DEST}/"
cp prepare.sh "${DEST}/"
cp requirements.txt "${DEST}/"
cp -Rf transbot "${DEST}/"
cp -Rf ../githubutil "${DEST}/transbot/githubutil"
cp -Rf ../gitutil "${DEST}/transbot/gitutil"
cp -Rf ../transutil "${DEST}/transbot/transutil"

