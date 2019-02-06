from gitutil.commands import GitCommand
from gitutil.configure import Configuration
from os.path import splitext, join


class TranslateUtil:
    _git_cmd = None
    __tree_cache = []
    _configure = None

    def __init__(self, repository_name, repository_root, config_file, git_path="git"):
        """
        Initialization.

        :param repository_name: Name of the repository (in the config file)
        :type repository_name: str
        :param repository_root: Repository Path
        :type repository_root: str
        :param config_file: Config file
        :type config_file: str
        :param git_path: Executable git path.
        :type git_path: str
        """
        self._git_cmd = GitCommand(repository_root, git_path)
        self._configure = Configuration(config_file)
        self._configure.repository = repository_name

    def _filter_file_type(self, file_name_list):
        """
        Only files with extensions in the list will left.
        :param file_name_list:
        :type file_name_list: list
        :rtype: list
        """
        ext_list = self._configure.get_valid_extensions()
        result = []
        for file_name in file_name_list:
            _, ext = splitext(file_name)
            if ext in ext_list:
                result.append(file_name)
        return result

    def _get_clean_files(self, path):
        """
        Get file list in specified path of specified branch.

        :param path: Relative path of the files we want.
        :type path: str
        :rtype: list
        """
        file_list = self._git_cmd.list_files()
        file_list = self._filter_file_type(file_list)
        result = []
        for file_name in file_list:
            if file_name.startswith(path):
                result.append(file_name.replace(path, ""))
        return result

    def find_new_files(self, branch, target):
        """
        Find files which is in the source path, but not in the
        target path, and return it as a List of string.

        :rtype: list
        :param branch: Branch name (in the configure file)
        :type branch: str
        :param target: Target name (in the configure file)
        :type target: str
        """
        target_path = self._configure.get_destination(target)["path"]
        source_path = self._configure.get_source()["path"]

        # List files in source/target path
        source_list = self._get_clean_files(source_path)
        target_list = self._get_clean_files(target_path)

        # return the different files list
        result = list(set(source_list) - set(target_list))
        result.sort()
        return result

    def find_updated_files(self, target):
        """
        Find files match this criteria:
        - Both in source and target.
        - Last commit of source file is later than the last commit of target file

        and return it as a List of string.

        :rtype: list
        :param target: Target name (in the configure file)
        :type target: str
        """

        target_path = self._configure.get_destination(target)["path"]
        source_path = self._configure.get_source()["path"]

        # get files both in source and target.
        source_list = self._get_clean_files(source_path)
        target_list = self._get_clean_files(target_path)
        same_files = list(set(source_list) & set(target_list))
        result = []
        for file_name in same_files:
            source_last_commit = \
                self._git_cmd.get_last_commit(source_path + file_name)
            target_commit = \
                self._git_cmd.get_last_commit(target_path + file_name)
            target_time = self._git_cmd.get_hash_time(target_commit)
            source_base_commit = self._git_cmd.get_file_hash_before(source_path + file_name, target_time)
            if source_base_commit != source_last_commit:
                # print("{} {} \n {}".format(
                #     source_last_commit,
                #     source_base_commit,
                #     file_name
                # ))
                diff = self._git_cmd.get_diff_by_hash(source_path + file_name,
                                                      source_last_commit, source_base_commit)
                result.append({file_name: diff})
        return result

    def show_something(self, branch, target):
        branch_name = self._configure.get_branch(branch)["value"]
        target_path = self._configure.get_destination(target)["path"]
        source_path = self._configure.get_source()["path"]

        # get files both in source and target.
        source_list = self._get_clean_files(source_path)
        target_list = self._get_clean_files(target_path)
        same_files = list(set(source_list) & set(target_list))
        count = 0
        for file_name in same_files:
            source_file = source_path + file_name
            target_file = target_path + file_name
            source_last_commit = self._git_cmd.get_last_commit(source_file)
            source_commit_date = self._git_cmd.get_hash_time(source_last_commit)
            target_last_commit = self._git_cmd.get_last_commit(target_file)
            target_commit_date = self._git_cmd.get_hash_time(target_last_commit)
            if source_commit_date > target_commit_date:
                print("{}\t{}\t{}\n{}\t{}\t{}".format(
                    source_last_commit, source_commit_date, source_file,
                    target_last_commit, target_commit_date, target_file
                ))
                branch_parent_hash = self._git_cmd.get_file_hash_before(source_file, target_commit_date)
                global_parent_hash = self._git_cmd.get_file_hash_before(source_file, target_commit_date)
                print("Branched Parent: {}\tGlobal Parent: {}\n".format(
                    branch_parent_hash, global_parent_hash))
            else:
                continue

            count += 1
        print(count)
