"""
STEP 18 · Lesson 18 · A signed receipt for every tool call

Every tool call produces a receipt: canonical JSON (sorted keys, no spaces), hashed
arguments and result, the previous receipt's hash, and an Ed25519 signature. Then we
tamper with one receipt and watch verification fail; delete one and watch the chain break.

Install:  pip install cryptography
Run:      python step18_receipts.py
"""
import hashlib
import json
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

import step04_tools  # noqa: F401
from core import TOOLS, run_agent, say

KEY = Ed25519PrivateKey.generate()
PUB = KEY.public_key()
CHAIN: list[dict] = []


def canonical(obj) -> bytes:  # JCS in spirit: sorted keys, compact separators, UTF-8
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def receipt(tool: str, args: dict, result: str) -> dict:
    body = {
        "v": "receipt.v1", "ts": time.time(), "tool": tool,
        "args_hash": h(canonical(args)), "result_hash": h(result.encode()),
        "prev": h(canonical(CHAIN[-1])) if CHAIN else None,
    }
    body["sig"] = KEY.sign(canonical({k: v for k, v in body.items()})).hex()
    CHAIN.append(body)
    return body


def verify(chain: list[dict]) -> bool:
    prev = None
    for i, r in enumerate(chain):
        unsigned = {k: v for k, v in r.items() if k != "sig"}
        try:
            PUB.verify(bytes.fromhex(r["sig"]), canonical(unsigned))
        except InvalidSignature:
            say("sys", f"receipt {i}: SIGNATURE INVALID (tampered)")
            return False
        if r["prev"] != prev:
            say("sys", f"receipt {i}: CHAIN BROKEN (missing or reordered receipt)")
            return False
        prev = h(canonical(r))
    say("tool", f"chain of {len(chain)} receipts verified with the public key only")
    return True


# wrap every registered tool so calls emit receipts, without touching the tools themselves
for name, entry in TOOLS.items():
    original = entry["fn"]

    def wrapped(*a, _orig=original, _name=name, **kw):
        result = str(_orig(*a, **kw))
        rc = receipt(_name, kw or {"args": a}, result)
        say("sys", f"receipt {len(CHAIN)} sig={rc['sig'][:16]}... prev={str(rc['prev'])[:12]}")
        return result

    entry["fn"] = wrapped

if __name__ == "__main__":
    run_agent([{"role": "system", "content": "Use tools. Be brief."}, {"role": "user", "content": "What day is it, and what is 3 * 420?"}])
    print()
    verify(CHAIN)
    tampered = json.loads(json.dumps(CHAIN))
    tampered[0]["tool"] = "transfer_money"
    verify(tampered)
    verify(CHAIN[1:])
    print("\nReceipts prove who did what, in which order, unaltered. They do not prove it was correct or allowed.")
