import json
from os import environ as env
from datetime import datetime as date

import requests
import jwt

GHOST_KEY = env.get("GHOST_KEY")
GHOST_URL = env.get("GHOST_URL")


class Ghost:
    def __init__(self, key=GHOST_KEY, api_url=GHOST_URL, status="published") -> None:
        self.__checkKey(key, api_url)
        self.key = key
        self.api_url = api_url
        self.status = status

    def send(self, *, article_id, title, transcript, image_url, date, source, **kw):
        body = self.__gen_body(article_id, title, transcript, image_url, date, source)
        headers = {"Authorization": f"Ghost {self.token}"}
        url = f"{GHOST_URL}/ghost/api/v3/admin/posts/"
        info = requests.post(url, json=body, headers=headers)
        data = info.json()
        posts = data.get("posts")
        errors = data.get("errors")
        return "ok" if posts else errors

    @property
    def token(self):
        # Split the key into ID and SECRET
        id, secret = self.key.split(":")

        # https://www.dazhuanlan.com/2020/01/06/5e128ff2cc17f/
        # Prepare header and payload
        # iat => Issued At
        iat = int(date.now().timestamp())
        header = {"alg": "HS256", "typ": "JWT", "kid": id}
        payload = {"iat": iat, "exp": iat + 5 * 60, "aud": "/v3/admin/"}
        return jwt.encode(payload, bytes.fromhex(secret), "HS256", header)

    def __gen_body(
        self, article_id, title, transcript, image_url, date, source
    ) -> dict:
        mobiledoc = Ghost.__gen_mobiledoc(date, source, transcript)
        return {
            "posts": [
                {
                    "title": title,
                    "slug": f"pbs-{article_id}",
                    "mobiledoc": json.dumps(mobiledoc),
                    "tags": ["pbs"],
                    "custom_excerpt": "news,english",
                    "feature_image": f"{GHOST_URL}/static/image/{image_url}?date={date}",
                    "status": self.status,
                }
            ]
        }

    @staticmethod
    def __gen_mobiledoc(date, source, transcript) -> dict:
        return {
            "version": "0.3.1",
            "markups": [],
            "atoms": [],
            "cards": [
                ["html", {"html": Ghost.__get_audio_element(date)}],
                ["html", {"html": "<br/>"}],
                ["html", {"html": transcript}],
                ["html", {"html": "<br/>"}],
                ["html", {"html": Ghost.__get_source_link(source)}],
            ],
            # https://github.com/bustle/mobiledoc-kit/blob/master/MOBILEDOC.md
            "sections": [[10, 0], [10, 1], [10, 2], [10, 3], [10, 4]],
        }

    @staticmethod
    def __get_audio_element(date) -> str:
        f_date = date.strftime("%d-%m-%Y")
        style = Ghost.__get_common_style()
        return f"{style}<audio class='news-audio' controls src='{GHOST_URL}/static/audio/{f_date}.mp3'></audio>"

    @staticmethod
    def __get_common_style() -> str:
        return """<style>
        .news-audio{width:100%;outline:none;}.video-transcript{padding:0;}
        .video-transcript li{list-style:none;}.pbs-from{text-align:right;}
        .video-transcript li p{text-indent:2em;text-align:justify;}</style>"""

    @staticmethod
    def __get_source_link(source) -> str:
        return f"<p class='pbs-from'>from:<a href={source} target='_blank'>pbs</a></p>"

    @staticmethod
    def __checkKey(key, api_url):
        if not (key and api_url):
            raise ValueError("GhostAuthSign : Invalid key")


if __name__ == "__main__":
    try:
        article = {
            "article_id": 1,
            "title": "test-article",
            "transcript": "transcript",
            "image_url": "pbs_newswrap_20210409.jpg",
            "date": date.now().date(),
            "source": "source",
        }
        blog = Ghost(status="draft")
        result = blog.send(**article)
        print("result", result)
    except Exception as e:
        print("e", e)
