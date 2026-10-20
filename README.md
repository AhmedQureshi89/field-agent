# Field Agent

One agent, built by hand in eighteen steps, following the lessons of Microsoft's open course
[AI Agents for Beginners](https://microsoft.github.io/ai-agents-for-beginners/). Each `stepNN_*.py`
adds one capability to the same ~120-line loop in `core.py`. Nothing is hidden behind a framework
until Step 14, when the finished agent is ported to Microsoft Agent Framework so the comparison is fair.

Runs on your own machine against Ollama or LM Studio. No cloud account is needed until you want one.

## Setup (Windows PowerShell)

```powershell
ollama pull qwen2.5:7b
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python step01_hello_agent.py
```

## The eighteen steps

| Step | Lesson | You build | You see |
|---|---|---|---|
| 01 | Intro | A chat loop with no tools | The model cannot read the environment |
| 02 | Frameworks | Provider switch | Same loop, different endpoints and latency |
| 03 | Principles | `/status` `/prompt` `/off` | Transparency and control as code |
| 04 | Tool use | Three tools and schemas | The model's tool call as JSON, then the result |
| 05 | Agentic RAG | Retriever plus evidence check | The agent rewriting a weak query by itself |
| 06 | Trust | Input filter, turn cap, approval, meta prompt | An attack blocked, a write waiting for your y/n |
| 07 | Planning | Typed JSON plan routed to specialists | A rejected plan retried until valid |
| 08 | Multi-agent | researcher → writer → reviewer hand-off | Who spoke, and a draft sent back for fixes |
| 09 | Metacognition | plan → act → evaluate → adjust | A strategy switch after bad feedback |
| 10 | Production | Spans to `traces.jsonl`, an eval gate | A pass rate that blocks a bad deploy |
| 11 | Protocols | An MCP server over your tools | Claude Desktop or VS Code calling your code |
| 12 | Context | Compression at 70%, tool selection | A budget bar that shrinks |
| 13 | Memory | SQLite memory, a knowledge agent | Preferences surviving a restart |
| 14 | Agent Framework | The port | What the framework now writes for you |
| 15 | Computer use | A read-only browser scout | observe → decide → act → verify |
| 16 | Deploy | FastAPI service, router, cache, approval | A smoke test against the live endpoint |
| 17 | Local | Sensitivity router with latency | Which requests never leave the machine |
| 18 | Security | Ed25519 receipts, hash chain | Tampering caught by verification |

## The learning page

`site/agentic-trajectory.html` is the companion page: eighteen animated scenes of the mechanisms these
steps build, a live playground, and the build track with this code bundled in. It is published at
https://claude.ai/artifact/ULQmLEw66Wg8obNNw89iEM. To rebuild it after editing any step file:

```powershell
python siteuild_page.py
```

## Release it

```powershell
git init ; git add . ; git commit -m "Field Agent: step 01"
gh repo create field-agent --public --source . --push
```

Commit after every step. The history of the repository becomes your learning log.

## License

MIT. Course content © Microsoft, MIT licensed.
