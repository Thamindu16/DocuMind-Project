from src.documind.agent.agent import (
    GENERAL_PROMPT,
    STRICT_PROMPT,
    _clean_history,
    _main_source,
    get_prompt,
)


def test_strict_mode_uses_the_strict_prompt():
    assert get_prompt(False) == STRICT_PROMPT
    assert "never use your own general knowledge" in STRICT_PROMPT


def test_general_mode_allows_general_questions():
    assert get_prompt(True) == GENERAL_PROMPT
    assert "never use your own general knowledge" not in GENERAL_PROMPT


def test_history_keeps_only_valid_recent_messages():
    history = [{"role": "system", "content": "x"}, {"role": "user", "content": ""}]
    history += [{"role": "user", "content": f"m{i}"} for i in range(20)]
    cleaned = _clean_history(history)
    assert len(cleaned) == 8
    assert cleaned[-1]["content"] == "m19"


def test_main_source_is_the_file_of_the_closest_passage():
    result = "[hr_policy.txt] Annual Leave: 14 days.\n\n[benefits_policy.txt] Training Budget: 100,000 LKR."
    assert _main_source(result) == "hr_policy.txt"


def test_main_source_is_none_when_nothing_was_found():
    assert _main_source("No documents are indexed yet.") is None