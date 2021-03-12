from datetime import datetime as date

import jwt
from app.setting import GHOST_KEY


def compute_sign():
    if not GHOST_KEY:
        return False, "No Ghost Key"
    # Split the key into ID and SECRET
    id, secret = GHOST_KEY.split(":")

    # Prepare header and payload
    iat = int(date.now().timestamp())

    header = {"alg": "HS256", "typ": "JWT", "kid": id}
    payload = {"iat": iat, "exp": iat + 5 * 60, "aud": "/v3/admin/"}

    # Create the token (including decoding secret)
    return (
        True,
        "Ok",
        jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header),
    )
