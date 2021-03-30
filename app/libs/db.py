from os import environ as env

import pymysql

from .util import head

HOST = env.get("HOST")
PORT = env.get("PORT")
DB_NAME = env.get("DB_NAME")
USER_NAME = env.get("USER_NAME")
PASSWORD = env.get("PASSWORD")


class DBHelper:
    def __init__(self) -> None:
        self.conn = pymysql.connect(
            host=HOST,
            port=int(PORT),
            db=DB_NAME,
            user=USER_NAME,
            password=PASSWORD,
            charset="utf8mb4",
        )

    # read
    def execute_sql(self, sql):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        except pymysql.Error as e:
            print("Db Query Err: ", e)

    # write (update,delete etc.)
    def execute_commit(self, sql, args=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, args)
                self.conn.commit()
                return cursor.lastrowid
        except pymysql.Error as e:
            self.conn.rollback()
            raise ValueError(f"DB Commit Err:", e)

    def fetchone(self, sql, args=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, args)
                return cursor.fetchone()
        except pymysql.Error as e:
            print("Db Query Err: ", e)

    def close(self):
        self.conn.cursor().close()
        self.conn.close()


db_helper = DBHelper()

if __name__ == "__main__":
    try:
        result = db_helper.fetchone("SELECT title FROM news WHERE id = %s", 2)
        sql = "UPDATE news SET title = %s WHERE id = 2"
        res = db_helper.execute_commit(sql, "hello world")
    except Exception as e:
        print("err", e)
