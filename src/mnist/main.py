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
    upload_dir = "./image"
    username = "n00"

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
    
    connection = pymysql.connect(
        host="172.18.0.1",
        user='mnist',
        password='1234',
        database='mnistdb',
        port=int('53306'),
        cursorclass=pymysql.cursors.DictCursor
        )

    insert_sql = """
        INSERT INTO image_processing(file_name, file_path, request_time, request_user)
        VALUES (%s, %s, %s, %s)
    """
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(insert_sql, (file_name, file_full_path, request_time, username))
        connection.commit()

    return {"filename": file.filename,
            "content_type": file.content_type,
            "file_full_path": file_full_path
            }

@app.get("/all")
def all():
    # DB 연결 SELECT ALL
    # 결과값 retrun
    

    connection = pymysql.connect(
        host="172.18.0.1",
        user='mnist',
        password='1234',
        database='mnistdb',
        port=int('53306'),
        cursorclass=pymysql.cursors.DictCursor
        )

    with connection:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM image_processing"
            cursor.execute(insert_sql, (file_name, file_full_path, request_time, username))
            result = cursor.fetchall()
            print(result)

@app.get("/one")
def one():
    # DB 연결 SELECT 값 중 하나만 리턴
    # 결과값 retrun


    connection = pymysql.connect(
        host="172.18.0.1",
        user='mnist',
        password='1234',
        database='mnistdb',
        port=int('53306'),
        cursorclass=pymysql.cursors.DictCursor
        )
    with connection:    
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `file_name`, `file_path` FROM image_processing WHERE 'request_time' > '2024-09-20 14:40:05'"
            cursor.execute(insert_sql, (file_name, file_full_path, request_time, username))
            result = cursor.fetchall()
            print(result)
