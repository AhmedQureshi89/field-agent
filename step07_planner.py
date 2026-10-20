"""
STEP 07 · Lesson 7 · A planner with typed output

The planner never acts. It turns a goal into a JSON plan whose shape is enforced by
Pydantic, then each subtask is routed to a specialist (stubbed here with the same model
and a different system prompt). Change the goal; watch the plan change.

Run:   python step07_planner.py "Plan a 3-day work trip from Riyadh to Dubai for two engineers"
"""
import json
import sys
from enum import Enum

from pydantic import BaseModel, ValidationError

from core import MODEL, make_client, say


class Agent(str, Enum):
    flights = "flights"
    hotel = "hotel"
    transport = "transport"
    activities = "activities"
    budget = "budget"


class SubTask(BaseModel):
    id: int
    agent: Agent
    instruction: str


class Plan(BaseModel):
    goal: str
    subtasks: list[SubTask]


PLANNER = (
    "You are a planner. Split the goal into subtasks for these agents only: flights, hotel, transport, activities, budget. "
    "Reply with ONLY JSON of the form {\"goal\": str, \"subtasks\": [{\"id\": int, \"agent\": str, \"instruction\": str}]}."
)
SPECIALIST = "You are the {agent} specialist. Do exactly your subtask in 3 bullet points. Invent nothing you cannot know; say what you would look up."


def plan(goal: str, client, attempts: int = 3) -> Plan:
    for i in range(attempts):
        r = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": PLANNER}, {"role": "user", "content": goal}], response_format={"type": "json_object"})
        raw = r.choices[0].message.content
        try:
            p = Plan.model_validate_json(raw)
            say("llm", f"plan accepted on attempt {i + 1}: {len(p.subtasks)} subtasks")
            return p
        except ValidationError as e:
            say("sys", f"plan rejected (attempt {i + 1}): {e.errors()[0]['msg']}")
    raise SystemExit("planner could not produce a valid plan")


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or "Plan a 2-day visit to Jeddah for a family of four"
    client = make_client()
    p = plan(goal, client)
    print(json.dumps(p.model_dump(), indent=2))
    results = []
    for st in p.subtasks:  # single subtask -> direct; many -> this simple coordinator loop
        say("sys", f"routing #{st.id} -> {st.agent.value} agent")
        r = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": SPECIALIST.format(agent=st.agent.value)}, {"role": "user", "content": st.instruction}])
        results.append(f"## {st.agent.value}\n{r.choices[0].message.content}")
    summary = client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": "Combine the specialist outputs into one short itinerary."}, {"role": "user", "content": "\n\n".join(results)}])
    say("llm", summary.choices[0].message.content)
