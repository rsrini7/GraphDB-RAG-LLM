import time
import logging
from typing import Dict, Any, Optional
from database.neo4j_driver import Neo4jDriver
from llm.query_translator import QueryTranslator
from llm.answer_generator import AnswerGenerator
from utils.error_handler import error_handler
from utils.monitoring import monitoring
from data_ingestion.preprocessor import document_preprocessor
from data_ingestion.embedding import embedding_generator
from database.neo4j_driver import neo4j_driver
from cache.response_cache import response_cache

class Orchestrator:
    """Central orchestrator for the GraphRAG system.
    
    This class coordinates the entire RAG process, including caching, query translation,
    database interaction, and answer generation.
    """
    
    def __init__(self):
        """Initialize the Orchestrator."""
        self.logger = logging.getLogger(__name__)
        self.query_translator = QueryTranslator()
        self.answer_generator = AnswerGenerator()
        self.db_driver = neo4j_driver
        self.cache = response_cache
        self.preprocessor = document_preprocessor
        self.embedding_generator = embedding_generator
    
    @error_handler.with_error_handling()
    @monitoring.time_function("process_question")
    def process_question(self, question: str) -> Dict[str, Any]:
        """Process a natural language question and generate an answer.
        
        Args:
            question: The natural language question from the user
            
        Returns:
            Dictionary containing the answer and additional information
        """
        # Log the activity
        monitoring.log_activity("question_received", {"question": question})
        
        # Check cache for existing results
        cached_result = self.cache.get(question)
        if cached_result:
            monitoring.log_activity("cache_hit", {"question": question})
            return cached_result
        
        monitoring.log_activity("cache_miss", {"question": question})
        
        # Get schema information from the database
        schema_info = self.db_driver.get_schema_info()
        
        # Perform vector search if applicable
        vector_context = self._perform_vector_search(question)
        
        # Generate Cypher query
        cypher_query = self.query_translator.generate_cypher(
            question=question,
            schema_info=schema_info,
            vector_context=vector_context
        )
        
        monitoring.log_activity("cypher_generated", {"cypher_query": cypher_query})
        
        # Execute Cypher query
        query_results = self.db_driver.execute_query(cypher_query)
        
        monitoring.log_activity("query_executed", {
            "cypher_query": cypher_query,
            "result_count": len(query_results)
        })
        
        # Generate answer
        answer = self.answer_generator.generate_answer(
            question=question,
            query_results=query_results,
            cypher_query=cypher_query,
            vector_context=vector_context
        )
        
        monitoring.log_activity("answer_generated", {"question": question})
        
        # Prepare result
        result = {
            "question": question,
            "answer": answer,
            "cypher_query": cypher_query,
            "query_results": query_results,
            "timestamp": time.time()
        }
        
        # Cache the result
        self.cache.set(question, result)
        
        return result
    
    def _perform_vector_search(self, question: str) -> Optional[str]:
        """Perform vector search to find similar documents.
        
        Args:
            question: The natural language question
            
        Returns:
            String containing context from similar documents, or None if not applicable
        """
        try:
            # Preprocess the question
            processed_question = self.preprocessor.preprocess(question)[0]
            
            # Generate embedding for the question
            question_embedding = self.embedding_generator.generate_embedding(processed_question["text"])
            
            # Perform vector search in Neo4j
            search_results = self.db_driver.perform_vector_search(
                embedding=question_embedding,
                node_label="Document",
                limit=3,  # Get top 3 most similar documents
                similarity_threshold=0.5  # Only include results with similarity >= 0.5
            )
            
            if not search_results:
                return None
            
            # Format the context from similar documents
            context_parts = []
            for i, result in enumerate(search_results):
                node = result["node"]
                similarity = result["similarity"]
                
                # Note: We're already filtering by similarity_threshold in perform_vector_search
                
                context_parts.append(f"Document {i+1} (Similarity: {similarity:.2f}):\n{node.get('text', '')}\n")
            
            if not context_parts:
                return None
            
            return "\n".join(context_parts)
        except Exception as e:
            self.logger.error(f"Error performing vector search: {str(e)}")
            return None

# Create a singleton instance
orchestrator = Orchestrator()
