from src.documind.ingestion.chunking import chunk_by_paragraph


def test_splits_on_blank_lines():
    text = "Title\n\n" + "A" * 50 + "\n\n" + "B" * 50
    chunks = chunk_by_paragraph(text)
    assert len(chunks) == 2  # the short title is dropped


def test_drops_short_pieces():
    assert chunk_by_paragraph("short") == []


def test_strips_surrounding_whitespace():
    assert chunk_by_paragraph("  " + "A" * 50 + "  ") == ["A" * 50]