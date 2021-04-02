from os import environ as env

import pymysql


HOST = env.get("HOST")
PORT = env.get("PORT")
DB_NAME = env.get("DB_NAME")
USER_NAME = env.get("USER_NAME")
PASSWORD = env.get("PASSWORD")


class DBHelper:
    def __init__(self) -> None:
        pass

    @property
    def connection(self):
        try:
            return pymysql.connect(
                host=HOST,
                port=int(PORT),
                db=DB_NAME,
                user=USER_NAME,
                password=PASSWORD,
                charset="utf8mb4",
            )
        except Exception as e:
            raise Exception("Connect db fail")

    # read
    def execute_sql(self, sql):
        with self.connection as conn:
            with conn.cursor() as c:
                c.execute(sql)
                return c.fetchall()

    # write (update,delete etc.)
    def execute_commit(self, sql, args=None):
        with self.connection as conn:
            with conn.cursor() as c:
                c.execute(sql, args)
            conn.commit()
            return c.lastrowid

    def fetchone(self, sql, args=None):
        with self.connection as conn:
            with conn.cursor() as c:
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
