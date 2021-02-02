import os
import json
import re

import requests

from app.setting import WX_APPID, WX_SECRET, WEB_APP_URL
from ..libs.helper import exec_sql, query_size

wx_base_url = "https://api.weixin.qq.com/cgi-bin"


def get_access_token():
    if WX_APPID and WX_SECRET:
        r = requests.get(
            url=f"{wx_base_url}/token",
            params={
                "grant_type": "client_credential",
                "appid": WX_APPID,
                "secret": WX_SECRET,
            },
        )
        result = r.json()
        return result.get("access_token")


# api unauthorized
def create_menu(token):
    payload = {
        "button": [
            {"type": "click", "name": "土味情话", "key": "love_words"},
            {"type": "view", "name": "新闻链接", "url": "http://ai.chenggang.win"},
        ]
    }
    r = requests.post(
        url=f"{wx_base_url}/menu/create?access_token={token}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )
    return r.json()


def get_material_list(token, file_type="image"):
    payload = {"type": file_type, "offset": 0, "count": 10}
    r = requests.post(
        url=f"{wx_base_url}/material/batchget_material?access_token={token}",
        json=payload,
    )
    return r.json()


def upload_material(filepath, file_type="image"):
    token = get_access_token()
    if not token:
        raise Exception("No WX Key")

    filename = os.path.basename(filepath)
    material = get_material_list(token, file_type)
    material_list = material.get("item")
    for item in material_list:
        if item.get("name") == filename:
            raise Exception(f"{filename} WX File Exists")

    files = {"media": open(filepath, "rb")}
    r = requests.post(
        url=f"{wx_base_url}/material/add_material?access_token={token}&type={file_type}",
        files=files,
    )
    print(r.text)
    media = r.json()
    media_id = media.get("media_id")
    error_msg = f"{filename} Upload WX Material Fail"
    if media_id:
        error_msg = f"{filename}: Upload WX Material Success"
        print(error_msg)
        return media_id
    # if file_type == "image":
    #     sql = "UPDATE news SET wx_thumb_id=%s WHERE image_url=%s"
    #     result = exec_sql(sql, (media_id, filename))
    #     if result != "Ok":
    #         raise Exception("WX Material Save Database Fail")
    print(error_msg)


def add_material(date, asset_path):
    token = get_access_token()
    if not token:
        raise Exception("No WX Key")

    q_sql = "SELECT id,title,summary,transcript FROM `news` WHERE `date`=%s"
    news_list = query_size(q_sql, date)

    if not news_list:
        raise Exception("Add Weixin News Fail")

    article = news_list[0]

    title = article[1] if len(article[1]) < 64 else f"{article[1][0:55]}..."
    material = get_material_list(token, "news")
    material_list = material.get("item")
    for item in material_list:
        content = item.get("content")
        news_item = content.get("news_item")
        if news_item and news_item[0].get("title") == title:
            raise Exception(f"News has been published")

    thumb_media_id = upload_material(asset_path)

    # never support voice
    # f_date = date.strftime("%d-%m-%Y")
    # audio = f"""<mpvoice name={f_date} voice_encode_fileid=""></mpvoice>"""
    # audio = re.sub(">\s*<", "><", f"<section>{audio}</section>")

    content = (
        article[3]
        .replace("ul", "section")
        .replace("li", "section")
        .replace("vt__person--host", "")
        .replace("vt__person", "")
        .replace("vt__body", "")
        .replace("body-text", "")
        .replace('class=" "', "")
    )
    content = re.sub(">\s*<", "><", content.strip())
    content = f'<section style="list-style: none;text-indent: 2em;">{content}</section>'
    summary = article[2] if len(article[2]) < 120 else f"{article[2][0:100]}..."
    content_source_url = f"{WEB_APP_URL}/detail/{article[0]}"
    payload = {
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
    r = requests.post(
        url=f"{wx_base_url}/material/add_news?access_token={token}",
        json=payload,
    )
    return r.json()


if __name__ == "__main__":
    action = input("please input action (1,2,3,4): ")
    result = ""
    if action == "1":
        token = get_access_token()
        result = create_menu(token)
    elif action == "2":
        token = get_access_token()
        result = get_material_list(token, "news")
    elif action == "3":
        try:
            filepath = input("please input file path: ")
            add_material("2021-02-01", filepath)
        except Exception as e:
            print("e:", e)
    print(result)
