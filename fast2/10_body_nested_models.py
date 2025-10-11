"""
FastAPI 자습서 - 본문 - 중첩 모델 (Body - Nested Models)

중첩된 Pydantic 모델을 사용하여 복잡한 데이터 구조를 정의합니다.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()


# 기본 중첩 모델
class Image(BaseModel):
    """이미지 모델"""
    url: HttpUrl
    name: str


class Item(BaseModel):
    """아이템 모델 (이미지 포함)"""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.post("/items/")
async def create_item(item: Item):
    """중첩 모델을 사용한 아이템 생성"""
    return item


# 리스트 중첩
class ItemWithImages(BaseModel):
    """여러 이미지를 가진 아이템"""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


@app.post("/items-with-images/")
async def create_item_with_images(item: ItemWithImages):
    """여러 이미지를 가진 아이템 생성"""
    return item


# 깊은 중첩
class Address(BaseModel):
    """주소 모델"""
    street: str
    city: str
    state: str | None = None
    country: str
    zip_code: str = Field(..., pattern="^[0-9]{5}(-[0-9]{4})?$")


class Contact(BaseModel):
    """연락처 모델"""
    phone: str
    email: str
    address: Address


class Company(BaseModel):
    """회사 모델"""
    name: str
    website: HttpUrl | None = None
    contact: Contact


class User(BaseModel):
    """사용자 모델 (회사 정보 포함)"""
    username: str
    email: str
    full_name: str | None = None
    company: Company | None = None


@app.post("/users/")
async def create_user(user: User):
    """깊은 중첩 모델"""
    return user


# 딕셔너리 사용
class Offer(BaseModel):
    """할인 정보"""
    name: str
    description: str | None = None
    price: float
    items: list[Item]


@app.post("/offers/")
async def create_offer(offer: Offer):
    """여러 아이템이 포함된 할인 정보"""
    return offer


# 순수 리스트 본문
@app.post("/images/multiple")
async def create_multiple_images(images: list[Image]):
    """여러 이미지 생성"""
    return images


# 딕셔너리 본문
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    """
    딕셔너리 본문
    - 키: 인덱스 (정수)
    - 값: 가중치 (실수)
    """
    return weights


# 복잡한 중첩 예제
class Specification(BaseModel):
    """제품 사양"""
    key: str
    value: str


class Manufacturer(BaseModel):
    """제조사"""
    name: str
    country: str
    website: HttpUrl | None = None


class Review(BaseModel):
    """리뷰"""
    username: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class Product(BaseModel):
    """상품 모델 (복잡한 중첩)"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price: float = Field(gt=0)
    discount_percentage: float = Field(ge=0, le=100, default=0)
    category: str
    tags: set[str] = Field(default_factory=set)
    images: list[Image] = Field(default_factory=list)
    specifications: list[Specification] = Field(default_factory=list)
    manufacturer: Manufacturer
    reviews: list[Review] = Field(default_factory=list)
    related_products: list[int] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


@app.post("/products/")
async def create_product(product: Product):
    """복잡한 중첩 모델을 사용한 상품 생성"""
    return product


# 자기 참조 모델
class Category(BaseModel):
    """카테고리 (자기 참조)"""
    name: str
    description: str | None = None
    parent_id: int | None = None
    subcategories: list['Category'] = Field(default_factory=list)


@app.post("/categories/")
async def create_category(category: Category):
    """자기 참조 모델을 사용한 카테고리 생성"""
    return category


# 실행 방법:
# uvicorn 10_body_nested_models:app --reload
#
# 테스트 (Swagger UI 사용 권장):
# http://127.0.0.1:8000/docs
#
# curl 예제:
# curl -X POST "http://127.0.0.1:8000/items/" \
#      -H "Content-Type: application/json" \
#      -d '{
#            "name": "노트북",
#            "price": 1500000,
#            "tags": ["전자제품", "컴퓨터"],
#            "image": {
#              "url": "https://example.com/laptop.jpg",
#              "name": "노트북 이미지"
#            }
#          }'

