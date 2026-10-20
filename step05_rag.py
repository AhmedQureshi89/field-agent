"""
STEP 05 · Lesson 5 · Agentic RAG over your own notes

No vector database yet: a bag-of-words retriever over notes/*.md is enough to see the
mechanism. The agent gets TWO tools: search_notes and assess_evidence. The system prompt
tells it to retrieve, judge the evidence, and rewrite the query when the score is weak,
with a hard cap of three attempts. Watch the loop rewrite a bad query on its own.

Try:   Which pattern should I use when one agent passes work to the next?
       What limits did we set for the browser agent?   (rewrite happens if the first query misses)

Run:   python step05_rag.py
"""
import math
import pathlib
import re
from collections import Counter

from core import chat_loop, tool

NOTES = pathlib.Path(__file__).parent / "notes"


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _chunks():
    for f in sorted(NOTES.glob("*.md")):
        paras = [p.strip() for p in f.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for i, p in enumerate(paras):
            yield f"{f.name}#{i}", p


def _cosine(a: Counter, b: Counter) -> float:
    dot = sum(a[t] * b.get(t, 0) for t in a)
    na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


@tool
def search_notes(query: str, k: int = 3) -> str:
    """Search the local notes for a query. Returns the top k passages with a relevance score from 0 to 1."""
    q = Counter(_tokens(query))
    scored = sorted(((_cosine(q, Counter(_tokens(t))), cid, t) for cid, t in _chunks()), reverse=True)[:k]
    return "\n---\n".join(f"[{cid}] score={s:.2f}\n{t}" for s, cid, t in scored) or "no notes found"


@tool
def assess_evidence(question: str, best_score: float) -> str:
    """Report whether the retrieved evidence is strong enough to answer. Pass the best score from search_notes."""
    if best_score >= 0.35:
        return "SUFFICIENT: answer from the evidence and cite the passage ids."
    return "INSUFFICIENT: rewrite the query with different words or a narrower topic and search again (max 3 attempts)."


SYSTEM = (
    "You are Field Agent, a careful researcher over local notes. Procedure: 1) search_notes, "
    "2) assess_evidence with the best score, 3) if INSUFFICIENT rewrite the query and repeat, at most 3 searches, "
    "4) answer only from retrieved passages and cite their ids. If still insufficient after 3 tries, say so and "
    "suggest a human check."
)

if __name__ == "__main__":
    chat_loop(SYSTEM, tool_names=["search_notes", "assess_evidence"], max_turns=10)
