import logging
import os
import json
from issueflow import action

TOKEN = os.getenv('GITHUB_TOKEN', "")
WORKFLOW = os.getenv('WORKFLOW', "")
ADMINS = os.getenv('ADMINS', "")
LOG_LEVEL = os.getenv('LOG_LEVEL',  str(logging.INFO))

logger = logging.getLogger()
logger.setLevel(int(LOG_LEVEL))

    
def webhook(event, context):
    if event["httpMethod"] != "POST":
        return {
            "isBase64Encoded": "false",
            "statusCode": 405,
            "headers": {},
            "body": "Method Not Allowed!"
        }

    data = json.loads(event["body"])
    event_type = event["headers"]["X-GitHub-Event"]
    event_id = event["headers"]["X-GitHub-Delivery"]
    logger.info(
        "Event type: {} Event ID: {}".format(event_type, event_id))

    if event_type == "on_issue":
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

    if event_type == "issue_comment":
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

    return {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "headers": {},
        "body": "Succ!"
    }


def log_incoming_comment(data):
    line = "User: {} Issue: {} Comment: {}"
    content = line.format(
        data["sender"]["login"],
        data["issue"]["number"],
        data["comment"]["body"]
    )
    logger.info(content)
