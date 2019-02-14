from gitutil.commands import GitCommand
from gitutil.configure import Configuration
from os.path import splitext
import os
import githubutil.github
import json


class TranslateUtil:
    _git_path = ""
    _github_token = ""
    _configure = None

    def __init__(self, config_file, github_token, git_path="git"):
        """
        Initialization.

        :param config_file: Name of the repository config file.
        :type config_file: str
        :param github_token: Github token
        :type github_token: str
        :param git_path: Executable git path.
        :type git_path: str
        """
        self._git_path = git_path
        self._configure = Configuration(config_file)
        self._github_token = github_token

    def _filter_file_type(self, repository_name, file_name_list):
        """
        Only files with extensions in the list will left.
        :param repository_name: Repository name (in the config file)
        :type repository_name: str
        :param file_name_list:
        :type file_name_list: list
        :rtype: list
        """
        ext_list = self._configure.get_valid_extensions(repository_name)
        result = []
        for file_name in file_name_list:
            _, ext = splitext(file_name)
            if ext in ext_list:
                result.append(file_name)
        return result

    def _get_git_commander(self, repo):
        return GitCommand(repo, self._git_path)

    def _get_repo_path(self, repository_name, branch_name):
        self._configure.repository = repository_name
        branch_item = self._configure.get_branch(repository_name, branch_name)
        return branch_item["path"]

    def _get_clean_files(self, repository, branch, path):
        """
        Get file list in specified path.

        :param path: Relative path of the files we want.
        :type path: str
        :rtype: list
        """

        file_list = self._get_git_commander(
            self._get_repo_path(repository, branch)
        ).list_files()
        file_list = self._filter_file_type(repository, file_list)
        path_sep = path.split(os.sep)
        result = [file_name[len(path):]
                  for file_name in file_list
                  if file_name.split(os.sep)[:len(path_sep)] == path_sep]
        return result

    def find_new_files(self, repository_name, branch_name, language):
        """
        Find files which is in the source path, but not in the
        target path, and return it as a List of string.

        :param branch_name:
        :param repository_name:
        :rtype: list of str
        :param language: Language name (in the configure file)
        :type language: str
        """
        target_path = self._configure.get_languages(repository_name,
                                                    language)["path"]
        source_path = self._configure.get_source(repository_name)["path"]

        # List files in source/language path
        source_list = self._get_clean_files(repository_name, branch_name, source_path)
        target_list = self._get_clean_files(repository_name, branch_name, target_path)

        # return the different files list
        result = list(set(source_list) - set(target_list))
        result.sort()
        return result

    def cache_issues(self, query, file_name, search_limit=30):
        """

        :param search_limit:
        :param query: Github query string
        :param file_name: Save search result into a json file

        record = {"query": query,
            "timestamp": 1234567
            items:
            [
                {
                "number": 1234,
                "title": "Issue Title",
                labels: ["version/1.12", "translating"]
                },
            ]
        }
        """
        github_client = githubutil.github.GithubOperator(self._github_token)
        issue_list = github_client.search_issue(query, search_limit)
        result = []
        for issue in issue_list:
            issue_item = {
                "number": issue.number,
                "title": issue.title,
                "labels": []
            }
            for label in issue.labels:
                issue_item["labels"].append(label.name)
            result.append(issue_item)
        with open(file_name, "w") as handle:
            json.dump(result, handle, indent=2)
        return len(result)

    def find_updated_files(self, repository_name, branch_name, language):
        """
        Find files match this criteria:
        - Both in source and target.
        - Last commit of source file is later than the last commit of target file

        and return it as a List of string.

        :param repository_name: Repository name (In the config file)
        :param branch_name: Branch name (In the config file)

        :rtype: dict
        :param language: Language name (in the configure file)
        :type language: str
        """

        repository_path = self._configure.get_branch(repository_name,
                                                     branch_name)["path"]
        git_cmd = self._get_git_commander(repository_path)

        target_path = self._configure.get_languages(repository_name,
                                                    language)["path"]
        source_path = self._configure.get_source(repository_name)["path"]

        # get files both in source and target.
        source_list = self._get_clean_files(repository_name,
                                            branch_name, source_path)
        target_list = self._get_clean_files(repository_name,
                                            branch_name, target_path)
        same_files = list(set(source_list) & set(target_list))

        result = {}
        for file_name in same_files:
            source_last_commit = \
                git_cmd.get_last_commit(source_path + file_name)
            target_commit = \
                git_cmd.get_last_commit(target_path + file_name)
            target_time = git_cmd.get_hash_time(target_commit)
            source_base_commit = git_cmd.get_file_hash_before(
                source_path + file_name, target_time)
            if source_base_commit != source_last_commit:
                diff = git_cmd.get_diff_by_hash(
                    source_path + file_name,
                    source_last_commit, source_base_commit)
                result[file_name] = diff
        return result

    def get_default_label(self, repository_name, branch, language):
        """

        :param repository_name:
        :param branch:
        :param language:
        :return:
        """
        labels = self._configure.get_repository(repository_name)["labels"]
        labels += self._configure.get_branch(repository_name, branch)["labels"]
        labels += self._configure.get_languages(repository_name, language)["labels"]
        return labels

    def get_search_label(self, repository_name, branch, language):
        labels = self._configure.get_branch(repository_name, branch)["labels"]
        labels += self._configure.get_languages(repository_name, language)["labels"]
        return labels

    def create_issue(self, github_repository, title, body, labels=[],
                     search_labels=[],
                     search_cache="",
                     search_online=False):
        """

        :param labels: Labels for new issue
        :type labels: list of str
        :param search_online: Search duplicated issues online
        :param github_repository: Name of the repository.
        :param title: Title of the new issue.

        :param body: Body of the new issue.
        :param search_labels: Search duplicated issues with title & labels.
        :type search_labels: list of str
        :param search_cache: Search in the cache file
        :type search_cache: str
        :rtype: github.Issue.Issue
        """
        dupe = False
        if len(search_cache) > 0:
            with open(search_cache, "r") as handler:
                obj = json.load(handler)
                for issue_record in obj:
                    if issue_record["title"] == title:
                        if len(search_labels) == 0:
                            dupe = True
                            break
                        else:
                            if set(search_labels).issubset(issue_record["labels"]):
                                dupe = True
                            break

        github_client = githubutil.github.GithubOperator(self._github_token)
        if search_online:
            search_cmd = "repo:{} in:title {}".format(github_repository, title)
            if len(search_labels) > 0:
                search_cmd = "{} {}".format(search_cmd,
                                            " ".join(
                                                ["label:{}".format(i) for i in search_labels])
                                            )
            issue_list = github_client.search_issue(search_cmd)
            for issue in issue_list:
                if issue.title == title:
                    dupe = True
        if dupe:
            return None
        new_issue = github_client.create_issue(github_repository, title, body)
        # Add labels
        for label_name in labels:
            new_issue.add_to_labels(label_name)
        return new_issue

    def gen_source_url(self, repo, branch, file_name):
        """

        :param repo:
        :param branch:
        :param file_name:
        """
        prefix = self._configure.get_branch(repo, branch)["url_prefix"]["source"]
        middle = ""
        if file_name[:1] != "/":
            middle = "/"
        return "{}{}{}".format(prefix, middle, file_name)

    def gen_web_url(self, repo, branch, file_name):
        """

        :param repo:
        :param branch:
        :param file_name:
        """
        prefix = self._configure.get_branch(repo, branch)["url_prefix"]["web"]
        middle = ""
        if file_name[:1] != "/":
            middle = "/"
        return "{}{}{}".format(prefix, middle, file_name)
