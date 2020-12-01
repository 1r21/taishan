import requests

from app.config.secure import DINGDING_TOKEN
from app.config.setting import WEB_SERVER, STATIC_SERVER
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
            "picUrl": f"{STATIC_SERVER}/{picUrl}",
            "messageUrl": WEB_SERVER,
        },
    }
    r = requests.post(req_url, headers=headers, json=json)
    return r.text


if __name__ == "__main__":
    result = send_message()
    print("result:", result)
