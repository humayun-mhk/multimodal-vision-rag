from utils.chat import is_greeting, plain_text


def test_common_greetings_bypass_document_retrieval():
    for greeting in ("hi", "Hello!", "hallo", "HEY", "good morning"):
        assert is_greeting(greeting)


def test_document_questions_are_not_treated_as_greetings():
    assert not is_greeting("hello, explain my document")


def test_plain_text_removes_markdown_bold_markers():
    assert plain_text("This is **important**.") == "This is important."
