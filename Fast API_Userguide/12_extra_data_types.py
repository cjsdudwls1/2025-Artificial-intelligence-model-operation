"""
FastAPI 자습서 - 추가 데이터 자료형 (Extra Data Types)

Pydantic이 지원하는 추가 데이터 타입들을 사용합니다.
"""

from fastapi import FastAPI, Body
from pydantic import BaseModel, Field, HttpUrl, EmailStr, FilePath, DirectoryPath
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from uuid import UUID
from typing import Annotated

app = FastAPI()


# 1. UUID
@app.get("/items/{item_id}")
async def read_item(item_id: UUID):
    """
    UUID 타입 사용
    예: 123e4567-e89b-12d3-a456-426614174000
    """
    return {"item_id": item_id}


# 2. 날짜와 시간
class Event(BaseModel):
    """이벤트 모델 (날짜/시간 타입)"""
    name: str
    event_date: date = Field(example="2024-12-31")
    event_time: time = Field(example="14:30:00")
    event_datetime: datetime = Field(example="2024-12-31T14:30:00")
    duration: timedelta = Field(example=7200)  # 초 단위


@app.post("/events/")
async def create_event(event: Event):
    """날짜와 시간 타입 사용"""
    return event


# 3. Decimal (정확한 소수 계산)
class Financial(BaseModel):
    """금융 모델 (Decimal 사용)"""
    amount: Decimal = Field(example="99.99")
    tax_rate: Decimal = Field(example="0.15")
    currency: str = Field(example="KRW")


@app.post("/financial/")
async def create_financial(financial: Financial):
    """
    Decimal 타입 사용
    - 금융 계산에 적합한 정확한 소수 처리
    """
    total = financial.amount * (1 + financial.tax_rate)
    return {
        "financial": financial,
        "total": total
    }


# 4. URL과 이메일
class Contact(BaseModel):
    """연락처 모델"""
    email: EmailStr = Field(example="hong@example.com")
    website: HttpUrl = Field(example="https://example.com")


@app.post("/contacts/")
async def create_contact(contact: Contact):
    """URL과 이메일 타입 사용"""
    return contact


# 5. bytes와 frozenset
class FileData(BaseModel):
    """파일 데이터 모델"""
    file_hash: str
    tags: frozenset[str] = Field(example=["tag1", "tag2"])


@app.post("/files/metadata")
async def create_file_metadata(
    file_data: FileData,
    file_bytes: Annotated[bytes, Body(example=b"file content")]
):
    """bytes와 frozenset 사용"""
    return {
        "file_data": file_data,
        "file_size": len(file_bytes)
    }


# 6. 모든 타입 종합
class CompleteExample(BaseModel):
    """모든 추가 타입을 사용하는 예제"""
    # UUID
    id: UUID = Field(example="123e4567-e89b-12d3-a456-426614174000")
    
    # 날짜와 시간
    created_date: date = Field(example="2024-01-01")
    created_time: time = Field(example="10:30:00")
    created_at: datetime = Field(example="2024-01-01T10:30:00")
    expires_in: timedelta = Field(example=86400)  # 1일
    
    # Decimal
    price: Decimal = Field(example="999.99")
    
    # URL과 이메일
    email: EmailStr = Field(example="user@example.com")
    website: HttpUrl = Field(example="https://example.com")
    
    # 집합
    tags: frozenset[str] = Field(default_factory=frozenset, example=["python", "fastapi"])
    
    # 기타
    metadata: dict[str, str] = Field(default_factory=dict)


@app.post("/complete/")
async def create_complete(item: CompleteExample):
    """모든 추가 데이터 타입 종합"""
    return item


# 7. 날짜/시간 쿼리 매개변수
@app.get("/items/search")
async def search_items(
    start_date: date | None = None,
    end_date: date | None = None,
    start_time: datetime | None = None
):
    """
    날짜/시간 쿼리 매개변수
    예: ?start_date=2024-01-01&end_date=2024-12-31
    """
    return {
        "start_date": start_date,
        "end_date": end_date,
        "start_time": start_time
    }


# 8. 복잡한 예제
class Product(BaseModel):
    """상품 모델 (다양한 타입 사용)"""
    product_id: UUID
    name: str
    price: Decimal = Field(gt=0)
    created_at: datetime
    updated_at: datetime | None = None
    available_from: date
    available_until: date | None = None
    delivery_time: timedelta = Field(example=259200)  # 3일
    manufacturer_website: HttpUrl
    support_email: EmailStr
    categories: frozenset[str] = Field(default_factory=frozenset)
    properties: dict[str, str] = Field(default_factory=dict)


@app.post("/products/")
async def create_product(product: Product):
    """다양한 추가 데이터 타입을 사용하는 상품"""
    return product


# 9. 응답에서 추가 타입 사용
@app.get("/current-time")
async def get_current_time():
    """현재 시간 반환"""
    return {
        "current_datetime": datetime.now(),
        "current_date": date.today(),
        "current_time": datetime.now().time()
    }


@app.get("/generate-uuid")
async def generate_uuid():
    """UUID 생성"""
    import uuid
    return {
        "uuid": uuid.uuid4()
    }


# 실행 방법:
# uvicorn 12_extra_data_types:app --reload
#
# 테스트:
# http://127.0.0.1:8000/items/123e4567-e89b-12d3-a456-426614174000
# http://127.0.0.1:8000/items/search?start_date=2024-01-01&end_date=2024-12-31
# http://127.0.0.1:8000/current-time
# http://127.0.0.1:8000/generate-uuid
# http://127.0.0.1:8000/docs

