"""
Analysis Page
EL image analysis and delamination detection
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from protocols.delam_001 import DELAM001Analyzer

st.set_page_config(page_title="EL Analysis", page_icon="🔍", layout="wide")

st.markdown("# 🔍 EL Image Analysis")
st.markdown("Automated electroluminescence image analysis for delamination detection")
st.markdown("---")


def main():
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = DELAM001Analyzer()

    # Initialize analysis results storage
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []

    # Tabs for different analysis functions
    tabs = st.tabs([
        "📸 Single Image Analysis",
        "📚 Batch Analysis",
        "📊 Results Summary",
        "🔄 Comparison"
    ])

    # Single Image Analysis Tab
    with tabs[0]:
        st.markdown("### Single EL Image Analysis")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### Upload EL Image")

            uploaded_file = st.file_uploader(
                "Select EL image file",
                type=['tiff', 'tif', 'png', 'jpg', 'jpeg'],
                help="Upload electroluminescence image for analysis"
            )

            if uploaded_file:
                # Display uploaded image
                st.image(uploaded_file, caption="Uploaded EL Image", use_container_width=True)

                # Image metadata
                st.markdown("**Image Information:**")
                st.text(f"Filename: {uploaded_file.name}")
                st.text(f"Size: {uploaded_file.size / 1024:.2f} KB")
                st.text(f"Type: {uploaded_file.type}")

        with col2:
            st.markdown("#### Analysis Parameters")

            defect_threshold = st.slider(
                "Defect Detection Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.15,
                step=0.01,
                help="Intensity threshold for defect detection"
            )

            min_defect_area = st.number_input(
                "Minimum Defect Area (mm²)",
                min_value=0.1,
                value=10.0,
                step=0.1,
                help="Minimum area to consider as defect"
            )

            module_type = st.selectbox(
                "Module Type",
                options=["monocrystalline", "polycrystalline", "thin_film", "bifacial"],
                help="Type of PV module"
            )

        # Analysis button
        if uploaded_file and st.button("🔍 Analyze Image", type="primary"):
            with st.spinner("Analyzing EL image..."):
                # Save uploaded file temporarily
                temp_path = project_root / "temp" / uploaded_file.name
                temp_path.parent.mkdir(parents=True, exist_ok=True)

                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                # Run analysis
                metadata = {
                    'filename': uploaded_file.name,
                    'timestamp': datetime.now().isoformat(),
                    'module_type': module_type
                }

                # Update analyzer config
                st.session_state.analyzer.config['defect_detection_threshold'] = defect_threshold
                st.session_state.analyzer.config['minimum_defect_area'] = min_defect_area

                # Perform analysis
                results = st.session_state.analyzer.analyze_image(temp_path, metadata)

                # Store results
                st.session_state.analysis_results.append(results)

                st.success("✅ Analysis completed successfully!")

        # Display results if available
        if st.session_state.analysis_results:
            latest_result = st.session_state.analysis_results[-1]

            st.markdown("---")
            st.markdown("### Analysis Results")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Delamination Detected",
                    "Yes" if latest_result.delamination_detected else "No",
                    delta=None,
                    help="Whether delamination was detected"
                )

            with col2:
                st.metric(
                    "Affected Area",
                    f"{latest_result.delamination_area_percent:.2f}%",
                    help="Percentage of module area affected"
                )

            with col3:
                st.metric(
                    "Defect Count",
                    latest_result.defect_count,
                    help="Number of defects detected"
                )

            with col4:
                severity_color = {
                    'none': '🟢',
                    'minor': '🟡',
                    'moderate': '🟠',
                    'severe': '🔴',
                    'critical': '⚫'
                }
                st.metric(
                    "Severity",
                    f"{severity_color.get(latest_result.severity_level, '')} {latest_result.severity_level.upper()}",
                    help="Delamination severity level"
                )

            # Defect details
            if latest_result.defect_regions:
                st.markdown("#### Detected Defects")

                defect_data = []
                for i, defect in enumerate(latest_result.defect_regions, 1):
                    defect_data.append({
                        'ID': i,
                        'Location': f"({defect.x}, {defect.y})",
                        'Size': f"{defect.width}x{defect.height}",
                        'Area (mm²)': f"{defect.area:.2f}",
                        'Severity': defect.severity,
                        'Mean Intensity': f"{defect.intensity_mean:.3f}"
                    })

                st.dataframe(defect_data, use_container_width=True)

            # Quality metrics
            if latest_result.quality_metrics:
                st.markdown("#### Image Quality Metrics")

                col1, col2, col3, col4 = st.columns(4)

                metrics = latest_result.quality_metrics

                with col1:
                    st.metric("Sharpness", f"{metrics.get('image_sharpness', 0):.2f}")

                with col2:
                    st.metric("Contrast", f"{metrics.get('contrast_ratio', 0):.2f}")

                with col3:
                    st.metric("Noise Level", f"{metrics.get('noise_level', 0):.3f}")

                with col4:
                    st.metric("Uniformity", f"{metrics.get('uniformity_index', 0):.2f}")

            # Export results
            if st.button("💾 Export Results"):
                import json
                export_path = project_root / "results" / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                export_path.parent.mkdir(parents=True, exist_ok=True)

                with open(export_path, 'w') as f:
                    json.dump(latest_result.to_dict(), f, indent=2)

                st.success(f"✅ Results exported to: {export_path}")

    # Batch Analysis Tab
    with tabs[1]:
        st.markdown("### Batch EL Image Analysis")

        uploaded_files = st.file_uploader(
            "Select multiple EL images",
            type=['tiff', 'tif', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help="Upload multiple images for batch analysis"
        )

        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} images selected for analysis")

            if st.button("🔍 Analyze Batch", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                batch_results = []

                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Analyzing {file.name}...")

                    # Save and analyze
                    temp_path = project_root / "temp" / file.name
                    temp_path.parent.mkdir(parents=True, exist_ok=True)

                    with open(temp_path, 'wb') as f:
                        f.write(file.getbuffer())

                    result = st.session_state.analyzer.analyze_image(temp_path)
                    batch_results.append(result)

                    progress_bar.progress((i + 1) / len(uploaded_files))

                status_text.text("✅ Batch analysis complete!")

                # Display batch summary
                st.markdown("#### Batch Analysis Summary")

                summary_data = []
                for i, result in enumerate(batch_results, 1):
                    summary_data.append({
                        'Image': result.image_metadata['filename'],
                        'Delamination': 'Yes' if result.delamination_detected else 'No',
                        'Area %': f"{result.delamination_area_percent:.2f}",
                        'Defects': result.defect_count,
                        'Severity': result.severity_level
                    })

                st.dataframe(summary_data, use_container_width=True)

    # Results Summary Tab
    with tabs[2]:
        st.markdown("### Analysis Summary")

        if st.session_state.analyzer.analysis_history:
            summary = st.session_state.analyzer.get_analysis_summary()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Analyses", summary['total_analyses'])

            with col2:
                st.metric("Delamination Detected", summary['delamination_detected_count'])

            with col3:
                st.metric(
                    "Detection Rate",
                    f"{summary['delamination_detection_rate']*100:.1f}%"
                )

            with col4:
                st.metric(
                    "Avg Delamination",
                    f"{summary['average_delamination_percent']:.2f}%"
                )

            # Severity distribution
            st.markdown("#### Severity Distribution")
            st.bar_chart(summary['severity_distribution'])

        else:
            st.info("📊 No analyses performed yet. Upload and analyze images to see summary.")

    # Comparison Tab
    with tabs[3]:
        st.markdown("### Image Comparison")

        st.info("Compare baseline and test images to detect progression of delamination")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Baseline Image")
            baseline_file = st.file_uploader(
                "Upload baseline EL image",
                type=['tiff', 'tif', 'png'],
                key="baseline"
            )

            if baseline_file:
                st.image(baseline_file, caption="Baseline", use_container_width=True)

        with col2:
            st.markdown("#### Test Image")
            test_file = st.file_uploader(
                "Upload test EL image",
                type=['tiff', 'tif', 'png'],
                key="test"
            )

            if test_file:
                st.image(test_file, caption="Test", use_container_width=True)

        if baseline_file and test_file:
            if st.button("🔄 Compare Images", type="primary"):
                with st.spinner("Comparing images..."):
                    # Save files temporarily
                    baseline_path = project_root / "temp" / baseline_file.name
                    test_path = project_root / "temp" / test_file.name

                    for path, file in [(baseline_path, baseline_file), (test_path, test_file)]:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with open(path, 'wb') as f:
                            f.write(file.getbuffer())

                    # Perform comparison
                    comparison = st.session_state.analyzer.compare_images(
                        baseline_path,
                        test_path
                    )

                    st.success("✅ Comparison complete!")

                    # Display comparison results
                    st.markdown("#### Comparison Results")

                    col1, col2, col3 = st.columns(3)

                    changes = comparison['changes']

                    with col1:
                        st.metric(
                            "Area Change",
                            f"{changes['delamination_area_change_percent']:.2f}%",
                            delta=f"{changes['delamination_area_change_percent']:.2f}%"
                        )

                    with col2:
                        st.metric(
                            "Defect Count Change",
                            changes['defect_count_change'],
                            delta=changes['defect_count_change']
                        )

                    with col3:
                        degradation = "⚠️ Yes" if changes['degradation_detected'] else "✅ No"
                        st.metric("Degradation Detected", degradation)

                    st.markdown(f"**Severity Progression:** {changes['severity_progression']}")


if __name__ == "__main__":
    main()
