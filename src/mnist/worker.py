import jigeum.seoul
from mnist.db import select, dml
import random
import os
import requests
import numpy as np
from PIL import Image
from keras.models import load_model
from tensorflow.keras.datasets import mnist


def get_job_img_task():
    sql = """
    SELECT num, file_name, file_path
    FROM image_processing
    WHERE prediction_result IS NULL
    ORDER BY num -- 가장 오래된 요청
    LIMIT 1 -- 하나씩
    """

    r = select(sql, 1)
    
    if len(r) > 0:
        return r[0]
    else:
        return None

def get_model():
    # 모델 로드
    model_path=os.path.dirname(os.path.abspath(__file__))
    model = load_model(f'{model_path}/mnist240924.keras')
    #model_path = os.getenv('MODEL_PATH', '/home/tommy/code/mnist/note/mnist240924.keras')
    #model = load_model(f'{model_path}')

    return model


# 사용자 이미지 불러오기 및 전처리
def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')  # 흑백 이미지로 변환
    img = img.resize((28, 28))  # 크기 조정

    # 흑백 반전
    img = 255 - np.array(img)  # 흑백 반전

    img = np.array(img)
    img = img.reshape(1, 28, 28, 1)  # 모델 입력 형태에 맞게 변형
    img = img / 255.0  # 정규화
    return img
    
def predict_digit(image_path):
    img = preprocess_image(image_path)
    prediction = model.predict(img)
    digit = np.argmax(prediction)
    return digit

def prediction(file_path, num):
    sql = """UPDATE image_processing
    SET prediction_result=%s,
        prediction_model='n03',
        prediction_time=%s
    WHERE num=%s
    """
    presult = predict_digit(file_path) 
    model = get_model()
    dml(sql, presult, model, now(), num)
    print("예측된 숫자:", presult)
    return presult

# image_path = '/home/tommy/code/mnist/note/train_img/2_1.png'

def run():

    """image_processing 테이블을 읽어서 가장 오래된 요청 하나씩을 처리"""
  
    # STEP 1
    # image_processing 테이블의 prediction_result IS NULL 인 ROW 1 개 조회 - num 가져오기
    job = get_job_img_task()

    if job is None:
        print(f"{jigeum.seoul.now()} - job is None")
        return 

    num = job['num']
    file_name = job['file_name']
    file_path = job['file_path']
    
    # STEP 2
    presult = prediction(file_path, num)
    print(jigeum.seoul.now())
    
    # STEP 3
    # LINE 으로 처리 결과 전송
    send_line_noti(file_name, presult)

def send_line_noti(file_name, presult):
    KEY = os.environ.get('LINE_NOIT_TOKEN')
    url = "https://notify-api.line.me/api/notify"
    data = {"message": f"{file_name} -> {presult}"}
    headers = {"Authorization": "Bearer " + KEY}
    response = requests.post(url, data=data, headers=headers)
    print(response.text)
    print("SEND LINE NOTI")
run()
