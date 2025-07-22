import json
from Response import execute_openai_batch_job

sql_queries = [
    "SELECT * FROM users WHERE status = 'active';",
    "UPDATE products SET price = price * 1.1 WHERE category = 'electronics';",
    "CREATE INDEX idx_customer_name ON customers (name);"
]

batch_requests = []
for i, query in enumerate(sql_queries):
    request = {
        "custom_id": f"sql_task_{i+1}",
        "method": "POST",
        "url": "/chat/completions",
        "body": {
            "model": "gpt-4.1-2",
            "messages": [{"role": "user", "content": f"Explain this SQL query:\n{query}"}]
        }
    }
    batch_requests.append(json.dumps(request))

print(batch_requests)
# Example: Writing to a JSONL file
with open("sql_explanation_batch.jsonl", "w") as f:
    for line in batch_requests:
        f.write(line + "\n")



execute_openai_batch_job("C:\\Users\\srivarshan\\Desktop\\OpenAIBatchAPI\\sql_explanation_batch.jsonl","/v1/chat/completions","gpt-4.1")

