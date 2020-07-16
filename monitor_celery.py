import os,sys
import yagmail

def sendEmail():
    # sender = ["test@ihr360.com", "york.yu@ihr360.com"]
    sender = ["york.yu@ihr360.com"]
    try:
        yag = yagmail.SMTP("devel@cnbexpress.com", "Ab135790", "smtp.mxhichina.com", 465)
        yag.send(to=sender, subject="服务异常", contents=" \t \t 接口测试平台服务异常请知晓 \n \n ")
        yag.close()
        print("发送邮件成功！")
    except BaseException as e:
        print("发送邮件失败！可能出现错误的原因：%s" % e)

val = os.popen('cd /home/york/HttpRunnerManger && python3 manage.py celery status').readlines()
if not "1 node online.\n" in val:
    print("服务异常")
    sendEmail()
print(val)
