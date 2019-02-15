#/usr/bin/env python3
from gitutil.configure import Configuration
from gitutil.commands import GitCommand
import os

REPOSITORY_CONFIG_FILE = os.getenv("REPOSITORY_CONFIG_FILE")
REPOSITORY_NAME = os.getenv("REPOSITORY")
config = Configuration(REPOSITORY_CONFIG_FILE)

for branch in config["branches"]:
    cmd = GitCommand(branch["path"])
    cmd.pull()
