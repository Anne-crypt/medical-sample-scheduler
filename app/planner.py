from typing import List, Tuple
from datetime import datetime, timedelta
import math
from app.models import (
    Sample,
    Technician,
    Equipment,
    SamplePriority,
    ScheduleItem,
    Metrics,
)
from utils.equipment_utils import next_available_equipment
from utils.lunch_utils import (
    schedule_lunch_breaks,
    handle_stat_interrupt,
    insert_mandatory_lunch,
)

TIME_FORMAT = "%H:%M"


def add_minutes(time_str: str, minutes: int) -> str:
    """Add minutes to HH:MM string and return new HH:MM"""
    t = datetime.strptime(time_str, TIME_FORMAT)
    t += timedelta(minutes=minutes)
    return t.strftime(TIME_FORMAT)


def next_available(start: str, duration: int, schedule_list):
    """Returns next available slot on schedule_list"""
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


def adjusted_analysis_time(base_minutes: int, efficiency: float) -> int:
    """Return effective duration based on technician efficiency."""
    safe_efficiency = efficiency if efficiency and efficiency > 0 else 1.0
    return max(1, math.ceil(base_minutes / safe_efficiency))


def planifyLab(
    samples: List[Sample], technicians: List[Technician], equipments: List[Equipment]
) -> Tuple[List[ScheduleItem], Metrics]:

    # Sort samples by priority (STAT first).
    priority_order = {
        SamplePriority.STAT: 1,
        SamplePriority.URGENT: 2,
        SamplePriority.ROUTINE: 3,
    }

    samples_sorted = sorted(samples, key=lambda s: priority_order[s.priority])

    schedule: List[ScheduleItem] = []

    # Track occupied slots for techs and equipments as (start, end) tuples.
    tech_schedule = {t.id: [] for t in technicians}  # list of (start,end)
    tech_schedule = schedule_lunch_breaks(technicians, tech_schedule)
    eq_schedule = {e.id: [] for e in equipments}  # list of (start,end)

    # Track lunch interruptions per technician
    metadata = {tech.id: {"lunchInterruptions": 0} for tech in technicians}

    conflicts = 0

    for sample in samples_sorted:
        # --- Find a compatible technician available ---
        assigned = False

        # --- Find compatible technicians ---
        compatible_techs = [
            t for t in technicians if sample.analysisType in t.specialty
        ]

        # STAT priority: assign to most specialized tech first (least specialties)
        if sample.priority == SamplePriority.STAT:
            compatible_techs.sort(key=lambda t: len(t.specialty))

        for tech in compatible_techs:
            effective_duration = adjusted_analysis_time(
                sample.analysisTime,
                getattr(tech, "efficiency", 1.0),
            )
            # start from arrivalTime or tech startTime
            earliest_start = max(sample.arrivalTime, tech.startTime)
            earliest_start = next_available(
                earliest_start, effective_duration, tech_schedule[tech.id]
            )
            end_time = add_minutes(earliest_start, effective_duration)
            tech_schedule = insert_mandatory_lunch(tech.id, tech_schedule)

            # Check equipment availability
            for eq in equipments:
                if sample.analysisType in eq.compatibleTypes:
                    start_for_eq, end_for_eq_with_cleanup = next_available_equipment(
                        earliest_start, effective_duration, eq, eq_schedule[eq.id]
                    )
                    if start_for_eq != earliest_start:
                        continue

                    if sample.priority == SamplePriority.STAT:
                        handle_stat_interrupt(
                            tech_id=tech.id,
                            stat_start=earliest_start,
                            stat_end=end_time,
                            tech_schedule=tech_schedule,
                            metadata=metadata,
                        )

                    schedule.append(
                        ScheduleItem(
                            sampleId=sample.id,
                            technicianId=tech.id,
                            equipmentId=eq.id,
                            startTime=start_for_eq,
                            endTime=add_minutes(start_for_eq, effective_duration),
                            priority=sample.priority,
                        )
                    )
                    tech_schedule[tech.id].append(
                        (start_for_eq, add_minutes(start_for_eq, effective_duration))
                    )
                    eq_schedule[eq.id].append((start_for_eq, end_for_eq_with_cleanup))
                    assigned = True
                    break
            if assigned:
                break
        if not assigned:
            conflicts += 1

    # to see interruptions metric
    # for tech_id, data in metadata.items():
    # print(f"Technician {tech_id} lunch interruptions: {data['lunchInterruptions']}")

    # --- Compute metrics ---

    def add_minutes_diff(start: str, end: str) -> int:
        t_start = datetime.strptime(start, TIME_FORMAT)
        t_end = datetime.strptime(end, TIME_FORMAT)
        return int((t_end - t_start).total_seconds() / 60)

    if schedule:
        # Total occupied time = from first start to last end
        first_start = min(
            datetime.strptime(item.startTime, TIME_FORMAT) for item in schedule
        )
        last_end = max(
            datetime.strptime(item.endTime, TIME_FORMAT) for item in schedule
        )
        total_time = int((last_end - first_start).total_seconds() / 60)

        # Sum of individual analysis times
        used_time = sum(
            add_minutes_diff(item.startTime, item.endTime) for item in schedule
        )

        efficiency = round(used_time / total_time * 100, 1)
    else:
        total_time = 0
        efficiency = 0

    metrics = Metrics(totalTime=total_time, efficiency=efficiency, conflicts=conflicts)

    return schedule, metrics
