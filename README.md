# AI Agent Skills 周报网站

这是一个可部署到 GitHub Pages 的静态周报网站，用于每周自动收集、分析、展示高价值 AI Agent Skill 与 Agent 工作流相关开源项目。

它会从 GitHub 搜索 Agent Skill、Codex Skill、Claude Skill、Cursor Rule、MCP、Token 节省、Office/PDF 输出、RAG、测试生成、代码审查等方向的仓库，生成历史快照，并计算 Star 增长榜。

## 功能

- 每周自动采集 GitHub 仓库数据
- 保存 `data/raw/latest.json`、`data/snapshots/YYYY-MM-DD.json`、`data/processed/skills.json`
- 展示 Token 节省精选区
- 展示 Office / Word / PPT / PDF 输出精选区
- 展示总 Star 榜 Top 50
- 展示 Star 增长最快榜
- 展示“实用 Skill 雷达”用途分类
- 支持搜索、分类筛选、排序、详情展开
- 暗色模式优先，并支持亮暗切换
- GitHub Actions 自动更新和部署到 GitHub Pages

## 本地运行

安装依赖：

```bash
npm install
```

采集并处理数据：

```bash
npm run update:data
```

启动开发服务器：

```bash
npm run dev
```

构建静态网页：

```bash
npm run build
```

构建产物在 `dist/`，可直接部署到 GitHub Pages、Netlify、Vercel 或任意静态站点服务。

## GitHub Token 配置

脚本会读取环境变量：

```bash
GH_TOKEN=your_token
```

或：

```bash
GITHUB_TOKEN=your_token
```

没有 token 时也能运行，但 GitHub Search API 速率限制较低，脚本会减少查询量，并在 `warnings` 中提示。GitHub Actions 中默认使用仓库内置的 `GITHUB_TOKEN`，不要把 token 写死在代码里。

## 手动更新数据

```bash
python scripts/fetch_skills.py
python scripts/process_skills.py
```

可选参数：

```bash
python scripts/fetch_skills.py --per-query 20 --max-repos 300
```

第一次运行时没有历史快照，`weekly_star_delta` 会是 `null`，页面会显示“首次采集，暂无增长数据”。第二次及之后运行会读取上一次快照计算增长。

## 部署到可公开搜索的网站

本地文件不会自己定时运行。要让网站公开访问并每周自动更新，需要把本项目推送到一个**公开的 GitHub 仓库**：

1. 在 GitHub 新建公开仓库，例如 `ai-agent-skills-weekly`，不要勾选初始化 README。
2. 在本项目目录执行：

   ```bash
   git init
   git add .
   git commit -m "feat: initial AI Agent Skills weekly site"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/ai-agent-skills-weekly.git
   git push -u origin main
   ```

3. 在仓库 `Settings → Pages → Build and deployment` 中选择 `GitHub Actions`。
4. 在 `Settings → Actions → General` 中确认 Workflow permissions 为 `Read and write permissions`。
5. 在 `Actions` 中手动运行 `Weekly Skill Update`，完成首次采集和发布。

发布地址通常是 `https://<你的用户名>.github.io/ai-agent-skills-weekly/`。首次收录到搜索引擎可能需要一段时间；工作流会自动生成 `robots.txt` 和 `sitemap.xml`，便于抓取。当前工作流在推送到 `main`/`master` 时会首次部署，之后每周一 08:00（北京时间）自动采集、构建和部署，也支持 `workflow_dispatch` 手动运行。

工作流使用 GitHub Actions 自带的 `GITHUB_TOKEN`，代码中没有硬编码密钥。公开仓库默认可直接使用；若组织策略限制 Actions 写权限，需要在仓库设置中打开上述权限。

工作流位于 `.github/workflows/weekly-update.yml`。它会：

- 安装 Python 和 Node 依赖
- 运行采集脚本
- 处理 JSON 数据
- 构建静态网页
- 提交更新后的 `data/` 和 `dist/`
- 部署 `dist/` 到 GitHub Pages

## 榜单计算逻辑

总 Star 榜 Top 50：

```text
stars 降序
stars 相同时 updated_at 较新者优先
```

Star 增长最快榜：

```text
weekly_star_delta 降序
weekly_star_delta 相同时 current_stars 降序
```

Star 增长计算：

```text
weekly_star_delta = current_stars - previous_stars
growth_rate = weekly_star_delta / previous_stars
```

## Skill 分类标准

分类由 `scripts/process_skills.py` 中的关键词规则决定，覆盖：

- 代码生成 / Code generation
- 代码审查 / Code review
- 测试生成 / Testing
- 文档生成 / Documentation
- 数据分析 / Data analysis
- 网页抓取 / Web scraping
- 自动化办公 / Office automation
- 知识库 / RAG
- PDF / 文档处理
- 图像 / 多模态
- DevOps / CI/CD
- 个人效率 / Productivity
- Prompt 优化
- Token 节省
- MCP / Tool integration

不是严格 Skill 但对 Agent 工作流很有价值的项目会被标注为“相关工具”“相关模板”或“MCP / Tool integration”。

## 评分规则

精选区按 `score` 排序：

```text
score =
stars_score * 0.35 +
recent_activity_score * 0.25 +
readme_quality_score * 0.15 +
category_relevance_score * 0.15 +
growth_score * 0.10
```

详细说明见 [docs/methodology.md](docs/methodology.md)。

## 项目结构

```text
.
├── README.md
├── package.json
├── src/
│   ├── App.tsx
│   ├── components/
│   ├── data/
│   └── styles/
├── scripts/
│   ├── fetch_skills.py
│   ├── process_skills.py
│   └── summarize_readme.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── snapshots/
├── public/
├── .github/
│   └── workflows/
│       └── weekly-update.yml
└── docs/
    └── methodology.md
```
