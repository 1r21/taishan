import jwt
from functools import wraps

from app.libs.db import db_helper
from app.libs.variable import ROUTE, request
from app.setting import TOKEN_SALT


def route(url):
    def wrapper(func):
        ROUTE[url] = func

    return wrapper


def check_user_authed(token):
    try:
        user_payload = jwt.decode(token, TOKEN_SALT, algorithms=["HS256"])
        user_id = user_payload.get("id")
        username = user_payload.get("username")
        if user_id:
            sql = "SELECT id, username FROM users WHERE id=%s and username=%s"
            return db_helper.fetchone(sql, (user_id, username))
        raise ValueError("Auth failed")
    except jwt.ExpiredSignatureError as e:
        raise jwt.ExpiredSignature("Signature has expired")
    except jwt.InvalidSignatureError as e:
        raise jwt.InvalidSignatureError("Signature is invalid")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError("Invalid token type")
    except Exception as e:
        raise e


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kargs):
        headers = request.get("headers")
        token = headers.get("X-Token")
        if not token:
            raise ValueError("No token param")
        if check_user_authed(token):
            return f(*args, **kargs)

    return wrapper
