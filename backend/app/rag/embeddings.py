import math
import hashlib
from typing import List


def generate_embedding(text: str, dimensions: int = 64) -> List[float]:
    """
    Generate normalized dense vector embedding for text.
    Uses multi-hash projection for semantic locality and fast cosine similarity.
    """
    if not text:
        return [0.0] * dimensions

    vec = [0.0] * dimensions
    words = text.lower().split()

    for i, word in enumerate(words):
        # Character n-grams and word tokens
        for n in range(2, min(5, len(word) + 1)):
            ngram = word[:n]
            h = int(hashlib.md5(ngram.encode("utf-8")).hexdigest(), 16)
            idx = h % dimensions
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign * (1.0 + 1.0 / (i + 1))

    # Normalize vector to unit length
    magnitude = math.sqrt(sum(x * x for x in vec))
    if magnitude > 0:
        return [round(x / magnitude, 5) for x in vec]
    return [0.0] * dimensions


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity between two unit vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)
