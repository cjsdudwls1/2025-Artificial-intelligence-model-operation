"""
FastAPI 백엔드 구현
"""
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Body
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import pandas as pd
import csv
import io
from typing import List, Optional
from models import (
    Course, Schedule, TimetableVersion, ScheduleHistory, init_db, get_db,
    TimetableResponse, VacancyResponse, CourseResponse,
    VersionResponse, VersionInfo, CourseAddRequest, CourseListResponse, CourseInfo
)
from scheduler import TimetableScheduler
from vacancy_analyzer import VacancyAnalyzer

app = FastAPI(title="실습실 시간표 자동 배정 시스템", version="1.0.0")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 데이터베이스 초기화 (앱 시작 시)
init_db()

# 상수 정의
ROOMS = ["1215", "1216", "1217", "1418", "RENTAL_1"]
DAYS = ["월", "화", "수", "목", "금"]
HOURS = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]


def get_timetable_metadata(version: Optional[int] = None, restored_from: Optional[int] = None) -> dict:
    """시간표 메타데이터 생성"""
    metadata = {
        "rooms": ROOMS,
        "days": DAYS,
        "hours": HOURS
    }
    if version is not None:
        metadata["version"] = version
    if restored_from is not None:
        metadata["restoredFrom"] = restored_from
    return metadata


def schedule_to_dict(schedule) -> dict:
    """Schedule 객체를 딕셔너리로 변환"""
    return {
        "courseCode": schedule.course_code,
        "courseName": schedule.course_name,
        "instructor": schedule.instructor,
        "department": schedule.department,
        "isLab": schedule.is_lab,
        "enrollment": schedule.enrollment,
        "weeks": schedule.weeks,
        "credits": schedule.credits,
        "day": schedule.day,
        "startTime": schedule.start_time,
        "endTime": schedule.end_time,
        "room": schedule.room
    }


def create_schedule_from_assignment(assignment) -> Schedule:
    """CourseAssignment로부터 Schedule 객체 생성"""
    return Schedule(
        course_id=assignment.course.id,
        course_code=assignment.course.course_code,
        course_name=assignment.course.course_name,
        instructor=assignment.course.instructor,
        department=assignment.course.department,
        day=assignment.day,
        start_time=assignment.start_time,
        end_time=assignment.end_time,
        room=assignment.room,
        is_lab=assignment.course.is_lab,
        enrollment=assignment.course.enrollment,
        weeks=assignment.course.weeks,
        credits=assignment.course.credits
    )


def create_schedule_from_history(history: ScheduleHistory) -> Schedule:
    """ScheduleHistory로부터 Schedule 객체 생성"""
    return Schedule(
        course_id=history.course_id,
        course_code=history.course_code,
        course_name=history.course_name,
        instructor=history.instructor,
        department=history.department,
        day=history.day,
        start_time=history.start_time,
        end_time=history.end_time,
        room=history.room,
        is_lab=history.is_lab,
        enrollment=history.enrollment,
        weeks=history.weeks,
        credits=history.credits
    )


def save_schedules_to_db(db: Session, assignments: List) -> None:
    """할당 목록을 Schedule 테이블에 저장"""
    db.query(Schedule).delete()
    for assignment in assignments:
        schedule = create_schedule_from_assignment(assignment)
        db.add(schedule)
    db.commit()


def reschedule_all(db: Session, description: str = "") -> Tuple[List, int]:
    """전체 시간표 재배정"""
    # 버전 이력 저장
    version_number = get_next_version_number(db)
    save_version_history(db, version_number, description)
    
    # 활성 강의 조회 및 재배정
    active_courses = db.query(Course).filter(Course.is_deleted == False).all()
    scheduler = TimetableScheduler(active_courses)
    assignments = scheduler.schedule()
    
    # Schedule 저장
    save_schedules_to_db(db, assignments)
    
    return assignments, version_number


def load_courses_from_csv(csv_content: str) -> List[Course]:
    """CSV 내용을 Course 객체 리스트로 변환"""
    df = pd.read_csv(io.StringIO(csv_content))
    courses = []
    
    for _, row in df.iterrows():
        course = Course(
            process=row.get("과정", ""),
            department=row.get("개설학과", ""),
            course_code=row.get("교과목코드", ""),
            course_name=row.get("교과목명", ""),
            grade=int(row.get("개설학년", 0)) if pd.notna(row.get("개설학년")) else 0,
            area=row.get("영역구분", ""),
            enrollment=int(row.get("수강인원", 0)) if pd.notna(row.get("수강인원")) else 0,
            main_instructor=row.get("강좌대표교수", ""),
            instructor=row.get("강좌담당교수", ""),
            weeks=int(row.get("수업주수", 0)) if pd.notna(row.get("수업주수")) else 0,
            credits=int(row.get("교과목학점", 0)) if pd.notna(row.get("교과목학점")) else 0,
            is_lab=row.get("강의유형구분", "") == "실습"
        )
        courses.append(course)
    
    return courses


def get_next_version_number(db: Session) -> int:
    """다음 버전 번호 가져오기"""
    latest_version = db.query(TimetableVersion).order_by(TimetableVersion.version_number.desc()).first()
    if latest_version:
        return latest_version.version_number + 1
    return 1


def save_version_history(db: Session, version_number: int, description: str = "") -> int:
    """현재 시간표를 버전 이력으로 저장"""
    # 이전 활성 버전 비활성화
    db.query(TimetableVersion).filter(TimetableVersion.is_active == True).update({"is_active": False})
    db.commit()
    
    # 새 버전 생성
    new_version = TimetableVersion(
        version_number=version_number,
        description=description,
        is_active=True
    )
    db.add(new_version)
    db.flush()
    
    # 현재 Schedule을 ScheduleHistory에 복사
    current_schedules = db.query(Schedule).all()
    for schedule in current_schedules:
        history = ScheduleHistory(
            version_id=new_version.id,
            course_id=schedule.course_id,
            course_code=schedule.course_code,
            course_name=schedule.course_name,
            instructor=schedule.instructor,
            department=schedule.department,
            day=schedule.day,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            room=schedule.room,
            is_lab=schedule.is_lab,
            enrollment=schedule.enrollment,
            weeks=schedule.weeks,
            credits=schedule.credits
        )
        db.add(history)
    
    db.commit()
    return new_version.id


@app.post("/api/schedule/build", response_model=TimetableResponse)
async def build_schedule(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    CSV 파일을 업로드하고 시간표 자동 배정 실행
    """
    try:
        # CSV 파일 읽기
        contents = await file.read()
        csv_content = contents.decode("utf-8-sig")  # BOM 제거
        
        # Course 객체 리스트 생성
        courses = load_courses_from_csv(csv_content)
        
        # 기존 데이터 삭제
        db.query(Course).delete()
        db.query(Schedule).delete()
        db.commit()
        
        # 데이터베이스에 저장
        for course in courses:
            db.add(course)
        db.commit()
        
        # 데이터베이스에서 다시 조회하여 ID를 포함한 Course 객체 사용
        db_courses = db.query(Course).all()
        
        # 시간표 자동 배정
        scheduler = TimetableScheduler(db_courses)
        assignments = scheduler.schedule()
        
        # Schedule 테이블에 저장
        save_schedules_to_db(db, assignments)
        
        # 응답 생성
        timetable_list = [assignment.to_dict() for assignment in assignments]
        return TimetableResponse(
            timetable=timetable_list,
            metadata=get_timetable_metadata()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시간표 배정 실패: {str(e)}")


@app.get("/api/schedule", response_model=TimetableResponse)
async def get_schedule(db: Session = Depends(get_db)):
    """
    최신 배정된 시간표 조회
    """
    schedules = db.query(Schedule).all()
    timetable_list = [schedule_to_dict(schedule) for schedule in schedules]
    return TimetableResponse(
        timetable=timetable_list,
        metadata=get_timetable_metadata()
    )


@app.get("/api/vacancy", response_model=VacancyResponse)
async def get_vacancy(db: Session = Depends(get_db)):
    """
    공실 분석 결과 조회
    """
    schedules = db.query(Schedule).all()
    
    if not schedules:
        return VacancyResponse(
            vacancies=[],
            summary={
                "utilizationRateByRoom": {},
                "overallUtilizationRate": 0.0
            }
        )
    
    # 공실 분석 실행
    analyzer = VacancyAnalyzer(schedules)
    result = analyzer.analyze()
    
    return VacancyResponse(**result)


@app.post("/api/schedule/what-if")
async def what_if_simulation(
    unavailable_times: Optional[List[dict]] = None,
    db: Session = Depends(get_db)
):
    """
    시뮬레이션 실행 (특강, 휴강, 대여 불가 시간 등 반영)
    """
    # TODO: 시뮬레이션 로직 구현
    # 현재는 기본 시간표 반환
    schedules = db.query(Schedule).all()
    
    if not schedules:
        raise HTTPException(status_code=404, detail="배정된 시간표가 없습니다.")
    
    # 시뮬레이션 결과 반환
    return {
        "message": "시뮬레이션 기능은 향후 구현 예정입니다.",
        "current_schedule_count": len(schedules)
    }


# 강의 관리 API
@app.post("/api/courses/add")
async def add_course(
    course_data: CourseAddRequest,
    db: Session = Depends(get_db)
):
    """개별 강의 추가 및 재배정"""
    try:
        # 새 강의 추가
        new_course = Course(
            process=course_data.process,
            department=course_data.department,
            course_code=course_data.course_code,
            course_name=course_data.course_name,
            grade=0,
            area=course_data.area,
            enrollment=course_data.enrollment,
            main_instructor=course_data.main_instructor,
            instructor=course_data.instructor,
            weeks=course_data.weeks,
            credits=course_data.credits,
            is_lab=course_data.is_lab
        )
        db.add(new_course)
        db.commit()
        
        # 전체 재배정
        assignments, version_number = reschedule_all(
            db, f"강의 추가: {course_data.course_name}"
        )
        
        # 응답 생성
        timetable_list = [assignment.to_dict() for assignment in assignments]
        return TimetableResponse(
            timetable=timetable_list,
            metadata=get_timetable_metadata(version=version_number)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"강의 추가 실패: {str(e)}")


@app.delete("/api/courses/{course_id}")
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """강의 삭제 및 재배정"""
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="강의를 찾을 수 없습니다.")
        
        # 논리적 삭제
        course.is_deleted = True
        db.commit()
        
        # 전체 재배정
        assignments, version_number = reschedule_all(
            db, f"강의 삭제: {course.course_name}"
        )
        
        # 응답 생성
        timetable_list = [assignment.to_dict() for assignment in assignments]
        return TimetableResponse(
            timetable=timetable_list,
            metadata=get_timetable_metadata(version=version_number)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"강의 삭제 실패: {str(e)}")


@app.get("/api/courses", response_model=CourseListResponse)
async def list_courses(db: Session = Depends(get_db)):
    """강의 목록 조회 (삭제되지 않은 것만)"""
    courses = db.query(Course).filter(Course.is_deleted == False).order_by(Course.id).all()
    
    course_list = []
    for course in courses:
        course_list.append(CourseInfo(
            id=course.id,
            process=course.process,
            department=course.department,
            courseCode=course.course_code,
            courseName=course.course_name,
            grade=course.grade,
            area=course.area,
            enrollment=course.enrollment,
            mainInstructor=course.main_instructor,
            instructor=course.instructor,
            weeks=course.weeks,
            credits=course.credits,
            isLab=course.is_lab,
            createdAt=course.created_at.isoformat() if course.created_at else "",
            updatedAt=course.updated_at.isoformat() if course.updated_at else ""
        ))
    
    return CourseListResponse(courses=course_list)


# 버전 관리 API
@app.get("/api/versions", response_model=VersionResponse)
async def list_versions(db: Session = Depends(get_db)):
    """버전 목록 조회"""
    versions = db.query(TimetableVersion).order_by(TimetableVersion.version_number.desc()).all()
    
    version_list = []
    for version in versions:
        # 각 버전의 과목 수 계산
        course_count = db.query(ScheduleHistory).filter(
            ScheduleHistory.version_id == version.id
        ).count()
        
        version_list.append(VersionInfo(
            id=version.id,
            versionNumber=version.version_number,
            createdAt=version.created_at.isoformat() if version.created_at else "",
            description=version.description or "",
            isActive=version.is_active,
            courseCount=course_count
        ))
    
    return VersionResponse(versions=version_list)


@app.get("/api/versions/{version_id}/schedule", response_model=TimetableResponse)
async def get_version_schedule(version_id: int, db: Session = Depends(get_db)):
    """특정 버전의 시간표 조회"""
    history_schedules = db.query(ScheduleHistory).filter(
        ScheduleHistory.version_id == version_id
    ).all()
    
    timetable_list = [schedule_to_dict(schedule) for schedule in history_schedules]
    return TimetableResponse(
        timetable=timetable_list,
        metadata=get_timetable_metadata()
    )


@app.post("/api/versions/{version_id}/restore", response_model=TimetableResponse)
async def restore_version(version_id: int, db: Session = Depends(get_db)):
    """특정 버전으로 시간표 복원"""
    try:
        version = db.query(TimetableVersion).filter(TimetableVersion.id == version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="버전을 찾을 수 없습니다.")
        
        history_schedules = db.query(ScheduleHistory).filter(
            ScheduleHistory.version_id == version_id
        ).all()
        
        if not history_schedules:
            raise HTTPException(status_code=404, detail="해당 버전의 시간표 데이터가 없습니다.")
        
        # 버전 이력 저장 (현재 버전)
        version_number = get_next_version_number(db)
        save_version_history(db, version_number, f"버전 복원: {version.version_number}번 버전")
        
        # 기존 Schedule 삭제 및 버전 데이터로 복원
        db.query(Schedule).delete()
        for history in history_schedules:
            schedule = create_schedule_from_history(history)
            db.add(schedule)
        db.commit()
        
        # 응답 생성
        timetable_list = [schedule_to_dict(history) for history in history_schedules]
        return TimetableResponse(
            timetable=timetable_list,
            metadata=get_timetable_metadata(
                version=version_number,
                restored_from=version.version_number
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버전 복원 실패: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 엔드포인트 - 메인 페이지"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

