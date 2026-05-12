from datetime import datetime, timedelta

TIME_FORMAT = "%H:%M"


def get_cleanup_time(equipment_type) -> int:
    """Return cleanup time in minutes for each equipment type"""
    cleanup_times = {
        "HEMATOLOGY": 10,
        "BIOCHEMISTRY": 15,
        "MICROBIOLOGY": 20,
        "IMMUNOLOGY": 12,
        "GENETICS": 30,
    }
    type_key = getattr(equipment_type, "name", str(equipment_type)).upper()
    aliases = {
        "BLOOD": "HEMATOLOGY",
        "CHEMISTRY": "BIOCHEMISTRY",
    }
    normalized = aliases.get(type_key, type_key)
    return cleanup_times.get(normalized, 0)


def get_equipment_usage_at(equipment_schedule, time_point):
    """
    Count how many analyses are running on the equipment at a given time_point (HH:MM string).
    """
    t_point = datetime.strptime(time_point, TIME_FORMAT)
    count = 0
    for s, e in equipment_schedule:
        s_dt = datetime.strptime(s, TIME_FORMAT)
        e_dt = datetime.strptime(e, TIME_FORMAT)
        if s_dt <= t_point < e_dt:
            count += 1
    return count


def is_equipment_available(equipment, start_time: str, end_time: str) -> bool:
    """
    Returns True if the equipment is available (capacity not exceeded + no maintenance overlap)
    """
    start_dt = datetime.strptime(start_time, TIME_FORMAT)
    end_dt = datetime.strptime(end_time, TIME_FORMAT)

    for maint_start, maint_end in equipment.maintenanceWindow or []:
        maint_start_dt = datetime.strptime(maint_start, TIME_FORMAT)
        maint_end_dt = datetime.strptime(maint_end, TIME_FORMAT)
        if start_dt < maint_end_dt and end_dt > maint_start_dt:
            return False

    return True


def next_available_equipment(
    start_time: str, duration: int, equipment, equipment_schedule
):
    """
    Return the earliest time this equipment can handle a new analysis of `duration` minutes,
    respecting its capacity.

    equipment: object with attributes .id and .capacity
    equipment_schedule: list of (start,end) tuples for this equipment
    """
    t_start = datetime.strptime(start_time, TIME_FORMAT)
    duration_td = timedelta(minutes=duration)
    cleanup_minutes = get_cleanup_time(equipment.type)

    while True:
        t_end = t_start + duration_td
        t_end_with_cleanup = t_end + timedelta(minutes=cleanup_minutes)

        # maintenance
        if not is_equipment_available(
            equipment, t_start.strftime(TIME_FORMAT), t_end.strftime(TIME_FORMAT)
        ):
            t_start += timedelta(minutes=1)
            continue

        # capacity
        conflict = False
        check_time = t_start
        while check_time < t_end:
            usage = get_equipment_usage_at(
                equipment_schedule, check_time.strftime(TIME_FORMAT)
            )
            if usage >= equipment.capacity:
                conflict = True
                break
            check_time += timedelta(minutes=1)

        if not conflict:
            return t_start.strftime(TIME_FORMAT), t_end_with_cleanup.strftime(
                TIME_FORMAT
            )

        # Shift start by 1 minute and try again
        t_start += timedelta(minutes=1)
