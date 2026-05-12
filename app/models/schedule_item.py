from dataclasses import dataclass
from app.models.sample import SamplePriority


@dataclass
class ScheduleItem:
    sampleId: str
    technicianId: str
    equipmentId: str
    startTime: str            # "HH:MM"
    endTime: str              # "HH:MM"
    priority: SamplePriority
