# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    print "读取映射关系"
    dict = KeyRefactor().refactor(PROJECT + "/android_map.xlsx")

    print "开始重构Language"
    LanguageRefactor().refactor(dict.values(), PROJECT + "/..")

if __name__ == "__main__":
    main()
