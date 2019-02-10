#!/usr/bin/env bash
set -x
CODE=`uuidgen`
TMP="/tmp/$CODE"
mkdir -p "$TMP"

cp -Rf githubutil "$TMP"
cp config.yaml "$TMP"
cp gcp-entry.py "$TMP/main.py"
cp gcp-requirements.txt "$TMP/requirements.txt"
cp ~/Downloads/permission.json "$TMP"
cd "$TMP"

find . -name __pycache__ -exec rm -Rf {} \;
find . -name *.pyc -exec rm -Rf {} \;

zip -r9 "/tmp/$CODE.zip" .
rm -Rf "$TMP"
