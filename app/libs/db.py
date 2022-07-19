from os import environ as env

import pymysql
from dbutils.pooled_db import PooledDB

from app.libs.logger import LoggerHandler

HOST = env.get("HOST")
PORT = env.get("PORT")
DB_NAME = env.get("DB_NAME")
USER_NAME = env.get("USER_NAME")
PASSWORD = env.get("PASSWORD")

logger = LoggerHandler("db")

db_config = {
    "host": HOST,
    "port": int(PORT),
    "user": USER_NAME,
    "passwd": PASSWORD,
    "db": DB_NAME,
    "charset": "utf8mb4",
    "maxconnections": 10,
    "mincached": 4,
    "maxcached": 0,
    "maxusage": 5,
    "blocking": True,
}


class DBHelper:
    __pool = None

    def __init__(self) -> None:
        self.conn = self.__get_connection()
        logger.info("Connect DB Success")

    def __get_connection(self):
        if DBHelper.__pool is None:
            try:
                __pool = PooledDB(pymysql, **db_config)
            except Exception:
                raise Exception("Connect DB Fail!")
        return __pool.connection()

    def execute_sql(self, sql, args=None):
        with self.conn.cursor() as c:
            c.execute(sql, args)
            return c.fetchall()

    # write (update,delete etc.)
    def execute_commit(self, sql, args=None):
        with self.conn.cursor() as c:
            c.execute(sql, args)
        self.conn.commit()
        return c.lastrowid

    def fetchone(self, sql, args=None):
        with self.conn.cursor() as c:
            c.execute(sql, args)
            return c.fetchone()


db_helper = DBHelper()

if __name__ == "__main__":
    try:
        article = db_helper.fetchone("SELECT title FROM news WHERE id = %s", 36)
        print("result", article)
        sql = "UPDATE news SET title = %s WHERE id = 32"
        update_res = db_helper.execute_commit(sql, "hello world")
        print("result", update_res)
    except Exception as e:
        print("err", e)
