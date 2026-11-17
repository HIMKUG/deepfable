#!/usr/bin/env python3
"""List, inspect, and load bundled skills. Standard library only.

Examples:
  python scripts/load_skill.py list
  python scripts/load_skill.py show docx --head 80
  python scripts/load_skill.py files pdf
  python scripts/load_skill.py check pptx
  python scripts/load_skill.py manifest --out /tmp/skills.json
  python scripts/load_skill.py list --root ~/.claude/skills
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = ROOT / "assets" / "skills"
LINK = re.compile(r"\]\((?!https?:|#)([^)]+)\)")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    data: dict[str, str] = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line or line.startswith((" ", "\t", "#")):
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in (">", "|", ">-", "|-"):
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            data[key] = (" " if value.startswith(">") else "\n").join(x for x in block if x)
            continue
        data[key] = value.strip('"').strip("'")
        i += 1
    return data


def discover(roots: list[Path]) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for root in roots:
        if not root.exists():
            continue
        for skill_md in sorted(root.glob("*/SKILL.md")):
            text = read_text(skill_md)
            fm = parse_frontmatter(text)
            name = fm.get("name") or skill_md.parent.name
            if name in found:
                continue
            found[name] = {
                "name": name,
                "path": skill_md.parent,
                "description": fm.get("description", ""),
                "root": root,
            }
    return found


def pick(skills: dict[str, dict], name: str) -> dict:
    if name in skills:
        return skills[name]
    lowered = {k.lower(): v for k, v in skills.items()}
    if name.lower() in lowered:
        return lowered[name.lower()]
    matches = [v for k, v in skills.items() if name.lower() in k.lower()]
    if len(matches) == 1:
        return matches[0]
    raise SystemExit(f"skill not found: {name}\nrun 'list' to see available names")


def cmd_list(args: argparse.Namespace, skills: dict[str, dict]) -> int:
    if not skills:
        print("no skills found under " + ", ".join(str(r) for r in args.root))
        return 1
    if args.json:
        print(json.dumps([{k: str(v[k]) if k == "path" else v[k] for k in ("name", "path", "description")} for v in skills.values()], ensure_ascii=False, indent=2))
        return 0
    for skill in sorted(skills.values(), key=lambda x: x["name"]):
        desc = " ".join(skill["description"].split())
        if len(desc) > 120:
            desc = desc[:117] + "..."
        print(f"{skill['name']}\t{desc}\t{skill['path']}")
    return 0


def cmd_show(args: argparse.Namespace, skills: dict[str, dict]) -> int:
    skill = pick(skills, args.name)
    skill_md = skill["path"] / "SKILL.md"
    text = read_text(skill_md)
    lines = text.splitlines()
    if args.head and args.head > 0:
        lines = lines[: args.head]
    print(f"# skill: {skill['name']}")
    print(f"# path: {skill['path']}")
    print(f"# note: relative paths in SKILL.md resolve against the path above.")
    print()
    print("\n".join(lines))
    if args.head and args.head < text.count("\n") + 1:
        print(f"\n# truncated: {args.head} of {text.count(chr(10)) + 1} lines; rerun without --head for the full file")
    return 0


def cmd_files(args: argparse.Namespace, skills: dict[str, dict]) -> int:
    skill = pick(skills, args.name)
    base = skill["path"]
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        print(f"{path.stat().st_size:>9}\t{path.relative_to(base).as_posix()}")
    return 0


def cmd_check(args: argparse.Namespace, skills: dict[str, dict]) -> int:
    skill = pick(skills, args.name)
    base = skill["path"]
    skill_md = base / "SKILL.md"
    text = read_text(skill_md) if skill_md.exists() else ""
    errors: list[str] = []
    warnings: list[str] = []

    if not text:
        errors.append("SKILL.md missing or empty")
    fm = parse_frontmatter(text)
    if not fm.get("name"):
        errors.append("frontmatter missing name")
    elif fm["name"] != base.name:
        warnings.append(f"frontmatter name '{fm['name']}' differs from folder '{base.name}'")
    if not fm.get("description"):
        errors.append("frontmatter missing description")
    for target in LINK.findall(text):
        if target.startswith(("mailto:", "tel:")) or target.startswith("//"):
            continue
        clean = target.split("#", 1)[0]
        if clean and not (base / clean).exists():
            warnings.append(f"linked path missing: {target}")

    scripts = list((base / "scripts").rglob("*")) if (base / "scripts").exists() else []
    print(f"skill={skill['name']} path={base}")
    print(f"files={sum(1 for p in base.rglob('*') if p.is_file())} scripts={sum(1 for p in scripts if p.is_file())}")
    for warning in warnings:
        print("WARN " + warning)
    for error in errors:
        print("ERROR " + error)
    if errors:
        return 1
    print("OK")
    return 0


def cmd_manifest(args: argparse.Namespace, skills: dict[str, dict]) -> int:
    payload = []
    for skill in sorted(skills.values(), key=lambda x: x["name"]):
        base = skill["path"]
        payload.append(
            {
                "name": skill["name"],
                "description": " ".join(skill["description"].split()),
                "path": str(base),
                "files": sum(1 for p in base.rglob("*") if p.is_file()),
                "scripts": sum(1 for p in (base / "scripts").rglob("*") if p.is_file())
                if (base / "scripts").exists()
                else 0,
            }
        )
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(payload)} skills)")
    else:
        print(text)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="List and load bundled skills.")
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="extra skills root; default is assets/skills",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list skills")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="print a skill's SKILL.md")
    p_show.add_argument("name")
    p_show.add_argument("--head", type=int, default=0, help="only print the first N lines")
    p_show.set_defaults(func=cmd_show)

    p_files = sub.add_parser("files", help="list a skill's files")
    p_files.add_argument("name")
    p_files.set_defaults(func=cmd_files)

    p_check = sub.add_parser("check", help="structural check for one skill")
    p_check.add_argument("name")
    p_check.set_defaults(func=cmd_check)

    p_manifest = sub.add_parser("manifest", help="emit JSON metadata for all skills")
    p_manifest.add_argument("--out", default="", help="write JSON to this path")
    p_manifest.set_defaults(func=cmd_manifest)

    args = parser.parse_args()
    roots = [DEFAULT_ROOT] + [Path(p).expanduser() for p in args.root]
    skills = discover(roots)
    return args.func(args, skills)


if __name__ == "__main__":
    raise SystemExit(main())
