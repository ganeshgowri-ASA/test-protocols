"""
Global search and filter system
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.protocol import Protocol, ServiceRequest, Equipment


class SearchEngine:
    """Global search across all modules"""

    def __init__(self, protocols: List[Protocol], service_requests: List[ServiceRequest], equipment: List[Equipment]):
        self.protocols = protocols
        self.service_requests = service_requests
        self.equipment = equipment

    def search_all(self, query: str) -> Dict[str, List[Any]]:
        """Search across all entities"""
        query_lower = query.lower()

        results = {
            'protocols': self.search_protocols(query),
            'service_requests': self.search_service_requests(query),
            'equipment': self.search_equipment(query)
        }

        return results

    def search_protocols(self, query: str) -> List[Protocol]:
        """Search protocols"""
        query_lower = query.lower()
        results = []

        for protocol in self.protocols:
            if (query_lower in protocol.protocol_id.lower() or
                query_lower in protocol.protocol_name.lower() or
                query_lower in protocol.service_request_id.lower() or
                query_lower in protocol.sample_id.lower() or
                (protocol.operator and query_lower in protocol.operator.lower()) or
                (protocol.equipment_id and query_lower in protocol.equipment_id.lower())):
                results.append(protocol)

        return results

    def search_service_requests(self, query: str) -> List[ServiceRequest]:
        """Search service requests"""
        query_lower = query.lower()
        results = []

        for sr in self.service_requests:
            if (query_lower in sr.request_id.lower() or
                query_lower in sr.customer_name.lower() or
                query_lower in sr.sample_id.lower() or
                (sr.assigned_to and query_lower in sr.assigned_to.lower())):
                results.append(sr)

        return results

    def search_equipment(self, query: str) -> List[Equipment]:
        """Search equipment"""
        query_lower = query.lower()
        results = []

        for eq in self.equipment:
            if (query_lower in eq.equipment_id.lower() or
                query_lower in eq.equipment_name.lower() or
                query_lower in eq.equipment_type.lower()):
                results.append(eq)

        return results

    def advanced_filter(self,
                       entity_type: str,
                       filters: Dict[str, Any]) -> List[Any]:
        """Apply advanced filters"""

        if entity_type == 'protocols':
            return self._filter_protocols(filters)
        elif entity_type == 'service_requests':
            return self._filter_service_requests(filters)
        elif entity_type == 'equipment':
            return self._filter_equipment(filters)

        return []

    def _filter_protocols(self, filters: Dict[str, Any]) -> List[Protocol]:
        """Filter protocols by criteria"""
        results = self.protocols

        # Filter by status
        if 'status' in filters and filters['status']:
            results = [p for p in results if p.status.value in filters['status']]

        # Filter by protocol type
        if 'protocol_type' in filters and filters['protocol_type']:
            results = [p for p in results if p.protocol_type.value in filters['protocol_type']]

        # Filter by date range
        if 'start_date' in filters and filters['start_date']:
            results = [
                p for p in results
                if p.start_time and p.start_time.date() >= filters['start_date']
            ]

        if 'end_date' in filters and filters['end_date']:
            results = [
                p for p in results
                if p.start_time and p.start_time.date() <= filters['end_date']
            ]

        # Filter by operator
        if 'operator' in filters and filters['operator']:
            results = [
                p for p in results
                if p.operator and p.operator in filters['operator']
            ]

        # Filter by QC result
        if 'qc_result' in filters and filters['qc_result']:
            results = [p for p in results if p.qc_result.value in filters['qc_result']]

        return results

    def _filter_service_requests(self, filters: Dict[str, Any]) -> List[ServiceRequest]:
        """Filter service requests by criteria"""
        results = self.service_requests

        # Filter by status
        if 'status' in filters and filters['status']:
            results = [sr for sr in results if sr.status in filters['status']]

        # Filter by priority
        if 'priority' in filters and filters['priority']:
            results = [sr for sr in results if sr.priority in filters['priority']]

        # Filter by date range
        if 'start_date' in filters and filters['start_date']:
            results = [
                sr for sr in results
                if sr.request_date.date() >= filters['start_date']
            ]

        if 'end_date' in filters and filters['end_date']:
            results = [
                sr for sr in results
                if sr.request_date.date() <= filters['end_date']
            ]

        # Filter by customer
        if 'customer' in filters and filters['customer']:
            results = [sr for sr in results if sr.customer_name in filters['customer']]

        return results

    def _filter_equipment(self, filters: Dict[str, Any]) -> List[Equipment]:
        """Filter equipment by criteria"""
        results = self.equipment

        # Filter by status
        if 'status' in filters and filters['status']:
            results = [eq for eq in results if eq.status in filters['status']]

        # Filter by type
        if 'equipment_type' in filters and filters['equipment_type']:
            results = [eq for eq in results if eq.equipment_type in filters['equipment_type']]

        # Filter by utilization threshold
        if 'min_utilization' in filters and filters['min_utilization']:
            results = [eq for eq in results if eq.utilization_rate >= filters['min_utilization']]

        if 'max_utilization' in filters and filters['max_utilization']:
            results = [eq for eq in results if eq.utilization_rate <= filters['max_utilization']]

        # Filter by calibration status
        if 'calibration_due_soon' in filters and filters['calibration_due_soon']:
            results = [eq for eq in results if eq.calibration_due_soon]

        return results

    def get_recent_searches(self) -> List[Dict[str, str]]:
        """Get recent search history (mock implementation)"""
        return [
            {'query': 'SR-2024001', 'timestamp': datetime.now().isoformat()},
            {'query': 'failed protocols', 'timestamp': datetime.now().isoformat()},
            {'query': 'equipment calibration', 'timestamp': datetime.now().isoformat()}
        ]

    def save_search_preset(self, name: str, filters: Dict[str, Any]) -> bool:
        """Save search preset for quick access"""
        # Implementation would save to database/file
        return True

    def get_saved_presets(self) -> List[Dict[str, Any]]:
        """Get saved search presets"""
        return [
            {'name': 'Overdue Protocols', 'filters': {'status': ['in_progress']}},
            {'name': 'Failed QC', 'filters': {'qc_result': ['fail']}},
            {'name': 'High Priority Requests', 'filters': {'priority': ['high', 'urgent']}}
        ]
