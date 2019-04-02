# -*- coding: UTF-8 -*-
import os
import github
import githubutil
from githubutil.github import GithubOperator
from gitutil.configure import Configuration as RepoConfig
from gitutil.commands import GitCommand
from transutil.transutil import TranslateUtil
from errbot import BotPlugin, botcmd, arg_botcmd
import logging

MAX_RESULT = int(os.getenv("MAX_RESULT"))
MAX_WRITE = int(os.getenv("MAX_WRITE"))
OPEN_CACHE = "/errbot/config/open_cache.txt"
REPOSITORY_CONFIG_FILE = os.getenv("REPOSITORY_CONFIG_FILE")
REPOSITORY_NAME = os.getenv("REPOSITORY")
TARGET_LANG = os.getenv("TARGET_LANG")


def build_issue(trans, branch, item_list):
    trans.wait_for_limit(MAX_RESULT, MAX_RESULT)
    if type(item_list) == dict:
        file_list = list(item_list.keys())
        type_label = "sync/update"
        is_diff = True
    else:
        file_list = item_list
        type_label = "sync/new"
        is_diff = False

    # Get default labels
    new_labels = trans.get_default_label(
        REPOSITORY_NAME, branch, TARGET_LANG)
    new_labels.append(type_label)
    search_labels = trans.get_search_label(
        REPOSITORY_NAME, branch, TARGET_LANG)

    # Create Issue for new files
    new_count = 0
    skip_count = 0
    for file_name in file_list:
        # Generate issue body
        if is_diff:
            diff = item_list[file_name]
            body = "Source File: [{}]({})\nDiff:\n~~~diff\n {}\n~~~"
            body = body.format(
                file_name,
                trans.gen_source_url(REPOSITORY_NAME, branch, file_name),
                diff
            )
        else:
            body = "Source File: [{}]({})"
            body = body.format(
                file_name,
                trans.gen_source_url(REPOSITORY_NAME, branch, file_name),
            )

        # Search and create issue
        new_issue = trans.create_issue(
            task_repository_name(),
            file_name, body, new_labels, search_labels,
            "", True
        )
        if new_issue is None:
            skip_count += 1
        else:
            new_count += 1
            if new_count >= MAX_WRITE:
                break
        if (new_count + skip_count) % MAX_RESULT:
            trans.wait_for_limit(MAX_RESULT, MAX_RESULT)
    return new_count, skip_count


def task_repository_name():
    repo_config = RepoConfig(REPOSITORY_CONFIG_FILE)
    repo_obj = repo_config.get_repository(REPOSITORY_NAME)
    repo_owner = repo_obj["github"]["task"]["owner"]
    repo_name = repo_obj["github"]["task"]["repository"]
    return "{}/{}".format(repo_owner, repo_name)


def code_repository_name():
    repo_config = RepoConfig(REPOSITORY_CONFIG_FILE)
    repo_obj = repo_config.get_repository(REPOSITORY_NAME)
    repo_owner = repo_obj["github"]["code"]["owner"]
    repo_name = repo_obj["github"]["code"]["repository"]
    return "{}/{}".format(repo_owner, repo_name)


def limit_result(result_set):
    """
    Limit result list with "MAX_RESULT"
    :type result_set: list of str
    :rtype: list of str
    """
    max_result = MAX_RESULT
    result = []
    if max_result > 0:
        result = result_set[:max_result]
    result.append("Total result: {}".format(len(result_set)))
    return result


class TransBot(BotPlugin):
    """
    ChatBot for Kubernetes & Istio
    """

    def _asset_bind(self, msg):
        assert self._github_bound(msg.frm.person), \
            "Bind your Github token please."

    def _github_operator(self, msg):
        """
        Get an Github Operator
        :param msg:
        :return: githubutil.github.GithubOperator
        :rtype: githubutil.github.GithubOperator
        """
        token = self[msg.frm.person + "github_token"]
        result = GithubOperator(token)
        return result

    def _translation_util(self, msg):
        """
        Get an Translation Util
        :param msg:
        :rtype: TranslateUtil
        """
        token = self[msg.frm.person + "github_token"]
        return TranslateUtil(REPOSITORY_CONFIG_FILE, token)

    @botcmd
    def list_branches(self, msg, args):
        """
        List all branches in current repository
        :param msg:
        :param args:
        :return:
        """
        trans = self._translation_util(msg)
        return "\n".join(trans.list_branches(REPOSITORY_NAME))

    @botcmd
    def find_dupe_issues(self, msg, args):
        """
        Find duplicated titles
        :param msg:
        :return:
        """
        github_client = self._github_operator(msg)
        query = "repo:{} is:open type:issue".format(task_repository_name())
        issue_list = github_client.search_issue(query, MAX_RESULT)
        tuple_list = [(issue.title, issue.number) for issue in issue_list]
        tuple_list.sort()
        count_list = {}
        for title, number in tuple_list:
            if title in count_list.keys():
                count_list[title].append(number)
            else:
                count_list[title] = [number]
        result = ""
        count = 0
        for title, number_list in count_list.items():
            if len(number_list) == 1:
                continue
            result += "{} \n {}\n".format(
                title, " ".join([str(i) for i in number_list]))
            count += 1
        result += "\n{} duplicated issues found.".format(count)
        return result

    @arg_botcmd('token', type=str)
    def github_bind(self, msg, token):
        client = github.Github(token)
        from_user = msg.frm.person
        user = client.get_user()
        self[from_user + "github_token"] = token
        self[from_user + "github_login"] = user.login
        return "Hello {}, Welcome.".format(user.login)

    @botcmd
    def github_whoami(self, msg, args):
        from_user = msg.frm.person
        try:
            yield ("**Github Token:**" + self[from_user + "github_token"])
            yield ("**Github Login:**" + self[from_user + "github_login"])
        except:
            yield ("**Bind your Github token please.**")

    def _github_bound(self, person):
        """
        Check if user had bound their github token.
        :param person:
        :rtype: bool
        """
        result = True
        try:
            result = len(self[person + "github_token"]) > 0
        except:
            result = False
        return result

    @botcmd
    def whatsnew(self, msg, args):
        """
        Find issues with the label "welcome"
        :param msg:
        :param args:
        :return:
        """
        self._asset_bind(msg)
        client = self._github_operator(msg)
        cmd = "repo:{} label:welcome is:open type:issue".format(
            task_repository_name())
        issue_list = client.search_issue(cmd, 10)
        result = limit_result(
            ["{}: {}".format(i.number, i.title)
             for i in issue_list])
        return "\n".join(result)

    @arg_botcmd('issue_id', type=int)
    @arg_botcmd('--comment', type=str)
    def comment_issue(self, msg, issue_id, comment):
        """
        Create comment for an issue
        :param msg:
        :param issue_id: Issue number
        :type issue_id: int
        :param comment: comment body
        :return: HTML
        """
        self._asset_bind(msg)
        client = self._github_operator(msg)
        comment_obj = client.issue_comment(task_repository_name(),
                                           issue_id, comment)
        return comment_obj.html_url

    @arg_botcmd('query', type=str)
    def search_issues(self, msg, query):
        """
        Search for issues.
        :param query:
        :return: Issue list.
        """
        self._asset_bind(msg)
        client = self._github_operator(msg)
        issue_list = client.search_issue(query, 10)
        return "\n".join(limit_result(
            ["{}: {}".format(i.number, i.title)
             for i in issue_list]
        ))

    @arg_botcmd('issue_id', type=int)
    def show_issue(self, msg, issue_id):
        """
        Show issue url by its id.
        :param issue_id: ID of the issue.
        :type issue_id: int
        :return: URL
        :rtype: str
        """
        self._asset_bind(msg)
        return "https://github.com/{}/issues/{}".format(task_repository_name(),
                                                        issue_id)

    @botcmd
    def cache_issue(self, msg, args):
        """
        Save opening issues into a text file
        :param msg:
        :param args:
        """
        self._asset_bind(msg)
        yield ("Processing....")
        trans = self._translation_util(msg)
        query = "repo:{} is:open type:issue".format(
            task_repository_name()
        )
        res = trans.cache_issues(query, OPEN_CACHE, MAX_RESULT)
        return "{} records had been cached".format(res)

    @arg_botcmd('branch', type=str)
    @arg_botcmd('--create_issue', type=int, default=0)
    def find_new_files_in(self, msg, branch, create_issue):
        """
        Find new files from a branch for a language.
        :param msg:
        :param branch:
        :param create_issue: if its value is
        0 (default), will only show the new files.
        else it will create new issue for them.
        :return:
        """
        self._asset_bind(msg)
        trans = self._translation_util(msg)
        new_file_list = trans.find_new_files(
            REPOSITORY_NAME, branch, TARGET_LANG)

        if create_issue == 0:
            yield ("\n".join(limit_result(new_file_list)))
        else:
            yield ("Processing....")
            new_count, skip_count = build_issue(trans, branch, new_file_list)
            yield ("{} Issues had been created. {} Issues had been skipped.".format(
                new_count, skip_count))
            yield ("Please cache issues again.")

    @arg_botcmd('branch', type=str)
    @arg_botcmd('--create_issue', type=int, default=0)
    def find_updated_files_in(self, msg, branch, create_issue):
        """
        Find updated files from a branch for a language.

        :param msg:
        :param branch:
        :param create_issue:
        """
        self._asset_bind(msg)
        yield ("Processing....")
        trans = self._translation_util(msg)
        updated_files = trans.find_updated_files(REPOSITORY_NAME, branch, TARGET_LANG)
        if create_issue == 0:
            yield ("\n".join(limit_result(list(updated_files.keys()))))
        else:
            new_count, skip_count = build_issue(trans, branch, updated_files)
            yield ("{} Issues had been created. {} Issues had been skipped.".format(
                new_count, skip_count))
            yield ("Please cache issues again.")

    @botcmd
    def show_limit(self, msg, args):
        self._asset_bind(msg)
        util = self._github_operator(msg)
        limit = util.get_limit()
        core_pattern = "Core-Limit: {}\nCore-Remaining: {}\nCore-Reset: {}\n"
        search_pattern = "Search-Limit: {}\nSearch-Remaining: {}\nSearch-Reset: {}\n"
        return (core_pattern + search_pattern).format(
            limit["core"]["limit"],
            limit["core"]["remaining"],
            limit["core"]["reset"],
            limit["search"]["limit"],
            limit["search"]["remaining"],
            limit["search"]["reset"],
        )

    @botcmd
    def refresh_repositories(self, msg, args):
        config = RepoConfig(REPOSITORY_CONFIG_FILE)
        branches = config.get_repository(REPOSITORY_NAME)["branches"]
        for branch in branches:
            cmd = GitCommand(branch["path"])
            cmd.pull()
            yield ("{} had been updated.".format((branch["path"])))

    @arg_botcmd('branch', type=str)
    def sync_with_pr_in(self, msg, branch):
        yield("Processing....")
        trans = self._translation_util(msg)
        result = trans.sync_pr_state_to_task_issue(REPOSITORY_NAME, branch, TARGET_LANG)
        for pr in result:
            yield(pr)
        yield("{} PR had been processed".format(len(result)))
