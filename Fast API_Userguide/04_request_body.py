"""
FastAPI 자습서 - 요청 본문 (Request Body)

Pydantic 모델을 사용하여 요청 본문을 정의하고 검증합니다.
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    """아이템 모델"""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items/")
async def create_item(item: Item):
    """아이템 생성"""
    return item


@app.post("/items-with-tax/")
async def create_item_with_tax(item: Item):
    """아이템 생성 (세금 계산 포함)"""
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    아이템 수정
    - 경로 매개변수와 요청 본문 조합
    """
    return {"item_id": item_id, **item.dict()}


@app.put("/items/{item_id}/with-query")
async def update_item_with_query(item_id: int, item: Item, q: str | None = None):
    """
    아이템 수정
    - 경로 매개변수, 쿼리 매개변수, 요청 본문 조합
    """
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


# 실행 방법:
# uvicorn 04_request_body:app --reload
#
# 테스트 (Swagger UI 사용 권장):
# http://127.0.0.1:8000/docs
#
# curl 예제:
# curl -X POST "http://127.0.0.1:8000/items/" \
#      -H "Content-Type: application/json" \
#      -d '{"name": "노트북", "price": 1000000, "tax": 100000}'

