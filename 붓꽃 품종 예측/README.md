# 🌸 붓꽃 품종 예측 API

FastAPI와 Gradio를 활용한 붓꽃(Iris) 품종 예측 웹 애플리케이션

## 📋 프로젝트 개요

이 프로젝트는 머신러닝 모델을 사용하여 붓꽃의 품종을 예측하는 웹 애플리케이션입니다.
scikit-learn의 DecisionTreeClassifier를 사용하여 학습된 모델을 FastAPI 서버로 제공하고,
Gradio를 통해 사용자 친화적인 웹 인터페이스를 제공합니다.

## ✨ 주요 기능

### 1. 🤖 머신러닝 모델
- **DecisionTreeClassifier** 기반 붓꽃 품종 분류 모델
- Iris 데이터셋으로 학습된 모델 (`iris_model.pkl`)
- 꽃받침 길이, 꽃받침 너비, 꽃잎 길이, 꽃잎 너비를 입력받아 품종 예측

### 2. 🌐 FastAPI 서버
- RESTful API 엔드포인트 제공
- `/` - API 상태 확인
- `/predict` - 붓꽃 품종 예측 (POST 요청)
- 포트 8004에서 실행

### 3. 🎨 Gradio 클라이언트
- 직관적인 웹 인터페이스
- 슬라이더를 통한 입력값 조정
- 실시간 예측 결과 표시
- 포트 7861에서 실행

## 🚀 설치 및 실행

### 1. 필요 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 서버 실행

먼저 FastAPI 서버를 실행합니다:

```bash
python main.py
```

서버가 실행되면 다음 주소에서 API를 확인할 수 있습니다:
- API 문서: http://localhost:8004/docs
- 대체 문서: http://localhost:8004/redoc
- API 루트: http://localhost:8004

### 3. 클라이언트 실행

새로운 터미널 창에서 Gradio 클라이언트를 실행합니다:

```bash
python client.py
```

클라이언트가 실행되면 브라우저에서 자동으로 열리며, 다음 주소에서 접속할 수 있습니다:
- 로컬: http://localhost:7861

## 📦 필요 패키지

- `fastapi`: RESTful API 프레임워크
- `uvicorn`: ASGI 서버
- `pandas`: 데이터 처리
- `scikit-learn`: 머신러닝 라이브러리
- `gradio`: 웹 UI 프레임워크
- `requests`: HTTP 요청 (클라이언트에서 사용)

## 📊 API 사용법

### 예측 요청

**엔드포인트**: `POST /predict`

**요청 본문**:
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

**응답**:
```json
{
  "prediction": "setosa"
}
```

### cURL 예시

```bash
curl -X POST "http://localhost:8004/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "sepal_length": 5.1,
       "sepal_width": 3.5,
       "petal_length": 1.4,
       "petal_width": 0.2
     }'
```

### Python 예시

```python
import requests

response = requests.post(
    "http://localhost:8004/predict",
    json={
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
)

print(response.json())
# 출력: {"prediction": "setosa"}
```

## 🌸 붓꽃 품종

이 모델은 다음 3가지 붓꽃 품종을 예측할 수 있습니다:

1. **setosa** (세토사)
2. **versicolor** (버시컬러)
3. **virginica** (버지니카)

## 📈 모델 정보

- **알고리즘**: DecisionTreeClassifier
- **학습 데이터**: Iris 데이터셋 (scikit-learn 내장)
- **테스트 데이터 비율**: 20%
- **랜덤 시드**: 42
- **입력 특성**:
  - `sepal_length`: 꽃받침 길이 (cm)
  - `sepal_width`: 꽃받침 너비 (cm)
  - `petal_length`: 꽃잎 길이 (cm)
  - `petal_width`: 꽃잎 너비 (cm)

## 🛠️ 기술 스택

- **Python 3.8+**
- **FastAPI**: 고성능 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **scikit-learn**: 머신러닝 라이브러리
- **Gradio**: 웹 UI 프레임워크
- **Pydantic**: 데이터 검증

## 📝 파일 구조

```
fast4/
├── main.py              # FastAPI 서버
├── client.py            # Gradio 클라이언트
├── iris_model.pkl       # 학습된 모델 파일
├── requirements.txt     # 필요 패키지 목록
└── README.md           # 프로젝트 문서
```

## 🔧 문제 해결

### 포트가 이미 사용 중인 경우

**서버 포트 변경** (`main.py`):
```python
uvicorn.run(app, host="0.0.0.0", port=8005)  # 다른 포트 번호 사용
```

**클라이언트 포트 변경** (`client.py`):
```python
iface.launch(server_port=7862, share=False)  # 다른 포트 번호 사용
```

**서버 URL 변경** (`client.py`):
```python
SERVER_URL = "http://localhost:8005"  # 서버 포트와 일치시켜야 함
```

### 서버에 연결할 수 없는 경우

1. FastAPI 서버가 실행 중인지 확인하세요.
2. `client.py`의 `SERVER_URL`이 올바른지 확인하세요.
3. 방화벽 설정을 확인하세요.

### 모델 파일이 없는 경우

`main.py`를 실행하면 자동으로 모델이 학습되고 `iris_model.pkl` 파일로 저장됩니다.

## 📄 라이선스

This project is for educational purposes.

## 👤 작성자

붓꽃 품종 예측 프로젝트

---

**Made with ❤️ using FastAPI and Gradio**

