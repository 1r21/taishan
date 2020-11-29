import datetime
from app.libs.helper import exec_sql, query_size, make_password


def gen_user():
    q_sql = f"Select `username` from  `users` where  `username` = %s"
    username = query_size(q_sql, "admin")
    if username:
        return "It Exist"

    add_sql = (
        "INSERT INTO `users` (`username`, `password`,`datetime`) VALUES (%s, %s, %s)"
    )
    password = make_password("admin")
    values = ("admin", password, datetime.datetime.now())
    return exec_sql(add_sql, values)


if __name__ == "__main__":
    ret = gen_user()
    print(ret)