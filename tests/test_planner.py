from app.models import Sample, Technician, Equipment, SamplePriority, SampleType, TechnicianSpeciality
from app.planner import planifyLab

def test_planifyLab_simple():
    # --- Create example samples ---
    samples = [
        Sample(id="S001", type=SampleType.BLOOD, priority=SamplePriority.STAT, analysisTime=30, arrivalTime="09:00", patientId="P123"),
        Sample(id="S002", type=SampleType.URINE, priority=SamplePriority.URGENT, analysisTime=20, arrivalTime="09:15", patientId="P124"),
    ]

    # --- Create example technicians ---
    technicians = [
        Technician(id="T1", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
        Technician(id="T2", name="Bob Dupont", speciality=TechnicianSpeciality.URINE, startTime="08:00", endTime="17:00"),
    ]

    # --- Create example equipments ---
    equipments = [
        Equipment(id="E1", name="Blood Analyzer", type=SampleType.BLOOD),
        Equipment(id="E2", name="Urine Analyzer", type=SampleType.URINE),
    ]

    # --- Call the function ---
    schedule, metrics = planifyLab(samples, technicians, equipments)

    # --- Verify the schedule has been created ---
    assert len(schedule) == 2

    # --- Verify STAT sample is scheduled first ---
    assert schedule[0].sampleId == "S001"
    assert schedule[0].priority == SamplePriority.STAT

    # --- Verify technician matches sample type ---
    assert schedule[0].technicianId == "T1"
    assert schedule[1].technicianId == "T2"