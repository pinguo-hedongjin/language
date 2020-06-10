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
LANGUAGE_SIMPLE_DIRECTORY = "zh"
LANGUAGE_ENGLISH_DIRECTORY = "en"
LANGUAGE_LOCALIZATION_FILE = "localization.strings"
LANGUAGE_LOCALIZATION_DIRECTORY = [LANGUAGE_ENGLISH_DIRECTORY, LANGUAGE_SIMPLE_DIRECTORY, "ko",
                                   "fr", "de", "pt", "es",
                                   "nl", "ru", "tr", "vi",
                                   "it", "in", "ms", "hi"]

# ANDROID目录结构
ANDROID_RESOURCE_DIRECTORY = "src/main/res"
ANDROID_TRADITIONAL_DIRECTORY = "values-zh-rHK"
ANDROID_LOCALIZATION_FILE = "strings.xml"
ANDROID_LOCALIZATION_DIRECTORY = ["values", "values-zh-rCN", "values-ko-rKR",
                                  "values-fr-rFR", "values-de-rDE", "values-pt-rPT", "values-es-rES",
                                  "values-nl-rNL", "values-ru-rRU", "values-tr-rTR", "values-vi-rVN",
                                  "values-it-rIT", "values-in-rID", "values-ms-rMY", "values-hi-rIN"]

# IOS目录结构
IOS_RESOURCE_DIRECTORY = "ios"
IOS_TRADITIONAL_DIRECTORY = "zh-Hant.lproj"
IOS_LOCALIZATION_FILE = "Localizable.strings"
IOS_LOCALIZATION_DIRECTORY = ["en.lproj", "zh-Hans.lproj", "ko.lproj",
                              "fr.lproj", "de.lproj", "pt.lproj", "es.lproj",
                              "nl.lproj", "ru.lproj", "tr.lproj", "vi.lproj",
                              "it.lproj", "id.lproj", "ms.lproj", "hi.lproj"]


class LanguageParser(object):

    def __init__(self, local):
        self.local_name = local

    def parse(self, path):
        """
        解析Language资源
        """
        result = collections.OrderedDict()

        for index in range(len(LANGUAGE_LOCALIZATION_DIRECTORY)):
            result[LANGUAGE_LOCALIZATION_DIRECTORY[index]] = self.localization(
                path + "/" + LANGUAGE_LOCALIZATION_DIRECTORY[index] + "/" + self.local_name
            )

        return result

    def localization(self, path):
        """
        解析localization文件
        """
        print "解析" + path

        result = collections.OrderedDict()

        if not os.path.exists(path):
            return result

        for line in open(path):
            if line.isspace():
                continue

            key_value = line.split("=", 1)
            if len(key_value) != 2:
                print "非法的长度：" + line
            else:
                key = key_value[0].strip()
                value = key_value[1].strip()
                result[key] = value

        return result

    def __special(self, replace):
        replace = re.sub(r'\\+\"', r'"', replace)
        replace = re.sub(r'\\+\'', r"'", replace)
        replace = re.sub(r'\\+\s*n', r'\\n', replace)

        # 去除转义符号
        pattern1 = re.search(r'%\s*(\d\s*\$)*\s*[@sftd]', replace)

        index = 0
        while pattern1:
            stub = pattern1.group()

            pattern2 = re.search(r'\d', stub)
            if pattern2:
                index = pattern2.group()
            else:
                index = index + 1

            replace = replace.replace(stub, "{" + str(index) + "}", 1)
            pattern1 = re.search(r'%\s*(\d\s*\$)*\s*[@sftd]', replace)

        return replace

class LanguageWriter(object):

    def __init__(self, local):
        self.local_name = local

    def write(self, dict, path):
        """
        写入android资源
        """
        for index in range(len(LANGUAGE_LOCALIZATION_DIRECTORY)):
            self.localization(
                dict[LANGUAGE_LOCALIZATION_DIRECTORY[index]],
                path + "/" + LANGUAGE_LOCALIZATION_DIRECTORY[index]
            )

    def localization(self, dict, parent):
        """
        写入localization文件
        """
        print "写入" + parent

        if not os.path.exists(parent):
            os.makedirs(parent)

        with open(parent + "/" + self.local_name, "w") as f:

            for key in dict.keys():
                name = re.sub(r'[\r\n]+', '', key)
                value = self.__special(re.sub(r'[\r\n]+', '', dict[key]))

                if len(value) <= 0 or len(name) <= 0:
                    continue

                f.write(name + "=" + value + "\n")

    def __special(self, replace):
        # 处理占位符 %1$@ -> {1}
        replace = re.sub(
            r'%\s*(\d\s*\$)*\s*@',
            lambda it: self.__stub(it.group()),
            replace
        )

        return replace

    def __stub(self, stub):
        pattern = re.search(r'\d', stub)
        if pattern:
            return "{" + str(pattern.group()) + "}"
        else:
            return "{1}"

class LanguageLint(object):

    def lint(self, path):
        """
        检查Language资源
        """
        self.__key(path)
        self.__stub(path)

    def __key(self, path):
        """
        检查key是否重复
        """
        en = path + "/" + LANGUAGE_ENGLISH_DIRECTORY + "/" + LANGUAGE_LOCALIZATION_FILE
        if not os.path.exists(en):
            return None

        lint = []
        for line in open(en):
            if line.isspace():
                continue

            key_value = line.split("=", 1)
            if len(key_value) != 2:
                print "非法的长度：" + line
            else:
                key = key_value[0].strip()
                if lint.count(key) >= 1:
                    raise RuntimeError("存在重复key:" + key)
                else:
                    lint.append(key)

    def __stub(self, path):
        """
        检查stub是否对应
        """
        # 获取
        dict = LanguageParser(LANGUAGE_LOCALIZATION_FILE).parse(path)

        # 以英文为标准
        en_dict = dict[LANGUAGE_ENGLISH_DIRECTORY]
        for language, language_dict in dict.items():
            if language == LANGUAGE_ENGLISH_DIRECTORY:
                continue

            for language_key, language_value in language_dict.items():
                if self.__count(language_value) == self.__count(en_dict[language_key]):
                    continue

                raise RuntimeError("language：" + language + ", language_key:" + language_key + "占位符不对应")

    def __count(self, content):
        return len(re.compile(r'\{[\s\n]*\d[\s\n]*\}').findall(content))

class LanguageConflict(object):
    def conflict(self, path):
        """
        检查Language资源
        """
        self.iter(path, lambda path: self.check(path))

    def iter(self, path, func):
        """
        迭代Language文件
        """
        for root, dirs, files in os.walk(path):
            for name in files:
                func(os.path.join(root, name))

    def check(self, path):
        """
        检查冲突文件
        """
        if not path.endswith(".py") and not path.endswith(".sh") and not path.endswith(".strings"):
            return None
        with open(path, "r+") as f:
            if re.search(r'<+[\s\n]+HEAD', f.read()) != None:
                raise RuntimeError("糟糕，发生了冲突：" + path)

class LanguageDiff(object):

    def diff(self, master_dict, feature_dict):
        """
        对比Language文件,新增、删除、修改
        """
        master_en_dict = master_dict[LANGUAGE_ENGLISH_DIRECTORY]
        feature_en_dict = feature_dict[LANGUAGE_ENGLISH_DIRECTORY]

        # 新增
        add_dict = self.create_dict()
        for feature_language_key, feature_language_value in feature_en_dict.items():
            if not master_en_dict.has_key(feature_language_key):
                self.copy_dict(feature_language_key, feature_dict, add_dict)

        add_table = ExcelWriter().convert(add_dict)
        self.insert_action(add_table, "新增")

        # 删除
        remove_dict = self.create_dict()
        for master_language_key, master_language_value in master_en_dict.items():
            if not feature_en_dict.has_key(master_language_key):
                self.copy_dict(master_language_key, master_dict, remove_dict)

        remove_table = ExcelWriter().convert(remove_dict)
        del remove_table[0]
        self.insert_action(remove_table, "移除")

        # 修改
        modify_dict = self.create_dict()
        for feature_language_key, feature_language_value in feature_en_dict.items():
            if not master_en_dict.has_key(feature_language_key):
                continue

            is_modify = False
            for language in LANGUAGE_LOCALIZATION_DIRECTORY:
                master_language_dict = master_dict[language]
                feature_language_dict = feature_dict[language]
                if self.get_safe(feature_language_key, master_language_dict) != self.get_safe(feature_language_key, feature_language_dict):
                    is_modify = True
                    break

            if is_modify:
                self.copy_dict(feature_language_key, feature_dict, modify_dict)

        modify_table = ExcelWriter().convert(modify_dict)
        del modify_table[0]
        self.insert_action(modify_table, "修改")

        return add_table + remove_table + modify_table

    def create_dict(self):
        language_dict = collections.OrderedDict()
        for language in LANGUAGE_LOCALIZATION_DIRECTORY:
            language_dict[language] = collections.OrderedDict()
        return language_dict

    def copy_dict(self, key, src_dict, dest_dict):
        for language in LANGUAGE_LOCALIZATION_DIRECTORY:
            if src_dict[language].has_key(key):
                dest_dict[language][key] = src_dict[language][key]

    def insert_action(self, table, action):
        for row in table:
            row.insert(0, action)

    def get_safe(self, key, dict):
        if dict.has_key(key):
            return dict[key]
        else:
            return None

class LanguageSort(object):

    def sort(self, parent):
        # 读取文件内容
        dict = LanguageParser().localization(parent + "/" + LANGUAGE_LOCALIZATION_FILE)

        # 排序文件内容
        dict = self.__sort(dict)

        # 重新写入文件
        LanguageWriter().localization(dict, parent)

    def __sort(self, dict):
        result = collections.OrderedDict()
        for it in sorted(dict.items(), key=lambda it: it[0]):
            result[it[0]] = it[1]

        return result

class AndroidWriter(object):

    def write(self, dict, path):
        """
        写入Android资源
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
        result = collections.OrderedDict()

        for key, value in dict.items():
            result[key] = Converter('zh-hant').convert(unicode(value, 'utf-8'))

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
            value = self.__special(dict[key].encode('utf-8'))

            if len(value) <= 0 or len(name) <= 0:
                continue

            node = tree.createElement("string")
            node.setAttribute("name", name)
            node.appendChild(tree.createTextNode(value))
            root.appendChild(node)

        with open(parent + "/" + ANDROID_LOCALIZATION_FILE, "w") as f:
            tree.writexml(f, addindent='\t', newl='\n', encoding='utf-8')

    def __special(self, replace):
        # 处理单引号转义
        replace = re.sub(r'\\*\'', r'\'', replace)

        # 处理占位符 {1} -> %1$s
        count = len(re.compile(r'\{[\s\n]*\d[^\}]*\}').findall(replace))
        replace = re.sub(
            r'\{[\s\n]*\d[^\}]*\}',
            lambda it: self.__stub(it.group(), count),
            replace
        )

        return replace

    def __stub(self, stub, count):
        if count == 1:
            return "%s"
        else:
            pattern = re.search(r'\d', stub)
            if pattern:
                return "%" + str(pattern.group()) + "$s"
            else:
                raise RuntimeError("没有位置下标")

class AndroidRefactor(object):

    def refactor(self, dict, path):
        """
        重构Android资源
        """
        self.iter(path, lambda file: self.file(dict, file))

    def iter(self, path, func):
        """
        迭代Android文件
        """
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.startswith(".*"):
                    continue
                func(os.path.join(root, name))
            for name in dirs:
                if name.startswith(".") or name == "build" or name == "libs":
                    continue

    def file(self, dict, path):
        """
        重构Android文件
        """
        if not (path.endswith(".xml") or path.endswith(".java") or path.endswith(".kt")):
            return None

        with open(path, "r+") as f:
            previous = f.read()
            replace = previous

            for key, value in dict.items():
                if path.endswith(".xml"):
                    replace = re.sub(
                        r'@[\n\s]*string[\n\s]*/[\n\s]*' + key + r'[\n\s]*"',
                        lambda it: r'@string/' + value + r'"',
                        replace
                    )
                    replace = re.sub(
                        r'@[\n\s]*string[\n\s]*/[\n\s]*' + key + r'[\n\s]*<',
                        lambda it: r'@string/' + value + r'<',
                        replace
                    )
                else:
                    # 换行
                    replace = re.sub(
                        r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'\r\n',
                        lambda it: r'R.string.' + value + r'\r\n',
                        replace
                    )
                    # 空格
                    replace = re.sub(
                        r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'\s',
                        lambda it: r'R.string.' + value + r' ',
                        replace
                    )
                    # 注释
                    replace = re.sub(
                        r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'//',
                        lambda it: r'R.string.' + value + r'//',
                        replace
                    )
                    # 括号
                    replace = re.sub(
                        r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'\)',
                        lambda it: r'R.string.' + value + r')',
                        replace
                    )
                    # 逗号
                    replace = re.sub(
                        r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r',',
                        lambda it: r'R.string.' + value + r',',
                        replace
                    )
                    # 分号
                    replace = re.sub(
                        r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r';',
                        lambda it: r'R.string.' + value + r';',
                        replace
                    )

            if previous != replace:
                print "重构文件：" + path

                # 清空文件
                f.seek(0)
                f.truncate()

                # 重写文件
                f.write(replace)
            else:
                print "跳过文件：" + path

class IosWriter(object):

    def write(self, dict, path):
        """
        写入ios资源
        """
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
        result = collections.OrderedDict()

        for key, value in dict.items():
            result[key] = Converter('zh-hant').convert(unicode(value, 'utf-8'))

        self.localization(result, parent)

    def localization(self, dict, parent):
        """
        写入localization文件
        """
        print "写入" + parent

        if not os.path.exists(parent):
            os.makedirs(parent)

        with open(parent + "/" + IOS_LOCALIZATION_FILE, "w") as f:
            for key in dict.keys():
                name = key.encode('utf-8')
                value = self.__special(dict[key].encode('utf-8'))

                if len(value) <= 0 or len(name) <= 0:
                    continue

                f.write("\"" + name + "\" = \"" + value + "\";\n")

    def __special(self, replace):
        # 处理双引号转义
        replace = re.sub(r'\\*\"', r'\"', replace)

        # 处理占位符 {1} -> %1$@
        count = len(re.compile(r'\{[\s\n]*\d[^\}]*\}').findall(replace))
        replace = re.sub(
            r'\{[\s\n]*\d[^\}]*\}',
            lambda it: self.__stub(it.group(), count),
            replace
        )

        return replace

    def __stub(self, stub, count):
        if count == 1:
            return "%@"
        else:
            pattern = re.search(r'\d', stub)
            if pattern:
                return "%" + str(pattern.group()) + "$@"
            else:
                raise RuntimeError("没有位置下标")

class LanguageRefactor(object):

    def refactor(self, list, path):
        """
        重构Language资源
        """
        # 检查文件引用
        self.iter(path, lambda file: self.file(list, file))
        # 打印无用资源
        for key in list:
            print "无用key:" + key

    def iter(self, path, func):
        """
        迭代Android文件
        """
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.startswith(".*"):
                    continue
                func(os.path.join(root, name))
            for name in dirs:
                if name.startswith(".") or name == "build" or name == "libs":
                    continue

    def file(self, list, path):
        """
        重构Android文件
        """
        if not (path.endswith(".xml") or path.endswith(".java") or path.endswith(".kt")):
            return None

        with open(path, "r+") as f:
            content = f.read()

            for key in list[:]:
                if path.endswith(".xml"):
                    # 布局
                    if re.search(r'@[\n\s]*string[\n\s]*/[\n\s]*' + key + r'[\n\s]*"', content):
                        list.remove(key)
                    # 样式
                    if re.search(r'@[\n\s]*string[\n\s]*/[\n\s]*' + key + r'[\n\s]*<', content):
                        list.remove(key)
                else:
                    # 换行
                    if re.search(r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'\r\n', content):
                        list.remove(key)
                    # 空格
                    if re.search(r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'\s', content):
                        list.remove(key)
                    # 注释
                    if re.search(r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'/', content):
                        list.remove(key)
                    # 括号
                    if re.search(r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r'\)', content):
                        list.remove(key)
                    # 逗号
                    if re.search(r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r',', content):
                        list.remove(key)
                    # 分号
                    if re.search(r'R[\n\s]*.[\n\s]*string[\n\s]*.[\n\s]*' + key + r';', content):
                        list.remove(key)

class IosRefactor(object):

    def refactor(self, dict, path):
        """
        重构Ios资源
        """
        self.iter(path, lambda file: self.file(dict, file))

    def iter(self, path, func):
        """
        迭代Ios文件
        """
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.startswith(".*"):
                    continue
                func(os.path.join(root, name))

    def file(self, dict, path):
        """
        重构Ios文件
        """
        if not path.endswith(".swift"):
            return None
        with open(path, "r+") as f:
            previous = f.read()
            replace = previous

            for _key, _value in dict.items():
                key = _key.encode('utf-8')
                value = _value.encode('utf-8')
                try:
                    replace = re.sub(
                        r'LOCALIZED[\n\s]*\([\n\s]*key[\n\s]*:[\n\s]*"' + key + r'"',
                        lambda it: r'LOCALIZED(key: "' + value + r'"',
                        replace
                    )
                    replace = re.sub(
                        r'\.kcText[\n\s]*=[\n\s]*"' + key + r'"',
                        lambda it: r'.kcText = "' + value + r'"',
                        replace
                    )
                    replace = re.sub(
                        r'\.kcPlaceholderSwitch[\n\s]*=[\n\s]*"' + key + r'"',
                        lambda it: r'.kcPlaceholderSwitch = "' + value + r'"',
                        replace
                    )
                    replace = re.sub(
                        r'\.kcSetTitle\([\n\s]*"' + key + r'"',
                        lambda it: r'.kcSetTitle("' + value + r'"',
                        replace
                    )
                except:
                    print "error = " + key

            if previous != replace:
                print "重构文件：" + path

                # 清空文件
                f.seek(0)
                f.truncate()

                # 重写文件
                f.write(replace)
            else:
                print "跳过文件：" + path

class ExcelParser(object):

    def parse(self, path):
        return self.dict(self.table(path))

    def table(self, path):
        """
        Excel制表：二维数组
        """
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_name("localization")

        table = []
        for col in range(sheet.ncols):
            language = []
            for row in range(sheet.nrows):
                language.append(sheet.cell(row, col).value)
            table.append(language)

        return table

    def dict(self, table):
        """
        Excel转字典
        """
        result = collections.OrderedDict()

        key = table[0]
        for index in range(len(table)):
            language = table[index][0]
            if language not in LANGUAGE_LOCALIZATION_DIRECTORY:
                continue

            for row in range(len(table[index])):
                if row == 0:
                    # 第一行代表语言名字
                    result[language] = collections.OrderedDict()
                else:
                    name = key[row]
                    value = table[index][row]
                    result[language][name] = value

        return result

class ExcelParser(object):

    def dict(self, path):
        """
        解析为字典
        """
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_name("localization")

        dict = collections.OrderedDict()
        for col in range(sheet.ncols):
            if col == 0:
                continue

            language = collections.OrderedDict()
            for row in range(sheet.nrows):
                if row == 0:
                    dict[sheet.cell(row, col).value] = language
                else:
                    key = sheet.cell(row, 0).value
                    value = sheet.cell(row, col).value
                    language[key] = value

        return dict

    def table(self, path):
        """
        解析为列表
        """
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_name("localization")

        table = []
        for row in range(sheet.nrows):
            language = []
            for col in range(sheet.ncols):
                language.append(sheet.cell(row, col).value)
            table.append(language)

        return table

class ExcelWriter(object):

    def convert(self, dict):
        """
        转table
        """
        table = []

        # 头部
        head = ["Key"]
        for key in dict.keys():
            head.append(key)
        table.append(head)

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

            table.append(body)

        return table

    def dict(self, dict, path):
        """
        写入excel资源
        """
        self.table(self.convert(dict), path)

    def table(self, table, path):
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet("localization", cell_overwrite_ok=True)

        for col in range(len(table)):
            for row in range(len(table[col])):
                sheet.write(col, row, table[col][row])

        book.save(path)
