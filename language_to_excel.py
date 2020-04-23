# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    print "开始解析Language"
    language = LanguageParser().parse(PROJECT)

    print "开始写入Excel"
    ExcelWriter().write(language, PROJECT + "/国际化.xlsx")



if __name__ == "__main__":
    main()
