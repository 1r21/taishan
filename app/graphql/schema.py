import graphene

from app.libs.db import db_helper
from app.setting import FILE_SERVER_URL


def _map_base_article(article):
    id, title, image_url, date, *_ = article

    return dict(
        id=id,
        title=title,
        cover=FILE_SERVER_URL + "/image/" + image_url,
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
        description = "article info"
        interfaces = (Character,)


class Query(graphene.ObjectType):
    root = graphene.String(description="when access / route")
    list = graphene.List(lambda: Article)
    article = graphene.Field(Article, id=graphene.NonNull(graphene.String))

    def resolve_root(self, info):
        return "this is index page"

    def resolve_list(root, info):
        sql = "SELECT id, title, image_url, date FROM news ORDER BY date DESC"
        articles = db_helper.execute_sql(sql)
        return list(map(_map_base_article, articles))

    def resolve_article(root, info, id):
        sql = "SELECT id, title, image_url, date, source, audio_url, transcript FROM news WHERE id = %s"
        article = db_helper.fetchone(sql, id)
        article_dict = _map_base_article(article)

        *_, source, audio_url, transcript = article

        article_dict["source"] = source
        article_dict["src"] = FILE_SERVER_URL + "/audio/" + audio_url
        article_dict["transcript"] = transcript
        return article_dict


schema = graphene.Schema(query=Query)
