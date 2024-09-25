from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from datetime import datetime
import pymysql.cursors
import os
import uuid
from jigeum.seoul import now

app = FastAPI()


@app.post("/files/")
async def file_list():
    conn = pymysql.connect(host='172.18.0.1', port = 53306,
                            user = 'mnist', password = '1234',
                            database = 'mnistdb',
                            cursorclass=pymysql.cursors.DictCursor)
    with conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
    return result


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    #from jigeum.seoul import now
    # 파일 저장
    img = await file.read()
    file_name = file.filename
    label = file_name[0]
    file_ext = file.content_type.split('/')[-1]
    #request_time = jigeum.seoul.now()  # 현재 시간을 포맷팅
    # upload_dir = "/home/ubuntu/tommy/code/mnist/image/n03/"
    # upload_dir = "/home/ubuntu/images/n03/"
    upload_dir = os.getenv('UPLOAD_DIR','/home/tommy/code/mnist/image')
    username = "n03"

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_full_path = os.path.join(upload_dir, f'{uuid.uuid4()}.{file_ext}')

    with open(file_full_path, "wb") as f:
        f.write(img)


    sql = "INSERT INTO image_processing(file_name, label, file_path, request_time, request_user) VALUES(%s, %s, %s, %s, %s)"
    import jigeum.seoul 
    from mnist.db import dml

    insert_row = 0
    insert_loop =1
    for _ in range(insert_loop):
        insert_row = dml(sql, file_name, label, file_full_path, jigeum.seoul.now(), 'n03')
    
    return {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_full_path": file_full_path,
            "insert_row_cont": insert_row
           }

@app.get("/all")
def all():
    from mnist.db import select
    sql = "SELECT * FROM image_processing"
    result = select(query=sql, size=-1)

    return result

@app.get("/one")
def one():
    from mnist.db import select
    sql = """
            SELECT *
            FROM image_processing
            WHERE prediction_time IS NULL
            ORDER BY num
            LIMIT 1"""
    result = select(query=sql, size=1)
    return result[0]

@app.get("/many/")
def many(size: int = -1):
    from mnist.db import get_conn

    sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num"
    conn = get_conn()

    with conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchmany(size)

    return result
