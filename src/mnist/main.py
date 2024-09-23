from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from datetime import datetime
import pymysql.cursors
import os
import uuid
import jigeum.seoul

app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    # 파일 저장
    img = await file.read()
    file_name = file.filename
    file_ext = file.content_type.split('/')[-1]
    request_time = jigeum.seoul.now()  # 현재 시간을 포맷팅
    # upload_dir = "/home/ubuntu/tommy/code/mnist/image/n03/"
    # upload_dir = "/home/ubuntu/images/n03/"
    upload_dir = os.getenv('UPLOAD_DIR','/home/tommy/code/mnist/image')
    username = "n03"

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_full_path = os.path.join(upload_dir, f'{uuid.uuid4()}.{file_ext}')

    with open(file_full_path, "wb") as f:
        f.write(img)


    # 파일 저장 경로 DB INSERT
    # tablename : inage_processing
    # 컬럼 정보 : num(초기 INSERT, 자동 증가)
    # 컬럼 정보 : 파일이름, 파일경로, 요청시간(초기 INSERT), 요청사용자(n00)
    # 컬럼 정보 : 예측모델, 예측결과, 예측시간(추후 업데이트)
    
    conn = pymysql.connect(
        host=os.getenv("DB", "localhost"),
        user='mnist',
        password='1234',
        database='mnistdb',
        port=int(os.getenv("DB_PORT", "53306")),
        cursorclass=pymysql.cursors.DictCursor
        )

    insert_sql = """
        INSERT INTO image_processing(file_name, file_path, request_time, request_user)
        VALUES (%s, %s, %s, %s)
    """
    
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql, (file_name, file_full_path, request_time, username))
        conn.commit()

    return {"filename": file.filename,
            "content_type": file.content_type,
            "file_full_path": file_full_path
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
