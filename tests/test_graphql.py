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
        """query GetArticle($id: String!) {
            article(id: $id) {
                date,
                id
            }
        }""",
        variables={"id": "218"},
    )
    assert executed == {"data": {"article": {"date": "2021-07-22", "id": "218"}}}
