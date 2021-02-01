from ..libs.variable import request
from ..libs.decorator import route
from ..weixin.sign import checkToken
from ..weixin.handle import receive


@route("/wx")
def weixin():
    data = request.get("data")
    if data:
        return receive(data)
    else:
        qs = request.get("qs")
        return checkToken(qs)
