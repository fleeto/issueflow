#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from github_webhook import Webhook
from flask import Flask
import os
import sys
from issueflow import action

import logging.handlers

MAX_LOG_BYTES = 1024 * 1024
LOG_LEVEL = os.getenv('LOG_LEVEL',  str(logging.INFO))
PORT = os.getenv("PORT", "80")
TOKEN = os.getenv('GITHUB_TOKEN', "")
WORKFLOW = os.getenv('WORKFLOW', "")
ADMINS = os.getenv('ADMINS', "")


handler = logging.StreamHandler(sys.stdout)
fmt = '%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)s - %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(int(LOG_LEVEL))

app = Flask(__name__)
webhook = Webhook(app)


def log_incoming_comment(data):
    line = "User: {} Issue: {} Comment: {}"
    content = line.format(
        data["sender"]["login"],
        data["issue"]["number"],
        data["comment"]["body"]
    )
    logger.info(content)


@webhook.hook("issues")
def on_issues(data):
    logger.info("issue action:{} {}".format(data["action"], data["issue"]["number"]))
    git_action = data["action"]
    if git_action != "opened":
        return
    subject = {
        "repo": data["repository"]["id"],
        "issue_id": data["issue"]["number"],
        "sender": data["sender"]["login"],
        "command": "opened"

    }
    action.execute(
        "config.yaml", TOKEN, WORKFLOW,
        ADMINS.split(","), "on_issue",
        subject
    )


@webhook.hook("issue_comment")
def on_issue_comment(data):
    log_incoming_comment(data)
    subject = {
        "repo": data["repository"]["id"],
        "issue_id": data["issue"]["number"],
        "sender": data["sender"]["login"],
        "command": data["comment"]["body"]
    }

    action.execute(
        "config.yaml", TOKEN, WORKFLOW,
        ADMINS.split(","), "on_comment",
        subject
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(PORT), debug=False)
