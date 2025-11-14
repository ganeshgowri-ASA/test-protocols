"""
UI Pages
Individual page components for the Streamlit application
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from protocols.loader import ProtocolLoader
from protocols.environmental.h2s_001 import H2S001Protocol
from database.session import session_scope
from database.models import Protocol, Module, TestExecution, ProtocolStatus, TestResult


def show_home_page():
    """Display home page with overview and quick stats"""
    st.title("🏠 PV Test Protocol Framework")

    st.markdown("""
    ## Welcome to the Modular PV Testing Protocol System

    This framework provides:
    - **JSON-based Protocol Definitions** - Flexible, version-controlled test specifications
    - **Automated Test Execution** - Guided workflows with built-in QC
    - **Real-time Data Collection** - Structured data capture with validation
    - **Comprehensive Analysis** - Automated calculations and pass/fail evaluation
    - **LIMS/QMS Integration** - Seamless integration with laboratory systems
    """)

    # Quick statistics
    col1, col2, col3, col4 = st.columns(4)

    with session_scope() as session:
        total_protocols = session.query(Protocol).count()
        total_modules = session.query(Module).count()
        total_tests = session.query(TestExecution).count()
        passed_tests = session.query(TestExecution).filter(
            TestExecution.result == TestResult.PASS
        ).count()

    with col1:
        st.metric("Protocols", total_protocols)
    with col2:
        st.metric("Modules Tested", total_modules)
    with col3:
        st.metric("Total Tests", total_tests)
    with col4:
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        st.metric("Pass Rate", f"{pass_rate:.1f}%")

    st.markdown("---")

    # Recent tests
    st.subheader("Recent Test Executions")
    with session_scope() as session:
        recent = session.query(TestExecution).order_by(
            TestExecution.test_date.desc()
        ).limit(5).all()

        if recent:
            data = []
            for test in recent:
                data.append({
                    "Execution ID": test.execution_id,
                    "Date": test.test_date.strftime("%Y-%m-%d"),
                    "Protocol": test.protocol.code,
                    "Module": test.module.module_id,
                    "Status": test.status.value,
                    "Result": test.result.value if test.result else "N/A"
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("No test executions yet. Start a new test from the 'New Test' page.")


def show_protocol_selection():
    """Display protocol selection interface"""
    st.title("🧪 New Test Execution")

    st.subheader("Step 1: Select Protocol")

    # Protocol selection
    protocol_dir = Path(__file__).parent.parent / "protocols" / "environmental"
    protocol_files = list(protocol_dir.glob("*.json"))

    if not protocol_files:
        st.warning("No protocol files found. Please add protocol JSON files to the protocols directory.")
        return

    protocol_options = {f.stem: f for f in protocol_files}
    selected = st.selectbox(
        "Select Protocol",
        options=list(protocol_options.keys()),
        format_func=lambda x: x.replace("_", " ").replace("-", " - ")
    )

    if selected:
        protocol_path = protocol_options[selected]

        # Load and display protocol info
        if selected == "P37-54_H2S-001":
            protocol = H2S001Protocol(protocol_path)
            st.session_state.current_protocol = protocol

            info = protocol.get_protocol_info()
            desc = protocol.get_description()

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"""
                **Protocol:** {info['id']} - {info['code']}
                **Name:** {info['name']}
                **Category:** {info['category']}
                **Version:** {info['version']}
                """)
            with col2:
                st.info(f"""
                **Status:** {info['status']}
                **Effective Date:** {info['effective_date']}
                """)

            st.markdown(f"**Purpose:** {desc['purpose']}")

            with st.expander("Protocol Details"):
                st.markdown(f"**Summary:** {desc['summary']}")
                st.markdown(f"**Scope:** {desc['scope']}")
                st.markdown("**References:**")
                for ref in desc['references']:
                    st.markdown(f"- {ref}")


def show_test_execution():
    """Display test execution interface"""
    if not st.session_state.current_protocol:
        return

    protocol = st.session_state.current_protocol

    st.markdown("---")
    st.subheader("Step 2: Module Information")

    col1, col2 = st.columns(2)
    with col1:
        module_id = st.text_input("Module ID*", key="module_id")
        manufacturer = st.text_input("Manufacturer*", key="manufacturer")
        model = st.text_input("Model*", key="model")
        technology = st.selectbox(
            "Technology*",
            ["mono-Si", "poly-Si", "CdTe", "CIGS", "a-Si", "other"],
            key="technology"
        )

    with col2:
        nameplate_power = st.number_input("Nameplate Power (W)*", min_value=0.0, key="nameplate")
        serial_number = st.text_input("Serial Number", key="serial")
        operator = st.text_input("Test Operator*", key="operator")
        severity_level = st.selectbox(
            "Severity Level",
            [1, 2, 3, 4],
            index=1,
            format_func=lambda x: f"Level {x}",
            key="severity"
        )

    st.markdown("---")
    st.subheader("Step 3: Test Execution")

    if st.button("Start Test Execution", type="primary"):
        if all([module_id, manufacturer, model, technology, nameplate_power, operator]):
            # Set module info
            module_info = {
                "module_id": module_id,
                "manufacturer": manufacturer,
                "model": model,
                "technology": technology,
                "nameplate_power": nameplate_power,
                "serial_number": serial_number,
                "test_date": datetime.now().isoformat(),
                "operator": operator,
                "severity_level": severity_level
            }
            protocol.set_module_info(module_info)
            protocol.start_protocol()
            st.session_state.test_started = True
            st.success("Test started! Proceed with test phases below.")
        else:
            st.error("Please fill in all required fields (marked with *)")

    # Show test phases if started
    if st.session_state.get("test_started"):
        show_test_phases(protocol)


def show_test_phases(protocol):
    """Display and execute test phases"""
    st.markdown("---")

    # Progress bar
    progress = protocol.get_progress()
    st.progress(progress["progress_percent"] / 100)
    st.caption(f"Progress: {progress['completed_steps']}/{progress['total_steps']} steps completed")

    # Phase tabs
    phase_names = [f"Phase {p.phase_id}: {p.name}" for p in protocol.phases]
    tabs = st.tabs(phase_names)

    for idx, (tab, phase) in enumerate(zip(tabs, protocol.phases)):
        with tab:
            show_phase_execution(protocol, phase, idx)


def show_phase_execution(protocol, phase, phase_idx):
    """Display individual phase execution"""
    st.subheader(f"{phase.name}")
    st.caption(f"Estimated Duration: {phase.duration}")

    # Start phase button
    if phase.status.value == "pending":
        if st.button(f"Start Phase {phase.phase_id}", key=f"start_phase_{phase_idx}"):
            phase.start()
            st.rerun()

    # Display steps
    for step_idx, step in enumerate(phase.steps):
        with st.expander(
            f"Step {step.step_id}: {step.action}",
            expanded=(step.status.value == "in_progress")
        ):
            st.markdown(f"**Description:** {step.description}")

            if step.acceptance_criteria:
                st.markdown(f"**Acceptance Criteria:** {step.acceptance_criteria}")

            if step.parameters:
                st.markdown("**Parameters:**")
                for key, value in step.parameters.items():
                    st.markdown(f"- {key}: {value}")

            # Step controls
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if step.status.value == "pending" and st.button(
                    "Start", key=f"start_{phase_idx}_{step_idx}"
                ):
                    step.start()
                    st.rerun()

            with col2:
                if step.status.value == "in_progress":
                    # Data entry for specific steps
                    if "Electrical Characterization" in step.action:
                        show_electrical_data_entry(protocol, step, phase_idx, step_idx)
                    elif "Insulation Resistance" in step.action:
                        show_insulation_data_entry(protocol, step, phase_idx, step_idx)
                    elif "Weight Measurement" in step.action:
                        show_weight_data_entry(protocol, step, phase_idx, step_idx)

            with col3:
                if step.status.value == "in_progress":
                    notes = st.text_area(
                        "Notes",
                        key=f"notes_{phase_idx}_{step_idx}",
                        height=100
                    )
                    if st.button("Complete Step", key=f"complete_{phase_idx}_{step_idx}"):
                        step.operator_notes = notes
                        step.complete()
                        # Check if phase is complete
                        if all(s.status.value == "completed" for s in phase.steps):
                            phase.complete()
                        st.rerun()

            # Show status
            status_colors = {
                "pending": "🔵",
                "in_progress": "🟡",
                "completed": "🟢",
                "failed": "🔴"
            }
            st.caption(f"Status: {status_colors.get(step.status.value, '')} {step.status.value}")


def show_electrical_data_entry(protocol, step, phase_idx, step_idx):
    """Show electrical measurement data entry form"""
    st.markdown("**Enter Measurements:**")

    col1, col2 = st.columns(2)
    with col1:
        voc = st.number_input("Voc (V)", min_value=0.0, key=f"voc_{phase_idx}_{step_idx}")
        vmp = st.number_input("Vmp (V)", min_value=0.0, key=f"vmp_{phase_idx}_{step_idx}")
        pmax = st.number_input("Pmax (W)", min_value=0.0, key=f"pmax_{phase_idx}_{step_idx}")

    with col2:
        isc = st.number_input("Isc (A)", min_value=0.0, key=f"isc_{phase_idx}_{step_idx}")
        imp = st.number_input("Imp (A)", min_value=0.0, key=f"imp_{phase_idx}_{step_idx}")
        ff = st.number_input("FF", min_value=0.0, max_value=1.0, key=f"ff_{phase_idx}_{step_idx}")

    if st.button("Save Measurements", key=f"save_elec_{phase_idx}_{step_idx}"):
        if phase_idx == 0:  # Baseline
            protocol.record_baseline_electrical(voc, isc, vmp, imp, pmax, ff)
        else:  # Post-test
            protocol.record_post_test_electrical(voc, isc, vmp, imp, pmax, ff)
        st.success("Measurements saved!")


def show_insulation_data_entry(protocol, step, phase_idx, step_idx):
    """Show insulation resistance data entry form"""
    insulation = st.number_input(
        "Insulation Resistance (MΩ)",
        min_value=0.0,
        key=f"insulation_{phase_idx}_{step_idx}"
    )
    if st.button("Save Insulation Measurement", key=f"save_insul_{phase_idx}_{step_idx}"):
        if phase_idx == 0:
            st.session_state.baseline_insulation = insulation
        else:
            protocol.record_insulation_resistance(
                st.session_state.get("baseline_insulation", 0),
                insulation
            )
        st.success("Measurement saved!")


def show_weight_data_entry(protocol, step, phase_idx, step_idx):
    """Show weight measurement data entry form"""
    weight = st.number_input(
        "Module Weight (kg)",
        min_value=0.0,
        key=f"weight_{phase_idx}_{step_idx}"
    )
    if st.button("Save Weight", key=f"save_weight_{phase_idx}_{step_idx}"):
        if phase_idx == 0:
            st.session_state.baseline_weight = weight
        else:
            protocol.record_weight_measurements(
                st.session_state.get("baseline_weight", 0),
                weight
            )
        st.success("Measurement saved!")


def show_results_viewer():
    """Display test results viewer"""
    st.title("📊 Test Results")

    with session_scope() as session:
        executions = session.query(TestExecution).order_by(
            TestExecution.test_date.desc()
        ).all()

        if not executions:
            st.info("No test results available yet.")
            return

        # Filter controls
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect(
                "Status",
                options=[s.value for s in ProtocolStatus],
                default=None
            )
        with col2:
            result_filter = st.multiselect(
                "Result",
                options=[r.value for r in TestResult],
                default=None
            )

        # Display results table
        data = []
        for exec in executions:
            if status_filter and exec.status.value not in status_filter:
                continue
            if result_filter and exec.result and exec.result.value not in result_filter:
                continue

            data.append({
                "Execution ID": exec.execution_id,
                "Date": exec.test_date,
                "Protocol": exec.protocol.code,
                "Module": exec.module.module_id,
                "Operator": exec.operator,
                "Status": exec.status.value,
                "Result": exec.result.value if exec.result else "N/A",
                "Pmax Degradation": f"{exec.degradation_pmax:.2f}%" if exec.degradation_pmax else "N/A"
            })

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)

            # Detailed view
            selected_exec = st.selectbox(
                "Select execution for details",
                options=[d["Execution ID"] for d in data]
            )

            if selected_exec:
                show_execution_details(selected_exec)


def show_execution_details(execution_id):
    """Show detailed results for a specific execution"""
    with session_scope() as session:
        exec = session.query(TestExecution).filter(
            TestExecution.execution_id == execution_id
        ).first()

        if not exec:
            return

        st.markdown("---")
        st.subheader(f"Details: {execution_id}")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pmax Degradation", f"{exec.degradation_pmax:.2f}%" if exec.degradation_pmax else "N/A")
        with col2:
            st.metric("Voc Degradation", f"{exec.degradation_voc:.2f}%" if exec.degradation_voc else "N/A")
        with col3:
            st.metric("Isc Degradation", f"{exec.degradation_isc:.2f}%" if exec.degradation_isc else "N/A")
        with col4:
            result_color = "🟢" if exec.result == TestResult.PASS else "🔴" if exec.result == TestResult.FAIL else "🟡"
            st.metric("Result", f"{result_color} {exec.result.value if exec.result else 'N/A'}")

        # Comparison chart
        if exec.baseline_pmax and exec.post_pmax:
            fig = go.Figure()
            params = ["Pmax", "Voc", "Isc", "FF"]
            baseline = [exec.baseline_pmax, exec.baseline_voc, exec.baseline_isc, exec.baseline_ff]
            post_test = [exec.post_pmax, exec.post_voc, exec.post_isc, exec.post_ff]

            fig.add_trace(go.Bar(name="Baseline", x=params, y=baseline))
            fig.add_trace(go.Bar(name="Post-Test", x=params, y=post_test))
            fig.update_layout(title="Baseline vs Post-Test Comparison", barmode="group")
            st.plotly_chart(fig, use_container_width=True)


def show_data_analysis():
    """Display data analysis and trends"""
    st.title("📈 Data Analysis")

    with session_scope() as session:
        executions = session.query(TestExecution).filter(
            TestExecution.degradation_pmax.isnot(None)
        ).all()

        if not executions:
            st.info("No test data available for analysis.")
            return

        # Create dataframe
        data = []
        for exec in executions:
            data.append({
                "Date": exec.test_date,
                "Module": exec.module.module_id,
                "Technology": exec.module.technology,
                "Pmax Degradation (%)": exec.degradation_pmax,
                "Voc Degradation (%)": exec.degradation_voc,
                "Isc Degradation (%)": exec.degradation_isc,
                "Result": exec.result.value if exec.result else "N/A"
            })

        df = pd.DataFrame(data)

        # Degradation over time
        st.subheader("Degradation Trends")
        fig = px.scatter(
            df,
            x="Date",
            y="Pmax Degradation (%)",
            color="Technology",
            title="Power Degradation Over Time",
            hover_data=["Module"]
        )
        st.plotly_chart(fig, use_container_width=True)

        # Technology comparison
        st.subheader("Technology Comparison")
        tech_avg = df.groupby("Technology")["Pmax Degradation (%)"].mean().reset_index()
        fig = px.bar(
            tech_avg,
            x="Technology",
            y="Pmax Degradation (%)",
            title="Average Power Degradation by Technology"
        )
        st.plotly_chart(fig, use_container_width=True)
