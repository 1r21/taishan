from ..libs.helper import query_all
from ..config.setting import STATIC_SERVER
from ..spider.index import parse_transcript_audio

# route map
ROUTE = {}


def route(url):
    def wrapper(func):
        ROUTE[url] = func

    return wrapper


@route("/")
def index():
    return "this is index page"


@route("/favicon.ico")
def favicon():
    return "icon"


@route("/api/news")
def get_news():
    # date desc
    sql = "Select `id`,`title`,`audio_url`,`transcript` from `news` order by `date` desc"
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
                src=STATIC_SERVER + "/audio/" + url,
                transcript=transcript,
                cover=STATIC_SERVER + "/image/ibelieve.jpeg",
            ),
        )

    return {"list": data}


# admin api
@route("/admin/crawl")
def start_crawl():
    message = parse_transcript_audio()
    return {"message": message}

