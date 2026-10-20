"""
STEP 08 · Lesson 8 · Three agents, one hand-off

researcher -> writer -> reviewer. Each agent owns one step and passes a structured
message to the next. The reviewer can send the draft BACK to the writer once.
Every hand-off is printed, so you see who spoke and why.

Run:   python step08_handoff.py "Explain function calling to a product manager"
"""
import json
import sys

from core import MODEL, make_client, say

ROLES = {
    "researcher": "You are the researcher. Produce 5 factual bullet points on the topic. No prose.",
    "writer": "You are the writer. Turn the research into a 120-word explanation for the stated audience. If reviewer notes are given, fix exactly those.",
    "reviewer": "You are the reviewer. Reply with ONLY JSON: {\"approved\": true|false, \"notes\": str}. Approve only if accurate and under 140 words.",
}


def ask(client, role: str, content: str) -> str:
    r = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": ROLES[role]}, {"role": "user", "content": content}])
    return r.choices[0].message.content


def handoff(frm: str, to: str, payload: dict) -> dict:
    say("sys", f"hand-off {frm} -> {to}: {json.dumps(payload)[:120]}...")
    return payload


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) or "Explain agentic RAG to a sales team"
    client = make_client()

    research = ask(client, "researcher", task)
    msg = handoff("researcher", "writer", {"task": task, "research": research})

    draft = ask(client, "writer", f"Audience/task: {msg['task']}\nResearch:\n{msg['research']}")
    for round_ in range(2):
        msg = handoff("writer", "reviewer", {"draft": draft})
        verdict = json.loads(ask(client, "reviewer", msg["draft"]))
        if verdict.get("approved"):
            say("llm", f"approved after {round_ + 1} review round(s)\n\n{draft}")
            break
        msg = handoff("reviewer", "writer", {"notes": verdict.get("notes", "")})
        draft = ask(client, "writer", f"Audience/task: {task}\nResearch:\n{research}\nReviewer notes: {msg['notes']}")
    else:
        say("sys", "not approved after 2 rounds; escalate to a human")
