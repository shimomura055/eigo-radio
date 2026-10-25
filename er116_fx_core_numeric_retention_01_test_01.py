# -*- coding: utf-8 -*-
"""er116 Production中核数値保持方式(v4+J2) のtest(API 0円。実LLMは呼ばない=FakeClient)。
FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07。Trial(er115)のmock test(Gate/STOP/E=∅/J2/resume)をProduction側へ移植し、
Trialの保存済みB3出力・Writer出力に対する決定論再適用(回帰)と、Isolation(Family Y/Zへ到達しない)・既定動作を検証する。"""
import ast
import glob
import hashlib
import json
import os
import re
import shutil
import types

import pytest

import er003_audio_tts_asr_safety as safety
import er019_family_x_entertainment_production_runner_01 as runner
import er019_family_x_storyline_b3_fact_selection_01 as b3
import er053_family_x_factlock_ja_writer_01 as w1
import er115_fx_numeric_retention_trial_01 as D        # Trial(DEV)。Production側のsource同一性・保存済み標本の再適用のためtest内だけで参照
import er116_fx_core_numeric_retention_01 as N

ROOT = os.path.dirname(os.path.abspath(__file__))
MOON = os.path.join(ROOT, "er019_output", "moon_shrinking", "run_ms_02")
TRIAL = os.path.join(ROOT, "er115_output", "fx_numeric_retention_trial_01")
FIELD_MOON = ["約42〜46 m"]


# ======================================================================================================
# Isolation / 撤去・残置(Grep相当)
# ======================================================================================================
def _py_files():
    return [p for p in glob.glob(os.path.join(ROOT, "*.py"))]


def test_isolation_only_family_x_runner_and_writer_reference_er116():
    hits = []
    for p in _py_files():
        base = os.path.basename(p)
        if base.startswith("er116_"):
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        if re.search(r"^[ \t]*(?:import|from)[ \t]+er116_fx_core_numeric_retention", txt, re.M):
            hits.append(base)
    assert hits == ["er019_family_x_entertainment_production_runner_01.py"], hits


def test_isolation_y_z_and_trial_do_not_reach_numeric_retention():
    """Family Y/Z・他Trialは er116 / numeric= / variant= / JANumericRetentionStopError に到達しない。"""
    bad = []
    for p in _py_files():
        base = os.path.basename(p)
        if base.startswith(("er110_", "er054_", "er036_", "er082_", "er083_", "er086_", "er090_")) or "family_z" in base:
            txt = open(p, encoding="utf-8", errors="replace").read()
            for needle in ("er116_", "numeric=", "numret", "JANumericRetentionStopError", "reader_must_hear_numbers"):
                if needle in txt:
                    bad.append((base, needle))
    assert bad == [], bad


def test_er116_does_not_import_er115_or_old_trial_artifacts():
    src = open(N.__file__, encoding="utf-8").read()
    tree = ast.parse(src)
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imported.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            imported.add(n.module)
    assert not any(m and m.startswith("er115") for m in imported)
    code_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for dead in ("B3_ADDENDUM", "B3_ADDENDUM_V1", "B3_ADDENDUM_V3", "B3_ADDENDUM_V3_FIELD", "RULE9_TEXT", "resume_w1_dev_from_r2", "run_w1_dev", "_AddendumClient",
                 "run_b3_dev", "derive_E_r5", "run_chain_dev", "field_priority_ddet"):
        assert dead not in code_names, dead
    # Storyline由来Eのsurfaces=None経路は移植しない
    assert "surfaces is None" not in src
    assert "os.environ" not in src          # 環境変数・flagでON/OFFする経路が無い


def test_storyline_b3_schema_constant_untouched_and_not_mutated():
    before = json.dumps(b3.STORYLINE_B3_JSON_SCHEMA, sort_keys=True)
    sha = hashlib.sha256(before.encode()).hexdigest()
    kw = {"format": {"type": "json_schema", **b3.STORYLINE_B3_JSON_SCHEMA}}
    out = N.with_field_schema(kw)
    assert json.dumps(b3.STORYLINE_B3_JSON_SCHEMA, sort_keys=True) == before
    assert hashlib.sha256(before.encode()).hexdigest() == sha
    assert N.B3_FIELD_NAME not in b3.STORYLINE_B3_JSON_SCHEMA["schema"]["properties"]
    assert N.B3_FIELD_NAME in out["format"]["schema"]["properties"] and N.B3_FIELD_NAME in out["format"]["schema"]["required"]
    assert out["format"]["schema"]["additionalProperties"] is False and out["format"]["strict"] if "strict" in out["format"] else True


def test_prompt_constants_unchanged():
    assert "\n5. 数字の規則: ニュース欄で【中核数値】と印の付いた数字だけを" in w1.FACTLOCK_R0_BLOCK_HEAD     # 規則5の文言は不変(運用はCURRENT_SPECに追記)
    assert hashlib.sha256(w1.jaw.R0_PROMPT.encode("utf-8")).hexdigest() == "6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366"


# ======================================================================================================
# Trial(検証済み)とのソース同一性: 移植した関数・定数がer115と1文字も違わない
# ======================================================================================================
VERBATIM_FUNCS = ["sha_text", "rdt", "rj", "wj", "wt", "unit_key", "currency_of", "own_unit_of", "req_unit", "_tokens_for", "trailing_has_unit",
                  "unit_hint_after", "match_core", "en_values", "en_present", "normalize_ranges", "normalize_ranges_counted", "is_time_premise",
                  "read_field_items", "T_is_ambiguous", "approx_forms_of", "check_retention", "display_form", "retention_note", "dimension_of",
                  "plan_o2prime", "swap_marks", "filter_overlay", "_num_tokens", "new_numbers", "with_field_schema"]
VERBATIM_CONSTS = ["B3_ADDENDUM_V2", "B3_ADDENDUM_V4_FIELD", "B3_ADDENDUM_V4", "B3_FIELD_NAME", "M1_RETRY_NOTE_V3_TEMPLATE", "RETENTION_NOTE_TEMPLATE",
                    "TIME_PREMISE_UNIT_RE", "MAX_E", "UNIT_GROUPS", "CURRENCY_SYMBOL", "WAVES", "EN_UNIT_RE", "DIM_OF_GROUP", "CORE_MARK", "PERIPH_MARK"]


def _funcs(path):
    src = open(path, encoding="utf-8").read()
    return {n.name: ast.get_source_segment(src, n) for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}


def test_ported_functions_are_source_identical_to_validated_trial():
    f115, f116 = _funcs(D.__file__), _funcs(N.__file__)
    diff = [n for n in VERBATIM_FUNCS if f115[n].replace("\r\n", "\n") != f116[n].replace("\r\n", "\n")]
    assert diff == []


def test_ported_constants_equal_validated_trial():
    for c in VERBATIM_CONSTS:
        a, b = getattr(D, c), getattr(N, c)
        if hasattr(a, "pattern"):
            a, b = a.pattern, b.pattern
        assert a == b, c
    assert N.B3_ADDENDUM_V4 == D.B3_ADDENDUM_V4 and N.B3_ADDENDUM_V4 == N.B3_ADDENDUM_V2 + N.B3_ADDENDUM_V4_FIELD
    assert N.sha_text(N.B3_ADDENDUM_V4) == D.sha_text(D.B3_ADDENDUM_V4)


# ======================================================================================================
# B3 variant: 検証済みバイト列で送り、variant=None は従来とバイト同一
# ======================================================================================================
def _capture_client(reply_story="月の半径は後期に約42〜46 m縮んだと推定される。", field=None):
    ev = json.load(open(os.path.join(MOON, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    sent = []

    class R:
        def create(self_inner, **kw):
            sent.append(kw)
            out = {"selected_storyline": reply_story, "fact_tests": ev["fact_tests"], "selected_fact_ids": ev["selected_fact_ids"],
                   "selected_fact_brief": ev["selected_fact_brief_text"], "recheck_note": ev["recheck_note"]}
            if field is not None:
                out[N.B3_FIELD_NAME] = field
            return types.SimpleNamespace(output_text=json.dumps(out, ensure_ascii=False), model=w1.routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"] + "-x",
                                         id="b3_%d" % len(sent), usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
    return types.SimpleNamespace(responses=R()), sent


def _ledger():
    return open(os.path.join(MOON, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()


def test_b3_variant_none_is_identical_to_current_production_request():
    c, sent = _capture_client()
    b3.run_storyline_b3_selection(c, "T", _ledger(), model=w1.routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"], effort="high")
    kw = sent[0]
    assert kw["text"] == {"format": {"type": "json_schema", **b3.STORYLINE_B3_JSON_SCHEMA}}
    assert kw["input"][-1]["content"] == b3.build_user_prompt("T", _ledger())


def test_b3_variant_v4_appends_addendum_and_extends_schema_copy_only():
    c, sent = _capture_client(field=FIELD_MOON)
    res = b3.run_storyline_b3_selection(c, "T", _ledger(), model=w1.routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"], effort="high", variant=N.variant())
    kw = sent[0]
    assert kw["input"][-1]["content"] == b3.build_user_prompt("T", _ledger()) + N.B3_ADDENDUM_V4
    assert N.B3_FIELD_NAME in kw["text"]["format"]["schema"]["properties"]
    assert N.B3_FIELD_NAME not in b3.STORYLINE_B3_JSON_SCHEMA["schema"]["properties"]
    assert res["parsed"][N.B3_FIELD_NAME] == FIELD_MOON


def test_b3_variant_m1_retry_note_matches_trial_bytes():
    probs = "約45(unmapped_to_news_field)"
    v = N.variant(retry_problems=probs)
    assert v["addendum"] == D.B3_ADDENDUM_V4 + D.M1_RETRY_NOTE_V3_TEMPLATE.format(problems=probs)


# ======================================================================================================
# W-1(Gate / 再生成枠 / STOP / E=∅ / J2 / O-2') FakeClient
# ======================================================================================================
def _make_dir(tmp_path, story="月の「しわ」から見積もった後期の縮みは、半径で約42〜46 mと推定される。", field=FIELD_MOON, name="moon"):
    d = tmp_path / name
    shutil.copytree(os.path.join(MOON, "research_ledger"), d / "research_ledger")
    (d / "storyline_b3").mkdir()
    ev = json.load(open(os.path.join(MOON, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    old_story = ev["selected_storyline"]
    ev = {k: v for k, v in ev.items() if k in ("selected_storyline", "full_ledger_fact_ids", "fact_tests", "selected_fact_ids",
                                              "selected_fact_brief_text", "recheck_note", "soft_warnings", "min2_policy")}
    ev["selected_storyline"] = story
    json.dump(ev, open(d / "storyline_b3" / "fact_selection_evidence.json", "w", encoding="utf-8"), ensure_ascii=False)
    brief = open(os.path.join(MOON, "storyline_b3", "selected_brief.md"), encoding="utf-8").read()
    (d / "storyline_b3" / "selected_brief.md").write_text(brief.replace(old_story, story), encoding="utf-8")
    (d / "storyline_b3" / "audit").mkdir()
    runner.run_annotation_producer(str(d))
    if field is not None:
        N.save_field(str(d / "storyline_b3"), {N.B3_FIELD_NAME: field}, "resp_b3_test")
    return str(d)


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.prompts = []
        outer = self

        class R:
            def create(self_inner, **kw):
                outer.prompts.append(kw["input"][-1]["content"])
                text = outer.script.pop(0)
                model = w1.R0_MODEL if "テーマ：" in kw["input"][-1]["content"] else w1.ASTRA_MODEL
                return types.SimpleNamespace(output_text=text, model=model + "-x", id="resp_%d" % len(outer.prompts),
                                             usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
        self.responses = R()


GOOD = "月のしわが語ること\n\n月の半径は、後期に約42から46メートル縮んだと推定されている。【事実3】\n"
NOPE = "月のしわが語ること\n\n月の半径は、後期にごくわずか縮んだと推定されている。【事実3】\n"
SYMB = "月のしわが語ること\n\n月の半径は、後期に約42〜46メートル縮んだと推定されている。【事実3】\n"
WAVE = "月のしわが語ること\n\n月の半径は、後期に約42〜46メートル縮んだと推定されている。\n"


def _run(d, fc):
    return w1.run_w1_writer(d, client=fc, numeric=N.NumericRetention.from_out_dir(d))


def test_ctx_from_field_gives_E_42_46(tmp_path):
    d = _make_dir(tmp_path)
    ctx = N.NumericRetention.from_out_dir(d)
    assert ctx.mode == "field_ok" and ctx.active
    assert [c["news_surface"] for c in ctx.gate_E] == ["約42〜46"] and ctx.gate_E[0]["unit_hint"] == "m"


def test_gate_all_ok_minimum_calls_and_r4_input_normalization(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 3
    assert "約42から46" in fc.prompts[0] and "約42〜46" not in fc.prompts[0].split("[ニュース]", 1)[1]
    nr = r["runtime_evidence"]["numeric_retention"]
    assert nr["mode"] == "field_ok" and nr["gate_E"] == ["約42〜46"] and nr["j2"]["r4_input_changed"]
    assert os.path.exists(os.path.join(d, "ja_writer", "numeric_retention.json"))
    assert r["runtime_evidence"]["r1"]["model"].startswith(w1.ASTRA_MODEL)     # actual model_id記録


def test_r0_retention_regen_once_with_note(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([NOPE, GOOD, GOOD, GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 4 and "次の数字が本文にありません: 約42から46 m" in fc.prompts[1]
    assert r["runtime_evidence"]["original"]["r0_calls"][1]["stage"] == "w1_r0_retention_regen"
    assert r["runtime_evidence"]["numeric_retention"]["retention"]["r0"]["regenerated"]


def test_r0_symbol_only_regen_uses_existing_symbol_regen_prompt(tmp_path):
    d = _make_dir(tmp_path)
    bad = SYMB.replace("縮んだ", "縮んだ…")      # 範囲値ではない禁止記号(…)でsymbol QAだけを起こす
    fc = FakeClient([bad.replace("42〜46", "42から46"), GOOD, GOOD, GOOD])
    r = _run(d, fc)
    assert r["runtime_evidence"]["original"]["r0_calls"][1]["stage"] == "w1_r0_symbol_regen"
    assert len(fc.prompts) == 4


def test_r0_regen_loses_E_is_stop_in_existing_stop_frame(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([NOPE, NOPE])
    with pytest.raises(w1.JANumericRetentionStopError) as ei:
        _run(d, fc)
    assert isinstance(ei.value, w1.JASymbolCheckStopError)        # 既存のSTOP枠(runnerの except w1.JASymbolCheckStopError に入る)
    assert ei.value.stage == "numeric_r0" and ei.value.findings
    for f in ("rejected_w1_r0_numeric_first.md", "rejected_w1_r0_numeric_rerun.md"):
        assert os.path.exists(os.path.join(d, "ja_writer", "audit", f))
    assert os.path.exists(os.path.join(d, "ja_writer", "runtime_evidence_stopped.json"))
    assert len(fc.prompts) == 2 and not os.path.exists(os.path.join(d, "ja_writer", "revision2.md"))


def test_stop_reaches_runner_stop_path_and_no_downstream(tmp_path, monkeypatch):
    """STOPの行き先=既存のJA記号QA STOPと同じ枠: runner.run_ja_writerがRuntimeError化し、EN/TTSへ進まない(run_ja_writerより後は呼ばれない)。"""
    d = _make_dir(tmp_path)
    fc = FakeClient([NOPE, NOPE])
    with pytest.raises(RuntimeError) as ei:
        runner.run_ja_writer(fc, d, 150.0)
    assert "JA_NUMERIC_RETENTION_STOP" in str(ei.value)
    assert not os.path.exists(os.path.join(d, "a2")) and not os.path.exists(os.path.join(d, "b1b"))


def test_r1_rerun_once_then_stop(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, NOPE, NOPE])
    with pytest.raises(w1.JANumericRetentionStopError) as ei:
        _run(d, fc)
    assert ei.value.stage == "numeric_r1" and len(fc.prompts) == 3


def test_r1_rerun_ok_uses_retention_rerun_tag(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, NOPE, GOOD, GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 4
    resp = json.load(open(os.path.join(d, "ja_writer", "factlock", "r1.response.json"), encoding="utf-8"))
    assert isinstance(resp, list) and len(resp) == 2
    assert r["runtime_evidence"]["numeric_retention"]["retention"]["r1"]["rerun"]


def test_r2_shares_single_rerun_slot(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, NOPE, GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 4
    assert r["runtime_evidence"]["symbol_qa"]["r2"]["rerun"] is True


def test_r2_rerun_still_missing_is_stop(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, NOPE, NOPE])
    with pytest.raises(w1.JANumericRetentionStopError) as ei:
        _run(d, fc)
    assert ei.value.stage == "numeric_r2" and len(fc.prompts) == 4


def test_r2_symbol_and_missing_share_single_rerun(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, NOPE.replace("縮んだ", "縮んだ…"), GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 4 and r["runtime_evidence"]["symbol_qa"]["r2"]["rerun"] is True


def test_m2_new_number_in_r2_uses_rerun_slot(tmp_path):
    d = _make_dir(tmp_path)
    mid = GOOD.replace("約42から46メートル", "約44メートル")     # 範囲値の中点(新規数値)はEの欠落でもある
    fc = FakeClient([GOOD, GOOD, mid, GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 4
    assert r["runtime_evidence"]["numeric_retention"]["new_numbers"]["r2"]["first"]


def test_m2_new_number_not_in_E_is_detected(tmp_path):
    d = _make_dir(tmp_path)
    extra = GOOD.replace("縮んだと推定されている。", "縮んだと推定されている。ほかに約77キログラムもある。")
    fc = FakeClient([GOOD, extra, GOOD, GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 4          # R1で新規数値→R1再実行枠(1回)


def test_gate_does_not_rewrite_text_only_range_normalization(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, GOOD])
    r = _run(d, fc)
    assert r["ja_text"].strip() == GOOD.replace("【事実3】", "").strip()


# ---- J2 ----
def test_j2_astra_output_range_wave_is_normalized_not_stop(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, WAVE, WAVE])
    r = _run(d, fc)
    assert len(fc.prompts) == 3 and "約42から46メートル" in r["ja_text"] and "〜" not in r["ja_text"]
    assert r["runtime_evidence"]["r1"]["range_wave_normalized"] == 1 and r["runtime_evidence"]["r1"]["raw_sha256_before_norm"]
    assert r["runtime_evidence"]["numeric_retention"]["j2"]["output_normalized"]["w1_astra_r2"] == 1


def test_j2_r0_output_range_wave_normalized_before_symbol_qa(tmp_path):
    d = _make_dir(tmp_path)
    fc = FakeClient([SYMB, GOOD, GOOD])
    r = _run(d, fc)
    assert len(fc.prompts) == 3                      # R0の〜はJ2で『から』になり、再生成枠を消費しない
    assert r["runtime_evidence"]["numeric_retention"]["j2"]["output_normalized"]["r0"] == 1


def test_j2_non_numeric_wave_still_flagged_by_symbol_qa(tmp_path):
    d = _make_dir(tmp_path)
    bad = "月のしわが語ること\n\n月の半径は約42から46メートル縮んだ。ローベート〜スカープ。\n"
    fc = FakeClient([GOOD, GOOD, bad, bad])
    with pytest.raises(w1.JASymbolCheckStopError) as ei:
        _run(d, fc)
    assert ei.value.stage == "r2_symbol"


def test_j2_text_is_not_touched_by_tts_normalizer_and_reads_kara():
    """J2後の本文には波ダッシュが無く、TTS用Normalizer(使い捨てコピーのみ)は何も変えない => 『42なになに46』は表に出ない。"""
    t = N.normalize_ranges("約42〜46メートル縮んだ")
    assert t == "約42から46メートル縮んだ" and safety.normalize_tilde_placeholder_ja(t) == t
    assert safety.normalize_tilde_placeholder_ja("約42〜46") == "約42なになに46"      # 旧欠陥(Normalizer単体の挙動は不変・残置)
    assert not safety.symbol_gate_requires_stop(safety.detect_prohibited_symbols(t, language="ja"))


def test_j2_does_not_touch_dates_hyphen_or_digits():
    assert N.normalize_ranges("10月27~28日") == "10月27~28日" and N.normalize_ranges("25-35度") == "25-35度"
    assert N.normalize_ranges("約3〜4億年前") == "約3から4億年前"
    assert re.sub(r"\D", "", N.normalize_ranges("約42〜46 m")) == "4246"            # 数字・桁は不変


# ---- E=∅ の既定経路 ----
def test_legacy_no_field_is_E_empty_no_gate_no_o2prime(tmp_path):
    d = _make_dir(tmp_path, field=None)
    ctx = N.NumericRetention.from_out_dir(d)
    assert ctx.mode == "legacy_no_field" and not ctx.active
    fc = FakeClient([NOPE, NOPE, NOPE])
    r = _run(d, fc)                                        # Gateなし: 数値が無くてもSTOP/再生成しない
    assert len(fc.prompts) == 3 and r["runtime_evidence"]["numeric_retention"]["o2prime"] is None


def test_field_empty_is_E_empty(tmp_path):
    d = _make_dir(tmp_path, field=[])
    ctx = N.NumericRetention.from_out_dir(d)
    assert ctx.mode == "field_empty" and not ctx.active
    r = _run(d, FakeClient([NOPE, NOPE, NOPE]))
    assert r["runtime_evidence"]["numeric_retention"]["gate_E"] == []


def test_m1_final_violation_continues_with_E_empty_and_warn(tmp_path, capsys):
    d = _make_dir(tmp_path, field=["約45 m"])             # ニュース欄に無い数値=unmapped_to_news_field
    ctx = N.NumericRetention.from_out_dir(d)
    assert ctx.mode == "m1_final_violation_E_empty" and not ctx.active
    assert "[WARN][numeric_retention]" in capsys.readouterr().out
    r = _run(d, FakeClient([NOPE, NOPE, NOPE]))
    ev = r["runtime_evidence"]["numeric_retention"]
    assert ev["warn"] and ev["m1_violations"] and ev["E"] == [] and len(r["runtime_evidence"]["original"]["r0_calls"]) == 1


def test_numeric_none_writer_is_unchanged_prompt(tmp_path):
    """numeric=None(Trial/Y/Z)は従来どおり: R0 promptは build_r0_prompt(storyline, news_text) そのもの(波ダッシュも入力のまま)。"""
    d = _make_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, GOOD])
    w1.run_w1_writer(d, client=fc)
    annotated = w1.contract.validate_annotated_b3(d) if hasattr(w1, "contract") else None
    assert "約42〜46" in fc.prompts[0].split("[ニュース]", 1)[1]
    ev = json.load(open(os.path.join(d, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))
    assert ev["numeric_retention"] is None


def test_o2prime_applied_only_when_active_and_files_unchanged(tmp_path):
    d = _make_dir(tmp_path)
    before = hashlib.sha256(open(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"), "rb").read()).hexdigest()
    ctx = N.NumericRetention.from_out_dir(d)
    fc = FakeClient([GOOD, GOOD, GOOD])
    r = w1.run_w1_writer(d, client=fc, numeric=ctx)
    after = hashlib.sha256(open(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"), "rb").read()).hexdigest()
    assert before == after                                  # 注記済みB3ファイル(契約sha)は不変
    o2 = r["runtime_evidence"]["numeric_retention"]["o2prime"]
    assert o2 and o2["applied"] and "length" in o2["e_dimensions"]
    prompt_news = fc.prompts[0].split("[ニュース]", 1)[1]
    for x in o2["demote"]:                                  # 付け替えた数値はWriter入力で【周辺数値】
        assert x["surface"] + "【中核数値】" not in prompt_news.replace("から", "〜")


# ---- resume / 再生成: 保存済みの欄からEを決定論で再構成(B3を呼ばない) ----
def test_resume_reconstructs_E_without_b3_call(tmp_path):
    d = _make_dir(tmp_path)
    a = N.NumericRetention.from_out_dir(d)
    b = N.NumericRetention.from_out_dir(d)
    assert a.ev["gate_E"] == b.ev["gate_E"] == ["約42〜46"]
    fc = FakeClient([GOOD, GOOD, GOOD])
    _run(d, fc)
    assert all("テーマ：" in p or "以下の記事" in p for p in fc.prompts)     # W-1のみ(B3 prompt無し)


# ======================================================================================================
# runner: M1 / B3再実行1回 / E=∅続行
# ======================================================================================================
def _b3_dir(tmp_path, name):
    d = tmp_path / name
    shutil.copytree(os.path.join(MOON, "research_ledger"), d / "research_ledger")
    return str(d)


def _b3_client(stories_fields):
    ev = json.load(open(os.path.join(MOON, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    queue, sent = list(stories_fields), []

    class R:
        def create(self_inner, **kw):
            sent.append(kw)
            story, field = queue.pop(0)
            out = {"selected_storyline": story, "fact_tests": ev["fact_tests"], "selected_fact_ids": ev["selected_fact_ids"],
                   "selected_fact_brief": ev["selected_fact_brief_text"], "recheck_note": ev["recheck_note"], N.B3_FIELD_NAME: field}
            return types.SimpleNamespace(output_text=json.dumps(out, ensure_ascii=False), model=w1.routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"] + "-x",
                                         id="b3_%d" % len(sent), usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
    return types.SimpleNamespace(responses=R()), sent


def _first_b3(client, d):
    ledger = _ledger()
    runner.run_storyline_b3(client, "T", ledger, d, numeric_variant=N.variant())
    runner.assert_b3_min_verified(d)
    runner.run_annotation_producer(d)
    return ledger


@pytest.fixture(autouse=False)
def no_budget(monkeypatch):
    monkeypatch.setattr(runner.efam, "assert_budget_ok", lambda *a, **k: 0.0)


def test_runner_m1_violation_reruns_b3_once_then_ok(tmp_path, no_budget):
    d = _b3_dir(tmp_path, "r1")
    good_story = "月の後期の縮みは、半径で約42〜46 mと推定される。"
    c, sent = _b3_client([("月の半径は約4億年で約45 m縮んだと見積もられる。", ["約45 m"]), (good_story, FIELD_MOON)])
    ledger = _first_b3(c, d)
    ev = runner.run_numeric_field_step(c, "T", ledger, d, 150.0, fresh_b3=True)
    assert ev["b3_rerun"] and ev["mode"] == "field_ok" and ev["gate_E"] == ["約42〜46"] and len(sent) == 2
    assert ev["first_pass"]["ok"] is False and ev["first_pass"]["violations"] and ev["first_pass"]["field_items"] == ["約45 m"]
    assert sent[1]["input"][-1]["content"].endswith(N.M1_RETRY_NOTE_V3_TEMPLATE.format(problems=N.m1_problem_text(
        {"violations": ev["first_pass"]["violations"]})))
    assert os.path.isdir(os.path.join(d, "storyline_b3_attempt1")) and os.path.exists(os.path.join(d, "storyline_b3", "numeric_retention_b3.json"))
    # 欄の1回目/最終値がrun単位で残る
    j = json.load(open(os.path.join(d, "storyline_b3", "numeric_retention_b3.json"), encoding="utf-8"))
    assert j["first_pass"]["field_items"] == ["約45 m"] and j["final_field_items"] == FIELD_MOON


def test_runner_m1_second_violation_is_E_empty_with_warn_not_second_rerun(tmp_path, no_budget):
    d = _b3_dir(tmp_path, "r2")
    c, sent = _b3_client([("月の半径は約4億年で約45 m縮んだと見積もられる。", ["約45 m"]), ("月の半径は約45 m縮んだ。", ["約45 m"])])
    ledger = _first_b3(c, d)
    ev = runner.run_numeric_field_step(c, "T", ledger, d, 150.0, fresh_b3=True)
    assert len(sent) == 2 and ev["b3_rerun"] and ev["mode"] == "m1_final_violation_E_empty" and ev["E"] == [] and ev["warn"]


def test_runner_no_rerun_when_reusing_existing_b3(tmp_path, no_budget):
    d = _b3_dir(tmp_path, "r3")
    c, sent = _b3_client([("月の半径は約4億年で約45 m縮んだと見積もられる。", ["約45 m"])])
    ledger = _first_b3(c, d)
    ev = runner.run_numeric_field_step(c, "T", ledger, d, 150.0, fresh_b3=False)       # 既存B3の再利用/再開: B3を呼ばない
    assert len(sent) == 1 and not ev["b3_rerun"] and ev["mode"] == "m1_final_violation_E_empty"


def test_runner_field_empty_and_legacy(tmp_path, no_budget):
    d = _b3_dir(tmp_path, "r4")
    c, sent = _b3_client([("月のしわは縮みを全部は語らない。", [])])
    ledger = _first_b3(c, d)
    ev = runner.run_numeric_field_step(c, "T", ledger, d, 150.0, fresh_b3=True)
    assert len(sent) == 1 and ev["mode"] == "field_empty" and not ev["b3_rerun"]
    d2 = _b3_dir(tmp_path, "r5")                                  # 旧記事(欄ファイルなし)
    shutil.copytree(os.path.join(MOON, "storyline_b3"), os.path.join(d2, "storyline_b3"))
    ev2 = runner.run_numeric_field_step(c, "T", ledger, d2, 150.0, fresh_b3=False)
    assert ev2["mode"] == "legacy_no_field" and len(sent) == 1


def test_runner_default_call_has_no_variant_for_other_callers():
    """Y Trial等が呼ぶ run_storyline_b3 の既定は variant なし(従来)。"""
    import inspect
    assert inspect.signature(runner.run_storyline_b3).parameters["numeric_variant"].default is None
    assert inspect.signature(w1.run_w1_writer).parameters["numeric"].default is None
    assert inspect.signature(b3.run_storyline_b3_selection).parameters["variant"].default is None


# ======================================================================================================
# 回帰: Trialの保存済みB3出力・Writer出力に対する決定論再適用(0円)
# ======================================================================================================
def _trial_samples():
    return sorted(os.path.dirname(os.path.dirname(p)) for p in glob.glob(os.path.join(TRIAL, "*", "A", "*", "storyline_b3", "reader_must_hear_numbers.json")))


def _same_E(a, b):
    keys = ("ok", "violations", "candidates", "gate_E", "observe_E", "ignored", "ambiguous_small_ints", "field_items")
    return {k: a.get(k) for k in keys} == {k: b.get(k) for k in keys}


def test_saved_trial_samples_E_parity_with_validated_trial():
    samples = _trial_samples()
    if not samples:
        pytest.skip("Trial保存済み標本なし")
    bad = []
    for d in samples:
        try:
            a = D.derive_E_r5(d)
        except FileNotFoundError:
            continue
        b = N.derive_E_from_field(d)
        if not _same_E(a, b):
            bad.append(d)
    assert bad == []
    assert len(samples) >= 10


def test_saved_trial_samples_o2prime_plan_parity():
    n = 0
    for d in _trial_samples():
        try:
            E = N.derive_E_from_field(d)
            ann = json.load(open(os.path.join(d, "storyline_b3", "annotation.json"), encoding="utf-8"))
            _, fm = w1.parse_brief_md(open(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"), encoding="utf-8").read())
        except FileNotFoundError:
            continue
        if E["ok"] and E["gate_E"]:
            assert N.plan_o2prime(ann, fm, E) == D.plan_o2prime(ann, fm, E)
            n += 1
    assert n >= 5


def test_saved_trial_final_texts_pass_production_gate():
    """Trialで合格した標本(6標本・4記事型)の保存済みR0/R1/R2に、Production Gateを当てると不足0・新規数値0(Trialの結論と一致)。"""
    checked = 0
    for d in _trial_samples():
        r2 = os.path.join(d, "ja_writer", "revision2.md")
        r0 = os.path.join(d, "ja_writer", "factlock", "r0.md")
        if not (os.path.exists(r2) and os.path.exists(r0)):
            continue
        try:
            ctx = N.NumericRetention.from_out_dir(d)
        except FileNotFoundError:
            continue
        if not ctx.active:
            continue
        txt = {k: open(os.path.join(d, rel), encoding="utf-8").read() for k, rel in (("r0", "ja_writer/factlock/r0.md"), ("r1", "ja_writer/revision1.md"), ("r2", "ja_writer/revision2.md"))}
        _, facts = w1.parse_brief_md(open(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"), encoding="utf-8").read())
        ctx.set_m2_context(txt["r0"], facts)
        m = {k: ctx.missing(v, k) for k, v in txt.items() if k == "r0"}
        for k in ("r1", "r2"):
            m[k] = ctx.missing(txt[k], k, m2=True)
        checked += 1
        assert not any(m.values()), (d, m)
    assert checked >= 4


def test_saved_trial_range_outputs_are_normalized_by_j2():
    """Trial実測(R1/R2が『から』を波ダッシュへ戻す)の保存済み生出力に対し、J2適用後は数字間の波ダッシュが0。"""
    seen = 0
    for p in glob.glob(os.path.join(TRIAL, "*", "A", "*", "ja_writer", "factlock", "r1.raw.orig.md")):
        t = open(p, encoding="utf-8").read()
        if re.search(r"\d\s*[〜～~]\s*\d", t):
            out = N.normalize_ranges(t)
            assert not re.search(r"\d\s*[〜～~]\s*\d", out)
            assert re.sub(r"[^0-9]", "", out) == re.sub(r"[^0-9]", "", t)      # 数字・桁は不変
            seen += 1
    assert seen >= 0


def test_en_observation_never_raises_and_writes_file(tmp_path):
    d = _make_dir(tmp_path)
    os.makedirs(os.path.join(d, "a2"))
    open(os.path.join(d, "a2", "article.md"), "w", encoding="utf-8").write("The moon shrank by about 42 to 46 meters.")
    os.makedirs(os.path.join(d, "ja_writer"), exist_ok=True)
    res = N.observe_en(d)
    assert res["levels"]["EN_Std"]["約42〜46"] is True and not res["warn"]
    open(os.path.join(d, "a2", "article.md"), "w", encoding="utf-8").write("The moon shrank a little.")
    res2 = N.observe_en(d)
    assert res2["warn"] and os.path.exists(os.path.join(d, "ja_writer", "numeric_retention_en_observation.json"))
    N.observe_en(str(tmp_path / "nonexistent"))     # 例外を外へ出さない
