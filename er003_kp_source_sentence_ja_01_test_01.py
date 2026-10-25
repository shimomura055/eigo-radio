# er003_kp_source_sentence_ja_01_test_01.py
# FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_16: 学習テキスト Part 1 T1(引用英文の日本語訳)工程のtest(API 0。LLMはmock call_fn)。
# 実行: .venv/Scripts/python.exe -m pytest er003_kp_source_sentence_ja_01_test_01.py -q
#  A: Prompt固定(sha)・入力隔離  B: 構造検査  C: 生成/retry/fail-closed/model契約  D: signature/resume/最新性
#  E: 解説工程との独立  F: X公開ページ共通builder  G: 判断記録・routing
import json
import os
import re
import shutil
import sys
import tempfile
from unittest import mock

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import er003_kp_general_explanation_01 as p1
import er003_kp_source_sentence_ja_01 as m
import er006_model_routing_contract_01 as routing

PROMPT_SHA = "98b1871caf77ade45cb7a1ab8d96abbbdbdef7c63b0252f29b0ee127d3d17999"
Q1 = "They tried to cross a bog, but the ground gave way beneath them."
Q2 = "Inventing convincing stories at a moment's notice was Vera's speciality."
ARTICLE = f"{Q1} Something else happened. {Q2}"


def items(g1="崩れる", g2="急なことにも即座に"):
    return [
        {"rank": 2, "display_phrase": "at a moment's notice", "used_form": "at a moment's notice", "fulltext_source_ref": "fulltext_exact_v1",
         "japanese_gloss": g2, "source_sentence": Q2, "meaning_in_text_en": "Without much warning.", "explanation_ja": "解説(混入チェック用)です。"},
        {"rank": 1, "display_phrase": "gave way", "used_form": "give way", "fulltext_source_ref": "fulltext_exact_v1",
         "japanese_gloss": g1, "source_sentence": Q1, "meaning_in_text_en": "To collapse."},
    ]


def ja_resp(n=2, ids=None, jas=None):
    ids = ids or list(range(1, n + 1))
    jas = jas or [f"これは{i}番の英文の自然な日本語訳です。" for i in ids]
    return json.dumps({"translations": [{"id": i, "ja": j} for i, j in zip(ids, jas)]}, ensure_ascii=False)


def recorder(responder, model="gpt-6-luna"):
    calls = []

    def fn(prompt):
        calls.append(prompt)
        return responder(prompt, len(calls)), model, {"input_tokens": 80, "cached_input_tokens": 0, "output_tokens": 40}, f"resp_{len(calls)}"
    fn.calls = calls
    return fn


# ---------------- A: Prompt固定・入力隔離 ----------------
def test_prompt_template_sha_is_pinned():
    assert m.PROMPT_TEMPLATE_SHA256 == PROMPT_SHA


def test_prompt_contains_only_quotes_in_variable_part():
    s = [Q1, Q2]
    p = m.build_prompt(s)
    assert m._variable_part(p) == s
    assert p.startswith(m.PROMPT_HEAD) and p.endswith("\n" + m.PROMPT_BODY)
    # 入力引数は引用英文のlistだけ(gloss・解説・本文を受け取る口がない)
    import inspect
    assert list(inspect.signature(m.build_prompt).parameters) == ["sentences"]


def test_wrapper_never_sends_gloss_explanation_or_phrase_context():
    fn = recorder(lambda p, n: ja_resp(2))
    m.generate_for_kp_items(items(), call_fn=fn)
    sent = fn.calls[0]
    for forbidden in ("崩れる", "急なことにも即座に", "解説(混入チェック用)", "To collapse.", "fulltext_exact_v1"):
        assert forbidden not in sent
    assert Q1 in sent and Q2 in sent
    assert sent.index(Q1) < sent.index(Q2)   # rank昇順(items順に依存しない)


def test_isolation_check_rejects_tampered_prompt_and_leaked_values():
    s = [Q1, Q2]
    with pytest.raises(m.KpSourceSentenceJaIsolationViolation):
        m.check_prompt_isolation(m.build_prompt(s) + "余計な文脈", s)
    with pytest.raises(m.KpSourceSentenceJaIsolationViolation):
        m.check_prompt_isolation(m.build_prompt([Q1]), [Q1, Q2])
    # item内の別文字列(gloss等)が引用英文として混入していれば検出
    leak = [{"rank": 1, "source_sentence": Q1, "meaning_in_text_en": "Without much warning at all"}]
    with pytest.raises(m.KpSourceSentenceJaIsolationViolation):
        m.check_prompt_isolation(m.build_prompt([Q1, "Without much warning at all"]), [Q1, "Without much warning at all"], leak)
    ok = [{"rank": 1, "source_sentence": Q1, "used_form": "give way", "japanese_gloss": "崩れる"}]
    m.check_prompt_isolation(m.build_prompt([Q1]), [Q1], ok)   # 表現(引用英文の部分文字列)・glossは正常


@pytest.mark.parametrize("bad", ["", "   ", "日本語を含む文です。", "line1\nline2", "x" * 401])
def test_validate_sentences_rejects(bad):
    with pytest.raises(ValueError):
        m.validate_sentences([bad])


def test_validate_sentences_limits_count():
    with pytest.raises(ValueError):
        m.validate_sentences([Q1] * (m.MAX_SENTENCES + 1))
    with pytest.raises(ValueError):
        m.validate_sentences([])


def test_source_sentence_required():
    it = items()
    it[0]["source_sentence"] = ""
    with pytest.raises(m.KpSourceSentenceJaInputError):
        m.strict_sentences(it)
    with pytest.raises(m.KpSourceSentenceJaInputError):
        m.strict_sentences([])


def test_trial_quotes_all_pass_validation():
    d = json.load(open(os.path.join(HERE, "docs", "research", "FAMILY-Z-STUDY-TEXT-TRIAL-01", "INPUT_04.json"), encoding="utf-8"))
    for w in d.values():
        m.validate_sentences([x["sentence"] for x in w])


def test_quote_must_exist_in_article_before_any_call():
    it = items()
    it[0]["source_sentence"] = "This sentence is not in the article at all."
    fn = recorder(lambda p, n: ja_resp(2))
    with pytest.raises(m.KpSourceSentenceJaInputError, match="QUOTE_NOT_IN_ARTICLE"):
        m.generate_for_kp_items(it, call_fn=fn, article_text=ARTICLE)
    assert fn.calls == []   # 課金前にSTOP
    m.generate_for_kp_items(items(), call_fn=fn, article_text=ARTICLE)
    assert len(fn.calls) == 1


# ---------------- B: 構造検査 ----------------
def test_parse_ok_and_fenced_json():
    s = [Q1, Q2]
    rows = m.parse_response(ja_resp(2), s)
    assert [r["rank_index"] for r in rows] == [1, 2] and rows[0]["source_sentence"] == Q1
    assert len(m.parse_response("```json\n" + ja_resp(2) + "\n```", s)) == 2


@pytest.mark.parametrize("text", [
    "", "not json", "[]", '{"translations": "x"}',
    ja_resp(1),                                                    # 件数不足
    ja_resp(2, ids=[2, 1]),                                        # id順不一致
    ja_resp(2, ids=[1, 3]),                                        # idずれ
    ja_resp(2, jas=["", "これは自然な日本語訳です。"]),                  # 空訳
    ja_resp(2, jas=["They tried to cross a bog", "これは自然な日本語訳です。"]),   # 英語のまま
    ja_resp(2, jas=["Ig Nobel Prize research", "これは自然な日本語訳です。"]),    # 英字優位(日本語なし)
    ja_resp(2, jas=["漢字漢字漢字漢字漢字", "これは自然な日本語訳です。"]),         # かな無し(中国語等)
    ja_resp(2, jas=["短い", "これは自然な日本語訳です。"]),                   # 短すぎる
    ja_resp(2, jas=["これは日本語:の訳です。", "これは自然な日本語訳です。"]),     # ページ禁止パターン
    ja_resp(2, jas=["行1\n行2の日本語訳です。", "これは自然な日本語訳です。"]),   # 改行
])
def test_parse_rejects(text):
    with pytest.raises(ValueError):
        m.parse_response(text, [Q1, Q2])


def test_proper_nouns_in_translation_are_allowed():
    rows = m.parse_response(json.dumps({"translations": [{"id": 1, "ja": "イグ・ノーベル賞(Ig Nobel Prize)は以前の研究に贈られました。"}]}, ensure_ascii=False),
                            ["The Ig Nobel Prize went to earlier research."])
    assert rows[0]["source_sentence_ja"].startswith("イグ")


# ---------------- C: 生成・retry・fail-closed・model契約 ----------------
def test_success_one_call_with_audit():
    fn = recorder(lambda p, n: ja_resp(2))
    r = m.generate_for_kp_items(items(), call_fn=fn)
    assert len(fn.calls) == 1
    a = r["audit"]
    assert a["model"] == "gpt-6-luna" and a["process"] == "KEY_PHRASE_SOURCE_SENTENCE_JA" and a["retried_for_parse"] is False
    assert a["prompt_template_sha256"] == PROMPT_SHA and a["response_ids"] == ["resp_1"] and a["input_sha256"]
    assert r["ranks"] == [1, 2] and r["sentences"] == [Q1, Q2]
    assert m.translations_by_rank(r) == {1: r["items"][0]["source_sentence_ja"], 2: r["items"][1]["source_sentence_ja"]}


def test_technical_retry_once_then_ok():
    fn = recorder(lambda p, n: "壊れた" if n == 1 else ja_resp(2))
    r = m.generate_for_kp_items(items(), call_fn=fn)
    assert len(fn.calls) == 2 and r["audit"]["retried_for_parse"] is True
    assert r["audit"]["calls"][0]["structure_error"]


def test_two_failures_fail_closed_with_no_third_call():
    fn = recorder(lambda p, n: "壊れた")
    with pytest.raises(m.KpSourceSentenceJaError, match="2回"):
        m.generate_for_kp_items(items(), call_fn=fn)
    assert len(fn.calls) == 2


def test_model_mismatch_stops_without_retry_or_fallback():
    fn = recorder(lambda p, n: ja_resp(2), model="gpt-other")
    with pytest.raises(m.KpSourceSentenceJaError, match="応答モデルが不一致"):
        m.generate_for_kp_items(items(), call_fn=fn)
    assert len(fn.calls) == 1


def test_default_client_path_uses_responses_create():
    class R:
        def create(self, **kw):
            from types import SimpleNamespace
            return SimpleNamespace(output_text=ja_resp(2), model="gpt-6-luna", id="r1", usage=SimpleNamespace(
                input_tokens=10, output_tokens=5, input_tokens_details=SimpleNamespace(cached_tokens=0), output_tokens_details=SimpleNamespace(reasoning_tokens=0)))
    c = type("C", (), {"responses": R()})()
    assert m.generate_for_kp_items(items(), client=c)["audit"]["response_ids"] == ["r1"]


# ---------------- D: signature / resume / 最新性 ----------------
def test_signature_depends_on_quotes_prompt_model_not_on_gloss_or_phrase():
    base = m.translations_signature(items())
    assert m.translations_signature(items(g1="全然違う意味", g2="別の意味")) == base          # gloss変更では再生成しない
    it = items(); it[1]["used_form"] = "give up"; it[1]["display_phrase"] = "gave up"
    assert m.translations_signature(it) == base                                              # KP表現変更でも再生成しない
    it = items(); it[1]["source_sentence"] = Q1 + " Again."
    assert m.translations_signature(it) != base                                              # 引用英文変更は再生成
    assert m.translations_signature(items(), model="gpt-x") != base
    with mock.patch.object(m, "PROMPT_TEMPLATE_SHA256", "0" * 64):
        assert m.translations_signature(items()) != base
    assert m.translations_signature(list(reversed(items()))) == base                         # rank昇順に正規化


def test_resume_reuses_without_call_and_regenerates_on_quote_change():
    fn = recorder(lambda p, n: ja_resp(2))
    doc = m.resolve_translations(items(), None, call_fn=fn)
    assert len(fn.calls) == 1 and doc["reused_from_previous_run"] is False
    again = m.resolve_translations(items(g1="別gloss"), doc, call_fn=fn)
    assert len(fn.calls) == 1 and again["reused_from_previous_run"] is True
    it = items(); it[0]["source_sentence"] = Q2 + " Indeed."
    m.resolve_translations(it, doc, call_fn=fn)
    assert len(fn.calls) == 2


def test_require_fresh_missing_stale_count():
    doc = m.generate_for_kp_items(items(), call_fn=recorder(lambda p, n: ja_resp(2)))
    m.require_fresh_translations(items(), doc, next_command="X")
    with pytest.raises(m.KpSourceSentenceJaStale, match="MISSING.*次の一手: NEXT"):
        m.require_fresh_translations(items(), None, next_command="NEXT")
    bad = dict(doc, translations_signature="0" * 64)
    with pytest.raises(m.KpSourceSentenceJaStale, match="STALE"):
        m.require_fresh_translations(items(), bad, next_command="NEXT")
    short = dict(doc, items=doc["items"][:1])
    with pytest.raises(m.KpSourceSentenceJaStale, match="COUNT_MISMATCH"):
        m.require_fresh_translations(items(), short, next_command="NEXT")


# ---------------- E: 解説工程との独立 ----------------
def test_independent_from_explanation_module():
    src_ja = open(os.path.join(HERE, "er003_kp_source_sentence_ja_01.py"), encoding="utf-8").read()
    src_ex = open(os.path.join(HERE, "er003_kp_general_explanation_01.py"), encoding="utf-8").read()
    assert "import er003_kp_general_explanation_01" not in src_ja
    assert "docs/research" not in src_ja.replace("# このmoduleはdocs/researchのTrial資産をimportしない。", "")
    assert not re.search(r"^import er003_kp_source_sentence_ja_01", src_ex, re.M)     # 解説moduleは訳moduleをtop-levelでimportしない
    assert m.MODEL_ROUTING_PROCESS != p1.MODEL_ROUTING_PROCESS
    assert m.TRANSLATIONS_FILENAME != p1.EXPLANATIONS_FILENAME
    # 解説Promptに引用英文は入らない(既存方針の維持)
    assert Q1 not in p1.build_prompt(["give way", "at a moment's notice"])


def test_explanation_prompt_sha_unchanged_by_t1():
    assert p1.PROMPT_TEMPLATE_SHA256 == "4d7ae557190650650592ae5e6df09e1946d87c582e32187bb8dfd6d32cfaf694"   # 解説Prompt不変(Trial-04 byte一致)
    sig = p1.phrases_signature(items())
    assert sig == p1.phrases_signature(items(g1="gloss変更"))   # 解説signatureも引用英文・gloss非依存(既存仕様)


# ---------------- F: 組立(5項)と描画 ----------------
def _kp_full_items():
    it = items()
    for x in it:
        x["gloss_alignment_status"] = "ALIGN_PASS"
    return sorted(it, key=lambda x: x["rank"])


def _ex_doc(its):
    phrases = [x["used_form"] for x in its]
    text = "\n".join(f"### {i}. {p}\n{p} の一般的な解説です。核となる意味と主要な使い方を説明します。*{p}* のように使われます。" for i, p in enumerate(phrases, 1))
    return p1.generate_for_kp_items(its, call_fn=lambda prompt: (text, "gpt-6-luna", {"input_tokens": 1, "output_tokens": 1}, "e1"))


def test_assemble_five_items_with_translations_and_render_t1():
    its = _kp_full_items()
    ex = _ex_doc(its)
    tr = m.generate_for_kp_items(its, call_fn=recorder(lambda p, n: ja_resp(2)))
    rows = p1.assemble_part1(its, ex, m.translations_by_rank(tr), ARTICLE)
    assert all(r["translation_status"] == "PROVIDED" and r["source_sentence_ja"] for r in rows)
    html_ = p1.render_html_block(rows)
    order = [html_.index(x) for x in ("<h4>give way</h4>", "<dt>本文中の意味</dt>", "<dt>本文の英文</dt>", "<dt>日本語訳</dt>", "<dt>解説</dt>")]
    assert order == sorted(order)
    assert "<table" not in html_ and "<h2" not in html_
    assert not p1.PAGE_FORBIDDEN_RE.search(re.sub(r"<[^>]+>", " ", html_))


def test_render_t1_stops_when_translation_missing():
    its = _kp_full_items()
    ex = _ex_doc(its)
    rows = p1.assemble_part1(its, ex, None, ARTICLE)
    assert all(r["translation_status"] == p1.TRANSLATION_PENDING for r in rows)
    with pytest.raises(p1.KpGeneralExplanationError, match="TRANSLATION_REQUIRED_BY_T1"):
        p1.render_html_block(rows)


def test_decision_record_is_t1_and_points_to_user_original():
    rec = p1.translation_decision_record()
    assert rec and rec["decision"] == "T1"
    assert os.path.isfile(os.path.join(HERE, rec["source"]))
    assert "T1：専用の翻訳工程を追加する方式を正式承認します" in open(os.path.join(HERE, rec["source"]), encoding="utf-8").read()
    assert p1.study_text_render_enabled() is True


# ---------------- G: X公開ページ共通builder ----------------
def _x_audio_dir(tmp):
    its = _kp_full_items()
    kd = f"{tmp}/b1b/key_phrases"
    os.makedirs(kd)
    json.dump({"items": its}, open(f"{kd}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False)
    ex = _ex_doc(its)
    tr = m.generate_for_kp_items(its, call_fn=recorder(lambda p, n: ja_resp(2)))
    json.dump(ex, open(f"{kd}/{p1.EXPLANATIONS_FILENAME}", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(tr, open(f"{kd}/{m.TRANSLATIONS_FILENAME}", "w", encoding="utf-8"), ensure_ascii=False)
    rows = p1.assemble_part1(its, ex, m.translations_by_rank(tr), ARTICLE)
    p1.write_study_text(f"{tmp}/b1b/study_text", rows)
    return its


def test_x_page_builder_renders_study_block():
    with tempfile.TemporaryDirectory() as t:
        _x_audio_dir(t)
        h = p1.study_html_for_audio_dir(t)
        assert h.count("<div class='study-item'>") == 2 and "<dt>日本語訳</dt>" in h and h.count("<section class='study'>") == 1


def test_x_page_builder_empty_without_decision_record():
    with tempfile.TemporaryDirectory() as t:
        _x_audio_dir(t)
        with mock.patch.object(p1, "TRANSLATION_DECISION_RECORD", os.path.join(t, "nope.json")):
            assert p1.study_html_for_audio_dir(t) == ""


@pytest.mark.parametrize("mutate", ["drop_study", "drop_ja", "drop_ex", "stale_ja", "stale_ex", "edit_row", "gloss_changed"])
def test_x_page_builder_fail_closed(mutate):
    with tempfile.TemporaryDirectory() as t:
        _x_audio_dir(t)
        kd = f"{t}/b1b/key_phrases"
        if mutate == "drop_study":
            os.remove(f"{t}/b1b/study_text/{p1.PART1_FILE_STEM}.json")
        elif mutate == "drop_ja":
            os.remove(f"{kd}/{m.TRANSLATIONS_FILENAME}")
        elif mutate == "drop_ex":
            os.remove(f"{kd}/{p1.EXPLANATIONS_FILENAME}")
        elif mutate in ("stale_ja", "stale_ex"):
            fn, key = (m.TRANSLATIONS_FILENAME, "translations_signature") if mutate == "stale_ja" else (p1.EXPLANATIONS_FILENAME, "phrases_signature")
            d = json.load(open(f"{kd}/{fn}", encoding="utf-8"))
            d[key] = "0" * 64
            json.dump(d, open(f"{kd}/{fn}", "w", encoding="utf-8"))
        elif mutate == "edit_row":
            sp = f"{t}/b1b/study_text/{p1.PART1_FILE_STEM}.json"
            d = json.load(open(sp, encoding="utf-8"))
            d["rows"][0]["source_sentence_ja"] = "書き換えられた訳です。"
            json.dump(d, open(sp, "w", encoding="utf-8"), ensure_ascii=False)
        elif mutate == "gloss_changed":
            kp = json.load(open(f"{kd}/keywords_canonicalized.json", encoding="utf-8"))
            kp["items"][0]["japanese_gloss"] = "更新後の意味"
            json.dump(kp, open(f"{kd}/keywords_canonicalized.json", "w", encoding="utf-8"), ensure_ascii=False)
        with pytest.raises(p1.KpGeneralExplanationError):
            p1.study_html_for_audio_dir(t)


def test_x_page_script_calls_builder_once_and_changes_nothing_else():
    s = open(os.path.join(HERE, "er019_nws2_final_page_01.py"), encoding="utf-8").read()
    assert s.count("study_html_for_audio_dir(") == 1
    assert 'tail=study_html' in s


# ---------------- H: routing ----------------
def test_routing_key_is_support_model_and_registered():
    assert routing.PROCESS_MODEL_MAP["KEY_PHRASE_SOURCE_SENTENCE_JA"] == routing.SUPPORT_MODEL == "gpt-6-luna"
    assert routing.require_model("KEY_PHRASE_SOURCE_SENTENCE_JA", "gpt-6-luna") == "gpt-6-luna"
    with pytest.raises(Exception):
        routing.require_model("KEY_PHRASE_SOURCE_SENTENCE_JA", "gpt-other")
