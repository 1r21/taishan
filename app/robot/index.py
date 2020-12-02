import requests

from app.setting import DINGDING_TOKEN, WEB_APP_URL, FILE_SERVER_URL
from .compute_sign import compute_sign

webhook = "https://oapi.dingtalk.com/robot/send?access_token="

headers = {
    "Content-Type": "application/json; charset=utf-8",
}


def send_message(title="pbs news wrap", content="pbs", picUrl=None):
    result = compute_sign()
    req_url = f"{webhook}{DINGDING_TOKEN}&timestamp={result[0]}&sign={result[1]}"
    json = {
        "msgtype": "link",
        "link": {
            "text": content,
            "title": title,
            "picUrl": f"{FILE_SERVER_URL}/{picUrl}",
            "messageUrl": WEB_APP_URL,
        },
    }
    r = requests.post(req_url, headers=headers, json=json)
    return r.text


if __name__ == "__main__":
    result = send_message()
    print("result:", result)
