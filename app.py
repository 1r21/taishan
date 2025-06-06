import json
from urllib.parse import parse_qs

from app.libs.logger import LoggerHandler
from app.libs.variable import ROUTE, request
from app.libs.response import show_reponse, Status
from app.setting import PORT

# https://stackoverflow.com/questions/43393764/python-3-6-project-structure-leads-to-runtimewarning
# registy router first (can't import in app/__init__.py)
from app.api.web import *
from app.api.admin import *
from app.api.weixin import *
from app.api.wedding_wishes import *

logger = LoggerHandler("app")


def application(environ, start_response):
    url = environ.get("PATH_INFO")
    method = environ.get("REQUEST_METHOD")
    qs = environ.get("QUERY_STRING")
    length = environ.get("CONTENT_LENGTH", "0")
    length = 0 if length == "" else int(length)
    data = environ["wsgi.input"].read(length)
    headers = {"method": method, "X-Token": environ.get("HTTP_X_TOKEN")}
    global request
    request["headers"] = headers
    request["qs"] = parse_qs(qs)
    if method.lower() == "post" and data:
        try:
            request["data"] = json.loads(data.decode())
        except Exception as e:
            logger.error(e)
            # xml,form
            request["data"] = data.decode()

    status = "200 OK"
    headers = [
        ("Content-type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Headers", "*"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Max-Age", "600"),  # cache preflight request 10min
    ]
    start_response(status, headers)
    try:
        data = ROUTE[url]()

        if type(data) is str:
            return [data.encode("utf-8")]
        return [json.dumps(data).encode("utf-8")]
    except Exception as e:
        err = show_reponse(code=Status.other, message=f"{e}")
        logger.error(e)
        return [json.dumps(err).encode("utf-8")]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    with make_server("", PORT, application) as httpd:
        logger.info(f"Serving on port {PORT}...")
        httpd.serve_forever()
