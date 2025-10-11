# 2학년 2학기 인공지능 모델운영 숙제 모음

이 저장소는 2학년 2학기 인공지능 모델운영 과목의 숙제들을 모아놓은 곳입니다.

## 📁 숙제 목록

### 1. fast 폴더 - FastAPI 기초 실습 (0922 강의 숙제)

**고객 및 상품 관리 시스템** - FastAPI를 사용한 CRUD API 구현

#### 주요 기능:
- **고객 관리**: 고객 정보 조회 및 검색 (이름, 연령, 주소별 필터링)
- **상품 관리**: 상품 정보 조회 및 검색 (이름, 가격, 카테고리별 필터링)
- **가격 견적**: 상품별 세금 포함 가격 계산 (10% 세금 적용)
- **데이터프레임**: pandas를 활용한 데이터 처리 및 HTML 테이블 출력

#### API 엔드포인트:
- `GET /` - 전체 정보 조회
- `GET /customers` - 고객 검색 (쿼리 파라미터: name, age_min, age_max, address)
- `GET /products` - 상품 검색 (쿼리 파라미터: name, price_min, price_max, category)
- `GET /quote/{product_id}` - 특정 상품 가격 견적
- `GET /quote` - 전체 상품 가격 견적
- `GET /dataframe` - JSON 형태 데이터프레임
- `GET /dataframe/html` - HTML 테이블 형태 데이터프레임

#### 기술 스택:
- **FastAPI**: 웹 API 프레임워크
- **Pandas**: 데이터 처리 및 분석
- **Python typing**: 타입 힌트 활용

### 2. fast2 폴더 - FastAPI 자습서 - 사용자 안내서

FastAPI 공식 자습서의 각 섹션을 구현한 예제 코드 모음입니다.

#### 프로젝트 구조:

```
homework/
├── fast/                            # 0922 강의 숙제
│   ├── homework_01.py              # 고객/상품 관리 시스템
│   └── homework_02.py              # 가격 견적 시스템 (확장판)
├── fast2/                          # FastAPI 자습서 예제
│   ├── 01_first_steps.py          # 첫걸음
│   ├── 02_path_parameters.py      # 경로 매개변수
│   ├── 03_query_parameters.py     # 쿼리 매개변수
│   ├── 04_request_body.py         # 요청 본문
│   ├── 05_query_validations.py    # 쿼리 매개변수와 문자열 검증
│   ├── 06_path_validations.py     # 경로 매개변수와 숫자 검증
│   ├── 07_query_parameter_models.py # 쿼리 매개변수 모델
│   ├── 08_body_multiple_parameters.py # 본문 - 다중 매개변수
│   ├── 09_body_fields.py          # 본문 - 필드
│   ├── 10_body_nested_models.py   # 본문 - 중첩 모델
│   ├── 11_request_example_data.py # 요청 예제 데이터 선언
│   └── 12_extra_data_types.py     # 추가 데이터 자료형
└── README.md                       # 프로젝트 설명서
```

## 설치 방법

각 폴더별로 필요한 패키지를 설치하세요:

### fast 폴더 (0922 강의 숙제)
```bash
cd fast
pip install fastapi uvicorn pandas
```

### fast2 폴더 (FastAPI 자습서)
```bash
cd fast2
pip install -r requirements.txt
```

## 실행 방법

### fast 폴더 실행
```bash
cd fast
uvicorn homework_01:app --reload
# 또는
uvicorn homework_02:app --reload
```

### fast2 폴더 실행
```bash
cd fast2
uvicorn 01_first_steps:app --reload
# 또는 다른 예제들
uvicorn 02_path_parameters:app --reload --port 8001
```

## 테스트 방법

서버 실행 후, 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### fast 폴더 API 테스트 예제:
- `GET /customers?age_min=30&age_max=40` - 30-40세 고객 검색
- `GET /products?category=전자제품` - 전자제품 카테고리 상품 검색
- `GET /quote/1` - 노트북 가격 견적 (세금 포함)

## 참고 자료

- [FastAPI 공식 문서 (한국어)](https://fastapi.tiangolo.com/ko/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
