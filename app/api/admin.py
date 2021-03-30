# admin api
import time
import jwt

from app.setting import TOKEN_EXP, TOKEN_SALT, FILE_SERVER_URL, WEB_APP_URL
from app.libs.db import db_helper
from app.libs.util import make_password, head
from app.libs.decorator import route, login_required
from app.libs.response import show_reponse, Status
from app.libs.variable import request
from app.sdk.dingding import Bot as DDBot
from app.spider.pbs_article import Automation

# admin user
@route("/admin/user")
def login():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.no_auth)
    username = data.get("username")
    password = data.get("password")
    query = "SELECT id FROM users WHERE username = %s and password = %s"
    user = db_helper.fetchone(query, (username, make_password(password, TOKEN_SALT)))
    if not user:
        return show_reponse(code=Status.no_auth)
    payload = {
        "id": str(head(user)),
        "username": username,
        "exp": time.time() + TOKEN_EXP,
    }
    token = jwt.encode(payload, TOKEN_SALT, algorithm="HS256")
    return show_reponse(data={"token": token.decode("utf8"), "username": username})


@route("/admin/crawl")
@login_required
def start_crawl():
    try:
        automation = Automation()
        art_status = automation.start()
        return show_reponse(code=Status.success, message=art_status.value)
    except:
        return show_reponse(code=Status.other)


@route("/admin/news")
def get_news():
    # date desc
    sql = (
        "SELECT id, title, summary, transcript, audio_url, image_url, source, date FROM news "
        "ORDER BY date desc"
    )
    articles = db_helper.execute_sql(sql)
    data = []
    for article in articles:
        id, title, summary, transcript, audio_url, image_url, source, date = article
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
    try:
        db_helper.execute_commit(sql, article_id)
        return show_reponse(code=Status.success)
    except Exception as e:
        return show_reponse(code=Status.other)


@route("/admin/send/news")
@login_required
def send_dd_message():
    data = request.get("data")
    err_code = Status.other
    err_message = "News is not exist!"
    if not data:
        return show_reponse(code=err_code, message="Param Error")
    article_id = data.get("id")
    sql = "SELECT date, title, image_url FROM news WHERE id = %s"
    article = db_helper.fetchone(sql, article_id)
    if article:
        date, title, image_url = article
        dd_bot = DDBot()
        template = DDBot.get_template(
            title=date.strftime("%d-%m-%Y"),
            content=title,
            pic_url=f"{FILE_SERVER_URL}/image/{image_url}",
            msg_url=f"{WEB_APP_URL}/detail/{article_id}",
        )
        dd_info = dd_bot.send(template)
        code = dd_info.get("errcode")
        err_message = dd_info.get("errmsg")
        if code == 0:
            err_code = Status.success
    return show_reponse(code=err_code, message=err_message)
