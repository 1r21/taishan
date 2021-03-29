import json
from os import environ as env
from hashlib import md5

import requests

BAIDU_APPID = env.get("BAIDU_APPID")
BAIDU_API_KEY = env.get("BAIDU_API_KEY")
BAIDU_API_SALT = env.get("BAIDU_API_SALT")


class BaiduT:
    BASE_URL = "http://api.fanyi.baidu.com/api/trans/vip/translate"

    def __init__(
        self, q: str, appid=BAIDU_APPID, key=BAIDU_API_KEY, salt=BAIDU_API_SALT
    ) -> None:
        self.__checkKey(appid, key, salt)
        self.appid = appid
        self.key = key
        self.salt = salt
        self.q = q

    def run(self):
        if len(self.q) > 1200:
            return "Too Long"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = requests.post(self.req_url, headers=headers)
        result = json.loads(data.content)
        return result.get("trans_result")

    @property
    def token(self):
        params = self.appid + self.q + self.salt + self.key
        sign = md5(params.encode())
        return sign.hexdigest()

    @property
    def req_url(self):
        params = f"{self.q}&from=auto&to=auto&appid={self.appid}&salt={self.salt}&sign={self.token}"
        return f"{BaiduT.BASE_URL}?q={params}"

    @staticmethod
    def __checkKey(appid, key, salt):
        if not (appid and key and salt):
            raise ValueError("BaiduAuthSign : Invalid key")


if __name__ == "__main__":
    try:
        bt = BaiduT("hello \n world")
        result = bt.run()
        print("result:", result)
    except Exception as e:
        print("e", e)
