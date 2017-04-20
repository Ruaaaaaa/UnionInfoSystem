# Union Info System
## 开发环境
0. Python 2.7  
1. Django 1.11+

## 开发流程示例
0. git checkout master && git pull origin master（确保基于最新的master开发）
2. git checkout -b gyc/homepage（建立新分支，以 [自己名字]/[分支作用] 命名）
2. 在自己的分支上进行开发
3. 开发完了
4. 再次git pull origin master（解决可能和master存在的冲突）
5. 在本仓库中提出Pull request申请，等待代码review
6. 负责人review通过后，会把你的分支和master合并
7. 一次开发结束，分支删除

## 语法规范
0. 函数名使用小驼峰式，如isValidUser(args)
1. 普通变量使用下划线式，如is_valid_user
2. 常量使用大写下划线式，如IS_VALID_USER
3. view的html采用下划线式，如admin_home.html
4. Django模版渲染内容内部两端要空格，如{% username %}
5. 建议函数之间间隔2行
6. 如有其他未定之处请补充
