from app.libs.variable import request
from app.libs.decorator import route
from app.sdk.weixin import WXBot


@route("/wx")
def weixin():
    data = request.get("data")
    if data:
        return WXBot.receive(data)
    else:
        qs = request.get("qs")
        return WXBot.check_token(qs)
