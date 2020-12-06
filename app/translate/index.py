import json

import requests

from .sign import compute_sign

BAIDU_TRASNSLATE_URL = "http://api.fanyi.baidu.com/api/trans/vip/translate"


def get_translate_url(q):
    sign_info = compute_sign(q)
    appid = sign_info[0]
    salt = sign_info[1]
    sign = sign_info[2]
    return f"{BAIDU_TRASNSLATE_URL}?q={q}&from=auto&to=auto&appid={appid}&salt={salt}&sign={sign}"


def run_translate(q):
    if len(q) > 1200:
        return "Too Long"
    url = get_translate_url(q)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url, headers=headers)
    r_dict = json.loads(r.content)
    return r_dict.get("trans_result")


if __name__ == "__main__":
    result = run_translate("hello \n world")
    print("result:", result)
