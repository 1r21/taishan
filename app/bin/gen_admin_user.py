import datetime
from app.libs.helper import exec_sql, query_size, make_password


def gen_user(uname, u_pass):
    q_sql = f"Select `username` from  `users` where  `username` = %s"
    username = query_size(q_sql, uname)
    if username:
        return "It Exist"

    add_sql = (
        "INSERT INTO `users` (`username`, `password`,`datetime`) VALUES (%s, %s, %s)"
    )

    password = make_password(u_pass)
    values = (uname, password, datetime.datetime.now())
    return exec_sql(add_sql, values)


if __name__ == "__main__":
    username = input("please input user name: ")
    password = input("please input password: ")
    ret = gen_user(username, password)
    print(ret)