# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    master_branch = sys.argv[1]
    feature_branch = sys.argv[2]

    print "开始解析 " + master_branch + " 分支"
    if os.system('git checkout ' + master_branch) != 0 and os.system('git pull --rebase') != 0:
        raise RuntimeError("切换 " + master_branch + " 分支失败")
    master_dict = LanguageParser(LANGUAGE_LOCALIZATION_FILE).parse(PROJECT)

    print "开始解析 " + feature_branch + " 分支"
    if os.system('git checkout ' + feature_branch) != 0 and os.system('git pull --rebase') != 0:
        raise RuntimeError("切换 " + feature_branch + " 分支失败")
    feature_dict = LanguageParser(LANGUAGE_LOCALIZATION_FILE).parse(PROJECT)

    print "开始对比 " + master_branch + "/"+ feature_branch + " 分支"
    diff_table = LanguageDiff().diff(master_dict, feature_dict)

    print "生成对比 localization.xlsx"
    ExcelWriter().table(diff_table, PROJECT + "/localization.xlsx")

if __name__ == "__main__":
    main()
