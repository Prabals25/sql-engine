from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def main():
    # Load tokenizer and model
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained("yasserrmd/Text2SQL-1.5B")
    model = AutoModelForCausalLM.from_pretrained("yasserrmd/Text2SQL-1.5B")

    # Define the pipeline
    print("Setting up pipeline...")
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

    # Define system instruction
    system_instruction = """Always separate code and explanation. Return SQL code in a separate block, followed by the explanation in a separate paragraph. Use markdown triple backticks (```sql for SQL) to format the code properly. Write the SQL query first in a separate code block. Then, explain the query in plain text. Do not merge them into one response. The query should always include the table structure using a CREATE TABLE statement before executing the main SQL query."""

    # Define user query
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

    # Define messages for input
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_query},
    ]

    # Generate SQL output
    print("Generating SQL...")
    response = pipe(messages)

    # Print the generated SQL query
    print("\nGenerated SQL:")
    print(response[0]['generated_text'])

if __name__ == "__main__":
    main()
