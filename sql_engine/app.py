from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pandas as pd
from sqlalchemy import inspect, text, create_engine
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://prabal@localhost:5432/prabal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Global variable to store unique values
column_unique_values = {}

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

@app.route('/api/submit-selections', methods=['POST'])
def submit_selections():
    """Accept selections from the frontend and handle them (extendable)"""
    try:
        data = request.get_json()  # The data sent from the frontend

        # Extract the columns and selected values
        selected_columns = data.get('columns', [])
        selected_values = data.get('selected_values', {})

        # For now, print the selections
        print("Selected Columns:", selected_columns)
        print("Selected Values:", selected_values)

        for x,v in selected_values.items():
            print(x,v)

        # You can process this data further here, e.g., perform database queries based on the selected values

        # Respond back with success
        return jsonify({'success': True, 'message': 'Selections received successfully!'}), 200
    except Exception as e:
        print(f"Error in submit-selections: {str(e)}")  # Log the error
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database with sample data
    if init_db():
        print("Database initialized successfully!")
    else:
        print("Failed to initialize database!")
    
    app.run(debug=True, port=5001)
