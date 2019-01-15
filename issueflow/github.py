# -*- coding: UTF-8 -*-

import github
import re
import time


class GithubOperator:
    token = ""
    client = None
    admin_list = None
    write_interval = 1

    def __init__(self, token):
        self.token = token
        self.client = github.Github(self.token)

    def get_repo(self, repo_name):
        return self.client.get_repo(repo_name)

    def get_issue(self, repo_name, issue_id):
        repo = self.get_repo(repo_name)
        return repo.get_issue(issue_id)


class GithubAction(GithubOperator):

    label_list = None

    def execute_action(self, subject, action):
        if action["type"] == "comment":
            self.comment(subject, action["value"])
        if action["type"] == "label":
            group_name = action["value"]["group"]
            mutex = bool(action["value"]["mutex"])
            label = action["value"]["label"]
            self.set_label(subject, group_name, label, mutex)
        if action["type"] == "assign":
            self.assign(subject, action["value"])
        if action["type"] == "set_state":
            self.set_state(subject, action["value"])

    def set_label(self, subject, group, label, mutex=False):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        existing_labels = []
        if mutex:
            for item in issue_obj.get_labels():
                existing_labels.append(item.name)
        for label_group in self.label_list:
            if label_group["group"] == group:
                for item in label_group["labels"]:
                    if item == label:
                        issue_obj.add_to_labels(label)
                        time.sleep(self.write_interval)
                    else:
                        if item in existing_labels:
                            issue_obj.remove_from_labels(item)
                            time.sleep(self.write_interval)

    def remove_label(self, subject, label):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        issue_obj.remove_from_labels(label)
        time.sleep(self.write_interval)

    def comment(self, subject, comment):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        var_processor = GithubVariable(self.token)
        issue_obj.create_comment(var_processor.translate(subject, comment))
        time.sleep(self.write_interval)

    def assign(self, subject, assignee):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        var_processor = GithubVariable(self.token)
        issue_obj.add_to_assignees(var_processor.translate(subject, assignee))
        time.sleep(self.write_interval)

    def set_state(self, subject, value):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        issue_obj.edit(state=value)
        time.sleep(self.write_interval)


class GithubCondition(GithubOperator):

    def check_condition(self, subject, item):
        if item["type"] == "labels":
            if not self.check_label(subject, item["value"]):
                return False
        if item["type"] == "state":
            if not self.check_state(subject, item["value"]):
                return False
        if item["type"] == "assigned":
            if not self.check_issue_assigned(subject, item["value"]):
                return False
        if item["type"] == "user_is_member":
            if not self.check_user_is_member(subject, item["value"]):
                return False
        if item["type"] == "search":
            if not self.check_search(subject, item["value"]):
                return False
        if item["type"] == "user_in_list":
            if not self.check_user_in_list(subject, item["value"]):
                return False
        return True

    def check_user_in_list(self, subject, user_list):
        result = []
        var_processor = GithubVariable(self.token)
        var_processor.admin_list = self.admin_list
        for item in user_list:
            res = var_processor.parse_variable(subject, item)
            if isinstance(res, list):
                result += res
            else:
                result.append(res)
        return subject["sender"] in result





    def check_label(self, subject, label_list):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        existing_labels = []
        for label in issue_obj.get_labels():
            existing_labels.append(label.name)
        return len(set(label_list) - set(existing_labels)) == 0

    def check_state(self, subject, state):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        return state == issue_obj.state

    def check_search(self, subject, search):
        var_processor = GithubVariable(self.token)
        repo = self.get_repo(subject["repo"])
        issue_list = repo.get_issues(
            assignee=var_processor.parse_variable(subject, search["assignee"]),
            labels=[repo.get_label(search["label"])]
        )
        max_count = search["max"]
        count = 0
        for _ in issue_list:
            count += 1
            if count >= max_count:
                return False
        return True

    def check_issue_assigned(self, subject, assigned):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        return str(issue_obj.assignee is not None).lower() == str(assigned).lower()

    def check_user_is_member(self, subject, user_is_member):
        repo = self.get_repo(subject["repo"])
        result = str(repo.has_in_assignees(subject["sender"])).lower()
        return result == str(user_is_member).lower()


class GithubVariable(GithubOperator):

    admin_list = []

    def parse_variable(self, subject, placeholder):
        if placeholder[0] != "%":
            return placeholder
        var_name = placeholder.strip("%")
        if var_name == "operator":
            return subject["sender"]

        if var_name == "admin_list":
            adm = []
            for item in self.admin_list:
                adm = "@" + item
            return ",".join(adm)

        if var_name == "admin":
            return self.admin_list

        if var_name == "assignee":
            issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
            result = []
            for item in issue_obj.assignees:
                result.append(item.login)
            return result

    def translate(self, subject, sentence):
        result = sentence
        var_list = re.findall("%.*?%", sentence)
        for item in var_list:
            var_value = self.parse_variable(subject, item)
            result = result.replace(item, var_value)
        return result
