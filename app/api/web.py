from app.libs.db import db_helper
from app.libs.logger import LoggerHandler
from app.libs.decorator import route
from app.libs.response import Status, show_reponse
from app.libs.util import head
from app.libs.variable import request
from app.setting import FILE_SERVER_URL
from app.sdk.baidu import BaiduT
from app.graphql.schema import schema

logger = LoggerHandler("api.web")


@route("/")
def index():
    return show_reponse(data="this is index page")


@route("/favicon.ico")
def favicon():
    return None


@route("/graphql")
def graphql_entry():
    data = request.get("data")
    query = data.get("query")
    context = data.get("context")
    variables = data.get("variables")
    operation_name = data.get("operation_name")
    result = schema.execute(
        query,
        context=context,
        variables=variables,
        operation_name=operation_name,
    )
    if result.errors:
        (first_err,) = result.errors
        logger.error(first_err)
        return show_reponse(code=Status.other, message=f"{first_err}")
    return show_reponse(data=result.data)


@route("/api/news")
def get_news():
    query = request.get("qs")
    default_page = 1
    default_page_size = 20
    page = default_page
    page_size = default_page_size
    if query:
        page = int(head(query.get("page") or [default_page]))
        page_size = int(head(query.get("pageSize") or [default_page_size]))

    # date desc
    sql = "SELECT id, title, image_url, date FROM news ORDER BY id DESC LIMIT %s OFFSET %s"
    total_sql = "SELECT COUNT(*) FROM news"
    limit = page_size
    offset = (page - 1) * page_size
    articles = db_helper.execute_sql(sql, (limit, offset))
    (total,) = db_helper.fetchone(total_sql)
    data = []
    for article in articles:
        id, title, image_url, date = article
        data.append(
            dict(
                id=id,
                title=title,
                cover=FILE_SERVER_URL + "/image/" + image_url,
                date=date.strftime("%Y-%m-%d"),
            ),
        )

    return show_reponse(
        data={
            "page": page,
            "pageSize": page_size,
            "total": total,
            "list": data,
        }
    )


@route("/api/news/detail")
def get_news_by_id():
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="param error")
    article_id = data.get("id")
    sql = "SELECT title, source, image_url, transcript, date, audio_url FROM news WHERE id = %s"
    article = db_helper.fetchone(sql, article_id)
    if article:
        title, source, image_url, transcript, date, audio_url = article
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
    q = data.get("q")
    result = BaiduT(q).run()
    return show_reponse(data={"list": result})
