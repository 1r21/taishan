import hashlib
import pymysql
from app.setting import HOST, PORT, USER_NAME, PASSWORD, DB_NAME, TOKEN_SALT


def create_connection():
    # Connect to the database
    connection = pymysql.connect(
        host=HOST,
        port=int(PORT),
        db=DB_NAME,
        user=USER_NAME,
        password=PASSWORD,
        charset="utf8mb4",
    )
    return connection


def exec_sql(sql, values, require_last_id=False):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # Create a new record
            # sql = "INSERT INTO `news` (`audio_url`, `title`,`transcript`,`date`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, values)
        # save changes.
        connection.commit()
        if require_last_id:
            return cursor.lastrowid
        return "Ok"
    except Exception as e:
        connection.rollback()
        raise Exception(f"{e}")
    finally:
        connection.close()


def query_all(sql, values=None):
    connection = create_connection()
    with connection.cursor() as cursor:
        # Create a new record
        cursor.execute(sql, values)
        result = cursor.fetchall()
        return result


def query_size(sql, values=None, size=1):
    connection = create_connection()
    with connection.cursor() as cursor:
        # Create a new record
        cursor.execute(sql, values)
        # size=1 == fetchone
        result = cursor.fetchmany(size=size)
        return result


def make_password(password):
    return hashlib.md5(f"{password}{TOKEN_SALT}".encode("utf-8")).hexdigest()


def head(list):
    return list[0] if list else None