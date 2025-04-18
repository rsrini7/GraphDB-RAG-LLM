import streamlit as st
import time
import logging
import json
import os
from orchestrator import Orchestrator
from utils import monitoring_dashboard
from utils.monitoring import monitoring
from utils.error_handler import error_handler
from typing import Dict, Any

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                st.session_state.history = json.load(f)
        except Exception as e:
            error_resp = error_handler.handle_error(e, {"action": "load_history"})
            logging.error(f"Failed to load chat history: {error_resp['error_message']}")
            st.session_state.history = []
    else:
        st.session_state.history = []

def save_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(st.session_state.history, f)
    except Exception as e:
        error_resp = error_handler.handle_error(e, {"action": "save_history"})
        logging.error(f"Failed to save chat history: {error_resp['error_message']}")

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

# Initialize or load session state for history
if 'history' not in st.session_state:
    load_history()

def process_question(question: str) -> Dict[str, Any]:
    """Process a user question through the orchestrator.
    
    Args:
        question: The natural language question from the user
        
    Returns:
        Dict containing the answer and additional information
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
        save_history()
        
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
        error_resp = error_handler.handle_error(e, {"question": question})
        logger.error(f"Error processing question: {error_resp['error_message']}")
        monitoring_dashboard.update_metrics("error", 1)
        monitoring_dashboard.log_activity("error", {
            "error_type": error_resp["error_type"],
            "error_message": error_resp["error_message"],
            "question": question
        })
        return {
            "status": "error",
            "error_message": error_resp["user_message"],
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

    st.header("Data Ingestion")
    load_sample = st.checkbox("Load from sample_data", value=True)
    data_location = st.text_input(
        "Data file location",
        value="",
        disabled=load_sample,
        placeholder="Enter path to your data file"
    )

    file_type = st.selectbox("File type", options=["", "csv", "json", "txt"], index=0)
    chunk_size = st.number_input("Chunk size (characters)", min_value=100, max_value=5000, value=512, step=100)
    chunk_overlap = st.number_input("Chunk overlap (characters)", min_value=0, max_value=1000, value=50, step=10)
    embedding_model = st.text_input("Embedding model (optional)", value="")
    clear_existing = st.checkbox("Clear existing data before ingestion", value=False)
    verbose = st.checkbox("Verbose logging", value=False)

    if st.button("Load Data"):
        if load_sample:
            selected_path = "sample_data"
        else:
            selected_path = data_location.strip()
        if not selected_path:
            st.warning("Please provide a valid data location.")
        else:
            try:
                import logging as pylogging
                from data_ingestion.ingest import DataIngestion

                if verbose:
                    pylogging.getLogger().setLevel(pylogging.DEBUG)
                else:
                    pylogging.getLogger().setLevel(pylogging.INFO)

                st.info(f"Starting data ingestion from: {selected_path}")

                ingestion = DataIngestion()

                if clear_existing:
                    st.info("Clearing existing data before ingestion...")
                    ingestion.clear_existing_data()

                ingestion.preprocessor.chunk_size = chunk_size
                ingestion.preprocessor.chunk_overlap = chunk_overlap

                if embedding_model:
                    ingestion.embedding_generator.model_name = embedding_model
                    ingestion.embedding_generator._load_model()

                ingestion.ingest_data(
                    data_path=selected_path,
                    file_type=file_type if file_type else None
                )

                st.success(f"Data ingestion completed successfully from: {selected_path}")
            except Exception as e:
                error_resp = error_handler.handle_error(e, {"action": "data_ingestion"})
                st.error(error_resp["user_message"])
    
    st.header("Query History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Q: {item['question'][:50]}..."):
                st.write(f"**Question:** {item['question']}")
                if item.get("status") == "error":
                    st.error(f"Error: {item['error_message']}")
                else:
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
                    st.error(result["error_message"])
                else:
                    # Display the answer
                    st.header("Answer")
                    st.write(result["answer"])
                    
                    # Display additional information in expandable sections
                    with st.expander("Cypher Query"):
                        st.code(result["cypher_query"], language="cypher")
                    
                    with st.expander("Query Results"):
                        st.json(result["query_results"])
        except Exception as e:
            error_resp = error_handler.handle_error(e, {"question": question})
            st.error(error_resp["user_message"])
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
