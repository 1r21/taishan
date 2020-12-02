from ..libs.helper import query_all
from ..libs.decorator import route
from ..libs.response import show_reponse
from ..setting import FILE_SERVER_URL


@route("/")
def index():
    return show_reponse(data="this is index page")


@route("/favicon.ico")
def favicon():
    return None


@route("/api/news")
def get_news():
    # date desc
    sql = (
        "Select `id`,`title`,`audio_url`,`transcript` from `news` order by `date` desc"
    )
    news = query_all(sql)
    data = []
    for item in news:
        id = item[0]
        title = item[1]
        url = item[2]
        transcript = item[3]
        data.append(
            dict(
                id=id,
                title=title,
                transcript=transcript,
                src=FILE_SERVER_URL + "/audio/" + url,
                cover=FILE_SERVER_URL + "/image/ibelieve.jpeg",
            ),
        )

    return show_reponse(data={"list": data})
