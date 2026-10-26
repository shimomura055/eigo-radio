# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-MALE7-TRIAL-01 offline test(API 0): 設定同一性・ラウンドロビン順序・停止規則の決定論・文境界判定。
実行: $env:PYTHONPATH="netblock_harness_01"; py -m pytest docs\\research\\FAMILY-Y-VOICE1-MALE7-TRIAL-01\\tools\\ym7_tools_test_01.py -q"""
import collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.getcwd())
import ym7_plan_01 as plan
import ym7_summarize_01 as summ
import ym7_measure_01 as meas


def test_plan_deterministic_and_balanced():
    a = plan.build(plan.NEW_VOICES, 2, 1, 3, control=True)
    b = plan.build(plan.NEW_VOICES, 2, 1, 3, control=True)
    assert a == b
    assert len(a) == 64
    per = collections.Counter((i["voice"], i["level"], i["body"]) for i in a)
    for v in plan.NEW_VOICES:
        for lv, bd in plan.CELLS:
            assert per[(v, lv, bd)] == 2, (v, lv, bd)          # 各Voice×cell=2 take(公平性)
    assert per[("Algieba", "a2", 1)] == 2 and per[("Algieba", "b1b", 1)] == 2 and sum(1 for i in a if i["voice"] == "Algieba") == 4
    # 特定Voiceが常に先頭にならない(ラウンドロビン回転)
    first_voices = {a[k]["voice"] for k in range(0, len(a), 5)}
    assert len(first_voices) >= 4
    # 各batchのVoice数が近い(偏りなし)
    for v in plan.NEW_VOICES:
        cnt = [sum(1 for i in a if i["batch"] == bt and i["voice"] == v) for bt in (1, 2, 3)]
        assert max(cnt) - min(cnt) <= 1, (v, cnt)


def test_sentence_boundary():
    assert meas.is_sent_end("house.") and meas.is_sent_end('too."') and meas.is_sent_end("really?") and not meas.is_sent_end("home,") and not meas.is_sent_end("simply")


def test_phase2_rule_deterministic():
    import numpy as np
    def mk(mean_vals):
        rows = []
        for v, vals in mean_vals.items():
            for lv, b in summ.CELLS:
                for x in vals:
                    rows.append({"voice": v, "level": lv, "body": b, "kind": "main", "origin": "fresh", "src": "trial", "take": 1, "attempt": 1, "mid_long1000": x,
                                 "long1000_n": x, "occ_pct": 18.0, "max_ms": 900, "bad_mid": 1 if x >= 1 else 0, "bad_any": 1 if x >= 1 else 0, "asr_verified": True, "rep_flag": False})
        return summ.prep(rows)
    # 1名だけ0、他は全て大きく悪い→bestは全員と区間分離→Phase 2なし
    rows = mk({"Algieba": [3, 3, 3, 3, 3, 3], "Schedar": [3, 3, 3, 3, 3, 3], "Fenrir": [0] * 12, "Orus": [3] * 12})
    S = {v: summ.voice_stats(rows, v, summ.CELLS, "t") for v in summ.VOICES}
    d1 = summ.decide_phase2(S)
    d2 = summ.decide_phase2(S)
    assert d1 == d2 and d1["best_by_mean"] == "Fenrir" and d1["best_separated_from_all"] and d1["phase2_voices"] == []
    # 同程度→Phase 2あり、Algiebaは必ず対象に入る
    rows = mk({"Algieba": [1, 0, 1, 0], "Schedar": [0, 1, 0, 1], "Fenrir": [0, 0, 1, 1], "Orus": [1, 1, 0, 0], "Puck": [0, 1, 1, 0]})
    S = {v: summ.voice_stats(rows, v, summ.CELLS, "t") for v in summ.VOICES}
    d = summ.decide_phase2(S)
    assert not d["best_separated_from_all"] and "Algieba" in d["phase2_voices"] and len(d["phase2_voices"]) <= 3


def test_zero_counts_interval_not_degenerate():
    rows = [{"voice": "X", "level": "a2", "body": 1, "kind": "main", "mid_long1000": 0, "bad_mid": 0} for _ in range(3)]
    iv = summ.interval(rows, "mid_long1000", [("a2", 1)], "t")
    assert iv["hi"] > 0.1       # 0件でも区間が潰れない(過剰断定の防止)


def test_generation_settings_identical_across_voices():
    """Voice以外の設定(Style sha・モデル・関数名・text sha)が全Voiceで同一。load_prodはimportのみでAPIを呼ばない。"""
    import ym7_generate_01 as g
    P = g.load_prod()
    for lv in ("a2", "b1b"):
        for b in (1, 2, 3):
            specs = [g.build_spec(lv, b, v, P) for v in ("Algieba", "Schedar", "Fenrir", "Orus", "Puck", "Iapetus", "Sadaltager")]
            for s in specs[1:]:
                for k in ("style_prefix_sha256", "text_sha256", "generator", "tts_backend", "style_profile", "tts_execution_mode", "slowdown_percent_a2", "words"):
                    assert s[k] == specs[0][k], (lv, b, k)
            assert len({s["voice_name"] for s in specs}) == 7
    assert g.build_spec("a2", 1, "Fenrir", P)["style_prefix_sha256"].startswith("9293e0c3b294")
    assert g.build_spec("b1b", 1, "Fenrir", P)["style_prefix_sha256"].startswith("07d72dd67728")
    try:
        g.build_spec("a2", 1, "Zephyr", P)
        assert False, "女性Voiceが許可されてはならない"
    except AssertionError as e:
        assert "男性許可リスト外" in str(e)
