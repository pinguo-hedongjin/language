# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    print "开始解析localization.strings"
    localization_dict = LanguageParser(LANGUAGE_LOCALIZATION_FILE).parse(PROJECT)

    print "开始写入Localizable.strings"
    IosWriter().write(localization_dict, PROJECT + "/../KuCoin")

if __name__ == "__main__":
    main()
