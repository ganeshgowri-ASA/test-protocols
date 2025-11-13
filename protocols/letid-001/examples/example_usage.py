"""
Example usage of LETID-001 protocol validation and processing.

This script demonstrates how to:
1. Load sample test data
2. Validate the data
3. Process and analyze the data
4. Generate reports
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from validation import LETID001Validator
from processor import LETID001Processor


def main():
    """Run example validation and processing workflow."""

    # Paths
    schema_path = Path(__file__).parent.parent / 'schemas' / 'protocol.json'
    sample_data_path = Path(__file__).parent / 'sample_data.json'

    # Load sample data
    print("Loading sample data...")
    with open(sample_data_path, 'r') as f:
        test_data = json.load(f)

    print(f"Test ID: {test_data['test_id']}")
    print(f"Module: {test_data['sample_info']['manufacturer']} {test_data['sample_info']['model']}")
    print()

    # =========================================================================
    # VALIDATION
    # =========================================================================

    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    validator = LETID001Validator(str(schema_path))

    # Validate complete test
    is_valid, validation_report = validator.validate_complete_test(test_data)

    print(f"\nValidation Result: {'PASS' if is_valid else 'FAIL'}")
    print(f"Sections Validated: {', '.join(validation_report['sections_validated'])}")

    if validation_report['errors']:
        print(f"\nErrors ({len(validation_report['errors'])}):")
        for error in validation_report['errors']:
            print(f"  - {error}")

    if validation_report['warnings']:
        print(f"\nWarnings ({len(validation_report['warnings'])}):")
        for warning in validation_report['warnings']:
            print(f"  - {warning}")

    # Check acceptance criteria
    if 'acceptance_criteria' in validation_report:
        criteria = validation_report['acceptance_criteria']
        print(f"\nAcceptance Criteria:")
        print(f"  Power Degradation: {criteria['power_degradation_percent']:.2f}%")
        print(f"  Test Result: {'PASS' if criteria['pass'] else 'FAIL'}")

        if criteria['failures']:
            print(f"  Failures:")
            for failure in criteria['failures']:
                print(f"    - {failure}")

    print()

    # =========================================================================
    # PROCESSING
    # =========================================================================

    print("=" * 70)
    print("PROCESSING & ANALYSIS")
    print("=" * 70)

    processor = LETID001Processor(str(schema_path))

    # Process time series
    initial_pmax = test_data['initial_characterization']['pmax']
    df = processor.process_time_series(test_data['time_series'], initial_pmax)

    print(f"\nTime Series Data: {len(df)} measurements")
    print(f"\nProcessed DataFrame columns:")
    print(f"  {', '.join(df.columns.tolist())}")

    # Calculate statistics
    stats = processor.calculate_statistics(df)

    print(f"\nTest Statistics:")
    print(f"  Total Duration: {stats['duration_hours']:.1f} hours")
    print(f"  Total Measurements: {stats['total_measurements']}")

    if 'power_stats' in stats:
        ps = stats['power_stats']
        print(f"\nPower Statistics:")
        print(f"  Min Normalized Power: {ps['min_normalized_power']:.2f}%")
        print(f"  Final Normalized Power: {ps['final_normalized_power']:.2f}%")
        print(f"  Final Degradation: {ps['final_degradation']:.2f}%")

    if 'environmental_stats' in stats:
        env = stats['environmental_stats']
        if 'temperature' in env:
            print(f"\nTemperature Statistics:")
            print(f"  Mean: {env['temperature']['mean']:.1f}°C")
            print(f"  Std Dev: {env['temperature']['std']:.2f}°C")
            print(f"  Range: {env['temperature']['min']:.1f}°C - {env['temperature']['max']:.1f}°C")

        if 'irradiance' in env:
            print(f"\nIrradiance Statistics:")
            print(f"  Mean: {env['irradiance']['mean']:.1f} W/m²")
            print(f"  Std Dev: {env['irradiance']['std']:.2f} W/m²")

    # Fit degradation model
    model = processor.fit_degradation_model(df)

    if 'error' not in model:
        print(f"\nDegradation Model:")
        print(f"  Type: {model['model_type']}")
        print(f"  R²: {model['r_squared']:.4f}")

        if model['model_type'] == 'linear':
            print(f"  Slope: {model['slope']:.4f} %/hour")
            print(f"  Intercept: {model['intercept']:.2f}%")
            print(f"  Predicted 300h Power: {model['predicted_300h_power']:.2f}%")
        elif model['model_type'] == 'exponential':
            print(f"  Decay Rate: {model['decay_rate']:.6f}")
            print(f"  Predicted 300h Power: {model['predicted_300h_power']:.2f}%")

    # Detect stabilization
    stabilization = processor.detect_stabilization(df)
    if stabilization:
        print(f"\nStabilization detected at: {stabilization:.1f} hours")
    else:
        print(f"\nNo stabilization detected")

    # Generate analysis report
    print(f"\nGenerating analysis report...")
    report = processor.generate_analysis_report(test_data)

    print(f"\nAnalysis Report:")
    print(f"  Protocol: {report['protocol_id']} v{report['protocol_version']}")
    print(f"  Analysis Timestamp: {report['analysis_timestamp']}")

    if 'results' in report:
        results = report['results']
        print(f"  Initial Pmax: {results['initial_pmax']:.2f} W")
        print(f"  Final Pmax: {results['final_pmax']:.2f} W")
        print(f"  Degradation: {results['degradation_percent']:.2f}%")

    # =========================================================================
    # EXPORT
    # =========================================================================

    print()
    print("=" * 70)
    print("EXPORT")
    print("=" * 70)

    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)

    # Export processed time series to CSV
    csv_path = output_dir / 'letid_time_series.csv'
    processor.export_to_csv(df, str(csv_path))
    print(f"\nExported time series to: {csv_path}")

    # Export analysis report to JSON
    json_path = output_dir / 'letid_analysis_report.json'
    processor.export_to_json(report, str(json_path))
    print(f"Exported analysis report to: {json_path}")

    print()
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
