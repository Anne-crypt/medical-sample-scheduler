from dataclasses import dataclass
from datetime import datetime
# from enum import Enum, auto


# class Technicianspecialty(Enum):
#     BLOOD = auto()
#     URINE = auto()
#     TISSUE = auto()
#     GENERAL = auto()


@dataclass
class Technician:
    id: str
    name: str
    specialty: list[str]
    efficiency: float
    analysisType: str
    startTime: str
    endTime: str
    lunchBreak: str = "12:30-13:30"

    def __post_init__(self):
        start, end = self.get_lunch_break_window()
        if int((end - start).total_seconds() / 60) != 60:
            raise ValueError("lunchBreak must be exactly 1 hour, format HH:MM-HH:MM")

    def get_start_datetime(self):
        return datetime.strptime(self.startTime, "%H:%M").time()

    def get_end_datetime(self):
        return datetime.strptime(self.endTime, "%H:%M").time()

    def get_lunch_break_window(self):
        start_str, end_str = self.lunchBreak.split("-")
        start = datetime.strptime(start_str, "%H:%M")
        end = datetime.strptime(end_str, "%H:%M")
        return start, end
