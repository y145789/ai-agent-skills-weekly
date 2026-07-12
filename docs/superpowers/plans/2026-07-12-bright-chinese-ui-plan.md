# 明亮中文 Skill 卡片界面 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将周报卡片改成中文主简介、同一区域展开详情，并把页面改为明亮低噪声 UI。

**Architecture:** Python 处理层生成 `description_zh`，React 类型和榜单消费该字段；`SkillCard` 只保留一个简介展开入口；CSS 通过 `.light` 默认主题和新的层级间距控制整体观感。

**Tech Stack:** Python 3、React 19、TypeScript、Vite、CSS、Lucide React。

## Global Constraints

- 原始 GitHub `description` 不删除，只在展开详情中展示。
- 不引入新的运行时依赖。
- 保留搜索、筛选、排序、下载和仓库链接。

### Task 1: 数据本地化

**Files:**
- Modify: `scripts/process_skills.py`
- Modify: `src/data/types.ts`

- [ ] 新增 `localized_description()`，基于分类、Skill 类型和仓库元数据生成 `description_zh`。
- [ ] 在 `process()` 为每个保留仓库写入 `description_zh`。
- [ ] 给 TypeScript `Skill` 增加可选 `description_zh`。
- [ ] 运行处理脚本并确认 JSON 包含该字段。

### Task 2: 卡片展开交互

**Files:**
- Modify: `src/components/SkillCard.tsx`
- Modify: `src/components/LeaderboardTable.tsx`

- [ ] 首屏使用 `description_zh`，只保留一个“展开完整简介”入口。
- [ ] 展开区显示中文说明、英文原文、使用场景和专项信息。
- [ ] 榜单简介使用 `description_zh`。
- [ ] 保留仓库、下载和键盘可用的展开按钮。

### Task 3: 明亮 UI

**Files:**
- Modify: `src/App.tsx`
- Modify: `src/styles/app.css`

- [ ] 默认主题设为明亮模式。
- [ ] 缩小 Hero 和统计面板，减少卡片标签和按钮视觉噪声。
- [ ] 调整卡片详情和表格为浅色边界、青绿色操作色。
- [ ] 保持桌面三列、平板两列、移动端单列响应式布局。

### Task 4: 验证与发布

**Files:**
- Modify: `项目日志.md`

- [ ] 运行 Python 编译检查、数据处理和 `pnpm run build`。
- [ ] 通过本地静态服务检查页面标题、卡片中文简介和详情展开。
- [ ] 提交并推送到 `main`，确认 GitHub Actions 和 Pages 部署成功。
