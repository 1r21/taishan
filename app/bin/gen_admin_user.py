import datetime
from app.libs.helper import exec_sql, query_size, make_password


def gen_user():
    q_sql = f"Select `username` from  `users` where  `username` = %s"
    input_u = input('please input user name: ')
    username = query_size(q_sql, input_u)
    if username:
        return "It Exist"

    add_sql = (
        "INSERT INTO `users` (`username`, `password`,`datetime`) VALUES (%s, %s, %s)"
    )
    input_pass = input('please input password: ')
    password = make_password(input_pass)
    values = (input_u, password, datetime.datetime.now())
    return exec_sql(add_sql, values)


if __name__ == "__main__":
    ret = gen_user()
    print(ret)