"""Generate crawler-facing files for the deployed static site."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-url", required=True, help="Public site URL without a trailing slash")
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()

    site_url = args.site_url.rstrip("/")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n",
        encoding="utf-8",
    )
    (out / "sitemap.xml").write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        f"  <url><loc>{site_url}/</loc></url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
