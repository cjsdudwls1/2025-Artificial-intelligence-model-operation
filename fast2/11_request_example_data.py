"""
FastAPI 자습서 - 요청 예제 데이터 선언 (Declare Request Example Data)

API 문서에 표시될 예제 데이터를 정의합니다.
"""

from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI()


# 1. Field의 example 사용
class Item(BaseModel):
    """아이템 모델 (Field example 사용)"""
    name: str = Field(example="노트북")
    description: str | None = Field(default=None, example="고성능 게이밍 노트북")
    price: float = Field(example=1500000)
    tax: float | None = Field(default=None, example=150000)


@app.post("/items-field/")
async def create_item_field(item: Item):
    """Field example을 사용한 예제"""
    return item


# 2. model_config의 json_schema_extra 사용
class ItemConfig(BaseModel):
    """아이템 모델 (model_config 사용)"""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "노트북",
                    "description": "고성능 게이밍 노트북",
                    "price": 1500000,
                    "tax": 150000
                }
            ]
        }
    }


@app.post("/items-config/")
async def create_item_config(item: ItemConfig):
    """model_config를 사용한 예제"""
    return item


# 3. 여러 예제 정의
class ItemMultipleExamples(BaseModel):
    """아이템 모델 (여러 예제)"""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "노트북",
                    "description": "고성능 게이밍 노트북",
                    "price": 1500000,
                    "tax": 150000
                },
                {
                    "name": "마우스",
                    "description": "무선 게이밍 마우스",
                    "price": 80000,
                    "tax": 8000
                },
                {
                    "name": "키보드",
                    "description": "기계식 키보드",
                    "price": 150000,
                    "tax": 15000
                }
            ]
        }
    }


@app.post("/items-multiple/")
async def create_item_multiple(item: ItemMultipleExamples):
    """여러 예제를 정의"""
    return item


# 4. Body에서 examples 사용
class ItemSimple(BaseModel):
    """간단한 아이템 모델"""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items-body-examples/")
async def create_item_body_examples(
    item: Annotated[
        ItemSimple,
        Body(
            examples=[
                {
                    "name": "노트북",
                    "description": "고성능 게이밍 노트북",
                    "price": 1500000,
                    "tax": 150000
                },
                {
                    "name": "마우스",
                    "description": "무선 게이밍 마우스",
                    "price": 80000,
                    "tax": 8000
                }
            ]
        )
    ]
):
    """Body에서 examples 사용"""
    return item


# 5. OpenAPI에서의 예제 (이름과 설명 포함)
@app.post("/items-openapi-examples/")
async def create_item_openapi_examples(
    item: Annotated[
        ItemSimple,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "일반 예제",
                    "description": "**일반적인** 아이템 예제입니다.",
                    "value": {
                        "name": "노트북",
                        "description": "고성능 게이밍 노트북",
                        "price": 1500000,
                        "tax": 150000
                    }
                },
                "premium": {
                    "summary": "프리미엄 예제",
                    "description": "**프리미엄** 아이템 예제입니다.",
                    "value": {
                        "name": "프리미엄 노트북",
                        "description": "최고급 게이밍 노트북",
                        "price": 3000000,
                        "tax": 300000
                    }
                },
                "budget": {
                    "summary": "저가형 예제",
                    "description": "**저가형** 아이템 예제입니다.",
                    "value": {
                        "name": "저가형 마우스",
                        "description": "기본 마우스",
                        "price": 10000,
                        "tax": 1000
                    }
                }
            }
        )
    ]
):
    """OpenAPI examples 사용 (이름과 설명 포함)"""
    return item


# 6. 복잡한 모델의 예제
class Image(BaseModel):
    """이미지 모델"""
    url: str = Field(example="https://example.com/image.jpg")
    name: str = Field(example="상품 이미지")


class Tag(BaseModel):
    """태그 모델"""
    name: str = Field(example="전자제품")
    color: str = Field(example="#FF5733")


class Product(BaseModel):
    """상품 모델"""
    name: str = Field(example="고급 노트북")
    description: str | None = Field(default=None, example="최신 사양의 고급 노트북")
    price: float = Field(example=2500000)
    discount: float = Field(default=0, example=10.0)
    images: list[Image] = Field(
        default_factory=list,
        example=[
            {"url": "https://example.com/1.jpg", "name": "전면"},
            {"url": "https://example.com/2.jpg", "name": "측면"}
        ]
    )
    tags: list[Tag] = Field(
        default_factory=list,
        example=[
            {"name": "전자제품", "color": "#FF5733"},
            {"name": "컴퓨터", "color": "#33FF57"}
        ]
    )


@app.post("/products/")
async def create_product(product: Product):
    """복잡한 모델의 예제"""
    return product


# 실행 방법:
# uvicorn 11_request_example_data:app --reload
#
# 테스트 (Swagger UI에서 예제 확인):
# http://127.0.0.1:8000/docs

