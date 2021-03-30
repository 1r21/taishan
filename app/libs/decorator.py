from functools import wraps

import jwt

from app.libs.util import head
from app.libs.db import db_helper
from app.libs.variable import ROUTE, request
from app.setting import TOKEN_SALT


def route(url):
    def wrapper(func):
        ROUTE[url] = func

    return wrapper


def check_user_authed(token):
    user_decode = jwt.decode(token.encode(), TOKEN_SALT, algorithms=["HS256"])
    user_id = user_decode.get("id")
    username = user_decode.get("username")
    if user_id:
        sql = "SELECT id, username FROM users WHERE id=%s and username=%s"
        user = db_helper.fetchone(sql, (head(user_id), username))
        return bool(user)
    return False


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kargs):
        headers = request.get("headers")
        token = headers.get("X-Token")
        if not token or not check_user_authed(token):
            return {"message": "No Auth"}
        return f(*args, **kargs)

    return wrapper