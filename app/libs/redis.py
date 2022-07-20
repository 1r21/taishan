from os import environ as env

import redis

from app.libs.logger import LoggerHandler

HOST = env.get("REDIS_HOST")
PORT = env.get("REDIS_PORT")
USERNAME = env.get("REDIS_USERNAME")
PASSWD = env.get("REDIS_PASSWORD")

logger = LoggerHandler("redis")


class RedisHelper:
    def __init__(self) -> None:
        __pool = redis.ConnectionPool(
            host=HOST, port=PORT, username=USERNAME, password=PASSWD, db=0
        )
        self.__conn = redis.Redis(connection_pool=__pool)
        if self.__conn.ping():
            logger.info("Connect Redis Success")
        else:
            logger.error("Connect Redis Fail!")

    def has(self, name):
        return self.__conn.exists(name) == 1

    def get(self, name):
        self.__conn.get(name)

    def set(self, name, value):
        self.__conn.set(name, value)

    def set_list(self, name, *values):
        self.__conn.rpush(name, *values)

    def get_list(self, name, start=0, stop=-1):
        return self.__conn.lrange(name, start, stop)

    def set_sort_list(self, name, *values):
        self.__conn.zadd(name, *values)


redis_helper = RedisHelper()
