import logging
from typing import Dict, Any, Optional
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, QUERY_TRANSLATOR_MODEL  # Changed from relative to absolute import

class QueryTranslator:
    """Translates natural language questions into Cypher queries using LLMs via OpenRouter API.
    
    This class is responsible for generating valid Neo4j Cypher queries based on
    natural language questions and database schema information.
    """
    
    def __init__(self):
        """Initialize the QueryTranslator with configuration from config module."""
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = QUERY_TRANSLATOR_MODEL
        
        if not self.api_key:
            logging.error("OpenRouter API key not found. Please set OPENROUTER_API_KEY environment variable.")
            raise ValueError("OpenRouter API key not found")
    
    def generate_cypher(self, question: str, schema_info: Dict[str, Any], 
                        vector_context: Optional[str] = None) -> str:
        """Generate a Cypher query from a natural language question.
        
        Args:
            question: The natural language question
            schema_info: Database schema information (node labels, relationship types, properties)
            vector_context: Optional context from vector search results
            
        Returns:
            Generated Cypher query as a string
        """
        # Prepare the prompt for the LLM
        prompt = self._prepare_prompt(question, schema_info, vector_context)
        
        try:
            # Call the OpenRouter API
            response = self._call_openrouter(prompt)
            
            # Extract and validate the Cypher query
            cypher_query = self._extract_cypher(response)
            
            logging.info(f"Generated Cypher query: {cypher_query}")
            return cypher_query
        except Exception as e:
            logging.error(f"Error generating Cypher query: {str(e)}")
            raise
    
    def _prepare_prompt(self, question: str, schema_info: Dict[str, Any], 
                         vector_context: Optional[str] = None) -> str:
        """Prepare the prompt for the LLM to generate a Cypher query.
        
        Args:
            question: The natural language question
            schema_info: Database schema information
            vector_context: Optional context from vector search results
            
        Returns:
            Formatted prompt string
        """
        # Format the schema information for the prompt
        nodes_str = "\n".join([f"- {label}: {', '.join(props)}" 
                           for label, props in schema_info.get("nodes", {}).items()])
        
        relationships_str = "\n".join([f"- {rel_type}: {', '.join(props)}" 
                                  for rel_type, props in schema_info.get("relationships", {}).items()])
        
        # Base prompt
        prompt = f"""
        You are an expert in translating natural language questions into Neo4j Cypher queries.
        Your task is to generate a valid Cypher query based on the following information:
        
        DATABASE SCHEMA:
        Node Labels and Properties:
        {nodes_str}
        
        Relationship Types and Properties:
        {relationships_str}
        
        USER QUESTION:
        {question}
        """
        
        # Add vector context if available
        if vector_context:
            prompt += f"""
            
            ADDITIONAL CONTEXT FROM SIMILAR DOCUMENTS:
            {vector_context}
            """
        
        prompt += """
        
        INSTRUCTIONS:
        1. Generate a valid Neo4j Cypher query that answers the user's question.
        2. Use only the node labels, relationship types, and properties defined in the schema.
        3. Return ONLY the Cypher query without any explanations or markdown formatting.
        4. Ensure the query is optimized and follows Neo4j best practices.
        5. If the question cannot be answered with the given schema, return a simple query that explains the limitation.
        
        CYPHER QUERY:
        """
        
        return prompt
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call the OpenRouter API to generate a response.
        
        Args:
            prompt: The formatted prompt string
            
        Returns:
            Generated text response from the LLM
            
        Raises:
            ValueError: If the API call fails with a detailed error message
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a Neo4j Cypher query generator."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Low temperature for more deterministic outputs
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            error_msg = f"OpenRouter API request failed: {str(e)}"
            if response.status_code == 404:
                error_msg = "OpenRouter API endpoint not found. Please check your OPENROUTER_BASE_URL configuration."
            elif response.status_code == 401:
                error_msg = "Invalid OpenRouter API key. Please check your OPENROUTER_API_KEY configuration."
            logging.error(error_msg)
            raise ValueError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while calling OpenRouter API: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            error_msg = f"Invalid response from OpenRouter API: {str(e)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
    
    def _extract_cypher(self, response: str) -> str:
        """Extract and validate the Cypher query from the LLM response.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            Cleaned Cypher query string
        """
        # Remove any markdown code block formatting if present
        if "```" in response:
            # Extract content between code blocks
            parts = response.split("```")
            for part in parts:
                if part.strip().lower().startswith("cypher"):
                    return part.strip()[6:].strip()  # Remove 'cypher' and whitespace
                elif not part.strip().startswith("```") and len(part.strip()) > 0:
                    return part.strip()
        
        # If no code blocks, return the response as is
        return response.strip()

# Create a singleton instance
query_translator = QueryTranslator()
