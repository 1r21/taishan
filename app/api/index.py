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
