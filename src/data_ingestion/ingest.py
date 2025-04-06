import logging
import argparse
import os
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import nltk
nltk.download('punkt', quiet=True)

from .preprocessor import document_preprocessor
from .embedding import embedding_generator
from database.neo4j_driver import neo4j_driver
from utils.monitoring import monitoring
from utils.error_handler import error_handler

class DataIngestion:
    """Main data ingestion script for the GraphRAG system.
    
    This class is responsible for reading data from source files, preprocessing it,
    generating embeddings, and storing the data in the Neo4j database.
    """
    
    def __init__(self):
        """Initialize the DataIngestion component."""
        self.logger = logging.getLogger(__name__)
        self.preprocessor = document_preprocessor
        self.embedding_generator = embedding_generator
        self.db_driver = neo4j_driver
        
    def clear_existing_data(self):
        """Clear existing data from the Neo4j database.
        
        This method removes all document nodes and their associated embeddings.
        """
        try:
            # Delete all document nodes and their relationships
            cypher_query = """
            MATCH (d:Document) 
            DETACH DELETE d
            """
            self.db_driver.execute_query(cypher_query)
            
            self.logger.info("Cleared existing document data from the database")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing existing data: {str(e)}")
            raise
    
    @error_handler.with_error_handling()
    @monitoring.time_function("data_ingestion")
    def ingest_data(self, data_path: str, file_type: Optional[str] = None):
        """Main method to ingest data from files.
        
        Args:
            data_path: Path to the data file or directory
            file_type: Optional file type to filter by (csv, json, txt)
        """
        data_path = Path(data_path)
        
        if data_path.is_file():
            self._process_file(data_path)
        elif data_path.is_dir():
            self._process_directory(data_path, file_type)
        else:
            raise ValueError(f"Data path does not exist: {data_path}")
    
    def _process_directory(self, directory: Path, file_type: Optional[str] = None):
        """Process all files in a directory.
        
        Args:
            directory: Path to the directory
            file_type: Optional file type to filter by
        """
        self.logger.info(f"Processing directory: {directory}")
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                if file_type and file_path.suffix.lower() != f".{file_type.lower()}":
                    continue
                self._process_file(file_path)
            elif file_path.is_dir():
                # Recursively process subdirectories
                self._process_directory(file_path, file_type)
    
    def _process_file(self, file_path: Path):
        """Process a single file based on its type.
        
        Args:
            file_path: Path to the file
        """
        self.logger.info(f"Processing file: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == ".csv":
                self._process_csv(file_path)
            elif file_extension == ".json":
                self._process_json(file_path)
            elif file_extension in [".txt", ".md", ".html"]:
                self._process_text(file_path)
            else:
                self.logger.warning(f"Unsupported file type: {file_extension}")
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            # Continue with other files instead of raising
    
    def _process_csv(self, file_path: Path):
        """Process a CSV file.
        
        Args:
            file_path: Path to the CSV file
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Get column names
            columns = df.columns.tolist()
            
            # Determine node labels and relationship structure based on the CSV structure
            # This is a simplified approach - in a real system, you might want to provide a mapping configuration
            primary_label = file_path.stem.capitalize()
            
            # Process each row
            for _, row in df.iterrows():
                # Convert row to dictionary
                properties = row.to_dict()
                
                # Create node in Neo4j
                self._create_graph_node(primary_label, properties)
                
                # Check if any columns contain text that should be vectorized
                for col in columns:
                    if isinstance(properties.get(col), str) and len(properties.get(col, "")) > 100:
                        # This column contains substantial text, process it for vector embedding
                        self._process_text_content(
                            properties.get(col),
                            metadata={
                                "source": file_path.name,
                                "node_label": primary_label,
                                "node_properties": {k: v for k, v in properties.items() if k != col}
                            }
                        )
        except Exception as e:
            self.logger.error(f"Error processing CSV file {file_path}: {str(e)}")
            raise
    
    def _process_json(self, file_path: Path):
        """Process a JSON file.
        
        Args:
            file_path: Path to the JSON file
        """
        try:
            # Read JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # List of objects
                primary_label = file_path.stem.capitalize()
                
                for item in data:
                    if isinstance(item, dict):
                        # Create node in Neo4j
                        self._create_graph_node(primary_label, item)
                        
                        # Process text fields for vector embedding
                        for key, value in item.items():
                            if isinstance(value, str) and len(value) > 100:
                                self._process_text_content(
                                    value,
                                    metadata={
                                        "source": file_path.name,
                                        "node_label": primary_label,
                                        "node_properties": {k: v for k, v in item.items() if k != key}
                                    }
                                )
            elif isinstance(data, dict):
                # Single object or complex structure
                # For simplicity, we'll create a node for the top-level object
                primary_label = file_path.stem.capitalize()
                self._create_graph_node(primary_label, data)
                
                # Process text fields for vector embedding
                self._process_nested_dict(data, file_path.name, primary_label)
        except Exception as e:
            self.logger.error(f"Error processing JSON file {file_path}: {str(e)}")
            raise
    
    def _process_nested_dict(self, data: Dict[str, Any], source: str, parent_label: str, parent_props: Dict[str, Any] = None):
        """Process a nested dictionary for text fields.
        
        Args:
            data: Dictionary to process
            source: Source file name
            parent_label: Label of the parent node
            parent_props: Properties of the parent node
        """
        if parent_props is None:
            parent_props = {}
        
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 100:
                # Process text for vector embedding
                self._process_text_content(
                    value,
                    metadata={
                        "source": source,
                        "node_label": parent_label,
                        "node_properties": {**parent_props, key: "[TEXT]"},
                        "field_name": key
                    }
                )
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                child_label = f"{parent_label}{key.capitalize()}"
                self._create_graph_node(child_label, value)
                self._process_nested_dict(value, source, child_label, {**parent_props, "parent": parent_label})
            elif isinstance(value, list):
                # Process list items
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        child_label = f"{parent_label}{key.capitalize()}"
                        self._create_graph_node(child_label, {**item, "index": i})
                        self._process_nested_dict(item, source, child_label, {**parent_props, "parent": parent_label})
                    elif isinstance(item, str) and len(item) > 100:
                        # Process text for vector embedding
                        self._process_text_content(
                            item,
                            metadata={
                                "source": source,
                                "node_label": parent_label,
                                "node_properties": {**parent_props, key: f"[LIST_ITEM_{i}]"},
                                "field_name": f"{key}[{i}]"
                            }
                        )
    
    def _process_text(self, file_path: Path):
        """Process a text file.
        
        Args:
            file_path: Path to the text file
        """
        try:
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create metadata
            metadata = {
                "source": file_path.name,
                "file_path": str(file_path),
                "file_type": file_path.suffix.lower()[1:]
            }
            
            # Process text content
            self._process_text_content(content, metadata)
        except Exception as e:
            self.logger.error(f"Error processing text file {file_path}: {str(e)}")
            raise
    
    def _process_text_content(self, text: str, metadata: Dict[str, Any]):
        """Process text content for vector embedding.
        
        Args:
            text: Text content to process
            metadata: Metadata to associate with the text
        """
        # Preprocess the text into chunks
        chunks = self.preprocessor.preprocess(text, metadata)
        
        # Generate embeddings for the chunks
        chunks_with_embeddings = self.embedding_generator.process_chunks(chunks)
        
        # Store the chunks and embeddings in Neo4j
        for chunk in chunks_with_embeddings:
            self._store_document_with_embedding(chunk)
    
    def _create_graph_node(self, label: str, properties: Dict[str, Any]):
        """Create a node in the Neo4j graph database.
        
        Args:
            label: Node label
            properties: Node properties
        """
        # Clean properties (remove None values and non-primitive types)
        cleaned_props = {}
        for key, value in properties.items():
            if value is not None and isinstance(value, (str, int, float, bool, list)):
                if isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) for item in value):
                    cleaned_props[key] = value
                elif not isinstance(value, list):
                    cleaned_props[key] = value
        
        # Create Cypher query
        query = f"""
        CREATE (n:{label} $properties)
        RETURN n
        """
        
        params = {"properties": cleaned_props}
        
        try:
            self.db_driver.execute_query(query, params)
            self.logger.info(f"Created {label} node with properties: {cleaned_props}")
        except Exception as e:
            self.logger.error(f"Error creating graph node: {str(e)}")
            raise
    
    def _store_document_with_embedding(self, chunk: Dict[str, Any]):
        """Store a document chunk with its embedding in Neo4j.
        
        Args:
            chunk: Document chunk with text, embedding, and metadata
        """
        # Extract data from chunk
        text = chunk["text"]
        embedding = chunk["embedding"]
        metadata = chunk.get("metadata", {})
        chunk_id = chunk.get("chunk_id", 0)
        total_chunks = chunk.get("total_chunks", 1)
        
        # Prepare properties
        properties = {
            "text": text,
            "chunk_id": chunk_id,
            "total_chunks": total_chunks,
            **metadata
        }
        
        # Store in Neo4j with vector embedding
        try:
            self.db_driver.store_vector_embedding("Document", properties, embedding)
            self.logger.info(f"Stored document chunk {chunk_id+1}/{total_chunks} with embedding")
        except Exception as e:
            self.logger.error(f"Error storing document with embedding: {str(e)}")
            raise

# Create a singleton instance
data_ingestion = DataIngestion()

# Command-line interface
def main():
    parser = argparse.ArgumentParser(description="Ingest data into the GraphRAG system")
    parser.add_argument("--data-path", required=True, help="Path to data file or directory")
    parser.add_argument("--file-type", help="Filter by file type (csv, json, txt)")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run ingestion
    data_ingestion.ingest_data(args.data_path, args.file_type)
    
    print(f"Data ingestion completed for {args.data_path}")

if __name__ == "__main__":
    main()
