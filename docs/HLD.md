# Power Query - High Level Design Document

## 1. Introduction

### 1.1 Purpose
Power Query is a natural language to SQL query conversion system that allows users to interact with databases using plain English. The system uses Large Language Models (LLMs) to generate and validate SQL queries based on user input and selections. MOAT : 2 LLMs (Just Llama 3.2) sequential decomposition leading to excellent results. Agentic decomposition can result in excellent results.

### 1.2 System Overview
The system consists of a web-based frontend that communicates with a backend service. The backend uses LLMs to process natural language queries and generate SQL queries, which are then executed against a PostgreSQL database.

## 2. System Architecture

### 2.1 High-Level Components
```
┌───────────────┐     ┌──────────────────────┐      ┌─────────────┐
│  Frontend     │     │   Backend            │      │  Database   │
│(HTML,CSS & JS)|◄───►│ (Flask)-LLM Pipeline │◄────►│ (PostgreSQL)│
└───────────────┘     └──────────────────────┘      └─────────────┘
```

### 2.2 Component Details

#### 2.2.1 Frontend
- **Technology**: React.js with Bootstrap
- **Key Features**:
  - User query input interface
  - Column selection interface
  - Value filtering interface
  - Results display
  - Query history visualization
- **Directory Structure**:
  - `static/`: Static assets (CSS, JS, images)
  - `templates/`: HTML templates
  - `static/js/`: Frontend JavaScript code

#### 2.2.2 Backend
- **Technology**: Flask (Python)
- **Key Components**:
  - API endpoints for query processing
  - LLM integration (Ollama)
  - Database connection management
  - Query logging system
- **Directory Structure**:
  - `sql_engine/`: Main application code
  - `models/`: LLM and database models
  - `utils/`: Utility functions
  - `logs/`: Query execution logs

#### 2.2.3 Database
- **Technology**: PostgreSQL
- **Features**:
  - Sample sales data
  - Optimized for query performance
  - Schema validation
- **Table Structure**:
  ```sql
  CREATE TABLE sampledb (
      id SERIAL PRIMARY KEY,
      order_date DATE,
      region VARCHAR(50),
      rep VARCHAR(100),
      item VARCHAR(100),
      units INTEGER,
      unit_cost DECIMAL(10,2),
      total DECIMAL(10,2)
  );
  ```

## 3. Data Flow

### 3.1 Query Processing Flow
1. User submits natural language query and selections
2. Frontend sends data to backend API
3. Backend processes query through LLM pipeline:
   - First LLM generates initial SQL
   - Second LLM validates and updates SQL
4. Backend executes final SQL query
5. Results are returned to frontend
6. Frontend displays results

### 3.2 LLM Pipeline
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  User Query │     │  Initial    │     │  Final SQL  │
│ & Selections│────►│  SQL Gen    │────►│  Validation │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 4. Key Features

### 4.1 Natural Language Processing
- Converts plain English to SQL
- Handles complex queries
- Supports filtering and aggregation
- Uses Ollama LLM for query generation

### 4.2 Query Validation
- Validates generated SQL
- Ensures query safety
- Optimizes query performance
- Uses Ollama LLM for validation

### 4.3 Data Filtering
- Column selection
- Value filtering
- Dynamic filter generation
- Unique value retrieval

### 4.4 Logging and Monitoring
- Query execution logging
- Error tracking
- Performance monitoring
- Log file management

## 5. API Endpoints

### 5.1 Query Processing
- **POST /api/submit-selections**
  - Accepts user query and selections
  - Returns query results
  - Request format:
    ```json
    {
        "query": "natural language query",
        "columns": ["column1", "column2"],
        "selected_values": {
            "column1": ["value1", "value2"]
        }
    }
    ```

### 5.2 Schema Information
- **GET /api/schema**
  - Returns database schema information
  - Used for column selection
  - Response format:
    ```json
    {
        "columns": ["column1", "column2"],
        "types": ["type1", "type2"]
    }
    ```

### 5.3 Unique Values
- **GET /api/unique-values**
  - Returns unique values for categorical columns
  - Used for value filtering
  - Response format:
    ```json
    {
        "column_name": ["value1", "value2"]
    }
    ```

## 6. Error Handling

### 6.1 Error Types
- Query generation errors
- SQL validation errors
- Database execution errors
- API request errors

### 6.2 Error Response Format
```json
{
    "success": false,
    "error": "Error message",
    "details": "Additional error details"
}
```

## 7. Security Considerations

### 7.1 Input Validation
- Sanitize user inputs
- Validate SQL queries
- Prevent SQL injection
- CORS configuration

### 7.2 API Security
- Request validation
- Rate limiting
- Environment variable protection
- Secure database credentials

## 8. Performance Considerations

### 8.1 Query Optimization
- Query caching
- Index optimization
- Result pagination
- Database connection pooling

### 8.2 System Performance
- Load balancing
- Resource management
- Response time optimization
- Log file rotation

## 9. Deployment

### 9.1 Requirements
- Python 3.8+
- PostgreSQL 12+
- Ollama LLM service (hosted locally)
- Required Python packages (requirements.txt):
  ```
  flask
  flask-sqlalchemy
  flask-cors
  pandas
  python-dotenv
  ollama
  ```

### 9.2 Environment Variables
```
FLASK_CONFIG=development
DATABASE_URL=postgresql://user:pass@localhost:5432/db
OLLAMA_HOST=http://localhost:11434
```

## 10. Monitoring and Maintenance

### 10.1 Logging
- Query execution logs
- Error logs
- Performance metrics
- Log file rotation

### 10.2 Monitoring
- System health checks
- Performance monitoring
- Error tracking
- Resource utilization

## 11. Future Enhancements

### 11.1 Planned Features
- Query/Chat history.
- Database automation.
- Vector DB Integrating and Query caching.
- Multi Agentic Decomposition of initial queries.
- Implementing guardrails in SQL queries.
- E2E deployment on cloud.

### 11.2 Scalability
- Horizontal scaling
- Database sharding
- Caching layer
- Load balancing

## 12. Conclusion

This HLD document provides a comprehensive overview of the Power Query system architecture and design. The system is designed to be scalable, maintainable, and user-friendly while ensuring robust query generation and execution capabilities.

## 13. References

1. [A Survey on Employing Large Language Models for Text-to-SQL Tasks](https://arxiv.org/pdf/2407.15186)
2. [https://arxiv.org/pdf/2312.11242](https://arxiv.org/pdf/2312.11242)
3. [Evaluating and Enhancing LLMs for Multi-turnText-to-SQL with Multiple Question Types](https://arxiv.org/pdf/2412.17867) 
