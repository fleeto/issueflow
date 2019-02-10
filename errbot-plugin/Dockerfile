FROM alpine
COPY prepare.sh /usr/local/bin
COPY requirements.txt /tmp/requirements.txt
RUN /usr/local/bin/prepare.sh
COPY config.py /errbot/
COPY transbot /errbot/plugins/transbot
WORKDIR /errbot
VOLUME ["/errbot/data", "/errbot/config"]
CMD ["/usr/local/bin/entry.sh"]