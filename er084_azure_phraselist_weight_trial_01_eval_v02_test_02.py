# -*- coding: utf-8 -*-
"""eval_v02 / Phase B v02 runner / prodtakes / tts v02 のtest(API 0、judgeはfake)。"""
import json
import os

import pytest

import er084_azure_phraselist_weight_trial_01_eval_v02 as E
import er084_azure_phraselist_weight_trial_01_lib as L
import er084_azure_phraselist_weight_trial_01_prodtakes as PT
import er084_azure_phraselist_weight_trial_01_run as R
import er084_azure_phraselist_weight_trial_01_tts as T

D = os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01")
CRIT = json.load(open(os.path.join(D, "criteria_thresholds_01.json"), encoding="utf-8"))
DESIGN = json.load(open(os.path.join(D, "design_matrix_01.json"), encoding="utf-8"))
CANON = "Then Melos walked away."


def fake_judge(canonical, primary, secondary, wav_path, segment_id):
    if secondary is None:
        return {"state": "PASS" if "Melos" in (primary or "") else "NG_SECONDARY_UNAVAILABLE"}
    if "Melos" in (primary or ""):
        return {"state": "PASS"}
    return {"state": "PASS_WITH_WARNING" if "Melos" in secondary else "NG_BOTH"}


def mk_meta(aid, set_name="POS_SYN", sent=None, voice="Aoede", slow=False, primary="Then Mello walked away.", canon=CANON,
            text=None, label=None):
    return {"id": aid, "set": set_name, "label": label or ("positive" if set_name.startswith("POS") else "negative"),
            "canonical_text": canon, "text": text or canon, "primary_text": primary, "segment_id": "full_story_part1_c1",
            "voice": voice, "slow6": slow, "sentence_id": sent or aid, "path": "x.wav", "duration_s": 3.0, "confusable": None,
            "ledger_phrases": ["Melos"], "expected_melos": 1 if "Melos" in canon else 0}


def mk_row(aid, cond, text, rep=1):
    return {"phase": "B", "audio_id": aid, "cond": cond, "rep": rep, "text": text, "err": None}


def scenario(n_pos=8, up=6, down=0, same_cluster=False, neg_fp_w15=0, neg_n=6):
    meta, rows = {}, []
    voices = ["Aoede", "Charon", "Aoede"]
    for i in range(n_pos):
        aid = f"P{i}"
        meta[aid] = mk_meta(aid, sent=("S0" if same_cluster else f"S{i % 4}"), voice=("Aoede" if same_cluster else voices[i % 3]),
                            slow=(False if same_cluster else i % 2 == 1))
        base_pass = i < down  # downの数だけベースラインPASS
        rows.append(mk_row(aid, "no_pl", "Then Mellows walked away."))
        rows.append(mk_row(aid, "pl_unspecified", "Then Melos walked away." if base_pass else "Then Mellows walked away."))
        w15_pass = (i < up) if not base_pass else False
        rows.append(mk_row(aid, "pl_w1.5", "Then Melos walked away." if w15_pass else "Then Mellows walked away."))
        rows.append(mk_row(aid, "pl_w2.0", "Then Mellows walked away."))
    for j in range(neg_n):
        aid = f"N{j}"
        meta[aid] = mk_meta(aid, "NEG_MP", primary="Then Mello walked away.", text="Then Mello walked away.")
        for c in ("no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0"):
            t = "Then Melos walked away." if (c == "pl_w1.5" and j < neg_fp_w15) else "Then Mello walked away."
            rows.append(mk_row(aid, c, t))
    return meta, rows


def run(meta, rows):
    return E.run_eval(rows, meta, CRIT, fake_judge)


def test_sign_test_values():
    assert E.sign_test_p(5, 0) == pytest.approx(1 / 32)
    assert E.sign_test_p(3, 0) == pytest.approx(0.125)
    assert E.sign_test_p(7, 1) == pytest.approx(9 / 256)
    assert E.sign_test_p(9, 2) == pytest.approx(67 / 2048)
    assert E.sign_test_p(0, 0) == 1.0
    assert E.rule_of_three_upper(33, 0) == pytest.approx(3 / 33) and E.rule_of_three_upper(33, 1) is None


def test_validated_candidate():
    ev, ov, _ = run(*scenario(n_pos=8, up=6))
    w = ov["weights"]["pl_w1.5"]
    assert ov["R"] == 8 and w["roles"]["full_story"]["up"] == 6 and w["roles"]["full_story"]["down"] == 0
    assert w["criteria"] == {"1_identifiable": True, "2_effect": True, "3_sign_test": True, "4_spread": True,
                             "5_no_side_effect": True, "6_no_degradation": True, "7_tier3less_not_reversed": True}
    assert ov["status"] == "VALIDATED候補"


def test_inconclusive_when_R_below_6_takes_priority_over_rejected():
    ev, ov, _ = run(*scenario(n_pos=5, up=0))
    assert ov["R"] == 5 and ov["status"] == "INCONCLUSIVE"


def test_rejected_when_effect_too_small():
    ev, ov, _ = run(*scenario(n_pos=8, up=2))
    assert ov["weights"]["pl_w1.5"]["status"] == "REJECTED" and ov["status"] == "REJECTED"


def test_inconclusive_when_sign_test_not_significant():
    ev, ov, _ = run(*scenario(n_pos=8, up=3))  # 3:0 -> p=0.125
    w = ov["weights"]["pl_w1.5"]
    assert w["criteria"]["2_effect"] is True and w["criteria"]["3_sign_test"] is False and ov["status"] == "INCONCLUSIVE"


def test_tradeoff_negative_false_pass_increase_is_decision_candidate():
    ev, ov, _ = run(*scenario(n_pos=8, up=6, neg_fp_w15=1))
    w = ov["weights"]["pl_w1.5"]
    assert w["criteria"]["5_no_side_effect"] is False and ov["status"] == "判断候補"
    assert w["neg_false_pass_increase"] == {"full_story": 1, "no_tier3": 1} and w["neg_false_melos_increase"] == 1


def test_not_spread_over_clusters_is_decision_candidate():
    ev, ov, _ = run(*scenario(n_pos=8, up=6, same_cluster=True))
    assert ov["weights"]["pl_w1.5"]["criteria"]["4_spread"] is False and ov["status"] == "判断候補"


def test_primary_pass_wav_excluded_from_flip():
    meta, rows = scenario(n_pos=8, up=6)
    meta["P0"]["primary_text"] = CANON  # Primary PASS
    ev, ov, _ = run(meta, rows)
    r = ov["weights"]["pl_w1.5"]["roles"]["full_story"]
    assert r["primary_pass_excluded"] == 1 and r["up"] == 5 and ov["R"] == 7


def test_unstable_wav_excluded_not_counted_up():
    meta, rows = scenario(n_pos=8, up=6)
    rows.append(mk_row("P0", "pl_w1.5", "Then Mellows walked away.", rep=2))  # rep1=PASS/rep2=NG -> 不安定
    ev, ov, _ = run(meta, rows)
    r = ov["weights"]["pl_w1.5"]["roles"]["full_story"]
    assert "P0" in r["unstable"] and r["up"] == 5


def test_down_counts_as_degradation_and_tier3less_reversal():
    ev, ov, _ = run(*scenario(n_pos=14, up=11, down=2))
    w = ov["weights"]["pl_w1.5"]
    assert w["roles"]["full_story"]["down"] == 2 and w["criteria"]["6_no_degradation"] is False
    assert ov["status"] == "判断候補"


def test_other_word_perturbation_and_protected():
    ref = "He did not trust Melos at the gate by 5 pm."
    base = E.other_diffs(ref, "He did not trust Mellows at the gate by 5 pm.")
    w = E.other_diffs(ref, "He did trust Mellows at the gate by 6 pm.")
    assert base == []  # Melos位置の差分のみ→他語perturbationなし
    ne = E.new_errors(base, w)
    assert ne["n_new_diffs"] == 2 and set(ne["protected_kinds"]) >= {"negation", "number"}
    assert ne["melos_dists"] and all(d is not None for d in ne["melos_dists"])
    # 機能語のみの揺れ(onto->unto)は保護対象でない
    ne2 = E.new_errors([], E.other_diffs("He got onto his knees.", "He got unto his knees."))
    assert ne2["n_new_diffs"] == 1 and ne2["protected_kinds"] == []


def test_boundary_and_diagnosis_flags_present():
    meta, rows = scenario(n_pos=8, up=6)
    meta["B1"] = mk_meta("B1", "NEG_BOUNDARY", primary="Then Milos walked away.", text="Then Milos walked away.")
    for c in ("no_pl", "pl_unspecified", "pl_w1.5", "pl_w2.0"):
        rows.append(mk_row("B1", c, "Then Melos walked away." if c == "pl_w2.0" else "Then Milos walked away."))
    ev, ov, ex = run(meta, rows)
    b = ex["boundary"][("full_story", "pl_w2.0")]
    assert b["n"] == 1 and b["melos"] == ["B1"] and b["pass"] == ["B1"]
    assert set(ex["diagnosis"]["flags"]) == {"a_条件が簡単すぎた", "b_PLが効いていない", "c_1.0(現行)で既に十分", "d_文脈・音声品質で変わる", "e_重みでは解決できない"}
    # 境界例は有効負例の分母・判定に影響しない
    assert ov["weights"]["pl_w1.5"]["negatives_detail"]["full_story|pl_w1.5"]["n"] == 6


def test_all_rows_counted_err_separate():
    meta, rows = scenario(n_pos=8, up=6)
    rows.append({"phase": "B", "audio_id": "P0", "cond": "pl_w2.0", "rep": 3, "text": None, "err": "boom"})
    ev, _, _ = run(meta, rows)
    assert sum(ev.n_err.values()) == 1 and len(ev.rows) == len(rows)  # errも行としては保持


def test_thresholds_not_hardcoded_in_eval_v02():
    src = open(os.path.join(L.ROOT, "er084_azure_phraselist_weight_trial_01_eval_v02.py"), encoding="utf-8").read()
    assert "0.30" not in src and "0.05" not in src and "0.025" not in src and "== 33" not in src
    assert 'crit["fixed_min_abs"]' in src and 'v["alpha_primary"]' in src


# ---- Phase B v02 runner ----
M1 = os.path.join(L.ROOT, "er084_output", "azure_phraselist_weight_trial_01", "wav", "manifest_01.json")
M2 = os.path.join(L.ROOT, "er084_output", "azure_phraselist_weight_trial_01", "wav", "manifest_02.json")
PROD = os.path.join(L.ROOT, "er084_output", "azure_phraselist_weight_trial_01", "production_takes_manifest_01.json")


@pytest.mark.skipif(not (os.path.exists(M1) and os.path.exists(M2) and os.path.exists(PROD)), reason="manifest未生成")
def test_phase_b_v02_call_counts_and_spot_rule():
    m1, m2, prod = [json.load(open(p, encoding="utf-8")) for p in (M1, M2, PROD)]
    calls = R.build_calls_v02(DESIGN, m1, m2, prod)
    n_wav = len(m1["audio"]) + len(m2["audio"]) + len(prod["audio"])
    assert (len(m1["audio"]), len(m2["audio"]), len(prod["audio"])) == (42, 27, 20) and n_wav == 89
    spot = {c["audio_id"] for c in calls if c["spot"]}
    assert len(spot) == 9
    assert len(calls) == 89 * 4 + 9 + 9 * 5  # 4条件rep1 + w1.0 rep1(抜き打ち) + rep2(5条件)
    assert all(c["duration_s_expected"] <= 10.0 for c in calls if c["spot"])
    assert not [c for c in calls if c["cond"] == "pl_w1.0" and not c["spot"]]
    assert not [c for c in calls if c["rep"] == 2 and not c["spot"]]
    # 抜き打ちは結果非依存の決定論(再計算で同一)
    assert set(R.build_calls_v02(DESIGN, m1, m2, prod) and {c["audio_id"] for c in R.build_calls_v02(DESIGN, m1, m2, prod) if c["spot"]}) == spot
    # PL: 本番takeはledger_phrases、合成はdesign phrase_list
    assert all(c["phrases"] == ["Melos"] for c in calls)
    assert {c["set"] for c in calls} == {"POS_SYN", "POS_PROD", "NEG_VALID", "NEG_BOUNDARY", "NEG_MP"}
    est = R.estimate_v02(calls)
    assert est["n_calls"] == len(calls) and est["est_jpy"] < 170


def test_phase_b_v02_blocked_when_golden_gate_fails(monkeypatch, tmp_path):
    called = []
    monkeypatch.setattr(R, "golden_gate_ok", lambda: False)
    monkeypatch.setattr(L, "azure_transcribe", lambda *a, **k: called.append(1))
    if not (os.path.exists(M1) and os.path.exists(M2) and os.path.exists(PROD)):
        pytest.skip("manifest未生成")
    rc = R.main(["--design", os.path.join(D, "design_matrix_01.json"), "--manifest", M1, "--manifest2", M2, "--production-takes", PROD,
                 "--phase", "B", "--out", str(tmp_path), "--budget-jpy", "170"])
    assert rc == 6 and called == [] and not (tmp_path / "raw").exists()


def test_phase_b_v02_dry_run_no_write_and_budget_guard(tmp_path, capsys):
    if not (os.path.exists(M1) and os.path.exists(M2) and os.path.exists(PROD)):
        pytest.skip("manifest未生成")
    args = ["--design", os.path.join(D, "design_matrix_01.json"), "--manifest", M1, "--manifest2", M2, "--production-takes", PROD,
            "--phase", "B", "--out", str(tmp_path)]
    assert R.main(args + ["--budget-jpy", "170", "--dry-run"]) == 0
    assert not (tmp_path / "raw").exists()
    assert R.main(args + ["--budget-jpy", "10", "--dry-run"]) == 2


def test_done_keys_skip_existing_paid_calls(tmp_path):
    raw = tmp_path / "azure_calls.jsonl"
    L.append_raw(str(raw), {"phase": "B", "audio_id": "a", "cond": "no_pl", "rep": 1, "err": None})
    L.append_raw(str(raw), {"phase": "B", "audio_id": "a", "cond": "pl_w1.5", "rep": 1, "err": "x"})
    L.append_raw(str(raw), {"phase": "A", "audio_id": "rec", "cond": "no_pl", "rep": 1, "err": None})
    assert R.done_keys(str(raw)) == {("a", "no_pl", 1)}


# ---- prodtakes selection rule ----
def _c(seg, canon_sha, sha, dur, text="Melos x."):
    return {"segment_id": seg, "canon_sha12": canon_sha, "sha256": sha, "duration_s": dur, "canonical_text": text * 1,
            "json": "j", "wav": "w", "run": "r", "level": "a2", "attempt": 1, "route": "r", "voice": "Aoede", "model": "m",
            "primary_text": "p", "clip_kind": "narrator"}


def test_prodtakes_selection_rule_dedup_representative_and_caps():
    cands = [_c("segA", "c1", "s2", 3.0), _c("segA", "c1", "s1", 3.5), _c("segA", "c1", "s1", 3.5),  # sha重複除外、代表=sha最小s1
             _c("segA", "c2", "s9", 2.0, "Melos longer text here."), _c("segB", "c3", "s5", 100.0)]
    sel = PT.select(cands, max_takes=20, max_seconds=500)
    ids = {(s["canon_sha12"], s["sha256"]) for s in sel}
    assert ("c1", "s1") in ids and ("c1", "s2") not in ids  # 1文1代表(sha昇順最小)
    assert sel[0]["canon_sha12"] == "c1" and sel[0]["selection"]["n_ng_takes_in_group"] == 2 and sel[0]["selection"]["round"] == 1
    assert [s["segment_id"] for s in sel[:2]] == ["segA", "segB"]  # 第1巡=segment名昇順
    capped = PT.select(cands, max_takes=2, max_seconds=500)
    assert len(capped) == 2
    cap_s = PT.select(cands, max_takes=20, max_seconds=50)
    assert [s["canon_sha12"] for s in cap_s][-1] != "c3"  # 500秒(ここでは50秒)超は打切り


@pytest.mark.skipif(not os.path.exists(PROD), reason="manifest未生成")
def test_production_takes_manifest_matches_rule_and_sha():
    m = json.load(open(PROD, encoding="utf-8"))
    assert m["n_audio"] == len(m["audio"]) == 20 and m["total_seconds"] <= 500
    for a in m["audio"]:
        assert L.wav_info(os.path.join(L.ROOT, a["path"]))["sha256"] == a["sha256"]
        assert a["ledger_phrases"] == ["Melos"] and len(L.RE_MELOS.findall(a["primary_text"])) != a["expected_melos"]
    assert len({a["sentence_id"] for a in m["audio"]}) == 20  # 1文1take


# ---- tts v02 plan ----
def test_tts_plan_v02_counts_and_canonical_is_original_melos_sentence():
    plan = T.build_plan_v02(DESIGN)
    assert (plan["n_tts"], plan["n_slow"], plan["n_wav"]) == (18, 9, 27)
    ids = [e["id"] for e in plan["takes"] + plan["slows"]]
    assert len(set(ids)) == 27
    for e in plan["takes"] + plan["slows"]:
        assert e["label"] == "negative" and e["canonical_text"].count("Melos") == 1 and "Melos" not in e["text"]
    e = [x for x in plan["takes"] if x["id"] == "NM_P3_mullos_Charon_take1"][0]
    assert e["text"] == "The man waiting at the gate was Mullos." and e["canonical_text"] == "The man waiting at the gate was Melos."
    assert all(x["voice"] == "Aoede" for x in plan["slows"])


def test_tts_v02_dry_run_no_api_and_requires_standard(monkeypatch, capsys):
    dm = os.path.join(D, "design_matrix_01.json")
    monkeypatch.delenv("TTS_EXECUTION_MODE", raising=False)
    assert T.main(["--design", dm, "--out", "x", "--budget-jpy", "6", "--tts-execution-mode", "STANDARD", "--only-group", "negatives_v02"]) == 2
    monkeypatch.setenv("TTS_EXECUTION_MODE", "STANDARD")
    monkeypatch.setattr(T, "generate_take", lambda *a, **k: (_ for _ in ()).throw(AssertionError("API呼出禁止")))
    assert T.main(["--design", dm, "--out", "x", "--budget-jpy", "6", "--tts-execution-mode", "STANDARD", "--only-group",
                   "negatives_v02", "--dry-run"]) == 0
    assert '"n_wav": 27' in capsys.readouterr().out
    assert T.main(["--design", dm, "--out", "x", "--budget-jpy", "3", "--tts-execution-mode", "STANDARD", "--only-group",
                   "negatives_v02", "--dry-run"]) == 2


@pytest.mark.skipif(not os.path.exists(M2), reason="manifest未生成")
def test_manifest_02_fixed_wavs_sha_and_reclassification():
    m = json.load(open(M2, encoding="utf-8"))
    assert m["n_audio"] == len(m["audio"]) == 27 and set(m["reclassification"]) == {"N2_mellows", "N4_milos"}
    for a in m["audio"]:
        assert L.wav_info(os.path.join(L.ROOT, a["path"]))["sha256"] == a["sha256"]
        assert a["label"] == "negative" and a["negative_kind"] == "minimal_pair" and a["canonical_text"].count("Melos") == 1
