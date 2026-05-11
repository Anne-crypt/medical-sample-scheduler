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


def test_planifyLab_priority_regression_not_ok_if_urgent_before_stat():
    """Fail fast if URGENT is ever scheduled before STAT."""
    # Input order is intentionally wrong; planner must still prioritize STAT first.
    samples = [
        Sample(id="S010", type=SampleType.URINE, priority=SamplePriority.URGENT, analysisTime=20, arrivalTime="09:00", patientId="P210"),
        Sample(id="S011", type=SampleType.BLOOD, priority=SamplePriority.STAT, analysisTime=20, arrivalTime="09:00", patientId="P211"),
    ]

    technicians = [
        Technician(id="T1", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
        Technician(id="T2", name="Bob Dupont", speciality=TechnicianSpeciality.URINE, startTime="08:00", endTime="17:00"),
    ]

    equipments = [
        Equipment(id="E1", name="Blood Analyzer", type=SampleType.BLOOD),
        Equipment(id="E2", name="Urine Analyzer", type=SampleType.URINE),
    ]

    schedule, _ = planifyLab(samples, technicians, equipments)

    assert len(schedule) == 2
    assert schedule[0].priority == SamplePriority.STAT, "not ok: URGENT was scheduled before STAT"


def test_planifyLab_technician_handles_only_one_sample_at_a_time():
    samples = [
        Sample(id="S100", type=SampleType.BLOOD, priority=SamplePriority.STAT, analysisTime=30, arrivalTime="09:00", patientId="P300"),
        Sample(id="S101", type=SampleType.BLOOD, priority=SamplePriority.URGENT, analysisTime=30, arrivalTime="09:00", patientId="P301"),
    ]

    # One blood technician only.
    technicians = [
        Technician(id="T1", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
    ]

    # Two compatible machines to isolate the technician-capacity rule.
    equipments = [
        Equipment(id="E1", name="Blood Analyzer A", type=SampleType.BLOOD),
        Equipment(id="E2", name="Blood Analyzer B", type=SampleType.BLOOD),
    ]

    schedule, _ = planifyLab(samples, technicians, equipments)

    # With overlapping requests and only one technician, only one sample can be assigned.
    assert len(schedule) == 1
    assert schedule[0].technicianId == "T1"


def test_planifyLab_equipment_handles_only_one_sample_at_a_time():
    samples = [
        Sample(id="S200", type=SampleType.BLOOD, priority=SamplePriority.STAT, analysisTime=30, arrivalTime="09:00", patientId="P400"),
        Sample(id="S201", type=SampleType.BLOOD, priority=SamplePriority.URGENT, analysisTime=30, arrivalTime="09:00", patientId="P401"),
    ]

    # Two blood technicians to isolate the equipment-capacity rule.
    technicians = [
        Technician(id="T1", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
        Technician(id="T2", name="Bob Dupont", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
    ]

    # One compatible machine only.
    equipments = [
        Equipment(id="E1", name="Blood Analyzer", type=SampleType.BLOOD),
    ]

    schedule, _ = planifyLab(samples, technicians, equipments)

    # With overlapping requests and only one equipment, only one sample can be assigned.
    assert len(schedule) == 1
    assert schedule[0].equipmentId == "E1"

