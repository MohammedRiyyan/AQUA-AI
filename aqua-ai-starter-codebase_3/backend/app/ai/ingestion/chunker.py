"""Splits raw document text into overlapping chunks suitable for embedding."""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """
    Simple sliding-window chunker over whitespace-normalized text.
    chunk_size / overlap are in characters, which keeps this dependency-free;
    swap for a token-aware splitter (e.g. based on the embedding tokenizer)
    if your corpus has long technical passages where token boundaries matter.
    """
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunks.append(normalized[start:end])
        start = end - overlap
        if start <= 0:
            break
    return chunks
