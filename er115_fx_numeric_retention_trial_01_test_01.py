# -*- coding: utf-8 -*-
"""er115 DEV/Trial のtest(API 0円・Production非接続。実LLMは呼ばない=FakeClient)。"""
import glob
import hashlib
import json
import os
import re
import shutil
import types

import pytest

import er115_fx_numeric_retention_trial_01 as D
import er115_fx_numeric_retention_calibration_01 as C

ROOT = D.ROOT
MOON = os.path.join(ROOT, "er019_output", "moon_shrinking", "run_ms_02")
PINNED_R0_PROMPT_SHA = "6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366"


# ---------------- Isolation(Production到達経路に入らない) ----------------
def test_isolation_no_production_reference():
    hits = []
    for p in glob.glob(os.path.join(ROOT, "*.py")):
        base = os.path.basename(p)
        if base.startswith("er115_"):
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        if "er115_" in txt or "JANumericRetentionStopError" in txt or "B3_ADDENDUM" in txt:
            hits.append(base)
    assert hits == [], hits


def test_production_prompt_constants_unchanged():
    assert hashlib.sha256(D.jaw.R0_PROMPT.encode("utf-8")).hexdigest() == PINNED_R0_PROMPT_SHA
    # R0_PROMPT本体の「800～1000字」は残る(範囲正規化は入力側のみ)
    assert "800～1000字" in D.jaw.R0_PROMPT or "800〜1000字" in D.jaw.R0_PROMPT


def test_off_is_byte_identical_to_production():
    story = "月面の「しわ」から推定された後期の縮みは約42〜46【中核数値】 mだった。"
    news = "- 【事実1】月の半径が約42〜46【中核数値】 m縮んだと推定された。\n"
    assert D.build_r0_prompt_dev(story, news, None) == D.w1.build_r0_prompt(story, news, None)
    on = D.build_r0_prompt_dev(story, news, None, range_norm=True)
    assert on != D.w1.build_r0_prompt(story, news, None)
    assert "約42から46【中核数値】" in on
    # R0_PROMPT本体(「テーマ：」行以外の固定部)は一切変わらない(範囲正規化の対象は『テーマ：』行とニュース欄だけ)
    old_lines = D.w1.build_r0_prompt(story, news, None).split("[ニュース]")[0].splitlines()
    new_lines = on.split("[ニュース]")[0].splitlines()
    assert [l for l in old_lines if not l.startswith("テーマ：")] == [l for l in new_lines if not l.startswith("テーマ：")]


def test_dev_flag_free_import():
    # 環境変数・CLI引数でProduction挙動が変わる経路が無いこと(DEV runnerを起動しない限り何も起きない)
    src = open(D.__file__, encoding="utf-8").read()
    assert "os.environ" not in src


# ---------------- R4 範囲正規化 ----------------
def test_normalize_ranges_only_number_wave_number():
    assert D.normalize_ranges("約42〜46【中核数値】 m") == "約42から46【中核数値】 m"
    assert D.normalize_ranges("約42～46 m") == "約42から46 m"
    assert D.normalize_ranges("傾き25〜35度") == "傾き25から35度"
    assert D.normalize_ranges("10月27~28日") == "10月27~28日"            # 日付範囲は対象外
    assert D.normalize_ranges("25-35度") == "25-35度"                   # ハイフン範囲は対象外
    assert D.normalize_ranges("ローベート〜スカープ") == "ローベート〜スカープ"   # 数字以外は触れない
    assert D.normalize_ranges("約3〜4億年前") == "約3から4億年前"


# ---------------- M4 照合 ----------------
def test_match_core_synthetic_all_correct():
    bad = []
    for surface, hint, text, exp, note in C.SYNTHETIC:
        if D.match_core(surface, text, hint)["present"] != exp:
            bad.append((surface, note, text))
    assert bad == []


def test_match_core_blind_labels_zero_error():
    r = C.run()
    assert r["new"]["FP"] == 0 and r["new"]["FN"] == 0, r["errors"]
    assert r["new"]["TP"] + r["new"]["TN"] == 122


def test_en_present_units():
    assert D.en_present("約42〜46", "shrank by about 42 to 46 meters", "m")
    assert not D.en_present("約42〜46", "about 42 to 46 people", "m")
    assert D.en_present("約4億年", "about 400 million years ago")
    assert D.en_present("2026年9月3日", "x") is None


# ---------------- M1 / E ----------------
def _make_dir(tmp_path, story):
    d = tmp_path / "moon"
    shutil.copytree(os.path.join(MOON, "research_ledger"), d / "research_ledger")
    (d / "storyline_b3").mkdir()
    ev = json.load(open(os.path.join(MOON, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    ev = {k: v for k, v in ev.items() if k in ("selected_storyline", "full_ledger_fact_ids", "fact_tests", "selected_fact_ids",
                                              "selected_fact_brief_text", "recheck_note", "soft_warnings", "min2_policy")}
    ev["selected_storyline"] = story
    json.dump(ev, open(d / "storyline_b3" / "fact_selection_evidence.json", "w", encoding="utf-8"), ensure_ascii=False)
    brief = open(os.path.join(MOON, "storyline_b3", "selected_brief.md"), encoding="utf-8").read()
    old_story = json.load(open(os.path.join(MOON, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))["selected_storyline"]
    assert old_story in brief
    (d / "storyline_b3" / "selected_brief.md").write_text(brief.replace(old_story, story), encoding="utf-8")
    runner = D.runner
    (d / "storyline_b3" / "audit").mkdir()
    runner.run_annotation_producer(str(d))
    return str(d)


def test_derive_E_ok_with_42_46(tmp_path):
    d = _make_dir(tmp_path, "月の「しわ」から見積もった後期の縮みは、半径で約42〜46 mと推定される。")
    e = D.derive_E(d)
    assert e["ok"], e["violations"]
    assert [c["news_surface"] for c in e["candidates"]] == ["約42〜46"]
    assert e["gate_E"] and e["gate_E"][0]["unit_hint"] == "m"


def test_derive_E_spelling_variation_maps_to_news_surface(tmp_path):
    d = _make_dir(tmp_path, "月の「しわ」から見積もった後期の縮みは、半径で42〜46メートルと推定される。")
    e = D.derive_E(d)
    assert e["ok"], e["violations"]
    assert e["candidates"][0]["news_surface"] == "約42〜46"
    assert e["candidates"][0]["story_surface"] != e["candidates"][0]["news_surface"]


def test_derive_E_peripheral_number_in_storyline_is_violation(tmp_path):
    d = _make_dir(tmp_path, "月の半径は約4億年で約45 m縮んだと見積もられる。")
    e = D.derive_E(d)
    assert not e["ok"]
    assert any(v["reason"] == "peripheral_number_in_storyline" for v in e["violations"])
    assert e["gate_E"] == []


def test_derive_E_time_premise_is_observation_only(tmp_path):
    d = _make_dir(tmp_path, "月の後期の縮みは約42〜46 mで、約4億年前から続いたという仮定つきの推定である。")
    e = D.derive_E(d)
    assert e["ok"], e["violations"]
    assert [c["news_surface"] for c in e["gate_E"]] == ["約42〜46"]
    assert any(c["time_premise"] for c in e["observe_E"])


def test_derive_E_more_than_two_is_violation(tmp_path):
    d = _make_dir(tmp_path, "8,900本超のしわから約42〜46 mの縮みが約4億年かけて起きたと推定された。")
    e = D.derive_E(d)
    assert not e["ok"] and any("too_many" in v["reason"] for v in e["violations"])


def test_derive_E_no_numbers_is_empty_not_violation(tmp_path):
    d = _make_dir(tmp_path, "月のしわは縮みを全部は語らない。")
    e = D.derive_E(d)
    assert e["ok"] and e["gate_E"] == [] and e["storyline_has_no_numbers"]


# ---------------- Gate / 再実行枠(FakeClient) ----------------
class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.prompts = []
        outer = self

        class R:
            def create(self_inner, **kw):
                outer.prompts.append(kw["input"][-1]["content"])
                text = outer.script.pop(0)
                model = D.w1.R0_MODEL if len(outer.prompts) == 1 or "テーマ：" in kw["input"][-1]["content"] else D.w1.ASTRA_MODEL
                return types.SimpleNamespace(output_text=text, model=model + "-x", id="resp_%d" % len(outer.prompts),
                                             usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
        self.responses = R()


GOOD = "月のしわが語ること\n\n月の半径は、後期に約42から46メートル縮んだと推定されている。【事実3】\n"
NOPE = "月のしわが語ること\n\n月の半径は、後期にごくわずか縮んだと推定されている。【事実3】\n"
SYMB = "月のしわが語ること\n\n月の半径は、後期に約42〜46メートル縮んだと推定されている。【事実3】\n"


def _chain_dir(tmp_path):
    d = _make_dir(tmp_path, "月の「しわ」から見積もった後期の縮みは、半径で約42〜46 mと推定される。")
    E = D.derive_E(d)
    return d, E


def test_gate_all_ok_minimum_calls(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, GOOD])
    r = D.run_w1_dev(d, fc, E)
    ev = r["runtime_evidence"]
    assert ev["calls_count"] == {"r0": 1, "r1": 1, "r2": 1}
    assert "約42から46" in fc.prompts[0]          # 範囲正規化が入力に効いている
    assert "約42〜46" not in fc.prompts[0].split("[ニュース]", 1)[1]


def test_r0_retention_regen_once_with_note(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([NOPE, GOOD, GOOD, GOOD])
    r = D.run_w1_dev(d, fc, E)
    assert r["runtime_evidence"]["calls_count"]["r0"] == 2
    assert "次の数字が本文にありません: 約42から46 m" in fc.prompts[1]
    assert r["runtime_evidence"]["retention"]["r0"]["table_case"] == "ret_only"


def test_r0_symbol_only_regen_then_ok(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([SYMB, GOOD, GOOD, GOOD])
    r = D.run_w1_dev(d, fc, E)
    assert r["runtime_evidence"]["retention"]["r0"]["table_case"] == "sym_only"
    assert r["runtime_evidence"]["calls_count"]["r0"] == 2


def test_r0_regen_loses_E_is_stop(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([SYMB.replace("約42〜46メートル", "約42〜46メートル"), NOPE])
    with pytest.raises(D.JANumericRetentionStopError) as ei:
        D.run_w1_dev(d, fc, E)
    assert ei.value.stage == "r0"
    assert os.path.exists(os.path.join(d, "ja_writer", "audit", "rejected_w1_r0_first.md"))
    assert os.path.exists(os.path.join(d, "ja_writer", "audit", "rejected_w1_r0_regen.md"))
    assert len(fc.prompts) == 2             # R0は最大2呼出


def test_r1_rerun_once_then_stop(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([GOOD, NOPE, NOPE])
    with pytest.raises(D.JANumericRetentionStopError) as ei:
        D.run_w1_dev(d, fc, E)
    assert ei.value.stage == "r1" and len(fc.prompts) == 3


def test_r2_shares_single_rerun_slot(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, NOPE, GOOD])
    r = D.run_w1_dev(d, fc, E)
    assert r["runtime_evidence"]["calls_count"] == {"r0": 1, "r1": 1, "r2": 2}


def test_r2_rerun_still_missing_is_stop(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, NOPE, NOPE])
    with pytest.raises(D.JANumericRetentionStopError) as ei:
        D.run_w1_dev(d, fc, E)
    assert ei.value.stage == "r2" and len(fc.prompts) == 4


def test_r2_symbol_and_missing_share_single_rerun(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, NOPE.replace("縮んだ", "縮んだ〜"), GOOD])
    r = D.run_w1_dev(d, fc, E)
    assert r["runtime_evidence"]["calls_count"]["r2"] == 2
    assert r["runtime_evidence"]["retention"]["r2"]["table_case"] in ("sym+ret", "ret_only")


def test_gate_does_not_rewrite_text(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, GOOD])
    r = D.run_w1_dev(d, fc, E)
    assert open(os.path.join(d, "ja_writer", "revision2.md"), encoding="utf-8").read().strip().startswith("月のしわが語ること")


def test_misread_warn_observation_only():
    w = D.scan_misreading("約4億年前から今も同じ速さで縮んでいる。月の誕生以来のことだ。")
    assert w["near_time_misread"] and w["origin_claims_unnegated"]
    w2 = D.scan_misreading("約4億年前以降の後期の縮みで、開始時期は推定である。")
    assert not w2["near_time_misread"] and not w2["origin_claims"]


def test_retention_note_text():
    e = {"news_surface": "約42〜46", "unit_hint": "m"}
    assert D.retention_note([e]) == "次の数字が本文にありません: 約42から46 m。ニュース欄のとおりに含めて書き直してください。他の数字は増やさないでください。"


# ---------------- B3 DEV(追記ブロック・M1再実行)をFakeClientで ----------------
def _b3_fake(stories):
    ev = json.load(open(os.path.join(MOON, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    queue = list(stories)
    sent = []

    class R:
        def create(self_inner, **kw):
            sent.append(kw["input"][-1]["content"])
            story = queue.pop(0)
            out = {"selected_storyline": story, "fact_tests": ev["fact_tests"], "selected_fact_ids": ev["selected_fact_ids"],
                   "selected_fact_brief": ev["selected_fact_brief_text"], "recheck_note": ev["recheck_note"]}
            return types.SimpleNamespace(output_text=json.dumps(out, ensure_ascii=False), model=D.w1.routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"] + "-x",
                                         id="b3_%d" % len(sent), usage=types.SimpleNamespace(input_tokens=1, output_tokens=1))
    c = types.SimpleNamespace(responses=R())
    return c, sent


def test_b3_dev_appends_addendum_and_reruns_once_on_m1_violation(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "OUT_ROOT", str(tmp_path / "out"))
    monkeypatch.setattr(D.cl, "install", lambda p: None)
    client, sent = _b3_fake(["月の半径は約4億年で約45 m縮んだと見積もられる。", "月の後期の縮みは、半径で約42〜46 mと推定される。"])
    res = D.run_b3_dev("moon_shrinking", "A", "t1", per_run_cap=30, phase_cap=120, client=client)
    assert res["status"] == "E_OK" and res["b3_rerun"] and not res["first_pass_ok"]
    assert sent[0].endswith(D.B3_ADDENDUM)
    assert sent[1].endswith(D.M1_RETRY_NOTE_TEMPLATE.format(problems="約45(peripheral_number_in_storyline)")) or "前回出力の修正指示(数値)" in sent[1]
    assert os.path.isdir(os.path.join(D.sample_dir("moon_shrinking", "A", "t1"), "storyline_b3_attempt1"))
    assert [c["news_surface"] for c in res["E"]["gate_E"]] == ["約42〜46"]


def test_b3_dev_second_violation_is_not_E_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "OUT_ROOT", str(tmp_path / "out"))
    monkeypatch.setattr(D.cl, "install", lambda p: None)
    client, sent = _b3_fake(["月の半径は約4億年で約45 m縮んだと見積もられる。", "月の半径は約45 m縮んだ。"])
    res = D.run_b3_dev("moon_shrinking", "A", "t2", per_run_cap=30, phase_cap=120, client=client)
    assert res["status"] == "M1_VIOLATION" and len(sent) == 2


def test_b3_dev_E_empty_when_storyline_has_no_numbers(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "OUT_ROOT", str(tmp_path / "out"))
    monkeypatch.setattr(D.cl, "install", lambda p: None)
    client, sent = _b3_fake(["月のしわは縮みを全部は語らない。"])
    res = D.run_b3_dev("moon_shrinking", "A", "t3", per_run_cap=30, phase_cap=120, client=client)
    assert res["status"] == "E_EMPTY" and len(sent) == 1


# ---------------- R1/R2が波ダッシュへ戻す問題(Phase 1実測)への後処理と再開 ----------------
WAVE_R1 = "月のしわが語ること\n\n月の半径は、後期に約42〜46メートル縮んだと推定されている。\n"


def test_astra_output_range_wave_is_normalized_not_stop(tmp_path):
    d, E = _chain_dir(tmp_path)
    fc = FakeClient([GOOD, WAVE_R1, WAVE_R1])
    r = D.run_w1_dev(d, fc, E)
    assert r["runtime_evidence"]["calls_count"] == {"r0": 1, "r1": 1, "r2": 1}
    assert "約42から46メートル" in r["ja_text"] and "〜" not in r["ja_text"]
    assert r["runtime_evidence"]["r1_calls"][0]["range_wave_normalized"] == 1


def test_non_numeric_wave_still_flagged_by_symbol_qa(tmp_path):
    d, E = _chain_dir(tmp_path)
    bad = "月のしわが語ること\n\n月の半径は約42から46メートル縮んだ。ローベート〜スカープ。\n"
    fc = FakeClient([GOOD, GOOD, bad, bad])
    with pytest.raises(D.JANumericRetentionStopError) as ei:
        D.run_w1_dev(d, fc, E)
    assert ei.value.stage == "r2"


def test_resume_from_r2_reuses_r0_r1_and_normalizes(tmp_path, monkeypatch):
    d, E = _chain_dir(tmp_path)
    monkeypatch.setattr(D, "normalize_ranges_counted", lambda t: (t, 0))
    fc = FakeClient([GOOD, WAVE_R1, WAVE_R1, WAVE_R1])
    with pytest.raises(D.JANumericRetentionStopError):
        D.run_w1_dev(d, fc, E)                     # 旧挙動(正規化なし)の再現: R2で記号STOP
    monkeypatch.undo()
    fc2 = FakeClient([WAVE_R1])
    r = D.resume_w1_dev_from_r2(d, fc2, E)
    assert len(fc2.prompts) == 1                    # R2を1呼出するだけ(R0/R1は再利用)
    assert "約42から46メートル" in r["ja_text"]
    assert os.path.exists(os.path.join(d, "ja_writer", "factlock", "r1.raw.orig.md"))
    assert r["runtime_evidence"]["resumed_from_r2"]["r1_raw_range_wave_normalized"] == 1


def test_origin_claim_negation_detected():
    w = D.scan_misreading("これは月の誕生以来の縮み総決算ではない点だ。")
    assert w["origin_claims"] and w["origin_claims"][0]["negated"] and not w["origin_claims_unnegated"]
    w2 = D.scan_misreading("月は誕生以来ずっと縮んでいる。")
    assert w2["origin_claims_unnegated"]
