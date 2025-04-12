import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")

# LLM Model Configuration
QUERY_TRANSLATOR_MODEL = os.getenv("QUERY_TRANSLATOR_MODEL", "openrouter/optimus-alpha")
ANSWER_GENERATOR_MODEL = os.getenv("ANSWER_GENERATOR_MODEL", "openrouter/optimus-alpha")

# Embedding Model Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # Dimension for the specified model

# Vector Search Configuration
VECTOR_INDEX_NAME = "document_embeddings"
VECTOR_NODE_LABEL = "Document"
VECTOR_PROPERTY = "embedding"

# Cache Configuration
# Time to live in seconds (default: 1 hour)
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")