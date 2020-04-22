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
    echo $runport
    port_exit=$(netstat -anpt | grep $runport)
    if [ "$port_exit" ]
    then
        kill -s 9 `ps -ef|grep $runport | grep -v grep | head -2|awk '{print $2}'`
	echo "执行kill命令端口"
    fi

    # 判断runserver是否存在，如果存在kill
   #runserver_pid_list=$(ps -ef|grep runserver | grep $runport |grep -v grep |head -2 |awk '{print $2}')
   runserver_pid_list=$(ps -ef|grep runserver |grep -v grep |head -2 |awk '{print $2}')
   if [ "$port_exit" ]
   then
       for runserver_pid in $runserver_pid_list
       do
           kill -s 9 $runserver_pid
       	   echo "kill runnserver"
       done
   fi



    # 判断是否存在celery进程，如果存在，杀死进程
  #  celery_pid_list=$(ps -ef|grep celery | grep HttpRunnerManage | grep -v grep | head -2 | awk '{print $2}')
    celery_pid_list=$(ps -ef|grep celery | grep -v grep | head -2 | awk '{print $2}')
    for celery_pid in $celery_pid_list
    do
    	kill -s 9 $celery_pid
	echo "kill celery"
    done
    


    # 判断是否存在celery beat进程，如果存在，杀死进程
 #   celerybeat_pid_list=$(ps -ef|grep celery | grep HttpRunnerManage | grep beat | grep -v grep | head -2 | awk '{print $2}')
    celerybeat_pid_list=$(ps -ef|grep celery | grep beat | grep -v grep | head -2 | awk '{print $2}')
    for celerybeat_pid in $celerybeat_pid_list
    do
        kill -s 9 $celerybeat_pid
        echo "kill celerybeat"
    done


    # 判断是否存在celery flower进程，如果存在，杀死进程
#    celeryflower_pid_list=$(ps -ef|grep flower |grep localhost | grep -v grep | head -2 | awk '{print $2}')
    celeryflower_pid_list=$(ps -ef|grep flower | grep -v grep | head -2 | awk '{print $2}')
    for celeryflower_pid in $celeryflower_pid_list
    do
        kill -s 9 $celeryflower_pid
        echo "kill celeryflower"
    done

    # pip3 install -r requirements.txt
    # 数据库迁移
    # python3 manage.py makemigrations
    # python3 manage.py migrate
    # 守护进程方式 启动celery
   #  python3 manage.py celery multi start w1 -A QAPlatform  --loglevel=info

    # 启动项目
   nohup python3 manage.py runserver 0.0.0.0:$runport >djo.out 2>&1 &
   echo "启动Django项目成功"
   nohup python3 manage.py celery -A HttpRunnerManager worker --loglevel=info  >worker.out 2>&1 & # 启动worker 后台启动
   echo "启动celery worker成功"
   nohup python3 manage.py celery -A HttpRunnerManager beat --loglevel=info >worker1.out 2>&1 &			  # 启动定时任务监听器
   nohup python3 manage.py celery beat --loglevel=info >worker1.out 2>&1 &			  # 启动定时任务监听器
   echo "启动celery beat成功"
   nohup celery flower --broker=amqp://user:user123@localhost:5672// >worker2.out 2>&1 &	# 启动任务监控后台。
   echo "启动celery flower成功"

}

if [ $is_work -eq '1' ]
then
    #执行启动函数
    run_server $1
fi
