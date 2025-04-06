import streamlit as st
import time
import logging
from orchestrator import Orchestrator
from utils import monitoring_dashboard
from utils.monitoring import monitoring
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the orchestrator
orchestrator = Orchestrator()

# Set page configuration
st.set_page_config(
    page_title="GraphRAG - Graph-based Retrieval-Augmented Generation",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

def process_question(question: str) -> Dict[str, Any]:
    """Process a user question through the orchestrator.
    
    Args:
        question: The natural language question from the user
        
    Returns:
        Dictionary containing the answer and additional information
    """
    start_time = time.time()
    try:
        # Log the activity
        monitoring.log_activity("ui_question_submitted", {"question": question})
        monitoring_dashboard.log_activity("question_submitted", {"question": question})
        
        # Process the question through the orchestrator
        result = orchestrator.process_question(question)
        
        # Add to history
        st.session_state.history.append({
            "question": question,
            "answer": result["answer"],
            "cypher_query": result["cypher_query"],
            "query_results": result["query_results"]
        })
        
        # Update dashboard metrics
        elapsed_time = time.time() - start_time
        monitoring_dashboard.update_metrics("response_time", elapsed_time)
        if "cache_hit" in result and result["cache_hit"]:
            monitoring_dashboard.update_metrics("cache_hit", 1)
        else:
            monitoring_dashboard.update_metrics("cache_miss", 1)
        
        monitoring_dashboard.log_activity("answer_generated", {
            "question": question,
            "response_time": elapsed_time
        })
        
        return result
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        monitoring_dashboard.update_metrics("error", 1)
        monitoring_dashboard.log_activity("error", {"error": str(e), "question": question})
        return {
            "status": "error",
            "error_message": str(e),
            "question": question
        }

# Main UI layout
st.title("GraphRAG - Graph-based Retrieval-Augmented Generation")

# Sidebar for system information and history
with st.sidebar:
    st.header("System Information")
    st.info(
        "This system uses a Neo4j graph database with vector search capabilities "
        "to answer questions based on both structured data and semantic similarity."
    )
    
    st.header("Query History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Q: {item['question'][:50]}..."):
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Answer:** {item['answer']}")
                st.write(f"**Cypher Query:**\n```\n{item['cypher_query']}\n```")
    else:
        st.write("No queries yet. Ask a question to get started!")

# Initialize session state for button state if not exists
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Main content area
st.header("Ask a Question")
question = st.text_area("Enter your question:", height=100)

if st.button("Submit", type="primary", disabled=st.session_state.processing):
    if question:
        try:
            st.session_state.processing = True
            with st.spinner("Processing your question..."):
                # Process the question
                result = process_question(question)
                
                if "status" in result and result["status"] == "error":
                    st.error(f"Error: {result['error_message']}")
                else:
                    # Display the answer
                    st.header("Answer")
                    st.write(result["answer"])
                    
                    # Display additional information in expandable sections
                    with st.expander("Cypher Query"):
                        st.code(result["cypher_query"], language="cypher")
                    
                    with st.expander("Query Results"):
                        st.json(result["query_results"])
        finally:
            st.session_state.processing = False
    else:
        st.warning("Please enter a question.")

# Monitoring dashboard
# Render the monitoring dashboard using the dedicated component
monitoring_dashboard.render_dashboard()

# Footer
st.markdown("---")
st.caption("GraphRAG - A Graph-based Retrieval-Augmented Generation System")
