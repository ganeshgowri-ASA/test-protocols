"""
Protocol Dispatcher - Routes work orders to appropriate protocol templates.

Manages protocol execution lifecycle and coordinates with equipment and analysis stages.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.validators import ProtocolValidator

logger = logging.getLogger(__name__)


class ProtocolDispatcher:
    """Dispatcher for routing and managing protocol execution."""

    def __init__(self, data_dir: str = "data/protocols"):
        """Initialize protocol dispatcher."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Protocol catalog mapping protocol IDs to their templates
        self.protocol_catalog = self._load_protocol_catalog()

        # Active protocol executions
        self.active_executions: Dict[str, Dict[str, Any]] = {}

    def _load_protocol_catalog(self) -> Dict[str, Dict[str, Any]]:
        """
        Load protocol catalog.

        This would typically load from a database or configuration file.
        For now, returning a sample catalog of 54 protocols.
        """
        return {
            # IEC 61215 Series - Crystalline Silicon Modules
            "IEC-61215-1": {
                "protocol_id": "IEC-61215-1",
                "protocol_name": "Crystalline Silicon Terrestrial PV Modules - Design Qualification and Type Approval",
                "category": "Module Testing",
                "standard": "IEC 61215-1:2021",
                "equipment_required": ["Solar Simulator", "Thermal Chamber", "UV Test Chamber"],
                "estimated_duration_hours": 240
            },
            "IEC-61215-2": {
                "protocol_id": "IEC-61215-2",
                "protocol_name": "Crystalline Silicon Module Test Procedures",
                "category": "Module Testing",
                "standard": "IEC 61215-2:2021",
                "equipment_required": ["Solar Simulator", "Thermal Chamber"],
                "estimated_duration_hours": 160
            },

            # IEC 61730 Series - Safety
            "IEC-61730-1": {
                "protocol_id": "IEC-61730-1",
                "protocol_name": "PV Module Safety Qualification - Requirements for Construction",
                "category": "Safety Testing",
                "standard": "IEC 61730-1:2016",
                "equipment_required": ["Insulation Tester", "High Potential Tester"],
                "estimated_duration_hours": 80
            },
            "IEC-61730-2": {
                "protocol_id": "IEC-61730-2",
                "protocol_name": "PV Module Safety Qualification - Requirements for Testing",
                "category": "Safety Testing",
                "standard": "IEC 61730-2:2016",
                "equipment_required": ["Thermal Chamber", "Mechanical Load Tester"],
                "estimated_duration_hours": 120
            },

            # IEC 61646 - Thin Film Modules
            "IEC-61646": {
                "protocol_id": "IEC-61646",
                "protocol_name": "Thin-Film Terrestrial PV Modules - Design Qualification and Type Approval",
                "category": "Module Testing",
                "standard": "IEC 61646:2008",
                "equipment_required": ["Solar Simulator", "Thermal Chamber", "UV Test Chamber"],
                "estimated_duration_hours": 260
            },

            # IEC 62804 Series - PID Testing
            "IEC-62804-1": {
                "protocol_id": "IEC-62804-1",
                "protocol_name": "PV Modules - Test Methods for Detection of PID - Part 1",
                "category": "Degradation Testing",
                "standard": "IEC 62804-1:2015",
                "equipment_required": ["Thermal Chamber", "High Potential Tester", "Solar Simulator"],
                "estimated_duration_hours": 96
            },

            # IEC 61853 Series - Performance Testing
            "IEC-61853-1": {
                "protocol_id": "IEC-61853-1",
                "protocol_name": "PV Module Performance Testing - Irradiance and Temperature Performance",
                "category": "Performance Testing",
                "standard": "IEC 61853-1:2011",
                "equipment_required": ["Solar Simulator", "Thermal Chamber"],
                "estimated_duration_hours": 40
            },

            # UL Standards
            "UL-1703": {
                "protocol_id": "UL-1703",
                "protocol_name": "Flat-Plate Photovoltaic Modules and Panels",
                "category": "Safety Testing",
                "standard": "UL 1703",
                "equipment_required": ["Fire Test Equipment", "Thermal Chamber", "Mechanical Load Tester"],
                "estimated_duration_hours": 100
            },

            # ASTM Standards
            "ASTM-E948": {
                "protocol_id": "ASTM-E948",
                "protocol_name": "Electrical Performance of Non-Concentrator PV Cells Using Reference Cells",
                "category": "Performance Testing",
                "standard": "ASTM E948",
                "equipment_required": ["Solar Simulator", "Reference Cell"],
                "estimated_duration_hours": 8
            },

            # Add more protocols (showing structure for comprehensive catalog)
            "IEC-60068-2-21": {
                "protocol_id": "IEC-60068-2-21",
                "protocol_name": "Environmental Testing - Dry Heat",
                "category": "Environmental Testing",
                "standard": "IEC 60068-2-21",
                "equipment_required": ["Thermal Chamber"],
                "estimated_duration_hours": 48
            },
        }

    def dispatch_protocol(self, work_order_id: str, protocol_id: str,
                         service_request_id: str, inspection_id: str,
                         equipment_assignment: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Dispatch protocol for execution.

        Args:
            work_order_id: Work order ID
            protocol_id: Protocol to execute
            service_request_id: Originating service request
            inspection_id: Related inspection ID
            equipment_assignment: Assigned equipment details

        Returns:
            Tuple of (success, message, execution_record)
        """
        try:
            # Check if protocol exists in catalog
            if protocol_id not in self.protocol_catalog:
                return False, f"Protocol {protocol_id} not found in catalog", None

            protocol_info = self.protocol_catalog[protocol_id]

            # Generate execution ID
            execution_id = self._generate_execution_id(protocol_id)

            # Create execution record
            execution_record = {
                "execution_id": execution_id,
                "protocol_id": protocol_id,
                "protocol_name": protocol_info["protocol_name"],
                "work_order_id": work_order_id,
                "workflow_metadata": {
                    "service_request_id": service_request_id,
                    "inspection_id": inspection_id,
                    "equipment_assigned": equipment_assignment,
                    "status": "Dispatched",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                "execution_details": {
                    "start_time": None,
                    "end_time": None,
                    "technician": None,
                    "test_data": {},
                    "measurements": [],
                    "observations": []
                },
                "results": {
                    "pass_fail": None,
                    "analysis_complete": False,
                    "report_generated": False
                }
            }

            # Save execution record
            self._save_execution(execution_record)

            logger.info(f"Protocol {protocol_id} dispatched with execution ID {execution_id}")
            return True, f"Protocol dispatched with execution ID {execution_id}", execution_record

        except Exception as e:
            logger.error(f"Failed to dispatch protocol {protocol_id}: {str(e)}")
            return False, f"Error dispatching protocol: {str(e)}", None

    def start_protocol_execution(self, execution_id: str, technician: str) -> Tuple[bool, str]:
        """Start protocol execution."""
        try:
            execution = self.get_execution(execution_id)
            if not execution:
                return False, f"Execution {execution_id} not found"

            execution["workflow_metadata"]["status"] = "In Progress"
            execution["workflow_metadata"]["updated_at"] = datetime.now().isoformat()
            execution["execution_details"]["start_time"] = datetime.now().isoformat()
            execution["execution_details"]["technician"] = technician

            self._save_execution(execution)

            logger.info(f"Protocol execution {execution_id} started by {technician}")
            return True, f"Protocol execution {execution_id} started successfully"

        except Exception as e:
            logger.error(f"Failed to start execution {execution_id}: {str(e)}")
            return False, f"Error starting execution: {str(e)}"

    def complete_protocol_execution(self, execution_id: str, test_data: Dict[str, Any],
                                   pass_fail: str) -> Tuple[bool, str]:
        """Complete protocol execution with test results."""
        try:
            execution = self.get_execution(execution_id)
            if not execution:
                return False, f"Execution {execution_id} not found"

            execution["workflow_metadata"]["status"] = "Completed"
            execution["workflow_metadata"]["updated_at"] = datetime.now().isoformat()
            execution["execution_details"]["end_time"] = datetime.now().isoformat()
            execution["execution_details"]["test_data"] = test_data
            execution["results"]["pass_fail"] = pass_fail

            self._save_execution(execution)

            logger.info(f"Protocol execution {execution_id} completed with result: {pass_fail}")
            return True, f"Protocol execution completed successfully"

        except Exception as e:
            logger.error(f"Failed to complete execution {execution_id}: {str(e)}")
            return False, f"Error completing execution: {str(e)}"

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve protocol execution by ID."""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]

        execution_file = self.data_dir / f"{execution_id}.json"
        if execution_file.exists():
            with open(execution_file, 'r') as f:
                execution_data = json.load(f)
                self.active_executions[execution_id] = execution_data
                return execution_data

        return None

    def list_protocols(self, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available protocols, optionally filtered by category."""
        protocols = []

        for protocol_id, protocol_info in self.protocol_catalog.items():
            if category_filter and protocol_info["category"] != category_filter:
                continue

            protocols.append(protocol_info)

        return sorted(protocols, key=lambda x: x["protocol_id"])

    def list_executions(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List protocol executions, optionally filtered by status."""
        executions = []

        for execution_file in self.data_dir.glob("PE-*.json"):
            try:
                with open(execution_file, 'r') as f:
                    execution = json.load(f)
                    status = execution.get("workflow_metadata", {}).get("status")

                    if status_filter and status != status_filter:
                        continue

                    executions.append({
                        "execution_id": execution["execution_id"],
                        "protocol_id": execution["protocol_id"],
                        "protocol_name": execution["protocol_name"],
                        "status": status,
                        "created_at": execution["workflow_metadata"]["created_at"]
                    })
            except Exception as e:
                logger.warning(f"Failed to load execution {execution_file}: {str(e)}")

        return sorted(executions, key=lambda x: x["created_at"], reverse=True)

    def _generate_execution_id(self, protocol_id: str) -> str:
        """Generate unique execution ID."""
        timestamp = datetime.now().strftime("%Y%H%M%S")
        clean_id = protocol_id.replace("-", "").replace(".", "")
        return f"PE-{clean_id}-{timestamp}"

    def _save_execution(self, execution_data: Dict[str, Any]):
        """Save execution record to disk."""
        execution_id = execution_data["execution_id"]
        execution_file = self.data_dir / f"{execution_id}.json"

        with open(execution_file, 'w') as f:
            json.dump(execution_data, f, indent=2)

        self.active_executions[execution_id] = execution_data

    def get_protocol_details(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a protocol."""
        return self.protocol_catalog.get(protocol_id)
