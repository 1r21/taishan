FROM alpine

LABEL maintainer="iron"

COPY ./requirements.txt /taishan/requirements.txt

WORKDIR /taishan

RUN sed -i s/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g /etc/apk/repositories && \
    apk --update --no-cache add uwsgi-python py3-pip py3-lxml && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip install -r requirements.txt

CMD [ "uwsgi", "/etc/uwsgi/uwsgi.ini" ]