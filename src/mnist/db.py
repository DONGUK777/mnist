import pymysql.cursors
import os

def get_conn():
    conn = pymysql.connect(host=os.getenv("DB", "localhost"),
                            user='mnist',
                            password='1234',
                            database='mnistdb',
                            port=int(os.getenv("DB_PORT", "53306")),
                            cursorclass=pymysql.cursors.DictCursor)

    return conn

def select(query:str, size= -1):
    conn = get_conn()
    with conn:
        with conn.cursor() as cursor:
          cursor.execute(query)
          result = cursor.fetchmany(size)

    return result

def dml(sql, *values):
    conn = get_conn()

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, values)
            conn.commit()

            return cursor.rowcount
