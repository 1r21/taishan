import graphene
from graphql.execution.executor import resolve_field
from app.libs.db import db_helper
from app.setting import FILE_SERVER_URL


def _map_article(article):
    id, title, summary, transcript, audio_url, image_url, source, date = article
    return dict(
        id=id,
        title=title,
        cover=FILE_SERVER_URL + "/image/" + image_url,
        summary=summary,
        transcript=transcript,
        src=FILE_SERVER_URL + "/audio/" + audio_url,
        source=source,
        date=date.strftime("%Y-%m-%d"),
    )


class Character(graphene.Interface):
    id = graphene.NonNull(graphene.String)
    title = graphene.String()
    cover = graphene.String()
    summary = graphene.String()
    transcript = graphene.String()
    src = graphene.String()
    source = graphene.String()
    date = graphene.String()


class Article(graphene.ObjectType):
    class Meta:
        interfaces = (Character,)

    info = graphene.String()


base_sql = "SELECT id, title, summary, transcript, audio_url, image_url, source, date FROM news"


class Query(graphene.ObjectType):
    root = graphene.String(description="when access / route")
    list = graphene.List(lambda: Article)
    article = graphene.Field(Article, id=graphene.NonNull(graphene.String))

    def resolve_root(root, info):
        return "this is index page"

    def resolve_list(root, info):
        sql = f"{base_sql} ORDER BY date desc"
        articles = db_helper.execute_sql(sql)
        return list(map(_map_article, articles))

    def resolve_article(root, info, id):
        sql = f"{base_sql} WHERE id = %s"
        article = db_helper.fetchone(sql, id)
        return _map_article(article)


schema = graphene.Schema(query=Query)
