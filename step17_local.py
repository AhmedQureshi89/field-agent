"""
STEP 17 · Lesson 17 · Fully local, with a sensitivity router

Everything in this project already runs on Ollama. This step makes the choice explicit:
a router sends SENSITIVE requests (salary, patient, password, contract...) to the local
model no matter what, HARD requests to the cloud when a cloud endpoint is configured,
and everything else local. It also measures latency so you can argue with numbers.

Run:   python step17_local.py
"""
import os
import re
import time

from openai import OpenAI

import step04_tools  # noqa: F401
import step05_rag  # noqa: F401
from core import run_agent, say

LOCAL = OpenAI(base_url=os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1"), api_key="ollama")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "qwen2.5:7b")
CLOUD = OpenAI(base_url=os.environ["CLOUD_BASE_URL"], api_key=os.environ["CLOUD_API_KEY"]) if os.getenv("CLOUD_BASE_URL") else None
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "")

SENSITIVE = re.compile(r"salary|password|patient|contract|iban|national id|confidential", re.I)
HARD = re.compile(r"prove|derive|architecture|trade-?offs|compare .* and .*", re.I)


def route(q: str):
    if SENSITIVE.search(q):
        return "local (sensitive)", LOCAL, LOCAL_MODEL
    if HARD.search(q) and CLOUD:
        return "cloud (hard)", CLOUD, CLOUD_MODEL
    return "local", LOCAL, LOCAL_MODEL


if __name__ == "__main__":
    print("cloud configured" if CLOUD else "no cloud endpoint: everything stays on this machine")
    while True:
        user = input("\nyou > ").strip()
        if user in {"quit", "exit"}:
            break
        where, client, model = route(user)
        say("sys", f"ROUTE -> {where} · {model}")
        t0 = time.perf_counter()
        run_agent([{"role": "system", "content": "You are Field Agent. Use tools. Be brief."}, {"role": "user", "content": user}], client=client, model=model)
        say("sys", f"latency {time.perf_counter() - t0:.1f}s")
