from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from summarize_readme import summarize_readme


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
SNAPSHOT_DIR = ROOT / "data" / "snapshots"
API_ROOT = "https://api.github.com"

SEARCH_QUERIES = [
    '"codex skill" in:name,description,readme',
    '"prompt compression" in:name,description,readme',
    '"context compression" LLM in:name,description,readme',
    '"token reduction" LLM in:name,description,readme',
    '"office automation" AI in:name,description,readme',
    '"docx generation" AI in:name,description,readme',
    '"pptx generation" AI in:name,description,readme',
    '"pdf generation" LLM in:name,description,readme',
    '"agent skill" in:name,description,readme',
    '"AI agent skill" in:name,description,readme',
    '"ChatGPT skill" in:name,description,readme',
    '"Claude skill" in:name,description,readme',
    '"Cursor rules" in:name,description,readme',
    '"cursor rule" in:name,description,readme',
    '"MCP server" agent in:name,description,readme',
    '"model context protocol" in:name,description,readme',
    '"long context" agent in:name,description,readme',
    '"prompt optimization" agent in:name,description,readme',
    '"RAG" agent tool in:name,description,readme',
    '"web scraping" agent in:name,description,readme',
    '"code review" agent in:name,description,readme',
    '"test generation" LLM in:name,description,readme',
]

SEED_REPOSITORIES = [
    "microsoft/LLMLingua",
    "openai/tiktoken",
    "yamadashy/repomix",
    "mem0ai/mem0",
    "getzep/zep",
    "microsoft/markitdown",
    "docling-project/docling",
    "unstructured-io/unstructured",
    "python-openxml/python-docx",
    "scanny/python-pptx",
    "py-pdf/pypdf",
    "marp-team/marp",
    "marp-team/marp-cli",
    "gotenberg/gotenberg",
    "modelcontextprotocol/servers",
    "punkpeye/awesome-mcp-servers",
    "upstash/context7",
    "microsoft/playwright-mcp",
    "langchain-ai/langchain",
    "langchain-ai/langgraph",
    "run-llama/llama_index",
    "deepset-ai/haystack",
    "microsoft/autogen",
    "crewAIInc/crewAI",
    "browser-use/browser-use",
    "openai/openai-cookbook",
    "anthropics/anthropic-cookbook",
    "PatrickJS/awesome-cursorrules",
]

RELEVANCE_KEYWORDS = [
    "agent",
    "skill",
    "codex",
    "chatgpt",
    "claude",
    "cursor",
    "mcp",
    "model context protocol",
    "prompt",
    "llm",
    "automation",
    "rag",
    "docx",
    "pptx",
    "xlsx",
    "pdf",
    "token",
    "context",
    "workflow",
]


class GitHubClient:
    def __init__(self, token: str | None, pause: float = 0.3) -> None:
        self.token = token
        self.pause = pause
        self.warnings: list[str] = []

    def request(self, path: str, params: dict[str, Any] | None = None, raw: bool = False) -> Any:
        url = path if path.startswith("http") else f"{API_ROOT}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai-agent-skills-weekly",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if raw:
            headers["Accept"] = "application/vnd.github.raw"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
                time.sleep(self.pause)
                if raw:
                    return payload.decode("utf-8", errors="ignore")
                return json.loads(payload.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            if exc.code in {403, 429}:
                self.warnings.append(
                    f"GitHub API rate limit or abuse guard hit for {url}. Configure GH_TOKEN/GITHUB_TOKEN for higher limits."
                )
                return None
            if exc.code == 404:
                return None
            self.warnings.append(f"GitHub API error {exc.code} for {url}: {body[:180]}")
            return None
        except Exception as exc:  # noqa: BLE001
            self.warnings.append(f"Request failed for {url}: {exc}")
            return None


def normalize_repo(repo: dict[str, Any], client: GitHubClient, rich_metadata: bool) -> dict[str, Any] | None:
    owner = repo.get("owner", {}).get("login")
    name = repo.get("name")
    if not owner or not name:
        return None

    full_name = f"{owner}/{name}"
    description = repo.get("description") or ""
    topics = repo.get("topics") or []
    keyword_blob = " ".join([name, full_name, description, " ".join(topics)]).lower()
    if not any(keyword in keyword_blob for keyword in RELEVANCE_KEYWORDS):
        return None

    zip_url = f"https://github.com/{owner}/{name}/archive/refs/heads/{repo.get('default_branch') or 'main'}.zip"
    download_url = zip_url
    if rich_metadata:
        release = client.request(f"/repos/{owner}/{name}/releases/latest")
        download_url = release.get("html_url") if isinstance(release, dict) and release.get("html_url") else zip_url

    readme_text = ""
    if rich_metadata:
        readme_payload = client.request(f"/repos/{owner}/{name}/readme")
        if isinstance(readme_payload, dict) and readme_payload.get("content"):
            try:
                readme_text = base64.b64decode(readme_payload["content"]).decode("utf-8", errors="ignore")
            except Exception:
                readme_text = ""
    summary = summarize_readme(readme_text, fallback=description)

    license_info = repo.get("license") or {}
    now = datetime.now(timezone.utc).isoformat()
    return {
        "name": name,
        "owner": owner,
        "full_name": full_name,
        "repo_url": repo.get("html_url"),
        "description": description,
        "stars": repo.get("stargazers_count") or 0,
        "forks": repo.get("forks_count") or 0,
        "topics": topics,
        "primary_language": repo.get("language"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "license": license_info.get("spdx_id") or license_info.get("name"),
        "readme_summary": summary.summary,
        "readme_length": summary.length,
        "readme_quality_hints": summary.quality_hints,
        "skill_type": None,
        "category": None,
        "download_url": download_url,
        "weekly_star_delta": None,
        "previous_stars": None,
        "current_stars": repo.get("stargazers_count") or 0,
        "last_checked_at": now,
        "archived": bool(repo.get("archived")),
        "disabled": bool(repo.get("disabled")),
        "default_branch": repo.get("default_branch") or "main",
        "source_search_url": repo.get("url"),
    }


def search_repositories(client: GitHubClient, query: str, per_query: int) -> list[dict[str, Any]]:
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_query,
    }
    data = client.request("/search/repositories", params=params)
    if not isinstance(data, dict):
        return []
    return data.get("items") or []


def collect(per_query: int, max_repos: int) -> dict[str, Any]:
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    client = GitHubClient(token=token, pause=0.15 if token else 0.8)
    seen: set[str] = set()
    repos: list[dict[str, Any]] = []
    queries = SEARCH_QUERIES if token else SEARCH_QUERIES[:10]
    rich_metadata = bool(token)

    for full_name in SEED_REPOSITORIES:
        repo = client.request(f"/repos/{full_name}")
        if not isinstance(repo, dict):
            continue
        repo_full_name = repo.get("full_name")
        if not repo_full_name or repo_full_name.lower() in seen:
            continue
        seen.add(repo_full_name.lower())
        normalized = normalize_repo(repo, client, rich_metadata=rich_metadata)
        if normalized:
            repos.append(normalized)
        if len(repos) >= max_repos:
            break

    for query in queries:
        for repo in search_repositories(client, query, per_query):
            full_name = repo.get("full_name")
            if not full_name or full_name.lower() in seen:
                continue
            seen.add(full_name.lower())
            normalized = normalize_repo(repo, client, rich_metadata=rich_metadata)
            if normalized:
                repos.append(normalized)
            if len(repos) >= max_repos:
                break
        if len(repos) >= max_repos:
            break

    generated_at = datetime.now(timezone.utc).isoformat()
    return {
        "generated_at": generated_at,
        "snapshot_date": generated_at[:10],
        "source": "github-search-api",
        "token_used": bool(token),
        "query_count": len(queries),
        "warnings": sorted(set(client.warnings)),
        "repositories": repos,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch AI Agent Skill repositories from GitHub.")
    parser.add_argument("--per-query", type=int, default=15, help="GitHub search results per query.")
    parser.add_argument("--max-repos", type=int, default=220, help="Maximum normalized repositories to keep.")
    args = parser.parse_args()

    payload = collect(per_query=max(1, min(args.per_query, 50)), max_repos=max(10, args.max_repos))
    write_json(RAW_DIR / "latest.json", payload)
    write_json(SNAPSHOT_DIR / f"{payload['snapshot_date']}.json", payload)
    print(f"Fetched {len(payload['repositories'])} repositories.")
    for warning in payload.get("warnings", []):
        print(f"WARNING: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
