# GraphRAG - Graph-based Retrieval-Augmented Generation System

This project implements a local Graph-based Retrieval-Augmented Generation (GraphRAG) system that allows users to ask natural language questions via a Streamlit interface. The system leverages a Langchain orchestrator to process questions, perform vector searches and structured graph queries against a local Neo4j database, and use an LLM (via OpenRouter) to generate Cypher queries and synthesize final natural language answers.

## Architecture

The system consists of the following components:

- **User Interface**: Streamlit web interface for user interaction
- **Orchestration**: Langchain for coordinating the RAG process
- **LLM Interface**: OpenRouter API for accessing language models
- **Graph Database**: Neo4j (running via Docker Compose) with Vector Index functionality
- **Database Driver**: Neo4j Python Driver for database interaction
- **Data Processing**: Components for ingestion, preprocessing, and embedding generation

## Setup Instructions

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- OpenRouter API key

### Installation

1. Clone this repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with the following variables:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=password
   ```

### Starting the System

1. Start the Neo4j database:
   ```bash
   docker-compose up -d
   ```
2. Run the data ingestion script (if needed):
   ```bash
   python src/data_ingestion/ingest.py --data-path /path/to/your/data
   ```
3. Start the Streamlit application:
   ```bash
   streamlit run src/app.py
   ```

## Usage

1. Open your browser and navigate to http://localhost:8501
2. Enter your question in the text input field
3. View the generated answer and any additional information displayed

## Project Structure

```
.
├── docker-compose.yml        # Docker configuration for Neo4j
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in version control)
├── README.md                 # This file
└── src/                      # Source code
    ├── app.py                # Streamlit application entry point
    ├── config.py             # Configuration management
    ├── orchestrator/         # Langchain orchestration components
    │   ├── __init__.py
    │   └── orchestrator.py   # Main orchestrator implementation
    ├── llm/                  # LLM interface components
    │   ├── __init__.py
    │   ├── query_translator.py  # Cypher query generation
    │   └── answer_generator.py  # Final answer generation
    ├── database/             # Database interaction components
    │   ├── __init__.py
    │   └── neo4j_driver.py   # Neo4j driver implementation
    ├── data_ingestion/       # Data ingestion components
    │   ├── __init__.py
    │   ├── ingest.py         # Main ingestion script
    │   ├── preprocessor.py   # Document preprocessing
    │   └── embedding.py      # Embedding generation
    ├── cache/                # Caching components
    │   ├── __init__.py
    │   └── response_cache.py # Response cache implementation
    └── utils/                # Utility functions
        ├── __init__.py
        ├── error_handler.py  # Error handling
        └── monitoring.py     # Monitoring and logging
```