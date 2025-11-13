"""
Base protocol class for all PV testing protocols
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel, Field


class ProtocolMetadata(BaseModel):
    """Metadata for a test protocol"""
    protocol_id: str
    name: str
    version: str
    standard: str
    category: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TestConditions(BaseModel):
    """Base test conditions"""
    temperature: float = Field(..., description="Temperature in °C")
    timestamp: datetime = Field(default_factory=datetime.now)
    operator: Optional[str] = None
    equipment_id: Optional[str] = None
    notes: Optional[str] = None


class BaseProtocol(ABC):
    """
    Abstract base class for all PV testing protocols

    Provides common functionality for:
    - Loading JSON schemas
    - Data validation
    - Result calculation
    - Report generation
    - Database integration
    """

    def __init__(self, protocol_id: str, schema_path: Optional[Path] = None):
        self.protocol_id = protocol_id
        self.schema_path = schema_path
        self.schema = self._load_schema() if schema_path else None
        self.metadata = self._get_metadata()
        self.results: Dict[str, Any] = {}

    @abstractmethod
    def _get_metadata(self) -> ProtocolMetadata:
        """Return protocol metadata"""
        pass

    @abstractmethod
    def validate_inputs(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate input data against protocol requirements

        Returns:
            (is_valid, error_messages)
        """
        pass

    @abstractmethod
    def calculate_results(self, measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate test results from measurements

        Args:
            measurements: Raw measurement data

        Returns:
            Calculated results
        """
        pass

    @abstractmethod
    def generate_visualizations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Plotly visualizations for the test data

        Returns:
            Dictionary of plot objects
        """
        pass

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file"""
        if not self.schema_path or not self.schema_path.exists():
            return {}

        with open(self.schema_path, 'r') as f:
            return json.load(f)

    def save_results(self, output_path: Path, format: str = 'json'):
        """
        Save test results to file

        Args:
            output_path: Path to save results
            format: Output format (json, csv, excel)
        """
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
        elif format == 'csv':
            df = pd.DataFrame([self.results])
            df.to_csv(output_path, index=False)
        elif format == 'excel':
            df = pd.DataFrame([self.results])
            df.to_excel(output_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert protocol instance to dictionary"""
        return {
            'protocol_id': self.protocol_id,
            'metadata': self.metadata.model_dump(),
            'results': self.results,
        }

    def generate_report(self) -> str:
        """
        Generate a text report of the test results

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append(f"Protocol: {self.metadata.name}")
        report.append(f"Standard: {self.metadata.standard}")
        report.append(f"Version: {self.metadata.version}")
        report.append("=" * 80)
        report.append("")

        if self.results:
            report.append("TEST RESULTS:")
            report.append("-" * 80)
            for key, value in self.results.items():
                report.append(f"  {key}: {value}")
        else:
            report.append("No results available")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)
