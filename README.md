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
5. git push origin gyc/homepage（将你的分支推送上来）
6. 提出Pull request申请，等待代码review
7. 负责人review通过后，会把你的分支和master合并
8. 一次开发结束，分支删除

## 文件结构
三个个App：**base**，**dashboard** 和 **participation**。  
基础共用的view、api写在base下，和管理员后台相关的view、api写在dashboard下；和教师参与相关的view、api写在participation下。  

## JSON响应规范
成功: {status: 'success', msg: '我是成功后提示给用户的信息', data: { 我是传递给前端的数据 } }   
失败: {status: 'error', msg: '我是失败后提示给用户的信息'}   

## api与views
原则上 views.py 中不能直接与数据库交互，读写数据库的数据都需要在 api.py 中写相应的函数进行调用，尽量使 api.py 中的函数可重用性更强。

## sessions
base下的 sessions.py 提供了基础的session操作，请阅读。

## decorators
base下的 decorators.py 提供了 require_login 和 require_admin 两个装饰器，用于页面访问时的身份检查，请阅读。

## model
目前所有的表写在base的model中。  

## 全局常量
全局共享的常量存放在 **/InfoSystem/shared.py** 中。  

## 语法规范
0. 函数名使用小驼峰式，如isValidUser(args)
1. 普通变量使用下划线式，如is_valid_user
2. 常量使用大写下划线式，如IS_VALID_USER
3. view的html采用下划线式，如admin_home.html
4. Django模版渲染内容内部两端要空格，如{{ username }}
5. 建议函数之间间隔2行
6. 如有其他未定之处请补充
