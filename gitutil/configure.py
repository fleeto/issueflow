# -*- coding: UTF-8 -*-

import yaml


class Configuration:
    __configure_file = ""
    __configure_object = None
    _current_repository_name = ""

    def __init__(self, configfile):
        with open(configfile, "r") as handler:
            self.__configure_object = yaml.load(handler)

    def _repository_set(self, name):
        self._current_repository_name = name

    def _repository_get(self):
        assert self._current_repository_name != "", "Set current repository name first."
        return self.__configure_object["repositories"][self._current_repository_name]

    repository = property(_repository_get, _repository_set)

    def list_repository(self):
        list((self.__configure_object["repositories"]).keys())

    def list_branch(self):
        result = []
        for item in self.repository["branches"]:
            result.append(item["name"])
        return result

    def get_source(self):
        return self.repository["source"]

    def get_branch(self, branch_name):
        assert self._current_repository_name != ""
        branch_list = self.repository["branches"]
        for branch_item in branch_list:
            if branch_item["name"] == branch_name:
                return branch_item
        return None

    def list_destination(self):
        result = []
        for item in self.__configure_object["destination"]:
            result.append(item)
        return result

    def get_destination(self, name):

        for item in self.repository["destination"]:
            if item["name"] == name:
                return item
        return None

    def get_valid_extensions(self):
        return self.repository["valid_extensions"]