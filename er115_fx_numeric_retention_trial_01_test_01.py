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
        if base.startswith(("er115_", "er116_")) or base.endswith(("_test_01.py", "_test.py")):     # testファイルは許可リストでer115_を名指しするため対象外(Production module判定)。er116_ = 委任_07のProduction module/test(test側がTrialとのsource同一性検査のためer115をimport。moduleはer115を参照しない=er116 testで確認)
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        # 委任_07: Productionは自前のJANumericRetentionStopError(er053)・B3_ADDENDUM_V4(er116)を持つため、Trial固有名はer115_の参照のみで判定する
        if "er115_" in txt:
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


# ======================================================================================================
# 委任_03 M5
S1 = os.path.join(ROOT, "er115_output", "fx_numeric_retention_trial_01", "moon_shrinking", "A", "s1")


def _s1_dir(tmp_path):
    """Phase 1 標本A/s1(B3 DEV実出力: E={約42〜46}, 約750がニュース欄の中核数値, 約3〜4億年)をtmpへ複製。API 0。"""
    d = tmp_path / "s1"
    shutil.copytree(os.path.join(S1, "storyline_b3"), d / "storyline_b3")
    shutil.copytree(os.path.join(MOON, "research_ledger"), d / "research_ledger")   # prepare_dirと同じ元ledger(dev_source.jsonのsha一致)
    return str(d), D.derive_E(str(d))
# O-2'(同単位系の印付け替え)・O-1'・M2(新規数値検出)
# ======================================================================================================
def _sidecar_plan(numbers, facts_marked, gate_surface="約42〜46", hint="m", extra_candidates=()):
    E_info = {"gate_E": [{"news_surface": gate_surface, "unit_hint": hint, "concept": "C1"}],
              "candidates": [{"news_surface": gate_surface, "concept": "C1"}, *extra_candidates]}
    return D.plan_o2prime({"numbers": numbers}, facts_marked, E_info)


def _num(surface, concept, cls="core", kind=None, ids=("F01",)):
    return {"surface": surface, "kind": kind or D.P.surface_kind(surface), "class": cls, "concept": concept, "ledger_ids": list(ids), "role": ""}


FACTS_MARKED = ("- 【事実1】半径が約42〜46【中核数値】 m縮んだ。約750【中核数値】 m以上の予測があり、約11cm/100万年【中核数値】の速度や約3〜4億年【中核数値】前、"
                "9.14ドル【中核数値】、約15%【中核数値】、約5,470本【中核数値】、約9か月【中核数値】、約1.1【周辺数値】 kmもある。\n")


def test_o2prime_demotes_only_same_unit_system_values():
    nums = [_num("約42〜46", "C1"), _num("約750", "C2"), _num("約11cm/100万年", "C3"), _num("約3〜4億年", "C4"), _num("9.14ドル", "C5"),
            _num("約15%", "C6"), _num("約5,470本", "C7"), _num("約9か月", "C8")]
    plan = _sidecar_plan(nums, FACTS_MARKED)
    assert plan["e_dimensions"] == ["length"] and plan["applied"]
    assert sorted(x["surface"] for x in plan["demote"]) == ["約11cm/100万年", "約750"]            # 長さ(m/cm、速度含む)だけ
    kept = {x["surface"]: x["why_kept"] for x in plan["kept_core"]}
    assert kept["約3〜4億年"] == "year_system_or_period"                                      # 年系は下げない
    assert kept["約9か月"] == "year_system_or_period"
    assert kept["9.14ドル"] == "different_unit_system_from_E" and kept["約15%"] == "different_unit_system_from_E"   # 別の単位系は下げない
    assert kept["約5,470本"] == "unit_unresolved_or_other_system"                              # 単位が取れない/対象外は下げない
    assert kept["約42〜46"] == "in_E"


def test_o2prime_unit_unresolved_and_small_ints_not_demoted():
    nums = [_num("約42〜46", "C1"), _num("1", "C2"), _num("約300", "C3")]
    facts = "- 【事実1】約42〜46【中核数値】 m。長さ1【中核数値】 km超。約300【中核数値】はある。\n"
    plan = _sidecar_plan(nums, facts)
    assert plan["demote"] == []
    kept = {x["surface"]: x["why_kept"] for x in plan["kept_core"]}
    assert kept["1"] == "unitless_small_int" and kept["約300"] == "unit_unresolved_or_other_system"


def test_o2prime_E_members_never_demoted_and_empty_E_demotes_nothing():
    nums = [_num("約42〜46", "C1"), _num("約750", "C2")]
    both = D.plan_o2prime({"numbers": nums}, FACTS_MARKED, {"gate_E": [{"news_surface": "約42〜46", "unit_hint": "m"}, {"news_surface": "約750", "unit_hint": "m"}],
                                                          "candidates": [{"concept": "C1", "news_surface": "約42〜46"}, {"concept": "C2", "news_surface": "約750"}]})
    assert both["demote"] == []                                     # 750がEに入るs2/s5型: O-2'は効かない(O-1'の担当)
    empty = D.plan_o2prime({"numbers": nums}, FACTS_MARKED, {"gate_E": [], "candidates": []})
    assert empty["demote"] == [] and not empty["applied"]            # E空=何も下げない(uk_train型)


def test_o2prime_peripheral_numbers_untouched_and_dates_untouched():
    nums = [_num("約42〜46", "C1"), _num("約1.1", "C2", cls="peripheral"), _num("2026年10月19日", "C3", kind="date_time")]
    plan = _sidecar_plan(nums, FACTS_MARKED + "2026年10月19日【中核数値】\n")
    assert plan["demote"] == []


def test_swap_marks_changes_only_targeted_marks():
    t = FACTS_MARKED
    new, n = D.swap_marks(t, ["約750", "約11cm/100万年"])
    assert n == 2
    assert "約750【周辺数値】" in new and "約11cm/100万年【周辺数値】" in new
    assert re.sub(r"【(?:中核|周辺)数値】", "", new) == re.sub(r"【(?:中核|周辺)数値】", "", t)             # 印以外の文字は不変
    assert "約42〜46【中核数値】" in new and "約3〜4億年【中核数値】" in new
    same, n0 = D.swap_marks(t, ["約9999"])
    assert same == t and n0 == 0
    assert D.swap_marks(t, ["約75"])[1] == 0                         # 数字境界: 『約75』は『約750』の一部に一致しない


def test_o2prime_off_is_byte_identical_and_writes_nothing(tmp_path):
    d, E = _s1_dir(tmp_path)
    fc = FakeClient([GOOD, GOOD, GOOD])
    D.run_w1_dev(d, fc, E)                                          # o2prime既定=False
    ann = D.contract.validate_annotated_b3(d)
    story, facts = D.w1.parse_brief_md(ann.annotated_md_text)
    overlay, _ = D.rounding.load_overlay_for_writer(d, ann.annotated_md_sha256)
    news = D.rounding.news_field_for_writer(ann.news_field_text, facts, ann.constraints_text, overlay, D.P.CONS_HEADING, D.P.compose_news_field)
    assert fc.prompts[0] == D.build_r0_prompt_dev(story, news, overlay, range_norm=True)     # OFF=従来DEVとバイト一致
    assert not os.path.exists(os.path.join(d, "o2prime_plan.json"))


def test_o2prime_on_swaps_marks_in_writer_input_only(tmp_path):
    d, E = _s1_dir(tmp_path)
    sha_before = hashlib.sha256(open(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"), "rb").read()).hexdigest()
    fc = FakeClient([GOOD, GOOD, GOOD])
    r = D.run_w1_dev(d, fc, E, o2prime=True)
    plan = json.load(open(os.path.join(d, "o2prime_plan.json"), encoding="utf-8"))
    dem = [x["surface"] for x in plan["demote"]]
    assert "約750" in dem and "約3〜4億年" not in dem
    nf = fc.prompts[0].split("[ニュース]", 1)[1]
    assert "約750【周辺数値】" in nf and "約750【中核数値】" not in nf
    assert "約3から4億年【中核数値】" in nf and "約42から46【中核数値】" in nf                  # 年系とEは中核のまま
    assert hashlib.sha256(open(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"), "rb").read()).hexdigest() == sha_before   # 契約済みファイル不変
    D.contract.validate_annotated_b3(d)                                                       # 契約検証は引き続きPASS
    assert r["runtime_evidence"]["o2prime"] is True and plan["marks_swapped"]["demoted_surfaces"] == len(dem)


# ---- M2: R1/R2の新規数値検出(中点『約45』型) ----
MID = "月のしわが語ること\n\n月の半径は、後期に約42から46メートル、つまり約45メートル縮んだと推定されている。【事実3】\n"


def test_new_numbers_detects_midpoint_and_not_known_values():
    news = "半径が約42〜46 m縮んだ。約750 m以上の予測。約3〜4億年前。"
    r0 = "後期に約42から46メートル縮んだと推定されている。"
    assert D.new_numbers("後期に約42〜46メートル、約45メートル縮んだ。", r0, news) == ["約45"]
    assert D.new_numbers("後期に約42から46メートル縮んだ。", r0, news) == []
    assert D.new_numbers("3つの理由がある。", r0, news) == []                                 # 単位なし小整数は対象外


def test_m2_off_does_not_check_midpoint_phase1_behavior(tmp_path):
    d, E = _s1_dir(tmp_path)
    fc = FakeClient([GOOD, MID, GOOD])
    r = D.run_w1_dev(d, fc, E)                                       # m2=False: Phase 1と同じ(検出しない)
    assert r["runtime_evidence"]["calls_count"] == {"r0": 1, "r1": 1, "r2": 1}


def test_m2_r1_new_number_shares_single_rerun_then_ok(tmp_path):
    d, E = _s1_dir(tmp_path)
    fc = FakeClient([GOOD, MID, GOOD, GOOD])
    r = D.run_w1_dev(d, fc, E, m2=True)
    assert r["runtime_evidence"]["calls_count"] == {"r0": 1, "r1": 2, "r2": 1}
    assert r["runtime_evidence"]["new_numbers"]["r1"]["first"] == ["約45"] and r["runtime_evidence"]["new_numbers"]["r1"]["after"] == []


def test_m2_r1_new_number_persists_is_stop(tmp_path):
    d, E = _s1_dir(tmp_path)
    fc = FakeClient([GOOD, MID, MID])
    with pytest.raises(D.JANumericRetentionStopError) as ei:
        D.run_w1_dev(d, fc, E, m2=True)
    assert ei.value.stage == "r1" and len(fc.prompts) == 3 and ei.value.missing[0]["news_surface"] == "NEW:約45"


def test_m2_r2_new_number_one_rerun_then_stop(tmp_path):
    d, E = _s1_dir(tmp_path)
    ok = D.run_w1_dev(d, FakeClient([GOOD, GOOD, MID, GOOD]), E, m2=True)
    assert ok["runtime_evidence"]["calls_count"]["r2"] == 2
    d2, E2 = _s1_dir(tmp_path / "x")
    fc = FakeClient([GOOD, GOOD, MID, MID])
    with pytest.raises(D.JANumericRetentionStopError) as ei:
        D.run_w1_dev(d2, fc, E2, m2=True)
    assert ei.value.stage == "r2" and len(fc.prompts) == 4


# ---- O-1' ----
def test_b3_addendum_v2_text_and_v1_unchanged(tmp_path, monkeypatch):
    assert "比較相手" in D.B3_ADDENDUM_V2 and "比較そのものが問いへの答えである場合を除き" in D.B3_ADDENDUM_V2
    assert "答えそのものの値だけ" in D.B3_ADDENDUM_V2 and "最大2個" in D.B3_ADDENDUM_V2
    assert "比較相手" not in D.B3_ADDENDUM                          # v1(Phase 1)は不変
    monkeypatch.setattr(D, "OUT_ROOT", str(tmp_path / "out"))
    monkeypatch.setattr(D.cl, "install", lambda p: None)
    client, sent = _b3_fake(["月の後期の縮みは、半径で約42〜46 mと推定される。"])
    res = D.run_b3_dev("moon_shrinking", "A", "t9", per_run_cap=30, phase_cap=120, client=client, addendum_version="v2")
    assert sent[0].endswith(D.B3_ADDENDUM_V2) and res["b3_addendum_version"] == "v2"


def test_isolation_phase1b_flags_have_no_env_or_default_on():
    import inspect
    sig = inspect.signature(D.run_w1_dev)
    assert sig.parameters["o2prime"].default is False and sig.parameters["m2"].default is False
    assert inspect.signature(D.run_b3_dev).parameters["addendum_version"].default == "v1"


# ======================================================================================================
# 委任_06 C-1(欄の数値をderive_ranksのStoryline同等に扱う。DEV専用・API 0)/ C-3(EN照合: 倍率語・3D誤一致)
# ======================================================================================================
SEMI = os.path.join(D.OUT_ROOT, "semiconductor_earnings", "A")
COFFEE = os.path.join(D.OUT_ROOT, "coffee_prices", "A")
needs_artifacts = pytest.mark.skipif(not os.path.isdir(os.path.join(SEMI, "r6s1", "storyline_b3_attempt1")), reason="Trial artifactなし")


def test_c1_production_ddet_untouched_and_restored():
    orig = D.P.ddet
    with D.field_priority_ddet(["167億ドル"]):
        assert D.P.ddet is not orig
    assert D.P.ddet is orig
    with pytest.raises(RuntimeError):
        with D.field_priority_ddet([]):
            raise RuntimeError("x")
    assert D.P.ddet is orig     # 例外時も必ず復元


def test_c1_field_priority_story_adds_only_mappable_surfaces():
    facts = "- 売上は167億ドルで、前年比221％増。"
    sf = D.field_priority_surfaces(["167億ドル", "999億ドル", "2025年"], facts, "story")
    assert sf["kept"] == ["167億ドル"] and sf["unmapped"] == ["999億ドル"]       # 年系は対象外・写像できない値はunmapped
    assert D.field_priority_story("元の一文", ["167億ドル"], facts) == "元の一文\n167億ドル"
    assert D.field_priority_story("元の一文", [], facts) == "元の一文"              # 欄が空なら元と同一(E=∅は現行と同じ)


@needs_artifacts
def test_c1_reapply_makes_attempt1_samples_e_ok_and_keeps_finals(tmp_path):
    r = D.reapply_field_priority(os.path.join(SEMI, "r6s1"), str(tmp_path / "s1a1"), attempt1=True)
    assert r["base"]["status"] == "M1_VIOLATION" and r["base"]["violations"][0]["reason"] == "peripheral_number_in_storyline"
    assert r["new"]["status"] == "E_OK" and len(r["new"]["E"]) == 2
    assert any("217" in s for s in r["core_added"])
    # 最終採用側(2回目)は結果が変わらない(回帰なし)
    f = D.reapply_field_priority(os.path.join(SEMI, "r6s1"), str(tmp_path / "s1f"), attempt1=False)
    assert f["base"]["status"] == f["new"]["status"] == "E_OK" and f["core_added"] == [] and f["core_removed"] == []


@needs_artifacts
def test_c1_reapply_does_not_modify_source_sample(tmp_path):
    src = os.path.join(SEMI, "r6s1", "storyline_b3_attempt1", "annotation.json")
    before = hashlib.sha256(open(src, "rb").read()).hexdigest()
    D.reapply_field_priority(os.path.join(SEMI, "r6s1"), str(tmp_path / "x"), attempt1=True)
    assert hashlib.sha256(open(src, "rb").read()).hexdigest() == before


@needs_artifacts
def test_c1_coffee_attempt1_pair_becomes_ok(tmp_path):
    r = D.reapply_field_priority(os.path.join(COFFEE, "r6c2"), str(tmp_path / "c"), attempt1=True)
    assert r["base"]["status"] == "M1_VIOLATION" and r["new"]["status"] == "E_OK"
    assert r["new"]["E"] == ["8.7%", "0.6%"]


@needs_artifacts
def test_c1_unmapped_field_value_still_m1_violation(tmp_path):
    # 欄にFact本文へ写像できない数値があれば、優先化せず従来どおり構造違反(unmapped_to_news_field)のまま
    import shutil as _sh
    src = os.path.join(SEMI, "r6s1")
    dst = str(tmp_path / "u")
    r = D.reapply_field_priority(src, dst, attempt1=True)
    p = os.path.join(dst, "new", "storyline_b3", "reader_must_hear_numbers.json")
    obj = json.load(open(p, encoding="utf-8"))
    obj["items"] = ["167億ドル", "9999億ドル"]
    json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    with D.field_priority_ddet(obj["items"]):
        D.P.produce_annotated_b3(os.path.join(dst, "new"))
    E = D.derive_E_r5(os.path.join(dst, "new"))
    assert not E["ok"] and any(v["reason"] == "unmapped_to_news_field" for v in E["violations"])
    assert r["new"]["status"] == "E_OK"


def test_c3_en_present_times_fold_and_3d():
    assert D.en_present("3倍超", "it holds three times the energy") is True
    assert D.en_present("3倍超", "over 3x more") is True
    assert D.en_present("3倍", "it has three dimensions") is False          # 語数詞の誤一致なし
    assert D.en_present("3倍", "a 3D structure") is False                    # 単位なしの3が3Dに一致しない
    assert D.en_present("3倍", "He has 3 dogs") is False
    assert D.en_present("10 m", "10m away") is True                          # 小文字mは数値+単位として維持
    assert D.en_present("167億ドル", "$16.7 billion") is True               # 既存(億ドル→billion)は不変


def test_c3_en_tokens_exclude_3d():
    import er115_fx_numeric_r5_score_01 as S
    assert S.en_tokens("a 3D crystal, 3 times more, 41%, $16.7 billion, 10 m") == ["3 times", "41%", "$16.7 billion", "10 m"]


def test_c3_comparison_fix_script_idempotent_and_uses_b3_rerun():
    src = open(os.path.join(ROOT, "er115_fx_numeric_r5_comparison_fix_01.py"), encoding="utf-8").read()
    assert "b3_rerun" in src and "rerun=None" in src       # 旧表示を置換する対象としてだけ登場
    md = open(os.path.join(ROOT, "docs", "research", "FX-CORE-NUMERIC-RETENTION-TRIAL-01", "COMPARISON_05.md"), encoding="utf-8").read()
    assert "first_pass_ok=False b3_rerun=True" in md and "first_pass_ok=False rerun=None" not in md


def test_c1_default_off_no_global_flag():
    # 既定OFF: P.ddet は未差替え、er115以外のmoduleがC-1関数を参照しない(Production非接続)
    for p in glob.glob(os.path.join(ROOT, "*.py")):
        base = os.path.basename(p)
        if base.startswith(("er115_", "er116_")) or base.endswith(("_test_01.py", "_test.py")):     # testファイルは許可リストでer115_を名指しするため対象外(Production module判定)。er116_ testは『Productionに移植しない』ことをAST名で検査するため名前を含む
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        assert "field_priority_ddet" not in txt and "reapply_field_priority" not in txt, base
