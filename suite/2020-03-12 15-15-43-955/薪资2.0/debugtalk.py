# debugtalk.py

#!/usr/bin/env python
#coding:utf-8

#Author:xiemengting
import re,os,time,datetime
import calendar

# 获取请求头部中token
def getHeadersToken(req_headers):
    try:
        # TODO: write code...
        result = re.findall("XSRF-TOKEN=(.{36})", req_headers)[0]
        return result
    except Exception as e:
        print("获取请求头部中token失败，请检查问题。可能原因:{}".format(e))
        raise e

def getMonthFirstDayAndLastDay(year=None, month=None):
    """
    :param year: 年份，默认是本年，可传int或str类型
    :param month: 月份，默认是本月，可传int或str类型
    :return: firstDay: 当月的第一天，datetime.date类型
            lastDay: 当月的最后一天，datetime.date类型
    """
    if year:
        year = int(year)
    else:
        year = datetime.date.today().year

    if month:
        month = int(month)
    else:
        month = datetime.date.today().month

    # 获取当月第一天的星期和当月的总天数
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)

    # 获取当月的第一天
    firstDay = datetime.date(year=year, month=month, day=1)
    lastDay = datetime.date(year=year, month=month, day=monthRange)

    return str(firstDay), str(lastDay)


def getStartTime():
    startTime, endTime = getMonthFirstDayAndLastDay()
    return  startTime

def getEndTime():
    startTime, endTime = getMonthFirstDayAndLastDay()
    return endTime

# 获取当前月份   
def getCurrentMonth():
    year = datetime.date.today().year
    month = datetime.date.today().month
    return str(year) + '-' + str(month)

# 获取当前日期
def getCurrentDate():
    return str(datetime.date.today())
    
    
# 计算当前日期往后一周的日期
def cal_date():
    date = str(datetime.date.today())
    c = datetime.datetime.strptime(date, "%Y-%m-%d")
    d = datetime.timedelta(weeks=1)
    return (c+d).strftime("%Y-%m-%d")

# 获取当前时间戳
def getCurTimerstamp():
    return str(time.time()).split('.')[0]
    
    
#设定延迟时间
def sleep(t):
     time.sleep(t)
     
# 将时间戳转换为日期类型
def timestamp2data(timestamp):
    timestamp = str(timestamp)
    if len(timestamp) > 11:
        timestamp = timestamp[:-3]
    date = time.localtime(int(timestamp))
    re_date = time.strftime("%Y-%m-%d",date)
    return re_date
