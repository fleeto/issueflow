# -*- coding: UTF-8 -*-

import yaml


class Configuration:
    __configure_file = ""
    __configure_object = None
    _current_repository_name = ""

    def __init__(self, configfile):
        with open(configfile, "r") as handler:
            self.__configure_object = yaml.load(handler)

    def _get_repository(self, repository_name):
        return self.__configure_object["repositories"][repository_name]

    def list_repository(self):
        return list((self.__configure_object["repositories"]).keys())

    def get_repository(self, name):
        return self.__configure_object["repositories"][name]

    def get_ignore_re_list(self, repository_name, branch_name):
        branch_item = self.get_branch(repository_name, branch_name)
        if "ignore" in branch_item.keys():
            return branch_item["ignore"]
        return []

    def list_branch(self, repository_name):
        """

        :rtype: list of str
        :param repository_name:
        :return: List of branch names.
        """
        result = []
        repo_data = self._get_repository(repository_name)
        for item in repo_data["branches"]:
            result.append(item["name"])
        return result

    def get_source(self, repository_name):
        repo_data = self._get_repository(repository_name)
        return repo_data["source"]

    def get_branch(self, repository_name, branch_name):
        repo_data = self._get_repository(repository_name)
        branch_list = repo_data["branches"]
        for branch_item in branch_list:
            if branch_item["name"] == branch_name:
                return branch_item
        return None

    def list_languages(self, repository_name):
        result = []
        repo_data = self._get_repository(repository_name)
        for item in repo_data["languages"]:
            result.append(item)
        return result

    def get_languages(self, repository_name, name):
        repo_data = self._get_repository(repository_name)
        for item in repo_data["languages"]:
            if item["name"] == name:
                return item
        return None

    def get_valid_extensions(self, repository_name):
        repo_data = self._get_repository(repository_name)
        return repo_data["valid_extensions"]
