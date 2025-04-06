import logging
from typing import List, Dict, Any, Optional
import numpy as np

class VectorSearch:
    """
    Vector search functionality for the Neo4j database.
    
    This class provides methods for performing vector similarity searches
    in the Neo4j database using vector indexes.
    """
    
    def __init__(self, neo4j_driver):
        """Initialize the VectorSearch with a Neo4j driver.
        
        Args:
            neo4j_driver: Instance of Neo4jDriver for database interaction
        """
        self.logger = logging.getLogger(__name__)
        self.driver = neo4j_driver
    
    def search(self, embedding: List[float], node_label: str = "Document", 
               property_name: str = "embedding", limit: int = 5, 
               similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Perform a vector similarity search in the Neo4j database.
        
        Args:
            embedding: The query embedding vector
            node_label: Label of nodes to search (default: "Document")
            property_name: Name of the property containing embeddings (default: "embedding")
            limit: Maximum number of results to return (default: 5)
            similarity_threshold: Minimum similarity score to include in results (default: 0.5)
            
        Returns:
            List of dictionaries containing nodes and their similarity scores
        """
        try:
            # Construct the Cypher query for vector search
            cypher_query = f"""
            CALL db.index.vector.queryNodes($index_name, $k, $embedding)
            YIELD node, score
            WHERE score >= $threshold
            RETURN node, score
            LIMIT $limit
            """
            
            # Prepare parameters
            params = {
                "index_name": f"{node_label}_{property_name}_index",
                "k": limit * 2,  # Request more results than needed to filter by threshold
                "embedding": embedding,
                "threshold": similarity_threshold,
                "limit": limit
            }
            
            # Execute the query
            results = self.driver.execute_query(cypher_query, params)
            
            # Format the results
            formatted_results = []
            for record in results:
                formatted_results.append({
                    "node": dict(record["node"]),
                    "similarity": record["score"]
                })
            
            self.logger.info(f"Vector search returned {len(formatted_results)} results")
            return formatted_results
        
        except Exception as e:
            self.logger.error(f"Error performing vector search: {str(e)}")
            raise
    
    def create_vector_index(self, node_label: str = "Document", 
                           property_name: str = "embedding", 
                           dimension: int = 384) -> bool:
        """Create a vector index in the Neo4j database.
        
        Args:
            node_label: Label of nodes to index (default: "Document")
            property_name: Name of the property containing embeddings (default: "embedding")
            dimension: Dimension of the embedding vectors (default: 384)
            
        Returns:
            Boolean indicating success
        """
        try:
            # Construct the Cypher query for creating a vector index
            cypher_query = f"""
            CALL db.index.vector.createNodeIndex(
                $index_name,
                $node_label,
                $property_name,
                $dimension,
                $similarity_metric
            )
            """
            
            # Prepare parameters
            params = {
                "index_name": f"{node_label}_{property_name}_index",
                "node_label": node_label,
                "property_name": property_name,
                "dimension": dimension,
                "similarity_metric": "cosine"
            }
            
            # Execute the query
            self.driver.execute_query(cypher_query, params)
            
            self.logger.info(f"Created vector index for {node_label}.{property_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating vector index: {str(e)}")
            raise
    
    def drop_vector_index(self, node_label: str = "Document", 
                         property_name: str = "embedding") -> bool:
        """Drop a vector index from the Neo4j database.
        
        Args:
            node_label: Label of nodes in the index (default: "Document")
            property_name: Name of the property in the index (default: "embedding")
            
        Returns:
            Boolean indicating success
        """
        try:
            # Construct the Cypher query for dropping a vector index
            cypher_query = f"""
            CALL db.index.vector.deleteNodeIndex($index_name)
            """
            
            # Prepare parameters
            params = {
                "index_name": f"{node_label}_{property_name}_index"
            }
            
            # Execute the query
            self.driver.execute_query(cypher_query, params)
            
            self.logger.info(f"Dropped vector index for {node_label}.{property_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error dropping vector index: {str(e)}")
            raise
    
    def list_vector_indexes(self) -> List[Dict[str, Any]]:
        """List all vector indexes in the Neo4j database.
        
        Returns:
            List of dictionaries containing index information
        """
        try:
            # Construct the Cypher query for listing vector indexes
            cypher_query = """
            CALL db.index.vector.list()
            YIELD name, type, labelsOrTypes, properties, dimension, similarityFunction
            RETURN name, type, labelsOrTypes, properties, dimension, similarityFunction
            """
            
            # Execute the query
            results = self.driver.execute_query(cypher_query)
            
            # Format the results
            formatted_results = []
            for record in results:
                formatted_results.append({
                    "name": record["name"],
                    "type": record["type"],
                    "labels_or_types": record["labelsOrTypes"],
                    "properties": record["properties"],
                    "dimension": record["dimension"],
                    "similarity_function": record["similarityFunction"]
                })
            
            self.logger.info(f"Listed {len(formatted_results)} vector indexes")
            return formatted_results
        
        except Exception as e:
            self.logger.error(f"Error listing vector indexes: {str(e)}")
            raise