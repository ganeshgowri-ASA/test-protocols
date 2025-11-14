"""
Base Protocol Class

Abstract base class for all test protocols. Provides common functionality
for loading protocol definitions, validating data, executing tests, and
generating reports.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json
import jsonschema
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
import pandas as pd


class ProtocolStep(BaseModel):
    """Model for a protocol step"""
    step_number: int
    name: str
    type: str
    description: str
    duration: Optional[Dict[str, Any]] = None
    automated: bool = False
    quality_checks: List[str] = Field(default_factory=list)


class DataField(BaseModel):
    """Model for a data field"""
    field_id: str
    name: str
    type: str
    unit: Optional[str] = None
    required: bool = False
    validation: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    step_number: Optional[int] = None


class QCCriterion(BaseModel):
    """Model for a QC criterion"""
    criterion_id: str
    name: str
    type: str
    field_id: Optional[str] = None
    condition: Dict[str, Any]
    severity: str = "warning"


class ProtocolDefinition(BaseModel):
    """Model for complete protocol definition"""
    protocol_id: str
    name: str
    category: str
    version: str
    description: Optional[str] = None
    standards: List[Dict[str, Any]] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    steps: List[ProtocolStep]
    data_fields: List[DataField]
    qc_criteria: List[QCCriterion] = Field(default_factory=list)
    analysis: Optional[Dict[str, Any]] = None
    report_template: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class TestRun(BaseModel):
    """Model for a test run instance"""
    run_id: str
    protocol_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    operator: str
    status: str = "in_progress"  # in_progress, completed, failed, cancelled
    data: Dict[str, Any] = Field(default_factory=dict)
    qc_results: List[Dict[str, Any]] = Field(default_factory=list)


class BaseProtocol(ABC):
    """
    Abstract base class for all test protocols.

    Provides common functionality including:
    - Loading and validating protocol definitions
    - Data validation against protocol schema
    - QC check execution
    - Result calculation and analysis
    - Report generation
    """

    def __init__(self, definition_path: Optional[Path] = None,
                 definition_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize protocol with definition from file or dict.

        Args:
            definition_path: Path to protocol JSON definition file
            definition_dict: Protocol definition as dictionary
        """
        if definition_path:
            self.definition = self._load_definition(definition_path)
        elif definition_dict:
            self.definition = ProtocolDefinition(**definition_dict)
        else:
            raise ValueError("Either definition_path or definition_dict must be provided")

        self.test_run: Optional[TestRun] = None
        self.validation_errors: List[str] = []

    def _load_definition(self, path: Path) -> ProtocolDefinition:
        """
        Load protocol definition from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            ProtocolDefinition instance
        """
        with open(path, 'r') as f:
            definition_dict = json.load(f)

        # Validate against JSON schema if available
        schema_path = Path(__file__).parent.parent.parent / "config" / "protocol_schema.json"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            jsonschema.validate(definition_dict, schema)

        return ProtocolDefinition(**definition_dict)

    def create_test_run(self, run_id: str, operator: str,
                       initial_data: Optional[Dict[str, Any]] = None) -> TestRun:
        """
        Create a new test run instance.

        Args:
            run_id: Unique identifier for this test run
            operator: Name of test operator
            initial_data: Initial data values

        Returns:
            TestRun instance
        """
        self.test_run = TestRun(
            run_id=run_id,
            protocol_id=self.definition.protocol_id,
            start_date=datetime.now(),
            operator=operator,
            data=initial_data or {}
        )
        return self.test_run

    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data against protocol field definitions.

        Args:
            data: Data dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        for field in self.definition.data_fields:
            if field.required and field.field_id not in data:
                errors.append(f"Required field missing: {field.name} ({field.field_id})")

        # Validate field values
        for field_id, value in data.items():
            field_def = self._get_field_definition(field_id)
            if not field_def:
                errors.append(f"Unknown field: {field_id}")
                continue

            # Type validation
            if not self._validate_field_type(value, field_def.type):
                errors.append(f"Invalid type for {field_def.name}: expected {field_def.type}")

            # Range/pattern validation
            if field_def.validation:
                validation_errors = self._validate_field_rules(value, field_def)
                errors.extend(validation_errors)

        return len(errors) == 0, errors

    def _get_field_definition(self, field_id: str) -> Optional[DataField]:
        """Get field definition by ID"""
        for field in self.definition.data_fields:
            if field.field_id == field_id:
                return field
        return None

    def _validate_field_type(self, value: Any, field_type: str) -> bool:
        """Validate value against field type"""
        type_map = {
            "number": (int, float),
            "text": str,
            "date": (str, datetime),
            "datetime": (str, datetime),
            "boolean": bool,
            "select": str,
            "multiselect": list,
            "file": str
        }

        expected_type = type_map.get(field_type)
        if expected_type is None:
            return True  # Unknown type, skip validation

        return isinstance(value, expected_type)

    def _validate_field_rules(self, value: Any, field: DataField) -> List[str]:
        """Validate value against field validation rules"""
        errors = []
        validation = field.validation

        if not validation:
            return errors

        # Min/max validation for numeric fields
        if "min" in validation and isinstance(value, (int, float)):
            if value < validation["min"]:
                errors.append(f"{field.name} must be >= {validation['min']}")

        if "max" in validation and isinstance(value, (int, float)):
            if value > validation["max"]:
                errors.append(f"{field.name} must be <= {validation['max']}")

        # Options validation for select fields
        if "options" in validation and isinstance(value, str):
            if value not in validation["options"]:
                errors.append(f"{field.name} must be one of: {', '.join(validation['options'])}")

        # Pattern validation
        if "pattern" in validation and isinstance(value, str):
            import re
            if not re.match(validation["pattern"], value):
                errors.append(f"{field.name} does not match required pattern")

        return errors

    def run_qc_checks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run quality control checks on data.

        Args:
            data: Data to check

        Returns:
            List of QC check results
        """
        results = []

        for criterion in self.definition.qc_criteria:
            result = self._evaluate_qc_criterion(criterion, data)
            results.append(result)

        return results

    def _evaluate_qc_criterion(self, criterion: QCCriterion,
                               data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single QC criterion"""
        result = {
            "criterion_id": criterion.criterion_id,
            "name": criterion.name,
            "severity": criterion.severity,
            "passed": True,
            "message": ""
        }

        if criterion.type == "threshold":
            result = self._check_threshold(criterion, data)
        elif criterion.type == "range":
            result = self._check_range(criterion, data)
        elif criterion.type == "comparison":
            result = self._check_comparison(criterion, data)
        elif criterion.type == "pattern":
            result = self._check_pattern(criterion, data)

        return result

    def _check_threshold(self, criterion: QCCriterion,
                        data: Dict[str, Any]) -> Dict[str, Any]:
        """Check threshold-based criterion"""
        field_id = criterion.field_id
        if field_id not in data:
            return {
                "criterion_id": criterion.criterion_id,
                "name": criterion.name,
                "severity": criterion.severity,
                "passed": False,
                "message": f"Missing data for {field_id}"
            }

        value = data[field_id]
        condition = criterion.condition
        operator = condition.get("operator")
        threshold = condition.get("threshold")

        passed = True
        message = ""

        if operator == "greater_than" and value <= threshold:
            passed = False
            message = f"{field_id} ({value}) must be > {threshold}"
        elif operator == "less_than" and value >= threshold:
            passed = False
            message = f"{field_id} ({value}) must be < {threshold}"
        elif operator == "degradation_less_than":
            baseline_field = condition.get("baseline_field")
            if baseline_field in data:
                baseline = data[baseline_field]
                degradation = ((baseline - value) / baseline) * 100
                if degradation > threshold:
                    passed = False
                    message = f"Degradation ({degradation:.2f}%) exceeds limit ({threshold}%)"

        return {
            "criterion_id": criterion.criterion_id,
            "name": criterion.name,
            "severity": criterion.severity,
            "passed": passed,
            "message": message or "Check passed"
        }

    def _check_range(self, criterion: QCCriterion,
                    data: Dict[str, Any]) -> Dict[str, Any]:
        """Check range-based criterion"""
        field_id = criterion.field_id
        value = data.get(field_id)
        condition = criterion.condition

        min_val = condition.get("min")
        max_val = condition.get("max")

        passed = True
        message = ""

        if value is not None:
            if min_val is not None and value < min_val:
                passed = False
                message = f"{field_id} ({value}) below minimum ({min_val})"
            elif max_val is not None and value > max_val:
                passed = False
                message = f"{field_id} ({value}) above maximum ({max_val})"

        return {
            "criterion_id": criterion.criterion_id,
            "name": criterion.name,
            "severity": criterion.severity,
            "passed": passed,
            "message": message or "Check passed"
        }

    def _check_comparison(self, criterion: QCCriterion,
                         data: Dict[str, Any]) -> Dict[str, Any]:
        """Check comparison-based criterion"""
        field_id = criterion.field_id
        value = data.get(field_id)
        condition = criterion.condition

        operator = condition.get("operator")
        expected = condition.get("value")

        passed = True
        message = ""

        if operator == "equals" and value != expected:
            passed = False
            message = f"{field_id} should be {expected}, got {value}"

        return {
            "criterion_id": criterion.criterion_id,
            "name": criterion.name,
            "severity": criterion.severity,
            "passed": passed,
            "message": message or "Check passed"
        }

    def _check_pattern(self, criterion: QCCriterion,
                      data: Dict[str, Any]) -> Dict[str, Any]:
        """Check pattern-based criterion"""
        field_id = criterion.field_id
        value = data.get(field_id)
        condition = criterion.condition

        fail_values = condition.get("fail_values", [])
        warning_values = condition.get("warning_values", [])

        passed = value not in fail_values
        message = ""

        if value in fail_values:
            message = f"{field_id} has unacceptable value: {value}"
        elif value in warning_values:
            message = f"{field_id} has warning value: {value}"

        return {
            "criterion_id": criterion.criterion_id,
            "name": criterion.name,
            "severity": criterion.severity,
            "passed": passed,
            "message": message or "Check passed"
        }

    def calculate_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate derived results from raw data.

        Args:
            data: Raw measurement data

        Returns:
            Dictionary of calculated results
        """
        results = {}

        if not self.definition.analysis:
            return results

        calculations = self.definition.analysis.get("calculations", [])

        for calc in calculations:
            try:
                # Simple formula evaluation (extend for complex cases)
                formula = calc["formula"]
                # Replace field_ids with values
                for field_id in data.keys():
                    formula = formula.replace(field_id, str(data[field_id]))

                # Safely evaluate (consider using safer eval alternatives)
                result = eval(formula)
                results[calc["name"]] = {
                    "value": result,
                    "unit": calc.get("unit", ""),
                    "description": calc.get("description", "")
                }
            except Exception as e:
                results[calc["name"]] = {
                    "value": None,
                    "error": str(e)
                }

        return results

    def get_data_as_dataframe(self) -> pd.DataFrame:
        """
        Convert test run data to pandas DataFrame.

        Returns:
            DataFrame with test data
        """
        if not self.test_run:
            return pd.DataFrame()

        return pd.DataFrame([self.test_run.data])

    @abstractmethod
    def execute_step(self, step_number: int, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute a specific protocol step.

        Args:
            step_number: Step number to execute
            **kwargs: Step-specific parameters

        Returns:
            Step execution results
        """
        pass

    @abstractmethod
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate test report.

        Args:
            output_path: Optional path to save report

        Returns:
            Report content or path to generated file
        """
        pass

    def get_next_step(self) -> Optional[ProtocolStep]:
        """Get the next step to execute"""
        if not self.test_run:
            return self.definition.steps[0] if self.definition.steps else None

        # Logic to determine next step based on current state
        # This is a simple implementation - override for complex workflows
        completed_steps = self.test_run.data.get("completed_steps", [])
        for step in self.definition.steps:
            if step.step_number not in completed_steps:
                return step

        return None  # All steps completed

    def mark_step_complete(self, step_number: int) -> None:
        """Mark a step as completed"""
        if self.test_run:
            completed = self.test_run.data.get("completed_steps", [])
            if step_number not in completed:
                completed.append(step_number)
                self.test_run.data["completed_steps"] = completed

    def get_protocol_info(self) -> Dict[str, Any]:
        """Get protocol information summary"""
        return {
            "protocol_id": self.definition.protocol_id,
            "name": self.definition.name,
            "version": self.definition.version,
            "category": self.definition.category,
            "num_steps": len(self.definition.steps),
            "num_data_fields": len(self.definition.data_fields),
            "standards": self.definition.standards,
            "metadata": self.definition.metadata
        }
