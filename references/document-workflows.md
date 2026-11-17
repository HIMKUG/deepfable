# 文档与办公文件工作流

> 何时读：任务涉及 .docx、.pdf、.pptx、.xlsx/.csv，或要写提案/规格/决策文档时。读完产出：正确的文件路由、格式硬规则、QA 结果。

这是 docx / pdf / pptx / xlsx / doc-coauthoring 五个 skill 的最小执行清单。完整指令在 `assets/skills/<name>/SKILL.md`；遇到格式细节、脚本或 QA 时，先加载完整 skill。

## 目录

- 1. 路由
- 2. DOCX
- 3. PDF
- 4. PPTX
- 5. XLSX
- 6. 文档协作
- 7. 依赖
- 8. 验证原则

## 1. 路由

| 输入/输出 | 加载 | 不要做什么 |
|---|---|---|
| .docx / .dotx | `docx` | 不要用 docx-js 打开已有文件 |
| .pdf | `pdf` | 不要把可提取文本先转成图片 |
| .pptx / .potx | `pptx` | 不要用同一套圆角卡片模板套所有主题 |
| .xlsx / .xlsm / .csv | `xlsx` | 不要把公式算成硬编码值 |
| 提案、规格、决策文档、RFC | `doc-coauthoring` | 不要跳过上下文收集直接写全文 |

## 2. DOCX

**创建**：写 docx-js 脚本，`require('docx')`。常见坑：

- 默认 A4；US Letter 设 `page.size` 为 12240×15840 DXA。
- 表格同时设 `columnWidths` 和每个 cell 的 `width`，都用 DXA；列宽之和等于表宽。
- 表格底纹用 `ShadingType.CLEAR`，不要 `SOLID`。
- 列表用 `numbering` 配置，不要插入字面量 `•`。
- `ImageRun` 必须给 `type`；`PageBreak` 必须在 `Paragraph` 内。
- 不要用 `\n` 换行，用独立 `Paragraph`。
- 每个标题级别都显式设字体、`before`/`after`、`keepNext`。
- 目录要求标题使用内置 `HeadingLevel.*`；自定义样式要设 `outlineLevel`。

**编辑已有文件**：解包 → `merge_runs.py` 合并碎片 run → 改 `word/document.xml` → 重新打包 → `validate.py --original`。修订用 `<w:ins>/<w:del>`；批注用 `comment.py` 生成六类关联文件并放置锚点。

**读取**：`pandoc -t markdown file.docx`。

**验证**：转 PDF、`pdftoppm` 成图，实际查看页面；检查表格、分页、目录、图片。

## 3. PDF

- 读/合并/拆分/旋转/元数据：`pypdf`。
- 文本与表格抽取：`pdfplumber`。
- 新建：`reportlab`。
- 表单：先读该 skill 的 `FORMS.md`，用自带脚本检查可填充字段、边界框、填写结果。
- 扫描件 OCR：`pytesseract` + `pdf2image`；先确认是否真的需要 OCR。
- 验证：页数、文本是否可提取、目标页内容、表单字段值；不要只检查文件存在。

## 4. PPTX

**创建**：pptxgenjs。常见坑：

- 阴影 `offset` 必须 ≥ 0；向上投影用 `angle: 270` + 正 offset。
- 文本框有内边距；要与形状/线条对齐时设 `margin: 0`。
- 堆叠条形图的 `dataLabelPosition` 只能用 `ctr` / `inEnd` / `inBase`。
- 图标先渲染 SVG，再以 ≥256px 栅格化；base64 前缀必须完整。
- 不要默认 Aptos。

**模板**：解包/打包与普通 pptx 相同，保留 `.potx` 扩展名。

**QA（必做）**：

1. 内容：`slide_text.py` 抽文本，查缺失、错序、模板残留（`lorem`、`TODO`、`[insert`）。
2. 文件：`validate.py`；来自模板时加 `--original`。
3. 视觉：转 PDF → `pdftoppm` → 逐页看图。先查文字溢出/裁切，再查重叠、间距、对齐、对比度、占位符残留。

## 5. XLSX

每个输出都必须满足：

- 使用专业字体（Arial / Times New Roman），除非用户另有要求。
- 公式必须是公式，不是 Python 算好的硬编码值；输入变化时表要能重算。
- 零公式错误；`recalc.py` 报 `errors_found` 时不能交付。
- 严格按用户给的 tab 名、列名、公式；不要"重新设计"成另一个计算口径。
- 每个假设和硬编码数字在读者可见处标注来源；用户提供的就写"用户提供"。
- 新建的填写模板要有图例和一个示例行；编辑已有文件时不加示例行。
- 编辑已有文件：匹配原有约定，只写标记出的输入单元格，不动已有公式。

**重算**：`python scripts/recalc.py output.xlsx`。`status` 为 `success` 也要看 `not_computed`；`_xlfn.XLOOKUP`、跨工作簿引用等 LibreOffice 可能算不了。先写 2–3 个公式验证取值，再铺开整个模型。

## 6. 文档协作

适用于提案、规格、决策文档、RFC，不适用于一句话说明或短邮件。

1. **上下文收集**：问文档类型、读者、期望影响、模板/格式、约束；让用户一次性倾倒背景；再问 5–10 个缺口问题。问不出边界条件和取舍，说明上下文还不够。
2. **细化与结构**：先定 3–5 个章节；从最不确定的章节开始；每节先给 5–20 个选项，再让用户保留/删除/合并；分节起草，做外科手术式修改；摘要最后写。
3. **读者测试**：让没有上下文的读者看一遍，记录他们卡住的地方；修的是理解障碍，不是文采。

用户拒绝流程时，直接按自由方式写，不强行套三个阶段。

## 7. 依赖

- Node/npm：`docx`、`pptxgenjs`、`react-icons`、`sharp`（按需）。
- Python：`pypdf`、`pdfplumber`、`reportlab`、`openpyxl`、`pandas`、`python-pptx`、`Pillow`、`defusedxml`、`lxml`、`markitdown`、`pytesseract`、`pdf2image`。
- 系统：LibreOffice（`soffice`）、Poppler（`pdftoppm`）、pandoc。
- 缺依赖时说明影响并询问是否安装；不要静默用未经验证的实现替代。

## 8. 验证原则

- 按 skill 的 QA 执行，不自创更重的测试。
- 默认验证：打开/渲染产物、抽文本、重算公式、截图查看。
- 用户明确要求测试时，才跑测试套件、探针、冒烟或全量回归。
- 无法验证的部分明确说明，不宣称正确。
