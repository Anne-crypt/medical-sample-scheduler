from app.models import Sample, Technician, Equipment, SamplePriority, SampleType, TechnicianSpeciality
from app.planner import planifyLab


def schedule_as_tuples(schedule):
    return [
        (item.sampleId, item.technicianId, item.equipmentId, item.startTime, item.endTime, item.priority)
        for item in schedule
    ]

def test_1():
    samples = [
        Sample(id="S001", type=SampleType.BLOOD, priority=SamplePriority.URGENT, analysisTime=30, arrivalTime="09:00", patientId="P001"),
    ]
    technicians = [
        Technician(id="T001", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
    ]
    equipments = [
        Equipment(id="E001", name="Blood Analyzer", type=SampleType.BLOOD),
    ]

    # --- Call the function ---
    schedule, metrics = planifyLab(samples, technicians, equipments)

    expected_schedule = [
        ("S001", "T001", "E001", "09:00", "09:30", SamplePriority.URGENT),
    ]

    assert schedule_as_tuples(schedule) == expected_schedule
    assert metrics.totalTime == 30
    assert metrics.efficiency == 100.0
    assert metrics.conflicts == 0

def test_2():
    samples = [
        Sample(id="S001", type=SampleType.BLOOD, priority=SamplePriority.URGENT, analysisTime=45, arrivalTime="09:00", patientId="P001"),
        Sample(id="S002", type=SampleType.BLOOD, priority=SamplePriority.STAT, analysisTime=30, arrivalTime="09:30", patientId="P002"),
    ]
    technicians = [
        Technician(id="T001", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
    ]
    equipments = [
        Equipment(id="E001", name="Blood Analyzer", type=SampleType.BLOOD),
    ]

    # --- Call the function ---
    schedule, metrics = planifyLab(samples, technicians, equipments)

    expected_schedule = [
        ("S002", "T001", "E001", "09:30", "10:00", SamplePriority.STAT),
        ("S001", "T001", "E001", "10:00", "10:45", SamplePriority.URGENT),
    ]

    assert schedule_as_tuples(schedule) == expected_schedule
    assert metrics.totalTime == 75
    assert metrics.efficiency == 100.0
    assert metrics.conflicts == 0

def test_3():
    samples = [
        Sample(id="S001", type=SampleType.BLOOD, priority=SamplePriority.URGENT, analysisTime=60, arrivalTime="09:00", patientId="P001"),
        Sample(id="S002", type=SampleType.URINE, priority=SamplePriority.URGENT, analysisTime=30, arrivalTime="09:15", patientId="P002"),
        Sample(id="S003", type=SampleType.BLOOD, priority=SamplePriority.ROUTINE, analysisTime=45, arrivalTime="09:00", patientId="P003"),
    ]
    technicians = [
        Technician(id="T001", name="Alice Martin", speciality=TechnicianSpeciality.BLOOD, startTime="08:00", endTime="17:00"),
        Technician(id="T002", name="Alix Martine", speciality=TechnicianSpeciality.GENERAL, startTime="08:00", endTime="17:00"),
    ]
    equipments = [
        Equipment(id="E001", name="Blood Analyzer", type=SampleType.BLOOD),
        Equipment(id="E002", name="Urine Analyzer", type=SampleType.URINE),
    ]

    # --- Call the function ---
    schedule, metrics = planifyLab(samples, technicians, equipments)

    expected_schedule = [
        ("S001", "T001", "E001", "09:00", "10:00", SamplePriority.URGENT),
        ("S002", "T002", "E002", "09:15", "09:45", SamplePriority.URGENT),
        ("S003", "T001", "E001", "10:00", "10:45", SamplePriority.ROUTINE),
    ]

    assert schedule_as_tuples(schedule) == expected_schedule
    assert metrics.totalTime == 105
    assert metrics.efficiency == 128.6
    assert metrics.conflicts == 0


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

    expected_schedule = [
        ("S001", "T1", "E1", "09:00", "09:30", SamplePriority.STAT),
        ("S002", "T2", "E2", "09:15", "09:35", SamplePriority.URGENT),
    ]

    assert schedule_as_tuples(schedule) == expected_schedule
    assert metrics.totalTime == 35
    assert metrics.conflicts == 0


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

    expected_schedule = [
        ("S011", "T1", "E1", "09:00", "09:20", SamplePriority.STAT),
        ("S010", "T2", "E2", "09:00", "09:20", SamplePriority.URGENT),
    ]

    assert schedule_as_tuples(schedule) == expected_schedule, "not ok: URGENT was scheduled before STAT"

