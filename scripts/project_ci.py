#!/usr/bin/env python3
"""Validate self-contained browser projects and build a Pages gallery."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
SLUG = re.compile(r"^[a-z][a-z0-9-]{1,49}$")
REQUIRED = ("index.html", "README.md")
MAX_FILE_BYTES = 40 * 1024 * 1024

def discover():
    if not PROJECTS.exists():
        return []
    return sorted(p for p in PROJECTS.iterdir() if p.is_dir() and not p.name.startswith("."))

def validate(project):
    issues = []
    if not SLUG.fullmatch(project.name):
        issues.append(f"{project}: invalid slug (lowercase kebab-case required)")
    for filename in REQUIRED:
        if not (project / filename).is_file():
            issues.append(f"{project}: missing {filename}")
    if (project / "package.json").exists():
        issues.append(f"{project}: package.json is not supported (no build step)")
    for p in project.rglob("*"):
        if p.is_symlink():
            issues.append(f"{p}: symlinks are not allowed")
        elif p.is_file():
            if p.stat().st_size > MAX_FILE_BYTES:
                issues.append(f"{p}: file exceeds 40 MiB; use smaller media assets")
            if p.suffix.lower() in (".exe", ".dll", ".bat", ".ps1", ".sh"):
                issues.append(f"{p}: executable scripts/binaries are not allowed")
    index = project / "index.html"
    if index.is_file():
        data = index.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"<html\b", data, re.I) or not re.search(r"<title\b", data, re.I):
            issues.append(f"{index}: expected html and title tags")
    return issues

def build(output, projects):
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / ".nojekyll").write_text("")
    cards = []
    manifest = []
    for project in projects:
        target = output / "projects" / project.name
        shutil.copytree(project, target, symlinks=False, ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"))
        label = project.name.replace("-", " ").title()
        manifest.append({"slug": project.name, "url": f"./projects/{project.name}/"})
        cards.append(f'<a class="card" href="./projects/{html.escape(project.name)}/"><span class="tag">WEB PROJECT</span><h2>{html.escape(label)}</h2><p>Открыть проект →</p></a>')
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    body = "\n".join(cards) if cards else '<p class="empty">Пока нет опубликованных проектов. Создайте первый PR!</p>'
    page = """<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Build Challenge — Student Gallery</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 75% 0%,#302058 0%,transparent 42%),radial-gradient(ellipse at 0% 80%,#0d4051 0%,transparent 40%),#080b14;color:#f6f6fb;font:16px system-ui,-apple-system,Segoe UI,sans-serif}.wrap{max-width:1140px;margin:auto;padding:90px 30px}.eyebrow{color:#a995ff;letter-spacing:.22em;font-size:12px;font-weight:700}h1{font-size:clamp(42px,7vw,82px);letter-spacing:-.06em;line-height:1.02;margin:16px 0 22px}header p{color:#aeb6c9;max-width:620px;line-height:1.7}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px;margin-top:56px}.card{border:1px solid #ffffff27;border-radius:22px;padding:30px;min-height:190px;text-decoration:none;color:inherit;background:linear-gradient(145deg,#ffffff12,#ffffff05);backdrop-filter:blur(16px);transition:transform .2s,border-color .2s}.card:hover{transform:translateY(-5px);border-color:#a995ff}.tag{color:#8fd6f1;font-size:10px;letter-spacing:.16em}.card h2{font-size:24px;letter-spacing:-.03em;margin:26px 0}.card p,.empty{color:#b7bdd1}footer{margin-top:80px;color:#777e98;font-size:13px}</style></head><body><div class="wrap"><header><div class="eyebrow">ITHUB / PROMPT ENGINEERING</div><h1>AI Build<br>Challenge<span style="color:#a995ff">.</span></h1><p>Командные игры и веб-приложения. Каждый проект прошёл проверку и опубликован через GitHub Actions.</p></header><main class="grid">""" + body + """</main><footer>Student Projects · GitHub Pages</footer></div></body></html>"""
    (output / "index.html").write_text(page, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    projects = discover()
    issues = [issue for p in projects for issue in validate(p)]
    if issues:
        print("\n".join(issues), file=sys.stderr)
        return 1
    output = Path(args.output).resolve()
    if output == ROOT or output == PROJECTS or PROJECTS in output.parents:
        print("Unsafe output directory", file=sys.stderr)
        return 1
    build(output, projects)
    print(f"Validated {len(projects)} projects; gallery: {output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
