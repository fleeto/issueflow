#!/usr/bin/env python3


from gitutil.transutil import TranslateUtil, Configuration
# TODO: 初始化

util = TranslateUtil(
    "kubernetes",
    "/Users/dustise/Downloads/website",
    "repository.yaml"
)

# TODO: 校验

config = Configuration("repository.yaml")
# print(config.list_repository())
config.repository = "kubernetes"
# print(config.list_branch())
# print(config.get_source())


# TODO: 获取某分支新建内容

# print("\n".join(util.find_new_files("1.12", "zh")))

# TODO: 获取某分支更新翻译

util.find_updated_files("zh")
# util.show_something("1.12", "zh")

# TODO: 创建新翻 Issue

# TODO: 创建更新 Issue

# TODO: 定义缺省标签