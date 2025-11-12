"""
Workflow Engine
Orchestrates the complete testing workflow
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Orchestrates the complete testing workflow"""

    def __init__(self, db_manager):
        """
        Initialize workflow engine

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def create_complete_workflow(
        self,
        service_request_data: Dict[str, Any],
        inspection_data: Dict[str, Any],
        protocol_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Create complete workflow from service request through protocol execution

        Args:
            service_request_data: Service request information
            inspection_data: Inspection details
            protocol_ids: List of protocol IDs to execute

        Returns:
            Workflow summary with all created IDs
        """
        workflow = {
            'created_at': datetime.now().isoformat(),
            'status': 'success',
            'entities': {}
        }

        try:
            # Step 1: Create service request
            request_id = self.db.create_service_request(service_request_data)
            workflow['entities']['service_request'] = request_id
            logger.info(f"Created service request: {request_id}")

            # Step 2: Create inspection linked to request
            inspection_data['request_id'] = request_id
            inspection_id = self.db.create_inspection(inspection_data)
            workflow['entities']['inspection'] = inspection_id
            logger.info(f"Created inspection: {inspection_id}")

            # Step 3: Create protocol executions
            execution_ids = []
            for protocol_id in protocol_ids:
                execution_data = {
                    'protocol_id': protocol_id,
                    'protocol_name': f"Protocol {protocol_id}",
                    'request_id': request_id,
                    'inspection_id': inspection_id,
                    'sample_id': inspection_data.get('sample_id'),
                    'status': 'not_started'
                }

                execution_id = self.db.create_protocol_execution(execution_data)
                execution_ids.append(execution_id)
                logger.info(f"Created protocol execution: {execution_id}")

            workflow['entities']['protocol_executions'] = execution_ids
            workflow['status'] = 'success'

        except Exception as e:
            workflow['status'] = 'error'
            workflow['error'] = str(e)
            logger.error(f"Workflow creation error: {e}")

        return workflow

    def get_workflow_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get complete status of a workflow

        Args:
            request_id: Service request ID

        Returns:
            Workflow status summary
        """
        status = {
            'request_id': request_id,
            'stages': {}
        }

        try:
            # Get service request
            requests = self.db.get_service_requests()
            request = next((r for r in requests if r['request_id'] == request_id), None)

            if request:
                status['stages']['service_request'] = {
                    'status': request['status'],
                    'created': request['requested_date']
                }

            # Get inspections
            inspections = self.db.get_inspections(request_id)
            status['stages']['inspection'] = {
                'count': len(inspections),
                'status': 'completed' if inspections else 'pending'
            }

            # Get protocol executions
            executions = self.db.execute_query(
                "SELECT * FROM protocol_executions WHERE request_id = ?",
                (request_id,)
            )

            if executions:
                status['stages']['protocol_execution'] = {
                    'total': len(executions),
                    'completed': len([e for e in executions if e['status'] == 'completed']),
                    'in_progress': len([e for e in executions if e['status'] == 'in_progress']),
                    'not_started': len([e for e in executions if e['status'] == 'not_started'])
                }

            # Calculate overall progress
            if executions:
                completed = len([e for e in executions if e['status'] == 'completed'])
                status['overall_progress'] = (completed / len(executions)) * 100
            else:
                status['overall_progress'] = 0

        except Exception as e:
            status['error'] = str(e)
            logger.error(f"Error getting workflow status: {e}")

        return status

    def advance_workflow(self, entity_type: str, entity_id: str, new_status: str) -> bool:
        """
        Advance workflow to next stage

        Args:
            entity_type: Type of entity ('service_request', 'inspection', 'execution')
            entity_id: Entity ID
            new_status: New status to set

        Returns:
            Success boolean
        """
        try:
            if entity_type == 'service_request':
                self.db.update_service_request_status(entity_id, new_status)

            elif entity_type == 'protocol_execution':
                self.db.update_protocol_status(entity_id, new_status)

                # If completing protocol, check if all protocols in request are done
                execution = self.db.execute_query(
                    "SELECT request_id FROM protocol_executions WHERE execution_id = ?",
                    (entity_id,)
                )

                if execution and new_status == 'completed':
                    request_id = execution[0]['request_id']
                    all_executions = self.db.execute_query(
                        "SELECT * FROM protocol_executions WHERE request_id = ?",
                        (request_id,)
                    )

                    if all(e['status'] == 'completed' for e in all_executions):
                        # All protocols complete - update service request
                        self.db.update_service_request_status(request_id, 'completed')
                        logger.info(f"All protocols completed for request {request_id}")

            return True

        except Exception as e:
            logger.error(f"Error advancing workflow: {e}")
            return False

    def get_next_actions(self, request_id: str) -> List[str]:
        """
        Get recommended next actions for a workflow

        Args:
            request_id: Service request ID

        Returns:
            List of recommended action descriptions
        """
        actions = []

        try:
            status = self.get_workflow_status(request_id)

            # Check service request
            if status['stages'].get('service_request', {}).get('status') == 'pending':
                actions.append("Approve service request")

            # Check inspection
            if status['stages'].get('inspection', {}).get('count', 0) == 0:
                actions.append("Complete incoming inspection")

            # Check protocols
            exec_status = status['stages'].get('protocol_execution', {})
            if exec_status.get('not_started', 0) > 0:
                actions.append(f"Start {exec_status['not_started']} pending protocol(s)")

            if exec_status.get('in_progress', 0) > 0:
                actions.append(f"Complete {exec_status['in_progress']} in-progress protocol(s)")

            if exec_status.get('completed', 0) == exec_status.get('total', 0) and exec_status.get('total', 0) > 0:
                actions.append("Generate final reports")
                actions.append("Close service request")

        except Exception as e:
            logger.error(f"Error determining next actions: {e}")

        return actions if actions else ["No pending actions"]
