"""
STEP 16 · Lesson 16 · Ship it as a service

The agent becomes a stateless HTTP endpoint: threads live in a dict keyed by session id
(swap for Redis or a database later), simple requests route to a small model, repeated
questions hit a cache, and refunds above a threshold need approval. A smoke test hits
the live endpoint after deploy.

Install:  pip install fastapi uvicorn
Run:      uvicorn step16_serve:app --reload
Smoke:    python step16_serve.py smoke
Docker:   docker build -t field-agent . ; docker run -p 8000:8000 field-agent
"""
import hashlib
import os
import sys

import step04_tools  # noqa: F401
from core import MODEL, run_agent, tool

SMALL_MODEL = os.getenv("AGENT_SMALL_MODEL", MODEL)
THREADS: dict[str, list] = {}
CACHE: dict[str, str] = {}
APPROVAL_THRESHOLD = 500.0


@tool
def refund(order_id: str, amount: float) -> str:
    """Refund an order. Amounts above the threshold require human approval and will be queued."""
    if amount > APPROVAL_THRESHOLD:
        return f"QUEUED for human approval: refund {amount} on {order_id}"
    return f"refunded {amount} on {order_id}"


def route(question: str) -> str:
    return SMALL_MODEL if len(question) < 60 and "?" in question else MODEL


def answer(session: str, question: str) -> dict:
    key = hashlib.sha1(question.lower().encode()).hexdigest()
    if key in CACHE:
        return {"answer": CACHE[key], "cached": True, "model": None}
    thread = THREADS.setdefault(session, [{"role": "system", "content": "You are Field Agent for Contoso support. Be brief. Use tools."}])
    thread.append({"role": "user", "content": question})
    model = route(question)
    text = run_agent(thread, model=model, on_event=lambda k, t: None)
    CACHE[key] = text
    return {"answer": text, "cached": False, "model": model}


try:
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI(title="field-agent")

    class Ask(BaseModel):
        session: str = "default"
        question: str

    @app.post("/ask")
    def ask(body: Ask) -> dict:
        return answer(body.session, body.question)

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "model": MODEL, "sessions": len(THREADS)}
except ImportError:  # the smoke test below still works without fastapi installed
    pass

if __name__ == "__main__" and sys.argv[1:] == ["smoke"]:
    import urllib.request, json
    for q in ["What is 2+2?", "Refund order A1 for 900"]:
        req = urllib.request.Request("http://localhost:8000/ask", data=json.dumps({"question": q}).encode(), headers={"Content-Type": "application/json"})
        print(q, "->", json.load(urllib.request.urlopen(req)))
    print("smoke test passed")
