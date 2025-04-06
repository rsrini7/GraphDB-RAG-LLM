import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
import json
from datetime import datetime

class Monitoring:
    """Monitoring and logging for the GraphRAG system.
    
    This class provides methods for logging activities, tracking metrics,
    and monitoring the performance of the system.
    """
    
    def __init__(self):
        """Initialize the Monitoring system."""
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging configuration."""
        # Configure logging format and level
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log an activity with details.
        
        Args:
            activity_type: Type of activity (e.g., 'query', 'answer', 'error')
            details: Dictionary with activity details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_type,
            "details": details
        }
        
        # Log as JSON for easier parsing
        self.logger.info(f"ACTIVITY: {json.dumps(log_entry)}")
        
        # Update metrics
        self._update_metrics(activity_type, details)
    
    def _update_metrics(self, activity_type: str, details: Dict[str, Any]):
        """Update internal metrics based on activity.
        
        Args:
            activity_type: Type of activity
            details: Activity details
        """
        # Initialize counter if not exists
        if activity_type not in self.metrics:
            self.metrics[activity_type] = {
                "count": 0,
                "details": {}
            }
        
        # Increment counter
        self.metrics[activity_type]["count"] += 1
        
        # Update specific metrics based on activity type
        if activity_type == "query":
            # Track query types
            query_type = details.get("query_type", "unknown")
            if query_type not in self.metrics[activity_type]["details"]:
                self.metrics[activity_type]["details"][query_type] = 0
            self.metrics[activity_type]["details"][query_type] += 1
        
        elif activity_type == "error":
            # Track error types
            error_type = details.get("error_type", "unknown")
            if error_type not in self.metrics[activity_type]["details"]:
                self.metrics[activity_type]["details"][error_type] = 0
            self.metrics[activity_type]["details"][error_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics.
        
        Returns:
            Dictionary with current metrics
        """
        return self.metrics
    
    def time_function(self, activity_name: Optional[str] = None):
        """Decorator to measure and log function execution time.
        
        Args:
            activity_name: Name of the activity for logging
            
        Returns:
            Decorated function with timing
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                execution_time = end_time - start_time
                activity = activity_name or func.__name__
                
                self.log_activity("timing", {
                    "activity": activity,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                })
                
                return result
            return wrapper
        return decorator
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {}
        self.logger.info("Metrics reset")

# Create a singleton instance
monitoring = Monitoring()