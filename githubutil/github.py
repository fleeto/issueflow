# -*- coding: UTF-8 -*-
import datetime

import github
import re
import time
import logging


class GithubOperator:
    _token = ""
    _client = None
    admin_list = None
    write_interval = 1

    def __init__(self, token):
        self._token = token
        self._client = github.Github(self._token)

    def get_repo(self, repo_name):
        """
        Get an Repository Object by its name.
        :type repo_name: str
        :param repo_name: full name of the repository
        :return: Repository Name
        :rtype: github.Repository.Repository
        """
        return self._client.get_repo(repo_name)

    def get_issue(self, repository_name, issue_id):
        """
        Get issue object
        :param repository_name:
        :param issue_id:
        :rtype: github.Issue.Issue
        """
        repo = self.get_repo(repository_name)
        return repo.get_issue(issue_id)

    def search_issue(self, query, limit_interval=0):
        """
        Search issues from Github.
        :param limit_interval: If limit_interval > 0, then check the rate limit.
        :param query: Github query
        :type query: str
        :rtype list of github.Issue.Issue
        """
        client = self._client
        res = client.search_issues(query)
        result = []
        count = 0
        for issue in res:
            if limit_interval > 0:
                count += 1
                if count % limit_interval == 0:
                    self.check_limit(search_limit=limit_interval)
            result.append(issue)
        return result

    def get_limit(self):
        limit = self._client.get_rate_limit()
        return {
            "core": {
                "remaining": limit.core.remaining,
                "limit": limit.core.limit,
                "reset": limit.core.reset
            },
            "search": {
                "remaining": limit.search.remaining,
                "limit": limit.search.limit,
                "reset": limit.search.reset
            }
        }

    def check_limit(self, core_limit=10, search_limit=10):
        """
        Wait for rate limit of github
        :param core_limit:
        :param search_limit:
        """

        limit = self._client.get_rate_limit()
        now = datetime.datetime.utcnow()

        if limit.core.remaining < core_limit:
            tick = (limit.core.reset - now).total_seconds()
            logging.warning(
                "Waiting core limits for {} seconds.".format(tick))
            time.sleep(tick + 2)
        if limit.search.remaining <= search_limit:
            tick = (limit.search.reset - now).total_seconds()
            logging.warning(
                "Waiting search limits for {} seconds.".format(tick))
            time.sleep(tick + 2)

    def create_issue(self, repository_name, title, body):
        """
        Create an issue in specified repository/
        :param repository_name:
        :param title:
        :param body:
        :rtype: github.Issue.Issue
        """
        repo = self.get_repo(repository_name)
        return repo.create_issue(title, body)

    def issue_comment(self, repository_name, issue_id, comment_body):
        """
        Post comment for the issue in specified repository.
        :type repository_name: str
        :type issue_id: int
        :type comment_body: str
        """
        issue = self.get_issue(repository_name, issue_id)
        return issue.create_comment(comment_body)


class GithubAction(GithubOperator):
    label_list = None

    def execute_action(self, subject, action):
        if action["type"] == "comment":
            self._comment(subject, action["value"])
        if action["type"] == "label":
            group_name = action["value"]["group"]
            mutex = bool(action["value"]["mutex"])
            label = action["value"]["label"]
            self._set_label(subject, group_name, label, mutex)
        if action["type"] == "assign":
            self._assign(subject, action["value"])
        if action["type"] == "set_state":
            self._set_state(subject, action["value"])
        if action["type"] == "create_issue":
            time.sleep(self.write_interval)
            return self.create_issue(subject["repo"],
                                     action["title"], action["body"])

    def _create_issue(self, subject, title, body):
        repo = self.get_repo(subject["repo"])
        time.sleep(self.write_interval)
        self.create_issue(subject["repo"], title)
        return repo.create_issue(title, body)

    def _set_label(self, subject, group, label, mutex=False):
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

    def _remove_label(self, subject, label):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        issue_obj.remove_from_labels(label)
        time.sleep(self.write_interval)

    def _comment(self, subject, comment):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        var_processor = GithubVariable(self._token)
        issue_obj.create_comment(var_processor.translate(subject, comment))
        time.sleep(self.write_interval)

    def _assign(self, subject, assignee):
        issue_obj = self.get_issue(subject["repo"], subject["issue_id"])
        var_processor = GithubVariable(self._token)
        issue_obj.add_to_assignees(var_processor.translate(subject, assignee))
        time.sleep(self.write_interval)

    def _set_state(self, subject, value):
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
        var_processor = GithubVariable(self._token)
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
        var_processor = GithubVariable(self._token)
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
