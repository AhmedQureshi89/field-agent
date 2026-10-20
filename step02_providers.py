"""
STEP 02 · Lesson 2 · One agent, any provider

The agent loop does not care who serves the model. Prove it: run the same prompt
against every endpoint you have and compare latency and style.

Run:   python step02_providers.py
Edit the PROVIDERS list, or set AGENT_BASE_URL / AGENT_MODEL / AGENT_API_KEY in .env.
"""
import os
import time

from openai import OpenAI

from core import say

PROVIDERS = [
    # name,        base_url,                         model,          api key
    ("ollama",     "http://localhost:11434/v1",      "qwen2.5:7b",   "ollama"),
    ("lmstudio",   "http://localhost:1234/v1",       "local-model",  "lm-studio"),
    # ("foundry",  os.getenv("AGENT_BASE_URL", ""),  os.getenv("AGENT_MODEL", ""), os.getenv("AGENT_API_KEY", "")),
]

PROMPT = "In one sentence: what is an AI agent, and what is it not?"

if __name__ == "__main__":
    for name, base, model, key in PROVIDERS:
        if not base:
            continue
        client = OpenAI(base_url=base, api_key=key)
        t0 = time.perf_counter()
        try:
            r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": PROMPT}])
            say("llm", f"{name:9} {time.perf_counter() - t0:5.1f}s  {r.choices[0].message.content.strip()}")
        except Exception as exc:
            say("sys", f"{name:9} unavailable: {exc.__class__.__name__}")
    print("\nNotice: only the client changed. The loop, the prompt and the tools stay the same.")
