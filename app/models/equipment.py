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
    maintenanceWindow: list[tuple[str, str]] = None
    cleaningTime: int = 0

    def __post_init__(self):
        if self.maintenanceWindow is None:
            self.maintenanceWindow = []
