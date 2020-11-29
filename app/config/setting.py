import os

TOKEN_EXP = 30 * 60
env = os.environ

STATIC_HOST = env.get("STATIC_HOST") or "localhost"
STATIC_PORT = env.get("STATIC_PORT") or "8001"
WEB_SERVER = env.get("WEB_SERVER") or "http://localhost:3000"
STATIC_SERVER = f"http://{STATIC_HOST}:{STATIC_PORT}"

ENABLE_PROXY = env.get("ENABLE_PROXY")
HTTP_PROXY = env.get("HTTP_PROXY")
HTTPS_PROXY = env.get("HTTPS_PROXY")
PROXY = {"http": HTTPS_PROXY, "https": HTTPS_PROXY} if ENABLE_PROXY else None
