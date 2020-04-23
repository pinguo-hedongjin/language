# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    print "开始解析Excel"
    language = ExcelParser().parse(PROJECT + "/国际化.xlsx")

    print "开始写入Language"
    LanguageWriter().write(language, PROJECT)



if __name__ == "__main__":
    main()
