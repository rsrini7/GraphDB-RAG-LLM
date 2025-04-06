#!/bin/bash

# GraphRAG Startup Script
# This script automates the startup process for the GraphRAG system

set -e  # Exit immediately if a command exits with a non-zero status

echo "===== Starting GraphRAG System ====="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

echo "[1/4] Starting Neo4j database with Docker Compose..."
if ! docker-compose up -d; then
  echo "Error: Failed to start Neo4j with Docker Compose."
  exit 1
fi

# Wait for Neo4j to be ready
echo "[2/4] Waiting for Neo4j to be ready..."
MAX_RETRIES=30
COUNTER=0
while ! docker exec neo4j-graphrag cypher-shell -u neo4j -p password "RETURN 1;" > /dev/null 2>&1; do
  if [ $COUNTER -eq $MAX_RETRIES ]; then
    echo "Error: Neo4j did not become ready in time."
    exit 1
  fi
  echo "Waiting for Neo4j to be ready... ($COUNTER/$MAX_RETRIES)"
  sleep 2
  COUNTER=$((COUNTER+1))
done
echo "Neo4j is ready!"

# Check if .env file exists
echo "[3/4] Checking environment configuration..."
if [ ! -f ".env" ]; then
  echo "Warning: .env file not found. Creating a basic .env file with default values."
  cat > .env << EOL
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
# Add your OpenRouter API key below
OPENROUTER_API_KEY=<REPLACE-KEY>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
QUERY_TRANSLATOR_MODEL=openrouter/quasar-alpha
ANSWER_GENERATOR_MODEL=openrouter/quasar-alpha
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CACHE_TTL=3600
LOG_LEVEL=INFO
EOL
  echo "Created .env file. Please edit it to add your OpenRouter API key."
fi

# Check if data ingestion is needed
echo "[4/4] Checking if data ingestion is needed..."
DOCUMENT_COUNT=$(docker exec neo4j-graphrag cypher-shell -u neo4j -p password "MATCH (d:Document) RETURN count(d) as count;" 2>/dev/null | grep -o '[0-9]\+' || echo "0")

if [ "$DOCUMENT_COUNT" -eq "0" ]; then
  echo "No documents found in the database. You may need to run data ingestion."
  echo "To ingest data, run: python src/data_ingestion/ingest.py --data-path /path/to/your/data"
else
  echo "Found $DOCUMENT_COUNT documents in the database."
fi

# Start the Streamlit application
echo "===== Starting Streamlit Application ====="
streamlit run src/app.py