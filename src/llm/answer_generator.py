import logging
from typing import Dict, List, Any, Optional
import json
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, ANSWER_GENERATOR_MODEL  # Changed from relative to absolute import

class AnswerGenerator:
    """Generates natural language answers from graph query results using LLMs via OpenRouter API.
    
    This class is responsible for synthesizing coherent, human-readable answers based on
    the original question, retrieved graph data, and potentially vector search results.
    """
    
    def __init__(self):
        """Initialize the AnswerGenerator with configuration from config module."""
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = ANSWER_GENERATOR_MODEL
        
        if not self.api_key:
            logging.error("OpenRouter API key not found. Please set OPENROUTER_API_KEY environment variable.")
            raise ValueError("OpenRouter API key not found")
    
    def generate_answer(self, question: str, query_results: List[Dict[str, Any]], 
                        cypher_query: str, vector_context: Optional[str] = None) -> str:
        """Generate a natural language answer based on query results and context.
        
        Args:
            question: The original natural language question
            query_results: Results from the Cypher query execution
            cypher_query: The Cypher query that was executed
            vector_context: Optional context from vector search results
            
        Returns:
            Generated natural language answer as a string
        """
        # Prepare the prompt for the LLM
        prompt = self._prepare_prompt(question, query_results, cypher_query, vector_context)
        
        try:
            # Call the OpenRouter API
            response = self._call_openrouter(prompt)
            
            logging.info("Generated answer successfully")
            return response
        except Exception as e:
            logging.error(f"Error generating answer: {str(e)}")
            raise
    
    def _prepare_prompt(self, question: str, query_results: List[Dict[str, Any]], 
                         cypher_query: str, vector_context: Optional[str] = None) -> str:
        """Prepare the prompt for the LLM to generate an answer.
        
        Args:
            question: The original natural language question
            query_results: Results from the Cypher query execution
            cypher_query: The Cypher query that was executed
            vector_context: Optional context from vector search results
            
        Returns:
            Formatted prompt string
        """
        # Format the query results for the prompt
        # Limit the size to avoid token limits
        results_str = json.dumps(query_results, indent=2)[:2000]  # Truncate if too large
        
        # Base prompt
        prompt = f"""
        You are an expert in explaining Neo4j graph database query results in natural language.
        Your task is to generate a clear, concise, and informative answer based on the following information:
        
        USER QUESTION:
        {question}
        
        CYPHER QUERY EXECUTED:
        ```cypher
        {cypher_query}
        ```
        
        QUERY RESULTS:
        ```json
        {results_str}
        ```
        """
        
        # Add vector context if available
        if vector_context:
            prompt += f"""
            
            ADDITIONAL CONTEXT FROM SIMILAR DOCUMENTS:
            {vector_context}
            """
        
        prompt += """
        
        INSTRUCTIONS:
        1. Generate a comprehensive answer to the user's question based on the query results.
        2. Explain the relationships and patterns found in the data.
        3. If the query returned no results or insufficient information, explain this clearly.
        4. Use a conversational and helpful tone.
        5. Do not mention the Cypher query or technical details unless relevant to the answer.
        6. Structure your answer in a readable format with paragraphs and bullet points if appropriate.
        
        ANSWER:
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
                {"role": "system", "content": "You are a helpful assistant that explains graph database query results."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,  # Slightly higher temperature for more creative answers
            "max_tokens": 1000
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

# Create a singleton instance
answer_generator = AnswerGenerator()
