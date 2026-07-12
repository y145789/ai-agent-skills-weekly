from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ReadmeSummary:
    summary: str
    length: int
    quality_hints: list[str]


NOISE_LINE_RE = re.compile(
    r"^\s*(?:!\[.*?\]\(.*?\)|\[!\[.*?\]\(.*?\)\]\(.*?\)|<p\b|</p>|<img\b|---+)\s*$",
    re.IGNORECASE,
)


def clean_markdown(markdown: str) -> str:
    text = re.sub(r"```.*?```", " ", markdown, flags=re.DOTALL)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or NOISE_LINE_RE.match(stripped):
            continue
        stripped = re.sub(r"^#{1,6}\s+", "", stripped)
        stripped = re.sub(r"^\s*[-*+]\s+", "", stripped)
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        stripped = re.sub(r"https?://\S+", " ", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        if len(stripped) >= 18:
            lines.append(stripped)
    return "\n".join(lines)


def summarize_readme(markdown: str, fallback: str = "") -> ReadmeSummary:
    cleaned = clean_markdown(markdown or "")
    length = len(cleaned)
    lower = cleaned.lower()
    hints = []
    for label, needles in {
        "install": ["install", "npm install", "pip install", "uv add", "setup"],
        "usage": ["usage", "quickstart", "getting started", "example"],
        "agent": ["agent", "mcp", "cursor", "codex", "claude", "chatgpt"],
        "docs": ["documentation", "api", "configuration", "workflow"],
    }.items():
        if any(needle in lower for needle in needles):
            hints.append(label)

    candidates = re.split(r"(?<=[.!?。！？])\s+", cleaned.replace("\n", " "))
    chosen: list[str] = []
    for sentence in candidates:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) < 24 and len(chosen) == 0:
            continue
        chosen.append(sentence)
        if len(" ".join(chosen)) >= 220 or len(chosen) >= 2:
            break

    summary = " ".join(chosen).strip()
    if not summary:
        summary = (fallback or "暂无 README 摘要。").strip()
    if len(summary) > 280:
        summary = summary[:277].rstrip() + "..."

    return ReadmeSummary(summary=summary, length=length, quality_hints=hints)


if __name__ == "__main__":
    import argparse
    import pathlib

    parser = argparse.ArgumentParser(description="Create a short deterministic README summary.")
    parser.add_argument("readme", type=pathlib.Path)
    args = parser.parse_args()
    print(summarize_readme(args.readme.read_text(encoding="utf-8", errors="ignore")).summary)
