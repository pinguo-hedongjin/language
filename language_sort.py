# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    print "开始英文排序"
    LanguageSort().sort(PROJECT + "/en")

if __name__ == "__main__":
    main()
