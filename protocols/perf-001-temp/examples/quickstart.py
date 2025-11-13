#!/usr/bin/env python3
"""
PERF-001 Quick Start Example

This script demonstrates basic usage of the PERF-001 protocol
for temperature performance testing of PV modules.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from perf_001_engine import (
    PERF001Calculator, Measurement, create_sample_data
)
from validation import validate_test_data


def example_basic_usage():
    """Example 1: Basic temperature coefficient calculation"""
    print("=" * 70)
    print("Example 1: Basic Temperature Coefficient Calculation")
    print("=" * 70)

    # Create calculator
    calc = PERF001Calculator(reference_temperature=25.0)

    # Add measurements (typical mono-Si module)
    measurements = [
        Measurement(
            temperature=15.0,
            pmax=330.5,
            voc=46.8,
            isc=9.12,
            vmp=38.2,
            imp=8.65
        ),
        Measurement(
            temperature=25.0,
            pmax=320.0,
            voc=45.2,
            isc=9.18,
            vmp=37.0,
            imp=8.65
        ),
        Measurement(
            temperature=50.0,
            pmax=290.0,
            voc=41.5,
            isc=9.30,
            vmp=34.2,
            imp=8.48
        ),
        Measurement(
            temperature=75.0,
            pmax=260.5,
            voc=38.0,
            isc=9.42,
            vmp=31.5,
            imp=8.27
        ),
    ]

    calc.add_measurements(measurements)

    # Calculate temperature coefficients
    results = calc.calculate_all_coefficients()

    # Display results
    print("\nTemperature Coefficients:")
    print("-" * 70)

    coef_pmax = results['temp_coefficient_pmax']
    print(f"Pmax: {coef_pmax['value']:+.4f} {coef_pmax['unit']} "
          f"(R² = {coef_pmax['r_squared']:.4f})")

    coef_voc = results['temp_coefficient_voc']
    print(f"Voc:  {coef_voc['value']:+.4f} {coef_voc['unit']} "
          f"(R² = {coef_voc['r_squared']:.4f})")

    coef_isc = results['temp_coefficient_isc']
    print(f"Isc:  {coef_isc['value']:+.4f} {coef_isc['unit']} "
          f"(R² = {coef_isc['r_squared']:.4f})")

    print(f"\nNormalized Power at 25°C: {results['normalized_power_25C']:.2f} W")
    print()


def example_with_validation():
    """Example 2: Complete workflow with validation"""
    print("=" * 70)
    print("Example 2: Complete Workflow with Validation")
    print("=" * 70)

    # Create sample test data
    test_data = create_sample_data()

    print("\nTest Specimen:", test_data['test_specimen']['model'])
    print("Manufacturer:", test_data['test_specimen']['manufacturer'])
    print("Test Date:", test_data['metadata']['test_date'])

    # Validate data
    print("\nValidating test data...")
    report = validate_test_data(test_data)

    print(f"\nValidation Results:")
    print("-" * 70)
    print(f"Overall Status: {'✓ PASS' if report.overall_passed else '✗ FAIL'}")
    print(f"Total Checks: {report.summary['total_checks']}")
    print(f"Passed: {report.summary['passed']}")
    print(f"Failed: {report.summary['failed']}")
    print(f"Warnings: {report.summary['warnings']}")
    print(f"Errors: {report.summary['errors']}")

    # Show any warnings or errors
    warnings = report.get_warnings()
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠️  {w.message}")

    errors = report.get_errors()
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  ❌ {e.message}")

    # Display results
    results = test_data['calculated_results']
    print("\n" + "=" * 70)
    print("Calculated Temperature Coefficients:")
    print("-" * 70)
    print(f"Pmax: {results['temp_coefficient_pmax']['value']:+.4f} "
          f"{results['temp_coefficient_pmax']['unit']}")
    print(f"Voc:  {results['temp_coefficient_voc']['value']:+.4f} "
          f"{results['temp_coefficient_voc']['unit']}")
    print(f"Isc:  {results['temp_coefficient_isc']['value']:+.4f} "
          f"{results['temp_coefficient_isc']['unit']}")
    print()


def example_json_export():
    """Example 3: Export test data to JSON"""
    print("=" * 70)
    print("Example 3: Export Test Data to JSON")
    print("=" * 70)

    # Create sample test data
    test_data = create_sample_data()

    # Export to JSON file
    output_file = "perf-001-example-output.json"
    with open(output_file, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"\n✓ Test data exported to: {output_file}")
    print(f"  File size: {Path(output_file).stat().st_size} bytes")

    # Show data structure
    print("\nData Structure:")
    print("-" * 70)
    for key in test_data.keys():
        print(f"  - {key}")

    print()


def example_efficiency_calculation():
    """Example 4: Calculate module efficiency"""
    print("=" * 70)
    print("Example 4: Module Efficiency Calculation")
    print("=" * 70)

    # Module specifications
    module_area = 1.96  # m²
    irradiance = 1000   # W/m²

    # Measurements at different temperatures
    measurements = [
        Measurement(temperature=15.0, pmax=330.5, voc=46.8, isc=9.12, vmp=38.2, imp=8.65),
        Measurement(temperature=25.0, pmax=320.0, voc=45.2, isc=9.18, vmp=37.0, imp=8.65),
        Measurement(temperature=50.0, pmax=290.0, voc=41.5, isc=9.30, vmp=34.2, imp=8.48),
        Measurement(temperature=75.0, pmax=260.5, voc=38.0, isc=9.42, vmp=31.5, imp=8.27),
    ]

    print(f"\nModule Area: {module_area} m²")
    print(f"Irradiance: {irradiance} W/m²")
    print("\nEfficiency at Different Temperatures:")
    print("-" * 70)

    for m in measurements:
        efficiency = m.calculate_efficiency(module_area, irradiance)
        print(f"T = {m.temperature:5.1f}°C: "
              f"Pmax = {m.pmax:6.2f}W, "
              f"η = {efficiency:5.2f}%, "
              f"FF = {m.fill_factor:.3f}")

    # Calculate efficiency loss per degree
    temps = [m.temperature for m in measurements]
    efficiencies = [m.efficiency for m in measurements]

    import numpy as np
    z = np.polyfit(temps, efficiencies, 1)
    efficiency_loss_per_degree = z[0]

    print(f"\nEfficiency temperature coefficient: {efficiency_loss_per_degree:+.4f} %abs/°C")
    print()


def example_quality_checks():
    """Example 5: Detailed quality checks"""
    print("=" * 70)
    print("Example 5: Detailed Quality Checks")
    print("=" * 70)

    # Create calculator with test data
    calc = PERF001Calculator()
    measurements = [
        Measurement(temperature=15.0, pmax=330.5, voc=46.8, isc=9.12, vmp=38.2, imp=8.65),
        Measurement(temperature=25.0, pmax=320.0, voc=45.2, isc=9.18, vmp=37.0, imp=8.65),
        Measurement(temperature=50.0, pmax=290.0, voc=41.5, isc=9.30, vmp=34.2, imp=8.48),
        Measurement(temperature=75.0, pmax=260.5, voc=38.0, isc=9.42, vmp=31.5, imp=8.27),
    ]
    calc.add_measurements(measurements)

    # Perform quality validation
    quality = calc.validate_data_quality()

    print("\nQuality Check Results:")
    print("-" * 70)

    checks = [
        ("Data Completeness", quality['data_completeness']),
        ("Measurement Stability", quality['measurement_stability']),
        ("Linearity Check (R² > 0.95)", quality['linearity_check']),
        ("Range Validation", quality['range_validation']),
    ]

    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check_name:.<50} {status}")

    # Show warnings and errors
    if quality['warnings']:
        print("\nWarnings:")
        for warning in quality['warnings']:
            print(f"  ⚠️  {warning}")

    if quality['errors']:
        print("\nErrors:")
        for error in quality['errors']:
            print(f"  ❌ {error}")

    if not quality['warnings'] and not quality['errors']:
        print("\n✓ No warnings or errors detected")

    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print(" PERF-001 QUICK START EXAMPLES")
    print("=" * 70)
    print()

    try:
        example_basic_usage()
        input("Press Enter to continue to Example 2...")

        example_with_validation()
        input("Press Enter to continue to Example 3...")

        example_json_export()
        input("Press Enter to continue to Example 4...")

        example_efficiency_calculation()
        input("Press Enter to continue to Example 5...")

        example_quality_checks()

        print("=" * 70)
        print(" ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
