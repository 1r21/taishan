from qiniu import Auth, BucketManager
from app.setting import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME

q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
bucket = BucketManager(q)


def save_file_2_qiniu(url, filename):
    try:
        ret, info = bucket.fetch(url, QINIU_BUCKET_NAME, filename)
        return ret.get("key")
    except Exception as e:
        raise Exception(f"{e}")


if __name__ == "__main__":
    url = input("please input user name: ")
    filename = input("please input filename: ")
    save_file_2_qiniu(url, filename)
