"""
Example: Database Integration

This example demonstrates how to integrate test results with the
database for tracking and analysis.
"""

from pathlib import Path

from src.database import get_session, init_db
from src.database.models import (
    Equipment,
    Protocol as ProtocolModel,
    QualityControl,
    Sample,
    TestExecution,
    TestResult,
)
from src.protocols import Protocol, SpectralResponseTest


def setup_database():
    """Initialize database and add sample data"""
    print("Initializing database...")
    init_db()
    session = get_session()

    # Add equipment
    equipment = Equipment(
        equipment_id="MONO-001",
        equipment_name="Monochromator System",
        equipment_type="optical",
        manufacturer="Acme Instruments",
        model="MONO-500",
        serial_number="SN-12345",
        status="active",
        specifications={
            "wavelength_range": [300, 1200],
            "accuracy": "±1 nm",
            "bandwidth": "10 nm"
        }
    )
    session.add(equipment)

    session.commit()
    print("✓ Database initialized")
    return session


def run_test_with_database():
    """Run test and store results in database"""

    print("=" * 60)
    print("SPEC-001: Database Integration Example")
    print("=" * 60)

    # Setup database
    session = setup_database()

    # Load protocol
    protocol_path = Path(__file__).parent.parent / "protocols" / "SPEC-001.json"
    protocol = Protocol(str(protocol_path))

    # Check if protocol exists in database, if not add it
    db_protocol = session.query(ProtocolModel).filter_by(
        protocol_id=protocol.protocol_id
    ).first()

    if not db_protocol:
        print("\nAdding protocol to database...")
        db_protocol = ProtocolModel(
            protocol_id=protocol.protocol_id,
            protocol_name=protocol.protocol_name,
            version=protocol.version,
            standard=protocol.standard,
            category=protocol.protocol_data.get("category"),
            description=protocol.protocol_data.get("description"),
            protocol_json=protocol.protocol_data,
            is_active=True
        )
        session.add(db_protocol)
        session.commit()
        print(f"✓ Protocol added: {protocol.protocol_id}")

    # Add sample to database
    sample_info = {
        "sample_id": "DB-CELL-001",
        "sample_type": "Solar Cell",
        "technology": "c-Si",
        "area": 2.0,
        "manufacturer": "DB Corp",
        "batch_number": "DB-BATCH-001"
    }

    db_sample = session.query(Sample).filter_by(
        sample_id=sample_info["sample_id"]
    ).first()

    if not db_sample:
        print("\nAdding sample to database...")
        db_sample = Sample(
            sample_id=sample_info["sample_id"],
            sample_type=sample_info["sample_type"],
            technology=sample_info["technology"],
            area=sample_info["area"],
            manufacturer=sample_info["manufacturer"],
            batch_number=sample_info["batch_number"],
            metadata=sample_info
        )
        session.add(db_sample)
        session.commit()
        print(f"✓ Sample added: {sample_info['sample_id']}")

    # Configure test parameters
    test_params = {
        "wavelength": {
            "start": 400,
            "end": 1000,
            "step_size": 50
        },
        "temperature": 25,
        "integration_time": 100,
        "averaging": 3
    }

    # Run test
    print("\n" + "-" * 60)
    print("Running spectral response test...")
    print("-" * 60)

    output_dir = Path(__file__).parent.parent / "output" / "database_example"
    test = SpectralResponseTest(protocol=protocol, output_dir=str(output_dir))
    test_id = test.initialize(test_params, sample_info)

    test.run()
    test.load_reference_calibration()
    test.analyze()
    qc_results = test.run_qc()
    test.export_results()
    test.complete()

    print("✓ Test completed")

    # Store test execution in database
    print("\n" + "-" * 60)
    print("Storing results in database...")
    print("-" * 60)

    db_test_execution = TestExecution(
        test_id=test_id,
        protocol_id=db_protocol.id,
        sample_id=db_sample.id,
        operator="Example User",
        start_time=test.start_time,
        end_time=test.end_time,
        status=test.status,
        test_parameters=test.test_params,
        results_summary={
            "peak_eqe": test.results["peak_eqe"],
            "peak_wavelength": test.results["peak_wavelength"],
            "integrated_jsc": test.results["integrated_jsc"]
        },
        qc_status="passed" if all(r["passed"] for r in qc_results.values()) else "failed"
    )
    session.add(db_test_execution)
    session.commit()
    print(f"✓ Test execution stored: {test_id}")

    # Store individual test results
    print("Storing measurement data...")
    for idx, row in test.calculated_data.iterrows():
        test_result = TestResult(
            test_execution_id=db_test_execution.id,
            measurement_type="spectral_response",
            wavelength=row["wavelength"],
            value=row["spectral_response"],
            unit="A/W"
        )
        session.add(test_result)

        test_result_eqe = TestResult(
            test_execution_id=db_test_execution.id,
            measurement_type="eqe",
            wavelength=row["wavelength"],
            value=row["external_quantum_efficiency"],
            unit="%"
        )
        session.add(test_result_eqe)

    session.commit()
    print(f"✓ {len(test.calculated_data) * 2} measurement points stored")

    # Store QC results
    print("Storing QC results...")
    for check_name, result in qc_results.items():
        qc = QualityControl(
            test_execution_id=db_test_execution.id,
            check_name=check_name,
            check_type="threshold",
            passed=result["passed"],
            measured_value=result["value"],
            threshold_value=result["threshold"],
            unit=result.get("unit"),
            action=result.get("action"),
            details=result
        )
        session.add(qc)

    session.commit()
    print(f"✓ {len(qc_results)} QC checks stored")

    # Query and display results
    print("\n" + "=" * 60)
    print("DATABASE QUERY RESULTS")
    print("=" * 60)

    # Query all tests for this sample
    sample_tests = session.query(TestExecution).filter_by(
        sample_id=db_sample.id
    ).all()

    print(f"\nTests for sample {db_sample.sample_id}:")
    for test_exec in sample_tests:
        print(f"\n  Test ID: {test_exec.test_id}")
        print(f"  Status: {test_exec.status}")
        print(f"  QC Status: {test_exec.qc_status}")
        print(f"  Peak EQE: {test_exec.results_summary.get('peak_eqe', 'N/A'):.1f}%")
        print(f"  Jsc: {test_exec.results_summary.get('integrated_jsc', 'N/A'):.2f} mA/cm²")

    # Query QC results
    print("\nQuality Control Results:")
    qc_checks = session.query(QualityControl).filter_by(
        test_execution_id=db_test_execution.id
    ).all()

    for qc in qc_checks:
        status = "✓ PASS" if qc.passed else "✗ FAIL"
        print(f"  {status:8} {qc.check_name:25} {qc.measured_value:8.3f} {qc.unit or '':4}")

    # Query spectral response data points
    sr_data_count = session.query(TestResult).filter_by(
        test_execution_id=db_test_execution.id,
        measurement_type="spectral_response"
    ).count()

    print(f"\nStored data points: {sr_data_count}")

    session.close()

    print("\n" + "=" * 60)
    print("Database integration example completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_test_with_database()
