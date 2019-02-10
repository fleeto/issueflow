#!/bin/sh
set -xe
apk add python3 git --update
apk add --virtual .build-deps \
    python3-dev musl-dev gcc libffi-dev openssl-dev \
    libxml2-dev
pip3 install --upgrade pip
pip3 install  --no-cache-dir -r /tmp/requirements.txt
apk del .build-deps

mkdir /errbot /errbot/data /errbot/plugins

cat >> /usr/local/bin/entry.sh << EOF
#!/bin/sh
if [ ! -f /errbot/config.py ]; then
    mkdir -p /errbot/data
    errbot --init
fi
errbot \$*
EOF

chmod a+x /usr/local/bin/entry.sh