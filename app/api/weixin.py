from app.libs.util import head
from app.libs.variable import request
from app.libs.decorator import route
from app.libs.response import show_reponse
from app.sdk.weixin import Bot as WXBot, WXSign

wx = WXSign()


@route("/wx")
def weixin():
    data = request.get("data")
    if data:
        return WXBot.receive(data)
    else:
        qs = request.get("qs")
        bot = WXBot()
        return bot.check_token(qs)


# /wxsdkconfig?url={url}
@route("/wxsdkconfig")
def get_wx_ticket():
    qs = request.get("qs")
    url = ''
    if qs and qs.get("url"):
        url = head(qs.get("url"))
    else:
        raise ValueError('url params is required!')

    ret = wx.sign(url)
    return show_reponse(data=ret)
