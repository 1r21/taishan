import json
import requests

from app.setting import DINGDING_PUSH, DINGDING_TOKEN, WEB_APP_URL, FILE_SERVER_URL
from .sign import compute_sign

webhook = "https://oapi.dingtalk.com/robot/send?access_token="

headers = {
    "Content-Type": "application/json; charset=utf-8",
}


def send_message(
    m_type="link", id=None, title="pbs", content="interesting news", picUrl=None
):
    if not DINGDING_PUSH:
        return {"errmsg": "Push Forbidden!"}
    timestamp, sign = compute_sign()
    req_url = f"{webhook}{DINGDING_TOKEN}&timestamp={timestamp}&sign={sign}"
    image_url = f"{FILE_SERVER_URL}/{picUrl}"
    app_url = f"{WEB_APP_URL}/detail/{id}" if id else WEB_APP_URL
    data = {
        "msgtype": m_type,
        m_type: {
            "title": title,
            "text": content,
            "picUrl": image_url,
            "messageUrl": app_url,
        },
    }
    if m_type == "text":
        data = {
            "msgtype": m_type,
            m_type: {"content": content},
            "at": {"isAtAll": True},
        }

    try:
        r = requests.post(req_url, headers=headers, json=data)
        return json.loads(r.text)
    except Exception as e:
        raise Exception(f"{e}")


if __name__ == "__main__":
    result = send_message(m_type="text")
    print("Send Result:", result)
