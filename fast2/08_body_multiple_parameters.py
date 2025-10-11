"""
FastAPI 자습서 - 본문 - 다중 매개변수 (Body - Multiple Parameters)

여러 본문 매개변수와 경로/쿼리 매개변수를 함께 사용합니다.
"""

from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()


class Item(BaseModel):
    """아이템 모델"""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    """사용자 모델"""
    username: str
    full_name: str | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    """
    여러 본문 매개변수
    - item과 user 두 개의 본문 매개변수
    """
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@app.put("/items-with-importance/{item_id}")
async def update_item_with_importance(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body()]
):
    """
    단일 값도 본문 매개변수로 받기
    - Body()를 사용하여 명시적으로 본문에서 받음
    """
    results = {
        "item_id": item_id,
        "item": item,
        "user": user,
        "importance": importance
    }
    return results


@app.put("/items-with-query/{item_id}")
async def update_item_with_query(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None
):
    """
    본문 매개변수와 쿼리 매개변수 혼합
    """
    results = {
        "item_id": item_id,
        "item": item,
        "user": user,
        "importance": importance
    }
    if q:
        results.update({"q": q})
    return results


@app.put("/items-embed/{item_id}")
async def update_item_embed(
    item_id: int,
    item: Annotated[Item, Body(embed=True)]
):
    """
    단일 본문 매개변수 임베드
    - embed=True: JSON에서 키로 감싸서 받음
    - 예: {"item": {...}} 형태로 전송
    """
    results = {"item_id": item_id, "item": item}
    return results


@app.put("/items-with-metadata/{item_id}")
async def update_item_with_metadata(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            title="아이템",
            description="수정할 아이템 정보",
            example={
                "name": "노트북",
                "description": "고성능 노트북",
                "price": 1500000,
                "tax": 150000
            }
        )
    ],
    user: Annotated[
        User,
        Body(
            example={
                "username": "hong",
                "full_name": "홍길동"
            }
        )
    ],
    importance: Annotated[
        int,
        Body(
            gt=0,
            le=5,
            description="아이템의 중요도 (1-5)"
        )
    ]
):
    """
    메타데이터와 예제가 포함된 본문 매개변수
    """
    results = {
        "item_id": item_id,
        "item": item,
        "user": user,
        "importance": importance
    }
    return results


# 실행 방법:
# uvicorn 08_body_multiple_parameters:app --reload
#
# 테스트 (Swagger UI 사용 권장):
# http://127.0.0.1:8000/docs
#
# curl 예제:
# curl -X PUT "http://127.0.0.1:8000/items/1" \
#      -H "Content-Type: application/json" \
#      -d '{
#            "item": {"name": "노트북", "price": 1000000},
#            "user": {"username": "hong", "full_name": "홍길동"}
#          }'

