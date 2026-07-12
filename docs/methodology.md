# Methodology

本项目将 “Skill” 作宽口径处理：严格意义上的 Agent Skill、Codex/Claude/Cursor 规则与模板、MCP 工具集成、以及能显著增强 Agent 工作流的相关开源工具都会进入候选池。非严格 Skill 会在 `skill_type` 中标注为“相关工具”或“MCP / Tool integration”。

## 数据采集

`scripts/fetch_skills.py` 使用 GitHub Search API 搜索以下方向：

- AI Agent Skill / Codex Skill / Agent Skill / ChatGPT Skill / Claude Skill
- Cursor Rule / MCP server / Model Context Protocol
- prompt compression / context compression / token reduction / long context
- Office automation / DOCX / PPTX / XLSX / PDF generation
- RAG、web scraping、code review、testing、documentation 等 Agent 常用能力

采集字段包含仓库基础信息、topics、主语言、license、README 摘要、Release 或 ZIP 下载链接、当前 Star 等。若有 latest release，`download_url` 使用 release 页面，否则使用默认分支 ZIP。

## 去重与过滤

处理脚本按 `owner/name` 去重。以下仓库会被过滤或降权：

- archived 且 Star 不高的仓库
- 多年无维护且 Star 较低的仓库
- README 太短且用途不明的仓库
- 名称、简介、topics、README 摘要中缺少 Agent / Skill / LLM / MCP / Prompt / 文档处理等相关关键词的仓库

Star 很高的历史项目即使归档也可能保留，因为仍有参考价值。

## 分类

`scripts/process_skills.py` 使用关键词将项目归入以下用途分类：

- 代码生成
- 代码审查
- 测试生成
- 文档生成
- 数据分析
- 网页抓取
- 自动化办公
- 知识库 / RAG
- PDF / 文档处理
- 图像 / 多模态
- DevOps / CI/CD
- 个人效率
- Prompt 优化
- Token 节省
- MCP / Tool integration

如果一个项目命中多个类别，优先选择命中关键词最多的类别。

## Star 增长

每次采集会写入：

- `data/raw/latest.json`
- `data/snapshots/YYYY-MM-DD.json`
- `data/processed/skills.json`

处理脚本会读取当前快照之前最近的一份快照，按 `owner/name` 对比：

```text
weekly_star_delta = current_stars - previous_stars
growth_rate = weekly_star_delta / previous_stars
```

如果没有历史快照，`weekly_star_delta` 为 `null`，页面显示“首次采集，暂无增长数据”。

## 评分公式

精选区使用以下公式排序：

```text
score =
stars_score * 0.35 +
recent_activity_score * 0.25 +
readme_quality_score * 0.15 +
category_relevance_score * 0.15 +
growth_score * 0.10
```

- `stars_score`：对 Star 数做 log 归一化，避免超大项目完全碾压垂直项目。
- `recent_activity_score`：按 `pushed_at` 距今天数衰减。
- `readme_quality_score`：根据 README 长度和是否包含 install、usage、agent、docs 等信号计算。
- `category_relevance_score`：根据分类关键词命中数量和 Agent 相关信号计算。
- `growth_score`：根据本周 Star 增长做 log 归一化；首次采集时为 0。

评分不是质量的绝对判断，只用于帮助页面在每周自动更新后保持较高信噪比。
