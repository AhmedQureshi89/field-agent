"""
STEP 14 · Lesson 14 · The same agent on Microsoft Agent Framework

You built the loop by hand in core.py. Now hand it to the framework the course uses and
notice what you no longer write: schema generation, the tool loop, thread state.
Your tools are plain functions, so they move across unchanged.

Install:  pip install agent-framework --pre
Run:      python step14_agent_framework.py

NOTE: the framework is young and its import names have moved between previews. If an
import fails, open the course's 04-tool-use Python sample and copy the import lines
from there; the body below stays the same.
"""
import asyncio
import os

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

import step04_tools as t
from core import BASE_URL, API_KEY, MODEL

os.environ.setdefault("OPENAI_BASE_URL", BASE_URL)
os.environ.setdefault("OPENAI_API_KEY", API_KEY)


async def main() -> None:
    agent = ChatAgent(
        chat_client=OpenAIChatClient(model_id=MODEL),
        name="field-agent",
        instructions="You are Field Agent. Use tools for dates, numbers and files.",
        tools=[t.get_current_time, t.calculate, t.read_file],  # the framework builds the schemas
    )
    thread = agent.get_new_thread()  # short-term memory, serialisable
    for q in ["What day is it?", "And 3 nights at 420 each?"]:
        print(f"\nyou > {q}")
        result = await agent.run(q, thread=thread)
        print("agent >", result.text)


if __name__ == "__main__":
    asyncio.run(main())
