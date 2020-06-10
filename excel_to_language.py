# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def all():
    print "开始解析localization.xlsx"
    localization_dict = ExcelParser().dict(PROJECT + "/localization.xlsx")

    print "开始写入localization.strings"
    LanguageWriter(LANGUAGE_LOCALIZATION_FILE).write(localization_dict, PROJECT)


def update():
    print "开始解析localization.xlsx"
    update_dict = ExcelParser().dict(PROJECT + "/localization.xlsx")

    print "开始解析localization.strings"
    localization_dict = LanguageParser(LANGUAGE_LOCALIZATION_FILE).parse(PROJECT)

    print "开始写入localization.strings"
    LanguageWriter(LANGUAGE_LOCALIZATION_FILE).write(localization(localization_dict, update_dict), PROJECT)


def localization(localization_dict, update_dict):
    result_dict = collections.OrderedDict()

    for language_name, language_dict in localization_dict.items():

        if update_dict.has_key(language_name):
            for update_key, update_value in update_dict[language_name].items():
                language_dict[update_key] = update_value

        result_dict[language_name] = language_dict

    return result_dict

if __name__ == "__main__":
    update()
