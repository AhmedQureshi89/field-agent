"""
core.py — the smallest honest agent loop.

Everything in this project is built on these ~120 lines. Read them once, slowly.

    perceive  -> the user's message and any tool results are appended to `messages`
    reason    -> the model reads `messages` and either answers or asks for a tool
    act       -> we run the tool the model asked for and feed the result back
    repeat    -> until the model answers in plain text or we hit max_turns

Works with any OpenAI-compatible endpoint:
    Ollama      AGENT_BASE_URL=http://localhost:11434/v1   AGENT_MODEL=qwen2.5:7b
    LM Studio   AGENT_BASE_URL=http://localhost:1234/v1    AGENT_MODEL=<loaded model>
    Azure/OpenAI see .env.example
"""
from __future__ import annotations

import inspect
import json
import os
import time
from typing import Any, Callable

from openai import OpenAI

# --------------------------------------------------------------------------- config
def load_env(path: str = ".env") -> None:
    """Tiny .env loader so you do not need another dependency."""
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


load_env()
BASE_URL = os.getenv("AGENT_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("AGENT_API_KEY", "ollama")
MODEL = os.getenv("AGENT_MODEL", "qwen2.5:7b")


def make_client() -> OpenAI:
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)


# --------------------------------------------------------------------------- tools
TOOLS: dict[str, dict[str, Any]] = {}

_PY_TO_JSON = {str: "string", int: "integer", float: "number", bool: "boolean"}


def tool(fn: Callable) -> Callable:
    """Register a plain Python function as a tool.

    The schema the model sees is built from the signature and the docstring,
    so the docstring IS the product: it is the only thing the model reads.
    """
    sig = inspect.signature(fn)
    props, required = {}, []
    for name, p in sig.parameters.items():
        props[name] = {"type": _PY_TO_JSON.get(p.annotation, "string")}
        if p.default is inspect.Parameter.empty:
            required.append(name)
    TOOLS[fn.__name__] = {
        "fn": fn,
        "schema": {
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": (fn.__doc__ or "").strip(),
                "parameters": {"type": "object", "properties": props, "required": required},
            },
        },
    }
    return fn


def schemas(names: list[str] | None = None) -> list[dict]:
    names = names or list(TOOLS)
    return [TOOLS[n]["schema"] for n in names]


# --------------------------------------------------------------------------- events
C = {"user": "\033[96m", "llm": "\033[93m", "tool": "\033[92m", "sys": "\033[90m", "end": "\033[0m"}


def say(kind: str, text: str) -> None:
    """Every stage of the loop prints with a label, so the mechanism stays visible."""
    print(f"{C.get(kind, '')}[{kind.upper():5}] {text}{C['end']}")


# --------------------------------------------------------------------------- loop
def run_agent(
    messages: list[dict],
    tool_names: list[str] | None = None,
    *,
    client: OpenAI | None = None,
    model: str = MODEL,
    max_turns: int = 8,
    on_event: Callable[[str, str], None] = say,
    approve: Callable[[str, dict], bool] | None = None,
) -> str:
    """Run the loop until the model answers in text. Returns the final text."""
    client = client or make_client()
    tools = schemas(tool_names) if (tool_names or TOOLS) else None

    for turn in range(1, max_turns + 1):
        t0 = time.perf_counter()
        resp = client.chat.completions.create(model=model, messages=messages, tools=tools)
        msg = resp.choices[0].message
        on_event("sys", f"turn {turn} - model answered in {time.perf_counter() - t0:.1f}s")

        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content or ""})
            on_event("llm", msg.content or "(empty)")
            return msg.content or ""

        # the model wants to ACT: it returned one or more tool calls
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            if os.getenv("AGENT_DEBUG"):  # AGENT_DEBUG=1 shows the raw tool call exactly as the model sent it
                on_event("sys", "raw tool_call: " + json.dumps(call.model_dump(), ensure_ascii=False))
            on_event("llm", f"wants {name}({json.dumps(args)})")
            if approve and not approve(name, args):
                result = "DENIED by the human. Explain that you could not do this."
            else:
                try:
                    result = TOOLS[name]["fn"](**args)
                except Exception as exc:  # the model gets the error and can recover
                    result = f"ERROR: {exc}"
            on_event("tool", f"{name} -> {str(result)[:300]}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    on_event("sys", "max turns reached; stopping to avoid an infinite loop")
    return "I stopped after too many steps."


def chat_loop(system: str, tool_names: list[str] | None = None, **kw) -> None:
    """A terminal chat that keeps the conversation (short-term memory) in `messages`."""
    messages = [{"role": "system", "content": system}]
    print(f"model={MODEL}  endpoint={BASE_URL}  tools={tool_names or list(TOOLS)}  (type 'quit' to exit)")
    while True:
        try:
            user = input("\nyou > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"quit", "exit"}:
            break
        if not user:
            continue
        messages.append({"role": "user", "content": user})
        run_agent(messages, tool_names, **kw)
