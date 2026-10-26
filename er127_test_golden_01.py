# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(R-2): scope外(Family A/B/C・単体呼出)のgolden。

**変更前コード(委任_02着手時のHEAD相当)で生成**した `er127_test_golden_01.json` と、現在のコードの出力をbyte同一で比較する。
対象: 変更した全leaf(voice01 / news_tail_fix / crosslevel / n3_tts L4・JA / repro01 strict・KP / er012_b hook=None)を、
scope外・新kwargなしで呼んだときの 結果dict・sleep列・TTS prompt列・judge呼出kw・HRQ行。
`FamilyAUnchangedTest`(working tree diff=0)はcommit後は常にPASSで保護にならない(Opus R-2)ため、本goldenを証拠とする。
"""
from __future__ import annotations

import json
import os
import re

import er127_test_fakes_01 as F

GOLDEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er127_test_golden_01.json")
TTS_ALL = [True] * 12
SCENARIOS = {
    "pass1": dict(judge=[F.PASS]),
    "ng_pass": dict(judge=[F.NG, F.PASS]),
    "ng_ng_pass": dict(judge=[F.NG, F.NG, F.PASS]),
    "all_ng_lr_ok": dict(judge=[F.NG, F.NG, F.NG, F.PASS]),
    "all_ng_lr_fail": dict(judge=[F.NG] * 6),
    "tech_fail_then_ok": dict(tts=[False, True, True], judge=[F.PASS]),
    "stop_retry": dict(judge=[F.NG, F.NG_STOP]),
}
LEAVES = ["L1", "L2", "L3", "L4", "L7a", "L7b", "L6", "L8"]
_ISO = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:[+-]\d\d:\d\d)?")


def _round(o):
    if isinstance(o, float):
        return round(o, 1)
    if isinstance(o, dict):
        return {k: _round(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round(v) for v in o]
    return o


def _norm(rec, tmp_root):
    n = F.normalize(_round(rec), tmp_root)
    return json.loads(_ISO.sub("<ISO>", json.dumps(n, ensure_ascii=False, sort_keys=True)))


def _invoke(leaf, w, cs):
    import er003_v1_crosslevel_audio_02_common as c
    import er003_v1_n3_01_tts_generate as n3
    import er003_v1_repro01_main_generate as repro01
    import er003_v1_sing01_news_tail_fix as ntf
    import er003_v1_sing01_voice01_generate as v1
    if leaf == "L1":
        return v1.generate_charon_english(F.TEXT, w.out_path, enable_connected_speech_equivalence_layer=cs)
    if leaf == "L2":
        return ntf.generate_news_narration_wide_margin(F.TEXT, w.out_path, enable_connected_speech_equivalence_layer=cs)
    if leaf == "L3":
        return c.generate_english_segment_with_fallback(F.TEXT, w.out_path, F.TEXT, enable_connected_speech_equivalence_layer=cs)
    if leaf == "L4":
        return n3.generate_a2_segment_with_slowdown(F.TEXT, w.out_path, F.TEXT, enable_connected_speech_equivalence_layer=cs)
    if leaf == "L7a":
        return n3.generate_a2_japanese_with_fallback(F.JA_TEXT, w.out_path, F.JA_TEXT)
    if leaf == "L7b":
        return v1.generate_charon_japanese(F.JA_TEXT, w.out_path, F.JA_TEXT)
    if leaf == "L6":
        return repro01.generate_key_phrase_component_verified(F.TEXT, w.out_path)
    if leaf == "L8":
        import er012_b_family_voices_production_01 as bv
        return bv.generate_voice_body_wide_margin(F.TEXT, w.out_path, "Puck", enable_connected_speech_equivalence_layer=cs)
    raise ValueError(leaf)


def run_case(leaf, scenario, cs, *, scope=None, seg=None, level=None):
    sc = SCENARIOS[scenario]
    ja = leaf in ("L7a", "L7b")
    kw = dict(tts=sc.get("tts", TTS_ALL), asr_text=F.JA_TEXT if ja else F.TEXT)
    if ja:
        kw["ja_judge"] = sc["judge"]
    else:
        kw["judge"] = sc["judge"]
    if seg:
        kw["seg"] = seg
    if level:
        kw["level"] = level
    w = F.World(**kw)
    try:
        with w.patched(scope=scope):
            try:
                r = _invoke(leaf, w, cs)
                err = None
            except BaseException as exc:      # noqa: BLE001  (golden: 例外型も記録)
                r, err = None, f"{type(exc).__name__}: {exc}"
        rec = {"leaf": leaf, "scenario": scenario, "cs": cs, "result": r, "error": err, "events": w.events,
               "prompts": [p for p in w.prompts], "judge_calls": [{k: v for k, v in j.items() if k != "path"} for j in w.judge_calls],
               "hr_rows": w.hr_rows() + w.hr_rows_ja(), "lr_calls": w.lr_calls, "sleeps": w.clock.sleeps}
        return _norm(rec, w.tmp_root)
    finally:
        w.cleanup()


def case_ids():
    out = []
    for leaf in LEAVES:
        for sc in SCENARIOS:
            for cs in ((True, False) if leaf in ("L1", "L2", "L3", "L8") else (True,)):
                if leaf in ("L7a", "L7b", "L6") and cs is False:
                    continue
                out.append((leaf, sc, cs))
    return out


# 旧コード(A/B/C)の既知欠陥: L1/L2でcs=Trueの『LR後も不合格』は `__wrapped__(max_attempts=1, cs=True)` が自分自身のLRへ再入し
# RecursionErrorになる(OPEN-376/D-B4)。欠陥の出力(例外)をgoldenの期待値にはしない: 除外する。scope内(X/Y/Z)ではLR再入禁止で別途検証する。
KNOWN_LEGACY_DEFECT_CASES = frozenset({("L1", "all_ng_lr_fail", True), ("L1", "stop_retry", True),
                                       ("L2", "all_ng_lr_fail", True), ("L2", "stop_retry", True)})


def build_golden():
    return {f"{leaf}|{sc}|{cs}": run_case(leaf, sc, cs) for leaf, sc, cs in case_ids() if (leaf, sc, cs) not in KNOWN_LEGACY_DEFECT_CASES}


if __name__ == "__main__":
    import sys
    if "--write" in sys.argv:
        g = build_golden()
        with open(GOLDEN_PATH, "w", encoding="utf-8") as f:
            json.dump(g, f, ensure_ascii=False, indent=1, sort_keys=True)
        print("wrote", GOLDEN_PATH, len(g))
