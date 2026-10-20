"""
STEP 10 · Lesson 10 · Traces, spans and an evaluation gate

Two things production needs and prototypes skip:
  1. tracing   -> every model call and tool call becomes a span in traces.jsonl (trace id, name, ms)
  2. offline eval -> evals.json holds questions with expected substrings; the gate prints a pass rate
Fail the gate on purpose (edit evals.json) and see it refuse.

Run:   python step10_trace_eval.py
Then:  Get-Content traces.jsonl -Tail 10
"""
import json
import time
import uuid

import step04_tools  # noqa: F401
from core import run_agent

TRACES = open("traces.jsonl", "a", encoding="utf-8")
EVALS = [
    {"q": "What is 12 * 12?", "expect": "144"},
    {"q": "What weekday is it today? Use the tool.", "expect": "day"},
    {"q": "Read notes/agents.md and name one agent type.", "expect": "agent"},
]


class Tracer:
    def __init__(self):
        self.trace_id = uuid.uuid4().hex[:8]
        self.t0 = time.perf_counter()
        self.spans = 0

    def event(self, kind: str, text: str) -> None:
        self.spans += 1
        span = {"trace": self.trace_id, "span": self.spans, "kind": kind, "text": text[:120], "ms": round((time.perf_counter() - self.t0) * 1000)}
        TRACES.write(json.dumps(span) + "\n")
        print(f"  span {span['span']:2} {span['ms']:6} ms  {kind:5} {span['text']}")


if __name__ == "__main__":
    passed = 0
    for case in EVALS:
        tr = Tracer()
        print(f"\ntrace {tr.trace_id}: {case['q']}")
        answer = run_agent([{"role": "system", "content": "Use tools. Be brief."}, {"role": "user", "content": case["q"]}], on_event=tr.event)
        ok = case["expect"].lower() in answer.lower()
        passed += ok
        print(f"  -> {'PASS' if ok else 'FAIL'} (expected '{case['expect']}')")
    rate = passed / len(EVALS)
    print(f"\npass rate {passed}/{len(EVALS)} = {rate:.0%}")
    raise SystemExit(0 if rate >= 0.67 else "GATE FAILED: do not deploy")
