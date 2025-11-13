"""
REST API Endpoints for STC-001 Protocol

This module provides comprehensive REST API endpoints for the STC-001 testing protocol.

Endpoints:
- GET    /api/v1/protocols/stc-001                    - Get protocol metadata
- GET    /api/v1/protocols/stc-001/ui                 - Get UI configuration
- POST   /api/v1/protocols/stc-001/tests              - Create new test
- GET    /api/v1/protocols/stc-001/tests              - List all tests
- GET    /api/v1/protocols/stc-001/tests/{test_id}    - Get test details
- PUT    /api/v1/protocols/stc-001/tests/{test_id}    - Update test
- DELETE /api/v1/protocols/stc-001/tests/{test_id}    - Delete test
- POST   /api/v1/protocols/stc-001/tests/{test_id}/validate-setup - Validate setup
- POST   /api/v1/protocols/stc-001/tests/{test_id}/upload-data    - Upload I-V data
- POST   /api/v1/protocols/stc-001/tests/{test_id}/execute        - Execute test
- POST   /api/v1/protocols/stc-001/tests/{test_id}/analyze        - Analyze data
- GET    /api/v1/protocols/stc-001/tests/{test_id}/graphs         - Get graphs
- GET    /api/v1/protocols/stc-001/tests/{test_id}/validate       - Validate results
- POST   /api/v1/protocols/stc-001/tests/{test_id}/review         - Review test
- GET    /api/v1/protocols/stc-001/tests/{test_id}/report         - Generate report
- GET    /api/v1/protocols/stc-001/tests/{test_id}/audit-trail    - Get audit trail
"""

from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime
from pathlib import Path
import io

# Import protocol
import sys
sys.path.append(str(Path(__file__).parent.parent))
from protocols.performance.stc_001 import STC001Protocol

# Create Blueprint
stc_001_bp = Blueprint('stc_001', __name__, url_prefix='/api/v1/protocols/stc-001')

# In-memory storage for demo (replace with database in production)
test_sessions = {}

# Configuration
UPLOAD_FOLDER = '/tmp/stc_uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx', 'xls'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_protocol_instance(test_id: str) -> Optional[STC001Protocol]:
    """Get or create protocol instance for test ID."""
    if test_id not in test_sessions:
        return None
    return test_sessions[test_id]['protocol']


def create_response(success: bool = True, data: Any = None,
                   message: str = None, status_code: int = 200) -> tuple:
    """Create standardized API response."""
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat(),
    }

    if data is not None:
        response['data'] = data

    if message is not None:
        response['message'] = message

    return jsonify(response), status_code


# ========================================
# Protocol Metadata Endpoints
# ========================================

@stc_001_bp.route('', methods=['GET'])
def get_protocol_metadata():
    """
    Get protocol metadata.

    Returns:
        200: Protocol metadata
    """
    protocol = STC001Protocol()
    metadata = protocol.get_metadata()

    return create_response(data=metadata)


@stc_001_bp.route('/ui', methods=['GET'])
def get_ui_configuration():
    """
    Get UI configuration for rendering the protocol interface.

    Returns:
        200: UI configuration JSON
    """
    protocol = STC001Protocol()
    ui_config = protocol.render_ui()

    return create_response(data=ui_config)


# ========================================
# Test Session Management Endpoints
# ========================================

@stc_001_bp.route('/tests', methods=['POST'])
def create_test():
    """
    Create a new test session.

    Request Body:
        {
            "test_id": "optional-custom-id",
            "description": "optional description"
        }

    Returns:
        201: Test session created
        400: Invalid request
    """
    data = request.get_json() or {}

    # Generate test ID if not provided
    test_id = data.get('test_id')
    if not test_id:
        test_id = f"STC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Check if test ID already exists
    if test_id in test_sessions:
        return create_response(
            success=False,
            message=f"Test ID '{test_id}' already exists",
            status_code=400
        )

    # Create protocol instance
    protocol = STC001Protocol()

    # Store session
    test_sessions[test_id] = {
        'protocol': protocol,
        'created_at': datetime.now().isoformat(),
        'description': data.get('description', ''),
        'status': 'created'
    }

    return create_response(
        data={
            'test_id': test_id,
            'created_at': test_sessions[test_id]['created_at']
        },
        message='Test session created successfully',
        status_code=201
    )


@stc_001_bp.route('/tests', methods=['GET'])
def list_tests():
    """
    List all test sessions.

    Query Parameters:
        status: Filter by status (optional)
        limit: Number of results (default: 100)
        offset: Pagination offset (default: 0)

    Returns:
        200: List of tests
    """
    status_filter = request.args.get('status')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))

    tests = []
    for test_id, session in test_sessions.items():
        if status_filter and session['status'] != status_filter:
            continue

        tests.append({
            'test_id': test_id,
            'status': session['status'],
            'created_at': session['created_at'],
            'description': session['description']
        })

    # Apply pagination
    paginated_tests = tests[offset:offset + limit]

    return create_response(data={
        'tests': paginated_tests,
        'total': len(tests),
        'limit': limit,
        'offset': offset
    })


@stc_001_bp.route('/tests/<test_id>', methods=['GET'])
def get_test(test_id: str):
    """
    Get test session details.

    Parameters:
        test_id: Test identifier

    Returns:
        200: Test details
        404: Test not found
    """
    if test_id not in test_sessions:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    protocol = test_sessions[test_id]['protocol']
    session = test_sessions[test_id]

    return create_response(data={
        'test_id': test_id,
        'status': session['status'],
        'created_at': session['created_at'],
        'description': session['description'],
        'test_data': protocol.test_data,
        'results': protocol.results,
        'parameters': protocol.parameters,
        'validation_errors': protocol.validation_errors,
        'warnings': protocol.warnings
    })


@stc_001_bp.route('/tests/<test_id>', methods=['DELETE'])
def delete_test(test_id: str):
    """
    Delete test session.

    Parameters:
        test_id: Test identifier

    Returns:
        200: Test deleted
        404: Test not found
    """
    if test_id not in test_sessions:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    del test_sessions[test_id]

    return create_response(message=f"Test '{test_id}' deleted successfully")


# ========================================
# Test Execution Endpoints
# ========================================

@stc_001_bp.route('/tests/<test_id>/validate-setup', methods=['POST'])
def validate_setup(test_id: str):
    """
    Validate test setup parameters.

    Parameters:
        test_id: Test identifier

    Request Body:
        {
            "serial_number": "PV-2025-001234",
            "manufacturer": "JinkoSolar",
            "model": "JKM400M-72H",
            "technology": "Mono c-Si",
            "rated_power": 400,
            "irradiance": 1000,
            "cell_temperature": 25,
            "equipment": {
                "solar_simulator": "SS-001",
                "iv_tracer": "IV-001",
                "temperature_sensor": "TS-001"
            }
        }

    Returns:
        200: Validation successful
        400: Validation failed
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    setup_data = request.get_json()
    if not setup_data:
        return create_response(
            success=False,
            message="Request body is required",
            status_code=400
        )

    # Validate setup
    is_valid, errors = protocol.validate_setup(setup_data)

    test_sessions[test_id]['status'] = 'setup_validated' if is_valid else 'setup_invalid'

    return create_response(
        success=is_valid,
        data={
            'valid': is_valid,
            'errors': errors,
            'warnings': protocol.warnings
        },
        message='Setup validation completed',
        status_code=200 if is_valid else 400
    )


@stc_001_bp.route('/tests/<test_id>/upload-data', methods=['POST'])
def upload_data(test_id: str):
    """
    Upload I-V curve data file.

    Parameters:
        test_id: Test identifier

    Request:
        multipart/form-data with 'file' field

    Query Parameters:
        voltage_column: Name of voltage column (optional, auto-detect if not provided)
        current_column: Name of current column (optional, auto-detect if not provided)

    Returns:
        200: File uploaded successfully
        400: Invalid file or data
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    # Check if file is in request
    if 'file' not in request.files:
        return create_response(
            success=False,
            message="No file provided",
            status_code=400
        )

    file = request.files['file']

    if file.filename == '':
        return create_response(
            success=False,
            message="No file selected",
            status_code=400
        )

    if not allowed_file(file.filename):
        return create_response(
            success=False,
            message=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            status_code=400
        )

    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, f"{test_id}_{filename}")
    file.save(filepath)

    # Get column names if provided
    voltage_col = request.args.get('voltage_column')
    current_col = request.args.get('current_column')

    # Load and validate data
    try:
        iv_data = protocol._load_iv_data_from_file(filepath, voltage_col, current_col)
        validation_result = protocol._validate_iv_data(iv_data)

        # Store file path
        protocol.test_data['iv_data_file'] = filepath

        test_sessions[test_id]['status'] = 'data_uploaded'

        return create_response(
            success=validation_result['valid'],
            data={
                'filename': filename,
                'filepath': filepath,
                'data_points': len(iv_data['voltage']),
                'validation': validation_result
            },
            message='Data uploaded and validated'
        )

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error processing file: {str(e)}",
            status_code=400
        )


@stc_001_bp.route('/tests/<test_id>/execute', methods=['POST'])
def execute_test(test_id: str):
    """
    Execute the test protocol.

    Parameters:
        test_id: Test identifier

    Request Body:
        {
            "data_source": "file",  // or "live"
            "file_path": "/path/to/file.csv"  // if data_source is "file"
        }

    Returns:
        200: Test executed successfully
        400: Execution failed
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    test_params = request.get_json() or {}

    # If no file path provided, use uploaded file
    if 'file_path' not in test_params and 'iv_data_file' in protocol.test_data:
        test_params['file_path'] = protocol.test_data['iv_data_file']
        test_params['data_source'] = 'file'

    # Execute test
    try:
        result = protocol.execute_test(test_params)

        if result['status'] == 'success':
            test_sessions[test_id]['status'] = 'executed'

            return create_response(
                data=result,
                message='Test executed successfully'
            )
        else:
            return create_response(
                success=False,
                data=result,
                message='Test execution failed',
                status_code=400
            )

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error executing test: {str(e)}",
            status_code=500
        )


@stc_001_bp.route('/tests/<test_id>/analyze', methods=['POST'])
def analyze_data(test_id: str):
    """
    Analyze test data.

    Parameters:
        test_id: Test identifier

    Returns:
        200: Analysis completed
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    if protocol.processed_data is None:
        return create_response(
            success=False,
            message="No processed data available. Execute test first.",
            status_code=400
        )

    # Perform analysis
    try:
        analysis_results = protocol.analyze_data(protocol.processed_data)

        test_sessions[test_id]['status'] = 'analyzed'

        return create_response(
            data=analysis_results,
            message='Data analysis completed'
        )

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error analyzing data: {str(e)}",
            status_code=500
        )


@stc_001_bp.route('/tests/<test_id>/graphs', methods=['GET'])
def get_graphs(test_id: str):
    """
    Get interactive graphs.

    Parameters:
        test_id: Test identifier

    Query Parameters:
        graph_type: Specific graph to retrieve (optional)
                   Options: iv_pv_curves, fill_factor, parameter_trends,
                           uncertainty_budget, temperature_coefficients

    Returns:
        200: Graph data (Plotly JSON)
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    if protocol.processed_data is None:
        return create_response(
            success=False,
            message="No data available for graphs. Execute test first.",
            status_code=400
        )

    graph_type = request.args.get('graph_type')

    try:
        graphs = protocol.generate_graphs(protocol.processed_data)

        # Return specific graph if requested
        if graph_type:
            if graph_type in graphs:
                return create_response(data=graphs[graph_type])
            else:
                return create_response(
                    success=False,
                    message=f"Graph type '{graph_type}' not found",
                    status_code=404
                )

        # Return all graphs
        return create_response(data=graphs)

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error generating graphs: {str(e)}",
            status_code=500
        )


@stc_001_bp.route('/tests/<test_id>/validate', methods=['GET'])
def validate_results(test_id: str):
    """
    Validate test results against acceptance criteria.

    Parameters:
        test_id: Test identifier

    Returns:
        200: Validation results
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    if not protocol.parameters:
        return create_response(
            success=False,
            message="No parameters available. Execute test first.",
            status_code=400
        )

    try:
        validation = protocol.validate_results(protocol.parameters)

        test_sessions[test_id]['status'] = 'validated'

        return create_response(data=validation)

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error validating results: {str(e)}",
            status_code=500
        )


@stc_001_bp.route('/tests/<test_id>/uncertainty', methods=['GET'])
def calculate_uncertainty(test_id: str):
    """
    Calculate measurement uncertainty.

    Parameters:
        test_id: Test identifier

    Returns:
        200: Uncertainty analysis
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    if not protocol.parameters:
        return create_response(
            success=False,
            message="No parameters available. Execute test first.",
            status_code=400
        )

    try:
        uncertainty = protocol.calculate_uncertainty(protocol.parameters)

        return create_response(data=uncertainty)

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error calculating uncertainty: {str(e)}",
            status_code=500
        )


@stc_001_bp.route('/tests/<test_id>/review', methods=['POST'])
def review_test(test_id: str):
    """
    Review and approve/reject test.

    Parameters:
        test_id: Test identifier

    Request Body:
        {
            "reviewer_id": "user123",
            "action": "approve" or "reject",
            "comments": "Review comments"
        }

    Returns:
        200: Review recorded
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    review_data = request.get_json()

    if not review_data or 'action' not in review_data:
        return create_response(
            success=False,
            message="Review action is required",
            status_code=400
        )

    action = review_data['action']
    if action not in ['approve', 'reject']:
        return create_response(
            success=False,
            message="Action must be 'approve' or 'reject'",
            status_code=400
        )

    # Log review action
    protocol.log_action(
        action=f'test_{action}',
        data=review_data,
        user_id=review_data.get('reviewer_id')
    )

    test_sessions[test_id]['status'] = f'{action}d'
    test_sessions[test_id]['review'] = {
        'reviewer_id': review_data.get('reviewer_id'),
        'action': action,
        'comments': review_data.get('comments', ''),
        'timestamp': datetime.now().isoformat()
    }

    return create_response(
        data=test_sessions[test_id]['review'],
        message=f'Test {action}d successfully'
    )


@stc_001_bp.route('/tests/<test_id>/report', methods=['GET'])
def generate_report(test_id: str):
    """
    Generate test report.

    Parameters:
        test_id: Test identifier

    Query Parameters:
        format: Report format (pdf, excel, json) - default: pdf

    Returns:
        200: Report file
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    report_format = request.args.get('format', 'pdf')

    if report_format not in ['pdf', 'excel', 'json']:
        return create_response(
            success=False,
            message="Invalid format. Must be 'pdf', 'excel', or 'json'",
            status_code=400
        )

    try:
        report_bytes = protocol.generate_report(format=report_format)

        # Determine MIME type and extension
        mime_types = {
            'pdf': 'application/pdf',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json'
        }
        extensions = {
            'pdf': 'pdf',
            'excel': 'xlsx',
            'json': 'json'
        }

        filename = f"{test_id}_report.{extensions[report_format]}"

        return send_file(
            io.BytesIO(report_bytes),
            mimetype=mime_types[report_format],
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error generating report: {str(e)}",
            status_code=500
        )


@stc_001_bp.route('/tests/<test_id>/audit-trail', methods=['GET'])
def get_audit_trail(test_id: str):
    """
    Get complete audit trail for test.

    Parameters:
        test_id: Test identifier

    Returns:
        200: Audit trail
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    audit_trail = protocol.get_audit_trail()

    return create_response(data={
        'test_id': test_id,
        'audit_trail': audit_trail,
        'total_entries': len(audit_trail)
    })


@stc_001_bp.route('/tests/<test_id>/state', methods=['GET'])
def get_state(test_id: str):
    """
    Get current protocol state.

    Parameters:
        test_id: Test identifier

    Returns:
        200: Protocol state
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    state = protocol.save_state()

    return create_response(data=state)


@stc_001_bp.route('/tests/<test_id>/state', methods=['POST'])
def load_state(test_id: str):
    """
    Load protocol state from saved data.

    Parameters:
        test_id: Test identifier

    Request Body:
        Protocol state JSON

    Returns:
        200: State loaded
        404: Test not found
    """
    protocol = get_protocol_instance(test_id)
    if not protocol:
        return create_response(
            success=False,
            message=f"Test '{test_id}' not found",
            status_code=404
        )

    state_data = request.get_json()

    if not state_data:
        return create_response(
            success=False,
            message="State data is required",
            status_code=400
        )

    try:
        protocol.load_state(state_data)

        return create_response(message='State loaded successfully')

    except Exception as e:
        return create_response(
            success=False,
            message=f"Error loading state: {str(e)}",
            status_code=500
        )


# ========================================
# Utility Endpoints
# ========================================

@stc_001_bp.route('/equipment', methods=['GET'])
def get_equipment_list():
    """
    Get list of available equipment.

    Query Parameters:
        type: Equipment type filter (optional)

    Returns:
        200: Equipment list
    """
    equipment_type = request.args.get('type')

    # This would query actual database
    equipment = {
        'solar_simulators': [
            {'id': 'SS-001', 'name': 'Solar Simulator A', 'status': 'active', 'calibration_valid': True},
            {'id': 'SS-002', 'name': 'Solar Simulator B', 'status': 'active', 'calibration_valid': True}
        ],
        'iv_tracers': [
            {'id': 'IV-001', 'name': 'I-V Tracer A', 'status': 'active', 'calibration_valid': True},
            {'id': 'IV-002', 'name': 'I-V Tracer B', 'status': 'active', 'calibration_valid': False}
        ],
        'temperature_sensors': [
            {'id': 'TS-001', 'name': 'Thermocouple A', 'status': 'active', 'calibration_valid': True}
        ]
    }

    if equipment_type:
        equipment = {equipment_type: equipment.get(equipment_type, [])}

    return create_response(data=equipment)


@stc_001_bp.route('/manufacturers', methods=['GET'])
def get_manufacturers():
    """
    Get list of module manufacturers.

    Returns:
        200: Manufacturer list
    """
    manufacturers = [
        'JinkoSolar', 'Trina Solar', 'LONGi Solar', 'JA Solar',
        'Canadian Solar', 'Hanwha Q CELLS', 'First Solar', 'SunPower',
        'REC Solar', 'Risen Energy', 'Other'
    ]

    return create_response(data={'manufacturers': manufacturers})


# ========================================
# Error Handlers
# ========================================

@stc_001_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return create_response(
        success=False,
        message="Resource not found",
        status_code=404
    )


@stc_001_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return create_response(
        success=False,
        message="Internal server error",
        status_code=500
    )


# ========================================
# Health Check
# ========================================

@stc_001_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        200: Service healthy
    """
    return create_response(data={
        'status': 'healthy',
        'protocol': 'STC-001',
        'version': '2.0',
        'active_tests': len(test_sessions)
    })
