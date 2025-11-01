"""
시간표 자동 배정 알고리즘 (유전 알고리즘 기반)
"""
from typing import List, Dict, Tuple, Optional
import random
from models import Course

# 시간 블록 상수
BLOCK_DURATION_MINUTES = 180  # 3시간 = 180분
DAILY_WORKING_HOURS = 9  # 09:00~18:00 = 9시간
DAILY_WORKING_MINUTES = 540  # 9시간 * 60분 = 540분
END_TIME_LIMIT = "18:00"
DEFAULT_ROOM_PREFERENCE = 0.8  # 기본 강의실 선호 확률
CROSSOVER_PREFERENCE_PROB = 0.7  # 교차 연산에서 우선 부모 선택 확률
TIME_SLOT_OVERUSE_THRESHOLD = 1.5  # 시간대 과다 사용 임계값 (평균의 배수)

# 시간대 정의 (3시간 블록 가능한 시작 시간)
TIME_SLOTS = [
    "09:00", "10:00", "11:00", "12:00", 
    "13:00", "14:00", "15:00"
]

# 요일 정의
DAYS = ["월", "화", "수", "목", "금"]

# 강의실 정의
ROOMS = ["1215", "1216", "1217", "1418"]
RENTAL_ROOM = "RENTAL_1"
ALL_ROOMS = ROOMS + [RENTAL_ROOM]

# 유전 알고리즘 파라미터
POPULATION_SIZE = 50
MAX_GENERATIONS = 100
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.1
ELITE_SIZE = 5
TOURNAMENT_SIZE = 3

# 적합도 함수 가중치
PENALTY_CONFLICT = -10000
PENALTY_UNASSIGNED = -5000
WEIGHT_VACANCY = -30
WEIGHT_RENTAL = -50
BONUS_EVEN_DISTRIBUTION = 5
BONUS_TIME_SLOT_DIVERSITY = 100
PENALTY_TIME_SLOT_OVERUSE = -30
PENALTY_ROOM_DAY_VACANCY_CONCENTRATION = -50
BONUS_3HOUR_VACANCY_BLOCK = 20
BONUS_ROOM_DAY_UTILIZATION = 15


# 유틸리티 함수
def time_to_minutes(time_str: str) -> int:
    """시간 문자열을 분으로 변환"""
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def minutes_to_time(minutes: int) -> str:
    """분을 시간 문자열로 변환"""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def get_3hour_end_time(start_time: str) -> str:
    """3시간 연속 블록의 종료 시간 계산"""
    start_minutes = time_to_minutes(start_time)
    end_minutes = start_minutes + BLOCK_DURATION_MINUTES
    return minutes_to_time(end_minutes)


def is_time_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """두 시간 구간이 겹치는지 확인"""
    s1 = time_to_minutes(start1)
    e1 = time_to_minutes(end1)
    s2 = time_to_minutes(start2)
    e2 = time_to_minutes(end2)
    return not (e1 <= s2 or e2 <= s1)


def is_valid_time_slot(start_time: str) -> bool:
    """시간 슬롯이 유효한지 확인 (18:00 이전 종료)"""
    end_time = get_3hour_end_time(start_time)
    return time_to_minutes(end_time) <= time_to_minutes(END_TIME_LIMIT)


class CourseAssignment:
    """교과목 배정 정보"""
    
    def __init__(self, course: Course, day: str, start_time: str, end_time: str, room: str):
        self.course = course
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "courseCode": self.course.course_code,
            "courseName": self.course.course_name,
            "instructor": self.course.instructor,
            "department": self.course.department,
            "isLab": self.course.is_lab,
            "enrollment": self.course.enrollment,
            "weeks": self.course.weeks,
            "credits": self.course.credits,
            "day": self.day,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "room": self.room
        }


class Chromosome:
    """유전 알고리즘 개체: 시간표 배정 상태를 나타냄"""
    
    def __init__(self, courses: List[Course]):
        self.courses = courses
        self.assignments: Dict[int, Tuple[str, str, str]] = {}
        self.fitness: float = -float('inf')
    
    def assign(self, course_id: int, day: str, start_time: str, room: str):
        """강의에 시간 배정"""
        self.assignments[course_id] = (day, start_time, room)
    
    def get_assignment(self, course_id: int) -> Optional[Tuple[str, str, str]]:
        """강의의 배정 정보 반환"""
        return self.assignments.get(course_id)
    
    def copy(self) -> 'Chromosome':
        """개체 복사"""
        new_chromosome = Chromosome(self.courses)
        new_chromosome.assignments = self.assignments.copy()
        new_chromosome.fitness = self.fitness
        return new_chromosome
    
    def to_course_assignments(self) -> List[CourseAssignment]:
        """CourseAssignment 리스트로 변환"""
        result = []
        for course in self.courses:
            if course.id in self.assignments:
                day, start_time, room = self.assignments[course.id]
                end_time = get_3hour_end_time(start_time)
                result.append(CourseAssignment(course, day, start_time, end_time, room))
        return result


class TimetableScheduler:
    """시간표 자동 배정 스케줄러 (유전 알고리즘)"""
    
    def __init__(self, courses: List[Course]):
        self.courses = courses
        self.best_chromosome: Optional[Chromosome] = None
    
    def _generate_random_chromosome(self) -> Chromosome:
        """랜덤 개체 생성 (초기 개체군용)"""
        chromosome = Chromosome(self.courses)
        time_slot_usage = {slot: 0 for slot in TIME_SLOTS}
        
        for course in self.courses:
            start_time = self._select_time_slot_by_usage(time_slot_usage)
            if not start_time:
                continue
            
            day = random.choice(DAYS)
            if not is_valid_time_slot(start_time):
                continue
            
            room = self._select_room_by_preference()
            chromosome.assign(course.id, day, start_time, room)
            time_slot_usage[start_time] += 1
        
        return chromosome
    
    def _select_time_slot_by_usage(self, time_slot_usage: Dict[str, int]) -> Optional[str]:
        """사용 빈도를 고려한 시간대 선택"""
        valid_slots = [slot for slot in TIME_SLOTS if is_valid_time_slot(slot)]
        if not valid_slots:
            return None
        
        weights = [1.0 / (time_slot_usage[slot] + 1) for slot in valid_slots]
        return random.choices(valid_slots, weights=weights, k=1)[0]
    
    def _select_room_by_preference(self) -> str:
        """강의실 선택 (기본 강의실 우선)"""
        return random.choice(ROOMS) if random.random() < DEFAULT_ROOM_PREFERENCE else RENTAL_ROOM
    
    def _calculate_fitness(self, chromosome: Chromosome) -> float:
        """적합도 함수 계산"""
        fitness = 0.0
        
        # 기본 페널티 계산
        conflicts, unassigned, rental_count = self._calculate_basic_penalties(chromosome)
        fitness += conflicts * PENALTY_CONFLICT
        fitness += unassigned * PENALTY_UNASSIGNED
        fitness += rental_count * WEIGHT_RENTAL
        
        # 공실 관련 계산
        vacancy_count, room_day_vacancy_map, room_day_utilization = \
            self._calculate_vacancy_info(chromosome)
        
        # 공실 페널티 및 보너스
        fitness += vacancy_count * WEIGHT_VACANCY
        fitness += self._calculate_vacancy_bonuses_and_penalties(
            room_day_vacancy_map, room_day_utilization
        )
        
        # 강의실 균등 분배 보너스
        room_usage = self._get_room_usage(chromosome)
        fitness += self._calculate_even_distribution_bonus(room_usage)
        
        # 시간대 다양성 보너스 및 페널티
        fitness += self._calculate_time_slot_diversity_score(chromosome)
        
        chromosome.fitness = fitness
        return fitness
    
    def _calculate_basic_penalties(
        self, chromosome: Chromosome
    ) -> Tuple[int, int, int]:
        """기본 페널티 계산 (충돌, 미배정, 임대 강의실)"""
        conflicts = 0
        unassigned = 0
        rental_count = 0
        
        for i, course1 in enumerate(self.courses):
            if course1.id not in chromosome.assignments:
                unassigned += 1
                continue
            
            day1, start_time1, room1 = chromosome.assignments[course1.id]
            end_time1 = get_3hour_end_time(start_time1)
            
            if room1 == RENTAL_ROOM:
                rental_count += 1
            
            # 다른 강의와의 충돌 검사
            for j, course2 in enumerate(self.courses):
                if i >= j or course2.id not in chromosome.assignments:
                    continue
                
                day2, start_time2, room2 = chromosome.assignments[course2.id]
                end_time2 = get_3hour_end_time(start_time2)
                
                # 강의실 충돌
                if room1 == room2 and day1 == day2:
                    if is_time_overlap(start_time1, end_time1, start_time2, end_time2):
                        conflicts += 1
                
                # 교수 충돌
                if course1.instructor == course2.instructor and day1 == day2:
                    if is_time_overlap(start_time1, end_time1, start_time2, end_time2):
                        conflicts += 1
        
        return conflicts, unassigned, rental_count
    
    def _get_room_usage(self, chromosome: Chromosome) -> Dict[str, int]:
        """강의실별 사용 횟수"""
        room_usage = {room: 0 for room in ALL_ROOMS}
        for course in self.courses:
            if course.id in chromosome.assignments:
                _, _, room = chromosome.assignments[course.id]
                room_usage[room] += 1
        return room_usage
    
    def _calculate_vacancy_info(
        self, chromosome: Chromosome
    ) -> Tuple[int, Dict, Dict]:
        """공실 정보 계산"""
        vacancy_count = 0
        room_day_vacancy_map: Dict[Tuple[str, str], List[str]] = {}
        room_day_utilization: Dict[Tuple[str, str], float] = {}
        
        for room in ALL_ROOMS:
            for day in DAYS:
                key = (room, day)
                room_day_vacancy_map[key] = []
                
                # 해당 요일, 해당 강의실에 배정된 강의들
                assigned_slots = []
                assigned_minutes = 0
                for course in self.courses:
                    if course.id in chromosome.assignments:
                        c_day, c_start, c_room = chromosome.assignments[course.id]
                        if c_day == day and c_room == room:
                            c_end = get_3hour_end_time(c_start)
                            assigned_slots.append((c_start, c_end))
                            assigned_minutes += BLOCK_DURATION_MINUTES
                
                # 활용률 계산
                utilization_rate = assigned_minutes / DAILY_WORKING_MINUTES if DAILY_WORKING_MINUTES > 0 else 0
                room_day_utilization[key] = utilization_rate
                
                # 공실 슬롯 찾기
                for start_time in TIME_SLOTS:
                    if not is_valid_time_slot(start_time):
                        continue
                    
                    end_time = get_3hour_end_time(start_time)
                    is_vacant = all(
                        not is_time_overlap(start_time, end_time, a_start, a_end)
                        for a_start, a_end in assigned_slots
                    )
                    
                    if is_vacant:
                        vacancy_count += 1
                        room_day_vacancy_map[key].append(start_time)
        
        return vacancy_count, room_day_vacancy_map, room_day_utilization
    
    def _calculate_vacancy_bonuses_and_penalties(
        self, 
        room_day_vacancy_map: Dict[Tuple[str, str], List[str]],
        room_day_utilization: Dict[Tuple[str, str], float]
    ) -> float:
        """공실 관련 보너스 및 페널티 계산"""
        score = 0.0
        total_3hour_vacancy_blocks = 0
        
        for room in ALL_ROOMS:
            for day in DAYS:
                key = (room, day)
                vacant_slots = room_day_vacancy_map.get(key, [])
                
                # 활용률 보너스
                utilization_rate = room_day_utilization.get(key, 0.0)
                score += BONUS_ROOM_DAY_UTILIZATION * utilization_rate
                
                # 공실 집중도 페널티
                if vacant_slots:
                    concentration_penalty = len(vacant_slots) * PENALTY_ROOM_DAY_VACANCY_CONCENTRATION
                    score += concentration_penalty
                    
                    # 3시간 블록 공실 보너스 계산
                    total_3hour_vacancy_blocks += self._count_3hour_vacancy_blocks(vacant_slots)
        
        # 3시간 블록 공실 보너스 적용
        if total_3hour_vacancy_blocks > 0:
            score += BONUS_3HOUR_VACANCY_BLOCK * total_3hour_vacancy_blocks
        
        return score
    
    def _count_3hour_vacancy_blocks(self, vacant_slots: List[str]) -> int:
        """정확히 3시간 블록인 공실 수 계산"""
        if not vacant_slots:
            return 0
        
        vacant_slots_sorted = sorted(vacant_slots, key=lambda s: time_to_minutes(s))
        count = 0
        
        for i, current_start in enumerate(vacant_slots_sorted):
            current_end = get_3hour_end_time(current_start)
            current_end_minutes = time_to_minutes(current_end)
            
            is_3hour_block = True
            
            # 다음 블록과 연속 확인
            if i + 1 < len(vacant_slots_sorted):
                next_start_minutes = time_to_minutes(vacant_slots_sorted[i + 1])
                if current_end_minutes == next_start_minutes:
                    is_3hour_block = False
            
            # 이전 블록과 연속 확인
            if i > 0:
                prev_end = get_3hour_end_time(vacant_slots_sorted[i - 1])
                prev_end_minutes = time_to_minutes(prev_end)
                if prev_end_minutes == time_to_minutes(current_start):
                    is_3hour_block = False
            
            if is_3hour_block:
                count += 1
        
        return count
    
    def _calculate_even_distribution_bonus(self, room_usage: Dict[str, int]) -> float:
        """강의실 균등 분배 보너스 계산"""
        if not room_usage:
            return 0.0
        
        usage_values = list(room_usage.values())
        if not usage_values:
            return 0.0
        
        mean_usage = sum(usage_values) / len(usage_values)
        variance = sum((u - mean_usage) ** 2 for u in usage_values) / len(usage_values)
        return BONUS_EVEN_DISTRIBUTION * (1.0 / (1.0 + variance))
    
    def _calculate_time_slot_diversity_score(self, chromosome: Chromosome) -> float:
        """시간대 다양성 점수 계산"""
        time_slot_usage = {slot: 0 for slot in TIME_SLOTS}
        
        for course in self.courses:
            if course.id in chromosome.assignments:
                _, start_time, _ = chromosome.assignments[course.id]
                if start_time in time_slot_usage:
                    time_slot_usage[start_time] += 1
        
        if not time_slot_usage:
            return 0.0
        
        usage_values = list(time_slot_usage.values())
        total_usage = sum(usage_values)
        if total_usage == 0:
            return 0.0
        
        used_slots = sum(1 for u in usage_values if u > 0)
        mean_usage = total_usage / len(usage_values)
        variance = sum((u - mean_usage) ** 2 for u in usage_values) / len(usage_values)
        
        score = 0.0
        
        # 시간대 다양성 보너스
        diversity_score = used_slots * (1.0 / (1.0 + variance))
        score += BONUS_TIME_SLOT_DIVERSITY * diversity_score
        
        # 시간대 과다 사용 페널티
        for slot, count in time_slot_usage.items():
            if count > mean_usage * TIME_SLOT_OVERUSE_THRESHOLD:
                overuse = count - mean_usage * TIME_SLOT_OVERUSE_THRESHOLD
                score += PENALTY_TIME_SLOT_OVERUSE * overuse
        
        # 사용되지 않은 시간대 보너스
        unused_slots = len(usage_values) - used_slots
        score += BONUS_TIME_SLOT_DIVERSITY * 2 * (len(usage_values) - unused_slots) / len(usage_values)
        
        return score
    
    def _select_parents(self, population: List[Chromosome]) -> Tuple[Chromosome, Chromosome]:
        """토너먼트 선택으로 부모 선택"""
        def tournament_select() -> Chromosome:
            tournament = random.sample(population, min(TOURNAMENT_SIZE, len(population)))
            return max(tournament, key=lambda c: c.fitness)
        
        return tournament_select(), tournament_select()
    
    def _count_vacancies(self, chromosome: Chromosome) -> int:
        """개체의 공실 수 계산"""
        vacancy_count = 0
        
        for room in ALL_ROOMS:
            for day in DAYS:
                assigned_slots = []
                for course in self.courses:
                    if course.id in chromosome.assignments:
                        c_day, c_start, c_room = chromosome.assignments[course.id]
                        if c_day == day and c_room == room:
                            c_end = get_3hour_end_time(c_start)
                            assigned_slots.append((c_start, c_end))
                
                for start_time in TIME_SLOTS:
                    if not is_valid_time_slot(start_time):
                        continue
                    
                    end_time = get_3hour_end_time(start_time)
                    is_vacant = all(
                        not is_time_overlap(start_time, end_time, a_start, a_end)
                        for a_start, a_end in assigned_slots
                    )
                    
                    if is_vacant:
                        vacancy_count += 1
        
        return vacancy_count
    
    def _crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        """교차 연산: 공실이 적은 부모의 배정을 우선 선택"""
        child = Chromosome(self.courses)
        
        # 각 부모의 공실 수 계산
        parent1_vacancies = self._count_vacancies(parent1)
        parent2_vacancies = self._count_vacancies(parent2)
        
        # 공실이 적은 부모를 더 높은 확률로 선택
        if parent1_vacancies < parent2_vacancies:
            preferred_parent_prob = CROSSOVER_PREFERENCE_PROB
        elif parent2_vacancies < parent1_vacancies:
            preferred_parent_prob = 1 - CROSSOVER_PREFERENCE_PROB
        else:
            preferred_parent_prob = 0.5
        
        # 각 강의에 대해 부모 중 하나의 배정을 상속
        for course in self.courses:
            if random.random() < preferred_parent_prob:
                source_parent = parent1 if course.id in parent1.assignments else parent2
            else:
                source_parent = parent2 if course.id in parent2.assignments else parent1
            
            if course.id in source_parent.assignments:
                day, start_time, room = source_parent.assignments[course.id]
                child.assign(course.id, day, start_time, room)
        
        return child
    
    def _mutate(self, chromosome: Chromosome):
        """돌연변이 연산: 일부 강의의 배정을 랜덤하게 변경"""
        time_slot_usage = {slot: 0 for slot in TIME_SLOTS}
        for course in self.courses:
            if course.id in chromosome.assignments:
                _, start_time, _ = chromosome.assignments[course.id]
                if start_time in time_slot_usage:
                    time_slot_usage[start_time] += 1
        
        for course in self.courses:
            if random.random() < MUTATION_RATE:
                day = random.choice(DAYS)
                start_time = self._select_time_slot_by_usage(time_slot_usage)
                if start_time:
                    time_slot_usage[start_time] += 1
                    room = self._select_room_by_preference()
                    chromosome.assign(course.id, day, start_time, room)
    
    def _has_conflict(
        self, 
        course: Course, 
        day: str, 
        start_time: str, 
        room: str, 
        chromosome: Chromosome
    ) -> bool:
        """강의 배정이 충돌하는지 확인"""
        end_time = get_3hour_end_time(start_time)
        
        for other_course in self.courses:
            if other_course.id == course.id or other_course.id not in chromosome.assignments:
                continue
            
            o_day, o_start, o_room = chromosome.assignments[other_course.id]
            o_end = get_3hour_end_time(o_start)
            
            # 강의실 충돌
            if room == o_room and day == o_day:
                if is_time_overlap(start_time, end_time, o_start, o_end):
                    return True
            
            # 교수 충돌
            if course.instructor == other_course.instructor and day == o_day:
                if is_time_overlap(start_time, end_time, o_start, o_end):
                    return True
        
        return False
    
    def _assign_to_best_slot(
        self, 
        course: Course, 
        chromosome: Chromosome, 
        avoid_conflicts: bool = True
    ) -> bool:
        """강의를 가장 적합한 시간대에 배정 시도"""
        # 시간대별 사용 빈도 계산
        time_slot_usage = {slot: 0 for slot in TIME_SLOTS}
        for c in self.courses:
            if c.id in chromosome.assignments:
                _, st, _ = chromosome.assignments[c.id]
                if st in time_slot_usage:
                    time_slot_usage[st] += 1
        
        # 사용 빈도가 낮은 시간대부터 시도
        valid_slots = [slot for slot in TIME_SLOTS if is_valid_time_slot(slot)]
        valid_slots.sort(key=lambda s: time_slot_usage[s])
        
        # 모든 조합 시도
        for start_time in valid_slots:
            for day in DAYS:
                for room in ALL_ROOMS:
                    if avoid_conflicts and self._has_conflict(course, day, start_time, room, chromosome):
                        continue
                    
                    chromosome.assign(course.id, day, start_time, room)
                    return True
        
        return False
    
    def _repair_chromosome(self, chromosome: Chromosome):
        """개체 수정: 명백한 충돌 제거 및 미배정 강의 배정"""
        # 미배정 강의 배정
        for course in self.courses:
            if course.id not in chromosome.assignments:
                self._assign_to_best_slot(course, chromosome, avoid_conflicts=True)
        
        # 충돌 해결
        max_iterations = 10
        for _ in range(max_iterations):
            conflict_found = False
            
            for i, course1 in enumerate(self.courses):
                if course1.id not in chromosome.assignments:
                    continue
                
                day1, start_time1, room1 = chromosome.assignments[course1.id]
                end_time1 = get_3hour_end_time(start_time1)
                
                for j, course2 in enumerate(self.courses):
                    if i >= j or course2.id not in chromosome.assignments:
                        continue
                    
                    day2, start_time2, room2 = chromosome.assignments[course2.id]
                    end_time2 = get_3hour_end_time(start_time2)
                    
                    # 충돌 확인
                    room_conflict = (
                        room1 == room2 and day1 == day2 and 
                        is_time_overlap(start_time1, end_time1, start_time2, end_time2)
                    )
                    instructor_conflict = (
                        course1.instructor == course2.instructor and day1 == day2 and
                        is_time_overlap(start_time1, end_time1, start_time2, end_time2)
                    )
                    
                    if room_conflict or instructor_conflict:
                        conflict_found = True
                        del chromosome.assignments[course1.id]
                        self._assign_to_best_slot(course1, chromosome, avoid_conflicts=True)
                        break
                
                if conflict_found:
                    break
            
            if not conflict_found:
                break
    
    def schedule(self) -> List[CourseAssignment]:
        """시간표 자동 배정 실행 (유전 알고리즘)"""
        if not self.courses:
            return []
        
        # 초기 개체군 생성 및 적합도 계산
        population = [self._generate_random_chromosome() for _ in range(POPULATION_SIZE)]
        for chromosome in population:
            self._calculate_fitness(chromosome)
        
        self.best_chromosome = max(population, key=lambda c: c.fitness).copy()
        
        # 진화 루프
        for generation in range(MAX_GENERATIONS):
            population.sort(key=lambda c: c.fitness, reverse=True)
            elites = [c.copy() for c in population[:ELITE_SIZE]]
            
            new_population = elites.copy()
            while len(new_population) < POPULATION_SIZE:
                if random.random() < CROSSOVER_RATE:
                    parent1, parent2 = self._select_parents(population)
                    child = self._crossover(parent1, parent2)
                    self._mutate(child)
                    self._repair_chromosome(child)
                else:
                    parent = self._select_parents(population)[0]
                    child = parent.copy()
                    self._mutate(child)
                    self._repair_chromosome(child)
                
                self._calculate_fitness(child)
                new_population.append(child)
            
            population = new_population
            
            # 최고 개체 업데이트
            current_best = max(population, key=lambda c: c.fitness)
            if current_best.fitness > self.best_chromosome.fitness:
                self.best_chromosome = current_best.copy()
            
            # 진행 상황 출력
            if (generation + 1) % 10 == 0:
                print(f"세대 {generation + 1}/{MAX_GENERATIONS}: 최고 적합도 = {self.best_chromosome.fitness:.2f}")
        
        return self.best_chromosome.to_course_assignments()
