"""AI Assistant Component - Phase 1
Provides PV testing knowledge chatbot with Pinecone integration
"""
import streamlit as st
import os

class PVTestingAssistant:
    """AI Assistant for PV Testing Knowledge"""
    
    def __init__(self):
        self.ready = True
        self.pinecone_configured = os.environ.get('PINECONE_API_KEY') is not None
        self.anthropic_configured = os.environ.get('ANTHROPIC_API_KEY') is not None
    
    def chat(self, query):
        """Process user query and return response"""
        if not self.pinecone_configured or not self.anthropic_configured:
            return (
                "AI assistant not fully configured. Please add PINECONE_API_KEY and ANTHROPIC_API_KEY to Railway environment variables.",
                []
            )
        
        # Placeholder for future Pinecone + Claude integration
        return (
            f"Placeholder response for: {query}. AI assistant will be fully functional after Pinecone and Anthropic APIs are configured.",
            []
        )

def render_ai_assistant_sidebar():
    """Render AI Assistant in Streamlit sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 PV Testing Assistant")
    st.sidebar.caption("Ask questions about IEC standards, test procedures, or equipment")
    
    # Check configuration
    pinecone_ok = os.environ.get('PINECONE_API_KEY') is not None
    anthropic_ok = os.environ.get('ANTHROPIC_API_KEY') is not None
    
    if not pinecone_ok or not anthropic_ok:
        st.sidebar.warning("⚠️ AI assistant requires configuration")
        st.sidebar.caption("Missing API keys:")
        if not pinecone_ok:
            st.sidebar.caption("- PINECONE_API_KEY")
        if not anthropic_ok:
            st.sidebar.caption("- ANTHROPIC_API_KEY")
        return
    
    # Initialize assistant
    if 'assistant' not in st.session_state:
        st.session_state.assistant = PVTestingAssistant()
    
    # Chat input
    user_query = st.sidebar.text_area(
        "Your question:",
        placeholder="e.g., What are the requirements for thermal cycling test?",
        height=100,
        key="ai_assistant_input"
    )
    
    if st.sidebar.button("💬 Ask Assistant", type="primary"):
        if user_query.strip():
            with st.sidebar.spinner("Thinking..."):
                response, context_docs = st.session_state.assistant.chat(user_query)
                st.sidebar.markdown("**Answer:**")
                st.sidebar.info(response)
        else:
            st.sidebar.warning("Please enter a question")
    
    # Example questions
    with st.sidebar.expander("💡 Example Questions"):
        st.sidebar.markdown("""
        - What is the acceptable Pmax degradation for thermal cycling?
        - What are Standard Test Conditions (STC)?
        - How many cycles are required for damp heat test?
        - What equipment is needed for electroluminescence imaging?
        """)