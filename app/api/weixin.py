from app.libs.variable import request
from app.libs.decorator import route
from app.sdk.weixin import Bot as WXBot


@route("/wx")
def weixin():
    data = request.get("data")
    if data:
        return WXBot.receive(data)
    else:
        qs = request.get("qs")
        bot = WXBot()
        return bot.check_token(qs)
