import json

from django import template

from ApiManager.utils.common import update_include

register = template.Library()


@register.filter(name='data_type')
def data_type(value):
    """
    返回数据类型 自建filter
    :param value:
    :return: the type of value
    """
    return str(type(value).__name__)


@register.filter(name='convert_eval')
def convert_eval(value):
    """
    数据eval转换 自建filter
    :param value:
    :return: the value which had been eval
    """
    return update_include(eval(value))


@register.filter(name='json_dumps')
def json_dumps(value):
    return json.dumps(value, indent=4, separators=(',', ': '), ensure_ascii=False)


@register.filter(name='is_del')
def id_del(value):
    if value.endswith('已删除'):
        return True
    else:
        return False



# 新增两个过滤器。01判断列表中是否存在id，存在返回Ture 02 测试用例对象中request为字符串数据，eval转换dict获取数据中url信息
@register.filter(name='isInclude')
def isInclude(value,id):
    if str(id) in value:
        #print("该用例被引用")
        return True
    else:
        #print("该用例没有被引用")
        return False

@register.filter(name='convert_eval_url')
def convert_eval_url(value):
    """
    字符串数据eval转换dict获取数据中url信息
    :param value: # {'test': {'name': '单接口-【班次】-B端添加班次', 'variables': [{'name': 'test01'}, {'type': 'WEEKLY'}], 'validate': [{'comparator': 'equals', 'check': 'status_code', 'expected': 200}], 'extract': [{'calendarId': 'content.data.id'}], 'request': {'method': 'POST', 'url': '/web/gateway/attendance/api/schedule/calendar/add.do', 'json': {'isUpdate': True, 'workingDays': '1111100', 'weekWorkDays': [5, 6], 'typeState': 'add', 'type': '$type', 'isDefault': False, 'calendarState': True, 'monthWorkDays': [6, 13, 20, 27], 'calendarId': '', 'baseOnStatutory': True, 'name': '$name', 'updateDefault': True, 'id': '', 'error': None, 'reEnter': True}, 'headers': {'X-XSRF-TOKEN': '${getHeadersToken($cookie_token)}'}}}}
    :return: the value which had been eval
    """
    try:
        # print(eval(value))
        dicts = eval(value)
        url = dicts['test']['request']['url']
        # print(url)
    except BaseException as e:
        url = None
    return url
