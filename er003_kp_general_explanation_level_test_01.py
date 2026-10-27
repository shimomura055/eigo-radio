# er003_kp_general_explanation_level_test_01.py
# SLOT-23-CONSUMER-DESIGN-01 委任_04B: Part 1生成工程のlevel化(Std=a2: 日本語解説・難易度調整のみ)とAdv(b1b)不変のgolden test。API 0。
#  G: golden(b1bのPrompt/sha/signature/保存doc/HTMLバイト固定、a2のsha固定)
#  L: level分離(a2 Head差分は2点のみ・BODY同一・隔離維持・stale・保存先dir分離・T1訳はlevel間再利用なし)
import hashlib
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import er003_kp_general_explanation_01 as m
import er003_kp_source_sentence_ja_01 as ja

# ---- golden値(委任_04B実装前のHEAD=35e508a28の実出力から算出した固定値。b1bはこれが1文字でも動いたらAdv回帰) ----
GOLDEN_B1B_SHA = "4d7ae557190650650592ae5e6df09e1946d87c582e32187bb8dfd6d32cfaf694"
GOLDEN_A2_SHA = "df21d3ef998a2b8d2aeb7219e25b2fdb85b0de32ec4b8a776c1a6fd10e2ee662"
GOLDEN_B1B_PROMPT_SHA = "18b8d02c042347d34f6d2e9cb6d590fdaf6fa68355dfebee14b094d88e703b2b"
GOLDEN_B1B_SIGNATURE = "7b560131503252c303332007266062009927afa497f338bd22370e16c98819b1"
GOLDEN_B1B_HTML_SHA = "20bd83daeb579e2cc9a70ce6a887da24b7a32076541922a62c62186e125d7d2a"

ITEMS = [
    {"rank": 1, "display_phrase": "gave way", "used_form": "give way", "fulltext_source_ref": "fulltext_exact_v1",
     "japanese_gloss": "崩れる", "source_sentence": "They tried to cross a bog, but the ground gave way beneath them."},
    {"rank": 2, "display_phrase": "at a moment's notice", "used_form": "at a moment's notice", "fulltext_source_ref": "fulltext_exact_v1",
     "japanese_gloss": "急なことにも即座に", "source_sentence": "Inventing convincing stories at a moment's notice was Vera's speciality."},
]
ARTICLE = ("They tried to cross a bog, but the ground gave way beneath them. "
           "Inventing convincing stories at a moment's notice was Vera's speciality.")
PHRASES = ["give way", "at a moment's notice"]


def _ok(phrases):
    return "\n".join(f"### {i}. {p}\n{p} の一般的な解説です。核となる意味と主要な使い方を説明します。" for i, p in enumerate(phrases, 1))


def _call(phrases=PHRASES, model="gpt-6-luna"):
    calls = []

    def fn(prompt):
        calls.append(prompt)
        return _ok(phrases), model, {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 1}, f"r{len(calls)}"
    return fn, calls


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _build_audio_dir(tmp_path, level, explanations_doc, translations_doc, rows):
    b = tmp_path / "audio" / level
    (b / "key_phrases").mkdir(parents=True)
    (b / "study_text").mkdir(parents=True)
    (b / "key_phrases" / m.EXPLANATIONS_FILENAME).write_text(json.dumps(explanations_doc, ensure_ascii=False), encoding="utf-8")
    (b / "key_phrases" / ja.TRANSLATIONS_FILENAME).write_text(json.dumps(translations_doc, ensure_ascii=False), encoding="utf-8")
    (b / "key_phrases" / "keywords_canonicalized.json").write_text(json.dumps({"items": ITEMS}, ensure_ascii=False), encoding="utf-8")
    m.write_study_text(str(b / "study_text"), rows, level=level)
    return str(tmp_path / "audio")


def _tr_doc():
    def fn(prompt):
        t = "\n".join(f"{i}. 訳文{i}です。" for i in range(1, 3))
        return t, "gpt-6-luna", {}, "t1"
    return None


def _translations_doc(items):
    sents = ja.strict_sentences(items)
    return {"schema": ja.SCHEMA_VERSION, "translations_signature": ja.translations_signature(items), "sentences": sents,
            "ranks": [it["rank"] for it in ja.sorted_items(items)],
            "items": [{"rank_index": i, "sentence": s, "source_sentence_ja": f"訳文{i}です。"} for i, s in enumerate(sents, 1)], "audit": {}}


def _render(tmp_path, monkeypatch, level):
    rec = tmp_path / "decision.json"
    rec.write_text(json.dumps({"decision": "T1", "source": "x"}), encoding="utf-8")
    monkeypatch.setattr(m, "TRANSLATION_DECISION_RECORD", str(rec))
    fn, _ = _call()
    ex = m.generate_for_kp_items(ITEMS, call_fn=fn, level=level)
    tr = _translations_doc(ITEMS)
    rows = m.assemble_part1(ITEMS, ex, ja.translations_by_rank(tr), ARTICLE, level=level)
    d = _build_audio_dir(tmp_path, level, ex, tr, rows)
    return d, ex, rows


# ============ G: golden ============
def test_G1_b1b_prompt_template_sha_fixed():
    assert m.PROMPT_TEMPLATE_SHA256 == GOLDEN_B1B_SHA


def test_G2_a2_prompt_template_sha_fixed():
    assert m.PROMPT_TEMPLATE_SHA256_A2 == GOLDEN_A2_SHA
    assert m.PROMPT_TEMPLATE_SHA256_A2 != m.PROMPT_TEMPLATE_SHA256


def test_G3_b1b_full_prompt_bytes_fixed_and_default_level_is_b1b():
    assert _sha(m.build_prompt(PHRASES)) == GOLDEN_B1B_PROMPT_SHA
    assert m.build_prompt(PHRASES) == m.build_prompt(PHRASES, "b1b")


def test_G4_b1b_signature_payload_unchanged_so_existing_adv_artifacts_stay_fresh():
    assert m.phrases_signature(ITEMS) == GOLDEN_B1B_SIGNATURE
    assert m.phrases_signature(ITEMS, level="b1b") == GOLDEN_B1B_SIGNATURE
    assert m.phrases_signature(ITEMS, level="a2") != GOLDEN_B1B_SIGNATURE


def test_G5_b1b_saved_doc_has_no_level_key_and_study_json_level_is_advanced(tmp_path, monkeypatch):
    d, ex, rows = _render(tmp_path, monkeypatch, "b1b")
    assert "level" not in ex
    saved = json.load(open(os.path.join(d, "b1b", "study_text", m.PART1_FILE_STEM + ".json"), encoding="utf-8"))
    assert saved["level"] == "Advanced"


def test_G6_b1b_page_html_bytes_fixed(tmp_path, monkeypatch):
    d, _, _ = _render(tmp_path, monkeypatch, "b1b")
    html_default = m.study_html_for_audio_dir(d)
    assert html_default == m.study_html_for_audio_dir(d, level="b1b")
    assert _sha(html_default) == GOLDEN_B1B_HTML_SHA


# ============ L: level分離 ============
def test_L1_a2_head_differs_from_b1b_in_exactly_two_places_and_body_is_identical():
    a, b = m.PROMPT_HEAD_A2, m.PROMPT_HEAD
    assert a.replace("A2〜B1相当", "B1〜B2相当").replace(m._STD_DIFFICULTY_LINE, "") == b
    assert m.PROMPT_HEADS["a2"].count("A2〜B1相当") == 1 and "(A2)" not in a and "(B1)" not in a
    assert not m.PAGE_FORBIDDEN_RE.search(a)
    assert m.build_prompt(PHRASES, "a2").endswith("\n" + m.PROMPT_BODY)
    assert "日本語で書いて" in a                      # 解説言語は日本語のまま(作業仮定A)


def test_L2_a2_generation_uses_a2_prompt_records_level_and_quality_check_is_same_as_adv():
    fn, calls = _call()
    out = m.generate_for_kp_items(ITEMS, call_fn=fn, level="a2")
    assert calls[0] == m.build_prompt(PHRASES, "a2") and out["level"] == "a2"
    assert out["audit"]["prompt_template_sha256"] == m.PROMPT_TEMPLATE_SHA256_A2
    assert out["phrases_signature"] == m.phrases_signature(ITEMS, level="a2")
    short = lambda p: ("\n".join(f"### {i}. {x}\n短い。" for i, x in enumerate(PHRASES, 1)), "gpt-6-luna", {}, "x")
    with pytest.raises(m.KpGeneralExplanationError):
        m.generate_for_kp_items(ITEMS, call_fn=short, level="a2")


def test_L3_isolation_is_kept_per_level():
    p = m.build_prompt(PHRASES, "a2")
    m.check_prompt_isolation(p, PHRASES, ITEMS, level="a2")
    with pytest.raises(m.KpIsolationViolation):
        m.check_prompt_isolation(p, PHRASES, ITEMS)                      # a2 Promptをb1bとして通せない
    with pytest.raises(m.KpIsolationViolation):
        m.check_prompt_isolation(m.build_prompt(PHRASES), PHRASES, ITEMS, level="a2")
    leaked = [dict(ITEMS[0], japanese_gloss="a" * 5), ITEMS[1]]
    bad = p.replace("1. 英語表現: give way", "1. 英語表現: give way aaaaa")
    with pytest.raises(m.KpIsolationViolation):
        m.check_prompt_isolation(bad, PHRASES, leaked, level="a2")
    with pytest.raises(m.KpGeneralExplanationInputError):
        m.build_prompt(PHRASES, "c1")


def test_L4_levels_do_not_reuse_or_pass_freshness_across_each_other():
    fn, calls = _call()
    ex_b = m.generate_for_kp_items(ITEMS, call_fn=fn, level="b1b")
    ex_a = m.generate_for_kp_items(ITEMS, call_fn=fn, level="a2")
    m.require_fresh_general_explanations(ITEMS, ex_b, next_command="x", level="b1b")
    m.require_fresh_general_explanations(ITEMS, ex_a, next_command="x", level="a2")
    with pytest.raises(m.KpGeneralExplanationStale):
        m.require_fresh_general_explanations(ITEMS, ex_a, next_command="x", level="b1b")
    with pytest.raises(m.KpGeneralExplanationStale):
        m.require_fresh_general_explanations(ITEMS, ex_b, next_command="x", level="a2")
    n = len(calls)
    r = m.resolve_general_explanations(ITEMS, ex_a, call_fn=fn, level="a2")
    assert r["reused_from_previous_run"] is True and len(calls) == n
    r = m.resolve_general_explanations(ITEMS, ex_a, call_fn=fn, level="b1b")      # a2 docをAdvが使わない=再生成
    assert r["reused_from_previous_run"] is False and len(calls) == n + 1


def test_L5_a2_pages_read_level_dir_only_and_do_not_touch_b1b(tmp_path, monkeypatch):
    d, ex, rows = _render(tmp_path, monkeypatch, "a2")
    h = m.study_html_for_audio_dir(d, level="a2")
    assert "Vocabulary &amp; Expressions" in h and "give way" in h and "訳文1です。" in h
    assert not os.path.exists(os.path.join(d, "b1b"))
    with pytest.raises(m.KpGeneralExplanationError):
        m.study_html_for_audio_dir(d)                                     # b1b dirは無い=Advは従来どおりfail-closed
    saved = json.load(open(os.path.join(d, "a2", "study_text", m.PART1_FILE_STEM + ".json"), encoding="utf-8"))
    assert saved["level"] == "Standard"


def test_L6_t1_translation_module_unchanged_and_level_independent():
    # 訳工程は変更しない(Prompt共通・level別dirで独立実行=level間再利用なし)。signatureにlevelが入らないことを固定
    assert "level" not in ja.translations_signature.__code__.co_varnames
    assert ja.translations_signature(ITEMS) == ja.translations_signature(list(ITEMS))
