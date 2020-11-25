import os

env = os.environ

STATIC_HOST = env.get("STATIC_HOST") or "localhost"
STATIC_PORT = env.get("STATIC_PORT") or "8001"
WEB_SERVER = env.get("WEB_SERVER") or "http://localhost:3000"
STATIC_SERVER = f"http://{STATIC_HOST}:{STATIC_PORT}"

HTTP_PROXY = env.get("HTTP_PROXY")
HTTPS_PROXY = env.get("HTTPS_PROXY")
PROXY = {"http": HTTPS_PROXY, "https": HTTPS_PROXY}
if not HTTP_PROXY:
    PROXY = {"http": "http://127.0.0.1:1087", "https": "http://127.0.0.1:1087"}
