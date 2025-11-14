"""Data models for Fire Resistance Testing Protocol"""

from .fire_resistance_model import (
    SampleInformation,
    EnvironmentalConditions,
    EquipmentCalibration,
    RealTimeMeasurement,
    TestObservations,
    AcceptanceCriteriaResult,
    TestResults,
    TestReport,
    TestStatus,
    PassFailResult,
    SmokeLevel,
    MaterialIntegrity
)

__all__ = [
    'SampleInformation',
    'EnvironmentalConditions',
    'EquipmentCalibration',
    'RealTimeMeasurement',
    'TestObservations',
    'AcceptanceCriteriaResult',
    'TestResults',
    'TestReport',
    'TestStatus',
    'PassFailResult',
    'SmokeLevel',
    'MaterialIntegrity'
]
