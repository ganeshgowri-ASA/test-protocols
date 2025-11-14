"""
Protocol Validator Module

Validates protocol structure and test data against protocol requirements.
"""

from typing import Dict, Any, List, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ProtocolValidator:
    """Validates protocols and test data."""

    REQUIRED_PROTOCOL_FIELDS = [
        'protocol_id',
        'name',
        'version',
        'category',
        'test_sequence'
    ]

    REQUIRED_STEP_FIELDS = [
        'step_id',
        'name',
        'type',
        'substeps'
    ]

    def validate_protocol_structure(self, protocol: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate the structure of a protocol definition.

        Args:
            protocol: Protocol dictionary to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required top-level fields
        for field in self.REQUIRED_PROTOCOL_FIELDS:
            if field not in protocol:
                errors.append(f"Missing required field: {field}")

        # Validate protocol_id format
        if 'protocol_id' in protocol:
            if not self._validate_protocol_id(protocol['protocol_id']):
                errors.append(
                    f"Invalid protocol_id format: {protocol['protocol_id']}. "
                    "Expected format: ABC-123"
                )

        # Validate version format (semver)
        if 'version' in protocol:
            if not self._validate_version(protocol['version']):
                errors.append(
                    f"Invalid version format: {protocol['version']}. "
                    "Expected format: X.Y.Z"
                )

        # Validate test sequence
        if 'test_sequence' in protocol:
            test_seq_errors = self._validate_test_sequence(protocol['test_sequence'])
            errors.extend(test_seq_errors)

        # Validate equipment requirements
        if 'equipment_requirements' in protocol:
            equip_errors = self._validate_equipment_requirements(
                protocol['equipment_requirements']
            )
            errors.extend(equip_errors)

        # Validate QC rules
        if 'qc_rules' in protocol:
            qc_errors = self._validate_qc_rules(protocol['qc_rules'])
            errors.extend(qc_errors)

        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"Protocol {protocol.get('protocol_id')} structure is valid")
        else:
            logger.error(
                f"Protocol {protocol.get('protocol_id')} has {len(errors)} validation errors"
            )

        return is_valid, errors

    def validate_test_data(
        self,
        protocol: Dict[str, Any],
        step_id: int,
        substep_id: float,
        data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate test data against protocol requirements.

        Args:
            protocol: Protocol definition
            step_id: Step ID
            substep_id: Substep ID
            data: Data to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Find the substep definition
        substep = self._find_substep(protocol, step_id, substep_id)
        if substep is None:
            errors.append(
                f"Step {step_id}.{substep_id} not found in protocol"
            )
            return False, errors

        # Get data field definitions
        data_fields = substep.get('data_fields', [])

        # Check required fields
        for field_def in data_fields:
            field_id = field_def['field_id']
            is_required = field_def.get('required', False)

            if is_required and field_id not in data:
                errors.append(
                    f"Missing required field: {field_def.get('label', field_id)}"
                )
                continue

            if field_id in data:
                # Validate field type and constraints
                field_errors = self._validate_field_data(
                    field_def,
                    data[field_id]
                )
                errors.extend(field_errors)

        # Check acceptance criteria if present
        acceptance_criteria = substep.get('acceptance_criteria', {})
        if acceptance_criteria:
            criteria_errors = self._check_acceptance_criteria(
                acceptance_criteria,
                data,
                substep
            )
            errors.extend(criteria_errors)

        is_valid = len(errors) == 0
        return is_valid, errors

    def check_qc_rules(
        self,
        protocol: Dict[str, Any],
        test_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check QC rules against test data.

        Args:
            protocol: Protocol definition
            test_data: Complete test data

        Returns:
            List of triggered QC rules with details
        """
        triggered_rules = []
        qc_rules = protocol.get('qc_rules', [])

        for rule in qc_rules:
            try:
                condition = rule['condition']
                # Evaluate condition (simplified - would need proper expression parser)
                # For now, log the rule
                triggered_rules.append({
                    'rule_id': rule['rule_id'],
                    'name': rule['name'],
                    'severity': rule['severity'],
                    'message': rule['message'],
                    'action': rule.get('action'),
                    'status': 'pending_evaluation'
                })
            except Exception as e:
                logger.error(f"Error evaluating QC rule {rule.get('rule_id')}: {e}")

        return triggered_rules

    def _validate_protocol_id(self, protocol_id: str) -> bool:
        """Validate protocol ID format."""
        pattern = r'^[A-Z]+-\d+$'
        return bool(re.match(pattern, protocol_id))

    def _validate_version(self, version: str) -> bool:
        """Validate version format (semver)."""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    def _validate_test_sequence(self, test_sequence: Dict[str, Any]) -> List[str]:
        """Validate test sequence structure."""
        errors = []

        if 'steps' not in test_sequence:
            errors.append("test_sequence missing 'steps' field")
            return errors

        steps = test_sequence['steps']
        if not isinstance(steps, list):
            errors.append("test_sequence.steps must be a list")
            return errors

        step_ids = set()
        for i, step in enumerate(steps):
            # Check required step fields
            for field in self.REQUIRED_STEP_FIELDS:
                if field not in step:
                    errors.append(f"Step {i}: missing required field '{field}'")

            # Check for duplicate step IDs
            step_id = step.get('step_id')
            if step_id in step_ids:
                errors.append(f"Duplicate step_id: {step_id}")
            step_ids.add(step_id)

            # Validate substeps
            substeps = step.get('substeps', [])
            if not isinstance(substeps, list):
                errors.append(f"Step {step_id}: substeps must be a list")
                continue

            substep_ids = set()
            for substep in substeps:
                substep_id = substep.get('substep_id')
                if substep_id in substep_ids:
                    errors.append(
                        f"Step {step_id}: duplicate substep_id {substep_id}"
                    )
                substep_ids.add(substep_id)

        return errors

    def _validate_equipment_requirements(
        self,
        equipment: List[Dict[str, Any]]
    ) -> List[str]:
        """Validate equipment requirements."""
        errors = []

        required_fields = ['equipment_id', 'name', 'specifications']

        for i, equip in enumerate(equipment):
            for field in required_fields:
                if field not in equip:
                    errors.append(
                        f"Equipment {i}: missing required field '{field}'"
                    )

        return errors

    def _validate_qc_rules(self, qc_rules: List[Dict[str, Any]]) -> List[str]:
        """Validate QC rules."""
        errors = []

        required_fields = ['rule_id', 'name', 'severity', 'condition', 'message']

        rule_ids = set()
        for rule in qc_rules:
            for field in required_fields:
                if field not in rule:
                    errors.append(
                        f"QC Rule {rule.get('rule_id', 'unknown')}: "
                        f"missing required field '{field}'"
                    )

            # Check for duplicate rule IDs
            rule_id = rule.get('rule_id')
            if rule_id in rule_ids:
                errors.append(f"Duplicate QC rule_id: {rule_id}")
            rule_ids.add(rule_id)

            # Validate severity
            severity = rule.get('severity')
            if severity not in ['info', 'warning', 'error']:
                errors.append(
                    f"QC Rule {rule_id}: invalid severity '{severity}'. "
                    "Must be 'info', 'warning', or 'error'"
                )

        return errors

    def _find_substep(
        self,
        protocol: Dict[str, Any],
        step_id: int,
        substep_id: float
    ) -> Optional[Dict[str, Any]]:
        """Find a substep in the protocol."""
        steps = protocol.get('test_sequence', {}).get('steps', [])

        for step in steps:
            if step.get('step_id') == step_id:
                for substep in step.get('substeps', []):
                    if substep.get('substep_id') == substep_id:
                        return substep

        return None

    def _validate_field_data(
        self,
        field_def: Dict[str, Any],
        value: Any
    ) -> List[str]:
        """Validate a single field's data."""
        errors = []
        field_id = field_def['field_id']
        field_type = field_def['type']

        if field_type == 'number':
            if not isinstance(value, (int, float)):
                errors.append(f"{field_id}: expected number, got {type(value).__name__}")
            else:
                # Check min/max if specified
                if 'min' in field_def and value < field_def['min']:
                    errors.append(
                        f"{field_id}: value {value} below minimum {field_def['min']}"
                    )
                if 'max' in field_def and value > field_def['max']:
                    errors.append(
                        f"{field_id}: value {value} above maximum {field_def['max']}"
                    )

        elif field_type == 'text':
            if not isinstance(value, str):
                errors.append(f"{field_id}: expected text, got {type(value).__name__}")

        elif field_type == 'boolean':
            if not isinstance(value, bool):
                errors.append(f"{field_id}: expected boolean, got {type(value).__name__}")

        elif field_type == 'datetime':
            # Would need proper datetime parsing
            if not isinstance(value, str):
                errors.append(f"{field_id}: expected datetime string")

        elif field_type == 'multiselect':
            options = field_def.get('options', [])
            if isinstance(value, list):
                for item in value:
                    if item not in options:
                        errors.append(
                            f"{field_id}: invalid option '{item}'. "
                            f"Valid options: {', '.join(options)}"
                        )
            else:
                errors.append(f"{field_id}: expected list for multiselect")

        elif field_type == 'file':
            # Basic file type validation
            if isinstance(value, str):
                file_types = field_def.get('file_types', [])
                if file_types:
                    ext = value.split('.')[-1].lower()
                    if ext not in file_types:
                        errors.append(
                            f"{field_id}: invalid file type '.{ext}'. "
                            f"Allowed: {', '.join(file_types)}"
                        )

        return errors

    def _check_acceptance_criteria(
        self,
        criteria: Dict[str, Any],
        data: Dict[str, Any],
        substep: Dict[str, Any]
    ) -> List[str]:
        """Check acceptance criteria."""
        errors = []

        for field_id, criterion in criteria.items():
            if field_id not in data:
                continue

            value = data[field_id]

            # Simple list matching (e.g., visual_defects: ["None"])
            if isinstance(criterion, list):
                if isinstance(value, list):
                    if not all(item in criterion for item in value):
                        errors.append(
                            f"Acceptance criteria failed for {field_id}: "
                            f"expected {criterion}, got {value}"
                        )
                elif value not in criterion:
                    errors.append(
                        f"Acceptance criteria failed for {field_id}: "
                        f"expected one of {criterion}, got {value}"
                    )

            # Dictionary with min/max/etc.
            elif isinstance(criterion, dict):
                if 'min' in criterion and value < criterion['min']:
                    errors.append(
                        f"Acceptance criteria failed for {field_id}: "
                        f"value {value} below minimum {criterion['min']}"
                    )
                if 'max' in criterion and value > criterion['max']:
                    errors.append(
                        f"Acceptance criteria failed for {field_id}: "
                        f"value {value} above maximum {criterion['max']}"
                    )

        return errors
