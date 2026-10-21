# ============================================================
# er091_asr_three_way_trial_01_takepart10.py (API 0)
# 既存Trial(FAMILY-X-KP-ASR-DUAL-PASS-TRIAL-01、er088_output)で保存済みの「同一wav(take part旧NG)を10回独立実行」の転写を使い、
# Phase 3 の構成C1〜C5を各回に適用する(同一音声の反復=安定性の証拠。独立音声10本ではない)。新規API呼出0。
# ============================================================
from __future__ import annotations
import collections
import json
import os
import sys

sys.path.insert(0, ".")
import er091_asr_three_way_trial_01_phase3 as p3  # noqa: E402 (モジュールimportで外部ASR呼出を禁止する差替が有効になる)
import er091_asr_three_way_trial_01_analyze as an  # noqa: E402

OUT = an.OUT
RES = an.RES


def main():
    man = {r["id"]: r for r in an.manifest()}
    m = man["prob_kp_takepart_user_reported"]
    rows = [json.loads(l) for l in open("er088_output/kp_asr_dual_pass_trial_01/results.jsonl", encoding="utf-8")]
    out = []
    for r in rows:
        ps = r["primary_and_secondary"]
        trans = {"openai": ps["primary_call"]["text"], "azure": ps["judge"]["secondary_text"], "whisper": " ".join(r["whisper"]["text"].split())}
        for cfg in p3.CONFIGS:
            if "medium" in str(cfg):
                continue   # 旧Trialにmedium転写は無い
            x = p3.run_one(m, cfg, trans)
            out.append({"trial": r["trial"], "config": cfg[0], "openai": trans["openai"], "azure": trans["azure"], "whisper": trans["whisper"], **x})
    json.dump(out, open(os.path.join(RES, "takepart10_phase3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = collections.Counter((o["config"], o["verified"]) for o in out)
    for cfg in [c_ for c_ in p3.CONFIGS if "medium" not in str(c_)]:
        print(cfg[0], "false_pass(of 10)=", c[(cfg[0], True)], "detected=", c[(cfg[0], False)])
    print("openai texts:", collections.Counter(o["openai"] for o in out if o["config"] == "C1"))


if __name__ == "__main__":
    main()
