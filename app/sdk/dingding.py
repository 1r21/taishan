import json
from time import time
from os import environ as env
import hmac
import hashlib
import base64
import urllib.parse

import requests

DINGDING_PUSH = env.get("DINGDING_PUSH") == "True"
DINGDING_ROBOT_KEY = env.get("DINGDING_ROBOT_KEY")
DINGDING_TOKEN = env.get("DINGDING_TOKEN")


class Bot:
    BASE_URL = f"https://oapi.dingtalk.com/robot/send"

    def __init__(self, key=DINGDING_ROBOT_KEY, token=DINGDING_TOKEN) -> None:
        self.__checkKey(key, token)
        self.key = key
        self.token = token
        self.iat = str(round(time() * 1000))

    def send(self, template):
        data = requests.post(self.__req_url, json=template)
        return json.loads(data.text)

    @property
    def __req_url(self):
        return f"{self.BASE_URL}?access_token={self.token}&timestamp={self.iat}&sign={self.__sign}"

    @property
    def __sign(self):
        str_sign = f"{self.iat}\n{self.key}"
        key_en = self.key.encode("utf-8")
        hmac_code = hmac.new(key_en, str_sign.encode("utf-8"), digestmod=hashlib.sha256)
        return urllib.parse.quote_plus(base64.b64encode(hmac_code.digest()))

    @staticmethod
    def get_template(msg_type="link", *, title, content, pic_url, msg_url):
        template = Bot.__get_link_template(title, content, pic_url, msg_url)
        if msg_type == "text":
            template = Bot.__get_text_template(content)
        return template

    @staticmethod
    def __get_link_template(title, content, pic_url, msg_url):
        return {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": content,
                "picUrl": pic_url,
                "messageUrl": msg_url,
            },
        }

    @staticmethod
    def __get_text_template(content, is_at_all=True):
        return {
            "msgtype": "text",
            "text": {"content": content},
            "at": {"isAtAll": is_at_all},
        }

    @staticmethod
    def __checkKey(key, token):
        if not (key and token):
            raise ValueError("DingDingAuthSign : Invalid key")


if __name__ == "__main__":
    try:
        bot = Bot()
        template = Bot.get_template(title="title", content="content")
        result = bot.send(template)
        print("Send Result:", result)
    except Exception as e:
        print("DingDing Err", e)
