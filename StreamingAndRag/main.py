from openAiHelpers import stream_complete, rollup_chat, rag_style_prompt

# 1.  A normal chat loop
chat_history = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain the FastAPI lifecycle in detail."},
]
answer = stream_complete(chat_history, temperature=0.7)
chat_history.append({"role": "assistant", "content": answer})

# 2.  Keep the window tidy every N turns
chat_history = rollup_chat(chat_history)

# 3.  Process a huge PDF you’ve extracted to text
with open("StreamingAndRag\whitepaper.txt",encoding="utf-8") as f:
    big_text = f.read()
summary = rag_style_prompt(big_text,
                           "Summarise each chunk in 5 bullets.")
