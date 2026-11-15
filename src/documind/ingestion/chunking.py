import re


def _split_long(text, max_length):
    """Split a long paragraph on sentence boundaries into pieces of at most max_length."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current = [], ""
    for sentence in sentences:
        # A single sentence longer than the limit is cut into fixed pieces
        while len(sentence) > max_length:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(sentence[:max_length])
            sentence = sentence[max_length:]
        if current and len(current) + len(sentence) + 1 > max_length:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks


def chunk_by_paragraph(text, min_length=40, max_length=1000):
    """Split text on blank lines; very long paragraphs are split further by sentence."""
    chunks = []
    for raw in text.split("\n\n"):
        # Join line breaks inside a paragraph (PDF text often has them)
        paragraph = " ".join(raw.split())
        # Drop very short pieces such as document titles
        if len(paragraph) < min_length:
            continue
        if len(paragraph) <= max_length:
            chunks.append(paragraph)
        else:
            chunks.extend(_split_long(paragraph, max_length))
    return chunks