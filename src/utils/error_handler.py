import logging
from typing import Callable, Any, Dict, Optional
import traceback
from functools import wraps

class ErrorHandler:
    """Centralized error handling for the GraphRAG system."""
    
    def __init__(self):
        """Initialize the ErrorHandler."""
        self.logger = logging.getLogger(__name__)

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle an exception and return an error response dictionary.
        
        Args:
            error: The exception that occurred
            context: Optional context about where/when the error occurred
            
        Returns:
            Dict containing error details and user-friendly message
        """
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Log the full error details
        self.logger.error(f"Error type: {error_type}")
        self.logger.error(f"Error message: {error_message}")
        self.logger.error(f"Stack trace: {stack_trace}")
        if context:
            self.logger.error(f"Error context: {context}")
        
        return {
            "status": "error",
            "error_type": error_type,
            "error_message": error_message,
            "user_message": self.get_user_friendly_message(error_type, error_message),
            "context": context or {},
            "stack_trace": stack_trace
        }

    def with_error_handling(self, fallback_return: Any = None):
        """Decorator for functions that need standardized error handling.
        
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
                    error_response = self.handle_error(e, {
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    })
                    return fallback_return if fallback_return is not None else error_response
            return wrapper
        return decorator

    def get_user_friendly_message(self, error_type: str, error_message: str) -> str:
        """Convert error details into a user-friendly message.
        
        Args:
            error_type: The type/class of the error
            error_message: The original error message
            
        Returns:
            A user-friendly error message string
        """
        if "NoneType" in error_message and "not subscriptable" in error_message:
            if "OpenRouter API endpoint not found" in error_message:
                return "Unable to connect to the AI service. Please check your OpenRouter API configuration and make sure you have a valid API key."
            return "The system received an unexpected response. Please try again or contact support if the issue persists."
            
        if error_type == "ValueError":
            if "OpenRouter API key not found" in error_message:
                return "The OpenRouter API key is missing. Please add your API key to the .env file."
            elif "OpenRouter API endpoint not found" in error_message:
                return "Unable to connect to OpenRouter API. Please check your API configuration."
            elif "Invalid OpenRouter API key" in error_message:
                return "Your OpenRouter API key appears to be invalid. Please check your API key configuration."
            return f"Invalid input or configuration: {error_message}"
            
        if error_type == "ConnectionError":
            return "Unable to connect to required services. Please check your internet connection and try again."
            
        if error_type == "TimeoutError":
            return "The request timed out. Please try again later."
            
        # Default user-friendly message for unknown errors
        return "An unexpected error occurred. Please try again or contact support if the issue persists."

# Create a singleton instance
error_handler = ErrorHandler()