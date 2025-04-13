import ollama
import json

class OllamaLLM:
    """
    A class to handle interactions with the Ollama LLM model and SQL query validation.
    This class combines the functionality of both OllamaLLM and SQLQueryValidator.
    """
    def __init__(self, model_name="sqls"):
        """
        Initialize the OllamaLLM class

        Args:
            model_name (str): Name of the Ollama model to use
        """
        # Initialize the Ollama client
        self.client = ollama.Client()
        self.model = model_name

    def generate_response(self, prompt):
        """
        Generate a response from the Ollama model
        
        Args:
            prompt (str): The input prompt to send to the model
            
        Returns:
            dict: Parsed JSON response from the model
        """
        try:
            # Send the query to the model
            print("Model being used: ", self.model)
            response = self.client.generate(model=self.model, prompt=prompt)
            
            # Get the response text and clean it
            resp = str(response.response).strip()
            print("Response inside generate_response function: ", resp)
            # Parse and return JSON response
            return json.loads(resp)
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None

    def set_model(self, model_name):
        """
        Change the model being used
        
        Args:
            model_name (str): New model name to use
        """
        self.model = model_name

    def generate_initial_sql(self, user_query):
        """
        Generate initial SQL query based on user's natural language query.
        
        Args:
            user_query (str): Natural language query from user
            
        Returns:
            dict: Response containing success status and SQL query
        """
        # Use the existing generate_response method with SQL model
        response = self.generate_response(user_query)
        
        if not response or 'sql_ans' not in response:
            return {
                'success': False,
                'error': 'Failed to generate SQL query'
            }
            
        if response['sql_ans'] == 'nan':
            return {
                'success': False,
                'error': 'Invalid query or question not related to database'
            }
            
        return {
            'success': True,
            'sql_query': response['sql_ans']
        }
    
    def create_query_object(self, user_query, generated_sql, columns, selected_values):
        """
        Create a query object for validation.
        
        Args:
            user_query (str): Original user query
            generated_sql (str): Generated SQL query
            columns (list): Selected columns
            selected_values (dict): Selected filter values
            
        Returns:
            dict: Query object for validation
        """
        return {
            "user_selections": {
                "columns": columns,
                "selected_values": selected_values
            },
            "user_query": user_query,
            "generated_sql": generated_sql
        }
    
    def validate_and_update_sql(self, query_object):
        """
        Validate and update SQL query based on user selections.
        
        Args:
            query_object (dict): Query object containing user selections and SQL
            
        Returns:
            dict: Response containing success status and updated SQL query
        """
        try:
            # Switch to checker model for validation
            self.set_model("checker")
            query_str = json.dumps(query_object)
            print("Query string: ", query_str)
            response = self.generate_response(query_str)

            print("Response: ", response)
            
            if not response or 'updated_sql' not in response:
                return {
                    'success': False,
                    'error': 'Failed to validate SQL query'
                }
                
            return {
                'success': True,
                'sql_query': response['updated_sql'],
                'comments': response['comments']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Reset model back to default
            self.set_model("sqls")

# # Example usage:
# llm = OllamaLLM()
# initial_response = llm.generate_initial_sql("What is the total sales for each region segment by product type?")
# if initial_response['success']:
#     query_obj = llm.create_query_object(
#         "What is the total sales for each region segment by product type?",
#         initial_response['sql_query'],
#         ["region", "total"],
#         {"region": ["East", "South"]}
#     )
#     final_response = llm.validate_and_update_sql(query_obj)
#     print(final_response)
#     print(initial_response['sql_query'])

