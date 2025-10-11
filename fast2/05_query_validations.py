"""
FastAPI 자습서 - 쿼리 매개변수와 문자열 검증 (Query Parameters and String Validations)

Query를 사용하여 쿼리 매개변수에 추가 검증과 메타데이터를 설정합니다.
"""

from fastapi import FastAPI, Query
from typing import Annotated

app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    """
    기본 검증
    - q: 최대 50자까지 허용
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-validation/")
async def read_items_validation(
    q: Annotated[
        str | None,
        Query(
            min_length=3,
            max_length=50,
            pattern="^[a-zA-Z가-힣]+$"
        )
    ] = None
):
    """
    추가 검증
    - min_length: 최소 3자
    - max_length: 최대 50자
    - pattern: 정규표현식 패턴 (영문/한글만)
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-metadata/")
async def read_items_metadata(
    q: Annotated[
        str | None,
        Query(
            title="검색어",
            description="아이템을 검색하기 위한 쿼리 문자열",
            min_length=3,
            max_length=50,
            example="노트북"
        )
    ] = None
):
    """
    메타데이터 추가
    - title, description: API 문서에 표시
    - example: 예제 값
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-required/")
async def read_items_required(
    q: Annotated[str, Query(min_length=3)]
):
    """
    필수 쿼리 매개변수
    - 기본값이 없으면 필수
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results.update({"q": q})
    return results


@app.get("/items-required-ellipsis/")
async def read_items_required_ellipsis(
    q: Annotated[str, Query(min_length=3)] = ...
):
    """
    명시적 필수 매개변수
    - ... 사용하여 필수임을 명시
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results.update({"q": q})
    return results


@app.get("/items-list/")
async def read_items_list(
    q: Annotated[list[str] | None, Query()] = None
):
    """
    쿼리 매개변수를 리스트로 받기
    - ?q=foo&q=bar 형태로 여러 값 전달
    """
    query_items = {"q": q}
    return query_items


@app.get("/items-list-default/")
async def read_items_list_default(
    q: Annotated[list[str], Query()] = ["foo", "bar"]
):
    """
    기본값을 가진 리스트
    """
    query_items = {"q": q}
    return query_items


@app.get("/items-deprecated/")
async def read_items_deprecated(
    q: Annotated[
        str | None,
        Query(
            deprecated=True,
            description="이 매개변수는 곧 사용 중단될 예정입니다."
        )
    ] = None
):
    """
    사용 중단 표시
    - deprecated=True: API 문서에 사용 중단 표시
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-alias/")
async def read_items_alias(
    q: Annotated[
        str | None,
        Query(
            alias="item-query",
            title="Item Query",
            description="Query string for the items to search"
        )
    ] = None
):
    """
    별칭 사용
    - alias: URL에서 다른 이름 사용 (?item-query=...)
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# 실행 방법:
# uvicorn 05_query_validations:app --reload
#
# 테스트:
# http://127.0.0.1:8000/items/?q=test
# http://127.0.0.1:8000/items-validation/?q=노트북
# http://127.0.0.1:8000/items-required/?q=required
# http://127.0.0.1:8000/items-list/?q=foo&q=bar
# http://127.0.0.1:8000/items-alias/?item-query=test
# http://127.0.0.1:8000/docs

