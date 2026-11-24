#!/usr/bin/env python3
"""Prepare the static site for its GitHub Pages project URL."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_FILES = (
    "index.html",
    "platform",
    "products",
    "support",
    "manual",
    "journal",
    "contact",
    "assets",
    "favicon.svg",
    "llms.txt",
    "robots.txt",
    "UNICOM MANUAL.pdf",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-path",
        default=f"/{ROOT.name}/",
        help="URL path prefix for the deployed site, including leading and trailing slashes.",
    )
    parser.add_argument("--output", default="_site", help="Output directory (must not already exist).")
    parser.add_argument(
        "--allow-indexing",
        action="store_true",
        help="Do not add noindex and include the production sitemap in the build output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_path = args.base_path
    if not base_path.startswith("/") or not base_path.endswith("/"):
        raise ValueError("--base-path must start and end with /")

    output = ROOT / args.output
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")

    for entry in SITE_FILES:
        source = ROOT / entry
        if not source.exists():
            raise FileNotFoundError(f"Website source is missing: {source}")
        destination = output / entry
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    if args.allow_indexing:
        shutil.copy2(ROOT / "sitemap.xml", output / "sitemap.xml")

    prefix_pattern = re.compile(r"""(?P<attribute>\b(?:href|src|action)=["'])/(?!/)""", re.IGNORECASE)
    html_files = sorted(output.rglob("*.html"))
    if not html_files:
        raise RuntimeError("No HTML pages were copied to the output directory.")

    for page in html_files:
        content = page.read_text(encoding="utf-8")
        content = prefix_pattern.sub(lambda match: f"{match.group('attribute')}{base_path}", content)
        if not args.allow_indexing:
            if "</head>" not in content:
                raise ValueError(f"Missing </head> in {page.relative_to(output)}")
            content = content.replace(
                "</head>",
                '  <meta name="robots" content="noindex, nofollow">\n</head>',
                1,
            )
        page.write_text(content, encoding="utf-8")

    (output / ".nojekyll").touch()
    print(f"Prepared {len(html_files)} HTML pages in {output.relative_to(ROOT)} with base path {base_path}")


if __name__ == "__main__":
    main()
