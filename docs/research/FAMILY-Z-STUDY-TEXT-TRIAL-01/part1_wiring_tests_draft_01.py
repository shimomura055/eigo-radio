# part1_wiring_tests_draft_01.py  (DEV雛形。Production未編集。FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_13)
# 実装委任で `er003_kp_general_explanation_01_test_01.py` として root へ移す。移設時に importorskip を外す。
# 実行: py -m pytest docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/part1_wiring_tests_draft_01.py -q
#  - Section A: Trial-04 fixtureの自己検証(Trial資産のみに依存。今すぐ実行可)。
#  - Section B/C: 提案API(`er003_kp_general_explanation_01`)に対するtest。module未作成の間は importorskip でskip。
#  - Section D: 統合test(実装委任で作成。現時点はskip)。
# 提案API(PART1_WIRING_DESIGN_01.md 2節):
#   build_prompt(phrases: list[str]) -> str                       # 入力は英語表現のみ(他引数なし)
#   phrases_signature(items: list[dict]) -> str                    # explanation_phrase(it)の並びのsha(gloss/source_sentenceは含めない)
#   generate_general_explanations(phrases, *, call_fn=None, client=None, process=None) -> dict   # {"items":{...}, "audit":{...}}
#   generate_for_kp_items(items, *, call_fn=None, client=None) -> dict   # items -> explanation_phrase(it)のみ抽出して上記へ
#   resolve_general_explanations(items, cached, *, call_fn=None, client=None) -> dict  # sig一致ならreuse
#   assemble_part1(kp_items, explanations, translations, article_text) -> list[dict]   # 出力組合せ(決定論)
import hashlib
import inspect
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
WORKS = ["gift", "ig_nobel", "open_window"]


def _inputs():
    return json.load(open(os.path.join(HERE, "INPUT_04.json"), encoding="utf-8"))


# ---------------- Section A: Trial-04 fixture自己検証(今すぐ実行可) ----------------
def test_A1_trial_alpha_prompt_files_match_trial_builder():
    import run_trial_04 as t4
    inp = _inputs()
    for w in WORKS:
        kps = [(x["kp"], x["gloss_in_text_ja"], x["sentence"]) for x in inp[w]]
        want = t4.p1_prompt(kps, "alpha")
        got = open(os.path.join(HERE, f"_prompt_04_{w}_p1a.txt"), encoding="utf-8").read()
        assert got.strip() == want.strip(), w


def test_A2_trial_alpha_prompt_contains_no_gloss_sentence_or_translation():
    inp = _inputs()
    for w in WORKS:
        p = open(os.path.join(HERE, f"_prompt_04_{w}_p1a.txt"), encoding="utf-8").read()
        for x in inp[w]:
            assert x["kp"] in p
            for forbidden in (x["gloss_in_text_ja"], x["sentence"], x["sentence_ja"]):
                assert forbidden not in p, (w, forbidden)


def test_A3_trial_alpha_usage_recorded_for_cost_baseline():
    costs = []
    for w in WORKS:
        for r in ("r1", "r2"):
            d = json.load(open(os.path.join(HERE, f"usage_04a_{r}_p1_{w}.json"), encoding="utf-8"))
            assert d["model_actual"] == "gpt-6-luna"
            costs.append(d["cost_jpy_at_160"])
    assert 0.05 < sum(costs) / len(costs) < 0.12   # 実測平均 約0.078円/call(3KP)


# ---------------- Section B: 提案module(未作成の間skip) ----------------
def _mod():
    return pytest.importorskip("er003_kp_general_explanation_01")


def _items(gloss="崩れる", sent="They tried to cross a bog, but the ground gave way beneath them."):
    return [
        {"rank": 1, "display_phrase": "gave way", "used_form": "give way", "fulltext_source_ref": "fulltext_exact_v1",
         "japanese_gloss": gloss, "source_sentence": sent, "meaning_in_text_en": "To collapse under pressure."},
        {"rank": 2, "display_phrase": "at a moment's notice", "used_form": "at a moment's notice",
         "fulltext_source_ref": "fulltext_exact_v1", "japanese_gloss": "急なことにも即座に",
         "source_sentence": "Inventing convincing stories at a moment's notice was Vera's speciality.",
         "meaning_in_text_en": "Without much warning."},
    ]


def _ok_response(phrases):
    return "\n".join(f"### {i}. {p}\n{p} の一般的な解説です。核となる意味と主要な使い方を説明します。" for i, p in enumerate(phrases, 1))


def _call_recorder(responder):
    calls = []

    def call_fn(prompt):
        calls.append(prompt)
        text = responder(prompt, len(calls))
        return text, "gpt-6-luna", {"input_tokens": 10, "cached_input_tokens": 0, "output_tokens": 10}, f"resp_{len(calls)}"
    return call_fn, calls


def test_B1_build_prompt_takes_only_phrases():
    m = _mod()
    assert list(inspect.signature(m.build_prompt).parameters) == ["phrases"]
    gp = list(inspect.signature(m.generate_general_explanations).parameters)
    assert gp[0] == "phrases" and set(gp[1:]) <= {"call_fn", "client", "process"}


@pytest.mark.parametrize("work", WORKS)
def test_B2_prompt_byte_identical_to_trial04_alpha(work):
    m = _mod()
    phrases = [x["kp"] for x in _inputs()[work]]
    want = open(os.path.join(HERE, f"_prompt_04_{work}_p1a.txt"), encoding="utf-8").read()
    assert m.build_prompt(phrases).strip() == want.strip()


def test_B3_wrapper_never_sends_gloss_source_sentence_or_meaning_to_llm():
    m = _mod()
    call_fn, calls = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    items = _items()
    m.generate_for_kp_items(items, call_fn=call_fn)          # 高水準wrapper: items -> explanation_phrase(it)のみ抽出
    assert len(calls) == 1
    for it in items:
        for k in ("japanese_gloss", "source_sentence", "meaning_in_text_en"):
            assert it[k] not in calls[0], k
    assert "give way" in calls[0] and "at a moment's notice" in calls[0]
    assert "gave way" not in calls[0]                         # display_phrase(本文表層形)ではなくused_form(基本形)


def test_B4_non_english_or_long_phrase_is_rejected_before_call():
    m = _mod()
    call_fn, calls = _call_recorder(lambda p, n: "")
    for bad in ("崩れる", "x" * 200, "a phrase\nwith newline", "他の語 give way"):
        with pytest.raises(ValueError):
            m.generate_general_explanations([bad], call_fn=call_fn)
    assert calls == []


def test_B5_signature_ignores_gloss_and_sentence_but_not_expression_or_order():
    m = _mod()
    a = m.phrases_signature(_items())
    assert a == m.phrases_signature(_items(gloss="別の意味", sent="Completely different sentence."))
    assert a != m.phrases_signature(list(reversed(_items())))
    changed = _items()
    changed[0]["used_form"] = "give up"
    assert a != m.phrases_signature(changed)


def test_B6_resume_reuses_when_signature_same_and_regenerates_when_changed():
    m = _mod()
    call_fn, calls = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    first = m.resolve_general_explanations(_items(), None, call_fn=call_fn)
    assert len(calls) == 1 and first["reused_from_previous_run"] is False
    again = m.resolve_general_explanations(_items(gloss="Human Review後の別gloss"), first, call_fn=call_fn)
    assert len(calls) == 1 and again["reused_from_previous_run"] is True      # gloss変更ではLLMを呼ばない
    changed = _items()
    changed[1]["used_form"] = "on short notice"
    call_fn2, calls2 = _call_recorder(lambda p, n: _ok_response(["give way", "on short notice"]))
    redo = m.resolve_general_explanations(changed, again, call_fn=call_fn2)
    assert len(calls2) == 1 and redo["reused_from_previous_run"] is False


def test_B7_parse_failure_retries_once_then_fails_closed():
    m = _mod()
    call_fn, calls = _call_recorder(lambda p, n: "壊れた出力(見出しなし)")
    with pytest.raises(m.KpGeneralExplanationError):
        m.generate_general_explanations(["give way", "at a moment's notice"], call_fn=call_fn)
    assert len(calls) == 2                                                     # 初回+技術retry1回のみ(上限厳守)


def test_B8_heading_mismatch_is_structure_failure():
    m = _mod()
    bad = "### 1. give way\n解説です。\n### 2. different phrase\n解説です。"
    call_fn, calls = _call_recorder(lambda p, n: bad)
    with pytest.raises(m.KpGeneralExplanationError):
        m.generate_general_explanations(["give way", "at a moment's notice"], call_fn=call_fn)


def test_B9_model_mismatch_is_contract_violation_without_fallback():
    m = _mod()

    def call_fn(prompt):
        return _ok_response(["give way"]), "some-other-model", {"input_tokens": 1, "output_tokens": 1}, "resp_x"
    with pytest.raises(Exception):
        m.generate_general_explanations(["give way"], call_fn=call_fn)


def test_B10_audit_records_model_prompt_sha_input_sha_response_id():
    m = _mod()
    call_fn, _ = _call_recorder(lambda p, n: _ok_response(["give way"]))
    r = m.generate_general_explanations(["give way"], call_fn=call_fn)
    a = r["audit"]
    for k in ("model", "prompt_sha256", "input_sha256", "response_ids", "calls", "process"):
        assert k in a, k
    assert a["model"] == "gpt-6-luna"
    assert a["prompt_sha256"] == hashlib.sha256(m.build_prompt(["give way"]).encode("utf-8")).hexdigest()


def test_B11_routing_process_registered_to_support_model():
    m = _mod()
    import er006_model_routing_contract_01 as routing
    assert routing.PROCESS_MODEL_MAP[m.MODEL_ROUTING_PROCESS] == routing.SUPPORT_MODEL


# ---------------- Section C: 出力組合せ(決定論) ----------------
def test_C1_assemble_has_five_fields_in_user_order_and_verbatim_quote():
    m = _mod()
    article = ("They tried to cross a bog, but the ground gave way beneath them. "
               "Inventing convincing stories at a moment's notice was Vera's speciality.")
    call_fn, _ = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    ex = m.resolve_general_explanations(_items(), None, call_fn=call_fn)
    tr = {1: "彼らは沼地を渡ろうとしたが、足元の地面が崩れた。", 2: "その場ですぐに、もっともらしい話を作ることがヴェラの得意技だった。"}
    out = m.assemble_part1(_items(), ex, tr, article)
    first = out[0]
    assert list(first)[:5] == ["english_expression", "meaning_in_text_ja", "source_sentence", "source_sentence_ja", "explanation_ja"]
    assert first["source_sentence"] in article


def test_C2_assemble_refuses_unresolved_gloss_and_non_verbatim_quote():
    m = _mod()
    call_fn, _ = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    ex = m.resolve_general_explanations(_items(), None, call_fn=call_fn)
    hr = _items()
    hr[0]["gloss_alignment_status"] = "HUMAN_REVIEW_REQUIRED"
    with pytest.raises(Exception):
        m.assemble_part1(hr, ex, {1: "訳", 2: "訳"}, "x give way x at a moment's notice")
    with pytest.raises(Exception):   # 本文に無い引用英文
        m.assemble_part1(_items(), ex, {1: "訳", 2: "訳"}, "unrelated text")


def test_C3_missing_translation_policy_is_explicit_not_silent():
    # 訳の生成元はユーザー判断待ち(DESIGN_01 11節)。判断後に (T1)欠落=STOP か (T2)訳欄を出さない のどちらかへ固定する。暗黙の空欄は禁止。
    m = _mod()
    call_fn, _ = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    ex = m.resolve_general_explanations(_items(), None, call_fn=call_fn)
    art = "x " + _items()[0]["source_sentence"] + " " + _items()[1]["source_sentence"]
    try:
        out = m.assemble_part1(_items(), ex, {}, art)
    except Exception:
        return
    assert all(("source_sentence_ja" not in r) or r["source_sentence_ja"] for r in out)


# ---------------- Section D: 統合(実装委任で埋める。現時点はskip) ----------------
@pytest.mark.skip(reason="実装委任で、mock modeのZ stage_kpに対して作成する")
def test_D1_z_stage_kp_runs_part1_after_kp_pass_before_tts_and_fails_closed():
    """期待: stage_kp内 kp_expl_b1b の後に kp_part1_b1b をensure_stage。失敗はFamilyZE2EStop(FAMILY_Z_KP_GENERAL_EXPLANATION_NOT_OK)でTTS未着手。"""


@pytest.mark.skip(reason="実装委任で作成")
def test_D2_x_scaffold_runs_part1_only_for_b1b_and_failure_sets_kp_stage_status_rc3():
    """期待: run_theme_scaffoldのb1bのみ。失敗はkp_stage_status=KP_PART1_FAILED(...)でmain()がrc=3。a2では呼ばれない。"""


@pytest.mark.skip(reason="実装委任で作成")
def test_D3_other_families_unchanged_no_call():
    """期待: A/B/C(strategy_l)経路ではPart 1 moduleが呼ばれずAPI呼出0・出力不変。"""
