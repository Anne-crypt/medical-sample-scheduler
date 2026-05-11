# app/models.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

# --- ENUMS ---

class SamplePriority(Enum):
    STAT = auto()
    URGENT = auto()
    ROUTINE = auto()

class SampleType(Enum):
    BLOOD = auto()
    URINE = auto()
    TISSUE = auto()

class TechnicianSpeciality(Enum):
    BLOOD = auto()
    URINE = auto()
    TISSUE = auto()
    GENERAL = auto()

@dataclass
class Sample:
    id: str
    type: SampleType          # BLOOD, URINE, TISSUE
    priority: SamplePriority  # STAT, URGENT, ROUTINE
    analysisTime: int         # durée en minutes
    arrivalTime: str          # "HH:MM" string
    patientId: str

    def get_arrival_datetime(self):
        """Return arrival time as a datetime.time object for calculations."""
        return datetime.strptime(self.arrivalTime, "%H:%M").time()


@dataclass
class Technician:
    id: str
    name: str
    speciality: TechnicianSpeciality  
    startTime: str            # "HH:MM"
    endTime: str              # "HH:MM"

    def get_start_datetime(self):
        return datetime.strptime(self.startTime, "%H:%M").time()

    def get_end_datetime(self):
        return datetime.strptime(self.endTime, "%H:%M").time()


@dataclass
class Equipment:
    id: str
    name: str
    type: SampleType                 
    available: bool = True

# --- OUTPUT CLASSES ---

@dataclass
class ScheduleItem:
    sampleId: str
    technicianId: str
    equipmentId: str
    startTime: str            # "HH:MM"
    endTime: str              # "HH:MM"
    priority: SamplePriority


@dataclass
class Metrics:
    totalTime: int            # minutes
    efficiency: float         # %
    conflicts: int            # number of detected conflicts