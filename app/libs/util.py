import hashlib


def make_password(password, salt):
    return hashlib.md5(f"{password}{salt}".encode("utf-8")).hexdigest()


def head(list):
    return list[0] if list else None