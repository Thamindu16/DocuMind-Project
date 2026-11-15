from src.documind.ingestion.chunking import chunk_by_paragraph


def test_splits_on_blank_lines():
    text = "Title\n\n" + "A" * 50 + "\n\n" + "B" * 50
    chunks = chunk_by_paragraph(text)
    assert len(chunks) == 2  # the short title is dropped


def test_drops_short_pieces():
    assert chunk_by_paragraph("short") == []


def test_strips_surrounding_whitespace():
    assert chunk_by_paragraph("  " + "A" * 50 + "  ") == ["A" * 50]


def test_long_paragraph_is_split_into_smaller_chunks():
    text = "This is one sentence about company policy. " * 60
    chunks = chunk_by_paragraph(text, max_length=500)
    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_line_breaks_inside_a_paragraph_are_joined():
    text = "First line of a paragraph\nsecond line of the same paragraph that is long enough"
    assert chunk_by_paragraph(text) == [
        "First line of a paragraph second line of the same paragraph that is long enough"
    ]