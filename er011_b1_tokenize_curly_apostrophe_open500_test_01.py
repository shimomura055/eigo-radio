# er011_b1_tokenize_curly_apostrophe_open500_test_01.py
# OPEN-500(ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02): F1 tokenize が ASR出力の ’(U+2019) を語構成文字として扱う(既存承認仕様の整合是正)。
# API 0。実行: .venv\Scripts\python.exe -m pytest er011_b1_tokenize_curly_apostrophe_open500_test_01.py -q
import er011_b1_connected_speech_validator_01 as csv3


def test_tokenize_curly_apostrophe_is_word_char():
    assert csv3.tokenize("you’ve felt it") == ["you've", "felt", "it"]
    assert csv3.tokenize("you've felt it") == ["you've", "felt", "it"]


def test_tokenize_left_single_quote_and_none():
    assert csv3.tokenize("‘hello’") == ["'hello'"]
    assert csv3.tokenize("") == []
    assert csv3.tokenize(None) == []


def test_curly_and_straight_asr_give_same_f1_result():
    c = "You've felt the study suggests cats."
    a_curly = "You’ve felt the study suggests cats."
    a_straight = "You've felt the study suggests cats."
    r1 = csv3.classify_connected_speech(c, a_curly)
    r2 = csv3.classify_connected_speech(c, a_straight)
    assert r1.get("new_judgment") == r2.get("new_judgment")
    assert len(r1.get("f1_residual") or []) == len(r2.get("f1_residual") or [])


def test_no_false_residual_from_curly_contraction():
    c = "Now let's look closely. The studies suggest cats."
    a = "Now let’s look closely. The study suggests cats."
    r = csv3.classify_connected_speech(c, a)
    assert not (r.get("f1_residual") or [])
