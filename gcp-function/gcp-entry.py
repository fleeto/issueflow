#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
from google.cloud import logging
from githubutil import action

TOKEN = os.getenv('GITHUB_TOKEN', "")
WORKFLOW = os.getenv('WORKFLOW', "")
ADMINS = os.getenv('ADMINS', "")
INTERVAL = os.getenv('INTERVAL', "1")

logging_client = logging.Client()
log_name = "github-webhook-{}".format(WORKFLOW)
logger = logging_client.logger(log_name)


def webhook(request):
    if request.method != "POST":
        return "Method Not Allowed"

    data = request.get_json()
    event_type = request.headers["X-GitHub-Event"]
    event_action = data["action"]
    logger.log_struct(
        {
            "Event Type": event_type,
            "Event ID": request.headers["X-GitHub-Delivery"],
            "Action": event_action
        }
    )

    if event_type == "issues":
        if event_action != "opened":
            return "Action '{}' is not supported".format(event_action)
        subject = {
            "repo": data["repository"]["id"],
            "issue_id": data["issue"]["number"],
            "sender": data["sender"]["login"],
            "command": "opened"
        }
        logger.log_struct(subject)
        action.execute(
            "config.yaml", TOKEN, WORKFLOW,
            ADMINS.split(","), "on_issue",
            subject, float(INTERVAL)
        )
        return "Event 'issues' had been processed."

    if event_type == "issue_comment":
        if event_action not in ["created", "edited"]:
            return "Action '{}' is not supported".format(event_action)
        subject = {
            "repo": data["repository"]["id"],
            "issue_id": data["issue"]["number"],
            "sender": data["sender"]["login"],
            "command": data["comment"]["body"]
        }
        logger.log_struct(subject)
        action.execute(
            "config.yaml", TOKEN, WORKFLOW,
            ADMINS.split(","), "on_comment",
            subject, float(INTERVAL)
        )
        return "Event 'issue_comment' had been processed."

    return "Current event '{}' is not supported.".format(event_type)
