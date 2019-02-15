import subprocess
import re
import os


class GitCommand:
    __repo_path = ""
    __git_path = "git"

    def __init__(self, path, git="git"):
        self.__repo_path = path
        self.__git_path = git

    def __command_wrapper(self, command):
        cwd = os.getcwd()
        os.chdir(self.__repo_path)
        try:
            output = subprocess.check_output([self.__git_path] + command)
            return output.decode("utf-8")
        except subprocess.CalledProcessError:
            return None
        finally:
            os.chdir(cwd)

    def list_branches(self, command=None, pattern=r"origin/release.*?$"):
        if command is None:
            command = ["branch", "-r"]
        output = self.__command_wrapper(command)
        result = []
        for line in output.split("\n"):
            if re.match(pattern, line.strip()) is not None:
                result.append(line.strip())
        return result

    def get_last_commit(self, file_name):
        cmd = [
            "log",
            "-1", "--oneline",
            file_name]
        output = self.__command_wrapper(cmd)
        if len(output.strip()) == 0:
            return None
        mat = re.match(r"^(.*?)\s+.*?$", output.strip())
        return mat[1]

    def list_files(self):
        command = ["ls-files"]
        lines = (self.__command_wrapper(command)).strip().split("\n")
        return lines

    def get_hash_time(self, hashcode):
        command = [
            "log", "-1", "--pretty=format:'%ad'",
            "--date=iso8601", hashcode
        ]
        return self.__command_wrapper(command).strip().strip("'")

    def get_file_hash_before(self, filename, iso8601_time):
        command = [
            "log", "-1",
            "--pretty=format:%h",
            "--before", iso8601_time,
            filename
        ]
        return self.__command_wrapper(command).strip()

    def get_diff_by_hash(self, filename, new_hashcode, old_hashcode):
        command = [
            "diff", new_hashcode, old_hashcode,
            filename
        ]
        return self.__command_wrapper(command).strip()

    def pull(self):
        command = ["pull"]
        return self.__command_wrapper(command).strip()
