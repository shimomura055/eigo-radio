# er003_kp_general_explanation_01_test_01.py
# FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14: 学習テキスト Part 1 案α Production配線のtest(API 0。LLMはmock call_fn)。
# 雛形: docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/part1_wiring_tests_draft_01.py
#  A: Trial-04資産との同一性(Prompt byte一致・実出力6件のparse較正・実データ較正)
#  B: module単体(入力隔離・signature・resume・retry・fail-closed)
#  C: 組立(5項順・逐語assert・HR/未評価STOP・訳PENDING)
#  M: Opus M1〜M4・実装時必須の固定
#  R: 描画停止(判断記録なし→描画なし。DefaultOffIsolation相当)
import glob
import hashlib
import inspect
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL = os.path.join(HERE, "docs", "research", "FAMILY-Z-STUDY-TEXT-TRIAL-01")
sys.path.insert(0, HERE)
import er003_kp_general_explanation_01 as m
import er006_model_routing_contract_01 as routing

WORKS = ["gift", "ig_nobel", "open_window"]


def _trial_inputs():
    return json.load(open(os.path.join(TRIAL, "INPUT_04.json"), encoding="utf-8"))


def _items(gloss="崩れる", sent="They tried to cross a bog, but the ground gave way beneath them."):
    return [
        {"rank": 1, "display_phrase": "gave way", "used_form": "give way", "fulltext_source_ref": "fulltext_exact_v1",
         "japanese_gloss": gloss, "source_sentence": sent, "meaning_in_text_en": "To collapse under pressure."},
        {"rank": 2, "display_phrase": "at a moment's notice", "used_form": "at a moment's notice",
         "fulltext_source_ref": "fulltext_exact_v1", "japanese_gloss": "急なことにも即座に",
         "source_sentence": "Inventing convincing stories at a moment's notice was Vera's speciality.",
         "meaning_in_text_en": "Without much warning."},
    ]


ARTICLE = ("They tried to cross a bog, but the ground gave way beneath them. "
           "Inventing convincing stories at a moment's notice was Vera's speciality.")


def _ok_response(phrases):
    return "\n".join(f"### {i}. {p}\n{p} の一般的な解説です。核となる意味と主要な使い方を説明します。*{p}* のように使われます。" for i, p in enumerate(phrases, 1))


def _call_recorder(responder, model="gpt-6-luna"):
    calls = []

    def call_fn(prompt):
        calls.append(prompt)
        text = responder(prompt, len(calls))
        return text, model, {"input_tokens": 10, "cached_input_tokens": 0, "output_tokens": 10}, f"resp_{len(calls)}"
    return call_fn, calls


# ============ A: Trial-04資産との同一性・較正 ============
@pytest.mark.parametrize("work", WORKS)
def test_A1_prompt_byte_identical_to_trial04_alpha(work):
    phrases = [x["kp"] for x in _trial_inputs()[work]]
    want = open(os.path.join(TRIAL, f"_prompt_04_{work}_p1a.txt"), encoding="utf-8").read()
    assert m.build_prompt(phrases).strip() == want.strip()


def test_A2_prompt_constants_equal_trial_builder():
    sys.path.insert(0, TRIAL)
    import run_trial_04 as t4
    assert m.PROMPT_HEAD == t4.P1_HEAD and m.PROMPT_BODY == t4.P1_BODY
    for w in WORKS:
        kps = [(x["kp"], x["gloss_in_text_ja"], x["sentence"]) for x in _trial_inputs()[w]]
        assert m.build_prompt([k for k, _, _ in kps]) == t4.p1_prompt(kps, "alpha")


@pytest.mark.parametrize("work", WORKS)
@pytest.mark.parametrize("run", ["r1", "r2"])
def test_A3_real_trial_outputs_parse_with_heading_normalization(work, run):
    """Opus必須1: 実出力6件(括弧付き見出し・曲がったアポストロフィを含む)が全件、retryなしでparseできる。"""
    phrases = [x["kp"] for x in _trial_inputs()[work]]
    text = open(os.path.join(TRIAL, f"_raw_04a_{run}_p1_{work}.txt"), encoding="utf-8").read()
    rows = m.parse_response(text, phrases)
    assert [r["phrase"] for r in rows] == phrases and all(len(r["explanation_ja"]) >= m.MIN_BODY_CHARS for r in rows)


def test_A4_min_body_threshold_calibrated_below_all_real_outputs():
    lens = []
    for w in WORKS:
        phrases = [x["kp"] for x in _trial_inputs()[w]]
        for run in ("r1", "r2"):
            rows = m.parse_response(open(os.path.join(TRIAL, f"_raw_04a_{run}_p1_{w}.txt"), encoding="utf-8").read(), phrases)
            lens += [len(r["explanation_ja"]) for r in rows]
    assert len(lens) == 18 and min(lens) > m.MIN_BODY_CHARS * 2   # 閾値は実最小値の半分未満(誤STOPしない余裕)


def test_A5_validate_phrases_accepts_every_real_fulltext_used_form():
    """Opus必須3: 既存の全keywords_canonicalized.json(fulltext_source_ref付き)のused_formが誤STOPしない。"""
    forms = set()
    for pat in ("er0*_output/**/keywords_canonicalized.json", "er1*_output/**/keywords_canonicalized.json"):
        for p in glob.glob(os.path.join(HERE, pat), recursive=True):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            for it in d.get("items", []) or []:
                if isinstance(it, dict) and it.get("fulltext_source_ref") and (it.get("used_form") or "").strip():
                    forms.add(it["used_form"])
    if not forms:
        pytest.skip("実データなし(clean checkout)")
    for f in sorted(forms):
        m.validate_phrases([f])


# ============ B: module単体 ============
def test_B1_build_prompt_takes_only_phrases():
    assert list(inspect.signature(m.build_prompt).parameters) == ["phrases"]
    gp = list(inspect.signature(m.generate_general_explanations).parameters)
    assert gp[0] == "phrases" and set(gp[1:]) <= {"call_fn", "client", "_items_for_isolation"}


def test_B3_wrapper_never_sends_gloss_source_sentence_or_meaning():
    call_fn, calls = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    items = _items()
    m.generate_for_kp_items(items, call_fn=call_fn)
    assert len(calls) == 1
    for it in items:
        for k in ("japanese_gloss", "source_sentence", "meaning_in_text_en"):
            assert it[k] not in calls[0], k
    assert "give way" in calls[0] and "gave way" not in calls[0]   # display_phrase(本文表層形)ではなくused_form


def test_B4_non_english_or_long_phrase_is_rejected_before_call():
    call_fn, calls = _call_recorder(lambda p, n: "")
    for bad in ("崩れる", "x" * 200, "a phrase\nwith newline", "他の語 give way", "", "a b c d e f g h i j k", "\x07bell"):
        with pytest.raises(ValueError):
            m.generate_general_explanations([bad], call_fn=call_fn)
    assert calls == []


def test_B5_signature_ignores_gloss_and_sentence_but_not_expression_order_prompt_or_model(monkeypatch):
    a = m.phrases_signature(_items())
    assert a == m.phrases_signature(_items(gloss="別の意味", sent="Completely different sentence."))
    assert a == m.phrases_signature(list(reversed(_items())))     # rank昇順に並べてから計算(入力順に依存しない)
    changed = _items()
    changed[0]["used_form"] = "give up"
    assert a != m.phrases_signature(changed)
    swapped = _items()
    swapped[0]["rank"], swapped[1]["rank"] = 2, 1                  # 順序(rank)が変われば別signature
    assert a != m.phrases_signature(swapped)
    monkeypatch.setattr(m, "PROMPT_TEMPLATE_SHA256", "0" * 64)
    assert a != m.phrases_signature(_items())
    monkeypatch.undo()
    assert a != m.phrases_signature(_items(), model="other-model")


def test_B6_resume_reuses_when_signature_same_and_regenerates_when_changed():
    call_fn, calls = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    first = m.resolve_general_explanations(_items(), None, call_fn=call_fn)
    assert len(calls) == 1 and first["reused_from_previous_run"] is False
    again = m.resolve_general_explanations(_items(gloss="Human Review後の別gloss"), first, call_fn=call_fn)
    assert len(calls) == 1 and again["reused_from_previous_run"] is True
    changed = _items()
    changed[1]["used_form"] = "on short notice"
    call_fn2, calls2 = _call_recorder(lambda p, n: _ok_response(["give way", "on short notice"]))
    redo = m.resolve_general_explanations(changed, again, call_fn=call_fn2)
    assert len(calls2) == 1 and redo["reused_from_previous_run"] is False


def test_B7_parse_failure_retries_once_then_fails_closed():
    call_fn, calls = _call_recorder(lambda p, n: "壊れた出力(見出しなし)")
    with pytest.raises(m.KpGeneralExplanationError):
        m.generate_general_explanations(["give way", "at a moment's notice"], call_fn=call_fn)
    assert len(calls) == 2


def test_B7b_retry_recovers_and_records_retried_flag():
    call_fn, calls = _call_recorder(lambda p, n: "壊れた" if n == 1 else _ok_response(["give way"]))
    r = m.generate_general_explanations(["give way"], call_fn=call_fn)
    assert len(calls) == 2 and r["audit"]["retried_for_parse"] is True


def test_B8_heading_mismatch_is_structure_failure():
    bad = "### 1. give way\n解説です。これは十分に長い日本語の説明文であるべきです。\n### 2. different phrase\n解説です。これも十分に長い日本語の説明文です。"
    call_fn, calls = _call_recorder(lambda p, n: bad)
    with pytest.raises(m.KpGeneralExplanationError):
        m.generate_general_explanations(["give way", "at a moment's notice"], call_fn=call_fn)


def test_B9_model_mismatch_stops_without_retry_or_fallback():
    call_fn, calls = _call_recorder(lambda p, n: _ok_response(["give way"]), model="some-other-model")
    with pytest.raises(m.KpGeneralExplanationError, match="応答モデルが不一致"):
        m.generate_general_explanations(["give way"], call_fn=call_fn)
    assert len(calls) == 1


def test_B10_audit_records_model_prompt_sha_input_sha_response_id():
    call_fn, _ = _call_recorder(lambda p, n: _ok_response(["give way"]))
    a = m.generate_general_explanations(["give way"], call_fn=call_fn)["audit"]
    for k in ("model", "prompt_sha256", "input_sha256", "response_ids", "calls", "process", "retried_for_parse", "reused_from_previous_run"):
        assert k in a, k
    assert a["model"] == "gpt-6-luna" and a["process"] == "KEY_PHRASE_GENERAL_EXPLANATION"
    assert a["prompt_sha256"] == hashlib.sha256(m.build_prompt(["give way"]).encode("utf-8")).hexdigest()


def test_B11_routing_process_registered_to_support_model():
    assert routing.PROCESS_MODEL_MAP[m.MODEL_ROUTING_PROCESS] == routing.SUPPORT_MODEL
    assert m.MODEL == routing.SUPPORT_MODEL == "gpt-6-luna"


def test_B12_page_forbidden_pattern_in_explanation_is_structure_failure():
    bad = "### 1. give way\nこれは英語: give way の説明であり十分に長い日本語の文章を含んでいます。"
    call_fn, calls = _call_recorder(lambda p, n: bad)
    with pytest.raises(m.KpGeneralExplanationError):
        m.generate_general_explanations(["give way"], call_fn=call_fn)
    assert len(calls) == 2


def test_B13_module_does_not_import_trial_assets():
    src = open(os.path.join(HERE, "er003_kp_general_explanation_01.py"), encoding="utf-8").read()
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    assert "run_trial_" not in code and "import docs" not in code
    assert not re.search(r"^\s*(import|from)\s+.*research", code, re.M)


# ============ M: Opus M4 / 必須2 ============
def test_M4_no_display_phrase_fallback():
    for bad in ({"rank": 1, "display_phrase": "gave way", "used_form": "give way"},                      # fulltext_source_refなし
                {"rank": 1, "display_phrase": "gave way", "used_form": "", "fulltext_source_ref": "x"},
                {"rank": 1, "display_phrase": "gave way", "fulltext_source_ref": "x"}):
        with pytest.raises(m.KpGeneralExplanationInputError):
            m.strict_phrase(bad)
        with pytest.raises(m.KpGeneralExplanationInputError):
            m.phrases_signature([bad])
        call_fn, calls = _call_recorder(lambda p, n: "")
        with pytest.raises(m.KpGeneralExplanationInputError):
            m.generate_for_kp_items([bad], call_fn=call_fn)
        assert calls == []                                                                               # 課金前にSTOP


def test_M4b_static_no_explanation_phrase_import_in_module():
    src = open(os.path.join(HERE, "er003_kp_general_explanation_01.py"), encoding="utf-8").read()
    code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
    assert "explanation_phrase(" not in code.replace("def strict_phrase", "")
    # item dictの文脈フィールドを読む記述が無い(isolation用の汎用収集と組立assemble_part1を除く)
    gen = inspect.getsource(m.generate_for_kp_items)
    assert not re.search(r"""(\[|\.get\()\s*["'](japanese_gloss|source_sentence|meaning_in_text_en|display_phrase|naive_ja)""", gen)


def test_M2_isolation_check_variable_part_only():
    phrases = ["give way", "at a moment's notice"]
    p = m.build_prompt(phrases)
    m.check_prompt_isolation(p, phrases, _items())                        # 固定HEAD/BODYの日本語で誤STOPしない
    with pytest.raises(m.KpIsolationViolation):
        m.check_prompt_isolation(p + "x", phrases, _items())              # 決定論再構成と不一致
    # gloss(短い日本語)がHEAD/BODYに偶然一致しても可変部の検査では誤STOPしない
    it = _items()
    it[0]["japanese_gloss"] = "意味"
    m.check_prompt_isolation(p, phrases, it)
    # 入れ子の文字列値が可変部に現れる場合はSTOP(表現そのものの部分文字列は除外)
    nested = _items()
    nested[0]["gloss_alignment"] = {"detail": ["give way\nat a moment's notice"]}
    with pytest.raises(m.KpIsolationViolation):
        m.check_prompt_isolation(p, phrases, nested)
    ok_nested = _items()
    ok_nested[0]["gloss_alignment"] = {"detail": ["give way"]}
    m.check_prompt_isolation(p, phrases, ok_nested)


def test_M2b_require_fresh_missing_and_stale_give_next_command():
    items = _items()
    call_fn, _ = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    doc = m.generate_for_kp_items(items, call_fn=call_fn)
    m.require_fresh_general_explanations(items, doc, next_command="X")
    with pytest.raises(m.KpGeneralExplanationStale, match="次の一手: CMD1"):
        m.require_fresh_general_explanations(items, None, next_command="CMD1")
    changed = _items()
    changed[0]["used_form"] = "give up"
    with pytest.raises(m.KpGeneralExplanationStale, match="次の一手: CMD2"):
        m.require_fresh_general_explanations(changed, doc, next_command="CMD2")
    stale_old = dict(doc)
    stale_old["phrases_signature"] = "0" * 64
    with pytest.raises(m.KpGeneralExplanationStale):
        m.require_fresh_general_explanations(items, stale_old, next_command="CMD3")
    legacy = [dict(items[0]), dict(items[1])]
    del legacy[0]["fulltext_source_ref"]                                   # 旧KP(Part 1導入前の入力)はSTOP
    with pytest.raises(m.KpGeneralExplanationStale):
        m.require_fresh_general_explanations(legacy, doc, next_command="CMD4")


# ============ C: 組立 ============
def _doc():
    call_fn, _ = _call_recorder(lambda p, n: _ok_response(["give way", "at a moment's notice"]))
    return m.generate_for_kp_items(_items(), call_fn=call_fn)


def test_C1_assemble_five_fields_in_user_order_verbatim_quote_translation_pending():
    out = m.assemble_part1(_items(), _doc(), None, ARTICLE)
    first = out[0]
    assert list(first)[:5] == ["english_expression", "meaning_in_text_ja", "source_sentence", "source_sentence_ja", "explanation_ja"]
    assert first["english_expression"] == "give way"                       # 見出し=入力used_form(LLM見出しではない)
    assert first["source_sentence"] in ARTICLE
    assert first["source_sentence_ja"] is None and first["translation_status"] == m.TRANSLATION_PENDING


def test_C1b_assemble_with_translation_marks_provided():
    out = m.assemble_part1(_items(), _doc(), {1: "彼らは沼地を渡ろうとしたが、足元の地面が崩れた。"}, ARTICLE)
    assert out[0]["translation_status"] == "PROVIDED" and out[1]["translation_status"] == m.TRANSLATION_PENDING


def test_C2_assemble_refuses_unresolved_gloss_non_verbatim_quote_and_stale_doc():
    hr = _items()
    import er003_key_words_gloss_alignment as ga
    hr[0]["gloss_alignment_status"] = ga.STATUS_HR_REQUIRED
    with pytest.raises(m.KpGeneralExplanationError, match="HUMAN_REVIEW"):
        m.assemble_part1(hr, _doc(), None, ARTICLE)
    with pytest.raises(m.KpGeneralExplanationError, match="QUOTE_NOT_IN_ARTICLE"):
        m.assemble_part1(_items(), _doc(), None, "unrelated text")
    empty = _items()
    empty[0]["japanese_gloss"] = ""
    with pytest.raises(m.KpGeneralExplanationError, match="GLOSS_(EMPTY|UNEVALUATED)"):
        m.assemble_part1(empty, _doc(), None, ARTICLE)
    changed = _items()
    changed[0]["used_form"] = "give up"
    with pytest.raises(m.KpGeneralExplanationStale):
        m.assemble_part1(changed, _doc(), None, ARTICLE)


def test_C3_quote_check_uses_existing_kp_normalization():
    import er003_key_words_min_unit as p2g
    it = _items()
    it[1]["source_sentence"] = "Inventing convincing stories at a moment’s notice was Vera’s speciality."   # 曲がった引用符
    m.assemble_part1(it, _doc(), None, ARTICLE)                            # 既存_normalize_for_match基準で一致
    assert m._norm_match("A ’x’  B") == p2g._normalize_for_match("A ’x’  B")


def test_C4_write_study_text_json_and_md_state_pending():
    import tempfile
    rows = m.assemble_part1(_items(), _doc(), None, ARTICLE)
    with tempfile.TemporaryDirectory() as td:
        paths = m.write_study_text(td, rows)
        j = json.load(open(paths["json"], encoding="utf-8"))
        assert all(r["source_sentence_ja"] is None and r["translation_status"] == "PENDING_USER_DECISION" for r in j["rows"])
        assert "PENDING_USER_DECISION" in open(paths["md"], encoding="utf-8").read()


# ============ R: 描画停止(M3 (ii)) / DefaultOffIsolation相当 ============
def _rows():
    return m.assemble_part1(_items(), _doc(), None, ARTICLE)


def test_R1_no_decision_record_means_no_render(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "TRANSLATION_DECISION_RECORD", str(tmp_path / "none.json"))
    assert m.translation_decision_record() is None and not m.study_text_render_enabled()
    assert m.render_html_block(_rows()) == ""


def test_R2_env_or_flags_cannot_enable_render(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "TRANSLATION_DECISION_RECORD", str(tmp_path / "none.json"))
    for k in ("STUDY_TEXT_RENDER_ENABLED", "PART1_RENDER", "STUDY_TEXT_RENDER", "KP_PART1_RENDER_ENABLED"):
        monkeypatch.setenv(k, "1")
    assert m.render_html_block(_rows()) == ""
    sig = inspect.signature(m.render_html_block)
    assert list(sig.parameters) == ["rows"]                                # 関数引数でflagを渡せない
    assert not inspect.signature(m.translation_decision_record).parameters


def test_R3_invalid_record_does_not_enable(monkeypatch, tmp_path):
    p = tmp_path / "d.json"
    monkeypatch.setattr(m, "TRANSLATION_DECISION_RECORD", str(p))
    for body in ('{"decision": "T3", "source": "x"}', '{"decision": "T2"}', "not json", '[]'):
        p.write_text(body, encoding="utf-8")
        assert m.render_html_block(_rows()) == ""


def test_R4_t2_renders_without_translation_row_and_standard_structure(monkeypatch, tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"decision": "T2", "source": "docs/pm/delegation_log/x.md"}), encoding="utf-8")
    monkeypatch.setattr(m, "TRANSLATION_DECISION_RECORD", str(p))
    rows = _rows()
    rows[0]["explanation_ja"] = "**核**の意味は<script>alert(1)</script>です。*give way* の例です。\n\n二段落目です。"
    h = m.render_html_block(rows)
    assert "<section class='study'>" in h and "<h3>Vocabulary &amp; Expressions</h3>" in h
    assert "<table" not in h and "<h2" not in h and "日本語訳" not in h
    assert "<script>" not in h and "&lt;script&gt;" in h and "<b>核</b>" in h and "<i>give way</i>" in h and h.count("<p>") >= 2
    assert not m.PAGE_FORBIDDEN_RE.search(re.sub(r"<[^>]+>", " ", h))     # ページlint禁止パターン非該当


def test_R5_t1_requires_translations_fail_closed(monkeypatch, tmp_path):
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"decision": "T1", "source": "x"}), encoding="utf-8")
    monkeypatch.setattr(m, "TRANSLATION_DECISION_RECORD", str(p))
    with pytest.raises(m.KpGeneralExplanationError, match="TRANSLATION_REQUIRED_BY_T1"):
        m.render_html_block(_rows())
    rows = m.assemble_part1(_items(), _doc(), {1: "訳1。", 2: "訳2。"}, ARTICLE)
    assert "日本語訳" in m.render_html_block(rows)


def test_R6_committed_repo_has_no_decision_record_yet():
    """UDR #197(T1/T2)の判断が出るまで、リポジトリに判断記録が無い=本番ページは描画しない状態であること。"""
    default = os.path.join(HERE, "docs", "pm", "decisions", "part1_translation_decision.json")
    assert os.path.normpath(m.TRANSLATION_DECISION_RECORD) == os.path.normpath(default)
    if os.path.exists(default):   # 判断が出て記録が置かれた後は、記録が有効形式(decision=T1/T2+source)であることだけを確認する
        assert m.translation_decision_record() is not None
    else:
        assert not m.study_text_render_enabled()
