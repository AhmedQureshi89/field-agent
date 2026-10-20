"""Bundle the field-agent source files into the page template -> agentic-trajectory.html"""
import io, json, pathlib
root = pathlib.Path(__file__).parent
files = {}
for p in sorted(root.parent.rglob("*")):
    if {"site", ".venv", "__pycache__", ".git", ".claude"} & set(p.parts):
        continue
    if p.is_file() and p.suffix in {".py", ".md", ".txt", ".example"} or p.name in {"Dockerfile", ".gitignore"}:
        files[p.relative_to(root.parent).as_posix()] = p.read_text(encoding="utf-8")
tpl = (root / "trajectory.template.html").read_text(encoding="utf-8")
blob = json.dumps(files, ensure_ascii=False).replace("</", "<\\/")
out = tpl.replace("/*CODE*/{}/*END*/", blob, 1)
assert out != tpl, "marker not found"
(root / "agentic-trajectory.html").write_text(out, encoding="utf-8", newline="\n")
print(f"bundled {len(files)} files, page {len(out)//1024} KB")
