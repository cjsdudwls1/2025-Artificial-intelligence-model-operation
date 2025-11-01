# 🎓 대학 강좌 데이터 EDA (Exploratory Data Analysis)

Google Gemini AI를 활용한 대학 강좌 데이터 탐색적 분석 웹 애플리케이션

## 📋 프로젝트 개요

이 프로젝트는 대학 강좌 데이터를 분석하고 시각화하는 웹 애플리케이션입니다. 
Google Gemini AI API를 활용하여 데이터에 대한 지능적인 인사이트를 제공하며, 
Gradio를 통해 사용자 친화적인 인터페이스를 제공합니다.

## ✨ 주요 기능

### 1. 📊 기본 정보
- 데이터셋 구조 확인
- 컬럼 정보 및 데이터 타입
- 결측치 확인
- 샘플 데이터 미리보기

### 2. 📈 통계 요약
- 수치형 데이터 통계 분석 (평균, 표준편차, 최소/최대값 등)
- 범주형 데이터 분포 분석
- 고유값 및 빈도 분석

### 3. 📉 시각화
- 학과별 강좌 수 분석
- 수강인원 분포
- 학년별 강좌 분포
- 교수별 강좌 수
- 학점별/수업주수별 분포

### 4. 📊 인터랙티브 차트
- Plotly 기반 동적 차트
- 학과별 평균 수강인원
- 과정별 강좌 분포 (파이 차트)
- 학년별 수강인원 통계

### 5. 🤖 AI 분석 (Gemini)
- **자동 인사이트 생성**: AI가 데이터를 분석하여 자동으로 통찰 제공
- **질의응답**: 데이터에 대해 자연어로 질문하고 AI로부터 답변 받기

### 6. 🔍 강좌 검색
- 교과목명, 학과명, 교수명으로 강좌 검색

## 🚀 설치 및 실행

### 1. 필요 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
python app.py
```

또는 Windows에서:

```bash
run.bat
```

### 3. 접속

로컬 브라우저에서 자동으로 열리며, 외부 공유 링크도 생성됩니다.
- 로컬: http://localhost:7860
- 외부 공유: 터미널에 표시되는 gradio.live 링크 사용

## 📦 필요 패키지

- `pandas`: 데이터 처리 및 분석
- `gradio`: 웹 UI 프레임워크
- `google-generativeai`: Google Gemini AI API
- `matplotlib`: 정적 시각화
- `seaborn`: 고급 통계 시각화
- `plotly`: 인터랙티브 시각화

## 🔑 API 키

Google Gemini API 키가 코드에 포함되어 있습니다. 
프로덕션 환경에서는 환경 변수로 관리하는 것을 권장합니다.

```python
# 환경 변수 사용 예시
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-default-key')
```

## 📊 데이터 구조

`class.txt` 파일은 다음과 같은 컬럼을 포함합니다:

| 컬럼명 | 설명 |
|--------|------|
| 과정 | 강좌 과정 유형 (전공심화, 정규일반 등) |
| 개설학과 | 강좌를 개설한 학과 |
| 교과목코드 | 교과목 고유 코드 |
| 교과목명 | 교과목 이름 |
| 개설학년 | 대상 학년 |
| 영역구분 | 영역 분류 (전공, 교양 등) |
| 수강인원 | 수강 신청 인원 |
| 강좌대표교수 | 대표 교수명 |
| 강좌담당교수 | 담당 교수명 |
| 수업주수 | 수업 진행 주수 |
| 교과목학점 | 학점 |
| 강의유형구분 | 강의 유형 (실습, 이론 등) |

## 💡 사용 예시

### AI에게 질문하기

```
질문: "수강인원이 가장 많은 학과는 어디인가요?"
질문: "각 학과의 평균 수강인원을 비교해주세요."
질문: "3학년 강좌의 특징은 무엇인가요?"
질문: "수업주수가 7주인 강좌와 15주인 강좌의 차이점은 무엇인가요?"
```

## 🛠️ 기술 스택

- **Python 3.8+**
- **Gradio**: 웹 인터페이스
- **Pandas**: 데이터 분석
- **Matplotlib & Seaborn**: 데이터 시각화
- **Plotly**: 인터랙티브 차트
- **Google Gemini AI**: 자연어 처리 및 인사이트 생성

## 📝 주의사항

- Windows 환경에서 한글 폰트는 'Malgun Gothic'을 사용합니다.
- 다른 OS에서는 적절한 한글 폰트로 변경이 필요할 수 있습니다.
- Gradio의 `share=True` 옵션은 72시간 동안 유효한 공개 링크를 생성합니다.

## 🔧 문제 해결

### 한글이 깨져 보이는 경우
```python
# Mac
plt.rcParams['font.family'] = 'AppleGothic'

# Linux
plt.rcParams['font.family'] = 'NanumGothic'
```

### 포트가 이미 사용 중인 경우
`app.py`의 `server_port` 값을 다른 번호로 변경하세요.

```python
demo.launch(
    share=True,
    server_port=7861,  # 다른 포트 번호 사용
)
```

## 📄 라이선스

This project is for educational purposes.

## 👤 작성자

대학 강좌 데이터 분석 프로젝트

---

**Made with ❤️ using Google Gemini AI and Gradio**

