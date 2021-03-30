import os
import json
import re

import requests

from app.setting import WX_APPID, WX_SECRET, WEB_APP_URL

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
        return False, "No WX Key"

    filename = os.path.basename(filepath)
    material = get_material_list(token, file_type)
    material_list = material.get("item")
    for item in material_list:
        if item.get("name") == filename:
            return False, f"{filename} WX File Exists"

    files = {"media": open(filepath, "rb")}
    r = requests.post(
        url=f"{wx_base_url}/material/add_material?access_token={token}&type={file_type}",
        files=files,
    )
    media = r.json()
    media_id = media.get("media_id")
    if media_id:
        return True, "Upload WX Asset Success", media_id
    return False, f"{filename} Upload WX Asset Fail"


def add_material(article, asset_path):
    token = get_access_token()
    if not token:
        return False, "No WX Key"

    article_id, title, transcript, *_, summary = article
    title = title if len(title) < 64 else f"{title[0:55]}..."
    material = get_material_list(token, "news")
    material_list = material.get("item")
    for item in material_list:
        content = item.get("content")
        news_item = content.get("news_item")
        if news_item and news_item[0].get("title") == title:
            return False, f"News has been published"

    is_upload_ok, message, thumb_media_id = upload_material(asset_path)
    if not is_upload_ok:
        return False, message

    content = (
        transcript.replace("<ul", "<section")
        .replace("</ul", "</section")
        .replace("<li", "<div")
        .replace("</li", "</div")
        .replace("vt__person--host", "")
        .replace("vt__person", "")
        .replace("vt__body", "")
        .replace("body-text", "")
        .replace('class=" "', "")
    )
    content = re.sub(">\s*<", "><", content.strip())
    content = f'<section style="list-style: none;text-indent: 2em;">{content}</section>'
    summary = summary if len(summary) < 120 else f"{summary[0:100]}..."
    content_source_url = f"{WEB_APP_URL}/detail/{article_id}"
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
    media = r.json()
    media_id = media.get("media_id")
    return True, media_id


if __name__ == "__main__":
    action = input("please input action (1,2): ")
    result = ""
    if action == "1":
        token = get_access_token()
        result = create_menu(token)
    elif action == "2":
        token = get_access_token()
        result = get_material_list(token, "news")
    print(result)
