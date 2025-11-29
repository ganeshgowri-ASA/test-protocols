"""Database seed data for test protocols and initial setup"""
from datetime import datetime
from sqlalchemy import select, func
from database.models import TestProtocol

# Comprehensive list of PV Testing Protocols based on IEC/IEEE standards
DEFAULT_PROTOCOLS = [
    # Performance Protocols
    {
        "protocol_id": "P1",
        "name": "I-V Performance Characterization",
        "category": "performance",
        "description": "Measure electrical performance under standard test conditions (STC: 1000 W/m², 25°C cell temp)",
        "standard_reference": "IEC 61215-2:2021 MQT 18",
        "estimated_duration_hours": 2.0,
        "is_active": True,
        "required_equipment": ["IV_Curve_Tester", "Solar_Simulator"],
        "input_parameters": {"irradiance": 1000, "temperature": 25, "measurement_type": "IV_curve"},
        "acceptance_criteria": {"tolerance": "±5%", "min_voc": 0, "max_isc": 1000},
    },
    {
        "protocol_id": "P2",
        "name": "P-V Curve Analysis",
        "category": "performance",
        "description": "Power-Voltage characterization to determine maximum power point (MPP)",
        "standard_reference": "IEC 61215-2:2021 MQT 14",
        "estimated_duration_hours": 2.0,
        "is_active": True,
        "required_equipment": ["IV_Curve_Tester"],
        "input_parameters": {"measurement_type": "pv_curve", "data_points": 50},
        "acceptance_criteria": {"tolerance": "±5%"},
    },
    {
        "protocol_id": "P3",
        "name": "Temperature Coefficient Measurement",
        "category": "performance",
        "description": "Measure electrical output variation with temperature",
        "standard_reference": "IEC 61215-2:2021",
        "estimated_duration_hours": 3.0,
        "is_active": True,
        "required_equipment": ["IV_Curve_Tester", "Climate_Chamber"],
        "input_parameters": {"temp_range": [-20, 65], "step": 5},
    },
    # Degradation Protocols
    {
        "protocol_id": "P4",
        "name": "Damp Heat Test (IEC 61215-2:2021)",
        "category": "degradation",
        "description": "85°C/85% RH aging for 1000 hours",
        "standard_reference": "IEC 61215-2:2021 TD 80",
        "estimated_duration_hours": 1080.0,
        "is_active": True,
        "required_equipment": ["Climate_Chamber", "IV_Curve_Tester"],
    },
    {
        "protocol_id": "P5",
        "name": "Reverse Current Overload",
        "category": "degradation",
        "description": "Bypass diode thermal test under reverse current",
        "standard_reference": "IEC 61215-2:2021 MQT 18",
        "estimated_duration_hours": 2.0,
        "is_active": True,
    },
    {
        "protocol_id": "P6",
        "name": "Impulse Voltage Test",
        "category": "safety",
        "description": "Lightning impulse withstand test (1.2/50 μs)",
        "standard_reference": "IEC 61730-2 MST 14",
        "estimated_duration_hours": 2.0,
        "is_active": True,
    },
    # Environmental Protocols
    {
        "protocol_id": "P7",
        "name": "Thermal Cycling Test",
        "category": "environmental",
        "description": "-40°C to +85°C, 200 cycles",
        "standard_reference": "IEC 61215-2:2021 TD 20",
        "estimated_duration_hours": 336.0,
        "is_active": True,
        "required_equipment": ["Climate_Chamber"],
    },
    {
        "protocol_id": "P8",
        "name": "UV Degradation Test",
        "category": "environmental",
        "description": "1000 hours UV-A exposure",
        "standard_reference": "IEC 61215-2:2021 TD 30",
        "estimated_duration_hours": 1000.0,
        "is_active": True,
    },
    {
        "protocol_id": "P9",
        "name": "Humidity Freeze Test",
        "category": "environmental",
        "description": "85°C/85% humidity followed by freeze cycles",
        "standard_reference": "IEC 61215-2:2021 TD 70",
        "estimated_duration_hours": 504.0,
        "is_active": True,
    },
    {
        "protocol_id": "P10",
        "name": "Salt Mist/Fog Corrosion Test",
        "category": "environmental",
        "description": "1000 hours salt fog exposure per ASTM B117",
        "standard_reference": "IEC 61215-2:2021 TD 50",
        "estimated_duration_hours": 1000.0,
        "is_active": True,
    },
    # Mechanical Protocols
    {
        "protocol_id": "P11",
        "name": "Static Load Test",
        "category": "mechanical",
        "description": "2400 Pa static load applied for 1 hour",
        "standard_reference": "IEC 61215-2:2021 MQT 9",
        "estimated_duration_hours": 1.5,
        "is_active": True,
    },
    {
        "protocol_id": "P12",
        "name": "Dynamic Load Test",
        "category": "mechanical",
        "description": "±2400 Pa cyclic loading, 10,000 cycles",
        "standard_reference": "IEC 61215-2:2021 MQT 10",
        "estimated_duration_hours": 20.0,
        "is_active": True,
    },
    {
        "protocol_id": "P13",
        "name": "Hail Impact Test",
        "category": "mechanical",
        "description": "25 mm hail impacts at 7.5 m/s from 6 directions",
        "standard_reference": "IEC 61215-2:2021 MQT 11",
        "estimated_duration_hours": 1.0,
        "is_active": True,
    },
    # Electrical Safety Protocols
    {
        "protocol_id": "P14",
        "name": "Leakage Current Measurement",
        "category": "safety",
        "description": "Measure leakage current under AC voltage stress",
        "standard_reference": "IEC 61730-2 MST 7",
        "estimated_duration_hours": 0.5,
        "is_active": True,
    },
    {
        "protocol_id": "P15",
        "name": "Dielectric Breakdown Test",
        "category": "safety",
        "description": "AC 1000V for 1 minute at 10 mA",
        "standard_reference": "IEC 61730-2 MST 1",
        "estimated_duration_hours": 0.5,
        "is_active": True,
    },
    {
        "protocol_id": "P16",
        "name": "Ground Continuity Test",
        "category": "safety",
        "description": "Verify ground path resistance < 100 mΩ",
        "standard_reference": "IEC 61730-2 MST 2",
        "estimated_duration_hours": 0.25,
        "is_active": True,
    },
    {
        "protocol_id": "P17",
        "name": "Hot Spot Temperature Test",
        "category": "performance",
        "description": "Measure hot spot temperature under shading",
        "standard_reference": "IEC 61215-2:2021 MQT 7",
        "estimated_duration_hours": 1.0,
        "is_active": True,
    },
    # Advanced & Defect Detection
    {
        "protocol_id": "P18",
        "name": "Electroluminescence (EL) Imaging",
        "category": "environmental",
        "description": "Detect micro-cracks, defects, and degradation patterns",
        "standard_reference": "IEC 61215-2:2021 MQT 6",
        "estimated_duration_hours": 1.0,
        "is_active": True,
    },
    {
        "protocol_id": "P19",
        "name": "Thermography Analysis",
        "category": "environmental",
        "description": "Infrared thermal imaging for hot spots and shunt paths",
        "standard_reference": "IEC 61215-2:2021",
        "estimated_duration_hours": 1.0,
        "is_active": True,
    },
    {
        "protocol_id": "P20",
        "name": "IV Curve Under Partial Shading",
        "category": "performance",
        "description": "Measure performance with various shading patterns",
        "standard_reference": "IEC 61215-2:2021",
        "estimated_duration_hours": 2.0,
        "is_active": True,
    },
]

def seed_test_protocols(db_session):
    """
    Seed the test_protocols table with standard IEC/IEEE protocols.
    Called during database initialization.
    
    Args:
        db_session: SQLAlchemy database session
    """
    try:
        # Check if protocols already seeded
        existing_count = db_session.execute(select(func.count()).select_from(TestProtocol)).scalar() or 0
        if existing_count > 0:
            print(f"✓ Test protocols already seeded ({existing_count} protocols found)")
            return
        
        # Add all default protocols
        protocols_added = []
        for protocol_data in DEFAULT_PROTOCOLS:
            protocol = TestProtocol(**protocol_data)
            db_session.add(protocol)
            protocols_added.append(protocol_data["protocol_id"])
        
        db_session.commit()
        print(f"✓ Successfully seeded {len(protocols_added)} test protocols")
        print(f"  Protocols: {', '.join(protocols_added)}")
        return len(protocols_added)
        
    except Exception as e:
        db_session.rollback()
        print(f"✗ Error seeding test protocols: {str(e)}")
        raise e
