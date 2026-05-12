import sys
from types import SimpleNamespace

from app import utils as app_utils
from app.models import Equipment, Sample, SamplePriority, SampleType, Technician
from app.models.equipment import EquipmentType
from app.planner import next_available, planifyLab

# app/planner.py imports "utils" as a top-level module.
# Expose app.utils under that name so tests can import planner reliably.
sys.modules.setdefault("utils", app_utils)


def test_next_available_pushes_after_lunch():
    tech_schedule = {"T1": [("12:00", "13:00")]}
    start = next_available("12:00", 30, tech_schedule["T1"])

    assert start == "13:00"


def test_planifyLab_schedules_after_lunch_break():
    samples = [
        SimpleNamespace(
            id="S001",
            analysisType="HEMATOLOGIE",
            priority=SamplePriority.URGENT,
            analysisTime=30,
            arrivalTime="12:00",
        )
    ]

    technicians = [
        SimpleNamespace(
            id="T1",
            specialty=["HEMATOLOGIE"],
            startTime="08:00",
        )
    ]

    equipments = [
        SimpleNamespace(
            id="E1",
            type="HEMATOLOGIE",
            compatibleTypes=["HEMATOLOGIE"],
            capacity=1,
            maintenanceWindow=[],
        )
    ]

    schedule, metrics = planifyLab(samples, technicians, equipments)

    assert len(schedule) == 1
    assert schedule[0].sampleId == "S001"
    assert schedule[0].technicianId == "T1"
    assert schedule[0].equipmentId == "E1"
    assert schedule[0].startTime == "13:00"
    assert schedule[0].endTime == "13:30"

    assert metrics.totalTime == 30
    assert metrics.efficiency == 100.0
    assert metrics.conflicts == 0


def test_planifyLab_with_20_samples_dataset():
    raw_samples = [
        {
            "id": "S001",
            "priority": "STAT",
            "type": "BLOOD",
            "analysisType": "Numeration complete",
            "analysisTime": 45,
            "arrivalTime": "08:30",
            "patientInfo": {
                "age": 67,
                "service": "Urgences",
                "diagnosis": "Suspicion hemorragie",
            },
        },
        {
            "id": "S008",
            "priority": "STAT",
            "type": "BLOOD",
            "analysisType": "Troponine",
            "analysisTime": 30,
            "arrivalTime": "09:15",
            "patientInfo": {
                "age": 55,
                "service": "Cardiologie",
                "diagnosis": "Infarctus suspecte",
            },
        },
        {
            "id": "S012",
            "priority": "STAT",
            "type": "BLOOD",
            "analysisType": "Hemoculture urgente",
            "analysisTime": 60,
            "arrivalTime": "10:45",
            "patientInfo": {
                "age": 34,
                "service": "Reanimation",
                "diagnosis": "Sepsis severe",
            },
        },
        {
            "id": "S017",
            "priority": "STAT",
            "type": "BLOOD",
            "analysisType": "Allergenes critiques",
            "analysisTime": 40,
            "arrivalTime": "13:20",
            "patientInfo": {
                "age": 8,
                "service": "Pediatrie",
                "diagnosis": "Choc anaphylactique",
            },
        },
        {
            "id": "S002",
            "priority": "URGENT",
            "type": "BLOOD",
            "analysisType": "Bilan hepatique",
            "analysisTime": 35,
            "arrivalTime": "08:45",
            "patientInfo": {
                "age": 42,
                "service": "Gastroenterologie",
                "diagnosis": "Hepatite virale",
            },
        },
        {
            "id": "S005",
            "priority": "URGENT",
            "type": "BLOOD",
            "analysisType": "Coagulation",
            "analysisTime": 25,
            "arrivalTime": "09:30",
            "patientInfo": {
                "age": 73,
                "service": "Chirurgie",
                "diagnosis": "Pre-operatoire",
            },
        },
        {
            "id": "S009",
            "priority": "URGENT",
            "type": "URINE",
            "analysisType": "ECBU",
            "analysisTime": 50,
            "arrivalTime": "10:15",
            "patientInfo": {
                "age": 29,
                "service": "Urologie",
                "diagnosis": "Infection urinaire",
            },
        },
        {
            "id": "S011",
            "priority": "URGENT",
            "type": "BLOOD",
            "analysisType": "Caryotype urgent",
            "analysisTime": 90,
            "arrivalTime": "11:00",
            "patientInfo": {
                "age": 32,
                "service": "Genetique medicale",
                "diagnosis": "Syndrome chromosomique",
            },
        },
        {
            "id": "S014",
            "priority": "URGENT",
            "type": "BLOOD",
            "analysisType": "Serologie HIV",
            "analysisTime": 55,
            "arrivalTime": "11:45",
            "patientInfo": {
                "age": 26,
                "service": "Infectiologie",
                "diagnosis": "Exposition VIH",
            },
        },
        {
            "id": "S016",
            "priority": "URGENT",
            "type": "BLOOD",
            "analysisType": "Frottis sanguin",
            "analysisTime": 40,
            "arrivalTime": "12:30",
            "patientInfo": {
                "age": 45,
                "service": "Hematologie",
                "diagnosis": "Leucemie suspectee",
            },
        },
        {
            "id": "S018",
            "priority": "URGENT",
            "type": "BLOOD",
            "analysisType": "Electrolytes",
            "analysisTime": 20,
            "arrivalTime": "14:15",
            "patientInfo": {
                "age": 81,
                "service": "Geriatrie",
                "diagnosis": "Deshydratation",
            },
        },
        {
            "id": "S020",
            "priority": "URGENT",
            "type": "TISSUE",
            "analysisType": "Parasitologie",
            "analysisTime": 65,
            "arrivalTime": "15:30",
            "patientInfo": {
                "age": 12,
                "service": "Pediatrie",
                "diagnosis": "Parasitose intestinale",
            },
        },
        {
            "id": "S003",
            "priority": "ROUTINE",
            "type": "BLOOD",
            "analysisType": "Bilan lipidique",
            "analysisTime": 30,
            "arrivalTime": "09:00",
            "patientInfo": {
                "age": 58,
                "service": "Medecine generale",
                "diagnosis": "Controle cholesterol",
            },
        },
        {
            "id": "S004",
            "priority": "ROUTINE",
            "type": "BLOOD",
            "analysisType": "Hemogramme standard",
            "analysisTime": 25,
            "arrivalTime": "09:15",
            "patientInfo": {
                "age": 35,
                "service": "Medecine du travail",
                "diagnosis": "Visite systematique",
            },
        },
        {
            "id": "S006",
            "priority": "ROUTINE",
            "type": "BLOOD",
            "analysisType": "Vaccination controle",
            "analysisTime": 35,
            "arrivalTime": "10:00",
            "patientInfo": {
                "age": 22,
                "service": "Medecine preventive",
                "diagnosis": "Titre anticorps",
            },
        },
        {
            "id": "S007",
            "priority": "ROUTINE",
            "type": "BLOOD",
            "analysisType": "Conseil genetique",
            "analysisTime": 120,
            "arrivalTime": "10:30",
            "patientInfo": {
                "age": 28,
                "service": "Consultation genetique",
                "diagnosis": "Antecedents familiaux",
            },
        },
        {
            "id": "S010",
            "priority": "ROUTINE",
            "type": "TISSUE",
            "analysisType": "Prelevement gorge",
            "analysisTime": 45,
            "arrivalTime": "11:15",
            "patientInfo": {
                "age": 19,
                "service": "ORL",
                "diagnosis": "Angine recidivante",
            },
        },
        {
            "id": "S013",
            "priority": "ROUTINE",
            "type": "BLOOD",
            "analysisType": "HbA1c",
            "analysisTime": 25,
            "arrivalTime": "12:00",
            "patientInfo": {
                "age": 52,
                "service": "Endocrinologie",
                "diagnosis": "Diabete type 2",
            },
        },
        {
            "id": "S015",
            "priority": "ROUTINE",
            "type": "BLOOD",
            "analysisType": "Vitesse sedimentation",
            "analysisTime": 60,
            "arrivalTime": "13:00",
            "patientInfo": {
                "age": 65,
                "service": "Rhumatologie",
                "diagnosis": "Inflammation chronique",
            },
        },
        {
            "id": "S019",
            "priority": "ROUTINE",
            "type": "BLOOD",
            "analysisType": "Pharmacogenetique",
            "analysisTime": 90,
            "arrivalTime": "14:45",
            "patientInfo": {
                "age": 47,
                "service": "Oncologie",
                "diagnosis": "Adaptation therapie",
            },
        },
    ]

    samples = [
        Sample(
            id=item["id"],
            priority=SamplePriority[item["priority"]],
            type=SampleType[item["type"]],
            analysisType=item["analysisType"],
            analysisTime=item["analysisTime"],
            arrivalTime=item["arrivalTime"],
            patientInfo=item["patientInfo"],
        )
        for item in raw_samples
    ]

    all_analysis_types = [item["analysisType"] for item in raw_samples]

    technicians = [
        Technician(
            id="T100",
            name="Tech polyvalent",
            specialty=all_analysis_types,
            efficiency=0.95,
            analysisType="ALL",
            startTime="08:00",
            endTime="20:00",
            lunchBreak="12:30-13:30",
        )
    ]

    equipments = [
        Equipment(
            id="EQ100",
            name="Analyzer multi",
            type=EquipmentType.BLOOD,
            compatibleTypes=all_analysis_types,
            capacity=100,
            maintenanceWindow=[],
            cleaningTime=0,
        )
    ]

    schedule, metrics = planifyLab(samples, technicians, equipments)

    assert len(schedule) == 20
    assert metrics.conflicts == 0

    first_four_ids = [item.sampleId for item in schedule[:4]]
    assert first_four_ids == ["S001", "S008", "S012", "S017"]


def test_planifyLab_with_8_technicians_dataset():
    technicians = [
        Technician(
            id="TECH001",
            name="Dr. Marie Dubois",
            specialty=["BLOOD", "CHEMISTRY"],
            efficiency=1.2,
            analysisType="MULTI",
            startTime="07:30",
            endTime="16:30",
            lunchBreak="12:30-13:30",
        ),
        Technician(
            id="TECH002",
            name="Jean-Pierre Martin",
            specialty=["MICROBIOLOGY", "IMMUNOLOGY"],
            efficiency=1.1,
            analysisType="MULTI",
            startTime="08:00",
            endTime="17:00",
            lunchBreak="13:00-14:00",
        ),
        Technician(
            id="TECH003",
            name="Sophie Bernard",
            specialty=["CHEMISTRY", "IMMUNOLOGY"],
            efficiency=1.0,
            analysisType="MULTI",
            startTime="08:00",
            endTime="17:00",
            lunchBreak="12:00-13:00",
        ),
        Technician(
            id="TECH004",
            name="Lucas Petit",
            specialty=["BLOOD", "GENETICS"],
            efficiency=0.95,
            analysisType="MULTI",
            startTime="09:00",
            endTime="18:00",
            lunchBreak="13:00-14:00",
        ),
        Technician(
            id="TECH005",
            name="Emma Rousseau",
            specialty=["MICROBIOLOGY"],
            efficiency=1.0,
            analysisType="MULTI",
            startTime="07:00",
            endTime="16:00",
            lunchBreak="12:30-13:30",
        ),
        Technician(
            id="TECH006",
            name="Thomas Moreau",
            specialty=["GENETICS", "IMMUNOLOGY"],
            efficiency=0.9,
            analysisType="MULTI",
            startTime="09:30",
            endTime="18:30",
            lunchBreak="13:30-14:30",
        ),
        Technician(
            id="TECH007",
            name="Camille Leroy",
            specialty=["CHEMISTRY", "BLOOD", "IMMUNOLOGY"],
            efficiency=1.05,
            analysisType="MULTI",
            startTime="08:30",
            endTime="17:30",
            lunchBreak="12:00-13:00",
        ),
        Technician(
            id="TECH008",
            name="Antoine Garnier",
            specialty=["BLOOD", "MICROBIOLOGY"],
            efficiency=0.85,
            analysisType="MULTI",
            startTime="10:00",
            endTime="19:00",
            lunchBreak="14:00-15:00",
        ),
    ]

    samples = [
        Sample(
            id="SX01",
            priority=SamplePriority.STAT,
            type=SampleType.BLOOD,
            analysisType="BLOOD",
            analysisTime=30,
            arrivalTime="08:00",
            patientInfo={"age": 60, "service": "Urgences", "diagnosis": "stat blood"},
        ),
        Sample(
            id="SX02",
            priority=SamplePriority.URGENT,
            type=SampleType.BLOOD,
            analysisType="CHEMISTRY",
            analysisTime=25,
            arrivalTime="08:10",
            patientInfo={"age": 45, "service": "Medecine", "diagnosis": "chem"},
        ),
        Sample(
            id="SX03",
            priority=SamplePriority.URGENT,
            type=SampleType.URINE,
            analysisType="MICROBIOLOGY",
            analysisTime=35,
            arrivalTime="08:20",
            patientInfo={"age": 30, "service": "Uro", "diagnosis": "micro"},
        ),
        Sample(
            id="SX04",
            priority=SamplePriority.ROUTINE,
            type=SampleType.BLOOD,
            analysisType="IMMUNOLOGY",
            analysisTime=40,
            arrivalTime="08:30",
            patientInfo={"age": 27, "service": "Immuno", "diagnosis": "immuno"},
        ),
        Sample(
            id="SX05",
            priority=SamplePriority.ROUTINE,
            type=SampleType.BLOOD,
            analysisType="GENETICS",
            analysisTime=45,
            arrivalTime="09:10",
            patientInfo={"age": 38, "service": "Genetique", "diagnosis": "genetics"},
        ),
        Sample(
            id="SX06",
            priority=SamplePriority.URGENT,
            type=SampleType.BLOOD,
            analysisType="BLOOD",
            analysisTime=20,
            arrivalTime="09:30",
            patientInfo={"age": 51, "service": "Cardio", "diagnosis": "blood2"},
        ),
        Sample(
            id="SX07",
            priority=SamplePriority.ROUTINE,
            type=SampleType.URINE,
            analysisType="MICROBIOLOGY",
            analysisTime=30,
            arrivalTime="10:15",
            patientInfo={"age": 33, "service": "Infectio", "diagnosis": "micro2"},
        ),
        Sample(
            id="SX08",
            priority=SamplePriority.ROUTINE,
            type=SampleType.BLOOD,
            analysisType="CHEMISTRY",
            analysisTime=25,
            arrivalTime="10:30",
            patientInfo={"age": 48, "service": "Chimie", "diagnosis": "chem2"},
        ),
    ]

    equipments = [
        Equipment(
            id="EQ-ALL",
            name="Analyzer all",
            type=EquipmentType.BLOOD,
            compatibleTypes=[
                "BLOOD",
                "CHEMISTRY",
                "MICROBIOLOGY",
                "IMMUNOLOGY",
                "GENETICS",
            ],
            capacity=100,
            maintenanceWindow=[],
            cleaningTime=0,
        )
    ]

    schedule, metrics = planifyLab(samples, technicians, equipments)

    assert len(technicians) == 8
    assert len(schedule) == len(samples)
    assert metrics.conflicts == 0
    assert {item.sampleId for item in schedule} == {item.id for item in samples}


def test_efficiency_coefficients():
    sample = Sample(
        id="SEFF01",
        priority=SamplePriority.URGENT,
        type=SampleType.BLOOD,
        analysisType="BLOOD",
        analysisTime=60,
        arrivalTime="09:00",
        patientInfo={"age": 40, "service": "Urgences", "diagnosis": "test"},
    )

    equipment = Equipment(
        id="EQ-EFF",
        name="Analyzer eff",
        type=EquipmentType.BLOOD,
        compatibleTypes=["BLOOD"],
        capacity=10,
        maintenanceWindow=[],
        cleaningTime=0,
    )

    fast_tech = Technician(
        id="TFAST",
        name="Fast",
        specialty=["BLOOD"],
        efficiency=1.2,
        analysisType="BLOOD",
        startTime="08:00",
        endTime="17:00",
        lunchBreak="12:30-13:30",
    )

    slow_tech = Technician(
        id="TSLOW",
        name="Slow",
        specialty=["BLOOD"],
        efficiency=0.8,
        analysisType="BLOOD",
        startTime="08:00",
        endTime="17:00",
        lunchBreak="12:30-13:30",
    )

    fast_schedule, _ = planifyLab([sample], [fast_tech], [equipment])
    slow_schedule, _ = planifyLab([sample], [slow_tech], [equipment])

    assert fast_schedule[0].startTime == "09:00"
    assert slow_schedule[0].startTime == "09:00"
    assert fast_schedule[0].endTime == "09:50"
    assert slow_schedule[0].endTime == "10:15"
