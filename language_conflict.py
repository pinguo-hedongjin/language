# /usr/bin/python
# coding=utf-8

import os
import traceback
from objects import *

PROJECT = os.path.abspath(os.getcwd())


def main():
    print "开始检查Conflict"
    try:
        LanguageConflict().conflict(PROJECT)
    except Exception:
        traceback.print_exc()
        os.system('kill 0')

if __name__ == "__main__":
    main()
