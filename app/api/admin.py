# admin api
import time

import jwt
from ..setting import TOKEN_EXP, TOKEN_SALT,FILE_SERVER_URL
from ..libs.helper import exec_sql, query_all, query_size, make_password
from ..libs.decorator import route, login_required
from ..libs.response import show_reponse, Status
from ..libs.variable import request
from ..robot.index import send_message
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


@route("/admin/news")
def get_news():
    # date desc
    sql = "Select `id`,`title`,`summary`,`transcript`,`audio_url`,`image_url`,`source`,`date` from `news` order by `date` desc"
    news = query_all(sql)
    data = []
    for item in news:
        id = item[0]
        title = item[1]
        summary = item[2]
        transcript = item[3]
        audio_url = item[4]
        image_url = item[5]
        source = item[6]
        date = item[7]
        data.append(
            dict(
                id=id,
                title=title,
                summary=summary,
                transcript=transcript,
                src=FILE_SERVER_URL + "/audio/" + audio_url,
                cover=FILE_SERVER_URL + "/image/" + image_url,
                source=source,
                date=date.strftime("%Y-%m-%d"),
            ),
        )

    return show_reponse(data={"list": data})


@route("/admin/delete/news")
@login_required
def delete_news():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="param error")
    article_id = data.get("id")
    sql = "DELETE FROM `news` where `id`=%s"
    message = exec_sql(sql, article_id)
    code = Status.success if message == "Ok" else Status.other
    return show_reponse(code=code, message=message)


@route("/admin/send/news")
@login_required
def send_dd_message():
    data = request.get("data")
    err_code = Status.other
    err_message = "News is not exist!"
    if not data:
        return show_reponse(code=err_code, message="Param Error")
    article_id = data.get("id")
    sql = f"Select `date`,`title`,`summary`,`image_url` from `news` where `id`=%s"
    result = query_size(sql, article_id)
    if result:
        article = result[0]
        f_date = article[0].strftime("%d-%m-%Y")
        r_dict = send_message(
            id=article_id,
            title=f"{f_date}:{article[1]}",
            content=article[2],
            picUrl=f"image/{article[3]}",
        )
        code = r_dict.get("errcode")
        err_message = r_dict.get("errmsg")
        if code == 0:
            err_code = Status.success
    return show_reponse(code=err_code, message=err_message)
