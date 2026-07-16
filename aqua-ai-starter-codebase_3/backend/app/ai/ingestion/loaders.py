"""
Loads raw text out of each supported upload format for the admin training
module: PDF, CSV, JSON, Markdown, TXT. Each loader returns plain text; the
chunker and embedder don't need to know the source format.
"""
import csv
import json
from pathlib import Path


def load_pdf(path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_txt_or_markdown(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def load_csv(path: str) -> str:
    """Flattens each row into a sentence-like line so it embeds meaningfully."""
    lines = []
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append(", ".join(f"{k}: {v}" for k, v in row.items() if v))
    return "\n".join(lines)


def load_json(path: str) -> str:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    # Support either a list of {"text": ...} records or arbitrary nested JSON.
    if isinstance(data, list):
        return "\n".join(item.get("text", json.dumps(item)) if isinstance(item, dict) else str(item) for item in data)
    return json.dumps(data)


LOADERS = {
    "pdf": load_pdf,
    "txt": load_txt_or_markdown,
    "markdown": load_txt_or_markdown,
    "md": load_txt_or_markdown,
    "csv": load_csv,
    "json": load_json,
}


def load_document(path: str, source_type: str) -> str:
    loader = LOADERS.get(source_type.lower())
    if not loader:
        raise ValueError(f"Unsupported source_type: {source_type}")
    return loader(path)
