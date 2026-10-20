# -*- coding: utf-8 -*-
"""eval_ext / tts plan / PRIMARY phase のtest(API 0)。Phase Aのraw 15行+合成行で検証。"""
import json
import os
import re

import pytest

import er084_azure_phraselist_weight_trial_01_lib as L
import er084_azure_phraselist_weight_trial_01_eval_ext as X
import er084_azure_phraselist_weight_trial_01_run as R
import er084_azure_phraselist_weight_trial_01_tts as T

DESIGN_DIR = os.path.join(L.ROOT, "docs", "research", "FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01")
DESIGN = os.path.join(DESIGN_DIR, "design_matrix_01.json")
RAW_A = os.path.join(L.ROOT, "er084_output", "azure_phraselist_weight_trial_01", "raw", "azure_calls.jsonl")
CRIT = X.load_criteria()


def fake_judge(canonical, primary, secondary, wav_path):
    """合成judge: secondaryがcanonicalと語一致ならPASS系、他はNG。"""
    ok = X._tok(canonical) == X._tok(secondary)
    return {"state": "PASS" if ok else "NG_BOTH"}


def row(aid, cond, rep, text):
    return {"audio_id": aid, "cond": cond, "rep": rep, "text": text, "err": None}


# ---- (a)(b) perturbation ----
def test_perturbation_excludes_target_diffs_and_counts_other_words():
    p = X.perturbation("He got onto his knees. Melos drank.", "He got unto his knees. Mellows drank.")
    assert p["n_target_diffs"] == 1
    assert p["n_other_diff_words"] == 1 and p["other_diffs"] == ["onto→unto"]
    assert p["protected_impact"] is False


def test_perturbation_protected_number_and_negation():
    p = X.perturbation("Melos did not take two steps.", "Melos did take three steps.")
    assert p["protected_impact"] is True
    assert p["number_mismatches"] or p["negation_mismatches"]


def test_perturbation_confusable_word_is_target_for_negatives():
    p = X.perturbation("Milos drank slowly.", "Melos drank slowly.", confusable="Milos")
    assert p["n_target_diffs"] == 1 and p["n_other_diff_words"] == 0


def test_phase_a_raw_perturbation_by_condition():
    if not os.path.exists(RAW_A):
        pytest.skip("Phase A raw無し")
    rows = [r for r in L.read_raw(RAW_A) if r.get("phase") == "A"]  # 委任_02b以降はPhase Bの行も同一rawに追記される
    assert len(rows) == 15
    d = json.load(open(DESIGN, encoding="utf-8"))
    a = d["phases"]["A"]["audio"][0]
    meta = {a["id"]: {"label": "positive", "canonical_text": a["canonical_text"], "expected_melos": 1}}
    pr = X.perturbation_rows(rows, meta)
    assert len(pr) == 15
    by = X.perturbation_by_condition(pr, "pl_unspecified")
    assert set(by) == set(L.COND_NAMES)
    assert by["pl_unspecified"]["delta_vs_baseline"] == 0
    # 設計書/Phase A実測: w2.0で onto->unto の他語perturbationが出る(baselineより増える)
    assert by["pl_w2.0"]["other_diff_words"] > by["pl_unspecified"]["other_diff_words"]
    assert any("onto→unto" in p["other_diffs"] for p in pr if p["cond"] == "pl_w2.0")


# ---- (c) negatives ----
def _meta():
    m = {}
    for i in range(6):  # 正例6wav(R>=6を作る)
        m[f"P{i}"] = {"label": "positive", "canonical_text": "Melos spoke today.", "text": "Melos spoke today.",
                      "expected_melos": 1, "primary_text": "Mello spoke today.", "path": "x.wav",
                      "sentence_id": f"S{i % 3}", "voice": "Aoede" if i < 4 else "Charon", "slow6": i == 1}
    m["N1"] = {"label": "negative", "canonical_text": "The Melos sound.", "text": "The mellow sound.", "expected_melos": 1,
               "primary_text": "The mellow sound.", "path": "x.wav", "confusable": "mellow", "sentence_id": "N1",
               "voice": "Aoede", "slow6": False}
    return m


def _rows(fixed_n=4, neg_false_w=0, base_neg=0, degrade=False):
    rows = []
    for i in range(6):
        for rep in (1, 2):
            rows.append(row(f"P{i}", "pl_unspecified", rep, "Mello spoke today."))
            rows.append(row(f"P{i}", "no_pl", rep, "Mello spoke today."))
            rows.append(row(f"P{i}", "pl_w1.0", rep, "Mello spoke today."))
            rows.append(row(f"P{i}", "pl_w1.5", rep, "Melos spoke today." if i < fixed_n else "Mello spoke today."))
            rows.append(row(f"P{i}", "pl_w2.0", rep, "Mello spoke today."))
    for cond, n in (("pl_unspecified", base_neg), ("pl_w1.5", neg_false_w), ("pl_w2.0", 0), ("no_pl", 0), ("pl_w1.0", 0)):
        rows.append(row("N1", cond, 1, "The Melos sound." if n else "The mellow sound."))
    return rows


def test_negatives_false_melos_and_false_pass():
    s = X.negatives_summary(_rows(neg_false_w=1), _meta(), CRIT, fake_judge)
    assert s["pl_w1.5"]["false_melos"] == 1 and s["pl_w1.5"]["false_pass"] == 1  # canonical=Melos文なので誤PASS
    assert s["pl_unspecified"]["false_melos"] == 0


def test_negative_judge_unavailable_when_no_primary():
    m = _meta()
    m["N1"]["primary_text"] = None
    s = X.negatives_summary(_rows(neg_false_w=1), m, CRIT, fake_judge)
    assert s["pl_w1.5"]["judge_unavailable"] == 1 and s["pl_w1.5"]["false_pass"] == 0


# ---- (d) criteria ----
def test_criteria_validated_candidate():
    ev = X.evaluate_criteria(_rows(fixed_n=4), _meta(), CRIT, fake_judge)
    w = ev["per_weight"]["pl_w1.5"]
    assert ev["R"] == 6 and w["fixed"] == 4
    assert w["criteria"] == {"1_fixed": True, "2_neg_not_increased": True, "3_degraded": True, "4_reproduced": True,
                             "5_judge_ng_to_pass": True}
    assert w["status"] == "VALIDATED候補" and ev["status"] == "VALIDATED候補"
    assert ev["per_weight"]["pl_w2.0"]["status"] == "REJECTED"


def test_criteria_rejected_when_fixed_below_min():
    ev = X.evaluate_criteria(_rows(fixed_n=2), _meta(), CRIT, fake_judge)
    assert ev["per_weight"]["pl_w1.5"]["status"] == "REJECTED"
    assert ev["status"] == "REJECTED"


def test_criteria_tradeoff_negative_increase_is_decision_candidate():
    ev = X.evaluate_criteria(_rows(fixed_n=4, neg_false_w=1), _meta(), CRIT, fake_judge)
    w = ev["per_weight"]["pl_w1.5"]
    assert w["criteria"]["2_neg_not_increased"] is False and w["status"] == "判断候補"


def test_criteria_inconclusive_when_R_below_min():
    m = _meta()
    rows = [r for r in _rows() if r["audio_id"] in ("P0", "P1", "P2", "N1")]
    ev = X.evaluate_criteria(rows, m, CRIT, fake_judge)
    assert ev["R"] == 3 and ev["status"] == "INCONCLUSIVE"


def test_criteria_unstable_wav_not_counted_as_fixed():
    rows = _rows(fixed_n=4)
    for r in rows:  # P0のw1.5をrep2だけ誤認識=不安定
        if r["audio_id"] == "P0" and r["cond"] == "pl_w1.5" and r["rep"] == 2:
            r["text"] = "Mello spoke today."
    ev = X.evaluate_criteria(rows, _meta(), CRIT, fake_judge)
    w = ev["per_weight"]["pl_w1.5"]
    assert w["fixed"] == 3 and "P0" in w["unstable_in_R"]


def test_criteria_degraded_counts_as_worse():
    rows = _rows(fixed_n=4)
    meta = _meta()
    for r in rows:  # P5はbaselineで全rep正認識、w1.5では誤認識に
        if r["audio_id"] == "P5" and r["cond"] == "pl_unspecified":
            r["text"] = "Melos spoke today."
    ev = X.evaluate_criteria(rows, meta, CRIT, fake_judge)
    assert ev["per_weight"]["pl_w1.5"]["degraded"] == 1
    assert ev["R"] == 5  # P5がRから抜ける


def test_thresholds_not_hardcoded_in_source():
    src = open(os.path.join(L.ROOT, "er084_azure_phraselist_weight_trial_01_eval_ext.py"), encoding="utf-8").read()
    assert "0.30" not in src and "0.3333" not in src and ">= 6" not in src
    assert re.search(r"criteria\[\"fixed_min_abs\"\]", src)


def test_criteria_json_matches_design_document():
    md = open(os.path.join(DESIGN_DIR, "TRIAL_DESIGN_01.md"), encoding="utf-8").read()
    assert "R≥6" in md or "R≥ 6" in md or "R >= 6" in md
    assert "fixed ≥ 3" in md and "0.30×R" in md and "1/3" in md and "増加0" in md
    assert CRIT["min_R_for_identifiability"] == 6 and CRIT["fixed_min_abs"] == 3
    assert CRIT["fixed_min_fraction_of_R"] == 0.30 and CRIT["negative_false_melos_increase_max"] == 0
    assert CRIT["degraded_max_abs"] == 1 and CRIT["min_contexts_sentences"] == 2 and CRIT["min_voice_speed_conditions"] == 2
    assert CRIT["baseline_cond"] == "pl_unspecified" and CRIT["candidate_conds"] == ["pl_w1.5", "pl_w2.0"]


# ---- TTS plan (W1) ----
def test_tts_plan_counts_match_design():
    plan = T.build_plan(json.load(open(DESIGN, encoding="utf-8")))
    assert (plan["n_tts"], plan["n_slow"], plan["n_wav"]) == (28, 14, 42)
    ids = [e["id"] for e in plan["takes"] + plan["slows"]]
    assert len(ids) == len(set(ids)) == 42
    neg = [e for e in plan["takes"] if e["label"] == "negative"]
    assert len(neg) == 8 and all("Melos" in e["canonical_text"] and e["expected_melos"] == 1 for e in neg)
    n4 = [e for e in neg if e["sentence_id"] == "N4_milos"][0]
    assert n4["canonical_text"] == "Melos drank slowly from the cup."
    assert sum(1 for e in plan["slows"] if e["sentence_id"] == "P1_nonsib") == 4
    assert all(e["voice"] == "Aoede" for e in plan["slows"])


def test_tts_main_refuses_without_standard_env(monkeypatch):
    monkeypatch.delenv("TTS_EXECUTION_MODE", raising=False)
    assert T.main(["--design", DESIGN, "--out", "x", "--budget-jpy", "15", "--tts-execution-mode", "STANDARD"]) == 2


def test_tts_dry_run_makes_no_api_call(monkeypatch, capsys):
    monkeypatch.setenv("TTS_EXECUTION_MODE", "STANDARD")
    monkeypatch.setattr(T, "generate_take", lambda *a, **k: (_ for _ in ()).throw(AssertionError("API呼出禁止")))
    assert T.main(["--design", DESIGN, "--out", "x", "--budget-jpy", "15", "--tts-execution-mode", "STANDARD", "--dry-run"]) == 0
    assert '"n_wav": 42' in capsys.readouterr().out


# ---- PRIMARY phase (W2): Azureを呼ばない・既記録は再呼出ししない ----
def test_primary_phase_never_calls_azure_and_skips_done(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "azure_transcribe", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Azure呼出禁止")))
    wav = tmp_path / "a.wav"
    import wave
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(b"\x00\x00" * 2400)
    info = L.wav_info(str(wav))
    monkeypatch.setattr(R, "ROOT", str(tmp_path))
    man = {"audio": [{"id": "a1", "path": "a.wav", "sha256": info["sha256"]}]}
    calls = []
    r1 = R.run_primary(man, str(tmp_path / "o"), 1.0, transcribe_fn=lambda p: (calls.append(p) or ("Melos", None)))
    r2 = R.run_primary(man, str(tmp_path / "o"), 1.0, transcribe_fn=lambda p: (calls.append(p) or ("X", None)))
    assert r1["n_called"] == 1 and r2["n_called"] == 0 and r2["n_skipped_existing"] == 1 and len(calls) == 1
    rows = L.read_raw(str(tmp_path / "o" / "raw" / "primary_calls.jsonl"))
    assert len(rows) == 1 and rows[0]["text"] == "Melos"


def test_primary_phase_sha_mismatch_aborts(tmp_path, monkeypatch):
    wav = tmp_path / "a.wav"
    import wave
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(b"\x00\x00" * 2400)
    monkeypatch.setattr(R, "ROOT", str(tmp_path))
    with pytest.raises(SystemExit):
        R.run_primary({"audio": [{"id": "a1", "path": "a.wav", "sha256": "0" * 64}]}, str(tmp_path / "o"), 1.0,
                      transcribe_fn=lambda p: ("x", None))


def test_manifest_fixed_wavs_match_sha_if_present():
    mp = os.path.join(L.ROOT, "er084_output", "azure_phraselist_weight_trial_01", "wav", "manifest_01.json")
    if not os.path.exists(mp):
        pytest.skip("manifest無し")
    m = json.load(open(mp, encoding="utf-8"))
    assert m["n_audio"] == len(m["audio"]) == 42
    for a in m["audio"]:
        assert L.wav_info(os.path.join(L.ROOT, a["path"]))["sha256"] == a["sha256"]
