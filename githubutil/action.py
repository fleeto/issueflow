# -*- coding: UTF-8 -*-

from githubutil import configure, github


def execute(config, token, workflow,
            admin_list, event, subject, interval=1):
    conf = configure.Configuration(config)
    action = github.GithubAction(token)
    action.write_interval = interval
    action.label_list = conf.get_labels(workflow)

    condition = github.GithubCondition(token)
    condition.admin_list = admin_list
    command = conf.get_command(workflow, event, subject["command"])
    if command is None:
        return False
    passed = True
    for item in command["conditions"]:
        if not condition.check_condition(subject, item):
            action_list = item["failed_actions"]
            for action_item in action_list:
                action.execute_action(subject, action_item)
            passed = False
            break
    if passed:
        action_list = command["actions"]
        for action_item in action_list:
            action.execute_action(subject, action_item)
    return True
