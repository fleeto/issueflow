#!/usr/bin/env python3


from transutil.transutil import TranslateUtil

from githubutil.github import GithubOperator

# TODO: 初始化

# gh = GithubOperator("")
# issue_list = gh.search_issue("repo:fleeto/docker-java label:welcome")
# print(["{} {}".format(i.number, i.title) for i in issue_list])
#
# exit(0)

util = TranslateUtil("/Users/dustise/Downloads/repository.yaml",
                     "")

# print(util.get_default_label("kubernetes", "1.12", "zh"))

# TODO: 校验

# TODO: 获取某分支新建内容

# util.find_new_files("kubernetes", "1.12", "zh")
# new_files = util.find_new_files("kubernetes", "1.12", "zh")
# print("\n".join(new_files))
# print(len(new_files))

# TODO: 获取某分支更新翻译

diff_list = util.find_updated_files("kubernetes", "1.12", "zh")
print("\n".join(list(diff_list.keys())))

# util.show_something("1.12", "zh")

# TODO: issue 缓存

# util.cache_issues("repo:fleeto/docker-java is:open type:issue label:sync/new label:translating",
#                   "translating.json")

# TODO: 创建新翻 Issue

util.create_issue("fleeto/docker-java",
                  "content/help/glossary/workload.md", "Nothing",
                  search_cache="translating.json",
                  search_labels=["sync/new", "translating"],
                  search_online=True)

# TODO: 创建更新 Issue

# TODO: 定义缺省标签
