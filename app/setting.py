from os import environ as env

# jwt
TOKEN_SALT = env.get("TOKEN_SALT")
TOKEN_EXP = 30 * 60

# server
WEB_APP_URL = env.get("WEB_APP_URL")
FILE_SERVER_URL = env.get("FILE_SERVER_URL")
