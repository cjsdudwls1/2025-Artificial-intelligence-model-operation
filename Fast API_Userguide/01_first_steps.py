"""
FastAPI 자습서 - 첫걸음 (First Steps)

가장 간단한 FastAPI 애플리케이션 예제입니다.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    """루트 경로"""
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    """이름을 받아서 인사하기"""
    return {"message": f"안녕하세요 {name}님!"}


# 실행 방법:
# uvicorn 01_first_steps:app --reload
#
# 테스트:
# http://127.0.0.1:8000/
# http://127.0.0.1:8000/hello/홍길동
# http://127.0.0.1:8000/docs

