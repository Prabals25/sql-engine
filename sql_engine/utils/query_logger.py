import os
from datetime import datetime
import json

class QueryLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
        
    def _ensure_log_dir(self):
        """Ensure the log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def _get_log_file(self):
        """Get the current log file path based on date"""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"queries_{today}.log")
        
    def log_query(self, success, user_query, selected_columns, selected_values, final_query, comments, error=None):
        """
        Log query execution details
        
        Args:
            success (bool): Whether the query was successful
            user_query (str): The original user query
            selected_columns (list): Selected columns
            selected_values (dict): Selected filter values
            final_query (str): The final SQL query generated
            comments (str): Comments from the LLM
            error (str, optional): Error message if query failed
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "user_query": user_query,
            "selected_columns": selected_columns,
            "selected_values": selected_values,
            "final_query": final_query,
            "comments": comments,
            "error": error
        }
        
        # Write to log file
        with open(self._get_log_file(), "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        # Also print to console for immediate feedback
        print("\n=== Query Execution Log ===")
        print(f"Timestamp: {log_entry['timestamp']}")
        print(f"Success: {success}")
        print(f"User Query: {user_query}")
        print(f"Selected Columns: {selected_columns}")
        print(f"Selected Values: {selected_values}")
        print(f"Final Query: {final_query}")
        print(f"Comments: {comments}")
        if error:
            print(f"Error: {error}")
        print("=========================\n") 