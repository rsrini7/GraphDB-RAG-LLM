# GraphRAG - Graph-based Retrieval-Augmented Generation System

This project implements a local Graph-based Retrieval-Augmented Generation (GraphRAG) system that allows users to ask natural language questions via a Streamlit interface. The system leverages a Langchain orchestrator to process questions, perform vector searches and structured graph queries against a local Neo4j database, and use an LLM (via OpenRouter) to generate Cypher queries and synthesize final natural language answers.

---

## Architecture

- **User Interface**: Streamlit web interface
- **Orchestration**: Langchain for coordinating RAG
- **LLM Interface**: OpenRouter API
- **Graph Database**: Neo4j (via Docker Compose) with Vector Index
- **Database Driver**: Neo4j Python Driver
- **Data Processing**: Ingestion, preprocessing, embedding generation
- **Caching**: Response caching for faster repeated queries
- **Utilities**: Monitoring, error handling, dashboard

---

## Documentation

- **DESIGN.md**: System design details
- **INGEST.md**: Data ingestion process
- **REQ.md**: Requirements and dependencies
- **START_README.md**: Quick start guide

---

## Setup Instructions

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- OpenRouter API key

### Installation

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp .env.example .env
   ```
   Edit `.env`:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```

---

## Starting the System

### Option 1: Using Docker Compose and helper script

Start Neo4j and the app together:
```bash
./start-with-docker-compose.sh
```

### Option 2: Manual steps

1. Start Neo4j:
   ```bash
   docker-compose up -d
   ```
2. Ingest your data (see `INGEST.md` for details):
   ```bash
   python src/data_ingestion/ingest.py --data-path /path/to/your/data
   ```
   Or use the sample data ingester:
   ```bash
   ./sample-data-ingester.sh
   ```
3. Launch the app:
   ```bash
   streamlit run src/app.py
   ```
   Or use the convenience script:
   ```bash
   ./run.sh
   ```

---

## Sample Data

Sample datasets are provided in `sample_data/`:

- `agentic_ai.csv`, `llm.csv`: CSV samples
- `agentic_ai.json`, `rag.json`: JSON samples

Use these for testing ingestion.

---

## Usage

- Open [http://localhost:8501](http://localhost:8501)
- Enter your question
- View the generated answer and related info

---

## Project Structure

```
.
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .env
├── README.md
├── DESIGN.md
├── INGEST.md
├── REQ.md
├── START_README.md
├── run.sh
├── start-with-docker-compose.sh
├── sample-data-ingester.sh
├── sample_data/
│   ├── agentic_ai.csv
│   ├── agentic_ai.json
│   ├── llm.csv
│   └── rag.json
└── src/
    ├── app.py
    ├── config.py
    ├── orchestrator/
    │   └── orchestrator.py
    ├── llm/
    │   ├── query_translator.py
    │   └── answer_generator.py
    ├── database/
    │   ├── neo4j_driver.py
    │   └── vector_search.py
    ├── data_ingestion/
    │   ├── ingest.py
    │   ├── preprocessor.py
    │   └── embedding.py
    ├── cache/
    │   └── response_cache.py
    └── utils/
        ├── error_handler.py
        ├── monitoring.py
        └── dashboard.py
```

---

## Notes

- For detailed ingestion instructions, see **INGEST.md**
- For system design, see **DESIGN.md**
- For requirements, see **REQ.md**
- For quick start, see **START_README.md**

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
