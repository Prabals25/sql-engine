# Power Query

A natural language to SQL query conversion system that allows users to interact with databases using plain English.

## Setup Instructions

### 1. Environment Setup

1. Create a `.env` file in the root directory of the project with the following variables:
```bash
# Flask Configuration
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DEV_DATABASE_URL=postgresql://user@localhost:5432/db_name
DATABASE_URL=postgresql://user@localhost:5432/db_name
TEST_DATABASE_URL=postgresql://user@localhost:5432/db_name_test

# Server Configuration
PORT=5001
HOST=0.0.0.0
FLASK_DEBUG=True

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
```

2. Replace the following values in the `.env` file:
   - `your-secret-key-here`: A secure random string for Flask session security
   - `user`: Your PostgreSQL username
   - `db_name`: Your database name
   - `db_name_test`: Your test database name
   - `localhost:5432`: Your PostgreSQL host and port (if different)
   - `PORT`: The port number for the Flask server (default: 5001)
   - `HOST`: The host address for the Flask server (default: 0.0.0.0)

### 2. Installation

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Setup

1. Create a PostgreSQL database
2. Run the schema.sql file to create the required tables

### 4. Running the Application

Start the Flask server:
```bash
python app.py
```

The application will be available at `http://localhost:5001` (or the port specified in your .env file).

