import json
from urllib.parse import parse_qs

from app.libs.variable import ROUTE, request
from app.libs.response import show_reponse, Status


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
    if method.lower() == "post":
        request["data"] = json.loads(data.decode())

    status = "200 OK"
    headers = [
        ("Content-type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Headers", "*"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Max-Age ", "600"), # cache preflight request 10min
    ]
    start_response(status, headers)
    try:
        data = ROUTE[url]()
        return [json.dumps(data).encode("utf-8")]
    except Exception as e:
        err = show_reponse(code=Status.other, message=f"{e}")
        return [json.dumps(err).encode("utf-8")]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server("", 8080, application) as httpd:
        print("Serving on port 8080...")
        httpd.serve_forever()
