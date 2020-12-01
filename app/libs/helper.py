import hashlib
import pymysql
from app.config.secure import HOST, PORT, USERNAME, PASSWORD, DB, TOKEN_SALT


def create_connection():
    # Connect to the database
    connection = pymysql.connect(
        host=HOST,
        port=PORT,
        user=USERNAME,
        password=PASSWORD,
        db=DB,
        charset="utf8mb4",
    )
    return connection


def exec_sql(sql, values):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # Create a new record
            # sql = "INSERT INTO `news` (`audio_url`, `title`,`transcript`,`date`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, values)
        # save changes.
        connection.commit()
        return "Ok"
    except Exception as e:
        connection.rollback()
        return f"{e}"
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
