"""
STEP 04 · Lesson 4 · Give the agent hands

Three tools. Watch the loop print the model's tool call as JSON, run it, and feed
the result back. Then ask the question Step 01 could not answer.

Try:   What is today's date?        -> get_current_time
       What is 17% of 2,340?         -> calculate
       What does notes/agents.md say? -> read_file
       A trip: 3 nights at 420 SAR, what is the total and what day is it? -> two tools, one answer

Run:   python step04_tools.py
"""
import ast
import datetime as dt
import operator as op
import pathlib

from core import chat_loop, tool

SANDBOX = pathlib.Path(__file__).parent.resolve()


@tool
def get_current_time(timezone_offset_hours: int = 3) -> str:
    """Return the current date and time. timezone_offset_hours is the offset from UTC (Riyadh is 3)."""
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=timezone_offset_hours)))
    return now.strftime("%A %Y-%m-%d %H:%M (UTC%z)")


_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg, ast.Mod: op.mod}


def _eval(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("only arithmetic is allowed")


@tool
def calculate(expression: str) -> str:
    """Evaluate an arithmetic expression such as '2340 * 0.17' or '3 * 420'. Use it for any number work."""
    return str(_eval(ast.parse(expression, mode="eval").body))


@tool
def read_file(path: str) -> str:
    """Read a text file inside the project folder (for example 'notes/agents.md'). Returns up to 4000 characters."""
    target = (SANDBOX / path).resolve()
    if SANDBOX not in target.parents and target != SANDBOX:
        return "ERROR: path is outside the project sandbox"
    return target.read_text(encoding="utf-8")[:4000]


SYSTEM = (
    "You are Field Agent. You have tools. Use them whenever a question needs live data, "
    "a calculation or a file. Never guess numbers or dates."
)

if __name__ == "__main__":
    chat_loop(SYSTEM)  # all registered tools are offered to the model
