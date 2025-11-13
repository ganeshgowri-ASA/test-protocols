"""Unit tests for protocol loader."""

import pytest
import json
from pathlib import Path

from protocol_engine import ProtocolLoader


def test_loader_initialization():
    """Test protocol loader initialization."""
    loader = ProtocolLoader()
    assert loader.protocols_dir.exists()


def test_load_schema():
    """Test loading protocol schema."""
    loader = ProtocolLoader()
    schema = loader.load_schema("iam-001")

    assert schema is not None
    assert "$schema" in schema
    assert schema["title"] == "IAM-001 Incidence Angle Modifier Protocol"


def test_load_template(protocol_template):
    """Test loading protocol template."""
    loader = ProtocolLoader()
    template = loader.load_template("iam-001")

    assert template is not None
    assert "protocol_info" in template
    assert template["protocol_info"]["protocol_id"] == "IAM-001"


def test_load_config(protocol_config):
    """Test loading protocol configuration."""
    loader = ProtocolLoader()
    config = loader.load_config("iam-001")

    assert config is not None
    assert config["protocol_id"] == "IAM-001"
    assert "default_settings" in config


def test_create_from_template():
    """Test creating protocol from template."""
    loader = ProtocolLoader()

    protocol = loader.create_from_template(
        "iam-001",
        **{"sample_info.sample_id": "TEST-123"}
    )

    assert protocol["protocol_info"]["protocol_id"] == "IAM-001"
    assert protocol["sample_info"]["sample_id"] == "TEST-123"


def test_save_and_load_protocol(temp_dir, sample_protocol_data):
    """Test saving and loading protocol."""
    loader = ProtocolLoader()

    file_path = temp_dir / "test_protocol.json"
    loader.save_protocol(sample_protocol_data, file_path)

    assert file_path.exists()

    loaded_data = loader.load_protocol(file_path)
    assert loaded_data["protocol_info"]["protocol_id"] == "IAM-001"
    assert len(loaded_data["measurements"]) == len(sample_protocol_data["measurements"])


def test_list_protocols():
    """Test listing available protocols."""
    loader = ProtocolLoader()
    protocols = loader.list_protocols()

    assert "iam-001" in protocols


def test_load_nonexistent_schema():
    """Test loading non-existent schema."""
    loader = ProtocolLoader()

    with pytest.raises(FileNotFoundError):
        loader.load_schema("nonexistent-protocol")


def test_apply_overrides_nested():
    """Test applying nested overrides."""
    loader = ProtocolLoader()

    protocol = loader.create_from_template(
        "iam-001",
        **{
            "sample_info.sample_id": "NESTED-001",
            "sample_info.manufacturer": "TestCo",
            "test_configuration.irradiance": 1200
        }
    )

    assert protocol["sample_info"]["sample_id"] == "NESTED-001"
    assert protocol["sample_info"]["manufacturer"] == "TestCo"
    assert protocol["test_configuration"]["irradiance"] == 1200
