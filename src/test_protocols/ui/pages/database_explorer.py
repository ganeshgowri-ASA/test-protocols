"""Database explorer page."""

import streamlit as st
import pandas as pd


def show_database_explorer_page():
    """Display database explorer page."""
    st.title("Database Explorer")
    st.write("Browse and manage test sessions and protocols.")

    try:
        from ...models import init_database, get_session, TestSession, Protocol

        init_database()

        tab1, tab2 = st.tabs(["Test Sessions", "Protocols"])

        with tab1:
            st.subheader("Test Sessions")

            with get_session() as session:
                # Query all sessions
                sessions = session.query(TestSession).order_by(TestSession.created_at.desc()).all()

                if sessions:
                    # Create dataframe for display
                    session_data = []

                    for ts in sessions:
                        session_data.append(
                            {
                                "Session ID": ts.session_id,
                                "Protocol": ts.protocol.name if ts.protocol else "N/A",
                                "Status": ts.status,
                                "Test Name": ts.test_name,
                                "Operator": ts.operator,
                                "Device": ts.device_under_test,
                                "Started": ts.started_at,
                                "Duration (s)": ts.duration_seconds,
                            }
                        )

                    df = pd.DataFrame(session_data)
                    st.dataframe(df, use_container_width=True)

                    # Session details
                    st.markdown("---")
                    st.subheader("Session Details")

                    selected_session = st.selectbox(
                        "Select session to view details:",
                        [s.session_id for s in sessions],
                    )

                    if selected_session:
                        ts = next((s for s in sessions if s.session_id == selected_session), None)

                        if ts:
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write(f"**ID**: {ts.id}")
                                st.write(f"**Session ID**: {ts.session_id}")
                                st.write(f"**Protocol**: {ts.protocol.name if ts.protocol else 'N/A'}")
                                st.write(f"**Status**: {ts.status}")
                                st.write(f"**Test Name**: {ts.test_name}")

                            with col2:
                                st.write(f"**Operator**: {ts.operator}")
                                st.write(f"**Location**: {ts.location}")
                                st.write(f"**Device**: {ts.device_under_test}")
                                st.write(f"**Started**: {ts.started_at}")
                                st.write(f"**Duration**: {ts.duration_seconds:.1f}s" if ts.duration_seconds else "N/A")

                            if ts.notes:
                                st.write(f"**Notes**: {ts.notes}")

                            if ts.error_message:
                                st.error(f"**Error**: {ts.error_message}")

                            # Action buttons
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                if st.button("View Results"):
                                    if ts.results:
                                        st.session_state["test_results"] = ts.results
                                        st.success("Results loaded! Go to 'Results & Analysis' page.")
                                    else:
                                        st.warning("No results available for this session.")

                            with col2:
                                if st.button("Delete Session"):
                                    if st.checkbox("Confirm deletion"):
                                        session.delete(ts)
                                        session.commit()
                                        st.success("Session deleted!")
                                        st.rerun()

                else:
                    st.info("No test sessions found in database.")

        with tab2:
            st.subheader("Registered Protocols")

            with get_session() as session:
                protocols = session.query(Protocol).all()

                if protocols:
                    protocol_data = []

                    for p in protocols:
                        protocol_data.append(
                            {
                                "Protocol ID": p.protocol_id,
                                "Name": p.name,
                                "Version": p.version,
                                "Category": p.category,
                                "Author": p.author,
                                "Created": p.created_at,
                                "Sessions": len(p.test_sessions),
                            }
                        )

                    df = pd.DataFrame(protocol_data)
                    st.dataframe(df, use_container_width=True)

                    # Protocol details
                    st.markdown("---")
                    st.subheader("Protocol Details")

                    selected_protocol = st.selectbox(
                        "Select protocol to view details:",
                        [p.protocol_id for p in protocols],
                    )

                    if selected_protocol:
                        p = next((pr for pr in protocols if pr.protocol_id == selected_protocol), None)

                        if p:
                            st.write(f"**Name**: {p.name}")
                            st.write(f"**Version**: {p.version}")
                            st.write(f"**Category**: {p.category}")
                            st.write(f"**Description**: {p.description}")
                            st.write(f"**Author**: {p.author}")

                            if p.standards:
                                st.write("**Standards**:")
                                for standard in p.standards:
                                    st.write(f"  - {standard}")

                            if p.equipment_required:
                                st.write("**Equipment Required**:")
                                for equipment in p.equipment_required:
                                    st.write(f"  - {equipment}")

                            st.write(f"**Created**: {p.created_at}")
                            st.write(f"**Updated**: {p.updated_at}")
                            st.write(f"**Test Sessions**: {len(p.test_sessions)}")

                else:
                    st.info("No protocols registered in database.")

                    if st.button("Register ENER-001 Protocol"):
                        from ...core.protocol_loader import load_protocol

                        try:
                            config = load_protocol("ENER-001")
                            protocol = Protocol.from_config(config)
                            session.add(protocol)
                            session.commit()
                            st.success("ENER-001 protocol registered!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error registering protocol: {e}")

    except Exception as e:
        st.error(f"Error accessing database: {e}")
        st.exception(e)


if __name__ == "__main__":
    show_database_explorer_page()
