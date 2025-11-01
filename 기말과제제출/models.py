"""
데이터베이스 모델 및 데이터 클래스 정의
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from datetime import time, datetime
from pydantic import BaseModel

Base = declarative_base()

class Course(Base):
    """교과목 테이블"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    process = Column(String)  # 과정
    department = Column(String)  # 개설학과
    course_code = Column(String)  # 교과목코드
    course_name = Column(String)  # 교과목명
    grade = Column(Integer)  # 개설학년
    area = Column(String)  # 영역구분
    enrollment = Column(Integer)  # 수강인원
    main_instructor = Column(String)  # 강좌대표교수
    instructor = Column(String)  # 강좌담당교수
    weeks = Column(Integer)  # 수업주수
    credits = Column(Integer)  # 교과목학점
    is_lab = Column(Boolean)  # 강의유형구분 (실습 여부)
    is_deleted = Column(Boolean, default=False)  # 논리적 삭제 여부
    created_at = Column(DateTime, default=datetime.utcnow)  # 생성 시간
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 수정 시간


class TimetableVersion(Base):
    """시간표 버전 테이블"""
    __tablename__ = "timetable_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_number = Column(Integer, unique=True, index=True)  # 버전 번호
    created_at = Column(DateTime, default=datetime.utcnow)  # 생성 시간
    description = Column(String)  # 버전 설명
    is_active = Column(Boolean, default=False)  # 현재 활성 버전 여부


class Schedule(Base):
    """시간표 테이블 (현재 버전)"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer)  # courses 테이블 참조
    course_code = Column(String)
    course_name = Column(String)
    instructor = Column(String)
    department = Column(String)
    day = Column(String)  # 요일 (월, 화, 수, 목, 금)
    start_time = Column(String)  # 시작 시간 (HH:MM)
    end_time = Column(String)  # 종료 시간 (HH:MM)
    room = Column(String)  # 강의실 번호
    is_lab = Column(Boolean)
    enrollment = Column(Integer)
    weeks = Column(Integer)
    credits = Column(Integer)


class ScheduleHistory(Base):
    """시간표 이력 테이블"""
    __tablename__ = "schedule_history"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("timetable_versions.id"), index=True)  # 버전 참조
    course_id = Column(Integer)  # courses 테이블 참조
    course_code = Column(String)
    course_name = Column(String)
    instructor = Column(String)
    department = Column(String)
    day = Column(String)  # 요일 (월, 화, 수, 목, 금)
    start_time = Column(String)  # 시작 시간 (HH:MM)
    end_time = Column(String)  # 종료 시간 (HH:MM)
    room = Column(String)  # 강의실 번호
    is_lab = Column(Boolean)
    enrollment = Column(Integer)
    weeks = Column(Integer)
    credits = Column(Integer)


# SQLite 데이터베이스 초기화
DATABASE_URL = "sqlite:///./timetable.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic 모델 (API 요청/응답)
class CourseResponse(BaseModel):
    """교과목 응답 모델"""
    courseCode: str
    courseName: str
    instructor: str
    department: str
    isLab: bool
    enrollment: int
    weeks: int
    credits: int
    day: str
    startTime: str
    endTime: str
    room: str
    
    class Config:
        from_attributes = True


class TimetableResponse(BaseModel):
    """시간표 응답 모델"""
    timetable: List[CourseResponse]
    metadata: dict


class VacancySlot(BaseModel):
    """공실 슬롯"""
    startTime: str
    endTime: str


class RoomVacancy(BaseModel):
    """강의실별 공실"""
    room: str
    day: str
    freeSlots: List[VacancySlot]


class VacancyResponse(BaseModel):
    """공실 분석 응답 모델"""
    vacancies: List[RoomVacancy]
    summary: dict


class VersionInfo(BaseModel):
    """버전 정보 응답 모델"""
    id: int
    versionNumber: int
    createdAt: str
    description: str
    isActive: bool
    courseCount: int


class VersionResponse(BaseModel):
    """버전 목록 응답 모델"""
    versions: List[VersionInfo]


class CourseAddRequest(BaseModel):
    """강의 추가 요청 모델"""
    process: str
    department: str
    course_code: str
    course_name: str
    grade: int
    area: str
    enrollment: int
    main_instructor: str
    instructor: str
    weeks: int
    credits: int
    is_lab: bool


class CourseInfo(BaseModel):
    """강의 정보 응답 모델"""
    id: int
    process: str
    department: str
    courseCode: str
    courseName: str
    grade: int
    area: str
    enrollment: int
    mainInstructor: str
    instructor: str
    weeks: int
    credits: int
    isLab: bool
    createdAt: str
    updatedAt: str


class CourseListResponse(BaseModel):
    """강의 목록 응답 모델"""
    courses: List[CourseInfo]

