"""
FastAPI 자습서 - 쿼리 매개변수 (Query Parameters)

쿼리 문자열을 사용하여 매개변수를 전달하는 방법입니다.
"""

from fastapi import FastAPI

app = FastAPI()


# 가짜 데이터베이스
fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"}
]


@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    """
    아이템 목록 조회
    - skip: 건너뛸 개수 (기본값: 0)
    - limit: 최대 개수 (기본값: 10)
    """
    return fake_items_db[skip : skip + limit]


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    """
    아이템 조회
    - item_id: 아이템 ID (필수)
    - q: 검색어 (선택)
    """
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


@app.get("/items/{item_id}/details")
async def read_item_details(item_id: str, short: bool = False):
    """
    아이템 상세 정보
    - item_id: 아이템 ID
    - short: 짧은 설명 여부 (기본값: False)
    """
    item = {"item_id": item_id, "name": "멋진 아이템"}
    if not short:
        item.update({
            "description": "이것은 매우 멋진 아이템입니다. 긴 설명이 포함되어 있습니다."
        })
    return item


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: str,
    q: str | None = None,
    short: bool = False
):
    """
    여러 경로 매개변수와 쿼리 매개변수 조합
    """
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({
            "description": "사용자의 아이템에 대한 상세 설명"
        })
    return item


@app.get("/items-required/{item_id}")
async def read_item_required(item_id: str, needy: str):
    """
    필수 쿼리 매개변수
    - needy: 필수 매개변수 (기본값 없음)
    """
    return {"item_id": item_id, "needy": needy}


# 실행 방법:
# uvicorn 03_query_parameters:app --reload
#
# 테스트:
# http://127.0.0.1:8000/items/
# http://127.0.0.1:8000/items/?skip=0&limit=2
# http://127.0.0.1:8000/items/foo?q=test
# http://127.0.0.1:8000/items/foo/details?short=true
# http://127.0.0.1:8000/items-required/foo?needy=required_value

