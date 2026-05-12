from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import TypedDict

# --- ENUMS ---

class SamplePriority(Enum):
    STAT = auto()
    URGENT = auto()
    ROUTINE = auto()

class SampleType(Enum):
    BLOOD = auto()
    URINE = auto()
    TISSUE = auto()


class PatientInfo(TypedDict):
    age: int
    service: str
    diagnosis: str

@dataclass
class Sample:
    id: str
    type: SampleType          # BLOOD, URINE, TISSUE
    priority: SamplePriority  # STAT, URGENT, ROUTINE
    analysisType: str
    analysisTime: int         
    arrivalTime: str          
    patientInfo: PatientInfo

    def get_arrival_datetime(self):
        """Return arrival time as a datetime.time object for calculations."""
        return datetime.strptime(self.arrivalTime, "%H:%M").time()
