# PostgreSQL database configuration
from sqlalchemy import create_engine,text

# query = '''
# SELECT region, SUM(total) AS total_sales 
# FROM sampledb 
# GROUP BY region 
# ORDER BY total_sales DESC 
# LIMIT 1
# '''

query = '''SELECT region, rep, SUM(units * unit_cost) AS sales_amount, SUM(units) AS unit_sold
FROM sampledb
WHERE rep IN ('Gill', 'Kivell') AND item IN ('Desk', 'Pen Set')
GROUP BY region, rep'''

def execute_sql_query(query):
    """
    Execute a SQL query on the PostgreSQL database and return the results
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        dict: Dictionary containing query results with columns and data
    """
    try:
        # Import SQLAlchemy create_engine
        # Create database engine
        engine = create_engine('postgresql://prabal@localhost:5432/prabal')
        
        # Execute query and fetch results
        with engine.connect() as connection:
            result = connection.execute(text(query))
            
            # Get column names
            columns = result.keys()
            
            # Fetch all rows
            rows = result.fetchall()
            
            # Convert rows to list of dictionaries
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
                
            return {
                'success': True,
                'columns': columns,
                'data': data,
                'count': len(data)
            }
            
    except Exception as e:
        return {
            'success': False, 
            'error': str(e)
        }


print(execute_sql_query(query))