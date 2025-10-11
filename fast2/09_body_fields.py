"""
FastAPI 자습서 - 본문 - 필드 (Body - Fields)

Pydantic의 Field를 사용하여 모델 필드에 추가 검증과 메타데이터를 설정합니다.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    """아이템 모델 (Field 사용)"""
    name: str = Field(
        ...,
        title="이름",
        description="아이템의 이름",
        min_length=1,
        max_length=100,
        example="노트북"
    )
    description: str | None = Field(
        default=None,
        title="설명",
        description="아이템에 대한 자세한 설명",
        max_length=500,
        example="고성능 게이밍 노트북"
    )
    price: float = Field(
        ...,
        gt=0,
        description="가격 (0보다 커야 함)",
        example=1500000
    )
    tax: float | None = Field(
        default=None,
        ge=0,
        description="세금 (0 이상)",
        example=150000
    )


@app.post("/items/")
async def create_item(item: Item):
    """아이템 생성"""
    return item


class Product(BaseModel):
    """상품 모델 (다양한 Field 검증)"""
    name: str = Field(min_length=3, max_length=50)
    sku: str = Field(
        ...,
        pattern="^[A-Z]{3}-[0-9]{4}$",
        description="SKU 형식: ABC-1234",
        example="LAP-1234"
    )
    price: float = Field(gt=0, le=1000000)
    discount_percentage: float = Field(ge=0, le=100, default=0)
    stock: int = Field(ge=0, default=0)
    rating: float = Field(ge=0, le=5, default=0)
    tags: list[str] = Field(default_factory=list, max_length=10)


@app.post("/products/")
async def create_product(product: Product):
    """상품 생성 (다양한 검증)"""
    return product


class User(BaseModel):
    """사용자 모델"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_]+$",
        description="사용자명 (영문, 숫자, 언더스코어만)",
        example="hong123"
    )
    email: str = Field(
        ...,
        pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
        description="이메일 주소",
        example="hong@example.com"
    )
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        example="홍길동"
    )
    age: int | None = Field(
        default=None,
        ge=0,
        le=150,
        description="나이",
        example=25
    )
    website: str | None = Field(
        default=None,
        pattern="^https?://",
        description="웹사이트 URL",
        example="https://example.com"
    )


@app.post("/users/")
async def create_user(user: User):
    """사용자 생성"""
    return user


class Image(BaseModel):
    """이미지 모델"""
    url: str = Field(
        ...,
        description="이미지 URL",
        example="https://example.com/image.jpg"
    )
    name: str = Field(..., max_length=100)


class ItemWithImages(BaseModel):
    """이미지가 포함된 아이템"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    tax: float | None = Field(default=None, ge=0)
    tags: set[str] = Field(default_factory=set)
    images: list[Image] | None = Field(default=None)


@app.post("/items-with-images/")
async def create_item_with_images(item: ItemWithImages):
    """이미지가 포함된 아이템 생성"""
    return item


class Config(BaseModel):
    """설정 모델"""
    app_name: str = Field(default="MyApp")
    admin_email: str = Field(
        ...,
        pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    )
    max_connections: int = Field(default=100, ge=1, le=1000)
    timeout: float = Field(default=30.0, gt=0, le=300)
    debug: bool = Field(default=False)
    allowed_hosts: list[str] = Field(default_factory=lambda: ["localhost"])


@app.post("/config/")
async def update_config(config: Config):
    """설정 업데이트"""
    return config


# 실행 방법:
# uvicorn 09_body_fields:app --reload
#
# 테스트 (Swagger UI 사용 권장):
# http://127.0.0.1:8000/docs
#
# curl 예제:
# curl -X POST "http://127.0.0.1:8000/items/" \
#      -H "Content-Type: application/json" \
#      -d '{
#            "name": "노트북",
#            "description": "고성능 노트북",
#            "price": 1500000,
#            "tax": 150000
#          }'

