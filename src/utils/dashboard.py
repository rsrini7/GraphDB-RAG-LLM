import streamlit as st
import pandas as pd
import altair as alt
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging

class MonitoringDashboard:
    """
    Dashboard for visualizing system metrics and activity.
    
    This class provides methods for creating and updating visualizations
    of system performance, query history, and component status.
    """
    
    def __init__(self):
        """Initialize the MonitoringDashboard."""
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "response_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "total_queries": 0,
            "error_count": 0,
            "component_status": {}
        }
        self.activity_log = []
    
    def update_metrics(self, metric_type: str, value: Any):
        """Update dashboard metrics.
        
        Args:
            metric_type: Type of metric to update
            value: Value to update with
        """
        try:
            if metric_type == "response_time":
                self.metrics["response_times"].append({
                    "timestamp": datetime.now().isoformat(),
                    "value": value
                })
            elif metric_type == "cache_hit":
                self.metrics["cache_hits"] += 1
                self.metrics["total_queries"] += 1
            elif metric_type == "cache_miss":
                self.metrics["cache_misses"] += 1
                self.metrics["total_queries"] += 1
            elif metric_type == "error":
                self.metrics["error_count"] += 1
            elif metric_type == "component_status":
                self.metrics["component_status"].update(value)
            
            self.logger.debug(f"Updated dashboard metric: {metric_type}")
        except Exception as e:
            self.logger.error(f"Error updating dashboard metric: {str(e)}")
    
    def log_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log an activity for the dashboard.
        
        Args:
            activity_type: Type of activity
            details: Dictionary with activity details
        """
        try:
            self.activity_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": activity_type,
                "details": details
            })
            
            # Keep log at a reasonable size
            if len(self.activity_log) > 100:
                self.activity_log = self.activity_log[-100:]
                
            self.logger.debug(f"Logged activity: {activity_type}")
        except Exception as e:
            self.logger.error(f"Error logging activity: {str(e)}")
    
    def render_performance_metrics(self):
        """Render performance metrics visualizations."""
        try:
            st.subheader("Performance Metrics")
            
            # Calculate derived metrics
            total_queries = self.metrics["total_queries"]
            cache_hit_rate = 0
            if total_queries > 0:
                cache_hit_rate = (self.metrics["cache_hits"] / total_queries) * 100
                
            avg_response_time = 0
            if self.metrics["response_times"]:
                response_times = [item["value"] for item in self.metrics["response_times"]]
                avg_response_time = sum(response_times) / len(response_times)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Avg. Response Time", value=f"{avg_response_time:.2f}s")
            with col2:
                st.metric(label="Cache Hit Rate", value=f"{cache_hit_rate:.1f}%")
            with col3:
                st.metric(label="Total Queries", value=total_queries)
            
            # Create response time chart if we have data
            if self.metrics["response_times"]:
                # Convert to DataFrame for charting
                df = pd.DataFrame(self.metrics["response_times"])
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                
                # Create chart
                chart = alt.Chart(df).mark_line().encode(
                    x='timestamp:T',
                    y='value:Q'
                ).properties(
                    title='Response Time Trend'
                )
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No response time data available yet.")
        except Exception as e:
            self.logger.error(f"Error rendering performance metrics: {str(e)}")
            st.error("Error rendering performance metrics.")
    
    def render_activity_log(self):
        """Render activity log visualizations."""
        try:
            st.subheader("Recent Activity")
            
            if not self.activity_log:
                st.info("No activity recorded yet.")
                return
            
            # Convert to DataFrame for display
            df = pd.DataFrame(self.activity_log)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Format for display
            display_df = df.copy()
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
            display_df["details"] = display_df["details"].apply(lambda x: str(x)[:50] + "..." if len(str(x)) > 50 else str(x))
            
            st.dataframe(display_df[["timestamp", "type", "details"]], use_container_width=True)
            
            # Activity type distribution
            if len(df) > 1:
                activity_counts = df["type"].value_counts().reset_index()
                activity_counts.columns = ["Activity Type", "Count"]
                
                st.bar_chart(activity_counts.set_index("Activity Type"))
        except Exception as e:
            self.logger.error(f"Error rendering activity log: {str(e)}")
            st.error("Error rendering activity log.")
    
    def render_system_status(self):
        """Render system status visualizations."""
        try:
            st.subheader("System Status")
            
            # Default component status if not set
            if not self.metrics["component_status"]:
                components = [
                    {"Component": "Neo4j Database", "Status": "Unknown", "Details": "Status not checked"},
                    {"Component": "LLM Service", "Status": "Unknown", "Details": "Status not checked"},
                    {"Component": "Vector Index", "Status": "Unknown", "Details": "Status not checked"},
                    {"Component": "Cache", "Status": "Unknown", "Details": "Status not checked"}
                ]
            else:
                components = []
                for component, status in self.metrics["component_status"].items():
                    components.append({
                        "Component": component,
                        "Status": status.get("status", "Unknown"),
                        "Details": status.get("details", "")
                    })
            
            # Display as a table
            st.table(pd.DataFrame(components))
            
            # Error rate
            error_rate = 0
            if self.metrics["total_queries"] > 0:
                error_rate = (self.metrics["error_count"] / self.metrics["total_queries"]) * 100
            
            st.metric(
                label="System Error Rate", 
                value=f"{error_rate:.2f}%",
                delta="0%"
            )
        except Exception as e:
            self.logger.error(f"Error rendering system status: {str(e)}")
            st.error("Error rendering system status.")
    
    def render_dashboard(self):
        """Render the complete monitoring dashboard."""
        try:
            st.header("System Monitoring Dashboard")
            
            tabs = st.tabs(["Performance Metrics", "Recent Activity", "System Status"])
            
            with tabs[0]:
                self.render_performance_metrics()
            
            with tabs[1]:
                self.render_activity_log()
            
            with tabs[2]:
                self.render_system_status()
                
        except Exception as e:
            self.logger.error(f"Error rendering dashboard: {str(e)}")
            st.error(f"Error rendering dashboard: {str(e)}")

# Create a singleton instance
monitoring_dashboard = MonitoringDashboard()