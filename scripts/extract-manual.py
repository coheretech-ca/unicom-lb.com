#!/usr/bin/env python3
"""Generate searchable manual pages and website-ready images from the source PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "UNICOM MANUAL.pdf"
IMAGE_DIR = ROOT / "assets" / "manual"
SCREEN_DIR = IMAGE_DIR / "screens"
TEMPLATE_PATH = ROOT / "manual" / "template.html"
OUTPUT_PATH = ROOT / "manual" / "index.html"

SCREENSHOTS = {
    "unicom-login": (7, 0),
    "pos-setup": (8, 1),
    "inventory-item": (26, 0),
    "accounting-main": (41, 0),
}

SECTION_HEADING = re.compile(r"^\d+(?:\.\d+)*\.?\s+[A-Za-z]")
PAGE_NUMBER = re.compile(r"^\d{1,2}$")
SKIP_TEXT = {
    "©Ali Rida",
    "UNICOM MANUAL",
    "Unicom manual| P a g e",
}


def clean_blocks(page: pymupdf.Page) -> list[str]:
    paragraphs: list[str] = []
    for block in page.get_text("blocks", sort=True):
        x0, y0, x1, y1, content, _block_no, block_type = block
        if block_type != 0:
            continue
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        lines = [
            line
            for line in lines
            if line not in SKIP_TEXT
            and not (PAGE_NUMBER.fullmatch(line) and (y0 < 75 or y1 > page.rect.height - 48))
        ]
        if lines:
            paragraphs.append("\n".join(lines))
    return paragraphs


def page_title(page_number: int, paragraphs: list[str]) -> str:
    if page_number == 1:
        return "UNICOM software manual"
    if page_number == 2:
        return "Copyright and rights"
    if page_number in (3, 4, 5):
        return "Contents"
    if page_number == 6:
        return "About the software"
    if page_number == 7:
        return "System presentation"

    for paragraph in paragraphs:
        for line in paragraph.splitlines():
            candidate = " ".join(line.split())
            if SECTION_HEADING.match(candidate):
                return candidate

    return f"Manual page {page_number}"


def paragraph_markup(paragraph: str) -> str:
    lines = [html.escape(line.strip()) for line in paragraph.splitlines() if line.strip()]
    if not lines:
        return ""
    return f"<p>{'<br>'.join(lines)}</p>"


def generate_page_markup(doc: pymupdf.Document) -> str:
    entries: list[str] = []
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    for page_index, page in enumerate(doc):
        page_number = page_index + 1
        paragraphs = clean_blocks(page)
        title = page_title(page_number, paragraphs)
        search_text = " ".join([title, *(line for paragraph in paragraphs for line in paragraph.splitlines())])
        image_name = f"page-{page_number:02}.jpg"
        image_path = IMAGE_DIR / image_name
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(1.6, 1.6),
            colorspace=pymupdf.csRGB,
            alpha=False,
        )
        pixmap.save(image_path, jpg_quality=78)

        body = "\n".join(paragraph_markup(paragraph) for paragraph in paragraphs)
        entries.append(
            f"""
<article class="manual-page" id="manual-page-{page_number:02}" data-manual-entry
  data-search="{html.escape(search_text.casefold(), quote=True)}">
  <h2>{html.escape(title)} <span>Page {page_number}</span></h2>
  <div class="manual-copy">{body}</div>
  <figure>
    <img src="/assets/manual/{image_name}" alt="Scanned page {page_number} of the UNICOM software manual"
      loading="lazy" decoding="async" width="950" height="1344">
    <figcaption>Original manual page {page_number} · 2019 edition</figcaption>
  </figure>
</article>"""
        )

    return "\n".join(entries)


def extract_screenshots(doc: pymupdf.Document) -> None:
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    for name, (page_index, image_index) in SCREENSHOTS.items():
        images = doc[page_index].get_images(full=True)
        if image_index >= len(images):
            raise RuntimeError(f"Expected screenshot {name} on manual page {page_index + 1}")
        extracted = doc.extract_image(images[image_index][0])
        extension = extracted["ext"]
        (SCREEN_DIR / f"{name}.{extension}").write_bytes(extracted["image"])


def main() -> None:
    if not PDF_PATH.is_file():
        raise FileNotFoundError(f"Upload the source manual at {PDF_PATH} before generating site assets.")
    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError(f"Manual page template is missing: {TEMPLATE_PATH}")

    doc = pymupdf.open(PDF_PATH)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    OUTPUT_PATH.write_text(
        template.replace("{{MANUAL_ENTRIES}}", generate_page_markup(doc)),
        encoding="utf-8",
    )
    extract_screenshots(doc)
    print(f"Generated {len(doc)} searchable manual pages in {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
