# debugtalk.py

# debugtalk.py
import re,os,time,random,datetime,base64

import requests
# 获取请求头部中token
def getHeadersToken(req_headers):
    try:
        # TODO: write code...
        result = re.findall("XSRF-TOKEN=(.{36})", req_headers)[0]
        return result
    except Exception as e:
        print("获取请求头部中token失败，请检查问题。可能原因:{}".format(e))
        raise e


def getCookiesToken(req_cookies):
    result = requests.utils.dict_from_cookiejar(req_cookies)
    return result


def getStrLen(strs,len=8):
    if isinstance(strs,int):
        strs = str(strs)
    return strs[:len]

# 获取项目datas下文件路径
def getProjectFile(path):
    '''path -> list'''
    path = eval(path)
    projectPath = "/home/york/HttpRunnerManager/datas"
    for i in range(len(path)):
        projectPath = os.path.join(projectPath,path[i])
    return projectPath

# 数据转化
def get_evelData(data):
    try:
        data = str(data)
        result = eval(data)
    except:
        result = data
    return result
    
def get_workDay():
    '''
    获取当前一天工作日，如当前一天非工作日则向前取
    :return: 工作日datetime
    '''
    # 获取当前时间datetime
    # datetime_tmp = datetime.datetime.today()
    datetime_tmp = datetime.date.today()+datetime.timedelta(days=-1)
    while True:
        # 获取当前时间属于周几
        dayOfWeek = datetime_tmp.weekday()
        if (int(dayOfWeek) in range(5)):
            return datetime_tmp
        else:
            print(datetime_tmp)
            datetime_tmp += datetime.timedelta(days=-1)

def get_workDay_starttimestamp(start_hours=None):
    '''
    生成当前时间前工作日（周一周五）9-18内时间戳
    :return:
    '''
        # 生成随机小时(09-18)
    a  = [9,10,11,13,14,15,16,17]
    start_hour = random.choice(a)
    if start_hours != None:
        start_hour = int(start_hours)
    datetime_tmp = get_workDay()
    today_datetime_start = datetime.datetime.strptime("{} {}:00:00".format(datetime_tmp, start_hour),
                                                      '%Y-%m-%d %H:%M:%S')  # 转换为datetime
    unix_time = time.mktime(today_datetime_start.timetuple())
    return str(int(unix_time))+"000"
    

def get_workDay_starttimestamp1():
    '''
    获取工作日非班段内时间戳
    :return:
    '''
    # 生成非班段内随机小时(09-18)
    a  = [0,1,2,3,4,5,6,7,8,18,19,20,21,22,23]
    start_hour = random.choice(a)
    datetime_tmp = get_workDay()
    today_datetime_start = datetime.datetime.strptime("{} {}:00:00".format(datetime_tmp, start_hour),
                                                      '%Y-%m-%d %H:%M:%S')  # 转换为datetime
    print(today_datetime_start)
    unix_time = time.mktime(today_datetime_start.timetuple())
    return str(int(unix_time))+"000"

def get_endtimestamp(value,hour=1):
    '''
    根据时间戳取几个小时后时间戳
    :param value:时间戳
    :param hour:int 几个小时
    :return: 一个小时后时间戳
    '''
    # 字符串转float转datetime
    today_datetime_start = datetime.datetime.fromtimestamp(float(value[:-3]))
    # datetime 小时加一
    today_datetime_end = today_datetime_start+datetime.timedelta(hours = +hour)
    # 格式化->时间戳
    print(today_datetime_end)
    unix_time = time.mktime(today_datetime_end.timetuple())
    return str(int(unix_time)) + "000"

#设定延迟时间
def sleep(response,t):
    if response.status_code==200:
        time.sleep(20)
    else:
        time.sleep(t)

#设定延迟时长
def sleepTime(t):
    time.sleep(t)


def get_base64(appID,appSecret):
    '''openapi中请求头Authorization：appID:appSecret的base64编码'''
    try:
        newStr = appID+":"+appSecret
        newStr = newStr.encode("utf-8")
        result = base64.b64encode(newStr)
        return result.decode('utf-8')
    except:
        return ""
