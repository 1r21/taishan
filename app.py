import json
from wsgiref.simple_server import make_server

from app.api.index import ROUTE


def application(environ, start_response):
    url = environ["PATH_INFO"]
    status = "200 OK"
    headers = [
        ("Content-type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
    ]
    start_response(status, headers)
    try:
        data = ROUTE[url]()
        return [json.dumps(data).encode("utf-8")]
    except Exception as e:
        print(f"Error: {e}")
        return {"message":'Error Happened'}


if __name__ == "__main__":
    with make_server("", 8080, application) as httpd:
        print("Serving on port 8080...")
        httpd.serve_forever()
