from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "latest.json"
SNAPSHOT_DIR = ROOT / "data" / "snapshots"
PROCESSED_PATH = ROOT / "data" / "processed" / "skills.json"

RADAR_CATEGORIES = {
    "代码生成": ["code generation", "coding", "developer", "copilot", "cursor", "codegen"],
    "代码审查": ["code review", "review", "lint", "security review"],
    "测试生成": ["test generation", "testing", "unit test", "pytest", "jest"],
    "文档生成": ["documentation", "docs", "readme", "doc generation"],
    "数据分析": ["data analysis", "analytics", "pandas", "notebook", "sql"],
    "网页抓取": ["web scraping", "crawler", "scraper", "browser automation"],
    "自动化办公": ["office automation", "docx", "pptx", "xlsx", "spreadsheet", "excel", "powerpoint", "word"],
    "知识库 / RAG": ["rag", "retrieval", "knowledge base", "vector", "embedding"],
    "PDF / 文档处理": ["pdf", "document", "markdown", "report"],
    "图像 / 多模态": ["image", "vision", "multimodal", "ocr"],
    "DevOps / CI/CD": ["devops", "ci/cd", "github actions", "deployment", "kubernetes"],
    "个人效率": ["productivity", "automation", "workflow", "assistant"],
    "Prompt 优化": ["prompt optimization", "prompt", "prompt engineering", "template"],
    "Token 节省": ["token", "context compression", "prompt compression", "summarization", "long context"],
    "MCP / Tool integration": ["mcp", "model context protocol", "tool integration", "server"],
}

TOKEN_KEYWORDS = [
    "token reduction",
    "context compression",
    "prompt compression",
    "summarization",
    "long context",
    "memory compaction",
    "reduce llm cost",
    "prompt optimization",
    "context pruning",
    "token",
    "compress",
]

OFFICE_KEYWORDS = [
    "word",
    "docx",
    "powerpoint",
    "pptx",
    "excel",
    "xlsx",
    "pdf",
    "document layout",
    "report generation",
    "slide generation",
    "office automation",
]


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def days_since(value: str | None) -> int:
    dt = parse_date(value)
    if not dt:
        return 9999
    return max(0, (datetime.now(timezone.utc) - dt).days)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def previous_snapshot(current_date: str | None) -> dict[str, Any] | None:
    snapshots = sorted(SNAPSHOT_DIR.glob("*.json"))
    candidates = [path for path in snapshots if path.stem != current_date]
    if not candidates:
        return None
    return load_json(candidates[-1])


def blob(repo: dict[str, Any]) -> str:
    return " ".join(
        str(part or "")
        for part in [
            repo.get("name"),
            repo.get("owner"),
            repo.get("description"),
            repo.get("readme_summary"),
            repo.get("primary_language"),
            " ".join(repo.get("topics") or []),
        ]
    ).lower()


def skill_type(repo: dict[str, Any], text: str) -> str:
    if "cursor" in text and ("rule" in text or "rules" in text):
        return "Cursor Rule"
    if "mcp" in text or "model context protocol" in text:
        return "MCP / Tool integration"
    if "prompt" in text or "template" in text:
        return "Prompt / Template"
    if "skill" in text or "agent" in text or "codex" in text or "claude" in text:
        return "Skill"
    return "相关工具"


def choose_category(text: str) -> str:
    scores = []
    for category, keywords in RADAR_CATEGORIES.items():
        count = sum(1 for keyword in keywords if keyword in text)
        if count:
            scores.append((count, category))
    if not scores:
        return "个人效率"
    return sorted(scores, key=lambda item: (-item[0], item[1]))[0][1]


def stars_score(stars: int) -> float:
    return min(1.0, math.log10(max(stars, 0) + 1) / 5)


def recent_activity_score(pushed_at: str | None) -> float:
    days = days_since(pushed_at)
    if days <= 14:
        return 1.0
    if days <= 90:
        return 0.82
    if days <= 180:
        return 0.65
    if days <= 365:
        return 0.48
    if days <= 730:
        return 0.3
    return 0.14


def readme_quality_score(repo: dict[str, Any]) -> float:
    length = int(repo.get("readme_length") or 0)
    hints = repo.get("readme_quality_hints") or []
    base = min(1.0, length / 6000)
    hint_bonus = min(0.3, len(hints) * 0.08)
    return min(1.0, base + hint_bonus)


def category_relevance_score(text: str, category: str) -> float:
    keywords = RADAR_CATEGORIES.get(category, [])
    hits = sum(1 for keyword in keywords if keyword in text)
    agent_bonus = 0.2 if any(k in text for k in ["agent", "codex", "cursor", "claude", "chatgpt", "mcp"]) else 0
    return min(1.0, hits / 3 + agent_bonus)


def growth_score(delta: int | None) -> float:
    if delta is None or delta <= 0:
        return 0.0
    return min(1.0, math.log10(delta + 1) / 3)


def explain_token(repo: dict[str, Any], text: str) -> dict[str, Any]:
    if "summar" in text:
        how = "通过摘要和压缩上下文保留关键信息，减少传入模型的冗余内容。"
    elif "prompt" in text:
        how = "通过优化或模板化 Prompt，减少重复说明和无效上下文。"
    else:
        how = "通过上下文裁剪、记忆压缩或成本优化策略降低 token 使用。"
    if "api" in text or "python" in text:
        threshold = "中等，需要脚本或 API 集成。"
    else:
        threshold = "较低，可从 README 示例或模板开始。"
    return {
        "token_reduction_method": how,
        "best_for": "长对话、Agent 多步骤任务、知识库检索前处理、需要控制 LLM 成本的工作流。",
        "adoption_threshold": threshold,
        "recommendation": recommendation(repo.get("score", 0)),
    }


def explain_office(repo: dict[str, Any], text: str) -> dict[str, Any]:
    file_types = []
    for label, keywords in {
        "DOCX/Word": ["docx", "word"],
        "PPTX/PowerPoint": ["pptx", "powerpoint", "slide"],
        "XLSX/Excel": ["xlsx", "excel", "spreadsheet"],
        "PDF": ["pdf"],
        "Markdown/HTML": ["markdown", "html"],
    }.items():
        if any(keyword in text for keyword in keywords):
            file_types.append(label)
    if not file_types:
        file_types = ["文档/报告"]
    deps = "可能需要 Python、Node、LibreOffice、Pandoc 或浏览器渲染依赖，具体以仓库 README 为准。"
    if "api" in text or "docker" in text:
        deps = "通常需要额外运行时或服务依赖，适合自动化流水线。"
    return {
        "file_types": file_types,
        "content_fit": "适合报告、周报、数据文档、幻灯片、合同模板、批量办公自动化输出。",
        "extra_dependencies": deps,
        "recommendation": recommendation(repo.get("score", 0)),
    }


def recommendation(score: float) -> str:
    if score >= 0.78:
        return "★★★★★"
    if score >= 0.62:
        return "★★★★☆"
    if score >= 0.45:
        return "★★★☆☆"
    return "★★☆☆☆"


def filter_repo(repo: dict[str, Any], text: str) -> bool:
    if repo.get("disabled"):
        return False
    stars = int(repo.get("stars") or 0)
    if repo.get("archived") and stars < 5000:
        return False
    stale_days = days_since(repo.get("pushed_at"))
    if stale_days > 1460 and stars < 1000:
        return False
    if int(repo.get("readme_length") or 0) < 120 and stars < 200:
        return False
    relevance_terms = [
        "agent",
        "skill",
        "codex",
        "claude",
        "chatgpt",
        "cursor",
        "mcp",
        "llm",
        "prompt",
        "automation",
        "rag",
        "token",
        "pdf",
        "docx",
        "pptx",
        "xlsx",
    ]
    return any(term in text for term in relevance_terms)


def process() -> dict[str, Any]:
    raw = load_json(RAW_PATH)
    current_date = raw.get("snapshot_date")
    previous = previous_snapshot(current_date)
    previous_by_repo = {}
    if previous:
        for repo in previous.get("repositories", []):
            full_name = (repo.get("full_name") or f"{repo.get('owner')}/{repo.get('name')}").lower()
            previous_by_repo[full_name] = repo

    seen = set()
    processed = []
    for repo in raw.get("repositories", []):
        full_name = (repo.get("full_name") or f"{repo.get('owner')}/{repo.get('name')}").lower()
        if full_name in seen:
            continue
        seen.add(full_name)
        text = blob(repo)
        if not filter_repo(repo, text):
            continue
        repo["skill_type"] = skill_type(repo, text)
        repo["category"] = choose_category(text)
        previous_repo = previous_by_repo.get(full_name)
        current_stars = int(repo.get("stars") or repo.get("current_stars") or 0)
        previous_stars = int(previous_repo.get("stars") or previous_repo.get("current_stars") or 0) if previous_repo else None
        weekly_delta = current_stars - previous_stars if previous_stars is not None else None
        repo["current_stars"] = current_stars
        repo["previous_stars"] = previous_stars
        repo["weekly_star_delta"] = weekly_delta
        repo["growth_rate"] = None if previous_stars in {None, 0} or weekly_delta is None else weekly_delta / previous_stars
        score = (
            stars_score(current_stars) * 0.35
            + recent_activity_score(repo.get("pushed_at")) * 0.25
            + readme_quality_score(repo) * 0.15
            + category_relevance_score(text, repo["category"]) * 0.15
            + growth_score(weekly_delta) * 0.10
        )
        repo["score"] = round(score, 4)
        repo["recommendation"] = recommendation(score)
        repo["usage_scenarios"] = infer_usage_scenarios(repo["category"], text)
        repo["description_zh"] = localized_description(repo, repo["category"], text)
        if any(keyword in text for keyword in TOKEN_KEYWORDS):
            repo["token_saving"] = explain_token(repo, text)
        if any(keyword in text for keyword in OFFICE_KEYWORDS):
            repo["office_output"] = explain_office(repo, text)
        processed.append(repo)

    processed.sort(key=lambda r: (-r["score"], -int(r.get("stars") or 0), r.get("name") or ""))
    token_featured = sorted(
        [repo for repo in processed if repo.get("token_saving")],
        key=lambda r: (-r["score"], -int(r.get("stars") or 0)),
    )[:12]
    office_featured = sorted(
        [repo for repo in processed if repo.get("office_output")],
        key=lambda r: (-r["score"], -int(r.get("stars") or 0)),
    )[:12]
    top_stars = sorted(
        processed,
        key=lambda r: (-int(r.get("stars") or 0), parse_date(r.get("updated_at")) or datetime.min.replace(tzinfo=timezone.utc)),
        reverse=False,
    )[:50]
    top_stars = sorted(top_stars, key=lambda r: (-int(r.get("stars") or 0), -(parse_date(r.get("updated_at")) or datetime.min.replace(tzinfo=timezone.utc)).timestamp()))
    if previous:
        top_growth = sorted(
            [repo for repo in processed if repo.get("weekly_star_delta") is not None],
            key=lambda r: (-(repo.get("weekly_star_delta") or 0), -int(r.get("current_stars") or 0)),
        )[:50]
    else:
        top_growth = []

    radar = {}
    for category in RADAR_CATEGORIES:
        candidates = [repo for repo in processed if repo.get("category") == category]
        if len(candidates) < 3:
            category_terms = RADAR_CATEGORIES[category]
            expanded = [
                repo
                for repo in processed
                if any(term in blob(repo) for term in category_terms)
            ]
            candidates = candidates + [repo for repo in expanded if repo not in candidates]
        if len(candidates) < 3:
            candidates = candidates + [repo for repo in processed if repo not in candidates]
        radar[category] = sorted(candidates, key=lambda r: (-r["score"], -int(r.get("stars") or 0)))[:10]

    warnings = list(raw.get("warnings") or [])
    if not previous:
        warnings.append("首次采集，暂无增长数据。")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "last_checked_at": raw.get("generated_at"),
        "snapshot_date": current_date,
        "is_first_run": previous is None,
        "warnings": warnings,
        "stats": {
            "total_skills": len(processed),
            "total_stars": sum(int(repo.get("stars") or 0) for repo in processed),
            "token_saving_count": len(token_featured),
            "office_count": len(office_featured),
            "radar_category_count": len([items for items in radar.values() if items]),
        },
        "featured_token_saving": token_featured,
        "featured_office": office_featured,
        "top_stars": top_stars,
        "top_growth": top_growth,
        "radar": radar,
        "skills": processed,
    }


def infer_usage_scenarios(category: str, text: str) -> str:
    if category == "Token 节省":
        return "压缩上下文、长任务记忆整理、降低 API 调用成本。"
    if category == "自动化办公":
        return "批量生成文档、报表、幻灯片或电子表格。"
    if category == "MCP / Tool integration":
        return "为 Agent 接入外部工具、数据源或本地能力。"
    if category == "知识库 / RAG":
        return "构建检索增强问答、企业知识库和上下文注入。"
    if "cursor" in text:
        return "Cursor、Codex 或 IDE 内的编码规则与工作流模板。"
    return f"{category} 场景下的 Agent / LLM 工作流增强。"


def localized_description(repo: dict[str, Any], category: str, text: str) -> str:
    """Create a concise Chinese summary while retaining the repository text for details."""
    category_focus = {
        "代码生成": "面向代码编写与 Agent 编程协作",
        "代码审查": "面向代码审查、质量检查与安全风险发现",
        "测试生成": "面向测试用例生成与自动化验证",
        "文档生成": "面向技术文档、说明和知识内容生成",
        "数据分析": "面向数据整理、分析和洞察提取",
        "网页抓取": "面向网页信息采集与浏览器自动化",
        "自动化办公": "面向 Word、PPT、Excel、PDF 等办公内容生成",
        "知识库 / RAG": "面向知识库检索、RAG 问答和上下文注入",
        "PDF / 文档处理": "面向 PDF、报告和结构化文档处理",
        "图像 / 多模态": "面向图像理解、OCR 和多模态任务",
        "DevOps / CI/CD": "面向部署、流水线和工程运维自动化",
        "个人效率": "面向日常工作流和个人效率提升",
        "Prompt 优化": "面向 Prompt 设计、模板复用和效果优化",
        "Token 节省": "面向上下文压缩、记忆整理和 LLM 成本控制",
        "MCP / Tool integration": "面向 Agent 外部工具、数据源和本地能力接入",
    }.get(category, "面向 Agent 工作流的实用工具")
    scenario = infer_usage_scenarios(category, text).rstrip("。")
    source = str(repo.get("description") or repo.get("readme_summary") or "").lower()
    capability = "帮助 Agent 更稳定地完成相关任务"
    for keywords, phrase in [
        (["compress", "summar", "token", "context"], "减少无效上下文并控制模型输入成本"),
        (["generate", "create", "automation"], "把重复步骤整理成可复用的自动化流程"),
        (["search", "retrieval", "rag", "knowledge"], "把分散的信息转成可检索、可调用的上下文"),
        (["review", "lint", "security"], "提供结构化检查结果并降低遗漏风险"),
        (["image", "vision", "ocr"], "将图像或视觉信息转成 Agent 可处理的结果"),
    ]:
        if any(keyword in source for keyword in keywords):
            capability = phrase
            break
    return f"{category_focus}，{capability}。适合用于{scenario}。"


def main() -> int:
    if not RAW_PATH.exists():
        raise SystemExit("data/raw/latest.json not found. Run scripts/fetch_skills.py first.")
    payload = process()
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Processed {payload['stats']['total_skills']} repositories.")
    if payload["is_first_run"]:
        print("首次采集，暂无增长数据。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
