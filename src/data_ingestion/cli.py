#!/usr/bin/env python
import argparse
import logging
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_ingestion.ingest import DataIngestion
from utils.monitoring import monitoring

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the data ingestion CLI."""
    parser = argparse.ArgumentParser(description="GraphRAG Data Ingestion Tool")
    
    # Required arguments
    parser.add_argument(
        "--data-path", 
        required=True, 
        help="Path to data file or directory to ingest"
    )
    
    # Optional arguments
    parser.add_argument(
        "--file-type", 
        choices=["csv", "json", "txt"], 
        help="Filter by file type when ingesting a directory"
    )
    parser.add_argument(
        "--chunk-size", 
        type=int, 
        default=512, 
        help="Maximum size of text chunks in characters"
    )
    parser.add_argument(
        "--chunk-overlap", 
        type=int, 
        default=50, 
        help="Overlap between chunks in characters"
    )
    parser.add_argument(
        "--embedding-model", 
        default=None, 
        help="Name of the SentenceTransformer model to use for embeddings"
    )
    parser.add_argument(
        "--clear-existing", 
        action="store_true", 
        help="Clear existing data before ingestion"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize the data ingestion component
        data_ingestion = DataIngestion()
        
        # Log the start of ingestion
        logger.info(f"Starting data ingestion from: {args.data_path}")
        monitoring.log_activity("data_ingestion_started", {
            "data_path": args.data_path,
            "file_type": args.file_type,
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap
        })
        
        # Clear existing data if requested
        if args.clear_existing:
            logger.info("Clearing existing data before ingestion")
            data_ingestion.clear_existing_data()
        
        # Configure the preprocessor with the specified chunk size and overlap
        data_ingestion.preprocessor.chunk_size = args.chunk_size
        data_ingestion.preprocessor.chunk_overlap = args.chunk_overlap
        
        # Configure the embedding generator with the specified model if provided
        if args.embedding_model:
            data_ingestion.embedding_generator.model_name = args.embedding_model
            data_ingestion.embedding_generator._load_model()
        
        # Perform the data ingestion
        data_ingestion.ingest_data(
            data_path=args.data_path,
            file_type=args.file_type
        )
        
        # Log successful completion
        logger.info("Data ingestion completed successfully")
        monitoring.log_activity("data_ingestion_completed", {
            "data_path": args.data_path,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        monitoring.log_activity("data_ingestion_error", {
            "data_path": args.data_path,
            "error": str(e)
        })
        sys.exit(1)

if __name__ == "__main__":
    main()