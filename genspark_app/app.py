"""
PV Testing LIMS-QMS GenSpark Application

Main application file with Flask backend and GenSpark frontend integration
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
import json

from config import get_config
from database import init_db, create_all_tables
from workflows import (
    ServiceRequestWorkflow,
    IncomingInspectionWorkflow,
    EquipmentBookingWorkflow,
    ProtocolExecutionWorkflow
)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
jwt = JWTManager(app)

# Initialize database
db_engine, db_session = init_db(app.config['DATABASE_URL'], echo=app.config['DEBUG'])

# Configure logging
logging.basicConfig(
    level=getattr(logging, app.config['LOG_LEVEL']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # In production: verify credentials against database
        # Placeholder implementation
        if username and password:
            access_token = create_access_token(
                identity=username,
                expires_delta=timedelta(seconds=app.config['JWT_ACCESS_TOKEN_EXPIRES'])
            )

            return jsonify({
                'success': True,
                'access_token': access_token,
                'user': {
                    'username': username,
                    'role': 'technician'  # From database
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


# ============================================================================
# SERVICE REQUEST ENDPOINTS
# ============================================================================

@app.route('/api/service-requests', methods=['POST'])
@jwt_required()
def create_service_request():
    """Create new service request"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()

        workflow = ServiceRequestWorkflow(db_session)
        service_request = workflow.create_request(
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            customer_phone=data.get('customer_phone'),
            customer_company=data.get('customer_company'),
            customer_address=data.get('customer_address'),
            required_date=data.get('required_date'),
            priority=data.get('priority', 'normal'),
            notes=data.get('notes'),
            created_by=current_user
        )

        return jsonify({'success': True, 'data': service_request}), 201

    except Exception as e:
        logger.error(f"Failed to create service request: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/service-requests/<request_id>/protocols', methods=['POST'])
@jwt_required()
def add_protocol_to_request(request_id):
    """Add protocol to service request"""
    try:
        data = request.get_json()

        workflow = ServiceRequestWorkflow(db_session)
        # Load existing request
        # workflow.load_request(request_id)

        success = workflow.add_protocol(
            protocol_id=data.get('protocol_id'),
            protocol_name=data.get('protocol_name'),
            quantity=data.get('quantity', 1),
            unit_price=data.get('unit_price')
        )

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to add protocol'}), 400

    except Exception as e:
        logger.error(f"Failed to add protocol: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/service-requests/<request_id>/quote', methods=['GET'])
@jwt_required()
def generate_quote(request_id):
    """Generate quote for service request"""
    try:
        workflow = ServiceRequestWorkflow(db_session)
        # workflow.load_request(request_id)

        quote = workflow.calculate_quote()

        return jsonify({'success': True, 'data': quote}), 200

    except Exception as e:
        logger.error(f"Failed to generate quote: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# INCOMING INSPECTION ENDPOINTS
# ============================================================================

@app.route('/api/samples', methods=['POST'])
@jwt_required()
def receive_sample():
    """Receive and register new sample"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()

        workflow = IncomingInspectionWorkflow(db_session)
        sample = workflow.receive_sample(
            service_request_id=data.get('service_request_id'),
            manufacturer=data.get('manufacturer'),
            model=data.get('model'),
            serial_number=data.get('serial_number'),
            technology=data.get('technology'),
            rated_power=data.get('rated_power'),
            received_by=current_user
        )

        return jsonify({'success': True, 'data': sample}), 201

    except Exception as e:
        logger.error(f"Failed to receive sample: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/samples/<sample_id>/inspection', methods=['POST'])
@jwt_required()
def perform_inspection(sample_id):
    """Perform visual inspection"""
    try:
        data = request.get_json()

        workflow = IncomingInspectionWorkflow(db_session)
        # workflow.load_sample(sample_id)

        inspection_results = workflow.perform_visual_inspection(
            inspection_checklist=data.get('checklist', {})
        )

        return jsonify({'success': True, 'data': inspection_results}), 200

    except Exception as e:
        logger.error(f"Inspection failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# EQUIPMENT BOOKING ENDPOINTS
# ============================================================================

@app.route('/api/equipment/<equipment_id>/availability', methods=['GET'])
@jwt_required()
def check_equipment_availability(equipment_id):
    """Check equipment availability"""
    try:
        start_time = datetime.fromisoformat(request.args.get('start_time'))
        end_time = datetime.fromisoformat(request.args.get('end_time'))

        workflow = EquipmentBookingWorkflow(db_session)
        availability = workflow.check_availability(equipment_id, start_time, end_time)

        return jsonify({'success': True, 'data': availability}), 200

    except Exception as e:
        logger.error(f"Failed to check availability: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Create equipment booking"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()

        workflow = EquipmentBookingWorkflow(db_session)
        booking = workflow.create_booking(
            equipment_id=data.get('equipment_id'),
            test_execution_id=data.get('test_execution_id'),
            start_time=datetime.fromisoformat(data.get('start_time')),
            end_time=datetime.fromisoformat(data.get('end_time')),
            booked_by=current_user,
            purpose=data.get('purpose'),
            notes=data.get('notes')
        )

        return jsonify({'success': True, 'data': booking}), 201

    except Exception as e:
        logger.error(f"Failed to create booking: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# PROTOCOL EXECUTION ENDPOINTS
# ============================================================================

@app.route('/api/protocols', methods=['GET'])
@jwt_required()
def list_protocols():
    """List all available protocols"""
    try:
        # In production: query from database
        protocols = {
            'performance': 12,
            'degradation': 15,
            'environmental': 12,
            'mechanical': 8,
            'safety': 7
        }

        return jsonify({'success': True, 'data': protocols, 'total': 54}), 200

    except Exception as e:
        logger.error(f"Failed to list protocols: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/executions', methods=['POST'])
@jwt_required()
def create_execution():
    """Create new test execution"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()

        workflow = ProtocolExecutionWorkflow(db_session)
        execution = workflow.create_execution(
            service_request_id=data.get('service_request_id'),
            sample_id=data.get('sample_id'),
            protocol_id=data.get('protocol_id'),
            technician_id=current_user,
            input_parameters=data.get('input_parameters', {}),
            scheduled_start=datetime.fromisoformat(data['scheduled_start']) if data.get('scheduled_start') else None
        )

        return jsonify({'success': True, 'data': execution}), 201

    except Exception as e:
        logger.error(f"Failed to create execution: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/executions/<execution_id>/start', methods=['POST'])
@jwt_required()
def start_execution(execution_id):
    """Start test execution"""
    try:
        workflow = ProtocolExecutionWorkflow(db_session)
        # workflow.load_execution(execution_id)

        success = workflow.start_execution()

        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to start execution'}), 400

    except Exception as e:
        logger.error(f"Failed to start execution: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/executions/<execution_id>/status', methods=['GET'])
@jwt_required()
def get_execution_status(execution_id):
    """Get execution status"""
    try:
        workflow = ProtocolExecutionWorkflow(db_session)
        # workflow.load_execution(execution_id)

        status = workflow.get_execution_status()

        return jsonify({'success': True, 'data': status}), 200

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/executions/<execution_id>/run', methods=['POST'])
@jwt_required()
def run_full_protocol(execution_id):
    """Run complete protocol workflow"""
    try:
        workflow = ProtocolExecutionWorkflow(db_session)
        # workflow.load_execution(execution_id)

        success = workflow.run_full_protocol()

        return jsonify({
            'success': success,
            'data': workflow.get_execution_status()
        }), 200 if success else 400

    except Exception as e:
        logger.error(f"Failed to run protocol: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # In production: query from database
        stats = {
            'active_tests': 5,
            'pending_service_requests': 12,
            'samples_in_lab': 25,
            'equipment_utilization': 78.5,
            'tests_completed_today': 8,
            'tests_completed_this_month': 156
        }

        return jsonify({'success': True, 'data': stats}), 200

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# WEB ROUTES (GenSpark UI)
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/service-requests')
def service_requests_page():
    """Service requests page"""
    return render_template('service_requests.html')


@app.route('/samples')
def samples_page():
    """Samples management page"""
    return render_template('samples.html')


@app.route('/protocols')
def protocols_page():
    """Protocols selection page"""
    return render_template('protocols.html')


@app.route('/equipment')
def equipment_page():
    """Equipment management page"""
    return render_template('equipment.html')


@app.route('/executions')
def executions_page():
    """Test executions page"""
    return render_template('executions.html')


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

def init_app():
    """Initialize application"""
    logger.info("Initializing PV Testing LIMS-QMS application...")

    # Create database tables if they don't exist
    try:
        create_all_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Additional initialization here
    logger.info("Application initialized successfully")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    init_app()

    logger.info(f"Starting {app.config['APP_NAME']} v{app.config['VERSION']}")
    logger.info(f"Environment: {app.config['FLASK_ENV']}")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
