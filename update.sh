#!/bin/bash
#1.同步submodule
git submodule update
#2.进入script目录
cd script
#3.生成android语言包
python language_to_android.py
#4.生成ios语言包
python language_to_ios.py
#5.回退上级目录
cd ..
