"""Unit tests for data processor."""

import pytest
from datetime import datetime
from src.core.data_processor import DataProcessor, Measurement


def test_data_processor_init(sample_protocol_dict):
    """Test DataProcessor initialization."""
    processor = DataProcessor(sample_protocol_dict)
    assert processor is not None
    assert processor.protocol == sample_protocol_dict


def test_add_measurement(data_processor):
    """Test adding a single measurement."""
    measurement = Measurement(
        measurement_id="test_voltage",
        phase_id="p1_test",
        timestamp=datetime.now(),
        value=50.0,
        unit="V",
    )

    data_processor.add_measurement(measurement)
    assert data_processor.get_measurement_count() == 1


def test_add_multiple_measurements(data_processor, sample_measurements):
    """Test adding multiple measurements."""
    data_processor.add_measurements(sample_measurements)
    assert data_processor.get_measurement_count() == len(sample_measurements)


def test_get_dataframe(data_processor, sample_measurements):
    """Test converting measurements to DataFrame."""
    data_processor.add_measurements(sample_measurements)
    df = data_processor.get_dataframe()

    assert not df.empty
    assert len(df) == len(sample_measurements)
    assert "timestamp" in df.columns
    assert "value" in df.columns
    assert "measurement_id" in df.columns


def test_aggregate_by_phase(data_processor, sample_measurements):
    """Test aggregating measurements by phase."""
    data_processor.add_measurements(sample_measurements)
    aggregated = data_processor.aggregate_by_phase()

    assert isinstance(aggregated, dict)
    assert "p1_test" in aggregated


def test_get_statistics(data_processor, sample_measurements):
    """Test calculating statistics."""
    data_processor.add_measurements(sample_measurements)
    stats = data_processor.get_statistics()

    assert "count" in stats
    assert "mean" in stats
    assert "std" in stats
    assert "min" in stats
    assert "max" in stats
    assert stats["count"] == len(sample_measurements)


def test_clear_measurements(data_processor, sample_measurements):
    """Test clearing measurements."""
    data_processor.add_measurements(sample_measurements)
    assert data_processor.get_measurement_count() > 0

    data_processor.clear_measurements()
    assert data_processor.get_measurement_count() == 0
