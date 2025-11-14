"""Results and analysis page."""

import streamlit as st


def show_results_page():
    """Display results and analysis page."""
    st.title("Results & Analysis")

    # Check if there are test results in session state
    if "test_results" in st.session_state:
        results = st.session_state["test_results"]

        st.success(f"Displaying results for session: **{results['session_id']}**")

        # Import and use the display function from test_execution
        from .test_execution import display_results

        display_results(results, "moderate")

    else:
        st.info("No test results available. Please run a test first from the 'Test Execution' page.")

        # Show option to load results from database
        if st.button("Load Results from Database"):
            load_results_from_database()


def load_results_from_database():
    """Load results from database."""
    try:
        from ...models import init_database, get_session, TestSession

        init_database()

        with get_session() as session:
            # Get all completed sessions
            sessions = (
                session.query(TestSession)
                .filter(TestSession.status.in_(["completed", "completed_with_errors"]))
                .order_by(TestSession.created_at.desc())
                .limit(20)
                .all()
            )

            if sessions:
                # Create selection
                session_options = {
                    f"{s.session_id} - {s.test_name} ({s.created_at})": s.id
                    for s in sessions
                }

                selected = st.selectbox("Select a test session:", list(session_options.keys()))

                if selected and st.button("Load"):
                    session_id = session_options[selected]
                    test_session = session.query(TestSession).filter_by(id=session_id).first()

                    if test_session and test_session.results:
                        st.session_state["test_results"] = test_session.results
                        st.rerun()
                    else:
                        st.error("No results found for this session.")
            else:
                st.warning("No completed test sessions found in database.")

    except Exception as e:
        st.error(f"Error loading from database: {e}")


if __name__ == "__main__":
    show_results_page()
