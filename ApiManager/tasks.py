# Create your tasks here
from __future__ import absolute_import, unicode_literals

import os
import shutil

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from ApiManager.models import ProjectInfo
from ApiManager.utils.common import timestamp_to_datetime
from ApiManager.utils.emails import send_email_reports
from ApiManager.utils.operation import add_test_reports,statistics_report_timeOut
from ApiManager.utils.runner import run_by_project, run_by_module, run_by_suite
from ApiManager.utils.testcase import get_time_stamp
from httprunner import HttpRunner, logger


@shared_task
def main_hrun(testset_path, report_name):
    """
    用例运行
    :param testset_path: dict or list
    :param report_name: str
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    runner.run(testset_path)
    shutil.rmtree(testset_path)

    runner.summary = timestamp_to_datetime(runner.summary)
    report_path = add_test_reports(runner, report_name=report_name)
    os.remove(report_path)


@shared_task
def project_hrun(name, base_url, project, receiver):
    """
    异步运行整个项目
    :param env_name: str: 环境地址
    :param project: str
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    id = ProjectInfo.objects.get(project_name=project).id

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    run_by_project(id, base_url, testcase_dir_path)

    runner.run(testcase_dir_path)
    shutil.rmtree(testcase_dir_path)

    runner.summary = timestamp_to_datetime(runner.summary)
    report_path = add_test_reports(runner, report_name=name)

    if receiver != '':
        send_email_reports(receiver, report_path, name=name)
    os.remove(report_path)


@shared_task
def module_hrun(name, base_url, module, receiver):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    module = list(module)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    try:
        for value in module:
            run_by_module(value[0], base_url, testcase_dir_path)
    except ObjectDoesNotExist:
        return '找不到模块信息'

    runner.run(testcase_dir_path)

    shutil.rmtree(testcase_dir_path)
    runner.summary = timestamp_to_datetime(runner.summary)
    report_path = add_test_reports(runner, report_name=name)

    if receiver != '':
        send_email_reports(receiver, report_path, name=name)
    os.remove(report_path)


@shared_task
def suite_hrun(name, base_url, suite, receiver):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    suite = list(suite)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    try:
        for value in suite:
            run_by_suite(value[0], base_url, testcase_dir_path)
    except ObjectDoesNotExist:
        return '找不到Suite信息'

    runner.run(testcase_dir_path)

    shutil.rmtree(testcase_dir_path)

    runner.summary = timestamp_to_datetime(runner.summary)
    report_path = add_test_reports(runner, report_name=name)
    # 处理报告结果失败，发送失败主题邮件
    if not runner.summary.get('success',None):
        FailName = []
        for i in runner.summary.get('details'):
            if i.get('success') == False:
                FailName.append(i.get('name'))
        # subjects = "定时任务出现错误情况预警通知"
        status="【失败】"
        bodyText = "{}定时任务执行错误用例如下：<br>&emsp; {} <br> 请套件相关维护人员及时确认！！！".format(name, '<br> &emsp;'.join(FailName))
        send_email_reports(receiver,report_path,name=name,bodyText=bodyText,status=status)
        os.remove(report_path)
        return ""

    # 处理接口响应时长超时，发送告警邮件
    timeOut_result = statistics_report_timeOut()
    if timeOut_result:
        status = "【告警】"
        bodyText = "{}定时任务执行接口时长告警用例如下：<br>&emsp; {} <br> ".format(name, '<br> &emsp;'.join(timeOut_result))
        send_email_reports(receiver, report_path, name=name, bodyText=bodyText, status=status)
    
    if receiver != '':
        send_email_reports(receiver, report_path, name=name)
    os.remove(report_path)