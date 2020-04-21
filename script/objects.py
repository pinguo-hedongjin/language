#!/usr/bin/python
# coding=utf-8

import os
import re
import xlwt
import xlrd
import collections
import xml.dom.minidom as dom
from langconv import *

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# LANGUAGE目录结构
LANGUAGE_RESOURCE_DIRECTORY = "language"
LANGUAGE_SIMPLE_DIRECTORY = "zh"
LANGUAGE_ENGLISH_DIRECTORY = "en"
LANGUAGE_LOCALIZATION_DIRECTORY = [LANGUAGE_ENGLISH_DIRECTORY, LANGUAGE_SIMPLE_DIRECTORY]

# ANDROID目录结构
ANDROID_RESOURCE_DIRECTORY = "android/src/main/res"
ANDROID_TRADITIONAL_DIRECTORY = "values-zh-rHK"
ANDROID_LOCALIZATION_DIRECTORY = ["values", "values-zh-rCN"]

# IOS目录结构
IOS_RESOURCE_DIRECTORY = "ios"
IOS_TRADITIONAL_DIRECTORY = "zh-HK"
IOS_LOCALIZATION_DIRECTORY = ["en", "zh"]


class LanguageParser(object):

    def parse(self, path):
        """
        解析Language资源
        """
        result = {}

        for index in range(len(LANGUAGE_LOCALIZATION_DIRECTORY)):
            result[LANGUAGE_LOCALIZATION_DIRECTORY[index]] = self.localization(
                path + "/" + LANGUAGE_RESOURCE_DIRECTORY + "/" + LANGUAGE_LOCALIZATION_DIRECTORY[index] + "/localization.xml"
            )

        return result


    def localization(self, path):
        """
        解析localization文件
        """
        print "解析" + path

        result = {}

        if os.path.exists(path):
            tree = dom.parse(path)
            root = tree.documentElement
            elements = root.getElementsByTagName("string")
            for item in elements:
                key = item.getAttribute("name")
                value = item.childNodes[0].data
                result[key] = value

        return result

class AndroidWriter(object):

    def write(self, dict, path):
        """
        写入android资源
        """
        for index in range(len(LANGUAGE_LOCALIZATION_DIRECTORY)):
            # 写入繁体
            if LANGUAGE_LOCALIZATION_DIRECTORY[index] == LANGUAGE_SIMPLE_DIRECTORY:
                self.traditional(
                    dict[LANGUAGE_LOCALIZATION_DIRECTORY[index]],
                    path + "/" + ANDROID_RESOURCE_DIRECTORY + "/" + ANDROID_TRADITIONAL_DIRECTORY
                )

            self.localization(
                dict[LANGUAGE_LOCALIZATION_DIRECTORY[index]],
                path + "/" + ANDROID_RESOURCE_DIRECTORY + "/" + ANDROID_LOCALIZATION_DIRECTORY[index]
            )



    def traditional(self, dict, parent):
        """
        写入localization文件
        """
        result = {}

        for key in dict.keys():
            result[key] = Converter('zh-hant').convert(dict[key])

        self.localization(result, parent)


    def localization(self, dict, parent):
        """
        写入localization文件
        """
        print "写入" + parent

        if not os.path.exists(parent):
            os.makedirs(parent)

        tree = dom.getDOMImplementation().createDocument(None, "resources", None)
        root = tree.documentElement

        for key in dict.keys():
            name = key.encode('utf-8')
            value = dict[key].encode('utf-8')

            if len(value) <= 0 or len(name) <= 0:
                continue

            node = tree.createElement("string")
            node.setAttribute("name", name)
            node.appendChild(tree.createTextNode(value))
            root.appendChild(node)


        with open(parent + "/strings.xml", "w") as f:
            tree.writexml(f, addindent='\t', newl='\n', encoding='utf-8')



class IosWriter(object):

    def write(self, dict, path):
        """
        写入ios资源
        """
        pass
        for index in range(len(LANGUAGE_LOCALIZATION_DIRECTORY)):
            # 写入繁体
            if LANGUAGE_LOCALIZATION_DIRECTORY[index] == LANGUAGE_SIMPLE_DIRECTORY:
                self.traditional(
                    dict[LANGUAGE_LOCALIZATION_DIRECTORY[index]],
                    path + "/" + IOS_RESOURCE_DIRECTORY + "/" + IOS_TRADITIONAL_DIRECTORY
                )

            self.localization(
                dict[LANGUAGE_LOCALIZATION_DIRECTORY[index]],
                path + "/" + IOS_RESOURCE_DIRECTORY + "/" + IOS_LOCALIZATION_DIRECTORY[index]
            )



    def traditional(self, dict, parent):
        """
        写入localization文件
        """
        result = {}

        for key in dict.keys():
            result[key] = Converter('zh-hant').convert(dict[key])

        self.localization(result, parent)


    def localization(self, dict, parent):
        """
        写入localization文件
        """
        print "写入" + parent

        if not os.path.exists(parent):
            os.makedirs(parent)

        with open(parent + "/Localizable.strings", "w") as f:
            for key in dict.keys():
                name = key.encode('utf-8')
                value = dict[key].encode('utf-8')

                if len(value) <= 0 or len(name) <= 0:
                    continue

                f.write("\"" + name + "\" = \"" + value + "\";\n")


class ExcelWriter(object):

    def write(self, dict, path):
        """
        写入excel资源
        """
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet("localization", cell_overwrite_ok=True)
        self.excel(self.table(dict), sheet)
        book.save(path + "/国际化.xlsx")

    def table(self, dict):
        """
        制表
        """
        result = []

        # 头部, 添加基础
        head = ["Key"]
        for key in dict.keys():
            head.append(key)
        result.append(head)

        # 主体, 以英文的key作为基准key
        en_dict = dict[LANGUAGE_ENGLISH_DIRECTORY]
        for en_key in en_dict.keys():
            body = [en_key]

            for language in LANGUAGE_LOCALIZATION_DIRECTORY:
                if dict[language].has_key(en_key):
                    body.append(dict[language][en_key])
                else:
                    # 占位
                    body.append("")

            result.append(body)

        return result


    def excel(self, table, sheet):
        """
        写入Excel
        """
        for column in range(len(table)):
            row_table = table[column]
            for row in range(len(row_table)):
                sheet.write(column, row, row_table[row])