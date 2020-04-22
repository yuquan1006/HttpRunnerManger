#!/bin/bash
#echo $0 文件名
#echo $1 端口号

is_work=1
# 判断是否存在一个参数：端口号
if [ $# != '1' ]
then
    echo "缺少一个参数：端口号 "
    is_work=0
fi

# 定义运行函数
run_server(){
    #获取端口号
    runport=$1
    # 判断端口是否被占用，如果占用，杀死进程
    port_exit=$(netstat -anpt | grep $runport)
    if [ "$port_exit" ]
    then
        kill -s 9 `ps -ef|grep $runport | grep -v grep | head -2|awk '{print $2}'`
	echo "执行kill命令端口"
    fi

    # 判断runserver是否存在，如果存在kill
   runserver_pid_list=$(ps -ef|grep runserver | grep $runport |grep -v grep |head -2 |awk '{print $2}')
   if [ "$port_exit" ]
   then
       for runserver_pid in $runserver_pid_list
       do
           kill -s 9 $runserver_pid
       	   echo "kill runnserver"
       done
   fi



    # 判断是否存在celery进程，如果存在，杀死进程
    celery_pid_list=$(ps -ef|grep celery | grep HttpRunnerManage | grep -v grep | head -2 | awk '{print $2}')
    for celery_pid in $celery_pid_list
    do
    	kill -s 9 $celery_pid
	echo "kill celery"
    done
    


    # 判断是否存在celery beat进程，如果存在，杀死进程
    celerybeat_pid_list=$(ps -ef|grep celery | grep HttpRunnerManage | grep beat | grep -v grep | head -2 | awk '{print $2}')
    for celerybeat_pid in $celerybeat_pid_list
    do
        kill -s 9 $celerybeat_pid
        echo "kill celerybeat"
    done


    # 判断是否存在celery flower进程，如果存在，杀死进程
    celeryflower_pid_list=$(ps -ef|grep flower | grep localhost | grep -v grep | head -2 | awk '{print $2}')
    for celeryflower_pid in $celeryflower_pid_list
    do
        kill -s 9 $celeryflower_pid
        echo "kill celeryflower"
    done
}

if [ $is_work -eq '1' ]
then
    #执行启动函数
    run_server $1
fi

