import os, itertools, math
from dataclasses import dataclass
from typing import Iterable, List
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import tiktoken

# ---------- 0.  CONFIG ----------
load_dotenv()

# old
# ENCODING = tiktoken.encoding_for_model("gpt-4.1")

# new – try official mapping first, else fall back
try:
    ENCODING = tiktoken.encoding_for_model("gpt-4.1")
except KeyError:
    ENCODING = tiktoken.get_encoding("o200k_base")  # GPT-4.1/4o/o-series
  # cl100k_base alias
CTX_LIMIT   = 1_000_000           # gpt-4.1 window  :contentReference[oaicite:0]{index=0}
OUT_LIMIT   = 32_768              # per-call completion cap  :contentReference[oaicite:1]{index=1}
DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_TOKEN"),
    api_version="2025-03-01-preview",  # or the version you're using
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# ---------- 1.  TOKEN COUNT ----------
def n_tokens(messages: list[dict]) -> int:
    text = "".join(m["content"] for m in messages)
    return len(ENCODING.encode(text))

# ---------- 2.  STREAM + AUTO-CONTINUE ----------
def stream_complete(
    messages: list[dict],
    max_tokens: int = 10_000,      # pick what you expect, ≤ OUT_LIMIT
    **kwargs
) -> str:
    """Streams until finish_reason=='stop', auto-issuing 'continue' when needed."""
    full = ""
    while True:
        stream = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            **kwargs
        )

        finish_reason = None
        for chunk in stream:
            if not chunk.choices:          # skip “[DONE]” sentinel
             continue
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)   # <-- or buffer
                full += delta.content
            finish_reason = chunk.choices[0].finish_reason or finish_reason

        if finish_reason == "stop":
            return full

        if finish_reason == "length":
            messages += [
                {"role": "assistant", "content": full},
                {"role": "user", "content": "continue"}
            ]
            full = ""
        else:
            raise RuntimeError(f"Unexpected finish_reason: {finish_reason}")

# ---------- 3.  SLIDING-WINDOW SUMMARISER ----------
def rollup_chat(history: list[dict], every_n_turns: int = 8) -> list[dict]:
    """When history grows, summarise the older part to stay < CTX_LIMIT."""
    if len(history) < every_n_turns or n_tokens(history) < 0.8 * CTX_LIMIT:
        return history  # nothing to do

    summary = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "system",
                   "content": "Summarise the conversation so far in 150 words."},
                  *history],
        max_tokens=512,
        temperature=0.2,
    ).choices[0].message.content

    return [{"role": "assistant", "content": summary}] + history[-every_n_turns:]

# ---------- 4.  LARGE-INPUT CHUNKER ----------
def chunks(text: str, chunk_tokens: int = 8_192) -> Iterable[str]:
    ids = ENCODING.encode(text)
    for i in range(0, len(ids), chunk_tokens):
        yield ENCODING.decode(ids[i:i + chunk_tokens])

def rag_style_prompt(long_text: str, system_prompt: str) -> str:
    """Example pattern: summarise each slice, then stitch."""
    summaries = []
    for part in chunks(long_text):
        msg = [{"role": "system", "content": system_prompt},
               {"role": "user", "content": part}]
        summaries.append(stream_complete(msg, max_tokens=1024, temperature=0.3))
    combined = "\n\n".join(summaries)
    final = stream_complete(
        [{"role": "system", "content": "Fuse these into one coherent answer:"},
         {"role": "user", "content": combined}],
        max_tokens=2048
    )
    return final
