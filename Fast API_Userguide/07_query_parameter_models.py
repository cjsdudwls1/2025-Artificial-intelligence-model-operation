"""
FastAPI 자습서 - 쿼리 매개변수 모델 (Query Parameter Models)

Pydantic 모델을 사용하여 쿼리 매개변수를 그룹화하고 관리합니다.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class FilterParams(BaseModel):
    """쿼리 매개변수 모델"""
    limit: int = Field(default=100, gt=0, le=100)
    offset: int = Field(default=0, ge=0)
    order_by: str = Field(default="created_at")
    tags: list[str] = Field(default=[])


@app.get("/items/")
async def read_items(filter_query: FilterParams):
    """
    쿼리 매개변수 모델 사용
    - 여러 쿼리 매개변수를 하나의 모델로 관리
    """
    return {
        "filter": filter_query,
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
    }


class SearchParams(BaseModel):
    """검색 매개변수"""
    q: str | None = Field(
        default=None,
        title="검색어",
        description="검색할 키워드",
        min_length=1,
        max_length=50
    )
    category: str | None = Field(default=None, max_length=20)
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    in_stock: bool = Field(default=True)


@app.get("/products/search")
async def search_products(search: SearchParams):
    """
    상품 검색
    - 복잡한 검색 조건을 모델로 관리
    """
    result = {
        "search_params": search,
        "results": []
    }
    
    if search.q:
        result["results"].append({
            "id": 1,
            "name": f"{search.q}와 관련된 상품"
        })
    
    return result


class PaginationParams(BaseModel):
    """페이지네이션 매개변수"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    page_size: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수")
    
    @property
    def offset(self) -> int:
        """오프셋 계산"""
        return (self.page - 1) * self.page_size


@app.get("/users/")
async def read_users(pagination: PaginationParams):
    """
    사용자 목록 조회
    - 페이지네이션 적용
    """
    return {
        "page": pagination.page,
        "page_size": pagination.page_size,
        "offset": pagination.offset,
        "users": [
            {"id": i, "name": f"User {i}"}
            for i in range(pagination.offset, pagination.offset + pagination.page_size)
        ]
    }


class AdvancedFilterParams(BaseModel):
    """고급 필터 매개변수"""
    search: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    min_rating: float = Field(default=0, ge=0, le=5)
    max_rating: float = Field(default=5, ge=0, le=5)
    sort_by: str = Field(default="relevance", pattern="^(relevance|price|rating|date)$")
    ascending: bool = True
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


@app.get("/products/")
async def list_products(filters: AdvancedFilterParams):
    """
    상품 목록 조회
    - 고급 필터링 및 정렬 옵션
    """
    return {
        "filters": filters,
        "total": 100,
        "products": [
            {
                "id": i,
                "name": f"Product {i}",
                "rating": 4.5
            }
            for i in range(1, 6)
        ]
    }


# 실행 방법:
# uvicorn 07_query_parameter_models:app --reload
#
# 테스트:
# http://127.0.0.1:8000/items/?limit=50&offset=10&order_by=name
# http://127.0.0.1:8000/products/search?q=노트북&min_price=500000&in_stock=true
# http://127.0.0.1:8000/users/?page=2&page_size=10
# http://127.0.0.1:8000/products/?search=laptop&sort_by=price&page=1&per_page=20
# http://127.0.0.1:8000/docs

