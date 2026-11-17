<div align="center">

# DeepFable

**Fable-style discipline for DeepSeek.**

A compact behavior contract, a deterministic prompt toolchain, and 19 loadable agent skills — packaged as one skill.

![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?style=flat-square)
![Dependencies](https://img.shields.io/badge/core%20toolchain-stdlib%20only-2ea44f?style=flat-square)
![Skills](https://img.shields.io/badge/bundled%20skills-19-6f42c1?style=flat-square)
![References](https://img.shields.io/badge/references-14-0b7285?style=flat-square)
![Prompt](https://img.shields.io/badge/prompt-4.5K%20tokens-d97706?style=flat-square)

</div>

> **中文速览**  
> DeepFable 把 Fable 风格的行为约束、输出路由、工程与排障纪律，以及 19 个可动态加载的技能，打包成一个可直接用于 DeepSeek 的 skill。核心提示词约 4.5K tokens；构建、校验、加载全部由脚本完成。它不试图让模型"更聪明"，而是让模型在长任务里更少复述、更少过度规划、更少过度测试，并且真的能交付文件、代码和复现证据。

## The problem

DeepSeek models are strong at reasoning and code, but a long system prompt has three failure modes:

1. **Drift** — rules in the middle of a 5K-token prompt get diluted; the model falls back to generic assistant behavior.
2. **Fragmentation** — document, design, MCP, and testing knowledge lives in separate skills, each with its own entry conditions.
3. **Ad-hoc verification** — either nothing is checked, or every task triggers a full test suite nobody asked for.

DeepFable treats the prompt as a runtime, not a paragraph.

## The idea

Three layers, one package:

- **A behavior contract** that compiles values into checkable rules: conclusion first, two registers, cost × reversibility, boundary-only defense, verification by request.
- **A skill router** that knows when to load one of 19 bundled skills, and how to load it without reading the whole bundle.
- **Deterministic tooling** that builds the prompt, catches assembly errors, and lists/inspects/checks skills — no model calls, no network.

## What's inside

| Layer | Content | Real size |
|---|---|---|
| Behavior contract | `assets/deepseek-fable.system.md` | 13.3 KB source · ~4.5K tokens built |
| Reference library | 14 focused guides under `references/` | behavior, frontend, backend, debugging, evals |
| Skill library | 19 vendored skills under `assets/skills/` | 443 files · 66 executable helpers |
| Toolchain | `scripts/fable_prompt.py`, `scripts/load_skill.py` | Python stdlib only |
| Anchors | seven non-negotiable rules at the end of the prompt | end-of-prompt anchoring |

## Architecture

```text
deepseek-fable/
├── SKILL.md                       # entrypoint: routing, workflow, checklists
├── assets/
│   ├── deepseek-fable.system.md   # the 4.5K-token behavior contract
│   ├── skills/                    # 19 loadable skills (full copies)
│   │   ├── docx/  pdf/  pptx/  xlsx/  ...
│   │   └── INDEX.md
│   └── upstream/                  # spec and template
├── references/
│   ├── behavior-core.md           # why the rules exist
│   ├── agentic-loop.md            # multi-step task lifecycle
│   ├── output-routing.md          # reply vs file vs page vs data
│   ├── visual-design.md           # typography, color, motion, anti-slop
│   ├── writing-voice.md           # de-AI-ified prose and UI copy
│   ├── backend-patterns.md        # layering, API, cache, MCP tools
│   ├── no-over-defense.md         # boundary validation, fail fast
│   ├── debugging.md               # root cause before fixes
│   ├── document-workflows.md      # docx/pdf/pptx/xlsx hard rules
│   ├── skills-registry.md         # which skill to load, and when
│   ├── skill-loading.md           # load protocol and precedence
│   ├── adapter-deepseek.md        # thinking mode, params, context
│   ├── evals.md                   # optional 11-probe protocol
│   └── design-notes.md            # design rationale and maintenance
└── scripts/
    ├── fable_prompt.py            # build + static check
    └── load_skill.py              # list / show / files / check / manifest
```

## Quick start

```bash
# Build a deployable system prompt. The 19-skill index is injected automatically.
python scripts/fable_prompt.py build --out prompt.md --name "DeepSeek 模型"

# Static check: placeholders, required sections, seven anchors, banned phrases.
python scripts/fable_prompt.py check prompt.md

# Inspect the bundled skill library.
python scripts/load_skill.py list
python scripts/load_skill.py show pptx
python scripts/load_skill.py check xlsx
```

Drop `prompt.md` into `messages[0]` as the system prompt. For an agent runtime, expose `load_skill.py show <name>` as a `load_skill` tool; without a tool, inject the target `SKILL.md` into the next turn.

## The contract in seven lines

1. First sentence is the answer or the deliverable; no restating, no step preview.
2. If you don't know, look it up or mark it; never invent sources, numbers, versions, or APIs.
3. Prose by default; lists only for parallel or comparative content, at most two levels.
4. At most one clarifying question; ask first only when a wrong guess is irreversible and expensive.
5. Tool calls follow the schema; retry once, then report — never silently switch paths.
6. Reasoning stays internal; the final answer must stand alone.
7. Verification is tiered: screenshot, happy path, build, static check by default; tests and probes only when requested.

## Dynamic skills

The package vendors 19 skills with their scripts, references, assets, and licenses. They are loaded on demand, not pasted into the prompt.

```bash
python scripts/load_skill.py show docx      # full SKILL.md for the Word workflow
python scripts/load_skill.py files pptx     # what the deck workflow brings
python scripts/load_skill.py manifest       # machine-readable inventory
```

Loading rules:

- Read the full `SKILL.md` before executing; a description is not an implementation.
- Run the skill's scripts directly; don't rewrite them. `--help` first.
- Resolve relative paths against the skill directory, not the repo root.
- One skill per task, at most two.
- Skill instructions override task steps, never the seven anchors or the user's current request.

## Design principles

- **Rules over adjectives.** "Be concise" is not checkable; "3–6 sentences, no restating" is.
- **Two registers.** Work mode is scan-friendly; chat mode is prose. Judge the scene before choosing the format.
- **Cost × reversibility.** The decision to ask is a function of what a wrong guess costs and whether it can be undone.
- **Boundary-only defense.** Validate at HTTP, IPC, files, env, forms, third-party responses; trust types inside.
- **Verification by request.** Default checks prove it runs; tests prove it is correct. Don't conflate them.
- **End-of-prompt anchoring.** The seven rules are repeated at the end to survive long-context dilution.
- **Skills as plugins.** Capability lives in loadable instructions and scripts, not in one giant prompt.

## Evaluation

This repository does not ship invented benchmark numbers. It ships a protocol and a static checker.

The optional 11-probe protocol in [`references/evals.md`](references/evals.md) covers: first sentence, restatement, register, clarification, tool failure, fabrication, long-context constraint, closing, frontend, backend, and debugging. Run each probe three times per model; report pass@3.

```text
| Probe            | Baseline pass@3 | DeepFable pass@3 | Notes |
|------------------|-----------------|------------------|-------|
| first sentence   | run             | run              |       |
| restatement      | run             | run              |       |
| ...              | run             | run              |       |
```

Static checks are deterministic and run without an API key:

- unresolved `{{...}}` placeholders
- missing required sections
- fewer than seven anchors
- banned phrases outside the ban list
- anchors placed after the language section

## Compatibility

- DeepSeek `deepseek-flash` and `deepseek-v4-pro`, thinking and non-thinking modes. Model names and limits change; verify against the official docs before deployment.
- Core toolchain: Python 3.9+, standard library only, no network.
- Bundled document/design skills have optional dependencies: Node/npm, LibreOffice, Poppler, pandoc, Playwright, and Python document libraries. Missing dependencies are reported, not silently replaced.

## Third-party notices

All third-party provenance and license texts are consolidated in [`THIRD_PARTY_NOTICES.txt`](THIRD_PARTY_NOTICES.txt). No model vendor affiliation is claimed.

Original code and documentation in this repository are released under the MIT License. Vendored skills remain under their respective licenses.

## Status

Version 1.4.0. The prompt builds and lints cleanly; all 19 bundled skills pass structural checks. Behavioral evaluation is opt-in and requires a DeepSeek API key.
