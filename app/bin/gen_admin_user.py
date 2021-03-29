from datetime import datetime
from app.libs.util import make_password
from app.libs.db import exec_sql, query_size
from app.setting import TOKEN_SALT


def gen_user(uname, u_pass):
    query = "SELECT username FROM `users` WHERE username = %s"
    username = query_size(query, uname)
    if username:
        return "It Exist"

    insert_user = "INSERT INTO users (username, password, datetime) VALUES (%s, %s, %s)"

    password = (u_pass, TOKEN_SALT)
    values = (uname, password, datetime.now())
    return exec_sql(insert_user, values)


if __name__ == "__main__":
    username = input("please input user name: ")
    password = input("please input password: ")
    ret = gen_user(username, password)
    print(ret)