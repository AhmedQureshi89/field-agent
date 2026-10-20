"""
STEP 09 · Lesson 9 · An agent that changes its strategy

plan -> act -> evaluate -> adjust. The agent recommends a hotel using a STRATEGY
("cheapest" or "best_value"). A simulated guest rates it. Bad ratings make the agent
switch strategy and explain why, in its own words, from the log.

Run:   python step09_reflect.py
"""
import json
import random

from core import MODEL, make_client, say

HOTELS = [
    {"name": "Budget Inn", "price": 90, "quality": 5},
    {"name": "Corniche Stay", "price": 160, "quality": 7},
    {"name": "Palm Suites", "price": 240, "quality": 9},
    {"name": "Old Town House", "price": 130, "quality": 8},
]


def act(strategy: str) -> dict:
    if strategy == "cheapest":
        return min(HOTELS, key=lambda h: h["price"])
    return max(HOTELS, key=lambda h: h["quality"] / h["price"])


def evaluate(hotel: dict) -> str:  # the environment answers back
    bad = hotel["quality"] < 7 or random.random() < 0.1
    return "bad" if bad else "good"


if __name__ == "__main__":
    random.seed(7)
    strategy, log = "cheapest", []
    for round_ in range(1, 7):
        choice = act(strategy)
        verdict = evaluate(choice)
        log.append({"round": round_, "strategy": strategy, "hotel": choice["name"], "verdict": verdict})
        say("tool", f"round {round_}: {strategy:10} -> {choice['name']:15} guest says {verdict}")
        if verdict == "bad" and strategy == "cheapest":
            strategy = "best_value"
            say("sys", "ADJUST: switching strategy cheapest -> best_value")
    r = make_client().chat.completions.create(model=MODEL, messages=[
        {"role": "system", "content": "You are the agent reflecting on your own decision log. In 3 sentences explain what you did, what feedback you got and why you changed strategy."},
        {"role": "user", "content": json.dumps(log)},
    ])
    say("llm", r.choices[0].message.content)
