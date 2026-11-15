from src.documind.agent.tools import calculate, list_indexed_documents


def test_addition():
    assert calculate("14 + 9") == "23"


def test_subtraction():
    assert calculate("14 - 9") == "5"


def test_percentage():
    assert calculate("2500 * 15 / 100") == "375.0"


def test_rejects_python_code():
    """The calculator must never execute arbitrary code."""
    result = calculate("__import__('os').system('echo hacked')")
    assert result.startswith("Calculation error")


def test_division_by_zero_is_handled():
    assert calculate("1 / 0").startswith("Calculation error")


def test_list_documents_tool_formats_files(monkeypatch):
    monkeypatch.setattr(
        "src.documind.agent.tools.list_documents",
        lambda: [{"source": "hr_policy.txt", "chunks": 4}],
    )
    assert "hr_policy.txt (4 passages)" in list_indexed_documents()