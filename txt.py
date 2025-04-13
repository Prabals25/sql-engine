from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

def load_model():
    """
    Load the Text2SQL model and tokenizer
    """
    try:
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained("yasserrmd/Text2SQL-1.5B")
        model = AutoModelForCausalLM.from_pretrained("yasserrmd/Text2SQL-1.5B")
        
        # Define the pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        return pipe
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

def generate_sql(pipe, user_query, system_instruction=None):
    """
    Generate SQL from natural language query
    
    Args:
        pipe: Hugging Face pipeline
        user_query: Natural language query
        system_instruction: Optional system instruction
        
    Returns:
        Generated SQL query
    """
    if not pipe:
        return "Error: Model not loaded"
        
    try:
        # Default system instruction if none provided
        if not system_instruction:
            system_instruction = """
            Always separate code and explanation. Return SQL code in a separate block, 
            followed by the explanation in a separate paragraph. Use markdown triple 
            backticks (```sql for SQL) to format the code properly. Write the SQL 
            query first in a separate code block. Then, explain the query in plain text. 
            Do not merge them into one response.
            """
            
        # Define messages for input
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_query},
        ]
        
        # Generate SQL output
        response = pipe(messages)
        
        # Extract and return the generated text
        return response[0]['generated_text']
        
    except Exception as e:
        print(f"Error generating SQL: {str(e)}")
        return f"Error: {str(e)}"

def main():
    # Load the model
    pipe = load_model()
    if not pipe:
        print("Failed to load model")
        return
        
    # Example user query
    user_query = """
    Show the total sales for each customer who has spent more than $50,000.
    
    CREATE TABLE sales (
        id INT PRIMARY KEY,
        customer_id INT,
        total_amount DECIMAL(10,2),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    
    CREATE TABLE customers (
        id INT PRIMARY KEY,
        name VARCHAR(255)
    );
    """
    
    # Generate SQL
    result = generate_sql(pipe, user_query)
    print("\nGenerated SQL:")
    print(result)

if __name__ == "__main__":
    main() 