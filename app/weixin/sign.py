import hashlib

from app.setting import WX_SALT


def checkToken(data):
    try:
        signature = data.get("signature")[0]
        timestamp = data.get("timestamp")[0]
        nonce = data.get("nonce")[0]
        echostr = data.get("echostr")[0]

        sha1 = hashlib.sha1()
        for param in [nonce, timestamp, WX_SALT]:
            sha1.update(param.encode("utf-8"))
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return echostr
        else:
            return "auth fail"
    except Exception as e:
        return f"Err: {e}"