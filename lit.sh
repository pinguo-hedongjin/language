#!/bin/bash
case $1 in
# 当前目录为父目录
# 同步分支,并同步到android语言包
pla)
  cd language
  git pull --rebase
  python language_conflict.py
  python language_lint.py
  python language_to_android.py
  cd ..
  ;;
# 同步分支,并同步到ios语言包
pli)
  cd language
  git pull --rebase
  python language_conflict.py
  python language_lint.py
  python language_to_ios.py
  cd ..
  ;;
# 提交分支
push)
  cd language
  python language_conflict.py
  python language_lint.py
  git push $2 $3
  cd ..
  ;;
# 添加android语言
android)
  cd language
  git add .
  python language_lint.py
  git commit -m "add language"
  git pull --rebase
  python language_conflict.py
  python language_lint.py
  git push origin $2
  python language_to_android.py
  cd ..
  ;;
# 添加ios语言
ios)
  cd language
  git add .
  python language_lint.py
  git commit -m "add language"
  git pull --rebase
  python language_conflict.py
  python language_lint.py
  git push origin $2
  python language_to_ios.py
  cd ..
  ;;
# diff语言
diff)
  cd language
  python language_diff.py $2 $3
  cd ..
  ;;
# import语言
import)
  cd language
  python excel_to_language.py
  cd ..
  ;;
# export语言
export)
  cd language
  python language_to_excel.py
  cd ..
  ;;
# lint语言
lint)
  cd language
  python language_conflict.py
  python language_lint.py
  cd ..
  ;;
*)
  echo "无法识别的命令，支持：pla、pli、push、android、ios、diff、import、export、lint"
  ;;
esac