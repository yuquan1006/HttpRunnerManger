基于HttpRunner的接口自动化测试平台: `HttpRunner`_, `djcelery`_ and `Django`_. HttpRunner手册: http://cn.httprunner.org/

Key Features
------------

- 项目管理：新增项目、列表展示及相关操作，支持用例批量上传(标准化的HttpRunner json和yaml用例脚本)
- 模块管理：为项目新增模块，用例和配置都归属于module，module和project支持同步和异步方式
- 用例管理：分为添加config与test子功能，config定义全部变量和request等相关信息 request可以为公共参数和请求头，也可定义全部变量
- 场景管理：可以动态加载可引用的用例，跨项目、跨模快，依赖用例列表支持拖拽排序和删除
- 运行方式：可单个test，单个module，单个project，也可选择多个批量运行，支持自定义测试计划，运行时可以灵活选择配置和环境，
- 分布执行：单个用例和批量执行结果会直接在前端展示，模块和项目执行可选择为同步或者异步方式，
- 环境管理：可添加运行环境，运行用例时可以一键切换环境
- 报告查看：所有异步执行的用例均可在线查看报告，可自主命名，为空默认时间戳保存，
- 定时任务：可设置定时任务，遵循crontab表达式，可在线开启、关闭，完毕后支持邮件通知
- 持续集成：jenkins对接，开发中。。。

本地开发环境部署
--------
1. 安装mysql数据库服务端(推荐5.7+),并设置为utf-8编码，创建相应HttpRunner数据库，设置好相应用户名、密码，启动mysql

2. 修改:HttpRunnerManager/HttpRunnerManager/settings.py里DATABASES字典和邮件发送账号相关配置
   ```python
        DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'HttpRunner',  # 新建数据库名
            'USER': 'root',  # 数据库登录名
            'PASSWORD': 'lcc123456',  # 数据库登录密码
            'HOST': '127.0.0.1',  # 数据库所在服务器ip地址
            'PORT': '3306',  # 监听端口 默认3306即可
        }
    }

    EMAIL_SEND_USERNAME = 'username@163.com'  # 定时任务报告发送邮箱，支持163,qq,sina,企业qq邮箱等，注意需要开通smtp服务
    EMAIL_SEND_PASSWORD = 'password'     # 邮箱密码
    ```
3. 安装rabbitmq消息中间件，启动服务，访问：http://host:15672/#/ host即为你部署rabbitmq的服务器ip地址
   username：guest、Password：guest, 成功登陆即可
    ```bash
        service rabbitmq-server start
    ```

4. 修改:HttpRunnerManager/HttpRunnerManager/settings.py里worker相关配置
    ```python
        djcelery.setup_loader()
        CELERY_ENABLE_UTC = True
        CELERY_TIMEZONE = 'Asia/Shanghai'
        BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672//'  # 127.0.0.1即为rabbitmq-server所在服务器ip地址
        CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
        CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
        CELERY_ACCEPT_CONTENT = ['application/json']
        CELERY_TASK_SERIALIZER = 'json'
        CELERY_RESULT_SERIALIZER = 'json'

        CELERY_TASK_RESULT_EXPIRES = 7200  # celery任务执行结果的超时时间，
        CELERYD_CONCURRENCY = 10  # celery worker的并发数 也是命令行-c指定的数目 根据服务器配置实际更改 默认10
        CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，默认100
    ```

5. 命令行窗口执行pip install -r requirements.txt 安装工程所依赖的库文件

6. 命令行窗口切换到HttpRunnerManager目录 生成数据库迁移脚本,并生成表结构
    ```bash
        python manage.py makemigrations ApiManager #生成数据迁移脚本
        python manage.py migrate  #应用到db生成数据表
    ```

7. 创建超级用户，用户后台管理数据库，并按提示输入相应用户名，密码，邮箱。 如不需用，可跳过此步骤
    ```bash
        python manage.py createsuperuser
    ```

8. 启动服务,
    ```bash
        python manage.py runserver 0.0.0.0:8000
    ```

9. 启动worker, 如果选择同步执行并确保不会使用到定时任务，那么此步骤可忽略
    ```bash
        python manage.py celery -A HttpRunnerManager worker --loglevel=info  #启动worker
        python manage.py celery beat --loglevel=info #启动定时任务监听器
        celery flower #启动任务监控后台
    ```

10. 访问：http://localhost:5555/dashboard 即可查看任务列表和状态

11. 浏览器输入：http://127.0.0.1:8000/api/register/  注册用户，开始尽情享用平台吧

12. 浏览器输入http://127.0.0.1:8000/admin/  输入步骤6设置的用户名、密码，登录后台运维管理系统，可后台管理数据

### 生产环境uwsgi+nginx部署参考：https://www.jianshu.com/p/d6f9138fab7b

新手入门手册
-----------
1、首先需要注册一个新用户,注册成功后会自动跳转到登录页面，正常登录即可访问页面
![注册页面](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/register_01.jpg)<br>
![登录页面](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/login_01.jpg)<br>

2、登陆后默认跳转到首页，左侧为菜单栏，上排有快捷操作按钮，当前只简单的做了项目，模块，用例，配置的统计
![首页](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/index_01.jpg)<br>
<br>
3、首先应该先添加一个项目，用例都是以项目为维度进行管理, 注意简要描述和其他信息可以为空, 添加成功后会自动重定向到项目列表
![新增项目](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_project_01.png)<br>
<br>
4、支持对项目进行二次编辑,也可以进行筛选等,项目列表页面可以选择单个项目运行，也可以批量运行，注意：删除操作会强制删除该项目下所有数据，请谨慎操作
![项目列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/project_list_01.jpg)<br>
<br>
5、当前项目可以新增模块了，之后用例或者配置都会归属模块下，必须指定模块所属的项目,模块列表与项目列表类似，故不赘述
![新增模块](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_module_01.jpg)<br>
<br>
6、新增用例，遵循HtttpRuunner脚本规范，可以跨项目，跨模块引用用例，支持拖拽排序，动态添加和删减，极大地方便了场景组织, HttpRunner用例编写很灵活，建议规范下编写方式
![新增用例01](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_01.jpg)<br>
<br>
![新增用例02](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_02.jpg)<br>
<br>
![新增用例03](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_03.jpg)<br>
<br>
![新增用例04](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_04.jpg)<br>
<br>
7、新增配置，可定义全局变量，全局hook，公共请求参数和公共headers,一般可用于测试环境，验证环境切换配置，具体用法参考HttpRunner手册
![新增配置](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_config_01.jpg)<br>
<br>
8、支持添加项目级别定时任务，模块集合的定时任务，遵循crontab表达式, 模块列表为空默认为整个项目，定时任务支持选择环境和配置
![添加任务](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_tasks_01.jpg)<br>
9、定时任务列表可以对任务进行开启或者关闭、删除，不支持二次更改
![任务列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/tasks_list_01.jpg)<br>
<br>
10、用例列表运行用例可以选择单个，批量运行，鼠标悬浮到用例名称后会自动展开依赖的用例，方便预览，鼠标悬浮到对应左边序列栏会自动收缩,只能同步运行
![用例列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/test_list_01.jpg)<br>
<br>
11、项目和模块列表可以选择单个，或者批量运行，可以选择运行环境，配置等，支持同步、异步选择，异步支持自定义报告名称，默认时间戳命名
![模块列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/module_list_01.jpg)<br>
<br>
12、异步运行的用例还有定时任务生成的报告均会存储在数据库，可以在线点击查看，当前不提供下载功能
![报告持久化](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/report_list_01.jpg)<br>
<br>
13、高大上的报告(基于extentreports实现), 可以一键翻转主题哦
![最终报告01](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/reports_01.jpg)<br>
<br>
![最终报告02](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/reports_02.jpg)<br>




#########################################################################################################################################################



概述
         httprunner在 2.0 版本中，功能实现方面变化最大的有两部分，测试用例的组织描述方式，以及 HttpRunner 本身的模块化拆分。除了这两大部分的改造，2.0 版本对于测试报告展现、性能测试支持、参数传参机制等一系列功能特性都进行了较大的优化和提升。



TIPS:

                        httprunnerV2中对测试用例格式有严格要求，如在用例中传入未定义的变量或者函数。那该用例会直接报错导致服务器500。请大家在编写用例时候务必注意该问题。





更新内容(底层）：


变更项	详细说明	方案	预期时间	
负责人



状态

HM平台后端引用模块和方法	V2版本中部分库和方法出现变更，先需要同步到HM平台后端中	主项目文件排查，后端引用和方法修改	8h	york	本地完成，带更新服务器
数据-测试用例结构-断言层	V2版本中测试用例结构-断言出现变更，需更新当前数据库用例-断言	数据修复：1 备份当前数据库 2 生成更新sql脚本	8h	york	本地完成，带更新服务器
新增、编辑测试用例断言落库和显示逻辑修改	
V2版本中测试用例结构-断言出现变更，需更新后端和前端对于的新增 编辑用例逻辑和显示

修改后端和前端对于的新增 编辑用例逻辑和显示	8h	york	本地完成，带更新服务器
数据-测试用例结构-配置层	V2版本中测试用例结构-配置层。base_url位置变更 导致运行无法获取base_url	修改后端获取config中base_url获取方式	4h	york	本地完成，带更新服务器
更新debugtalk加载机制	V2版本中debugtalk文件无法加载到	修改加载机制，由向上->向下一层	8h	york	本地完成，带更新服务器
更新多项目用例执行，debugtalk获取机制

多项目用例执行，debugtalk只能获取一个.	修改获取机制，将多项目debugtalk文件合并到第一个中	8h	york	本地完成，带更新服务器
irenshi-token获取	irenshi-token存在重定向无法直接从返回数据中获取	修改返回逻辑，增加req_headers，可以改数据中获取到token	4h	york	本地完成，带更新服务器
同步测试报告	V2测试结果数据集合和V1数据集合结构发送变更	1 使用V2对于测试报告模板或重写V1测试报告模板，修改后端测试报告生成逻辑 	12h	york	本地完成，带更新服务器
异步测试报告	V2测试结果数据集合和V1数据集合结构发送变更 且模板引擎需符合jinja2模板格式	1复制并修改上一步测试报告模板，修改部分语法(因为jinja2模板引擎和django语法有一点不一致). 2 修改后端生成测试报告的调用逻辑	8h	york	本地完成，带更新服务器
irenshi_跨环境运行对于请求地址

登录接口无须输入登录地址，自动按照运行环境请求对于环境的登录接口	修改后端编译url逻辑	4h	york	本地完成，带更新服务器
老的接口超时监控重写	V1接口超时监控从测试报告中获取数据判断，由于V2测试报告变更，故舍弃之前的重写从测试数据中直接获取数据并判断	后端定时任务中新增从测试数据集合中获取数据并判断时长，组装超时数据集合	8h	york	本地完成，带更新服务器
变量$支持jmeter中${变量名}写	1 变量写法现支持 $变量 和￥${变量}  . 2 $转义 使用 $$	变量获取正则表达式修改	2h	york	本地完成，带更新服务器






更新时间：
2021-03-29 18：00~2021-03-29 20：00  期间请无法操作平台。请知晓







更新后问题记录：
问题描述	问题截图	问题发生时间	提交问题者
例：批量执行用例 服务器500。  





2021-03-27 21：10	york





















































