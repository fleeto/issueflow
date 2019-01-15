#!/usr/bin/env bash
set -x
CODE=`uuidgen`
TMP="/tmp/$CODE"
mkdir -p "$TMP"
cp -Rf * "$TMP"
cd "$TMP"
rm -Rf .git

pip install -r requirements.txt  --target .
find . -name __pycache__ -exec rm -Rf {} \;
find . -name *.pyc -exec rm -Rf {} \;
rm build.sh

zip -r9 "/tmp/$CODE.zip" .
rm -Rf "$TMP"