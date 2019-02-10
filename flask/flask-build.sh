#!/usr/bin/env bash
set -x
CODE=`uuidgen`
TMP="/tmp/$CODE"
mkdir -p "$TMP"

cp -Rf ../githubutil "$TMP"
cp ../config/config.yaml "$TMP"
cp flask-requirements.txt "$TMP/requirements.txt"
cd "$TMP"

find . -name __pycache__ -exec rm -Rf {} \;
find . -name *.pyc -exec rm -Rf {} \;

zip -r9 "/tmp/$CODE.zip" .
rm -Rf "$TMP"
