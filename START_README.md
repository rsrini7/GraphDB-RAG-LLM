# GraphRAG Startup Guide

This guide explains how to start the GraphRAG system using the provided helper scripts.

---

## Prerequisites

Before starting, ensure you have:

1. Docker installed and running
2. Python 3.9+ with dependencies installed (`requirements.txt`)
3. An OpenRouter API key (for LLM features)
4. A configured `.env` file (copy from `.env.example` if needed)

---

## Using the Startup Script

The `start-with-docker-compose.sh` script automates the startup process:

- Starts the Neo4j database via Docker Compose
- Waits for Neo4j to be ready
- Checks for environment configuration
- Optionally, you can ingest data before or after startup
- Launches the Streamlit application

### To start the system, run:

```bash
./start-with-docker-compose.sh
```

---

## First-Time Setup

1. Copy `.env.example` to `.env` and add your OpenRouter API key.
2. If no data is present, ingest your data:

```bash
python src/data_ingestion/ingest.py --data-path /path/to/your/data
```

Or use the sample data ingester:

```bash
./sample-data-ingester.sh
```

---

## Alternative: Manual Startup

You can also start components manually:

1. Start Neo4j:

```bash
docker-compose up -d
```

2. Ingest data (if needed):

```bash
python src/data_ingestion/ingest.py --data-path /path/to/your/data
```

3. Launch the app:

```bash
streamlit run src/app.py
```

Or use:

```bash
./run.sh
```

---

## Troubleshooting

- Ensure Docker is running
- Check that ports 7474 and 7687 are free
- Verify `.env` contains valid credentials
- Review logs for errors

---

## Summary

- **Recommended:** `./start-with-docker-compose.sh`
- **Manual:** Start Neo4j, ingest data, then run Streamlit

## Troubleshoot

ERROR:database.vector_search:Error performing vector search: {code: Neo.ClientError.Procedure.ProcedureCallFailed} {message: Failed to invoke procedure `db.index.vector.queryNodes`: Caused by: java.lang.IllegalArgumentException: There is no such vector schema index: Document_embedding_index}
ERROR:database.neo4j_driver:Error in vector search: {code: Neo.ClientError.Procedure.ProcedureCallFailed} {message: Failed to invoke procedure `db.index.vector.queryNodes`: Caused by: java.lang.IllegalArgumentException: There is no such vector schema index: Document_embedding_index}
ERROR:orchestrator.orchestrator:Error performing vector search: {code: Neo.ClientError.Procedure.ProcedureCallFailed} {message: Failed to invoke procedure `db.index.vector.queryNodes`: Caused by: java.lang.IllegalArgumentException: There is no such vector schema index: Document_embedding_index}

then run ./fix-check-vector-index.sh
