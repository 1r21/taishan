import json
import requests

from .sign import compute_sign
from app.setting import GHOST_URL


def publish_blog(article):
    has_token, message, token = compute_sign()
    if not has_token:
        return message

    article_id, title, transcript, image_url, date, source, _ = article
    # 05-12-2020
    f_date = date.strftime("%d-%m-%Y")
    url = f"{GHOST_URL}/ghost/api/v3/admin/posts/"
    headers = {"Authorization": "Ghost {}".format(token.decode())}
    style = """<style>
        .news-audio{width:100%;outline:none;}.video-transcript{padding:0;}
        .video-transcript li{list-style:none;}.pbs-from{text-align:right;}
        .video-transcript li p{text-indent:2em;text-align:justify;}</style>"""

    audio = f"{style}<audio class='news-audio' controls src='{GHOST_URL}/static/audio/{f_date}.mp3'></audio>"
    s_link = f"<p class='pbs-from'>from:<a href={source} target='_blank'>pbs</a></p>"
    mobiledoc = {
        "version": "0.3.1",
        "markups": [],
        "atoms": [],
        "cards": [
            ["html", {"html": audio}],
            ["html", {"html": "<br/>"}],
            ["html", {"html": transcript}],
            ["html", {"html": "<br/>"}],
            ["html", {"html": s_link}],
        ],
        # https://github.com/bustle/mobiledoc-kit/blob/master/MOBILEDOC.md
        "sections": [[10, 0], [10, 1], [10, 2], [10, 3], [10, 4]],
    }
    body = {
        "posts": [
            {
                "title": title,
                "slug": f"pbs-{article_id}",
                "mobiledoc": json.dumps(mobiledoc),
                "tags": ["pbs"],
                "custom_excerpt": "news,english",
                "feature_image": f"{GHOST_URL}/static/image/{image_url}?date={f_date}",
                "status": "published",
            }
        ]
    }
    r = requests.post(url, json=body, headers=headers)
    posts = r.json().get("posts")
    return "ok" if posts else "pulish fail!"
