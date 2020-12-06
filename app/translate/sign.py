from hashlib import md5

from app.setting import BAIDU_APPID, BAIDU_API_KEY, BAIDU_API_SALT


def compute_sign(q):
    params = BAIDU_APPID + q + BAIDU_API_SALT + BAIDU_API_KEY
    sign = md5(params.encode())
    return BAIDU_APPID, BAIDU_API_SALT, sign.hexdigest()
