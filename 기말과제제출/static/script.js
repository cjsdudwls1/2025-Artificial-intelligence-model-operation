const API_BASE_URL = 'http://127.0.0.1:8000';

// 탭 전환
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // 모든 탭 비활성화
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 선택한 탭 활성화
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});

// 시간표 배정
async function buildSchedule() {
    const fileInput = document.getElementById('csv-file');
    const resultBox = document.getElementById('build-result');
    const calendarBox = document.getElementById('build-timetable-calendar');
    
    if (!fileInput.files[0]) {
        resultBox.className = 'result-box error';
        resultBox.textContent = '❌ CSV 파일을 선택해주세요.';
        return;
    }
    
    resultBox.className = 'result-box';
    resultBox.innerHTML = '<span class="loading"></span> 처리 중...';
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/schedule/build`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            resultBox.className = 'result-box success';
            resultBox.textContent = `✅ ${data.timetable.length}개 과목 배정 완료!`;
            displayCalendar(data.timetable, calendarBox);
        } else {
            const error = await response.json();
            resultBox.className = 'result-box error';
            resultBox.textContent = `❌ 오류: ${error.detail || '알 수 없는 오류'}`;
        }
    } catch (error) {
        resultBox.className = 'result-box error';
        resultBox.textContent = '❌ 서버에 연결할 수 없습니다.';
    }
}

// 시간표 조회
async function viewSchedule() {
    const roomSelect = document.getElementById('room-select').value;
    const summaryBox = document.getElementById('view-summary');
    const calendarBox = document.getElementById('view-timetable-calendar');
    
    summaryBox.innerHTML = '<span class="loading"></span> 로딩 중...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/schedule`);
        
        if (response.ok) {
            const data = await response.json();
            let timetable = data.timetable;
            
            // 강의실 필터링
            if (roomSelect !== '전체') {
                timetable = timetable.filter(t => t.room === roomSelect);
                summaryBox.textContent = `${roomSelect} 강의실: ${timetable.length}개 과목이 배정되었습니다.`;
            } else {
                summaryBox.textContent = `전체: 총 ${timetable.length}개 과목이 배정되었습니다.`;
            }
            
            displayCalendar(timetable, calendarBox);
        } else {
            summaryBox.className = 'result-box error';
            summaryBox.textContent = '❌ 시간표를 불러올 수 없습니다.';
        }
    } catch (error) {
        summaryBox.className = 'result-box error';
        summaryBox.textContent = '❌ 서버에 연결할 수 없습니다.';
    }
}

// 공실 분석
async function analyzeVacancy() {
    const resultBox = document.getElementById('vacancy-result');
    
    resultBox.innerHTML = '<span class="loading"></span> 분석 중...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/vacancy`);
        
        if (response.ok) {
            const data = await response.json();
            let html = '<h3>공실 분석 결과</h3>';
            html += `<p><strong>전체 활용률: ${(data.summary.overallUtilizationRate * 100).toFixed(1)}%</strong></p>`;
            html += '<h4>강의실별 활용률</h4><ul>';
            for (const [room, rate] of Object.entries(data.summary.utilizationRateByRoom)) {
                html += `<li>${room}: ${(rate * 100).toFixed(1)}%</li>`;
            }
            html += '</ul>';
            resultBox.innerHTML = html;
        } else {
            resultBox.className = 'result-box error';
            resultBox.textContent = '❌ 분석 실패';
        }
    } catch (error) {
        resultBox.className = 'result-box error';
        resultBox.textContent = '❌ 서버에 연결할 수 없습니다.';
    }
}

// 강의 추가
async function addCourse() {
    const resultBox = document.getElementById('add-result');
    const payload = {
        process: document.getElementById('process').value,
        department: document.getElementById('department').value,
        course_code: document.getElementById('course-code').value,
        course_name: document.getElementById('course-name').value,
        grade: 0,
        area: document.getElementById('area').value,
        enrollment: parseInt(document.getElementById('enrollment').value),
        main_instructor: document.getElementById('main-instructor').value,
        instructor: document.getElementById('instructor').value,
        weeks: parseInt(document.getElementById('weeks').value),
        credits: parseInt(document.getElementById('credits').value),
        is_lab: document.getElementById('is-lab').checked
    };
    
    resultBox.innerHTML = '<span class="loading"></span> 처리 중...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/courses/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const data = await response.json();
            resultBox.className = 'result-box success';
            resultBox.textContent = `✅ 강의 추가 완료! 총 ${data.timetable.length}개 과목 배정됨`;
            listCourses(); // 목록 새로고침
        } else {
            const error = await response.json();
            resultBox.className = 'result-box error';
            resultBox.textContent = `❌ 오류: ${error.detail || '알 수 없는 오류'}`;
        }
    } catch (error) {
        resultBox.className = 'result-box error';
        resultBox.textContent = '❌ 서버에 연결할 수 없습니다.';
    }
}

// 강의 목록 조회
async function listCourses() {
    const tableBox = document.getElementById('course-list-table');
    const checkboxBox = document.getElementById('delete-checkboxes');
    
    tableBox.innerHTML = '<p>로딩 중...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/courses`);
        
        if (response.ok) {
            const data = await response.json();
            const courses = data.courses;
            
            // 테이블 생성
            let tableHtml = '<table><thead><tr><th>ID</th><th>과목코드</th><th>과목명</th><th>교수</th><th>학과</th><th>학점</th><th>수강인원</th></tr></thead><tbody>';
            courses.forEach(course => {
                tableHtml += `<tr><td>${course.id}</td><td>${course.courseCode}</td><td>${course.courseName}</td><td>${course.instructor}</td><td>${course.department}</td><td>${course.credits}</td><td>${course.enrollment}</td></tr>`;
            });
            tableHtml += '</tbody></table>';
            tableBox.innerHTML = tableHtml;
            
            // 체크박스 생성
            let checkboxes = '<div class="checkbox-list">';
            courses.forEach(course => {
                checkboxes += `<div class="checkbox-item"><input type="checkbox" id="course-${course.id}" value="${course.id}"><label for="course-${course.id}">${course.courseCode} - ${course.courseName} (${course.instructor})</label></div>`;
            });
            checkboxes += '</div>';
            checkboxBox.innerHTML = checkboxes;
        } else {
            tableBox.innerHTML = '<p class="error">목록을 불러올 수 없습니다.</p>';
        }
    } catch (error) {
        tableBox.innerHTML = '<p class="error">서버에 연결할 수 없습니다.</p>';
    }
}

// 강의 삭제
async function deleteCourses() {
    const resultBox = document.getElementById('delete-result');
    const checkboxes = document.querySelectorAll('#delete-checkboxes input[type="checkbox"]:checked');
    
    const selectedIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (selectedIds.length === 0) {
        resultBox.className = 'result-box error';
        resultBox.textContent = '❌ 삭제할 강의를 선택해주세요.';
        return;
    }
    
    resultBox.innerHTML = '<span class="loading"></span> 처리 중...';
    
    const results = [];
    for (const id of selectedIds) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/courses/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                const data = await response.json();
                results.push(`강의 ID ${id}: ✅ 삭제 완료 (총 ${data.timetable.length}개 과목 배정됨)`);
            } else {
                const error = await response.json();
                results.push(`강의 ID ${id}: ❌ ${error.detail || '삭제 실패'}`);
            }
        } catch (error) {
            results.push(`강의 ID ${id}: ❌ 서버 연결 실패`);
        }
    }
    
    resultBox.className = results.every(r => r.includes('✅')) ? 'result-box success' : 'result-box';
    resultBox.innerHTML = results.join('<br>');
    
    listCourses(); // 목록 새로고침
}

// 캘린더 표시 (Python timetable_visualizer 로직을 JS로 변환)
function displayCalendar(timetable, container) {
    if (!timetable || timetable.length === 0) {
        container.innerHTML = '<p>시간표가 없습니다.</p>';
        return;
    }
    
    const days = ['월', '화', '수', '목', '금'];
    const timeSlots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'];
    
    // 강의실별 색상
    const rooms = [...new Set(timetable.map(t => t.room))].sort();
    const colors = ['#FFB6C1', '#87CEEB', '#98FB98', '#FFD700', '#FFA500', '#DDA0DD'];
    const roomColors = {};
    rooms.forEach((room, i) => {
        roomColors[room] = rooms.length === 1 ? '#87CEEB' : colors[i % colors.length];
    });
    
    // 시간을 분으로 변환
    const timeToMinutes = (timeStr) => {
        const [h, m] = timeStr.split(':').map(Number);
        return h * 60 + m;
    };
    
    let html = '<table class="timetable-container">';
    
    // 헤더
    html += '<tr><td class="time-cell"></td>';
    days.forEach(day => {
        html += `<td class="timetable-header">${day}</td>`;
    });
    html += '</tr>';
    
    // 시간대별 행
    timeSlots.forEach((timeSlot, idx) => {
        html += '<tr>';
        html += `<td class="time-cell">${timeSlot.split(':')[0]}시</td>`;
        
        days.forEach(day => {
            html += '<td class="timetable-cell" style="position: relative;">';
            
            const timeMin = timeToMinutes(timeSlot);
            const nextTimeMin = timeMin + 60;
            
            const dayClasses = timetable.filter(t => t.day === day);
            const displayedClasses = [];
            
            dayClasses.forEach(cls => {
                const startMin = timeToMinutes(cls.startTime);
                const endMin = timeToMinutes(cls.endTime);
                
                if (startMin < nextTimeMin && endMin > timeMin) {
                    const startRow = timeSlots.indexOf(cls.startTime);
                    if (startRow === idx) {
                        displayedClasses.push({cls, startMin, endMin});
                    }
                }
            });
            
            displayedClasses.forEach(({cls}, classIdx) => {
                const durationHours = (timeToMinutes(cls.endTime) - timeToMinutes(cls.startTime)) / 60;
                const blockHeight = durationHours * 60 - 4;
                const bgColor = roomColors[cls.room];
                const leftOffset = classIdx * 3;
                
                let courseName = cls.courseName;
                if (courseName.length > 18) {
                    courseName = courseName.substring(0, 18) + '...';
                }
                
                html += `<div class="course-block" style="background-color: ${bgColor}; top: 2px; left: ${2 + leftOffset}px; right: ${2 + leftOffset}px; height: ${blockHeight}px; z-index: ${100 + classIdx};">
                    <div class="course-name">${courseName}</div>
                    <div class="course-room">${cls.room}<br>${cls.instructor}</div>
                </div>`;
            });
            
            html += '</td>';
        });
        html += '</tr>';
    });
    
    html += '</table>';
    
    // 범례
    html += '<div style="margin-top: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;"><strong>강의실별 색상:</strong><br>';
    Object.entries(roomColors).forEach(([room, color]) => {
        html += `<span style="display: inline-block; width: 20px; height: 20px; background-color: ${color}; margin: 5px; border: 1px solid #ddd; vertical-align: middle;"></span>`;
        html += `<span style="margin-right: 15px;">${room}</span>`;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

