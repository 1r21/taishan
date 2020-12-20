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
    print(request)
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


@route("/api/news/detail")
def get_news_by_id():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="param error")
    article_id = data.get("id")
    sql = f"Select `title`,`audio_url`,`image_url`,`transcript`,`date` from `news` where `id`=%s"
    result = query_size(sql, article_id)
    if result:
        article = result[0]
        title = article[0]
        audio_url = article[1]
        image_url = article[2]
        transcript = article[3]
        date = article[4]
        detail = dict(
            title=title,
            transcript=transcript,
            src=FILE_SERVER_URL + "/audio/" + audio_url,
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
