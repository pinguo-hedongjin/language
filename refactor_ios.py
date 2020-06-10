# /usr/bin/python
# coding=utf-8

import os
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    print "读取映射关系"
    dict = KeyRefactor().refactor(PROJECT + "/ios_map.xlsx")

    print "开始重构Ios"
    # IosRefactor().refactor(dict, PROJECT + "/../KuCoin")
    # IosRefactor().refactor(dict, PROJECT + "/../../Modularization/KCUIKit/KCUIKit")
    # IosRefactor().refactor(dict, PROJECT + "/../../Modularization/KCCommonKit/KCCommonKit")
    # IosRefactor().refactor(dict, PROJECT + "/../../Modularization/KCComBusiness/KCComBusiness")
    IosRefactor().refactor(dict, PROJECT + "/../../Modularization/KuMEXKit/KuMEXKit")
    
    

if __name__ == "__main__":
    main()
