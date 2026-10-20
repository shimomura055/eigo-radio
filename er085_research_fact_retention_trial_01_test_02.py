# -*- coding: utf-8 -*-
"""XRFR 委任_02 検索込み腕/判定機械のtest(API 0)。"""
import copy
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er085_research_fact_retention_trial_01_lib as lib  # noqa: E402
import er085_research_fact_retention_trial_01_search_arm as sa  # noqa: E402
import er085_research_fact_retention_trial_01_eval as ev  # noqa: E402


def test_patched_prompts_restore_and_diff_only():
    v = lib._vfl01()
    o_r, o_v = v.build_researcher_prompt, v.build_verification_prompt
    topic = "中東情勢が悪化、イエメン・サウジ周辺で攻撃続く"
    base = o_r(topic=topic)
    led = {"facts": [{"fact_id": "F01"}]}
    vbase = o_v(topic, led)
    with sa.patched_prompts("E0") as vv:
        assert vv.build_researcher_prompt(topic=topic) == base           # E0: Prompt不変
        assert vv.build_verification_prompt(topic, led) == vbase
    with sa.patched_prompts("A") as vv:
        a = vv.build_researcher_prompt(topic=topic)
        assert a != base and a.replace(lib.A_INSERT.rstrip("\n"), "", 1) == base   # 差分=第5・6観点の挿入のみ
        assert vv.build_verification_prompt(topic, led) == vbase                  # Aの検証は不変
    with sa.patched_prompts("D") as vv:
        d = vv.build_verification_prompt(topic, led)
        assert d != vbase and d.replace("\n" + lib.VC_LINE, "", 1) == vbase       # 差分=VC_LINE 1行のみ
        assert vv.build_researcher_prompt(topic=topic) == a                      # DのResearcherはAと同一
    assert v.build_researcher_prompt is o_r and v.build_verification_prompt is o_v  # 必ず復元
    try:
        with sa.patched_prompts("D"):
            raise RuntimeError("x")
    except RuntimeError:
        pass
    assert v.build_researcher_prompt is o_r and v.build_verification_prompt is o_v  # 例外時も復元


def test_production_does_not_reference_trial_code():
    r = subprocess.run(["git", "grep", "-l", "er085_research_fact_retention", "--", "*.py"], cwd=ROOT, capture_output=True, text=True)
    assert all(os.path.basename(x).startswith("er085_") for x in r.stdout.split())


def test_dryrun_search_arm_api0_and_output_isolated():
    out = os.path.join(lib.OUT_ROOT, "search_arm_test_tmp")
    shutil.rmtree(out, ignore_errors=True)
    try:
        rc = sa.main(["--variants", "E0,A,D", "--topic", "mey", "--samples", "1", "--out", out, "--dry-run"])
        assert rc == 0
        d = os.path.join(out, "_dryrun")
        for v in ("E0", "A", "D"):
            s = lib.read_json(os.path.join(d, v, "mey", "s1", "summary.json"))
            assert s["research_web_search_calls"] == 3 and s["dry_run"] is True
        assert os.path.exists(os.path.join(d, "D", "mey", "s1", "verification.json"))
        assert not os.path.exists(os.path.join(d, "E0", "mey", "s1", "verification.json"))   # 検証はDのみ
        names = [f for _, _, fs in os.walk(out) for f in fs]
        assert "raw_usage_log.jsonl" not in names and not any(n.startswith("cost_log") for n in names)
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_out_root_guard():
    try:
        sa.main(["--variants", "E0", "--out", os.path.join(ROOT, "docs"), "--dry-run"])
        assert False
    except RuntimeError:
        pass


def test_score_cell_positive_negative():
    gold = lib.read_json(os.path.join(lib.DOC_DIR, "gold_02.json"))["topics"]["mey"]["items"]
    src = {"http://s/1": ("Statement. The latest attack on Riyadh airport by Ansar Allah killed 12 people. "
                          "Ansar Allah advances on Mokha and the coast along the Bab al-Mandab raised threats in the Red Sea. " * 3)}
    summ = {"cited_urls_draft": ["http://s/1"], "cited_urls_annotations": []}
    led_ok = ("[VERIFIED] F01: アンサール・アッラー(フーシ派)がリヤド空港を攻撃し12人が死亡した\n\n"
              "[VERIFIED] F02: フーシ派は紅海・バブ・アル・マンデブ沿岸で前進し商船への脅威が増した\n")
    draft_ok = {"facts": [{"fact_id": "F01", "claim": "アンサール・アッラーがリヤド空港を攻撃"}]}
    r = sa.score_cell(summ, led_ok, draft_ok, src, gold)
    assert r["items"]["SA"]["expected"] and r["items"]["SA"]["retained_ledger"]
    assert r["items"]["SC"]["expected"] and r["items"]["SC"]["retained_ledger"]
    led_ng = "[VERIFIED] F01: リヤド空港が攻撃され12人が死亡した\n"                      # 脱落(受動形): 主体なし
    r2 = sa.score_cell(summ, led_ng, {"facts": [{"fact_id": "F01", "claim": "リヤド空港が攻撃された"}]}, src, gold)
    assert r2["items"]["SA"]["expected"] and not r2["items"]["SA"]["retained_ledger"]
    assert r2["items"]["SC"]["expected"] and not r2["items"]["SC"]["retained_ledger"]
    src3 = {"http://s/1": "Weather in Riyadh was sunny. " * 50}                          # 出典に明示なし -> 保持を要求しない
    r3 = sa.score_cell(summ, led_ng, {"facts": []}, src3, gold)
    assert not r3["items"]["SA"]["expected"] and not r3["items"]["SC"]["expected"]
    r4 = sa.score_cell(summ, led_ok, draft_ok, {}, gold)                                 # 取得不能出典はexpectedに含めない
    assert r4["n_cited_available"] == 0 and not r4["items"]["SA"]["expected"]


def test_html_to_text():
    t = sa.html_to_text("<html><head><title>x</title></head><body><script>var a=1;</script><p>Ansar &amp; Allah</p><div>Red Sea</div></body></html>")
    assert "Ansar & Allah" in t and "var a" not in t and "Red Sea" in t


def _topic(key, ctrl=1.0, d=0.0, unsupp=0, unadj=0, calls=2):
    return {"key_ledger": key, "ctrl_ledger": ctrl, "delta_facts_vs_E0": d, "fabrication_unsupported": unsupp,
            "flags_unadjudicated": unadj, "schema_errors": 0, "mean_llm_calls": calls}


def test_verdict_machine():
    base = {"mey": _topic(0.75), "muse": _topic(0.8), "coffee": _topic(0.95)}
    good = {"mey": _topic(0.917, d=1.0), "muse": _topic(0.95), "coffee": _topic(0.95)}
    assert ev.classify_variant("A", good, base)["label"] == "VALIDATED_CANDIDATE_PENDING_SEARCH_ARM"
    bad = copy.deepcopy(good)
    bad["mey"]["fabrication_unsupported"] = 1
    assert ev.classify_variant("A", bad, base)["label"] == "REJECTED"
    un = copy.deepcopy(good)
    un["muse"]["flags_unadjudicated"] = 1
    assert ev.classify_variant("A", un, base)["label"] == "NOT_FINALIZABLE_UNADJUDICATED"
    small = copy.deepcopy(good)
    small["mey"]["key_ledger"] = 0.80                                                    # 改善+0.05 (<0.10)
    assert ev.classify_variant("A", small, base)["label"] == "REJECTED"
    mid = copy.deepcopy(good)
    mid["mey"]["key_ledger"] = 0.875                                                     # +0.125: (>=0.10, <0.17)
    assert ev.classify_variant("A", mid, base)["label"] == "NOT_VALIDATED_BELOW_CRITERION_A_PRIME"
    over = copy.deepcopy(good)
    over["coffee"]["delta_facts_vs_E0"] = 3.0
    assert ev.classify_variant("A", over, base)["label"] == "NOT_VALIDATED_CRITERIA_UNMET"
    reg = copy.deepcopy(good)
    reg["muse"]["key_ledger"] = 0.5                                                      # 一般化で回帰
    assert ev.classify_variant("A", reg, base)["label"] == "NOT_VALIDATED_CRITERIA_UNMET"
    ge = copy.deepcopy(good)
    ge["mey"]["mean_llm_calls"] = 3
    assert ev.classify_variant("E", ge, base)["label"] == "USER_DECISION_CANDIDATE_COST"
