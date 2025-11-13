"""Core protocol execution engine."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import importlib.util

from src.models.database import get_db
from src.models.protocol import Protocol, TestExecution, TestExecutionStatus
from src.core.schema_validator import SchemaValidator


class ProtocolEngine:
    """Engine for loading and executing protocol implementations."""

    def __init__(self, protocol_base_path: Optional[Path] = None):
        """
        Initialize protocol engine.

        Args:
            protocol_base_path: Base path for protocol directories
        """
        if protocol_base_path is None:
            protocol_base_path = Path(__file__).parent.parent.parent / "protocols"
        self.protocol_base_path = Path(protocol_base_path)

    def load_protocol_schema(self, pid: str) -> Dict[str, Any]:
        """
        Load protocol schema from file system.

        Args:
            pid: Protocol ID (e.g., 'pid-001')

        Returns:
            Protocol schema dictionary

        Raises:
            FileNotFoundError: If schema file doesn't exist
        """
        schema_path = self.protocol_base_path / pid / "schema.json"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found for protocol {pid}")

        with open(schema_path) as f:
            return json.load(f)

    def load_protocol_implementation(self, pid: str):
        """
        Dynamically load protocol implementation module.

        Args:
            pid: Protocol ID (e.g., 'pid-001')

        Returns:
            Protocol implementation module

        Raises:
            ImportError: If implementation module cannot be loaded
        """
        impl_path = self.protocol_base_path / pid / "implementation.py"
        if not impl_path.exists():
            raise ImportError(f"Implementation not found for protocol {pid}")

        # Dynamic module loading
        spec = importlib.util.spec_from_file_location(f"protocols.{pid}.implementation", impl_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load implementation for protocol {pid}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_protocol_from_db(self, pid: str) -> Optional[Protocol]:
        """
        Get protocol from database.

        Args:
            pid: Protocol ID

        Returns:
            Protocol instance or None if not found
        """
        with get_db() as db:
            protocol = db.query(Protocol).filter_by(pid=pid).first()
            if protocol:
                # Detach from session
                db.expunge(protocol)
            return protocol

    def create_test_execution(
        self, pid: str, parameters: Dict[str, Any]
    ) -> TestExecution:
        """
        Create a new test execution.

        Args:
            pid: Protocol ID
            parameters: Test parameters

        Returns:
            TestExecution instance

        Raises:
            ValueError: If protocol not found or parameters invalid
        """
        # Load protocol
        protocol = self.get_protocol_from_db(pid)
        if not protocol:
            raise ValueError(f"Protocol {pid} not found in database")

        # Validate parameters
        validator = SchemaValidator(protocol.schema)
        is_valid, errors = validator.validate_parameters(parameters)
        if not is_valid:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        # Load implementation
        impl_module = self.load_protocol_implementation(pid)

        # Get protocol class (assumes class name follows pattern)
        protocol_class_name = self._get_protocol_class_name(pid)
        if not hasattr(impl_module, protocol_class_name):
            raise ImportError(f"Protocol class {protocol_class_name} not found in implementation")

        protocol_impl = getattr(impl_module, protocol_class_name)()

        # Create test execution
        test_execution = protocol_impl.create_test_execution(protocol.id, parameters)

        # Save to database
        with get_db() as db:
            db.add(test_execution)
            db.commit()
            db.refresh(test_execution)
            db.expunge(test_execution)

        return test_execution

    def get_test_execution(self, test_id: str) -> Optional[TestExecution]:
        """
        Get test execution from database.

        Args:
            test_id: Test execution ID

        Returns:
            TestExecution instance or None
        """
        with get_db() as db:
            test_exec = db.query(TestExecution).filter_by(id=test_id).first()
            if test_exec:
                db.expunge(test_exec)
            return test_exec

    def update_test_execution_status(
        self, test_id: str, status: TestExecutionStatus, **kwargs
    ) -> TestExecution:
        """
        Update test execution status.

        Args:
            test_id: Test execution ID
            status: New status
            **kwargs: Additional fields to update

        Returns:
            Updated TestExecution instance
        """
        with get_db() as db:
            test_exec = db.query(TestExecution).filter_by(id=test_id).first()
            if not test_exec:
                raise ValueError(f"Test execution {test_id} not found")

            test_exec.status = status
            for key, value in kwargs.items():
                if hasattr(test_exec, key):
                    setattr(test_exec, key, value)

            db.commit()
            db.refresh(test_exec)
            db.expunge(test_exec)
            return test_exec

    def get_all_protocols(self) -> List[Protocol]:
        """
        Get all protocols from database.

        Returns:
            List of Protocol instances
        """
        with get_db() as db:
            protocols = db.query(Protocol).all()
            # Detach from session
            for protocol in protocols:
                db.expunge(protocol)
            return protocols

    def _get_protocol_class_name(self, pid: str) -> str:
        """
        Get protocol class name from PID.

        Args:
            pid: Protocol ID (e.g., 'pid-001')

        Returns:
            Protocol class name (e.g., 'PID001Protocol')
        """
        # Convert pid-001 to PID001Protocol
        parts = pid.upper().replace("-", "")
        return f"{parts}Protocol"

    def get_protocol_metadata(self, pid: str) -> Dict[str, Any]:
        """
        Get protocol metadata.

        Args:
            pid: Protocol ID

        Returns:
            Protocol metadata dictionary
        """
        protocol = self.get_protocol_from_db(pid)
        if not protocol:
            raise ValueError(f"Protocol {pid} not found")

        return {
            "pid": protocol.pid,
            "name": protocol.name,
            "version": protocol.version,
            "standard": protocol.standard,
            "description": protocol.description,
            "status": protocol.status.value,
            "created_at": protocol.created_at.isoformat() if protocol.created_at else None,
            "metadata": protocol.schema.get("metadata", {}),
        }
