FROM python:3.6
ENV PYTHONUNBUFFERED=1
RUN mkdir /HttpRunnerManager && mkdir /HttpRunnerManager/httprunner_2.5.1
WORKDIR /HttpRunnerManager
ADD requirements.txt /HttpRunnerManager/
RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple/ \
    && apt-get update \
    && apt-get install -y  erlang-nox \
    rabbitmq-server 
COPY httprunner_2.5.1/ /HttpRunnerManager/httprunner_2.5.1/
RUN  cd /HttpRunnerManager/httprunner_2.5.1 \
    &&  pip install .


