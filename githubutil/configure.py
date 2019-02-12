# -*- coding: UTF-8 -*-

import yaml
import re


class Configuration:
    __configure_file = ""
    __configure_object = None

    def __init__(self, configfile):
        with open(configfile, "r") as handler:
            self.__configure_object = yaml.load(handler)

    def __get_workflow(self, name=""):
        for item in self.__configure_object["workflow"]:
            if item["name"] == name:
                return item
        return None

    def __get_event(self, workflow, event):
        wf = self.__get_workflow(workflow)
        return wf["events"][event]

    def list_workflow(self):
        workflow_name_list = []
        for item in self.__configure_object["workflow"]:
            workflow_name_list.append(item["name"])
        return workflow_name_list

    def get_command(self, workflow, event, text):
        event_object = self.__get_event(workflow, event)
        for item in event_object:
            match = re.match(item["regex"], text)
            if match is not None:
                return item
        return None

    def get_labels(self, workflow):
        return self.__get_workflow(workflow)["labels"]
