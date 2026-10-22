# -*- coding: utf-8 -*-
# ============================================================
# er109_runtime_evidence_04_01.py  (有料: Azure STT 1回/case、ローカルWhisper。OpenAI Primaryは保存転写を使用)
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04 §6 runtime evidence(H1/H3 ASR段)。
# X/Zの保存wav(HR Lock済みattempt等)を、配線済みの本番adapter(evaluate_attempt_with_cascade_detail)へ
# run_scope("X"|"Z") 内で通す。Primary=保存OpenAI転写、Secondary=Azure実呼出(S1)、Whisper=ローカル実行。
# 結果は --out(json)へ。monkeypatchなし(scopeは本番と同じrun_scope)。
# 使い方: python er109_runtime_evidence_04_01.py --cases cases.json --out out.json
# cases.json: [{"id","family":"X|Z","kind":"kp|body","canonical","primary","wav","seg","level"}]
# ============================================================
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er109_xz_scope_01 as xz


def run_case(c):
    import er006_secondary_asr_01 as secondary_asr
    import er078_asr_unified_judge_01 as uj
    import er104_kp_vote_reuse_01 as kpr
    wav = os.path.join(ROOT, c["wav"])
    fam = c["family"]
    scope = xz.run_scope("X") if fam == "X" else xz.run_scope("Z")
    with scope:
        if c["kind"] == "kp":
            ev = kpr.evaluate_vote(c["canonical"], c["primary"], wav)
            aj = ev["asr_judgement"]
            return {"id": c["id"], "family": fam, "kind": "kp", "scope_active": xz.current_scope(), "state": ev["state"], "verified": ev["verified"],
                    "row": ev.get("row"), "azure_real_calls": ev.get("azure_real_calls"), "whisper_called": ev.get("whisper_called"),
                    "vote": ev.get("vote"), "orthographic_equivalence": aj.get("orthographic_equivalence"),
                    "reason_code": aj.get("reason_code"), "warnings": aj.get("warnings")}
        import er003_v1_repro01_main_generate as repro01
        ledger_phrases = [h["canonical_spelling"] for h in repro01.pronun_ledger.get_hint_for_text(c["canonical"], min_confidence="low")]
        max_len = len(c["canonical"]) + 10
        actx = {"slot": 1, "is_last_slot": False, "script_version": "v0", "cache": uj.SecondaryCache(), "max_len": max_len,
                "segment_key": c.get("seg") or "", "role": None}
        detail = secondary_asr.evaluate_attempt_with_cascade_detail(
            c["canonical"], c["primary"], [], wav, language="en-US", ledger_phrases=ledger_phrases,
            cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED, enable_non_latin_cascade=True, attempt_ctx=actx)
        aj = detail.get("asr_judgement") or {}
        return {"id": c["id"], "family": fam, "kind": "body", "scope_active": xz.current_scope(), "state": aj.get("state"), "verified": bool(detail.get("verified")),
                "reason_code": aj.get("reason_code"), "secondary": aj.get("secondary"), "orthographic_equivalence": aj.get("orthographic_equivalence"),
                "warnings": aj.get("warnings"), "final_gate": aj.get("final_gate"), "azure_real_calls": (aj.get("adapter") or {}).get("azure_real_calls")}


def main(argv=None):
    import er005_cost_logger as cl
    cl.init_logger(os.path.join(os.path.dirname(os.path.abspath(sys.argv[sys.argv.index("--out") + 1])), "cost_log.jsonl"))   # 実費記録(本evidence専用)
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cases = json.load(open(a.cases, encoding="utf-8"))
    out = []
    for c in cases:
        try:
            out.append(run_case(c))
        except Exception as exc:  # noqa: BLE001
            out.append({"id": c["id"], "family": c["family"], "error": f"{type(exc).__name__}: {exc}"})
        print(json.dumps(out[-1], ensure_ascii=False)[:400])
    json.dump({"results": out, "scope_after": xz.current_scope()}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
