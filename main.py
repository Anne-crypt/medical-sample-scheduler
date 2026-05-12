from app.models import Sample, Technician, Equipment, SamplePriority, SampleType
from app.models.equipment import EquipmentType
from app.planner import planifyLab

# --- Example data ---
samples = [
    Sample(
        id="S001",
        type=SampleType.BLOOD,
        priority=SamplePriority.URGENT,
        analysisType="Hémogramme",
        analysisTime=45,
        arrivalTime="09:00",
        patientInfo={"age": 45, "service": "Urgences", "diagnosis": "Suspicion anémie"},
    ),
    Sample(
        id="S002",
        type=SampleType.BLOOD,
        priority=SamplePriority.STAT,
        analysisType="Coagulation",
        analysisTime=30,
        arrivalTime="09:30",
        patientInfo={
            "age": 67,
            "service": "Urgences",
            "diagnosis": "Suspicion hémorragie",
        },
    ),
]

technicians = [
    Technician(
        id="T001",
        name="Alice Martin",
        specialty=["Hémogramme", "Coagulation"],
        efficiency=0.95,
        analysisType="BLOOD",
        startTime="08:00",
        endTime="17:00",
        lunchBreak="12:30-13:30",
    ),
]

# Maintenance data
maintenance_map = {
    "EQ001": [("06:00", "07:00")],
    "EQ002": [("06:30", "07:30")],
    "EQ003": [("07:00", "08:00")],
    "EQ004": [("05:30", "06:30")],
    "EQ005": [("19:00", "20:00")],
}

# Equipment list
equipments = [
    Equipment(
        id="EQ001",
        name="Blood Analyzer A",
        type=EquipmentType.BLOOD,
        compatibleTypes=["Hémogramme", "Coagulation"],
        capacity=2,
        maintenanceWindow=[],
        cleaningTime=10,
    ),
]

# Apply maintenance windows
for eq in equipments:
    eq.maintenanceWindow = maintenance_map.get(eq.id, [])

# --- Call the function ---
schedule, metrics = planifyLab(samples, technicians, equipments)

# --- Print the schedule ---
print("=== Schedule ===")
for s in schedule:
    print(
        f"{s.sampleId} -> Tech: {s.technicianId}, Equip: {s.equipmentId}, Start: {s.startTime}, End: {s.endTime}, Priority: {s.priority.name}"
    )

# --- Print metrics ---
print("\n=== Metrics ===")
print(
    f"Total time: {metrics.totalTime} min, Efficiency: {metrics.efficiency:.2f}%, Conflicts: {metrics.conflicts}"
)
