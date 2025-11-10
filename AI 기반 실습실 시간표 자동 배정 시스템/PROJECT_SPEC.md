# 프로젝트 명세서

## 목적

실습실·실습센터 시간표를 자동 배정하고 공실을 분석·시각화하며, 강의 관리 및 버전 관리를 지원하는 시스템입니다.

## 주요 기능

### 1. 시간표 자동 배정
- CSV 파일 업로드 → 자동 시간표 생성
- 3시간 연속 블록 배정
- 공실 최소화 알고리즘
- 교수/강의실 충돌 자동 검증

### 2. 강의 관리
- 개별 강의 추가/삭제
- 실시간 시간표 재배정
- 버전 이력 자동 저장

### 3. 버전 관리
- 모든 시간표 변경 이력 저장
- 이전 버전 조회
- 버전 복원 (롤백) 기능

### 4. 공실 분석
- 강의실별 활용률 계산
- 시간대별 공실 정보 제공

## 데이터 스키마

### 입력 데이터 (CSV)
- 과정, 개설학과, 교과목코드, 교과목명, 개설학년, 영역구분
- 수강인원, 강좌대표교수, 강좌담당교수, 수업주수, 교과목학점
- 강의유형구분 (실습 여부)

### 데이터베이스 테이블

**courses** - 교과목 정보
- id (PK), process, department, course_code, course_name, grade, area
- enrollment, main_instructor, instructor, weeks, credits, is_lab
- is_deleted (논리적 삭제), created_at, updated_at

**schedules** - 현재 배정된 시간표
- id (PK), course_id, course_code, course_name, instructor, department
- day, start_time, end_time, room
- is_lab, enrollment, weeks, credits

**timetable_versions** - 버전 정보
- id (PK), version_number (UNIQUE), created_at, description, is_active

**schedule_history** - 과거 버전의 시간표
- id (PK), version_id (FK), course_id, course_code, course_name
- instructor, department, day, start_time, end_time, room
- is_lab, enrollment, weeks, credits

## 제약 조건

### 강의실
- **기본**: 1215, 1216, 1217, 1418 (모두 실습실)
- **임대**: RENTAL_1 (필요시 사용)

### 시간표
- **요일**: 월~금
- **시간**: 09:00~18:00
- **블록**: 3시간 연속 (09:00~12:00, 10:00~13:00, ..., 15:00~18:00)
- **강의실 수용인원**: 제한 없음
- **교수 충돌**: 동일 시간 동일 교수 중복 금지
- **강의실 충돌**: 동일 시간 동일 강의실 중복 금지

### 최적화 기준
1. 공실(미사용 블록) 최소화
2. 실습 과목 우선 배정
3. 외부 대여 강의실 최소 사용

## 시스템 아키텍처

```
┌─────────────────────┐
│  Frontend (HTML)    │
│  static/index.html  │
│  static/style.css   │
│  static/script.js   │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  api.py             │
│  ├─ /api/schedule   │
│  ├─ /api/courses    │
│  └─ /api/versions   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Business Logic     │
│  scheduler.py       │  ← 시간표 배정 알고리즘
│  vacancy_analyzer.py│  ← 공실 분석
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Database Layer     │
│  models.py          │  ← SQLAlchemy ORM
│  timetable.db       │  ← SQLite
└─────────────────────┘
```

## API 명세

### 시간표 관리
- `POST /api/schedule/build` - CSV 업로드 및 배정
- `GET /api/schedule` - 현재 시간표 조회
- `GET /api/vacancy` - 공실 분석

### 강의 관리
- `GET /api/courses` - 강의 목록
- `POST /api/courses/add` - 강의 추가 및 재배정
- `DELETE /api/courses/{id}` - 강의 삭제 및 재배정

### 버전 관리
- `GET /api/versions` - 버전 이력 목록
- `GET /api/versions/{id}/schedule` - 버전별 시간표
- `POST /api/versions/{id}/restore` - 버전 복원

## 사용 시나리오

### 시나리오 1: 초기 시간표 생성
1. CSV 파일 업로드
2. 시간표 자동 배정 실행
3. 결과 확인 및 검증

### 시나리오 2: 강의 추가
1. "강의 관리" 탭에서 강의 정보 입력
2. "추가 및 재배정" 클릭
3. 이전 버전 자동 저장
4. 새 시간표 생성 및 표시

### 시나리오 3: 강의 삭제
1. "강의 관리" 탭에서 강의 선택
2. "삭제 및 재배정" 클릭
3. 이전 버전 자동 저장
4. 새 시간표 생성 및 표시

### 시나리오 4: 이전 버전으로 롤백
1. "버전 관리" 탭에서 버전 목록 확인
2. 복원할 버전 선택
3. "버전 복원" 클릭
4. 해당 버전으로 시간표 복원

