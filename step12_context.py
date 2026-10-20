"""
STEP 12 · Lesson 12 · A context budget you can watch

Two mechanisms:
  compress -> when the history passes 70% of BUDGET tokens, older turns are summarised into one line
  select   -> instead of offering all tools, pick the 2 most relevant to the question by keyword overlap
After each turn the agent prints the budget bar, so you see context being managed.

Run:   python step12_context.py
Paste a long paragraph a few times to trigger compression.
"""
import re

import step04_tools  # noqa: F401
import step05_rag  # noqa: F401
from core import MODEL, TOOLS, make_client, run_agent, say

BUDGET = 1200  # tokens, deliberately tiny so you can see compression happen


def est_tokens(messages) -> int:
    return sum(len(str(m.get("content") or "")) // 4 + 4 for m in messages)


def bar(used: int) -> str:
    n = min(20, used * 20 // BUDGET)
    return f"[{'#' * n}{'.' * (20 - n)}] {used}/{BUDGET} tokens"


def compress(messages, client):
    old, recent = messages[1:-4], messages[-4:]
    if not old:
        return messages
    text = "\n".join(f"{m['role']}: {m.get('content')}" for m in old if m.get("content"))
    r = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": "Summarise this conversation in 2 sentences, keeping facts and user preferences."}, {"role": "user", "content": text}])
    say("sys", f"COMPRESS: {len(old)} messages -> 1 summary")
    return [messages[0], {"role": "system", "content": "Earlier conversation summary: " + r.choices[0].message.content}] + recent


def select_tools(question: str, k: int = 2) -> list[str]:
    words = set(re.findall(r"[a-z]+", question.lower()))
    scored = sorted(TOOLS, key=lambda n: -len(words & set(re.findall(r"[a-z]+", TOOLS[n]["schema"]["function"]["description"].lower()))))
    return scored[:k]


if __name__ == "__main__":
    client = make_client()
    messages = [{"role": "system", "content": "You are Field Agent. Use tools when needed. Be brief."}]
    while True:
        user = input("\nyou > ").strip()
        if user in {"quit", "exit"}:
            break
        messages.append({"role": "user", "content": user})
        if est_tokens(messages) > BUDGET * 0.7:
            messages = compress(messages, client)
        chosen = select_tools(user)
        say("sys", f"SELECT: offering only {chosen}")
        run_agent(messages, chosen, client=client)
        say("sys", bar(est_tokens(messages)))
