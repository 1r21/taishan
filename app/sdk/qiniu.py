from os import environ as env

from qiniu import Auth, put_file, BucketManager

QINIU_ACCESS_KEY = env.get("QINIU_ACCESS_KEY")
QINIU_SECRET_KEY = env.get("QINIU_SECRET_KEY")
QINIU_BUCKET_NAME = env.get("QINIU_BUCKET_NAME")


class Qiniu:
    def __init__(self, filename, path) -> None:
        self.q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        self.bucket = BucketManager(self.q)
        self.filename = filename
        self.path = path

    def save(self):
        # file info
        ret, _ = self.bucket.stat(QINIU_BUCKET_NAME, self.filename)
        if not ret or "hash" not in ret:
            print(f"{self.filename} start upload...")
            put_file(self.token, self.filename, self.path)
            print(f"{self.filename} end upload!")
        else:
            print(f"{self.filename} already exists")

    @property
    def token(self):
        return self.q.upload_token(QINIU_BUCKET_NAME, self.filename, 3600)


if __name__ == "__main__":
    import os

    path = os.path.join(os.getcwd(), f"static/image", "pbs_newswrap_20210212.jpg")
    qiniu = Qiniu("test.jpg", path)
    qiniu.save()
