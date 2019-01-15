#!/usr/bin/env bash
set -xe
CODE=`uuidgen`
TMP="/tmp/$CODE"
mkdir -p "$TMP"
cp -Rf * "$TMP"
cd "$TMP"
rm -Rf .git
rm -Rf issueflow/__*
pip install -r requirements.txt  --target .
zip -r9 "/tmp/$CODE.zip" .
rm -Rf "$TMP"