from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> List[str]:
    """
    Split text into overlapping semantic chunks, attempting to break
    cleanly on paragraphs or sentence boundaries.
    """
    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks = []
    start = 0

    while start < len(cleaned):
        end = start + chunk_size

        if end >= len(cleaned):
            chunk = cleaned[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Look for natural breaking points (newline or period)
        break_point = -1
        sub = cleaned[start:end]

        for sep in ["\n\n", "\n", ". ", "? ", "! ", " "]:
            pos = sub.rfind(sep)
            if pos != -1 and pos > chunk_size * 0.4:
                break_point = start + pos + len(sep)
                break

        if break_point == -1:
            break_point = end

        chunk = cleaned[start:break_point].strip()
        if chunk:
            chunks.append(chunk)

        # Advance with overlap
        start = break_point - chunk_overlap
        if start >= len(cleaned) or start <= 0 and len(chunks) > 0:
            start = break_point

    return chunks
