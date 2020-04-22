# debugtalk.py
import time
import datetime
import random
import re

# 审批时获取任务taskId
def getTaskId(aname,sname,tid_1,tid_2):
    if aname==sname:
        return tid_1
    else:
        return tid_2

#设定延迟时间
def sleep(response,t):
    if response.status_code==200:
        time.sleep(10)
    else:
        time.sleep(t)

#获取当前时间（utc时间）
def get_current_utcTime():
    utcTime = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    utcTime = utcTime[:23] + utcTime[26:]
    return utcTime

#获取后一天的时间（utc时间）
def get_nextDay_utcTime():
    now_time=datetime.datetime.utcnow()
    utcTime = (now_time+datetime.timedelta(days=+1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    utcTime = utcTime[:23] + utcTime[26:]
    return utcTime

#第一次保存表单时按规则随机生成字段id
def setComponentId():
    unixTime = str(round(time.time() * 1000))
    return (''.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k','j','i','h','g','f','e','d','c','b','a','0','1','2','3','4','5','6','7','8','9'], 8))+unixTime)

def getHeadersToken(req_headers):
    try:
        # TODO: write code...
        result = re.findall("XSRF-TOKEN=(.{36})", req_headers)[0]
        return result
    except Exception as e:
        print("获取请求头部中token失败，请检查问题。可能原因:{}".format(e))
        raise e

#获取假期模板的ID
def getVocationModelId(data,vocationName):
    length = len(data)
    for i in range(0,length):
        if data[i]["name"] == vocationName:
            return data[i]["id"]
