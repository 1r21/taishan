import json
from datetime import datetime as date

import pytz
import requests

from .sign import token
from app.libs.helper import query_size
from app.setting import GHOST_URL

tz = pytz.timezone("America/New_York")


def publish_blog(date):
    q_sql = f"SELECT `id`,`title`,`transcript`,`image_url`,`source` FROM `news` WHERE `date`=%s"
    articles = query_size(q_sql, date)
    err_msg = {"errmsg": "Publish fail!"}
    if articles:
        (article,) = articles
        article_id, title, transcript, image_url, source = article
        # 05-12-2020
        f_date = date.strftime("%d-%m-%Y")

        url = f"{GHOST_URL}/ghost/api/v3/admin/posts/"
        headers = {"Authorization": "Ghost {}".format(token.decode())}
        style = "<style>.news-audio{width:100%;outline:none;}.video-transcript{padding:0;}.video-transcript li{list-style:none;}.video-transcript li p{text-indent:2em;text-align:justify;}.pbs-from{text-align:right;}</style>"
        body = {
            "posts": [
                {
                    "title": title,
                    "slug": f"pbs-{article_id}",
                    "mobiledoc": json.dumps(
                        {
                            "version": "0.3.1",
                            "markups": [],
                            "atoms": [],
                            "cards": [
                                [
                                    "html",
                                    {
                                        "html": f"{style}<audio class='news-audio' controls src='{GHOST_URL}/static/audio/{f_date}.mp3'></audio>"
                                    },
                                ],
                                ["html", {"html": "<br/>"}],
                                ["html", {"html": transcript}],
                                ["html", {"html": "<br/>"}],
                                [
                                    "html",
                                    {
                                        "html": f"<p class='pbs-from'>from:<a href={source}>pbs</a></p>"
                                    },
                                ],
                            ],
                            # https://github.com/bustle/mobiledoc-kit/blob/master/MOBILEDOC.md
                            "sections": [[10, 0], [10, 1], [10, 2], [10, 3], [10, 4]],
                        }
                    ),
                    "tags": ["pbs"],
                    "custom_excerpt": "news,english",
                    "feature_image": f"{GHOST_URL}/static/image/{image_url}?date={f_date}",
                    "status": "draft",
                }
            ]
        }
        r = requests.post(url, json=body, headers=headers)
        posts = r.json().get("posts")
        if posts:
            return f"ok"
    return err_msg


if __name__ == "__main__":
    try:
        c_date = date.strptime("2021-03-10", "%Y-%m-%d")
        publish_blog(c_date)
    except Exception as err:
        print(err)