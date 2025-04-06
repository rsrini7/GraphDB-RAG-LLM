import logging
from typing import Callable, Any, Dict, Optional
import traceback
from functools import wraps

class ErrorHandler:
    """Centralized error handling for the GraphRAG system.
    
    This class provides methods for catching and handling exceptions,
    implementing error recovery strategies, and logging errors.
    """
    
    def __init__(self):
        """Initialize the ErrorHandler."""
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle an exception and return an appropriate response.
        
        Args:
            error: The exception that was raised
            context: Optional context information about where the error occurred
            
        Returns:
            Dictionary with error information and status
        """
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Log the error with context
        self.logger.error(
            f"Error: {error_type}: {error_message}\n"
            f"Context: {context}\n"
            f"Stack trace: {stack_trace}"
        )
        
        # Prepare error response
        error_response = {
            "status": "error",
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        return error_response
    
    def with_error_handling(self, fallback_return: Any = None):
        """Decorator for functions to add error handling.
        
        Args:
            fallback_return: Value to return if an error occurs
            
        Returns:
            Decorated function with error handling
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context = {
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                    self.handle_error(e, context)
                    return fallback_return
            return wrapper
        return decorator
    
    def get_user_friendly_message(self, error_response: Dict[str, Any]) -> str:
        """Generate a user-friendly error message.
        
        Args:
            error_response: The error response dictionary
            
        Returns:
            User-friendly error message string
        """
        error_type = error_response.get("error_type", "Unknown error")
        error_message = error_response.get("error_message", "An unknown error occurred")
        
        # Map error types to user-friendly messages
        if error_type == "ConnectionError":
            return "Could not connect to the database. Please check that Neo4j is running."
        elif error_type == "AuthenticationError":
            return "Database authentication failed. Please check your credentials."
        elif error_type == "SyntaxError" and "Cypher" in error_message:
            return "There was an issue with the generated database query. Please try rephrasing your question."
        elif error_type == "ValueError" and "API key" in error_message:
            return "Missing API key. Please check your environment variables."
        elif error_type == "TimeoutError":
            return "The request timed out. Please try again later."
        else:
            return f"An error occurred: {error_message}"

# Create a singleton instance
error_handler = ErrorHandler()