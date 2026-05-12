from typing import List, Tuple
from datetime import datetime, timedelta
from app.models import Sample, Technician, Equipment, SamplePriority, ScheduleItem, Metrics

TIME_FORMAT = "%H:%M"

def add_minutes(time_str: str, minutes: int) -> str:
    """Add minutes to HH:MM string and return new HH:MM"""
    t = datetime.strptime(time_str, TIME_FORMAT)
    t += timedelta(minutes=minutes)
    return t.strftime(TIME_FORMAT)

def is_available(schedule_list: List[Tuple[str, str]], start: str, end: str) -> bool:
    """Check if a given time slot conflicts with a list of (start,end) tuples"""
    start_dt = datetime.strptime(start, TIME_FORMAT)
    end_dt = datetime.strptime(end, TIME_FORMAT)
    for s, e in schedule_list:
        s_dt = datetime.strptime(s, TIME_FORMAT)
        e_dt = datetime.strptime(e, TIME_FORMAT)
        if start_dt < e_dt and end_dt > s_dt:  # overlap
            return False
    return True

def planifyLab(samples: List[Sample],
               technicians: List[Technician],
               equipments: List[Equipment]
               ) -> Tuple[List[ScheduleItem], Metrics]:

    # --- 1️⃣ Sort samples by priority ---
    # STAT < URGENT < ROUTINE
    priority_order = {
        SamplePriority.STAT: 1,
        SamplePriority.URGENT: 2,
        SamplePriority.ROUTINE: 3
    }

    samples_sorted = sorted(samples, key=lambda s: priority_order[s.priority])

    # --- 2️⃣ Assign resources ---
    schedule: List[ScheduleItem] = []

    # --- Track occupied slots for techs and equipments ---
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
                end_time = add_minutes(earliest_start, sample.analysisTime)
                # check tech availability in its schedule
                if is_available(tech_schedule[tech.id], earliest_start, end_time) and end_time <= tech.endTime:
                    # --- Find a compatible equipment available ---
                    for eq in equipments:
                        if eq.type == sample.type and eq.available:
                            if is_available(eq_schedule[eq.id], earliest_start, end_time):
                                # assign
                                item = ScheduleItem(
                                    sampleId=sample.id,
                                    technicianId=tech.id,
                                    equipmentId=eq.id,
                                    startTime=earliest_start,
                                    endTime=end_time,
                                    priority=sample.priority
                                )
                                schedule.append(item)
                                # mark slots as occupied
                                tech_schedule[tech.id].append((earliest_start, end_time))
                                eq_schedule[eq.id].append((earliest_start, end_time))
                                assigned = True
                                break
                if assigned:
                    break
        # If no assignment possible, skip (could add conflicts count later)
    if not assigned:
        conflicts += 1
        
    # --- 3️⃣ Compute metrics ---
    def add_minutes_diff(start: str, end: str) -> int:
        t_start = datetime.strptime(start, TIME_FORMAT)
        t_end = datetime.strptime(end, TIME_FORMAT)
        return int((t_end - t_start).total_seconds() / 60)

    total_time = sum(add_minutes_diff(item.startTime, item.endTime) for item in schedule)
    efficiency = 100 if schedule else 0
    conflicts = 0

    metrics = Metrics(totalTime=total_time, efficiency=efficiency, conflicts=conflicts)

    return schedule, metrics