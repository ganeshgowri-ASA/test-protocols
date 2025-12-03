"""
AI Assistant Component for SolarEdge LIMS
Phase 1: PV Testing Knowledge Base Integration
"""

import streamlit as st
import os
from anthropic import Anthropic
from pinecone import Pinecone

class PVTestingAssistant:
    """AI Assistant for PV Testing queries and equipment guidance."""
    
    def __init__(self):
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.configured = bool(self.anthropic_api_key and self.pinecone_api_key)
        
        if self.configured:
            self.client = Anthropic(api_key=self.anthropic_api_key)
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            self.index = self.pc.Index("solaredge-lims")
    
    def query(self, user_question: str, namespace: str = "test-protocols") -> str:
        """
        Query the AI assistant with context from Pinecone vector database.
        
        Args:
            user_question: User's question
            namespace: Pinecone namespace to query ('test-protocols' or 'equipment-parameters')
        
        Returns:
            AI-generated response
        """
        if not self.configured:
            return "⚠️ AI Assistant not configured. Please set ANTHROPIC_API_KEY and PINECONE_API_KEY."
        
        try:
            # Query Pinecone for relevant context (stub for now - full implementation needs embeddings)
            # context_results = self.index.query(vector=embedding, namespace=namespace, top_k=5)
            
            # For Phase 1, use direct Claude query
            system_prompt = """
            You are an expert AI assistant for a Solar PV Testing Laboratory LIMS system.
            You help users with:
            - IEC 61215, IEC 61730, IEC 62804, ISO 17025 standards
            - Equipment specifications and calibration requirements
            - Test protocol guidance
            - Quality control procedures
            - Data analysis interpretation
            
            Provide accurate, concise, and actionable responses.
            """
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_question}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"❌ Error: {str(e)}"

def render_ai_assistant_sidebar():
    """
    Render AI Assistant in Streamlit sidebar.
    Call this function in any Streamlit page to add AI assistance.
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant")
        
        assistant = PVTestingAssistant()
        
        if not assistant.configured:
            st.warning("⚠️ AI Assistant not configured")
            st.caption("Set ANTHROPIC_API_KEY and PINECONE_API_KEY to enable")
            return
        
        st.success("✅ AI Assistant Ready")
        
        # Query input
        user_question = st.text_area(
            "Ask about PV testing, equipment, or standards:",
            placeholder="e.g., What are the key requirements for IEC 61215 testing?",
            height=100,
            key="ai_question"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            namespace = st.selectbox(
                "Context:",
                ["test-protocols", "equipment-parameters"],
                key="ai_namespace"
            )
        
        if st.button("Ask AI", type="primary", width="stretch"):
            if user_question:
                with st.spinner("Thinking..."):
                    response = assistant.query(user_question, namespace)
                    st.markdown("#### Response:")
                    st.markdown(response)
            else:
                st.warning("Please enter a question")
        
        st.caption("💡 Powered by Claude 3.5 Sonnet")