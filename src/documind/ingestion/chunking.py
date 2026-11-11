def chunk_by_paragraph(text, min_length=40):
    """Split text on blank lines; each paragraph becomes one chunk."""
    paragraphs = [p.strip() for p in text.split("\n\n")]
    # Drop very short pieces such as document titles
    return [p for p in paragraphs if len(p) >= min_length]