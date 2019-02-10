#!/bin/sh
set -x
DEST="/tmp/errbot"
rm -Rf "${DEST}"
cp -Rf errbot-plugin/ "${DEST}/"
cp -Rf githubutil "${DEST}/transbot/githubutil"
cp -Rf gitutil "${DEST}/transbot/gitutil"
cp -Rf transutil "${DEST}/transbot/transutil"

