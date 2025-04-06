# GraphRAG Startup Guide

This document explains how to use the automated startup script for the GraphRAG system.

## Prerequisites

Before running the startup script, ensure you have:

1. Docker installed and running
2. Python with all required dependencies installed (see `requirements.txt`)
3. An OpenRouter API key (if you plan to use the LLM features)

## Using the Startup Script

The `start.sh` script automates the entire process of starting the GraphRAG system. It will:

1. Check if Docker is running
2. Start the Neo4j database using Docker Compose
3. Wait for Neo4j to be ready and verify the connection
4. Check for environment configuration (.env file)
5. Check if data ingestion is needed
6. Start the Streamlit application

### Running the Script

To start the GraphRAG system, simply run:

```bash
./start.sh
```

### First-Time Setup

If this is your first time running the system:

1. The script will create a basic `.env` file if one doesn't exist
2. You'll need to edit the `.env` file to add your OpenRouter API key
3. If no documents are found in the database, you'll need to run data ingestion:

```bash
python src/data_ingestion/ingest.py --data-path /path/to/your/data
```

## Troubleshooting

If you encounter issues:

1. Ensure Docker is running
2. Check that ports 7474 and 7687 are available for Neo4j
3. Verify your OpenRouter API key is correctly set in the `.env` file
4. Check the logs for any error messages

## Manual Startup (Alternative)

If you prefer to start components manually:

1. Start Neo4j: `docker-compose up -d`
2. Run data ingestion (if needed): `python src/data_ingestion/ingest.py --data-path /path/to/your/data`
3. Start Streamlit: `streamlit run src/app.py`