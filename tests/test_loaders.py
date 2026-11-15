import pytest

from src.documind.ingestion.loaders import extract_text


def test_reads_text_file(tmp_path):
    file = tmp_path / "note.txt"
    file.write_text("Hello policy", encoding="utf-8")
    assert extract_text(file) == "Hello policy"


def test_rejects_unsupported_file_type(tmp_path):
    file = tmp_path / "data.exe"
    file.write_bytes(b"abc")
    with pytest.raises(ValueError):
        extract_text(file)