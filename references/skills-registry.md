# 技能注册表

> 何时读：任务可能命中外部 skill 时。读完产出：加载哪一个、为什么、需要哪些依赖。

内置 19 个 skill，完整副本在 `assets/skills/`。用 `python scripts/load_skill.py show <name>` 读取完整指令。不要只凭本表描述模仿。

## 目录

- 1. 文档与内容
- 2. 设计与视觉
- 3. 工程与测试
- 4. 沟通与辅助
- 5. 依赖与安装
- 6. 使用原则

## 1. 文档与内容

| Skill | 何时加载 | 关键能力 | 依赖 |
|---|---|---|---|
| `docx` | 创建、读取、编辑 .docx/.dotx；修订、批注、目录、表格 | docx-js 创建、OOXML 编辑、tracked changes、渲染校验 | npm `docx`、pandoc、LibreOffice、pdftoppm |
| `pdf` | 读取、合并、拆分、旋转、水印、表单、OCR | pypdf / pdfplumber / reportlab；表单脚本 | pypdf、pdfplumber、reportlab、Poppler；OCR 需 pytesseract/pdf2image |
| `pptx` | 创建或编辑 .pptx/.potx、模板、图表、视觉 QA | pptxgenjs、python-pptx、三层 QA、转图检查 | npm `pptxgenjs`、python-pptx、Pillow、defusedxml、lxml、LibreOffice、pdftoppm |
| `xlsx` | 创建、编辑、修复 .xlsx/.xlsm/.csv；公式、财务模型 | openpyxl、公式重算、错误检查、假设标注 | openpyxl、pandas、markitdown、LibreOffice |
| `doc-coauthoring` | 写文档、提案、技术规格、决策文档、RFC | 上下文收集 → 分节迭代 → 读者测试 | 无 |

## 2. 设计与视觉

| Skill | 何时加载 | 关键能力 | 依赖 |
|---|---|---|---|
| `frontend-design` | 新建或重塑网页/UI，需要明确视觉方向 | 主题定位、字体、版式、文案、两遍评审 | 无 |
| `canvas-design` | 海报、静态视觉、艺术图，输出 PNG/PDF | 设计哲学 → 画布表达；内置字体 | 内置字体；PNG/PDF 渲染工具 |
| `algorithmic-art` | p5.js 生成艺术、流场、粒子系统 | 算法哲学 → 交互式 p5.js 作品 | 浏览器；p5.js |
| `theme-factory` | 给幻灯片、文档、网页套统一主题 | 10 套配色/字体主题，可自定义 | 无 |
| `brand-guidelines` | 明确要求 Anthropic 品牌色/字体时 | Anthropic 官方品牌规范 | 无 |
| `slack-gif-creator` | 制作 Slack 动画 GIF | 尺寸/体积约束、帧合成、校验 | Pillow、imageio、numpy |

## 3. 工程与测试

| Skill | 何时加载 | 关键能力 | 依赖 |
|---|---|---|---|
| `mcp-builder` | 构建或审查 MCP server | 工具设计、协议、TypeScript/Python SDK、评估 | Node/Python MCP SDK、`npx @modelcontextprotocol/inspector` |
| `webapp-testing` | 用户要求测试本地 Web 应用 | Playwright、服务生命周期、侦察后操作 | Python `playwright` + Chromium |
| `web-artifacts-builder` | 复杂 React/Tailwind/shadcn 单文件页面 | 初始化、开发、打包成单 HTML | Node 18+、npm |
| `skill-creator` | 创建、修改、评估 skill | 结构、验证、评测、打包 | Python 脚本 |
| `claude-api` | 用户问 Claude API/SDK 时 | 模型、价格、参数、流式、工具、缓存 | 无 |

## 4. 沟通与辅助

| Skill | 何时加载 | 关键能力 | 依赖 |
|---|---|---|---|
| `internal-comms` | 写状态报告、领导层更新、内部通知 | 公司内部沟通格式 | 无 |
| `academy-guide` | 用户问如何使用 Claude 产品、要培训材料 | Claude Academy 课程与教程匹配 | 无 |
| `discernment-nudge` | 用户明确要求复核、审查或决策支持 | 在回答后追加 2–3 个针对性追问 | 无 |

`discernment-nudge` 默认不加载：它会在回答后追加追问，与"不写可选后续"的默认风格冲突。只有用户明确要求复核或审查时才用。

## 5. 依赖与安装

- 技能目录里的脚本按原样运行；先跑 `--help`。
- 依赖分为 npm、pip、系统工具三类：
  - npm：`docx`、`pptxgenjs`、React/Tailwind 相关包。
  - pip：`pypdf`、`pdfplumber`、`reportlab`、`openpyxl`、`pandas`、`python-pptx`、`Pillow`、`imageio`、`numpy`、`playwright`。
  - 系统：LibreOffice（`soffice`）、Poppler（`pdftoppm`）、pandoc、Chromium。
- 缺失依赖时先说明影响，再问是否安装；不要静默换成未经验证的实现。
- 第三方来源、许可证与声明集中在根目录 `THIRD_PARTY_NOTICES.txt`；再分发时保留该文件。

## 6. 使用原则

1. 一个任务一个 skill，最多两个。
2. 先读完整 `SKILL.md`，再读它要求的资源；不要整包读。
3. 技能路径是相对该 skill 目录的，不是相对 ds-Fable。
4. 技能规则覆盖任务步骤，但不覆盖七条锚定与用户当前请求。
5. 任务切换后停止套用旧 skill。
6. 技能缺失或依赖不可用时说明，并用核心规则完成。

## 7. 核心已吸收的内容

以下规则已提炼进 ds-Fable 的核心参考，简单任务不必加载完整 skill；遇到格式细节、脚本或 QA 时再加载：

| 已吸收 | 位置 |
|---|---|
| docx / pdf / pptx / xlsx 的硬规则与 QA | `document-workflows.md` |
| 前端视觉方向、字体、颜色、反模板 | `visual-design.md` |
| 去 AI 味与文档协作 | `writing-voice.md` |
| MCP 工具设计原则 | `backend-patterns.md` 第 12 节 |
| 输出形态与文件路由 | `output-routing.md` |
