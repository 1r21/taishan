import requests

from app.setting import DINGDING_PUSH, DINGDING_TOKEN, WEB_APP_URL, FILE_SERVER_URL
from .sign import compute_sign

webhook = "https://oapi.dingtalk.com/robot/send?access_token="

headers = {
    "Content-Type": "application/json; charset=utf-8",
}


def send_message(id=None, title="pbs", content="interesting news", picUrl=None):
    if not DINGDING_PUSH:
        return {"errmsg": "Push Forbidden!"}
    result = compute_sign()
    req_url = f"{webhook}{DINGDING_TOKEN}&timestamp={result[0]}&sign={result[1]}"
    json = {
        "msgtype": "link",
        "link": {
            "text": content,
            "title": title,
            "picUrl": f"{FILE_SERVER_URL}/{picUrl}",
            "messageUrl": f"{WEB_APP_URL}/detail/{id}" if id else WEB_APP_URL,
        },
    }
    r = requests.post(req_url, headers=headers, json=json)
    return r.text


if __name__ == "__main__":
    result = send_message()
    print("result:", result)
