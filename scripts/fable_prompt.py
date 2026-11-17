#!/usr/bin/env python3
"""Build and lint DeepSeek Fable system prompts. Standard library only.

Usage:
  python scripts/fable_prompt.py build --out prompt.md --name "DeepSeek 模型" --date 2026-11-17
  python scripts/fable_prompt.py build --out prompt.md --drop 6,7 --tools tools.md
  python scripts/fable_prompt.py build --out prompt.md --skills skills.md --no-skills
  python scripts/fable_prompt.py check prompt.md
  python scripts/fable_prompt.py check assets/deepseek-fable.system.md --allow-placeholders
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = ROOT / "assets" / "deepseek-fable.system.md"

HEADING = re.compile(r"^## (\d+)\. (.+)$", re.M)
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

ANCHORS = [
    "第一句给结论",
    "不确定就查",
    "默认散文",
    "一次最多一个澄清问题",
    "工具调用严格",
    "思考内容不外泄",
    "验证按用户要求分级",
]

BANNED = [
    "好的，我来",
    "当然，我来",
    "希望这对你有帮助",
    "作为 AI",
    "作为AI",
    "让我想想",
    "值得注意的是",
    "综上所述",
    "首先，我们需要",
]

REQUIRED_SECTIONS = ["回答前自检", "禁止清单", "不可协商"]


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, text: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def section_spans(text: str) -> list[tuple[int, str, int, int]]:
    matches = list(HEADING.finditer(text))
    spans: list[tuple[int, str, int, int]] = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        spans.append((int(match.group(1)), match.group(2).strip(), start, end))
    return spans


def get_section(text: str, name: str) -> str | None:
    for _, title, start, end in section_spans(text):
        if title == name:
            return text[start:end]
    return None


def drop_sections(text: str, numbers: set[int]) -> str:
    for number, _, start, end in reversed(section_spans(text)):
        if number in numbers:
            text = text[:start] + text[end:]
    return text


def estimate_tokens(text: str) -> int:
    cjk = sum(1 for ch in text if "一" <= ch <= "鿿")
    return int(cjk + (len(text) - cjk) / 4)


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
        key, value = key.strip(), value.strip()
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


def build_skill_index() -> str:
    root = ROOT / "assets" / "skills"
    rows: list[str] = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        fm = parse_frontmatter(read_text(skill_md))
        name = fm.get("name") or skill_md.parent.name
        desc = " ".join(fm.get("description", "").split())
        if len(desc) > 90:
            desc = desc[:87].rstrip() + "..."
        rows.append(f"- `{name}`: {desc}" if desc else f"- `{name}`")
    return "\n".join(rows)


def build(args: argparse.Namespace) -> int:
    try:
        text = read_text(args.template)
    except OSError as exc:
        print(f"ERROR cannot read template: {exc}", file=sys.stderr)
        return 2

    name = args.name or "DeepSeek 模型"
    date = args.date or datetime.date.today().isoformat()
    try:
        tools = read_text(args.tools).rstrip() if args.tools else ""
        if args.skills:
            skills_text = read_text(args.skills).rstrip()
        elif args.no_skills:
            skills_text = ""
        else:
            skills_text = build_skill_index()
    except OSError as exc:
        print(f"ERROR cannot read input file: {exc}", file=sys.stderr)
        return 2

    text = (
        text.replace("{{ASSISTANT_NAME}}", name)
        .replace("{{DATE}}", date)
        .replace("{{TOOLS}}", tools)
        .replace("{{SKILLS}}", skills_text)
    )

    if args.drop:
        try:
            numbers = {int(part) for part in args.drop.split(",") if part.strip()}
        except ValueError:
            print("ERROR --drop expects comma-separated section numbers, e.g. 6,7", file=sys.stderr)
            return 2
        text = drop_sections(text, numbers)

    missing = sorted(set(PLACEHOLDER.findall(text)))
    if missing:
        print("ERROR unresolved placeholders: " + ", ".join(missing), file=sys.stderr)
        return 1

    write_text(args.out, text)
    print(f"wrote {args.out}")
    print(f"chars={len(text)} lines={text.count(chr(10)) + 1} tokens~{estimate_tokens(text)}")
    return 0


def check(args: argparse.Namespace) -> int:
    try:
        text = read_text(args.path)
    except OSError as exc:
        print(f"ERROR cannot read file: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    placeholders = sorted(set(PLACEHOLDER.findall(text)))
    if placeholders and not args.allow_placeholders:
        errors.append("unresolved placeholders: " + ", ".join(placeholders))

    spans = section_spans(text)
    if not spans:
        errors.append("no '## N. Title' sections found")
    titles = [title for _, title, _, _ in spans]

    for required in REQUIRED_SECTIONS:
        if required not in titles:
            errors.append(f"missing required section: {required}")

    anchors_text = get_section(text, "不可协商") or ""
    numbered = re.findall(r"^\s*(\d+)\.\s", anchors_text, re.M)
    if len(numbered) < 7:
        errors.append(f"'不可协商' has {len(numbered)} numbered rules; expected 7")
    for anchor in ANCHORS:
        if anchor not in anchors_text:
            warnings.append(f"anchor text not found in '不可协商': {anchor}")

    scan = text
    ban_section = get_section(text, "禁止清单")
    if ban_section:
        scan = scan.replace(ban_section, "")
    hits = [phrase for phrase in BANNED if phrase in scan]
    if hits:
        errors.append("banned phrases outside '禁止清单': " + ", ".join(hits))

    if "不可协商" in titles and "语言" in titles:
        anchor_index = titles.index("不可协商")
        language_index = titles.index("语言")
        if anchor_index > language_index:
            errors.append("'不可协商' must appear before '语言' (end-of-prompt anchoring)")

    print(f"file={args.path}")
    print(f"chars={len(text)} lines={text.count(chr(10)) + 1} tokens~{estimate_tokens(text)}")
    for warning in warnings:
        print("WARN " + warning)
    for error in errors:
        print("ERROR " + error)

    if errors:
        return 1
    print("OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and lint DeepSeek Fable system prompts.")
    sub = parser.add_subparsers(dest="command", required=True)

    build_parser = sub.add_parser("build", help="fill placeholders and optionally drop sections")
    build_parser.add_argument("--out", required=True, help="output markdown path")
    build_parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="template path")
    build_parser.add_argument("--name", default="", help="replace {{ASSISTANT_NAME}}")
    build_parser.add_argument("--date", default="", help="replace {{DATE}}; defaults to today")
    build_parser.add_argument("--tools", default="", help="file whose content replaces {{TOOLS}}")
    build_parser.add_argument("--skills", default="", help="file whose content replaces {{SKILLS}}")
    build_parser.add_argument("--no-skills", action="store_true", help="replace {{SKILLS}} with nothing")
    build_parser.add_argument("--drop", default="", help="comma-separated section numbers to remove")
    build_parser.set_defaults(func=build)

    check_parser = sub.add_parser("check", help="lint an assembled prompt")
    check_parser.add_argument("path", help="markdown file to check")
    check_parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="allow {{...}} placeholders (use when linting the raw template)",
    )
    check_parser.set_defaults(func=check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
