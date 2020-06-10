# 集成方式

####预装环境

1. `ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

2. `sudo easy_install pip`

3. `pip install xlwt`

4. `pip install xlrd`

5. `sh update_android.sh/update_ios.sh`

####主仓库目录下

1. `git submodule add http://gitlab.kucoin.net/mobile/language.git`

2. `git submodule init&git submodule update`

###配置Shell别名

1. `vim ~/.bash_profile`

2. `alias lit='cd 工程主目录&&./language/lit.sh'`

3. `source ~/.bash_profile`

###使用说明(主仓库目录)

1. `lit pla：拉取语言仓库,并同步android资源`

2. `lit pli：拉取语言仓库,并同步ios资源`

3. `lit push origin 分支名：检查key是否重复，并推送语言仓库`

4. `lit android 分支名：提交本地改动，并推送语言仓库和同步android资源`

5. `lit ios 分支名：提交本地改动，并推送语言仓库和同步ios资源`

6. `lit diff 发版分支 业务分支：对比两个分支代码，生成对比localization表格`

7. `lit import：导入excel到语言仓库`

8. `lit export：导出语言仓库到excel`

9. `lit lint：检查key是否重复`

###使用流程

1. 增加或者修改子模块`language`下的语言包，比如`en`，如果是有占位符的字符串在`android.strings/ios.strings`文件里面增加，否则在`localization.strings`里面增加。

2. 执行`lit android 分支名/lit ios 分支名`

