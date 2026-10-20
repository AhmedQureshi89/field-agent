"""
STEP 13 · Lesson 13 · Memory that survives a restart

Short-term memory is the `messages` list and dies with the process. Long-term memory is
a SQLite table with two tools: remember() and recall(). A background "knowledge agent"
call decides after every turn whether anything is worth keeping, so you never have to
say "remember this".

Session 1:  I usually fly early mornings and I prefer aisle seats.
            quit
Session 2:  Book me a flight to Dubai next Tuesday, what do you already know about me?

Run:   python step13_memory.py
"""
import json
import sqlite3
import time

from core import MODEL, make_client, run_agent, say, tool

DB = sqlite3.connect("memory.db")
DB.execute("CREATE TABLE IF NOT EXISTS memory (ts REAL, kind TEXT, text TEXT)")


@tool
def remember(text: str, kind: str = "preference") -> str:
    """Store a durable fact about the user. kind is one of: preference, fact, episode."""
    DB.execute("INSERT INTO memory VALUES (?,?,?)", (time.time(), kind, text))
    DB.commit()
    return f"stored ({kind}): {text}"


@tool
def recall(topic: str = "") -> str:
    """Return stored memories, newest first, optionally filtered by a topic word."""
    rows = DB.execute("SELECT kind, text FROM memory WHERE text LIKE ? ORDER BY ts DESC LIMIT 10", (f"%{topic}%",)).fetchall()
    return "\n".join(f"- [{k}] {t}" for k, t in rows) or "nothing stored yet"


KNOWLEDGE_AGENT = (
    "You watch a conversation and extract durable user facts or preferences worth remembering across sessions. "
    "Reply ONLY with JSON {\"keep\": [str, ...]} (empty list if nothing durable)."
)


def harvest(client, user: str, answer: str) -> None:
    r = client.chat.completions.create(model=MODEL, response_format={"type": "json_object"}, messages=[{"role": "system", "content": KNOWLEDGE_AGENT}, {"role": "user", "content": f"user: {user}\nagent: {answer}"}])
    for fact in json.loads(r.choices[0].message.content).get("keep", []):
        say("sys", "KNOWLEDGE AGENT kept: " + remember(fact))


SYSTEM = "You are Field Agent. At the start of a task call recall() to personalise. Use remember() when the user states a lasting preference."

if __name__ == "__main__":
    client = make_client()
    messages = [{"role": "system", "content": SYSTEM}]
    say("sys", "long-term memory on disk: " + recall())
    while True:
        user = input("\nyou > ").strip()
        if user in {"quit", "exit"}:
            break
        messages.append({"role": "user", "content": user})
        answer = run_agent(messages, ["remember", "recall"], client=client)
        harvest(client, user, answer)
