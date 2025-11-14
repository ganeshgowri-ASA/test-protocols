"""
Example: Basic Spectral Response Test

This example demonstrates how to run a simple spectral response test
using the SPEC-001 protocol.
"""

from pathlib import Path

from src.protocols import Protocol, SpectralResponseTest


def main():
    """Run a basic spectral response test"""

    print("=" * 60)
    print("SPEC-001: Basic Spectral Response Test Example")
    print("=" * 60)

    # Load protocol
    protocol_path = Path(__file__).parent.parent / "protocols" / "SPEC-001.json"
    protocol = Protocol(str(protocol_path))

    print(f"\nProtocol: {protocol.protocol_name}")
    print(f"Version: {protocol.version}")
    print(f"Standard: {protocol.standard}")

    # Configure test parameters
    test_params = {
        "wavelength": {
            "start": 400,
            "end": 1000,
            "step_size": 20
        },
        "temperature": 25,
        "bias_voltage": 0,
        "bias_light_intensity": 0,
        "integration_time": 100,
        "averaging": 3
    }

    # Sample information
    sample_info = {
        "sample_id": "EXAMPLE-CELL-001",
        "sample_type": "Solar Cell",
        "technology": "c-Si",
        "area": 2.0,
        "manufacturer": "Example Corp",
        "batch_number": "BATCH-2025-001"
    }

    # Initialize test
    output_dir = Path(__file__).parent.parent / "output"
    test = SpectralResponseTest(protocol=protocol, output_dir=str(output_dir))

    print("\n" + "-" * 60)
    print("Initializing test...")
    print("-" * 60)

    test_id = test.initialize(test_params, sample_info)
    print(f"Test ID: {test_id}")
    print(f"Sample: {sample_info['sample_id']}")
    print(f"Technology: {sample_info['technology']}")
    print(f"Area: {sample_info['area']} cm²")

    # Run measurement
    print("\n" + "-" * 60)
    print("Running spectral response measurement...")
    print("-" * 60)

    wavelength_points = len(range(
        test_params['wavelength']['start'],
        test_params['wavelength']['end'] + 1,
        test_params['wavelength']['step_size']
    ))
    print(f"Wavelength range: {test_params['wavelength']['start']}-{test_params['wavelength']['end']} nm")
    print(f"Step size: {test_params['wavelength']['step_size']} nm")
    print(f"Measurement points: {wavelength_points}")

    test.run()
    print("✓ Measurement complete")

    # Load reference calibration
    print("\n" + "-" * 60)
    print("Loading reference calibration...")
    print("-" * 60)

    test.load_reference_calibration()
    print("✓ Using default reference calibration")

    # Analyze data
    print("\n" + "-" * 60)
    print("Analyzing data...")
    print("-" * 60)

    test.analyze()
    print("✓ Analysis complete")

    # Display results
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Peak EQE: {test.results['peak_eqe']:.1f}%")
    print(f"Peak Wavelength: {test.results['peak_wavelength']:.0f} nm")
    print(f"Integrated Jsc: {test.results['integrated_jsc']:.2f} mA/cm²")

    # Run QC checks
    print("\n" + "-" * 60)
    print("Running quality control checks...")
    print("-" * 60)

    qc_results = test.run_qc()

    for check_name, result in qc_results.items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"{status:8} {check_name:25} {result['value']:8.3f} {result.get('unit', ''):4} (threshold: {result['threshold']:.3f})")

    # Export results
    print("\n" + "-" * 60)
    print("Exporting results...")
    print("-" * 60)

    exported_files = test.export_results()

    for file_type, file_path in exported_files.items():
        print(f"✓ {file_type:20} -> {file_path}")

    # Complete test
    test.complete()

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    print(f"\nResults saved to: {test.output_dir}")


if __name__ == "__main__":
    main()
