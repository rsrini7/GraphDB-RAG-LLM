import logging
import json
import os
import time
from typing import Dict, Any, Optional, Union
from pathlib import Path
from config import CACHE_TTL

class ResponseCache:
    """Cache for storing and retrieving responses to avoid redundant LLM calls.
    
    This class implements a simple file-based cache system that stores responses
    with TTL (Time To Live) functionality.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the ResponseCache.
        
        Args:
            cache_dir: Directory to store cache files. If None, uses './cache'.
        """
        self.cache_dir = Path(cache_dir or os.path.join(os.path.dirname(__file__), 'cache_data'))
        self.ttl = CACHE_TTL
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        logging.info(f"Initialized response cache at {self.cache_dir}")
    
    def _get_cache_key(self, question: str) -> str:
        """Generate a cache key from the question.
        
        Args:
            question: The user's question
            
        Returns:
            A string key for cache lookup
        """
        # Simple hashing of the question for the filename
        # In a production system, consider using a more robust hashing method
        import hashlib
        return hashlib.md5(question.lower().strip().encode()).hexdigest()
    
    def get(self, question: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached response for a question if it exists and is not expired.
        
        Args:
            question: The user's question
            
        Returns:
            Cached response dictionary or None if not found or expired
        """
        cache_key = self._get_cache_key(question)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            logging.info(f"Cache miss for question: {question}")
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Check if the cache entry has expired
            timestamp = cached_data.get('timestamp', 0)
            if time.time() - timestamp > self.ttl:
                logging.info(f"Cache expired for question: {question}")
                return None
            
            logging.info(f"Cache hit for question: {question}")
            return cached_data.get('response')
        except Exception as e:
            logging.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def set(self, question: str, response: Dict[str, Any]) -> bool:
        """Store a response in the cache.
        
        Args:
            question: The user's question
            response: The response to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._get_cache_key(question)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_data = {
                'question': question,
                'response': response,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            logging.info(f"Cached response for question: {question}")
            return True
        except Exception as e:
            logging.error(f"Error storing in cache: {str(e)}")
            return False
    
    def clear(self, question: Optional[str] = None) -> bool:
        """Clear cache entries.
        
        Args:
            question: If provided, clears only the cache for this question.
                     If None, clears all cache entries.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if question:
                # Clear specific cache entry
                cache_key = self._get_cache_key(question)
                cache_file = self.cache_dir / f"{cache_key}.json"
                
                if cache_file.exists():
                    os.remove(cache_file)
                    logging.info(f"Cleared cache for question: {question}")
            else:
                # Clear all cache entries
                for cache_file in self.cache_dir.glob('*.json'):
                    os.remove(cache_file)
                logging.info("Cleared all cache entries")
            
            return True
        except Exception as e:
            logging.error(f"Error clearing cache: {str(e)}")
            return False

# Create a singleton instance
response_cache = ResponseCache()