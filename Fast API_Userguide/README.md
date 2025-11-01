# FastAPI 자습서 - 사용자 안내서

FastAPI 공식 자습서의 각 섹션을 구현한 예제 코드 모음입니다.

## 프로젝트 구조

```
fast2/
├── 01_first_steps.py                # 첫걸음
├── 02_path_parameters.py            # 경로 매개변수
├── 03_query_parameters.py           # 쿼리 매개변수
├── 04_request_body.py               # 요청 본문
├── 05_query_validations.py          # 쿼리 매개변수와 문자열 검증
├── 06_path_validations.py           # 경로 매개변수와 숫자 검증
├── 07_query_parameter_models.py     # 쿼리 매개변수 모델
├── 08_body_multiple_parameters.py   # 본문 - 다중 매개변수
├── 09_body_fields.py                # 본문 - 필드
├── 10_body_nested_models.py         # 본문 - 중첩 모델
├── 11_request_example_data.py       # 요청 예제 데이터 선언
└── 12_extra_data_types.py           # 추가 데이터 자료형
```

## 설치 방법

```bash
pip install -r requirements.txt
```

## 실행 방법

각 파일을 개별적으로 실행할 수 있습니다:

```bash
uvicorn 01_first_steps:app --reload
```

또는

```bash
uvicorn 02_path_parameters:app --reload --port 8001
```

## 테스트 방법

서버 실행 후, 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 참고 자료

- [FastAPI 공식 문서 (한국어)](https://fastapi.tiangolo.com/ko/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

