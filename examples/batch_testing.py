"""
Example: Batch Testing Multiple Samples

This example demonstrates how to run spectral response tests on
multiple samples in a batch with automated reporting.
"""

from pathlib import Path

import pandas as pd

from src.protocols import Protocol, SpectralResponseTest


def run_batch_tests(sample_list, test_params, output_dir):
    """
    Run spectral response tests on multiple samples

    Args:
        sample_list: List of sample information dictionaries
        test_params: Common test parameters
        output_dir: Output directory for results

    Returns:
        DataFrame with summary results
    """
    # Load protocol
    protocol_path = Path(__file__).parent.parent / "protocols" / "SPEC-001.json"
    protocol = Protocol(str(protocol_path))

    results_summary = []

    for i, sample_info in enumerate(sample_list, 1):
        print(f"\n{'=' * 60}")
        print(f"Testing Sample {i}/{len(sample_list)}: {sample_info['sample_id']}")
        print('=' * 60)

        # Initialize test
        test = SpectralResponseTest(protocol=protocol, output_dir=output_dir)
        test_id = test.initialize(test_params, sample_info)

        try:
            # Run test workflow
            print("Running measurement...")
            test.run()

            print("Analyzing data...")
            test.load_reference_calibration()
            test.analyze()

            print("Running QC checks...")
            qc_results = test.run_qc()

            # Check if all QC passed
            all_qc_passed = all(result["passed"] for result in qc_results.values())
            qc_status = "PASS" if all_qc_passed else "FAIL"

            print("Exporting results...")
            exported_files = test.export_results()

            # Complete test
            test.complete()

            # Store summary
            results_summary.append({
                "Test ID": test_id,
                "Sample ID": sample_info["sample_id"],
                "Technology": sample_info["technology"],
                "Area (cm²)": sample_info["area"],
                "Peak EQE (%)": test.results["peak_eqe"],
                "Peak λ (nm)": test.results["peak_wavelength"],
                "Jsc (mA/cm²)": test.results["integrated_jsc"],
                "QC Status": qc_status,
                "Status": "Completed"
            })

            print(f"✓ Test completed successfully")
            print(f"  Peak EQE: {test.results['peak_eqe']:.1f}%")
            print(f"  Jsc: {test.results['integrated_jsc']:.2f} mA/cm²")
            print(f"  QC Status: {qc_status}")

        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
            results_summary.append({
                "Test ID": test_id,
                "Sample ID": sample_info["sample_id"],
                "Technology": sample_info["technology"],
                "Area (cm²)": sample_info["area"],
                "Peak EQE (%)": None,
                "Peak λ (nm)": None,
                "Jsc (mA/cm²)": None,
                "QC Status": "ERROR",
                "Status": f"Failed: {str(e)}"
            })

    return pd.DataFrame(results_summary)


def main():
    """Run batch testing example"""

    print("=" * 60)
    print("SPEC-001: Batch Testing Example")
    print("=" * 60)

    # Define test parameters (common for all samples)
    test_params = {
        "wavelength": {
            "start": 300,
            "end": 1200,
            "step_size": 25
        },
        "temperature": 25,
        "integration_time": 100,
        "averaging": 3
    }

    # Define sample list
    sample_list = [
        {
            "sample_id": "BATCH-CELL-001",
            "sample_type": "Solar Cell",
            "technology": "c-Si",
            "area": 2.0,
            "manufacturer": "Vendor A",
            "batch_number": "BATCH-2025-A"
        },
        {
            "sample_id": "BATCH-CELL-002",
            "sample_type": "Solar Cell",
            "technology": "c-Si",
            "area": 2.0,
            "manufacturer": "Vendor A",
            "batch_number": "BATCH-2025-A"
        },
        {
            "sample_id": "BATCH-CELL-003",
            "sample_type": "Solar Cell",
            "technology": "mc-Si",
            "area": 2.5,
            "manufacturer": "Vendor B",
            "batch_number": "BATCH-2025-B"
        },
        {
            "sample_id": "BATCH-CELL-004",
            "sample_type": "Solar Cell",
            "technology": "Perovskite",
            "area": 1.0,
            "manufacturer": "Vendor C",
            "batch_number": "BATCH-2025-C"
        }
    ]

    # Output directory
    output_dir = Path(__file__).parent.parent / "output" / "batch_testing"

    print(f"\nBatch Configuration:")
    print(f"  Number of samples: {len(sample_list)}")
    print(f"  Wavelength range: {test_params['wavelength']['start']}-{test_params['wavelength']['end']} nm")
    print(f"  Output directory: {output_dir}")

    # Run batch tests
    results_df = run_batch_tests(sample_list, test_params, str(output_dir))

    # Display summary
    print("\n" + "=" * 60)
    print("BATCH TESTING SUMMARY")
    print("=" * 60)
    print(results_df.to_string(index=False))

    # Save summary to file
    summary_file = output_dir / "batch_summary.csv"
    results_df.to_csv(summary_file, index=False)
    print(f"\n✓ Summary saved to: {summary_file}")

    # Calculate statistics
    print("\n" + "-" * 60)
    print("STATISTICS")
    print("-" * 60)

    completed_tests = results_df[results_df["Status"] == "Completed"]
    if len(completed_tests) > 0:
        print(f"Completed tests: {len(completed_tests)}/{len(results_df)}")
        print(f"Average Peak EQE: {completed_tests['Peak EQE (%)'].mean():.1f}%")
        print(f"Average Jsc: {completed_tests['Jsc (mA/cm²)'].mean():.2f} mA/cm²")
        print(f"QC Pass Rate: {(completed_tests['QC Status'] == 'PASS').sum()}/{len(completed_tests)}")
    else:
        print("No tests completed successfully")

    print("\n" + "=" * 60)
    print("Batch testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
