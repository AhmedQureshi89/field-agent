"""
STEP 01 · Lesson 1 · Hello, agent

A model alone is not an agent. Run this, then ask it:  "What is today's date?"
It will guess or refuse, because it has no SENSOR to read the environment.
That gap is the whole reason the next steps exist.

Run:   python step01_hello_agent.py
"""
from core import chat_loop

SYSTEM = (
    "You are Field Agent, a small assistant being built step by step. "
    "Be brief. If you cannot know something, say exactly what you would need to find out."
)

if __name__ == "__main__":
    # No tools registered yet: the loop can only perceive text and reason about it.
    chat_loop(SYSTEM, tool_names=[])
