from qiniu import Auth, BucketManager
from app.setting import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME


def save_file_2_qiniu(url, filename):
    try:
        if QINIU_ACCESS_KEY and QINIU_SECRET_KEY:
            q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
            bucket = BucketManager(q)
            ret, info = bucket.fetch(url, QINIU_BUCKET_NAME, filename)
            return ret.get("key")
        return None
    except Exception as e:
        raise Exception(f"{e}")


if __name__ == "__main__":
    url = input("please input user name: ")
    filename = input("please input filename: ")
    save_file_2_qiniu(url, filename)
