---
name: deepseek-fable
description: 为 DeepSeek 模型编写和校准 Fable 式 system prompt，覆盖回答纪律、前端质感、后端模式、系统化排障与不过度防御，并内置 19 个可加载 skill。用于给 deepseek-flash / deepseek-v4-pro 写或调 system prompt、把其他模型的提示词移植到 DeepSeek、修复回答啰嗦或靠猜修 bug，或在 DeepSeek Agent 中动态调用 docx/pdf/pptx/xlsx、MCP、前端设计等技能。
metadata:
  version: "1.5.0"
  tags: deepseek, system-prompt, behavior, frontend, backend, debugging, skills
  dependencies: "Python 3.9+ for scripts; standard library only; no network. Optional bundled skills need Node/npm, LibreOffice, Poppler, pandoc, Playwright, or Python document libraries as listed in references/document-workflows.md. Behavior probes need a DeepSeek API key and network."
---

# DeepSeek Fable

一套面向 DeepSeek 的紧凑行为规范：把"自然、简洁、专业"翻译成可判定的规则，而不是形容词。主模板约 13 KB，可直接作为 system prompt，也可作为 Agent 的行为层。

范围：只规定行为、格式和任务流程，不规定内容政策。内容边界沿用模型自身策略与部署方要求。

## 目录

- 何时使用
- 快速路径
- 完整路径
- 按任务加载
- 动态技能
- 脚本
- 依赖
- 交付物
- 七条锚定
- 交付前检查
- 关键取舍

## 何时使用

- 为 DeepSeek API、私有部署或 Agent 框架编写 system prompt。
- 现有提示词有效，但输出仍像"AI 模板"：复述请求、层层列表、空泛免责、思考过程外泄。
- 多步任务里丢目标、重复劳动、过早宣布完成。
- 工具调用参数漂移、失败后静默换路。
- 写前端界面、服务端代码，或排障时需要一个稳定的行为基线。
- 部署的 DeepSeek Agent 需要按需加载 docx/pdf/pptx/xlsx、MCP、前端设计、文档协作等内置技能。

## 快速路径

直接用主模板，不定制：

1. 生成可粘贴的提示词（在技能目录下运行）：

   ```bash
   python scripts/fable_prompt.py build --out prompt.md --name "DeepSeek 模型"
   ```

2. 静态检查，退出码必须为 0：

   ```bash
   python scripts/fable_prompt.py check prompt.md
   ```

3. 把 `prompt.md` 作为 system prompt。`build` 会自动把 `assets/skills/` 下的 19 个技能清单注入 `{{SKILLS}}`；不需要时加 `--no-skills`。
4. 默认验证只做：跑一遍正常流程、构建、静态检查；有界面时截图查看。
5. 用户明确要求评测或测试时，才读 [references/evals.md](references/evals.md) 跑探针；不要主动加测试消耗用户时间。

## 完整路径

要裁剪或改规则时：

1. 确定部署形态：直连 OpenAI 兼容端点、Anthropic 兼容端点，还是接入 Agent 工具。
2. 读 [references/adapter-deepseek.md](references/adapter-deepseek.md)，核验模型名、思考模式、工具参数。
3. 用 `--drop` 裁掉不需要的章节。没有工具删 6、7；不涉及代码删 8；没有记忆删 9。
4. 改规则前读 [references/behavior-core.md](references/behavior-core.md) 与 [references/design-notes.md](references/design-notes.md)；一次只改一条，并说明理由。
5. 需要动态技能时，读 [references/skills-registry.md](references/skills-registry.md) 与 [references/skill-loading.md](references/skill-loading.md)，用 `scripts/load_skill.py` 加载；文档任务再读 [references/document-workflows.md](references/document-workflows.md)。
6. 默认验证：跑一遍正常流程、构建、静态检查；有界面时截图。用户明确要求评测时，才跑 [references/evals.md](references/evals.md) 的探针。
7. 记录变更理由与验证方式；用户未要求测试时，不写测试、不跑探针、不做冒烟或全量回归。

## 按任务加载

| 任务 | 读什么 | 读完应产出 |
|---|---|---|
| 调整行为规则 | [references/behavior-core.md](references/behavior-core.md) | 改动理由、默认验证结果 |
| 多步任务、无人值守 | [references/agentic-loop.md](references/agentic-loop.md) | 任务清单、阶段汇报、完成检查 |
| 决定回复还是文件 | [references/output-routing.md](references/output-routing.md) | 形态决定、文件清单、一行说明 |
| 去 AI 味、界面文案 | [references/writing-voice.md](references/writing-voice.md) | 删减后的版本 + 检查表 |
| 页面、组件、视觉交付 | [references/visual-design.md](references/visual-design.md) | 一句话方向、token 表、关键路由截图 |
| 服务端代码、API、数据访问 | [references/backend-patterns.md](references/backend-patterns.md) | 分层决定、事务边界、缓存失效方案 |
| 过度防御、错误吞噬、冗余判空 | [references/no-over-defense.md](references/no-over-defense.md) | 边界校验清单、错误传播路径、删掉的检查 |
| bug、测试失败、行为异常 | [references/debugging.md](references/debugging.md) | 一句话根因、可复现证据、验证结果 |
| 部署、换模型、参数异常 | [references/adapter-deepseek.md](references/adapter-deepseek.md) | 模型与参数核验记录 |
| 用户明确要求评测时 | [references/evals.md](references/evals.md) | 探针记录、失败原话 |
| 评估取舍、排查规则失效 | [references/design-notes.md](references/design-notes.md) | 变更理由、影响范围、回退方案 |
| Word / PDF / 演示 / 表格 | [references/document-workflows.md](references/document-workflows.md) | 文件路由、格式硬规则、QA 结果 |
| 选择或加载内置技能 | [references/skills-registry.md](references/skills-registry.md) + [references/skill-loading.md](references/skill-loading.md) | 技能选择、依赖、加载记录 |
| 创建或修改 skill | `assets/skills/skill-creator/SKILL.md` | 结构、校验、评测、打包 |
| 构建 MCP server | `assets/skills/mcp-builder/SKILL.md` | 工具设计、实现、评估 |

## 动态技能

技能包内置 19 个 skill，完整副本在 `assets/skills/`；第三方声明与许可证集中在根目录 `THIRD_PARTY_NOTICES.txt`。

```bash
python scripts/load_skill.py list
python scripts/load_skill.py show docx
python scripts/load_skill.py files docx
python scripts/load_skill.py check docx
python scripts/load_skill.py manifest --out skills.json
```

规则：

- 先读完整 `SKILL.md`，再执行；不要只凭描述模仿。
- 技能脚本直接运行，不重写；先跑 `--help`。
- 相对路径以该技能目录为根，不是 ds-Fable 目录。
- 一个任务一个 skill，最多两个。
- 技能规则覆盖任务步骤，但不覆盖七条锚定与用户当前请求。
- 技能缺失或依赖不可用时说明，并用核心规则完成。

部署侧接入方式：有工具调用能力时，把 `load_skill.py show <name>` 包成一个 `load_skill` 工具；没有工具时，由宿主在下一轮把目标 `SKILL.md` 注入上下文。模型不应假装加载了不存在的技能。

## 脚本

`scripts/fable_prompt.py` 只做确定性操作，不调用模型：

- `build`：替换 `{{ASSISTANT_NAME}}`、`{{DATE}}`、`{{TOOLS}}`、`{{SKILLS}}`；默认把 19 个内置技能清单注入 `{{SKILLS}}`，`--no-skills` 可关闭；`--drop` 按章节号裁剪；输出字符数、行数、估算 tokens。
- `check`：检查未替换占位符、必需章节、七条锚定是否完整、禁用短语是否出现在禁止清单之外、锚定节是否在语言节之前。有问题时退出码为 1。
- `load_skill.py`：`list` / `show` / `files` / `check` / `manifest`，只读 `assets/skills/`，不调用模型、不执行技能脚本。

原始模板含占位符，检查模板时加 `--allow-placeholders`：

```bash
python scripts/fable_prompt.py check assets/deepseek-fable.system.md --allow-placeholders
```

## 依赖

- Python 3.9+；`scripts/fable_prompt.py` 与 `scripts/load_skill.py` 只用标准库，不需要网络。
- 默认验证不需要 API key：正常流程、构建、静态检查、截图即可。
- 用户明确要求评测时，探针需要 DeepSeek API key 与网络；没有时明确记录"未验证"。
- 前端视觉验证需要可用的无头浏览器或 Browser 面板；没有时至少人工查看渲染结果。
- 内置文档技能的可选依赖：Node/npm（docx、pptxgenjs）、LibreOffice、Poppler、pandoc、Playwright、Python 文档库。缺依赖时按 `references/document-workflows.md` 说明影响。

## 交付物

| 文件 | 用途 |
|---|---|
| [assets/deepseek-fable.system.md](assets/deepseek-fable.system.md) | 可直接粘贴的 system prompt 模板 |
| [references/behavior-core.md](references/behavior-core.md) | 行为判据：寄存器、格式、事实、提问、错误处理 |
| [references/agentic-loop.md](references/agentic-loop.md) | 多步任务生命周期 |
| [references/output-routing.md](references/output-routing.md) | 回复 / 文件 / 网页 / 数据 / 长文判定表 |
| [references/writing-voice.md](references/writing-voice.md) | 去 AI 味：句子、用词、删除项、界面文案 |
| [references/visual-design.md](references/visual-design.md) | 前端质感：方向、字体、颜色、动效、反模板清单 |
| [references/backend-patterns.md](references/backend-patterns.md) | 后端：分层、API、数据访问、缓存、错误、重试、限流 |
| [references/no-over-defense.md](references/no-over-defense.md) | 不过度防御：边界校验、解析、错误传播、fallback 链 |
| [references/debugging.md](references/debugging.md) | 系统化排障：四阶段、假设验证、架构质疑 |
| [references/adapter-deepseek.md](references/adapter-deepseek.md) | 模型参数、思考模式、长上下文、失败模式 |
| [references/evals.md](references/evals.md) | 可选评测：探针、判分、记录表、失败修正 |
| [references/design-notes.md](references/design-notes.md) | 设计原理与维护方法 |
| [references/skills-registry.md](references/skills-registry.md) | 19 个内置 skill 的路由、依赖、何时加载 |
| [references/skill-loading.md](references/skill-loading.md) | 动态加载协议、优先级、上下文预算 |
| [references/document-workflows.md](references/document-workflows.md) | docx / pdf / pptx / xlsx / 文档协作的最小执行清单 |
| [assets/skills/INDEX.md](assets/skills/INDEX.md) | 内置技能索引 |
| [assets/skills/](assets/skills/) | 19 个内置 skill 完整副本（含脚本与资源） |
| [assets/upstream/](assets/upstream/) | 规范与模板 |
| [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) | 第三方来源、许可证与声明汇总 |
| [scripts/fable_prompt.py](scripts/fable_prompt.py) | 提示词构建与静态检查 |
| [scripts/load_skill.py](scripts/load_skill.py) | 技能列表、读取、检查、清单 |

## 七条锚定

无论裁剪成多短，这七条保留，并放在 system prompt 末尾（末尾锚定对抗长上下文依从衰减）：

1. 第一句给结论或交付物；不复述请求，不预告步骤。
2. 不确定就查或标注；不编造来源、数字、版本、API、链接。
3. 默认散文；列表只用于并列或对比，嵌套不超过两层，不整句加粗。
4. 一次最多一个澄清问题；只在错误猜测不可逆且代价高时先问。
5. 工具调用严格按 schema；失败重试一次后报告，不静默换路。
6. 思考内容不外泄；最终回答必须自包含。
7. 验证按用户要求分级；默认只做截图、正常流程、构建、静态检查，不主动加测试或探针。

## 交付前检查

- [ ] `build` 产物中没有 `{{...}}` 占位符
- [ ] `check` 退出码为 0
- [ ] 第 11 节七条完整，且位于语言节之前
- [ ] 目标模型、思考模式、工具参数已按官方文档核验
- [ ] 默认验证已完成：跑一遍正常流程、构建、静态检查；有界面时截图
- [ ] 用户没有要求测试时，没有额外加测试、探针、冒烟或全量回归
- [ ] `load_skill.py list` 显示 19 个内置技能，索引与 `assets/skills/` 一致
- [ ] 使用文档、视觉或工程技能时，已读完整 `SKILL.md`，没有只凭描述模仿
- [ ] 技能依赖缺失或不可用已说明，并给出回退方式
- [ ] 无法验证的部分已明确说明，没有宣称正确

## 关键取舍

- **规则而非人格**：DeepSeek 对"你是温暖、好奇的 AI"这类形容词依从弱，对"第一句给结论、最多问一个问题"这类可判定规则依从强。
- **双寄存器**：工作场景要短、要能扫读；闲聊要自然、不要列表。先判场景再选格式。
- **显式优先级**：`用户当前消息 > 项目/记忆中的偏好 > 默认风格`；冲突处写明谁赢。
- **压缩而非堆叠**：主模板约 13 KB，只保留判定点；细节进 references，按需加载。
- **验证分级**：默认只做截图、正常流程、构建、静态检查；测试、探针、冒烟、压测只在用户明确要求时进行。过度验证和过度防御一样，会消耗用户时间并掩盖真实问题。
- **预算无上限**：部署声明 unlimited 时，token 与算力不设上限，不因省 token 省略证据、边界情况和交付细节；但仍受长度纪律与验证分级约束，不主动加测试。
- **技能外挂**：19 个内置 skill 是任务级外挂，不替代七条锚定；加载前先读完整 `SKILL.md`，加载后按其流程执行，冲突时回到优先级。
