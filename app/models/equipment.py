from dataclasses import dataclass
from enum import Enum, auto

class EquipmentType(Enum):
    BLOOD = auto()
    CHEMISTRY = auto()
    MICROBIOLOGY = auto()
    IMMUNOLOGY = auto()
    GENETICS = auto()


@dataclass
class Equipment:
    id: str
    name: str
    type: EquipmentType
    compatibleTypes: list[str]
    capacity: int
    maintenanceWindow: str
    cleaningTime: int
