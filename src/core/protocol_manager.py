"""
Protocol Manager - Load, validate, and manage test protocols
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProtocolManager:
    """Manages test protocol loading, validation, and access."""

    def __init__(self, protocol_dir: str = "protocols"):
        """
        Initialize the protocol manager.

        Args:
            protocol_dir: Directory containing protocol definitions
        """
        self.protocol_dir = Path(protocol_dir)
        self.protocols: Dict[str, Dict] = {}
        self.configs: Dict[str, Dict] = {}
        self._load_all_protocols()

    def _load_all_protocols(self) -> None:
        """Load all protocols from the protocol directory."""
        if not self.protocol_dir.exists():
            logger.warning(f"Protocol directory not found: {self.protocol_dir}")
            return

        for protocol_path in self.protocol_dir.iterdir():
            if protocol_path.is_dir():
                self._load_protocol(protocol_path.name)

    def _load_protocol(self, protocol_id: str) -> None:
        """
        Load a specific protocol.

        Args:
            protocol_id: Protocol identifier (e.g., 'conc-001')
        """
        protocol_path = self.protocol_dir / protocol_id

        # Load schema
        schema_file = protocol_path / "schema" / f"{protocol_id}-schema.json"
        if schema_file.exists():
            with open(schema_file, 'r') as f:
                self.protocols[protocol_id] = json.load(f)
                logger.info(f"Loaded protocol: {protocol_id}")
        else:
            logger.warning(f"Schema not found for protocol: {protocol_id}")

        # Load default config
        config_file = protocol_path / "config" / "default-config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.configs[protocol_id] = json.load(f)
                logger.info(f"Loaded config for protocol: {protocol_id}")

    def get_protocol(self, protocol_id: str) -> Optional[Dict]:
        """
        Get protocol schema by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol schema dictionary or None if not found
        """
        return self.protocols.get(protocol_id)

    def get_config(self, protocol_id: str) -> Optional[Dict]:
        """
        Get protocol configuration by ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol configuration dictionary or None if not found
        """
        return self.configs.get(protocol_id)

    def list_protocols(self) -> List[str]:
        """
        List all available protocol IDs.

        Returns:
            List of protocol identifiers
        """
        return list(self.protocols.keys())

    def get_protocol_metadata(self, protocol_id: str) -> Optional[Dict]:
        """
        Get protocol metadata.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Protocol metadata dictionary or None if not found
        """
        protocol = self.get_protocol(protocol_id)
        if protocol:
            return {
                "protocol_id": protocol.get("protocol_id"),
                "name": protocol.get("name"),
                "version": protocol.get("version"),
                "description": protocol.get("description"),
                "metadata": protocol.get("metadata", {})
            }
        return None

    def get_form_template(self, protocol_id: str) -> Optional[Dict]:
        """
        Get UI form template for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Form template dictionary or None if not found
        """
        template_file = self.protocol_dir / protocol_id / "templates" / "form-template.json"
        if template_file.exists():
            with open(template_file, 'r') as f:
                return json.load(f)
        return None

    def get_qc_criteria(self, protocol_id: str) -> Optional[Dict]:
        """
        Get QC criteria for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            QC criteria dictionary or None if not found
        """
        protocol = self.get_protocol(protocol_id)
        if protocol:
            return protocol.get("qc_criteria", {})
        return None

    def get_calibration_requirements(self, protocol_id: str) -> Optional[Dict]:
        """
        Get calibration requirements for a protocol.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Calibration requirements dictionary or None if not found
        """
        protocol = self.get_protocol(protocol_id)
        if protocol:
            return protocol.get("calibration_requirements", {})
        return None

    def generate_test_run_id(self, protocol_id: str) -> str:
        """
        Generate a unique test run ID.

        Args:
            protocol_id: Protocol identifier

        Returns:
            Unique test run ID in format: PROTOCOL-YYYYMMDD-####
        """
        date_str = datetime.now().strftime("%Y%m%d")

        # In production, this would check database for existing IDs
        # For now, use timestamp-based sequence
        sequence = datetime.now().strftime("%H%M")

        return f"{protocol_id.upper()}-{date_str}-{sequence}"

    def validate_equipment_calibration(
        self,
        protocol_id: str,
        equipment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate equipment calibration status.

        Args:
            protocol_id: Protocol identifier
            equipment_data: Equipment information including calibration dates

        Returns:
            Validation result with status and messages
        """
        requirements = self.get_calibration_requirements(protocol_id)
        if not requirements:
            return {"valid": True, "message": "No calibration requirements defined"}

        result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }

        calibration_date = equipment_data.get("calibration_date")
        if not calibration_date:
            result["valid"] = False
            result["errors"].append("Calibration date not provided")
            return result

        # Parse calibration date
        try:
            cal_date = datetime.fromisoformat(calibration_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            result["valid"] = False
            result["errors"].append("Invalid calibration date format")
            return result

        # Check each equipment type
        days_since_cal = (datetime.now() - cal_date).days

        for equipment_type, req in requirements.items():
            max_days = req.get("frequency_days", 365)

            if days_since_cal > max_days:
                result["valid"] = False
                result["errors"].append(
                    f"{equipment_type} calibration expired "
                    f"({days_since_cal} days old, max {max_days} days)"
                )
            elif days_since_cal > max_days * 0.9:
                result["warnings"].append(
                    f"{equipment_type} calibration due soon "
                    f"({days_since_cal} days old, max {max_days} days)"
                )

        return result
