"""
Analytics API - REST endpoints for dashboard data
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.data_generator import get_sample_data
from analytics.protocol_analytics import ProtocolAnalytics
from search.search_engine import SearchEngine
from notifications.notification_manager import NotificationManager


class AnalyticsAPI:
    """REST API for analytics data"""

    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)

        # Load data
        self.data = get_sample_data()
        self.protocols = self.data['protocols']
        self.service_requests = self.data['service_requests']
        self.equipment = self.data['equipment']
        self.kpi_metrics = self.data['kpi_metrics']
        self.notifications_data = self.data['notifications']

        # Initialize services
        self.analytics = ProtocolAnalytics(self.protocols)
        self.search_engine = SearchEngine(self.protocols, self.service_requests, self.equipment)
        self.notification_manager = NotificationManager()
        self.notification_manager.notifications = self.notifications_data

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register API routes"""

        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })

        @self.app.route('/api/v1/statistics', methods=['GET'])
        def get_statistics():
            """Get overall statistics"""
            stats = self.analytics.get_overall_statistics()
            return jsonify(stats)

        @self.app.route('/api/v1/protocols', methods=['GET'])
        def get_protocols():
            """Get all protocols with optional filtering"""
            status = request.args.get('status')
            protocol_type = request.args.get('type')
            limit = request.args.get('limit', type=int, default=100)

            filtered = self.protocols

            if status:
                filtered = [p for p in filtered if p.status.value == status]

            if protocol_type:
                filtered = [p for p in filtered if p.protocol_type.value == protocol_type]

            # Convert to dict
            protocols_dict = [
                {
                    'protocol_id': p.protocol_id,
                    'protocol_name': p.protocol_name,
                    'protocol_type': p.protocol_type.value,
                    'status': p.status.value,
                    'qc_result': p.qc_result.value,
                    'service_request_id': p.service_request_id,
                    'sample_id': p.sample_id,
                    'operator': p.operator,
                    'equipment_id': p.equipment_id,
                    'duration_hours': p.duration_hours,
                    'start_time': p.start_time.isoformat() if p.start_time else None,
                    'end_time': p.end_time.isoformat() if p.end_time else None,
                    'is_overdue': p.is_overdue
                }
                for p in filtered[:limit]
            ]

            return jsonify({
                'count': len(protocols_dict),
                'total': len(filtered),
                'protocols': protocols_dict
            })

        @self.app.route('/api/v1/protocols/<protocol_id>', methods=['GET'])
        def get_protocol(protocol_id):
            """Get specific protocol by ID"""
            protocol = next((p for p in self.protocols if p.protocol_id == protocol_id), None)

            if not protocol:
                return jsonify({'error': 'Protocol not found'}), 404

            return jsonify({
                'protocol_id': protocol.protocol_id,
                'protocol_name': protocol.protocol_name,
                'protocol_type': protocol.protocol_type.value,
                'status': protocol.status.value,
                'qc_result': protocol.qc_result.value,
                'service_request_id': protocol.service_request_id,
                'sample_id': protocol.sample_id,
                'operator': protocol.operator,
                'equipment_id': protocol.equipment_id,
                'duration_hours': protocol.duration_hours,
                'start_time': protocol.start_time.isoformat() if protocol.start_time else None,
                'end_time': protocol.end_time.isoformat() if protocol.end_time else None,
                'is_overdue': protocol.is_overdue,
                'nc_number': protocol.nc_number,
                'test_data': protocol.test_data
            })

        @self.app.route('/api/v1/service-requests', methods=['GET'])
        def get_service_requests():
            """Get all service requests"""
            status = request.args.get('status')
            limit = request.args.get('limit', type=int, default=100)

            filtered = self.service_requests

            if status:
                filtered = [sr for sr in filtered if sr.status == status]

            requests_dict = [
                {
                    'request_id': sr.request_id,
                    'customer_name': sr.customer_name,
                    'sample_id': sr.sample_id,
                    'request_date': sr.request_date.isoformat(),
                    'priority': sr.priority,
                    'status': sr.status,
                    'assigned_to': sr.assigned_to,
                    'required_protocols': sr.required_protocols
                }
                for sr in filtered[:limit]
            ]

            return jsonify({
                'count': len(requests_dict),
                'total': len(filtered),
                'service_requests': requests_dict
            })

        @self.app.route('/api/v1/equipment', methods=['GET'])
        def get_equipment():
            """Get all equipment"""
            status = request.args.get('status')
            limit = request.args.get('limit', type=int, default=100)

            filtered = self.equipment

            if status:
                filtered = [eq for eq in filtered if eq.status == status]

            equipment_dict = [
                {
                    'equipment_id': eq.equipment_id,
                    'equipment_name': eq.equipment_name,
                    'equipment_type': eq.equipment_type,
                    'status': eq.status,
                    'utilization_rate': eq.utilization_rate,
                    'last_calibration': eq.last_calibration.isoformat() if eq.last_calibration else None,
                    'next_calibration': eq.next_calibration.isoformat() if eq.next_calibration else None,
                    'calibration_due_soon': eq.calibration_due_soon,
                    'total_hours': eq.total_hours
                }
                for eq in filtered[:limit]
            ]

            return jsonify({
                'count': len(equipment_dict),
                'equipment': equipment_dict
            })

        @self.app.route('/api/v1/kpi/metrics', methods=['GET'])
        def get_kpi_metrics():
            """Get KPI metrics"""
            days = request.args.get('days', type=int, default=30)

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            filtered_metrics = [
                m for m in self.kpi_metrics
                if start_date <= m.date <= end_date
            ]

            metrics_dict = [
                {
                    'date': m.date.isoformat(),
                    'total_samples': m.total_samples,
                    'completed_protocols': m.completed_protocols,
                    'pending_protocols': m.pending_protocols,
                    'failed_protocols': m.failed_protocols,
                    'average_tat': m.average_tat,
                    'pass_rate': m.pass_rate,
                    'first_time_pass_rate': m.first_time_pass_rate,
                    'equipment_utilization': m.equipment_utilization,
                    'throughput_daily': m.throughput_daily
                }
                for m in filtered_metrics
            ]

            return jsonify({
                'period_days': days,
                'count': len(metrics_dict),
                'metrics': metrics_dict
            })

        @self.app.route('/api/v1/analytics/trends', methods=['GET'])
        def get_trends():
            """Get trend analysis"""
            days = request.args.get('days', type=int, default=30)
            trends = self.analytics.get_trend_analysis(days)
            return jsonify(trends)

        @self.app.route('/api/v1/analytics/protocol-types', methods=['GET'])
        def get_protocol_type_breakdown():
            """Get protocol type breakdown"""
            breakdown = self.analytics.get_protocol_type_breakdown()
            return jsonify(breakdown)

        @self.app.route('/api/v1/analytics/failure-analysis', methods=['GET'])
        def get_failure_analysis():
            """Get failure mode analysis"""
            analysis = self.analytics.get_failure_mode_analysis()
            return jsonify(analysis)

        @self.app.route('/api/v1/analytics/performance', methods=['GET'])
        def get_performance_indicators():
            """Get performance indicators"""
            indicators = self.analytics.get_performance_indicators()
            return jsonify(indicators)

        @self.app.route('/api/v1/analytics/comparative', methods=['GET'])
        def get_comparative_analysis():
            """Get comparative analysis"""
            analysis = self.analytics.get_comparative_analysis()
            return jsonify(analysis)

        @self.app.route('/api/v1/analytics/predictive', methods=['GET'])
        def get_predictive_maintenance():
            """Get predictive maintenance indicators"""
            indicators = self.analytics.get_predictive_maintenance_indicators()
            return jsonify(indicators)

        @self.app.route('/api/v1/search', methods=['GET'])
        def search():
            """Global search"""
            query = request.args.get('q', '')

            if not query:
                return jsonify({'error': 'Query parameter "q" is required'}), 400

            results = self.search_engine.search_all(query)

            # Convert to dict
            results_dict = {
                'query': query,
                'protocols': [
                    {
                        'protocol_id': p.protocol_id,
                        'protocol_name': p.protocol_name,
                        'status': p.status.value
                    }
                    for p in results['protocols'][:10]
                ],
                'service_requests': [
                    {
                        'request_id': sr.request_id,
                        'customer_name': sr.customer_name,
                        'status': sr.status
                    }
                    for sr in results['service_requests'][:10]
                ],
                'equipment': [
                    {
                        'equipment_id': eq.equipment_id,
                        'equipment_name': eq.equipment_name,
                        'status': eq.status
                    }
                    for eq in results['equipment'][:10]
                ]
            }

            return jsonify(results_dict)

        @self.app.route('/api/v1/notifications', methods=['GET'])
        def get_notifications():
            """Get notifications"""
            notification_type = request.args.get('type')
            priority = request.args.get('priority')
            unread_only = request.args.get('unread', type=bool, default=False)
            limit = request.args.get('limit', type=int, default=50)

            notifications = self.notification_manager.notifications

            if notification_type:
                notifications = [n for n in notifications if n.notification_type == notification_type]

            if priority:
                notifications = [n for n in notifications if n.priority == priority]

            if unread_only:
                notifications = [n for n in notifications if not n.read]

            notifications_dict = [
                {
                    'notification_id': n.notification_id,
                    'notification_type': n.notification_type,
                    'title': n.title,
                    'message': n.message,
                    'created_at': n.created_at.isoformat(),
                    'priority': n.priority,
                    'read': n.read,
                    'action_url': n.action_url,
                    'related_entity_id': n.related_entity_id
                }
                for n in notifications[:limit]
            ]

            return jsonify({
                'count': len(notifications_dict),
                'unread_count': self.notification_manager.get_unread_count(),
                'notifications': notifications_dict
            })

        @self.app.route('/api/v1/notifications/<notification_id>/read', methods=['POST'])
        def mark_notification_read(notification_id):
            """Mark notification as read"""
            success = self.notification_manager.mark_as_read(notification_id)

            if success:
                return jsonify({'success': True, 'message': 'Notification marked as read'})
            else:
                return jsonify({'error': 'Notification not found'}), 404

        @self.app.route('/api/v1/notifications/summary', methods=['GET'])
        def get_notification_summary():
            """Get notification summary"""
            summary = self.notification_manager.get_notification_summary()
            return jsonify(summary)

        @self.app.route('/api/v1/export/protocols', methods=['GET'])
        def export_protocols():
            """Export protocols data"""
            format_type = request.args.get('format', 'json')

            if format_type == 'csv':
                # In production, would generate actual CSV
                return "CSV export functionality - Coming soon", 200, {'Content-Type': 'text/csv'}
            else:
                return self.get_protocols()

        @self.app.route('/api/v1/export/kpi', methods=['GET'])
        def export_kpi():
            """Export KPI data"""
            format_type = request.args.get('format', 'json')

            if format_type == 'csv':
                return "CSV export functionality - Coming soon", 200, {'Content-Type': 'text/csv'}
            else:
                return self.get_kpi_metrics()

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the API server"""
        self.app.run(host=host, port=port, debug=debug)


# API documentation
API_DOCUMENTATION = """
# Test Protocols Analytics API v1.0

## Base URL
`http://localhost:5000/api/v1`

## Endpoints

### Health Check
- **GET** `/health` - Check API health status

### Statistics
- **GET** `/statistics` - Get overall protocol statistics

### Protocols
- **GET** `/protocols` - Get all protocols (supports filtering)
  - Query params: `status`, `type`, `limit`
- **GET** `/protocols/<protocol_id>` - Get specific protocol

### Service Requests
- **GET** `/service-requests` - Get all service requests
  - Query params: `status`, `limit`

### Equipment
- **GET** `/equipment` - Get all equipment
  - Query params: `status`, `limit`

### KPI Metrics
- **GET** `/kpi/metrics` - Get KPI metrics
  - Query params: `days` (default: 30)

### Analytics
- **GET** `/analytics/trends` - Get trend analysis
  - Query params: `days` (default: 30)
- **GET** `/analytics/protocol-types` - Get protocol type breakdown
- **GET** `/analytics/failure-analysis` - Get failure mode analysis
- **GET** `/analytics/performance` - Get performance indicators
- **GET** `/analytics/comparative` - Get comparative analysis
- **GET** `/analytics/predictive` - Get predictive maintenance indicators

### Search
- **GET** `/search` - Global search
  - Query params: `q` (required)

### Notifications
- **GET** `/notifications` - Get notifications
  - Query params: `type`, `priority`, `unread`, `limit`
- **POST** `/notifications/<notification_id>/read` - Mark notification as read
- **GET** `/notifications/summary` - Get notification summary

### Export
- **GET** `/export/protocols` - Export protocols
  - Query params: `format` (json, csv)
- **GET** `/export/kpi` - Export KPI data
  - Query params: `format` (json, csv)

## Rate Limiting
- 1000 requests per hour per IP

## Authentication
- Coming soon: API key-based authentication
"""


if __name__ == '__main__':
    api = AnalyticsAPI()
    print("Starting Analytics API...")
    print("API Documentation available at /api/v1/health")
    api.run(debug=True)
