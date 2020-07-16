#!/bin/bash





run_server(){
    # 判断nginx是否存在，如果存在kill
   nginx_pid_list=$(ps -ef|grep nginx | grep -v grep |head -2 |awk '{print $2}')
   for nginx_pid in $nginx_pid_list
    do
        kill -s 9 $nginx_pid
       	echo "kill nginx"
    done

    # 判断uwsgi是否存在，如果存在kill
   uwsgi_pid_list=$(ps -ef|grep uwsgi | grep -v grep |head -2 |awk '{print $2}')
   for uwsgi_pid in $uwsgi_pid_list
    do
        kill -s 9 $uwsgi_pid
       	echo "kill uwsgi"
    done

#执lery进程，如果存在，杀死进程
  #  celery_pid_list=$(ps -ef|grep celery | grep HttpRunnerManage | grep -v grep | head -2 | awk '{print $2}')
    celery_pid_list=$(ps -ef|grep celery | grep -v grep | head -20 | awk '{print $2}')
    for celery_pid in $celery_pid_list
    do
    	kill -s 9 $celery_pid
	echo "kill celery"
    done
    


    # 判断是否存在celery beat进程，如果存在，杀死进程
 #   celerybeat_pid_list=$(ps -ef|grep celery | grep HttpRunnerManage | grep beat | grep -v grep | head -2 | awk '{print $2}')
    celerybeat_pid_list=$(ps -ef|grep celery | grep beat | grep -v grep | head -10 | awk '{print $2}')
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

# 启动服务


   /usr/local/nginx/sbin/nginx  # 启动nginx
   echo "启动nginx"
   uwsgi --ini /home/york/HttpRunnerManger/uwsgi.ini
   echo "启动uwsgi"
   nohup python3 manage.py celery worker --loglevel=info  >/var/log/httprunnermanger_worker.log 2>&1 & # 启动worker 后台启动
   echo "启动celery"
   nohup python3 manage.py celery beat --loglevel=info >/var/log/httprunnermanger_worker1.log 2>&1 &              # 启动定时任务监听器
   echo "启动beat"
   nohup celery flower --broker=amqp://user:user123@localhost:5672// >/var/log/httprunnermanger_worker2.log 2>&1 &    # 启动任务监控后台。
   echo "启动flower"

}
run_server
