from typing import List, Tuple
from datetime import datetime, timedelta
from app.models import Sample, Technician, Equipment, SamplePriority, ScheduleItem, Metrics

TIME_FORMAT = "%H:%M"

def add_minutes(time_str: str, minutes: int) -> str:
    """Add minutes to HH:MM string and return new HH:MM"""
    t = datetime.strptime(time_str, TIME_FORMAT)
    t += timedelta(minutes=minutes)
    return t.strftime(TIME_FORMAT)

# def is_available(schedule_list: List[Tuple[str, str]], start: str, end: str) -> bool:
#     """Check if a given time slot conflicts with a list of (start,end) tuples"""
#     start_dt = datetime.strptime(start, TIME_FORMAT)
#     end_dt = datetime.strptime(end, TIME_FORMAT)
#     for s, e in schedule_list:
#         s_dt = datetime.strptime(s, TIME_FORMAT)
#         e_dt = datetime.strptime(e, TIME_FORMAT)
#         if start_dt < e_dt and end_dt > s_dt:  # overlap
#             return False
#     return True

def next_available(start: str, duration: int, schedule_list):
    """Retourne le prochain créneau disponible sur schedule_list"""
    t_start = datetime.strptime(start, TIME_FORMAT)
    while True:
        t_end = t_start + timedelta(minutes=duration)
        overlap = False
        for s, e in schedule_list:
            s_dt = datetime.strptime(s, TIME_FORMAT)
            e_dt = datetime.strptime(e, TIME_FORMAT)
            if t_start < e_dt and t_end > s_dt:
                t_start = e_dt
                overlap = True
                break
        if not overlap:
            return t_start.strftime(TIME_FORMAT)

def planifyLab(samples: List[Sample],
               technicians: List[Technician],
               equipments: List[Equipment]
               ) -> Tuple[List[ScheduleItem], Metrics]:

    # Sort samples by priority (STAT first).
    priority_order = {
        SamplePriority.STAT: 1,
        SamplePriority.URGENT: 2,
        SamplePriority.ROUTINE: 3
    }

    samples_sorted = sorted(samples, key=lambda s: priority_order[s.priority])

    schedule: List[ScheduleItem] = []

    # Track occupied slots for techs and equipments as (start, end) tuples.
    tech_schedule = {t.id: [] for t in technicians}  # list of (start,end)
    eq_schedule = {e.id: [] for e in equipments}    # list of (start,end)

    conflicts = 0

    for sample in samples_sorted:
        # --- Find a compatible technician available ---
        assigned = False

        for tech in technicians:
            if tech.speciality.name == sample.type.name or tech.speciality.name == "GENERAL":
                # start from arrivalTime or tech startTime
                earliest_start = max(sample.arrivalTime, tech.startTime)
                earliest_start = next_available(earliest_start, sample.analysisTime, tech_schedule[tech.id])
                end_time = add_minutes(earliest_start, sample.analysisTime)
               
                # Check equipment availability
                for eq in equipments:
                    if eq.type == sample.type:
                        eq_start = next_available(earliest_start, sample.analysisTime, eq_schedule[eq.id])
                        if eq_start == earliest_start:
                            # Assign sample to technician and equipment
                             schedule.append(ScheduleItem(
                                sampleId=sample.id,
                                technicianId=tech.id,
                                equipmentId=eq.id,
                                startTime=earliest_start,
                                endTime=end_time,
                                priority=sample.priority
                            ))
                        # Mark slots as occupied
                        tech_schedule[tech.id].append((earliest_start, end_time))
                        eq_schedule[eq.id].append((earliest_start, end_time))
                        assigned = True
                        break
                if assigned:
                    break
    if not assigned:
        conflicts += 1
        
    # --- Compute metrics ---
    # def add_minutes_diff(start: str, end: str) -> int:
    #     t_start = datetime.strptime(start, TIME_FORMAT)
    #     t_end = datetime.strptime(end, TIME_FORMAT)
    #     return int((t_end - t_start).total_seconds() / 60)

    # total_time = sum(add_minutes_diff(item.startTime, item.endTime) for item in schedule)
    # efficiency = 100 if schedule else 0

    def add_minutes_diff(start: str, end: str) -> int:
        t_start = datetime.strptime(start, TIME_FORMAT)
        t_end = datetime.strptime(end, TIME_FORMAT)
        return int((t_end - t_start).total_seconds() / 60)

    if schedule:
        # Total occupied time = from first start to last end
        first_start = min(datetime.strptime(item.startTime, TIME_FORMAT) for item in schedule)
        last_end = max(datetime.strptime(item.endTime, TIME_FORMAT) for item in schedule)
        total_time = int((last_end - first_start).total_seconds() / 60)
        
        # Sum of individual analysis times
        used_time = sum(add_minutes_diff(item.startTime, item.endTime) for item in schedule)
        
        efficiency = round(used_time / total_time * 100, 1)
    else:
        total_time = 0
        efficiency = 0

    metrics = Metrics(totalTime=total_time, efficiency=efficiency, conflicts=conflicts)

    return schedule, metrics