from datetime import datetime, timedelta

TIME_FORMAT = "%H:%M"


def schedule_lunch_breaks(technicians, tech_schedule):
    """
    Schedule a mandatory 1-hour lunch break for each technician.

    Constraints:
    - Duration: exactly 60 minutes
    - Window: between 12:00 and 15:00
    - Flexibility: algorithm chooses the best start time
    - No overlapping analysis during the break

    Args:
        technicians: list of Technician objects
        tech_schedule: dict mapping tech_id -> list of (start, end) tuples for occupied slots

    Returns:
        Updated tech_schedule with lunch breaks included.
    """
    lunch_start_window = datetime.strptime("12:00", TIME_FORMAT)
    lunch_end_window = datetime.strptime("15:00", TIME_FORMAT)
    lunch_duration = 60  # minutes

    for tech in technicians:
        # Sort current schedule for proper conflict detection
        tech_schedule[tech.id].sort(key=lambda x: datetime.strptime(x[0], TIME_FORMAT))
        t_start = lunch_start_window
        while t_start <= lunch_end_window - timedelta(minutes=lunch_duration):
            t_end = t_start + timedelta(minutes=lunch_duration)
            conflict = False

            for s, e in tech_schedule[tech.id]:
                s_dt = datetime.strptime(s, TIME_FORMAT)
                e_dt = datetime.strptime(e, TIME_FORMAT)

                if t_start < e_dt and t_end > s_dt:
                    # If an analysis is in progress, shift t_start after its end
                    t_start = e_dt
                    conflict = True
                    break

            if not conflict:
                # Found a slot, schedule the lunch break
                tech_schedule[tech.id].append(
                    (t_start.strftime(TIME_FORMAT), t_end.strftime(TIME_FORMAT))
                )
                break
    return tech_schedule


def handle_stat_interrupt(tech_id, stat_start, stat_end, tech_schedule, metadata):
    """
    If a STAT sample overlaps a scheduled lunch, interrupt it and reschedule remaining time.
    """
    new_schedule = []
    for s, e in tech_schedule[tech_id]:
        s_dt = datetime.strptime(s, TIME_FORMAT)
        e_dt = datetime.strptime(e, TIME_FORMAT)

        # Case: pause overlaps with STAT
        if s_dt < datetime.strptime(stat_end, TIME_FORMAT) and e_dt > datetime.strptime(
            stat_start, TIME_FORMAT
        ):
            # Split pause
            if s_dt < datetime.strptime(stat_start, TIME_FORMAT):
                # Pause before STAT
                new_schedule.append((s, stat_start))
            if e_dt > datetime.strptime(stat_end, TIME_FORMAT):
                # Pause after STAT
                remaining_pause = (stat_end, e)
                new_schedule.append(remaining_pause)
            metadata[tech_id]["lunchInterruptions"] += 1
        else:
            new_schedule.append((s, e))

    tech_schedule[tech_id] = new_schedule


def insert_mandatory_lunch(tech_id, tech_schedule, lunch_duration=60):
    """
    Ensure a 60-min lunch is scheduled for the technician.

    Rules:
    - STAT > URGENT > Pause > ROUTINE
    - ROUTINE can be moved after 15:00 to free the slot
    """

    def add_minutes(time_str: str, minutes: int) -> str:
        t = datetime.strptime(time_str, TIME_FORMAT)
        t += timedelta(minutes=minutes)
        return t.strftime(TIME_FORMAT)

    lunch_window_start = datetime.strptime("12:00", TIME_FORMAT)
    lunch_window_end = datetime.strptime("15:00", TIME_FORMAT)
    lunch_delta = timedelta(minutes=lunch_duration)

    # Sort schedule chronologically
    tech_schedule[tech_id].sort(key=lambda x: datetime.strptime(x[0], TIME_FORMAT))

    t_start = lunch_window_start
    while t_start <= lunch_window_end - lunch_delta:
        t_end = t_start + lunch_delta
        conflict_idx = None

        for i, (s, e) in enumerate(tech_schedule[tech_id]):
            s_dt = datetime.strptime(s, TIME_FORMAT)
            e_dt = datetime.strptime(e, TIME_FORMAT)

            if t_start < e_dt and t_end > s_dt:
                conflict_idx = i
                break

        if conflict_idx is None:
            # Found free slot, schedule lunch
            tech_schedule[tech_id].append(
                (t_start.strftime(TIME_FORMAT), t_end.strftime(TIME_FORMAT))
            )
            break
        else:
            # Check if the conflicting task is ROUTINE -> shift it
            s, e = tech_schedule[tech_id][conflict_idx]
            # move ROUTINE after lunch
            tech_schedule[tech_id][conflict_idx] = (
                add_minutes(t_end.strftime(TIME_FORMAT), 0),
                e,
            )
            t_start += timedelta(minutes=5)  # try next slot
    else:
        # Could not fit in 12-15, append after 15:00
        last_end = max(
            datetime.strptime(e, TIME_FORMAT) for _, e in tech_schedule[tech_id]
        )
        t_start = max(last_end, lunch_window_end)
        t_end = t_start + lunch_delta
        tech_schedule[tech_id].append(
            (t_start.strftime(TIME_FORMAT), t_end.strftime(TIME_FORMAT))
        )

    return tech_schedule
