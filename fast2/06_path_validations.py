"""
FastAPI 자습서 - 경로 매개변수와 숫자 검증 (Path Parameters and Numeric Validations)

Path를 사용하여 경로 매개변수에 추가 검증과 메타데이터를 설정합니다.
"""

from fastapi import FastAPI, Path, Query
from typing import Annotated

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="조회할 아이템의 ID")],
    q: Annotated[str | None, Query(alias="item-query")] = None
):
    """
    기본 경로 매개변수 검증
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-order/{item_id}")
async def read_items_order(
    q: str,
    item_id: Annotated[int, Path(title="조회할 아이템의 ID")]
):
    """
    매개변수 순서 변경
    - Python에서 기본값이 없는 매개변수(q)를 먼저 선언
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-asterisk/{item_id}")
async def read_items_asterisk(
    *,
    item_id: Annotated[int, Path(title="조회할 아이템의 ID")],
    q: str
):
    """
    * 사용하여 순서 제약 없애기
    """
    results = {"item_id": item_id, "q": q}
    return results


@app.get("/items-numeric/{item_id}")
async def read_items_numeric(
    item_id: Annotated[
        int,
        Path(
            title="조회할 아이템의 ID",
            ge=1  # greater than or equal
        )
    ],
    q: str | None = None
):
    """
    숫자 검증: 크거나 같음
    - ge: greater than or equal (>= 1)
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-range/{item_id}")
async def read_items_range(
    item_id: Annotated[
        int,
        Path(
            title="조회할 아이템의 ID",
            gt=0,   # greater than (>)
            le=1000  # less than or equal (<=)
        )
    ],
    q: str | None = None,
    size: Annotated[
        float,
        Query(
            gt=0,   # 0보다 큼
            lt=10.5  # 10.5보다 작음
        )
    ] = None
):
    """
    숫자 범위 검증
    - gt: greater than (0보다 큼)
    - le: less than or equal (1000 이하)
    - lt: less than (10.5보다 작음)
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results


@app.get("/items-all-validations/{item_id}")
async def read_items_all_validations(
    item_id: Annotated[
        int,
        Path(
            title="아이템 ID",
            description="조회할 아이템의 고유 식별자",
            ge=1,
            le=9999,
            example=42
        )
    ],
    q: Annotated[
        str | None,
        Query(
            title="검색어",
            min_length=3,
            max_length=50
        )
    ] = None,
    size: Annotated[
        float | None,
        Query(
            title="크기",
            gt=0,
            le=100
        )
    ] = None
):
    """
    모든 검증 조합
    - 경로 매개변수: 1~9999 범위
    - 쿼리 매개변수(문자열): 3~50자
    - 쿼리 매개변수(숫자): 0 초과 100 이하
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results


# 실행 방법:
# uvicorn 06_path_validations:app --reload
#
# 테스트:
# http://127.0.0.1:8000/items/42?q=test
# http://127.0.0.1:8000/items-numeric/1
# http://127.0.0.1:8000/items-range/500?size=5.5
# http://127.0.0.1:8000/items-all-validations/42?q=노트북&size=50
# http://127.0.0.1:8000/docs

