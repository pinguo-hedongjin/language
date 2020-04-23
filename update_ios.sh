#!/bin/bash
#1.同步submodule
git pull --rebase
#2.生成ios语言包
python language_to_ios.py