from os import environ as env

# db
HOST = env.get("HOST")
PORT = env.get("PORT")
DB_NAME = env.get("DB_NAME")
USER_NAME = env.get("USER_NAME")
PASSWORD = env.get("PASSWORD")

# dingding robot
DINGDING_PUSH = bool(env.get("DINGDING_PUSH"))
DINGDING_ROBOT_KEY = env.get("DINGDING_ROBOT_KEY")
DINGDING_TOKEN = env.get("DINGDING_TOKEN")

# baidu translate
BAIDU_APPID = env.get("BAIDU_APPID")
BAIDU_API_KEY = env.get("BAIDU_API_KEY")
BAIDU_API_SALT = env.get("BAIDU_API_SALT")

# qiniu
QINIU_ACCESS_KEY = env.get('QINIU_ACCESS_KEY')
QINIU_SECRET_KEY = env.get('QINIU_SECRET_KEY')
QINIU_BUCKET_NAME = env.get('QINIU_BUCKET_NAME')

# jwt
TOKEN_SALT = env.get("TOKEN_SALT")
TOKEN_EXP = 30 * 60


# server
WEB_APP_URL = env.get("WEB_APP_URL")
FILE_SERVER_URL = env.get("FILE_SERVER_URL")

# proxy
HTTP_PROXY = env.get("HTTP_PROXY")
HTTPS_PROXY = env.get("HTTPS_PROXY")

PROXY = None
if HTTP_PROXY and HTTPS_PROXY:
    PROXY = {"http": HTTPS_PROXY, "https": HTTPS_PROXY}
