from dataclasses import dataclass

@dataclass
class Metrics:
    totalTime: int          
    efficiency: float         
    conflicts: int            