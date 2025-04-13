from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
from sqlalchemy import inspect, text, create_engine
import os
from dotenv import load_dotenv
from datetime import datetime
from models.llm_ollama import *
from utils.query_logger import QueryLogger
from config import config

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the app based on environment
config_name = os.getenv('FLASK_CONFIG', 'default')
app.config.from_object(config[config_name])

# Initialize extensions
CORS(app)
db = SQLAlchemy(app)

# Initialize query logger
query_logger = QueryLogger()

# Initialize LLM models
llm = OllamaLLM()

# Global variable to store unique values
column_unique_values = {}

def run_query(sql_query):
    """Run a SQL query and return the results as JSON"""
    print(f"Running query: {sql_query}")
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                # Get column names and convert to list
                columns = list(result.keys())
                # Fetch all rows
                rows = result.fetchall()
                # Convert rows to list of dictionaries
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                print(f"Query executed successfully")
                return {
                    'success': True,
                    'columns': columns,
                    'data': data,
                    'count': len(data)
                }
    except Exception as e:
        # Log the error and return an error response
        print(f"Error executing query: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
        

def init_db():
    """Initialize the database with tables based on SampleDB.csv"""
    try:
        # Read the CSV file
        df = pd.read_csv('SampleDB.csv')
        
        # Convert OrderDate to datetime
        df['OrderDate'] = pd.to_datetime(df['OrderDate'])
        
        with app.app_context():
            with db.engine.connect() as conn:
                # Create a single sampledb table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sampledb (
                        id SERIAL PRIMARY KEY,
                        order_date DATE,
                        region VARCHAR(50),
                        rep VARCHAR(100),
                        item VARCHAR(100),
                        units INTEGER,
                        unit_cost DECIMAL(10,2),
                        total DECIMAL(10,2)
                    );
                """))
                
                # Check if table is empty
                result = conn.execute(text("SELECT COUNT(*) FROM sampledb"))
                if result.scalar() == 0:
                    # Insert data from CSV
                    for _, row in df.iterrows():
                        conn.execute(text("""
                            INSERT INTO sampledb (order_date, region, rep, item, units, unit_cost, total)
                            VALUES (:date, :region, :rep, :item, :units, :cost, :total)
                        """), {
                            'date': row['OrderDate'],
                            'region': row['Region'],
                            'rep': row['Rep'],
                            'item': row['Item'],
                            'units': row['Units'],
                            'cost': row['UnitCost'],
                            'total': row['Total']
                        })
                
                # Store unique values only for categorical columns
                for column in ['region', 'rep', 'item']:
                    result = conn.execute(text(f"SELECT DISTINCT {column} FROM sampledb ORDER BY {column}"))
                    values = [str(row[0]) for row in result.fetchall()]
                    # Print the values to verify they are unique
                    print(f"Unique {column} values: {values}")
                    # Store unique values as a list with no duplicates
                    column_unique_values[column] = list(set(values))
                
                conn.commit()
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False
    return True

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Get database schema information"""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        schema_info = {}
        
        for table in tables:
            columns = inspector.get_columns(table)
            schema_info[table] = [
                {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col.get('nullable', True)
                }
                for col in columns
            ]
        
        return jsonify({'success': True, 'schema': schema_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/unique-values', methods=['GET'])
def get_unique_values():
    """Get unique values for all columns"""
    try:
        return jsonify({'success': True, 'unique_values': column_unique_values})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def process_user_query(user_query, columns, selected_values):
    """
    Process user query using the LLM pipeline
    
    Args:
        user_query (str): Natural language query
        columns (list): Selected columns
        selected_values (dict): Selected filter values
        
    Returns:
        dict: Response containing SQL query and status
    """
    try:
        # Generate initial SQL query
        print("columns: ", columns)
        print("selected_values: ", selected_values)

        initial_response = llm.generate_initial_sql(user_query)
        if not initial_response['success']:
            return initial_response
            
        print("Initial query: ", initial_response['sql_query'])
        # Create query object for validation
        query_obj = llm.create_query_object(
            user_query,
            initial_response['sql_query'],
            columns,
            selected_values
        )

        print("Query object: ", query_obj)
        
        # Validate and update SQL
        final_response = llm.validate_and_update_sql(query_obj)

        print("Final query: ", final_response['sql_query'])
        print("comments: ", final_response['comments'])
        return final_response
        
    except Exception as e:
        print(f"Error in process_user_query: {str(e)}")  # Add detailed error logging
        return {
            'success': False,
            'error': str(e),
            'comments': 'Error occurred during query processing',
            'sql_query': ''
        }

@app.route('/api/submit-selections', methods=['POST'])
def submit_selections():
    """Accept selections from the frontend and handle them"""
    try:
        data = request.get_json()
        
        # Extract the columns and selected values
        selected_columns = data.get('columns', [])
        selected_values = data.get('selected_values', {})
        user_query = data.get('user_query', '')

        print("selected_columns: ", selected_columns)
        print("selected_values: ", selected_values)
        print("user_query: ", user_query)
        
        # Process the query through the LLM pipeline
        query_response = process_user_query(user_query, selected_columns, selected_values)
        
        # Log the entire query response
        query_logger.log_query(
            success=query_response['success'],
            user_query=user_query,
            selected_columns=selected_columns,
            selected_values=selected_values,
            final_query=query_response.get('sql_query', ''),
            comments=query_response.get('comments', ''),
            error=query_response.get('error', '')
        )
        
        if not query_response['success']:
            return jsonify({
                'success': False,
                'error': query_response.get('error', 'Failed to process query')
            }), 400
            
        # Execute the final SQL query
        query_results = run_query(query_response['sql_query'])
        
        if not query_results['success']:
            return jsonify({
                'success': False,
                'error': query_results['error']
            }), 400
            
        # Return the complete response
        return jsonify({
            'success': True,
            'message': 'Query processed successfully!',
            'user_query': user_query,
            'sql_query': query_response['sql_query'],
            'columns': query_results['columns'],
            'data': query_results['data'],
            'count': query_results['count']
        })
            
    except Exception as e:
        # Log error
        query_logger.log_query(
            success=False,
            user_query=user_query,
            selected_columns=selected_columns,
            selected_values=selected_values,
            final_query='',
            comments='',
            error=str(e)
        )
        print(f"Error in submit-selections: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize database with sample data
    if init_db():
        print("Database initialized successfully!")
    else:
        print("Failed to initialize database!")
    
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 5001))
    # Get host from environment variable or use default
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
