FROM alpine

LABEL maintainer="iron"

ENV HTTP_PROXY=
ENV HTTPS_PROXY=
ENV UWSGI_PORT=8000
ENV WEB_APP_ADDR=http://localhost

EXPOSE 8000

WORKDIR /taishan

COPY ./app /taishan/app
COPY ./static /taishan/static
COPY ./app.py /taishan/app.py
COPY ./requirements.txt /taishan/requirements.txt
COPY ./uwsgi.ini /etc/uwsgi/uwsgi.ini

RUN sed -i s/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g /etc/apk/repositories && \
    apk --update add uwsgi-python py3-pip py3-lxml tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' > /etc/timezone && apk del tzdata && \ 
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip install -r requirements.txt

CMD [ "uwsgi", "/etc/uwsgi/uwsgi.ini" ]