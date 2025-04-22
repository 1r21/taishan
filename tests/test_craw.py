"""Tests for web crawling and data extraction functionality."""
from app.spider.pbs_article import PBSArticle


def test_transcript():
    pbsArticle = PBSArticle()
    pbsArticle.get_transcript(
        "https://www.pbs.org/newshour/show/news-wrap-world-health-organization-declares-end-to-covid-19-global-emergency"
    )
