# admin api
import time
import jwt

from app.setting import TOKEN_EXP, TOKEN_SALT, FILE_SERVER_URL
from app.libs.db import db_helper
from app.libs.util import make_password
from app.libs.decorator import route, login_required
from app.libs.response import show_reponse, Status
from app.libs.variable import request
from app.spider.pbs_article import automation

# admin user
@route("/admin/user")
def login():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.no_auth)
    username = data.get("username")
    password = data.get("password")
    query = "SELECT id FROM users WHERE username = %s and password = %s"
    user_id = db_helper.fetchone(
        query, (username, make_password(password, TOKEN_SALT))
    )
    if user_id:
        return show_reponse(code=Status.no_auth)
    payload = {"id": user_id[0], "username": username, "exp": time.time() + TOKEN_EXP}
    token = jwt.encode(payload, TOKEN_SALT, algorithm="HS256")
    return show_reponse(data={"token": token.decode("utf8"), "username": username})


@route("/admin/crawl")
@login_required
def start_crawl():
    automation.start()
    code = Status.success if message == "Ok" else Status.other
    return show_reponse(code=code, message=message)


@route("/admin/news")
def get_news():
    # date desc
    sql = (
        "SELECT id, title, summary, transcript, audio_url, image_url, source, date FROM news "
        "ORDER BY date desc"
    )
    news = db_helper.execute_sql(sql)
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
    sql = "DELETE FROM news WHERE id = %s"
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
    sql = "SELECT date, title, summary, image_url FROM news WHERE id = %s"
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
