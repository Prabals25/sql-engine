from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model_path = 'gaussalgo/T5-LM-Large-text2sql-spider'
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

question = "What's the mom growth rate for the region with the highest sales?"
schema = """
   "sampledb" "order_date" date , "region" text , "rep" text , "item" text , "units" int , "unit_cost" decimal , "total" decimal , foreign_key: , primary key: "id"
"""

input_text = " ".join(["Question: ",question, "Schema:", schema])

model_inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(**model_inputs, max_length=512)

output_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)

print("SQL Query:")
print(output_text)
