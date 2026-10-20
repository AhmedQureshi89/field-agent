"""Bundle the field-agent source files into the page template -> agentic-trajectory.html"""
import io, json, pathlib
root = pathlib.Path(__file__).parent
repo = root.parent
SKIP = {"site", ".venv", "__pycache__", ".git", ".claude"}
files = {}
for p in sorted(repo.rglob("*")):
    # Match SKIP against the path relative to the repo, not the absolute path. A git
    # worktree created by Claude Code lives under <repo>/.claude/worktrees/<name>/, so
    # every absolute path there contains ".claude" and the absolute form skipped the
    # entire tree -- bundling nothing, with no error.
    rel = p.relative_to(repo)
    if SKIP & set(rel.parts):
        continue
    if p.is_file() and p.suffix in {".py", ".md", ".txt", ".example"} or p.name in {"Dockerfile", ".gitignore"}:
        files[rel.as_posix()] = p.read_text(encoding="utf-8")
assert files, f"no source files found under {repo}"
tpl = (root / "trajectory.template.html").read_text(encoding="utf-8")
blob = json.dumps(files, ensure_ascii=False).replace("</", "<\\/")
out = tpl.replace("/*CODE*/{}/*END*/", blob, 1)
assert out != tpl, "marker not found"
(root / "agentic-trajectory.html").write_text(out, encoding="utf-8", newline="\n")
print(f"bundled {len(files)} files, page {len(out)//1024} KB")
