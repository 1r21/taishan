FROM heng1025/uwsgi:python

LABEL maintainer="iron"

ENV HTTP_PROXY=
ENV HTTPS_PROXY=
ENV UWSGI_PORT=8000
ENV WEB_APP_URL=http://localhost

EXPOSE 8000

WORKDIR /taishan

COPY ./app /taishan/app
COPY ./static /taishan/static
COPY ./app.py /taishan/app.py
COPY ./uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY ./requirements.txt /taishan/requirements.txt

RUN pip install -r requirements.txt