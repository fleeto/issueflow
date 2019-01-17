#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os

from google.cloud import logging
from issueflow import action

TOKEN = os.getenv('GITHUB_TOKEN', "")
WORKFLOW = os.getenv('WORKFLOW', "")
ADMINS = os.getenv('ADMINS', "")

logging_client = logging.Client()
log_name = "github-webhook-{}".format(WORKFLOW)
logger = logging_client.logger(log_name)


def webhook(request):
    event_type = request.headers["X-GitHub-Event"]
    logger.log_struct(
        {
            "Event Type": event_type,
            "Event ID": request.headers["X-GitHub-Delivery"]
        }
    )
    if request.method != "POST":
        return "Method Not Allowed"
    data = request.get_json()

    if event_type == "issues":
        git_action = data["action"]
        if git_action != "opened":
            return
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
            subject
        )
        return "Event 'issues' processed."

    if event_type == "issue_comment":
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
            subject
        )
        return "Event 'issue_comment' processed."

    return "Current event '{}' is not supported.".format(event_type)
