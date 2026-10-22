"""
Text file analysis service.

Analyzes text files for encoding, word/line/character counts, and basic
language detection. Demonstrates data processing pipeline patterns used
in cloud-based document processing.
"""

import chardet


# Common English words for basic language detection
ENGLISH_COMMON_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there",
    "their", "what", "so", "up", "out", "if", "about", "who", "get",
    "which", "go", "me", "when", "make", "can", "like", "time", "no",
    "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then",
    "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "how", "our", "work", "first", "well",
    "way", "even", "new", "want", "because", "any", "these", "give",
    "day", "most", "us", "is", "are", "was", "were", "been", "has",
    "had", "did", "does",
}

# Minimum ratio of English words to consider text as English
ENGLISH_THRESHOLD = 0.15


def analyze_text(file_bytes: bytes, encoding: str = None) -> dict | None:
    """
    Analyze a text file and extract statistics.

    Args:
        file_bytes: Raw bytes of the file.
        encoding: Optional encoding override. If None, auto-detects.

    Returns:
        Dictionary with text analysis results, or None if the file
        cannot be decoded as text. Keys include:
            - encoding: Detected or specified encoding
            - line_count: Number of lines
            - word_count: Number of words
            - char_count: Number of characters
            - avg_line_length: Average characters per line
            - is_empty: Whether the file has no content
            - language_guess: Best guess at the language
    """
    # Auto-detect encoding if not provided
    if encoding is None:
        encoding = _detect_encoding(file_bytes)

    # Try to decode the file
    try:
        text = file_bytes.decode(encoding)
    except (UnicodeDecodeError, LookupError, TypeError):
        # Could not decode — likely a binary file
        return None

    # Check for null bytes (strong binary indicator)
    if "\x00" in text:
        return None

    # Calculate statistics
    is_empty = len(text.strip()) == 0
    lines = text.splitlines()
    line_count = len(lines)
    words = text.split()
    word_count = len(words)
    char_count = len(text)

    # Average line length
    if line_count > 0:
        avg_line_length = round(char_count / line_count, 1)
    else:
        avg_line_length = 0.0

    # Language detection
    language_guess = _guess_language(words)

    return {
        "encoding": encoding,
        "line_count": line_count,
        "word_count": word_count,
        "char_count": char_count,
        "avg_line_length": avg_line_length,
        "is_empty": is_empty,
        "language_guess": language_guess,
    }


def _detect_encoding(file_bytes: bytes) -> str:
    """
    Auto-detect file encoding using chardet.

    Args:
        file_bytes: Raw bytes of the file.

    Returns:
        Detected encoding string, defaults to 'utf-8' if detection fails.
    """
    if not file_bytes:
        return "utf-8"

    result = chardet.detect(file_bytes)
    encoding = result.get("encoding")

    if encoding is None:
        return "utf-8"

    return encoding


def _guess_language(words: list) -> str:
    """
    Basic language detection by checking for common English words.

    Args:
        words: List of words from the text.

    Returns:
        'english' if enough common English words are found, otherwise 'unknown'.
    """
    if not words:
        return "unknown"

    lower_words = [w.lower().strip(".,!?;:\"'()[]{}") for w in words]
    english_count = sum(1 for w in lower_words if w in ENGLISH_COMMON_WORDS)
    ratio = english_count / len(lower_words)

    if ratio >= ENGLISH_THRESHOLD:
        return "english"

    return "unknown"
