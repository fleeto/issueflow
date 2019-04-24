#!/usr/bin/env python3


from transutil.transutil import TranslateUtil

from githubutil.github import GithubOperator

# TODO: 初始化

# gh = GithubOperator("")
# issue_list = gh.search_issue("repo:fleeto/docker-java label:welcome")
# print(["{} {}".format(i.number, i.title) for i in issue_list])
#
# exit(0)

util = TranslateUtil("/Users/dustise/Downloads/istio-repository.yaml",
                     "")

result = util.sync_pr_state_to_task_issue("istio", "1.1", "zh", days=5)

for item in result:
    print(item)
