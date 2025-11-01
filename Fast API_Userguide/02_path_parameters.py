"""
FastAPI 자습서 - 경로 매개변수 (Path Parameters)

경로에서 매개변수를 받아 처리하는 방법을 다룹니다.
"""

from fastapi import FastAPI
from enum import Enum

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """아이템 ID로 조회"""
    return {"item_id": item_id}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    """사용자 ID로 조회"""
    return {"user_id": user_id}


# 경로 순서가 중요합니다
@app.get("/users/me")
async def read_user_me():
    """현재 사용자 정보"""
    return {"user_id": "현재 사용자"}


@app.get("/users/{user_id}")
async def read_user_by_id(user_id: str):
    """특정 사용자 정보"""
    return {"user_id": user_id}


# Enum을 사용한 경로 매개변수
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    """모델 선택 (Enum 사용)"""
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    
    return {"model_name": model_name, "message": "Have some residuals"}


# 파일 경로를 매개변수로 받기
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    """파일 경로를 매개변수로 받기"""
    return {"file_path": file_path}


# 실행 방법:
# uvicorn 02_path_parameters:app --reload
#
# 테스트:
# http://127.0.0.1:8000/items/42
# http://127.0.0.1:8000/users/me
# http://127.0.0.1:8000/models/alexnet
# http://127.0.0.1:8000/files/home/user/file.txt

