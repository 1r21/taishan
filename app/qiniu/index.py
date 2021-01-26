from qiniu import Auth, put_file
from app.setting import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME


def save_file_2_qiniu(path, filename):
    try:
        if QINIU_ACCESS_KEY and QINIU_SECRET_KEY:
            q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
            token = q.upload_token(QINIU_BUCKET_NAME, filename, 3600)
            print('start upload...')
            put_file(token, filename, path)
            print('end upload!')
    except Exception as e:
        raise Exception(f"Qiniu Err: {e}")


if __name__ == "__main__":
    url = input("please input user name: ")
    filename = input("please input filename: ")
    save_file_2_qiniu(url, filename)
