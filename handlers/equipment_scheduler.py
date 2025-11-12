"""
Equipment Planning and Scheduling Handler - Resource allocation optimizer.

Manages equipment allocation, scheduling, and optimization for protocol execution.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.validators import EquipmentPlanningValidator

logger = logging.getLogger(__name__)


class EquipmentScheduler:
    """Handler for equipment planning, allocation, and scheduling."""

    def __init__(self, data_dir: str = "data/equipment"):
        """Initialize equipment scheduler."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.validator = EquipmentPlanningValidator()
        self.equipment_catalog: Dict[str, Dict[str, Any]] = {}
        self.planning_records: Dict[str, Dict[str, Any]] = {}

        self._load_equipment_catalog()

    def _load_equipment_catalog(self):
        """Load equipment catalog from disk."""
        catalog_file = self.data_dir / "equipment_catalog.json"
        if catalog_file.exists():
            with open(catalog_file, 'r') as f:
                self.equipment_catalog = json.load(f)
        else:
            # Create default catalog with common equipment
            self.equipment_catalog = self._create_default_catalog()
            self._save_equipment_catalog()

    def _create_default_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Create default equipment catalog."""
        return {
            "SOLAR-SIM-001": {
                "equipment_id": "SOLAR-SIM-001",
                "equipment_type": "Solar Simulator",
                "manufacturer": "Newport",
                "model": "VeraSol-2",
                "status": "Available",
                "protocol_compatibility": ["IEC-61215", "IEC-61646", "ASTM-E948"],
                "capabilities": {
                    "sample_capacity": 4,
                    "irradiance": "1000 W/m2"
                },
                "calibration_info": {
                    "last_calibration_date": "2025-01-15",
                    "next_calibration_due": "2025-07-15",
                    "is_calibrated": True
                }
            },
            "THERMAL-CHAMBER-001": {
                "equipment_id": "THERMAL-CHAMBER-001",
                "equipment_type": "Thermal Chamber",
                "manufacturer": "Espec",
                "model": "TSA-71",
                "status": "Available",
                "protocol_compatibility": ["IEC-61215", "IEC-61730", "IEC-62804"],
                "capabilities": {
                    "temperature_range": {
                        "min_celsius": -40,
                        "max_celsius": 150
                    },
                    "sample_capacity": 8
                },
                "calibration_info": {
                    "last_calibration_date": "2025-01-10",
                    "next_calibration_due": "2025-07-10",
                    "is_calibrated": True
                }
            },
            "UV-CHAMBER-001": {
                "equipment_id": "UV-CHAMBER-001",
                "equipment_type": "UV Test Chamber",
                "manufacturer": "Atlas",
                "model": "Ci4000",
                "status": "Available",
                "protocol_compatibility": ["IEC-61215", "IEC-61730"],
                "capabilities": {
                    "sample_capacity": 6
                },
                "calibration_info": {
                    "last_calibration_date": "2025-02-01",
                    "next_calibration_due": "2025-08-01",
                    "is_calibrated": True
                }
            }
        }

    def create_equipment_plan(self, work_order_id: str, service_request_id: str,
                             protocols_to_execute: List[Dict[str, Any]]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Create equipment planning and allocation for work order.

        Args:
            work_order_id: Work order ID
            service_request_id: Service request ID
            protocols_to_execute: List of protocols needing equipment

        Returns:
            Tuple of (success, message, planning_object)
        """
        try:
            planning_id = self.validator.generate_equipment_id().replace("EQ-", "EP-")

            # Allocate equipment for each protocol
            equipment_allocation = self._allocate_equipment(protocols_to_execute)

            # Create schedule
            schedule = self._create_schedule(equipment_allocation, protocols_to_execute)

            # Resource optimization
            optimization = self._optimize_resources(equipment_allocation, protocols_to_execute)

            planning_data = {
                "planning_id": planning_id,
                "work_order_id": work_order_id,
                "service_request_id": service_request_id,
                "protocols_to_execute": protocols_to_execute,
                "equipment_allocation": equipment_allocation,
                "schedule": schedule,
                "resource_optimization": optimization,
                "workflow_metadata": {
                    "status": "Draft",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                "notes": []
            }

            # Save planning
            self._save_planning(planning_data)

            logger.info(f"Equipment plan {planning_id} created for work order {work_order_id}")
            return True, f"Equipment plan {planning_id} created successfully", planning_data

        except Exception as e:
            logger.error(f"Failed to create equipment plan: {str(e)}")
            return False, f"Error creating equipment plan: {str(e)}", None

    def _allocate_equipment(self, protocols: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Allocate equipment for protocols."""
        allocation = []

        for protocol in protocols:
            protocol_id = protocol["protocol_id"]
            equipment_required = protocol.get("equipment_required", [])

            # Find compatible equipment
            for eq_type in equipment_required:
                available_eq = self._find_available_equipment(eq_type, protocol_id)
                if available_eq:
                    allocation.append({
                        **available_eq,
                        "allocated_for_protocols": [protocol_id]
                    })

        return allocation

    def _find_available_equipment(self, equipment_type: str, protocol_id: str) -> Optional[Dict[str, Any]]:
        """Find available equipment matching type and protocol compatibility."""
        for eq_id, equipment in self.equipment_catalog.items():
            if (equipment["equipment_type"] == equipment_type and
                equipment["status"] == "Available" and
                equipment.get("calibration_info", {}).get("is_calibrated", False)):

                # Check protocol compatibility
                compatible_protocols = equipment.get("protocol_compatibility", [])
                if any(protocol_id.startswith(cp) for cp in compatible_protocols):
                    return equipment

        return None

    def _create_schedule(self, equipment_allocation: List[Dict[str, Any]],
                        protocols: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create execution schedule."""
        # Calculate total duration
        total_duration_hours = sum(p.get("estimated_duration_hours", 8) for p in protocols)

        # Schedule start time (next business day at 8 AM)
        now = datetime.now()
        scheduled_start = now + timedelta(days=1)
        scheduled_start = scheduled_start.replace(hour=8, minute=0, second=0, microsecond=0)

        estimated_completion = scheduled_start + timedelta(hours=total_duration_hours)

        return {
            "scheduled_start": scheduled_start.isoformat(),
            "estimated_completion": estimated_completion.isoformat(),
            "buffer_time_hours": total_duration_hours * 0.2,  # 20% buffer
            "shift_assignment": "Day Shift",
            "assigned_technicians": []
        }

    def _optimize_resources(self, equipment_allocation: List[Dict[str, Any]],
                           protocols: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform resource optimization analysis."""
        optimization_score = 85.0  # Simple scoring for now

        # Detect conflicts
        conflicts = []
        if len(equipment_allocation) < len([e for p in protocols for e in p.get("equipment_required", [])]):
            conflicts.append({
                "conflict_type": "Equipment Unavailable",
                "description": "Not all required equipment could be allocated",
                "resolution": "Contact lab manager for equipment availability"
            })

        # Find parallel execution opportunities
        parallel_opportunities = []
        if len(protocols) > 1:
            parallel_opportunities.append("Multiple protocols can be executed in parallel with available equipment")

        return {
            "optimization_score": optimization_score,
            "optimization_method": "Auto - Load Balancing",
            "conflicts_detected": conflicts,
            "parallel_execution_opportunities": parallel_opportunities
        }

    def approve_equipment_plan(self, planning_id: str, approved_by: str) -> Tuple[bool, str]:
        """Approve equipment plan and reserve equipment."""
        try:
            planning = self.get_equipment_plan(planning_id)
            if not planning:
                return False, f"Equipment plan {planning_id} not found"

            # Update status
            planning["workflow_metadata"]["status"] = "Approved"
            planning["workflow_metadata"]["approved_by"] = approved_by
            planning["workflow_metadata"]["approved_at"] = datetime.now().isoformat()
            planning["workflow_metadata"]["updated_at"] = datetime.now().isoformat()

            # Reserve equipment
            for equipment in planning["equipment_allocation"]:
                eq_id = equipment["equipment_id"]
                if eq_id in self.equipment_catalog:
                    self.equipment_catalog[eq_id]["status"] = "Reserved"

            self._save_equipment_catalog()
            self._save_planning(planning)

            logger.info(f"Equipment plan {planning_id} approved by {approved_by}")
            return True, f"Equipment plan {planning_id} approved and equipment reserved"

        except Exception as e:
            logger.error(f"Failed to approve equipment plan {planning_id}: {str(e)}")
            return False, f"Error approving equipment plan: {str(e)}"

    def get_equipment_plan(self, planning_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve equipment plan by ID."""
        if planning_id in self.planning_records:
            return self.planning_records[planning_id]

        planning_file = self.data_dir / f"{planning_id}.json"
        if planning_file.exists():
            with open(planning_file, 'r') as f:
                planning_data = json.load(f)
                self.planning_records[planning_id] = planning_data
                return planning_data

        return None

    def list_equipment(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all equipment, optionally filtered by status."""
        equipment_list = []

        for eq_id, equipment in self.equipment_catalog.items():
            if status_filter and equipment["status"] != status_filter:
                continue

            equipment_list.append({
                "equipment_id": eq_id,
                "equipment_type": equipment["equipment_type"],
                "manufacturer": equipment["manufacturer"],
                "model": equipment["model"],
                "status": equipment["status"],
                "is_calibrated": equipment.get("calibration_info", {}).get("is_calibrated", False)
            })

        return equipment_list

    def _save_planning(self, planning_data: Dict[str, Any]):
        """Save planning to disk."""
        planning_id = planning_data["planning_id"]
        planning_file = self.data_dir / f"{planning_id}.json"

        with open(planning_file, 'w') as f:
            json.dump(planning_data, f, indent=2)

        self.planning_records[planning_id] = planning_data

    def _save_equipment_catalog(self):
        """Save equipment catalog to disk."""
        catalog_file = self.data_dir / "equipment_catalog.json"
        with open(catalog_file, 'w') as f:
            json.dump(self.equipment_catalog, f, indent=2)
