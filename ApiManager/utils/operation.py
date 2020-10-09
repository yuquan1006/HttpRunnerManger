import datetime
import logging
import os
import requests
import re, hashlib
import random
import pymysql
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from django.db import DataError

from ApiManager import separator
from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo, EnvInfo, TestReports, DebugTalk, \
    TestSuite


logger = logging.getLogger('HttpRunnerManager')


def add_register_data(**kwargs):
    """
    用户注册信息逻辑判断及落地
    :param kwargs: dict
    :return: ok or tips
    """
    user_info = UserInfo.objects
    try:
        username = kwargs.pop('account')
        password = kwargs.pop('password')
        email = kwargs.pop('email')

        if user_info.filter(username__exact=username).filter(status=1).count() > 0:
            logger.debug('{username} 已被其他用户注册'.format(username=username))
            return '该用户名已被注册，请更换用户名'
        if user_info.filter(email__exact=email).filter(status=1).count() > 0:
            logger.debug('{email} 昵称已被其他用户注册'.format(email=email))
            return '邮箱已被其他用户注册，请更换邮箱'
        user_info.create(username=username, password=password, email=email)
        logger.info('新增用户：{user_info}'.format(user_info=user_info))
        return 'ok'
    except DataError:
        logger.error('信息输入有误：{user_info}'.format(user_info=user_info))
        return '字段长度超长，请重新编辑'


def add_project_data(type, **kwargs):
    """
    项目信息落地 新建时必须默认添加debugtalk.py
    :param type: true: 新增， false: 更新
    :param kwargs: dict
    :return: ok or tips
    """
    project_opt = ProjectInfo.objects
    project_name = kwargs.get('project_name')
    if type:
        if project_opt.get_pro_name(project_name) < 1:
            try:
                project_opt.insert_project(**kwargs)
                belong_project = project_opt.get(project_name=project_name)
                DebugTalk.objects.create(belong_project=belong_project, debugtalk='# debugtalk.py')
            except DataError:
                return '项目信息过长'
            except Exception:
                logging.error('项目添加异常：{kwargs}'.format(kwargs=kwargs))
                return '添加失败，请重试'
            logger.info('项目添加成功：{kwargs}'.format(kwargs=kwargs))
        else:
            return '该项目已存在，请重新编辑'
    else:
        if project_name != project_opt.get_pro_name('', type=False, id=kwargs.get(
                'index')) and project_opt.get_pro_name(project_name) > 0:
            return '该项目已存在， 请重新命名'
        try:
            project_opt.update_project(kwargs.pop('index'), **kwargs)  # testcaseinfo的belong_project也得更新，这个字段设计的有点坑了
        except DataError:
            return '项目信息过长'
        except Exception:
            logging.error('更新失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'
        logger.info('项目更新成功：{kwargs}'.format(kwargs=kwargs))

    return 'ok'


'''模块数据落地'''


def add_module_data(type, **kwargs):
    """
    模块信息落地
    :param type: boolean: true: 新增， false: 更新
    :param kwargs: dict
    :return: ok or tips
    """
    module_opt = ModuleInfo.objects
    belong_project = kwargs.pop('belong_project')
    module_name = kwargs.get('module_name')
    if type:
        if module_opt.filter(belong_project__project_name__exact=belong_project) \
                .filter(module_name__exact=module_name).count() < 1:
            try:
                belong_project = ProjectInfo.objects.get_pro_name(belong_project, type=False)
            except ObjectDoesNotExist:
                logging.error('项目信息读取失败：{belong_project}'.format(belong_project=belong_project))
                return '项目信息读取失败，请重试'
            kwargs['belong_project'] = belong_project
            try:
                module_opt.insert_module(**kwargs)
            except DataError:
                return '模块信息过长'
            except Exception:
                logging.error('模块添加异常：{kwargs}'.format(kwargs=kwargs))
                return '添加失败，请重试'
            logger.info('模块添加成功：{kwargs}'.format(kwargs=kwargs))
        else:
            return '该模块已在项目中存在，请重新编辑'
    else:
        if module_name != module_opt.get_module_name('', type=False, id=kwargs.get('index')) \
                and module_opt.filter(belong_project__project_name__exact=belong_project) \
                .filter(module_name__exact=module_name).count() > 0:
            return '该模块已存在，请重新命名'
        try:
            module_opt.update_module(kwargs.pop('index'), **kwargs)
        except DataError:
            return '模块信息过长'
        except Exception:
            logging.error('更新失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'
        logger.info('模块更新成功：{kwargs}'.format(kwargs=kwargs))
    return 'ok'


'''用例数据落地'''


def add_case_data(type, **kwargs):
    """
    用例信息落地
    :param type: boolean: true: 添加新用例， false: 更新用例
    :param kwargs: dict
    :return: ok or tips
    """
    case_info = kwargs.get('test').get('case_info')
    case_opt = TestCaseInfo.objects
    name = kwargs.get('test').get('name')
    module = case_info.get('module')
    project = case_info.get('project')
    belong_module = ModuleInfo.objects.get_module_name(module, type=False)
    config = case_info.get('config', '')
    if config != '':
        case_info.get('include')[0] = eval(config)

    try:
        if type:

            if case_opt.get_case_name(name, module, project) < 1:
                case_opt.insert_case(belong_module, **kwargs)
                logger.info('{name}用例添加成功: {kwargs}'.format(name=name, kwargs=kwargs))
            else:
                return '用例或配置已存在，请重新编辑'
        else:
            index = case_info.get('test_index')
            if name != case_opt.get_case_by_id(index, type=False) \
                    and case_opt.get_case_name(name, module, project) > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            case_opt.update_case(belong_module, **kwargs)
            logger.info('{name}用例更新成功: {kwargs}'.format(name=name, kwargs=kwargs))

    except DataError:
        logger.error('用例信息：{kwargs}过长！！'.format(kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'


'''配置数据落地'''


def add_config_data(type, **kwargs):
    """
    配置信息落地
    :param type: boolean: true: 添加新配置， fasle: 更新配置
    :param kwargs: dict
    :return: ok or tips
    """
    case_opt = TestCaseInfo.objects
    config_info = kwargs.get('config').get('config_info')
    name = kwargs.get('config').get('name')
    module = config_info.get('module')
    project = config_info.get('project')
    belong_module = ModuleInfo.objects.get_module_name(module, type=False)

    try:
        if type:
            if case_opt.get_case_name(name, module, project) < 1:
                case_opt.insert_config(belong_module, **kwargs)
                logger.info('{name}配置添加成功: {kwargs}'.format(name=name, kwargs=kwargs))
            else:
                return '用例或配置已存在，请重新编辑'
        else:
            index = config_info.get('test_index')
            if name != case_opt.get_case_by_id(index, type=False) \
                    and case_opt.get_case_name(name, module, project) > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            case_opt.update_config(belong_module, **kwargs)
            logger.info('{name}配置更新成功: {kwargs}'.format(name=name, kwargs=kwargs))
    except DataError:
        logger.error('{name}配置信息过长：{kwargs}'.format(name=name, kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'


def add_suite_data(**kwargs):
    belong_project = kwargs.pop('project')
    suite_name = kwargs.get('suite_name')
    kwargs['belong_project'] = ProjectInfo.objects.get(project_name=belong_project)

    try:
        if TestSuite.objects.filter(belong_project__project_name=belong_project, suite_name=suite_name).count() > 0:
            return 'Suite已存在, 请重新命名'
        TestSuite.objects.create(**kwargs)
        logging.info('suite添加成功: {kwargs}'.format(kwargs=kwargs))
    except Exception:
        return 'suite添加异常，请重试'
    return 'ok'


def edit_suite_data(**kwargs):
    id = kwargs.pop('id')
    project_name = kwargs.pop('project')
    suite_name = kwargs.get('suite_name')
    include = kwargs.pop('include')
    belong_project = ProjectInfo.objects.get(project_name=project_name)

    suite_obj = TestSuite.objects.get(id=id)
    try:
        if suite_name != suite_obj.suite_name and \
                TestSuite.objects.filter(belong_project=belong_project, suite_name=suite_name).count() > 0:
            return 'Suite已存在, 请重新命名'
        suite_obj.suite_name = suite_name
        suite_obj.belong_project = belong_project
        suite_obj.include = include
        suite_obj.save()
        logging.info('suite更新成功: {kwargs}'.format(kwargs=kwargs))
    except Exception:
        return 'suite添加异常，请重试'
    return 'ok'


'''环境信息落地'''


def env_data_logic(**kwargs):
    """
    环境信息逻辑判断及落地
    :param kwargs: dict
    :return: ok or tips
    """
    id = kwargs.get('id', None)
    if id:
        try:
            EnvInfo.objects.delete_env(id)
        except ObjectDoesNotExist:
            return '删除异常，请重试'
        return 'ok'
    index = kwargs.pop('index')
    env_name = kwargs.get('env_name')
    if env_name is '':
        return '环境名称不可为空'
    elif kwargs.get('base_url') is '':
        return '请求地址不可为空'
    elif kwargs.get('simple_desc') is '':
        return '请添加环境描述'

    if index == 'add':
        try:
            if EnvInfo.objects.filter(env_name=env_name).count() < 1:
                EnvInfo.objects.insert_env(**kwargs)
                logging.info('环境添加成功：{kwargs}'.format(kwargs=kwargs))
                return 'ok'
            else:
                return '环境名称重复'
        except DataError:
            return '环境信息过长'
        except Exception:
            logging.error('添加环境异常：{kwargs}'.format(kwargs=kwargs))
            return '环境信息添加异常，请重试'
    else:
        try:
            if EnvInfo.objects.get_env_name(index) != env_name and EnvInfo.objects.filter(
                    env_name=env_name).count() > 0:
                return '环境名称已存在'
            else:
                EnvInfo.objects.update_env(index, **kwargs)
                logging.info('环境信息更新成功：{kwargs}'.format(kwargs=kwargs))
                return 'ok'
        except DataError:
            return '环境信息过长'
        except ObjectDoesNotExist:
            logging.error('环境信息查询失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'


def del_module_data(id):
    """
    根据模块索引删除模块数据，强制删除其下所有用例及配置
    :param id: str or int:模块索引
    :return: ok or tips
    """
    try:
        module_name = ModuleInfo.objects.get_module_name('', type=False, id=id)
        TestCaseInfo.objects.filter(belong_module__module_name=module_name).delete()
        ModuleInfo.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('{module_name} 模块已删除'.format(module_name=module_name))
    return 'ok'


def del_project_data(id):
    """
    根据项目索引删除项目数据，强制删除其下所有用例、配置、模块、Suite
    :param id: str or int: 项目索引
    :return: ok or tips
    """
    try:
        project_name = ProjectInfo.objects.get_pro_name('', type=False, id=id)

        belong_modules = ModuleInfo.objects.filter(belong_project__project_name=project_name).values_list('module_name')
        for obj in belong_modules:
            TestCaseInfo.objects.filter(belong_module__module_name=obj).delete()

        TestSuite.objects.filter(belong_project__project_name=project_name).delete()

        ModuleInfo.objects.filter(belong_project__project_name=project_name).delete()

        DebugTalk.objects.filter(belong_project__project_name=project_name).delete()

        ProjectInfo.objects.get(id=id).delete()

    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('{project_name} 项目已删除'.format(project_name=project_name))
    return 'ok'


def del_test_data(id):
    """
    根据用例或配置索引删除数据
    :param id: str or int: test or config index
    :return: ok or tips
    """
    try:
        TestCaseInfo.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('用例/配置已删除')
    return 'ok'


def del_suite_data(id):
    """
    根据Suite索引删除数据
    :param id: str or int: test or config index
    :return: ok or tips
    """
    try:
        TestSuite.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('Suite已删除')
    return 'ok'


def del_report_data(id):
    """
    根据报告索引删除报告
    :param id:
    :return: ok or tips
    """
    try:
        TestReports.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    return 'ok'


def copy_test_data(id, name):
    """
    复制用例信息，默认插入到当前项目、莫夸
    :param id: str or int: 复制源
    :param name: str：新用例名称
    :return: ok or tips
    """
    try:
        test = TestCaseInfo.objects.get(id=id)
        belong_module = test.belong_module
    except ObjectDoesNotExist:
        return '复制异常，请重试'
    if TestCaseInfo.objects.filter(name=name, belong_module=belong_module).count() > 0:
        return '用例/配置名称重复了哦'
    test.id = None
    test.name = name
    request = eval(test.request)
    if 'test' in request.keys():
        request.get('test')['name'] = name
    else:
        request.get('config')['name'] = name
    test.request = request
    test.save()
    logging.info('{name}用例/配置添加成功'.format(name=name))
    return 'ok'


def copy_suite_data(id, name):
    """
    复制suite信息，默认插入到当前项目、莫夸
    :param id: str or int: 复制源
    :param name: str：新用例名称
    :return: ok or tips
    """
    try:
        suite = TestSuite.objects.get(id=id)
        belong_project = suite.belong_project
    except ObjectDoesNotExist:
        return '复制异常，请重试'
    if TestSuite.objects.filter(suite_name=name, belong_project=belong_project).count() > 0:
        return 'Suite名称重复了哦'
    suite.id = None
    suite.suite_name = name
    suite.save()
    logging.info('{name}suite添加成功'.format(name=name))
    return 'ok'


def add_test_reports(runner, report_name=None):
    """
    定时任务或者异步执行报告信息落地
    :param start_at: time: 开始时间
    :param report_name: str: 报告名称，为空默认时间戳命名
    :param kwargs: dict: 报告结果值
    :return:
    """
    time_stamp = int(runner.summary["time"]["start_at"])
    runner.summary['time']['start_datetime'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
    report_name = report_name if report_name else runner.summary['time']['start_datetime']
    runner.summary['html_report_name'] = report_name

    report_path = os.path.join(os.getcwd(), "reports{}{}.html".format(separator, int(runner.summary['time']['start_at'])))
    runner.gen_html_report(html_report_template=os.path.join(os.getcwd(), "templates{}extent_report_template.html".format(separator)))

    with open(report_path, encoding='utf-8') as stream:
        reports = stream.read()

    test_reports = {
        'report_name': report_name,
        'status': runner.summary.get('success'),
        'successes': runner.summary.get('stat').get('successes'),
        'testsRun': runner.summary.get('stat').get('testsRun'),
        'start_at': runner.summary['time']['start_datetime'],
        'reports': reports
    }

    test_reports_obj = TestReports.objects.create(**test_reports)
    return report_path,test_reports_obj.id


def statistics_report_timeOut(html_doc, time_ms=300.00):
    """统计报告中是否存在接口超时请求
    html_doc:html报告路径
    time_ms：超时判定的毫米
    :return：totalCaseNameList 组装后的超时用例集合列表： [ 用例：冒烟18-排班分组-全部人员更新排班表成功 下 [单接口-【排班管理】-B端更新全部员工排班分组接口, 响应时间:4634.45 ms, 用例状态:pass], 用例：xxx]
            signleTotal  超时用例列表：[单接口-【排班管理】-B端更新全部员工排班分组接口,x2,x3]
    """
    with open(html_doc, 'rb') as f:
        soup = BeautifulSoup(f.read(), "lxml")
        totalCaseNameList = list()
        signleTotal = list()
        signleUrl = list()
        # # 创建CSS选择器
        result = soup.select("ul#test-collection>li>div.test-content")  # 获取测试集合节点
        for site in result:  # 获取单个用例的位置
            totalCaseName = site.select("div.test-attributes>div>span:nth-child(1)")
            caseTotal = "用例：{} 下 ".format(totalCaseName[0].get_text())
            signleSuiteCase = site.select("ul.node-list>li")
            for s in signleSuiteCase:
                signleCase = ""
                signleurl = ""
                caseName = s.select("div>div.node-name")
                responseTime = s.select("div>span.node-duration")
                responseResult = s.select("div>span.test-status")
                responseUrl = s.select("tbody > tr:nth-child(1)>td.step-details")
                if "登录" in caseName[0].get_text(): continue # 去除登录接口的校验

                if float(responseTime[0].get_text()[15:].replace("ms", "")) >= time_ms:
                    caseTotal += "[{}接口, 响应时间:{}, 用例状态:{}]".format(caseName[0].get_text(),responseTime[0].get_text()[15:],responseResult[0].get_text())
                    signleCase +="{}接口".format(caseName[0].get_text())
                    signleurl  +="接口地址：{}".format(responseUrl[0].get_text())
                    signleUrl.append(signleurl)
                    signleTotal.append(signleCase)
            if caseTotal.endswith("]"):
                totalCaseNameList.append(caseTotal)
    print("组装超时用例集列表", totalCaseNameList)
    print("单个超时用例列表", signleTotal)
    return totalCaseNameList,dict(zip(signleTotal,signleUrl))

def callDingTalkRobot(name,text):
    # --- 钉钉机器人
    import requests
    url = 'https://oapi.dingtalk.com/robot/send?access_token=07633a4a9b6f5bddd87604ffe67021125e00d62d0eba6844cd793ad6fa9d3ce9'
    headers = {'Content-Type': 'application/json'}
    content = "通知内容：{}执行失败\n".format(name)
    content += text
    payload = {"msgtype": "text", "isAtAll": True, "text": {"content": content}}
    response = requests.post(url,headers=headers,json=payload)
    if "ok" in response.text:print("钉钉机器人调用成功：{}".format(response.text))
    else:print("钉钉机器人调用失败：{}".format(response.text))

def queryZentaoBug(sql):
    config = {'host': '192.168.1.172','port': 3306,'user': 'zentao','passwd': 'zentaodba2015','charset': 'utf8','cursorclass': pymysql.cursors.DictCursor}
    try:
        con = pymysql.connect(**config)
        con.autocommit(1)
        con.select_db("zentao")
        cur = con.cursor()
        cur.execute(sql)
        result = cur.fetchall()
    except BaseException as e:
        print("程序异常:%s"%e)
    finally:
        cur.close()
        con.close()
    #print(result)
    return result

def createrZentaoBug(suite,caseDict,report_id=0):
    """
    创建禅道bug
    :param suite: 平台套件id列表
    :param caseList: 超时接口列表
    :param report_id: 定时任务报告id
    :return:
    """
    # 禅道登录
    s = requests.Session()
    response = s.get("https://zentao.ihr360.com/zentao/user-login.html", verify=False)
    rand = re.findall("name='verifyRand' id='verifyRand' value='(.+?)'", response.text)[0]
    password = hashlib.md5((hashlib.md5("Admin@123".encode()).hexdigest() + rand).encode())
    response = s.post("https://zentao.ihr360.com/zentao/user-login.html",data={"account": "api.Report", "password": password.hexdigest(), "verifyRand": rand}, headers={"Content-Type": "application/x-www-form-urlencoded"}, verify=False)
    # 获取禅道迭代（单）接口性能优化下bug-title列表
    caseAll =[i.get("title") for i in queryZentaoBug("select title from zt_bug where project=265 and status!='closed'")]
    # print("caseList：%s"%caseList)
    # 获取套件关联项目，根据项目设置禅道指派给/模块
    obj = TestSuite.objects.get(id=int(suite[0]))
    project = obj.belong_project
    project_name = project.project_name
    caseList= caseDict.keys()
    for case in caseList:
        apiurl= caseDict[case]
        case += ",请求超时(大于300ms)" # 完善格式和bug对比
        # title重复就跳过
        if case in caseAll:
            print("准备跳过：%s"%case)
            continue
        else:
            title = case
            module, assignedTo = "240", "Damon.Shi"
            if "绩效" in project_name:
                module,assignedTo = "232","vic.zhao"
            elif "薪资" in project_name or "薪税通" in project_name or "福利管理" in project_name:
                module,assignedTo = "231","richey.liu"
            elif "组织" in project_name:
                module,assignedTo = "465","Frank.Li"
            elif "人事" in project_name:
                module,assignedTo = "229","Frank.Li"
            elif "考勤" in project_name:
                module,assignedTo = "230","jerry.xiao"
            elif "openAPI" in project_name:
                module,assignedTo = "292","david.wei"
            elif "审批中心" in project_name:
                module,assignedTo = "377","Jack.Zhao"
        # 创建禅道bug
        params = {"product": (None, "3"), "module": (None, module), "project": (None, "265"),"assignedTo": (None, assignedTo),"deadline": (None, ""), "type": (None, "codeerror"), "os": (None, "PROD"), "browser": (None, "all"),"title": (None, title), "severity": (None, "3"), "pri": (None, "2"),"steps": (None, "<p>{}      接口平台报告地址：http://192.168.1.196/api/view_report/{}/</p><p>{}</p>".format(title,report_id,apiurl)),"story": (None, ""), "keywords": (None, "内部QA"), "uid": str(random.randint(1,100000))}
        response = s.post("https://zentao.ihr360.com/zentao/bug-create-3-0-moduleID=0.html",files=params)
        if response.status_code == 200:
            print("创建用例成功%s"%case)

