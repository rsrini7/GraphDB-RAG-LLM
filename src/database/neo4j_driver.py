from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
import logging
from config import (
    NEO4J_URI, 
    NEO4J_USERNAME, 
    NEO4J_PASSWORD, 
    EMBEDDING_DIMENSION, 
    VECTOR_INDEX_NAME, 
    VECTOR_NODE_LABEL, 
    VECTOR_PROPERTY
)
from database.vector_search import VectorSearch  # Changed from relative to absolute

class Neo4jDriver:
    """Neo4j database driver for interacting with the Neo4j graph database.
    
    This class provides methods for executing Cypher queries, fetching schema information,
    and managing vector embeddings in the Neo4j database.
    """
    
    def __init__(self):
        """Initialize the Neo4j driver with connection details from config."""
        self.uri = NEO4J_URI
        self.username = NEO4J_USERNAME
        self.password = NEO4J_PASSWORD
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.connect()
        
        # Initialize vector search component
        self.vector_search = VectorSearch(self)
    
    def connect(self):
        """Establish connection to the Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            # Verify connection
            self.driver.verify_connectivity()
            logging.info("Successfully connected to Neo4j database")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j database: {str(e)}")
            raise
    
    def close(self):
        """Close the connection to the Neo4j database."""
        if self.driver:
            self.driver.close()
            logging.info("Neo4j database connection closed")
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return the results.
        
        Args:
            query: The Cypher query to execute
            params: Optional parameters for the query
            
        Returns:
            List of dictionaries containing the query results
        """
        if not self.driver:
            self.connect()
            
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            logging.error(f"Error executing query: {str(e)}\nQuery: {query}\nParams: {params}")
            raise
    
    def perform_vector_search(self, embedding: List[float], node_label: str = VECTOR_NODE_LABEL, 
                     property_name: str = VECTOR_PROPERTY, limit: int = 5, 
                     similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a vector similarity search in the Neo4j database.
        
        Args:
            embedding: The query embedding vector
            node_label: Label of nodes to search (default from config)
            property_name: Name of the property containing embeddings (default from config)
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score to include in results
            
        Returns:
            List of dictionaries containing nodes and their similarity scores
        """
        try:
            return self.vector_search.search(
                embedding=embedding,
                node_label=node_label,
                property_name=property_name,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
        except Exception as e:
            self.logger.error(f"Error in vector search: {str(e)}")
            raise
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Retrieve the database schema information.
        
        Returns:
            Dictionary containing node labels, relationship types, and properties
        """
        # Query to get node labels and their properties
        node_query = """
        CALL db.schema.nodeTypeProperties() 
        YIELD nodeType, propertyName
        RETURN nodeType, collect(propertyName) AS properties
        """
        
        # Query to get relationship types and their properties
        rel_query = """
        CALL db.schema.relTypeProperties()
        YIELD relType, propertyName
        RETURN relType, collect(propertyName) AS properties
        """
        
        try:
            nodes = self.execute_query(node_query)
            relationships = self.execute_query(rel_query)
            
            return {
                "nodes": {node["nodeType"]: node["properties"] for node in nodes},
                "relationships": {rel["relType"]: rel["properties"] for rel in relationships}
            }
        except Exception as e:
            logging.error(f"Error retrieving schema info: {str(e)}")
            raise
    
    def store_vector_embedding(self, node_label: str, properties: Dict[str, Any], embedding: List[float]):
        """Store a vector embedding in the Neo4j database.
        
        Args:
            node_label: The label for the node
            properties: Dictionary of node properties
            embedding: Vector embedding as a list of floats
        """
        query = f"""
        CREATE (n:{node_label} $properties)
        SET n.embedding = $embedding
        RETURN n
        """
        
        params = {
            "properties": properties,
            "embedding": embedding
        }
        
        try:
            self.execute_query(query, params)
            logging.info(f"Stored vector embedding for {node_label} node")
        except Exception as e:
            logging.error(f"Error storing vector embedding: {str(e)}")
            raise
    
    # Note: The vector_search functionality has been moved to the VectorSearch class
    # and is now accessed through the perform_vector_search method

# Singleton instance
neo4j_driver = Neo4jDriver()
