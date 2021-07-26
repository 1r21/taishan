from graphene.test import Client
from app.graphql.schema import schema


def test_index_query():
    client = Client(schema)
    executed = client.execute(
        """query root {
            root
        }"""
    )
    assert executed == {"data": {"root": "this is index page"}}


def test_detail_query():
    client = Client(schema)
    executed = client.execute(
        """{
            info: article(id: "218") {
                src
                title
            }
        }"""
    )
    assert executed == {
        "data": {
            "info": {
                "src": "http://ai.chenggang.win/static/audio/pbs_newswrap_20210722.mp3",
                "title": "News Wrap: DOJ announces strike force to tackle suspect gun networks",
            }
        }
    }