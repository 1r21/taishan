from ..libs.helper import query_all, query_size
from ..libs.decorator import route
from ..libs.response import Status, show_reponse
from ..libs.variable import request
from ..setting import FILE_SERVER_URL
from ..translate.index import run_translate


@route("/")
def index():
    return show_reponse(data="this is index page")


@route("/favicon.ico")
def favicon():
    return None


@route("/api/news")
def get_news():
    # date desc
    sql = "Select `id`,`title`,`image_url`,`date` from `news` order by `date` desc"
    news = query_all(sql)
    data = []
    for item in news:
        id = item[0]
        title = item[1]
        image_url = item[2]
        date = item[3]
        data.append(
            dict(
                id=id,
                title=title,
                cover=FILE_SERVER_URL + "/image/" + image_url,
                date=date.strftime("%Y-%m-%d"),
            ),
        )

    return show_reponse(data={"list": data})


@route("/api/news/detail")
def get_news_by_id():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="param error")
    article_id = data.get("id")
    sql = f"Select `title`,`source`,`image_url`,`transcript`,`date`,`audio_url` from `news` where `id`=%s"
    result = query_size(sql, article_id)
    if result:
        article = result[0]
        title = article[0]
        source = article[1]
        image_url = article[2]
        transcript = article[3]
        date = article[4]
        audio_url = article[5]
        detail = dict(
            title=title,
            transcript=transcript,
            src=FILE_SERVER_URL + "/audio/" + audio_url,
            source=source,
            cover=FILE_SERVER_URL + "/image/" + image_url,
            date=date.strftime("%Y-%m-%d"),
        )
        return show_reponse(data=detail)
    return show_reponse(code=Status.other, message="News is not exist!")


@route("/api/translate")
def translate():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="param error")
    result = run_translate(data.get("q"))
    return show_reponse(data={"list": result})
