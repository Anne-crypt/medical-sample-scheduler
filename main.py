from app.models import Sample, Technician, Equipment, SamplePriority, SampleType, TechnicianSpeciality
from app.planner import planifyLab

# --- Example data ---
samples = [
    Sample(id="S001", type=SampleType.BLOOD, priority=SamplePriority.STAT, analysisTime=30, arrivalTime="09:00", patientId="P123"),
    Sample(id="S002", type=SampleType.URINE, priority=SamplePriority.URGENT, analysisTime=20, arrivalTime="09:15", patientId="P124"),
    Sample(id="S003", type=SampleType.BLOOD, priority=SamplePriority.ROUTINE, analysisTime=45, arrivalTime="10:00", patientId="P125"),
]

technicians = [
    Technician(id="T1", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
    Technician(id="T2", name="Bob Dupont", speciality=TechnicianSpeciality.URINE, startTime="08:00", endTime="17:00"),
]

equipments = [
    Equipment(id="E1", name="Blood Analyzer", type=SampleType.BLOOD),
    Equipment(id="E2", name="Urine Analyzer", type=SampleType.URINE),
]

# --- Call the function ---
schedule, metrics = planifyLab(samples, technicians, equipments)

# --- Print the schedule ---
print("=== Schedule ===")
for s in schedule:
    print(f"{s.sampleId} -> Tech: {s.technicianId}, Equip: {s.equipmentId}, Start: {s.startTime}, End: {s.endTime}, Priority: {s.priority.name}")

# --- Print metrics ---
print("\n=== Metrics ===")
print(f"Total time: {metrics.totalTime} min, Efficiency: {metrics.efficiency:.2f}%, Conflicts: {metrics.conflicts}")