import random
import time
from lxml import etree

from ..weixin.words import words


def gen_response(from_user, to_user, content):

    return f"<xml>\
            <ToUserName><![CDATA[{from_user}]]>\
            </ToUserName><FromUserName><![CDATA[{to_user}]]>\
            </FromUserName><CreateTime>{int(time.time())}</CreateTime>\
            <MsgType><![CDATA[text]]></MsgType>\
            <Content><![CDATA[{content}]]></Content>\
        </xml>"


def receive(data):
    try:
        root = etree.fromstring(data)
        info_from_user = {}
        for child in root:
            info_from_user[child.tag] = child.text

        MsgType = info_from_user.get("MsgType")
        FromUserName = info_from_user.get("FromUserName")
        ToUserName = info_from_user.get("ToUserName")
        Content = info_from_user.get("Content")
        # Event = info_from_user.get("Event")
        # EventKey = info_from_user.get("EventKey")

        if MsgType == "text" and Content:
            r_index = random.randint(1, len(words))
            return gen_response(FromUserName, ToUserName, words[r_index])
        else:
            return "success"
    except Exception as e:
        print(f"Err: {e}")
        return "success"