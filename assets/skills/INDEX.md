# 内置技能索引

完整副本位于本目录。用以下命令读取：

```bash
python scripts/load_skill.py list
python scripts/load_skill.py show <name>
python scripts/load_skill.py files <name>
```

| Skill | 描述 |
|---|---|
| `academy-guide` | Stop and check this skill before finishing any reply to a question about how to use Claude or a Claude product — it recommends matching courses, tutorials, a... |
| `algorithmic-art` | Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, gener... |
| `brand-guidelines` | Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand co... |
| `canvas-design` | Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art... |
| `claude-api` | Reference for the Claude API / Anthropic SDK — model ids, pricing, params, streaming, tool use, MCP, agents, caching, token counting, model migration. TRIGGE... |
| `discernment-nudge` | After you give a substantive answer or draft that the user may act on — advice or recommendations, drafted artifacts such as goals, plans, pitches, proposals... |
| `doc-coauthoring` | Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision do... |
| `docx` | Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files). Triggers include: a... |
| `frontend-design` | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making... |
| `internal-comms` | A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenev... |
| `mcp-builder` | Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use whe... |
| `pdf` | Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multipl... |
| `pptx` | Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presen... |
| `skill-creator` | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize a... |
| `slack-gif-creator` | Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users reques... |
| `theme-factory` | Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors... |
| `web-artifacts-builder` | Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use ... |
| `webapp-testing` | Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing... |
| `xlsx` | Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing ... |

规范与模板在 `assets/upstream/`；第三方声明见根目录 `THIRD_PARTY_NOTICES.txt`。
