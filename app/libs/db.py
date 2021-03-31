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
        self.connection = None

    @property
    def conn(self):
        if not self.connection:
            self.connection = pymysql.connect(
                host=HOST,
                port=int(PORT),
                db=DB_NAME,
                user=USER_NAME,
                password=PASSWORD,
                charset="utf8mb4",
            )
            return self.connection
        return self.connection

    @property
    def cusor(self):
        return self.conn.cursor()

    # read
    def execute_sql(self, sql):
        conn = self.conn
        with self.cusor as c:
            c.execute(sql)
            conn.commit()
            return c.fetchall()

    # write (update,delete etc.)
    def execute_commit(self, sql, args=None):
        conn = self.conn
        try:
            with self.cusor as c:
                c.execute(sql, args)
                conn.commit()
                return c.lastrowid
        except pymysql.Error as e:
            conn.rollback()
            raise ValueError(f"DB Commit Err:", e)

    def fetchone(self, sql, args=None):
        conn = self.conn
        with self.cusor as c:
            c.execute(sql, args)
            conn.commit()
            return c.fetchone()


db_helper = DBHelper()

if __name__ == "__main__":
    try:
        result = db_helper.fetchone("SELECT title FROM news WHERE id = %s", 32)
        sql = "UPDATE news SET title = %s WHERE id = 32"
        res = db_helper.execute_commit(sql, "hello world")
        print("result", res)
    except Exception as e:
        print("err", e)
