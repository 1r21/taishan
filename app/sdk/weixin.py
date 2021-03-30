import os
import re
import random
import time
import hashlib
from os import environ as env

from lxml import etree
import requests

from app.libs.util import head
from app.setting import WEB_APP_URL
from . import wx_words as words

WX_APPID = env.get("WX_APPID")
WX_SECRET = env.get("WX_SECRET")
WX_SALT = env.get("WX_SALT")


class Weixin:
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, appid=WX_APPID, secret=WX_SECRET) -> None:
        self.__checkKey(appid, secret)
        self.appid = appid
        self.secret = secret

    # upload article
    def add_material(self, asset_path, *, article_id, title, transcript, summary, **kw):
        title = title if len(title) < 64 else f"{title[0:55]}..."
        material_list = self.__get_material_list("news")

        for item in material_list:
            content = item.get("content")
            news_item = head(content.get("news_item"))
            if news_item and news_item.get("title") == title:
                return f"News has been published"

        is_upload_ok, message, thumb_media_id = self.upload_material(asset_path)
        if not is_upload_ok:
            return message

        content = Weixin.__format_content(transcript)
        payload = Weixin.__gen_article_payload(
            article_id, title, summary, thumb_media_id, content
        )
        url = self.__get_req_url("/material/add_news")
        data = self.make_request("post", url, json=payload)
        return data.get("media_id")

    # upload image
    def upload_material(self, filepath, file_type="image"):
        filename = os.path.basename(filepath)
        material_list = self.__get_material_list(file_type)

        for item in material_list:
            if item.get("name") == filename:
                return False, f"{filename} exists"

        url = self.__get_req_url("/material/add_material")
        files = {"media": open(filepath, "rb")}
        data = self.make_request(
            "post",
            url=f"{url}&type={file_type}",
            files=files,
        )
        media_id = data.get("media_id")
        if media_id:
            return True, "WX media_id: ", media_id
        return False, f"{filename} Upload WX Asset Fail"

    def __get_material_list(self, file_type="image"):
        payload = {"type": file_type, "offset": 0, "count": 10}
        url = self.__get_req_url("/material/batchget_material")
        data = self.make_request("post", url, json=payload)
        return data.get("item")

    def __get_req_url(self, url):
        return f"{Weixin.BASE_URL}{url}?access_token={self.token}"

    @property
    def token(self):
        url = f"{Weixin.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret,
        }
        return self.make_request("get", url, params=params)

    @staticmethod
    def make_request(method, url, **kwargs):
        req = requests.request(method, url, **kwargs)
        data = req.json()
        code = data.get("errcode")
        message = data.get("errmsg")
        if code == 0:
            return data
        raise ValueError(message)

    @staticmethod
    def __checkKey(appid, secret):
        if not (appid and secret):
            raise ValueError("WeixinAuthSign: Invalid key")

    @staticmethod
    def __gen_article_payload(article_id, title, summary, thumb_media_id, content):
        summary = summary if len(summary) < 120 else f"{summary[0:100]}..."
        content_source_url = f"{WEB_APP_URL}/detail/{article_id}"
        return {
            "articles": [
                {
                    "title": title,
                    "thumb_media_id": thumb_media_id,
                    "digest": summary,
                    "show_cover_pic": 0,
                    "content": content,
                    "content_source_url": content_source_url,
                    "need_open_comment": 1,
                    "only_fans_can_comment": 1,
                }
            ]
        }

    @staticmethod
    def __format_content(html):
        content = (
            html.replace("<ul", "<section")
            .replace("</ul>", "</section>")
            .replace("<li", "<div")
            .replace("</li>", "</div>")
            .replace("vt__person--host", "")
            .replace("vt__person", "")
            .replace("vt__body", "")
            .replace("body-text", "")
            .replace('class=" "', "")
        )
        content = re.sub(">\s*<", "><", content.strip())
        content = (
            f'<section style="list-style: none;text-indent: 2em;">{content}</section>'
        )
        return content


class Bot:
    def __init__(self, salt=WX_SALT) -> None:
        self.salt = salt

    @staticmethod
    def receive(data):
        root = etree.fromstring(data)
        info_from_user = {}
        for child in root:
            info_from_user[child.tag] = child.text

        MsgType = info_from_user.get("MsgType")
        FromUserName = info_from_user.get("FromUserName")
        ToUserName = info_from_user.get("ToUserName")
        Content = info_from_user.get("Content")

        if MsgType == "text" and Content:
            r_index = random.randint(1, len(words))
            return Bot.gen_response(FromUserName, ToUserName, words[r_index])
        return "success"

    @staticmethod
    def gen_response(from_user, to_user, content):
        return f"<xml>\
                <ToUserName><![CDATA[{from_user}]]>\
                </ToUserName><FromUserName><![CDATA[{to_user}]]>\
                </FromUserName><CreateTime>{int(time.time())}</CreateTime>\
                <MsgType><![CDATA[text]]></MsgType>\
                <Content><![CDATA[{content}]]></Content>\
            </xml>"

    def check_token(self, data):
        signature = head(data.get("signature"))
        timestamp = head(data.get("timestamp"))
        nonce = head(data.get("nonce"))
        echostr = head(data.get("echostr"))

        sha1 = hashlib.sha1()
        for param in [nonce, timestamp, self.salt]:
            sha1.update(param.encode("utf-8"))
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return echostr
        return "Auth Fail"


if __name__ == "__main__":
    pass
