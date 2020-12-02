# admin api
import time
import jwt
from ..libs.helper import exec_sql, query_size, make_password
from ..libs.decorator import route, login_required
from ..libs.response import show_reponse, Status
from ..libs.variable import request
from ..setting import TOKEN_EXP,TOKEN_SALT
from ..spider.index import parse_transcript_audio

# admin user
@route("/admin/user")
def login():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.no_auth)
    username = data.get("username")
    password = data.get("password")
    sql = "Select  `id` from `users` where `username`=%s and `password`=%s"
    user_id = query_size(sql, (username, make_password(password)))
    if len(user_id) == 0:
        return show_reponse(code=Status.no_auth)
    payload = {"id": user_id[0], "username": username, "exp": time.time() + TOKEN_EXP}
    token = jwt.encode(payload, TOKEN_SALT, algorithm="HS256")
    return show_reponse(data={"token": token.decode("utf8"), "username": username})


@route("/admin/crawl")
@login_required
def start_crawl():
    message = parse_transcript_audio()
    code = Status.success if message == "Ok" else Status.other
    return show_reponse(code=code, message=message)


@route("/admin/delete/news")
@login_required
def delete_news():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="param error")
    news_id = data.get("id")
    sql = "DELETE FROM `news` where `id`=%s"
    message = exec_sql(sql, news_id)
    code = Status.success if message == "Ok" else Status.other
    return show_reponse(code=code, message=message)
