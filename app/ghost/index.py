import json
import requests

from .sign import compute_sign
from app.setting import GHOST_URL


class Blog:
    def __init__(self, article) -> None:
        article_id, title, transcript, image_url, _, source, _ = article
        self.article_id = article_id
        self.title = title
        self.transcript = transcript
        self.image_url = image_url
        self.source = source
        self.f_date = self.date.strftime("%d-%m-%Y")

    def publish(self):
        token, message = compute_sign()
        if token:
            body = self.__gen_body()
            headers = {"Authorization": f"Ghost {token.decode()}"}
            url = f"{GHOST_URL}/ghost/api/v3/admin/posts/"
            data = requests.post(url, json=body, headers=headers)
            posts = data.json().get("posts")
            return "ok" if posts else "Pulish Fail"
        else:
            return message

    def __gen_body(self) -> dict:
        mobiledoc = self.__gen_mobiledoc()
        return {
            "posts": [
                {
                    "title": self.title,
                    "slug": f"pbs-{self.article_id}",
                    "mobiledoc": json.dumps(mobiledoc),
                    "tags": ["pbs"],
                    "custom_excerpt": "news,english",
                    "feature_image": f"{GHOST_URL}/static/image/{self.image_url}?date={self.f_date}",
                    "status": "published",
                }
            ]
        }

    def __gen_mobiledoc(self) -> dict:
        audio_element = self.__gen_audio_element()
        source_element = self.__gen_source_link()
        return {
            "version": "0.3.1",
            "markups": [],
            "atoms": [],
            "cards": [
                ["html", {"html": audio_element}],
                ["html", {"html": "<br/>"}],
                ["html", {"html": self.transcript}],
                ["html", {"html": "<br/>"}],
                ["html", {"html": source_element}],
            ],
            # https://github.com/bustle/mobiledoc-kit/blob/master/MOBILEDOC.md
            "sections": [[10, 0], [10, 1], [10, 2], [10, 3], [10, 4]],
        }

    def __gen_audio_element(self) -> str:
        style = self.__gen_style()
        return f"{style}<audio class='news-audio' controls src='{GHOST_URL}/static/audio/{self.f_date}.mp3'></audio>"

    def __gen_style() -> str:
        return """<style>
        .news-audio{width:100%;outline:none;}.video-transcript{padding:0;}
        .video-transcript li{list-style:none;}.pbs-from{text-align:right;}
        .video-transcript li p{text-indent:2em;text-align:justify;}</style>"""

    def __gen_source_link(self) -> str:
        return f"<p class='pbs-from'>from:<a href={self.source} target='_blank'>pbs</a></p>"
