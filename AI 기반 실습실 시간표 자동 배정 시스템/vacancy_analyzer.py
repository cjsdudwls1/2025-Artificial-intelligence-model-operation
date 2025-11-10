"""
공실 분석 로직
"""
from typing import List, Dict
from models import Schedule, VacancySlot, RoomVacancy
from scheduler import DAYS, TIME_SLOTS, time_to_minutes, minutes_to_time, get_3hour_end_time, is_time_overlap


class VacancyAnalyzer:
    """공실 분석기"""
    
    def __init__(self, schedules: List[Schedule]):
        self.schedules = schedules
        self.rooms = ["1215", "1216", "1217", "1418", "RENTAL_1"]
    
    def analyze(self) -> Dict:
        """공실 분석 실행"""
        vacancies = []
        room_utilization = {}
        
        for room in self.rooms:
            room_utilization[room] = {"total_slots": 0, "used_slots": 0}
            
            for day in DAYS:
                # 해당 방, 해당 요일의 배정된 시간표만 필터링
                day_schedules = [
                    s for s in self.schedules 
                    if s.room == room and s.day == day
                ]
                
                # 전체 가능한 시간대에서 공실 찾기
                free_slots = self._find_free_slots(day, room, day_schedules)
                
                if free_slots:
                    vacancies.append({
                        "room": room,
                        "day": day,
                        "freeSlots": free_slots
                    })
                
                # 활용률 계산
                total_minutes = 0
                used_minutes = 0
                
                for start_time in TIME_SLOTS:
                    end_time = get_3hour_end_time(start_time)
                    if time_to_minutes(end_time) > time_to_minutes("18:00"):
                        continue
                    
                    total_minutes += 180  # 3시간 = 180분
                    
                    # 해당 시간대에 배정된 수업이 있는지 확인
                    for schedule in day_schedules:
                        if is_time_overlap(
                            start_time, end_time,
                            schedule.start_time, schedule.end_time
                        ):
                            # 겹치는 부분만 계산
                            overlap_minutes = self._calculate_overlap_minutes(
                                start_time, end_time,
                                schedule.start_time, schedule.end_time
                            )
                            used_minutes += overlap_minutes
                            break
                
                room_utilization[room]["total_slots"] += total_minutes
                room_utilization[room]["used_slots"] += used_minutes
        
        # 활용률 계산
        utilization_by_room = {}
        total_all = 0
        used_all = 0
        
        for room in self.rooms:
            total = room_utilization[room]["total_slots"]
            used = room_utilization[room]["used_slots"]
            total_all += total
            used_all += used
            
            if total > 0:
                utilization_by_room[room] = round(used / total, 2)
            else:
                utilization_by_room[room] = 0.0
        
        overall_utilization = round(used_all / total_all, 2) if total_all > 0 else 0.0
        
        return {
            "vacancies": vacancies,
            "summary": {
                "utilizationRateByRoom": utilization_by_room,
                "overallUtilizationRate": overall_utilization
            }
        }
    
    def _find_free_slots(self, day: str, room: str, schedules: List[Schedule]) -> List[Dict]:
        """공실 슬롯 찾기"""
        # 모든 가능한 3시간 블록 생성
        all_slots = []
        for start_time in TIME_SLOTS:
            end_time = get_3hour_end_time(start_time)
            if time_to_minutes(end_time) <= time_to_minutes("18:00"):
                all_slots.append((start_time, end_time))
        
        # 배정된 시간표와 겹치지 않는 슬롯 찾기
        free_slots = []
        
        for start_time, end_time in all_slots:
            is_free = True
            for schedule in schedules:
                if is_time_overlap(
                    start_time, end_time,
                    schedule.start_time, schedule.end_time
                ):
                    is_free = False
                    break
            
            if is_free:
                free_slots.append({
                    "startTime": start_time,
                    "endTime": end_time
                })
        
        # 연속된 공실 슬롯 병합
        merged_slots = self._merge_continuous_slots(free_slots)
        
        return merged_slots
    
    def _merge_continuous_slots(self, slots: List[Dict]) -> List[Dict]:
        """연속된 공실 슬롯 병합"""
        if not slots:
            return []
        
        # 시간순 정렬
        sorted_slots = sorted(slots, key=lambda x: time_to_minutes(x["startTime"]))
        
        merged = []
        current_start = sorted_slots[0]["startTime"]
        current_end = sorted_slots[0]["endTime"]
        
        for slot in sorted_slots[1:]:
            slot_start = time_to_minutes(slot["startTime"])
            current_end_minutes = time_to_minutes(current_end)
            
            # 연속된 경우 (1시간 블록이므로 바로 다음 블록인지 확인)
            if slot_start == current_end_minutes:
                current_end = slot["endTime"]
            else:
                merged.append({
                    "startTime": current_start,
                    "endTime": current_end
                })
                current_start = slot["startTime"]
                current_end = slot["endTime"]
        
        merged.append({
            "startTime": current_start,
            "endTime": current_end
        })
        
        return merged
    
    def _calculate_overlap_minutes(self, start1: str, end1: str, start2: str, end2: str) -> int:
        """두 시간 구간의 겹치는 분 계산"""
        s1 = time_to_minutes(start1)
        e1 = time_to_minutes(end1)
        s2 = time_to_minutes(start2)
        e2 = time_to_minutes(end2)
        
        overlap_start = max(s1, s2)
        overlap_end = min(e1, e2)
        
        return max(0, overlap_end - overlap_start)

