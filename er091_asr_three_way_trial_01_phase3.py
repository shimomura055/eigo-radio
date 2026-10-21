# ============================================================
# er091_asr_three_way_trial_01_phase3.py  (API 0)  Phase 3: Validator込み最終判定(構成比較)
# Production判定関数 er006_secondary_asr_01.evaluate_attempt_with_cascade_detail を**呼ぶ**(改変しない)。
# 構成ごとに「Primary転写の供給元」「Secondary取得関数の戻り(キャッシュ転写)」だけを差し替えるTrial wrapper。
# Secondary取得関数 get_full_text_via_azure_stt_with_phrase_list をプロセス内でキャッシュ転写返却へ差替える(ファイル改変なし)。
# ネットワーク禁止: Primary(OpenAI)呼出・OpenAI client取得・Azure呼出は差替/例外化(本scriptはAPIを呼ばない)。
# 入替構成ではProduction規則(Primary言語prior前提のCMU/Tier1、Secondary accepted集合、low_ratio 0.98、entity救済、M1)が
# そのまま妥当とは限らない -> 結果は「現行ルールを流用した場合の参考値」。
# ============================================================
from __future__ import annotations
import collections
import json
import os
import sys

sys.path.insert(0, ".")
OUT = "er091_output/asr_three_way_trial_01"
RES = os.path.join(OUT, "results")
import er091_asr_three_way_trial_01_analyze as an  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
cl.install(os.path.join(RES, "phase3_cl_unused.jsonl"))
import er006_secondary_asr_01 as sec  # noqa: E402
import er006_asr_provider_routing_01 as routing  # noqa: E402
import er078_asr_unified_attempt_ctx_01 as ctxm  # noqa: E402
import er078_asr_unified_judge_01 as uj  # noqa: E402

STATE = {"sec_text": None, "sec_calls": 0}


def _fake_secondary(wav_path, language="en-US", phrases=None, timeout_seconds=90.0):
    STATE["sec_calls"] += 1
    return STATE["sec_text"], (None if STATE["sec_text"] is not None else "no_cached_transcript")


def _forbidden(*a, **k):
    raise RuntimeError("Phase3 must not call external ASR")


sec.get_full_text_via_azure_stt_with_phrase_list = _fake_secondary
routing.transcribe = _forbidden
routing._get_openai_client = _forbidden

CONFIGS = [
    # id, 説明, primary供給元, secondary供給元, force_secondary(callable or bool)
    ("C1", "現行: OpenAI Primary -> Azure Secondary(Primary PASSならSecondary不要)", "openai", "azure", False),
    ("C1d", "現行+両方PASS必須(force_secondary=True; KP dual-pass案)", "openai", "azure", True),
    ("C2", "Azure Primary -> OpenAI Secondary", "azure", "openai", False),
    ("C3", "Whisper Primary -> OpenAI Secondary", "whisper", "openai", False),
    ("C4", "Whisper Primary -> Azure Secondary", "whisper", "azure", False),
    ("C5", "現行 + Whisper単独verdictがNGの音声のみforce_secondary(案A)", "openai", "azure", "whisper_veto"),
    # 追加(small->medium で容量由来の誤りが減ることを実測した後の追加構成)
    ("C3m", "Whisper medium Primary -> OpenAI Secondary", "whisper_medium", "openai", False),
    ("C4m", "Whisper medium Primary -> Azure Secondary", "whisper_medium", "azure", False),
    ("C5m", "現行 + Whisper medium単独verdictがNGの音声のみforce_secondary", "openai", "azure", "whisper_medium_veto"),
]


def run_one(m, cfg, trans):
    cid, desc, p_src, s_src, force = cfg
    ptext = trans[p_src]
    STATE["sec_text"] = trans[s_src]
    STATE["sec_calls"] = 0
    if force in ("whisper_veto", "whisper_medium_veto"):
        wpass, _, _ = an.verdict(m["canonical"], trans["whisper" if force == "whisper_veto" else "whisper_medium"])
        force_b = not wpass
    else:
        force_b = bool(force)
    canon = m["canonical"]
    kp = m["kind"] == "kp"
    max_len = len(canon) + (10 if kp else 15)
    detail = sec.evaluate_attempt_with_cascade_detail(
        canon, ptext, [], m["wav"], language="en-US", ledger_phrases=m["ledger_phrases"],
        cascade_enabled=sec.FEATURE_FLAG_SECONDARY_ASR_ENABLED, force_secondary=force_b, enable_non_latin_cascade=kp,
        enable_connected_speech_equivalence_layer=(not kp), segment_id=None,
        attempt_ctx=ctxm.build_attempt_ctx(1, 2, slot_offset=0, total_slots=(4 if kp else 3), max_len=max_len))
    audit = detail.get("asr_judgement") or {}
    length_ok = ptext is not None and len(ptext) <= max_len
    verified = bool(detail["verified"]) and uj.final_length_ok(length_ok, detail)
    return {"verified": verified, "state": audit.get("state"), "reason_code": audit.get("reason_code"),
            "secondary_called": (audit.get("secondary") or {}).get("called"), "secondary_cached": (audit.get("secondary") or {}).get("cached"),
            "secondary_accepted": (audit.get("secondary") or {}).get("accepted"), "sec_fn_calls": STATE["sec_calls"],
            "primary_passed": (audit.get("primary") or {}).get("passed"), "primary_label": (audit.get("primary") or {}).get("label"),
            "force_secondary": force_b, "final_status": detail.get("final_status")}


def main():
    man = {r["id"]: r for r in an.manifest() if not r["duplicate_of"]}
    eff = an.effective(an.raw())
    out = []
    for rid, m in man.items():
        trans = {}
        for meth in ("openai", "azure", "whisper", "whisper_medium"):
            e = eff.get((rid, meth))
            t_ = (e["prod"].get("text") if e and e["prod"] else None)
            trans[meth] = " ".join(t_.split()) if t_ is not None else None   # Whisper二重空白の除去(length判定の人工的NG防止)
        if any(trans[k] is None for k in ("openai", "azure", "whisper")):
            print("skip(no transcript)", rid, {k: v is None for k, v in trans.items()})
            continue
        for cfg in CONFIGS:
            if "whisper_medium" in (cfg[2], cfg[3], cfg[4]) and trans.get("whisper_medium") is None:
                continue
            try:
                r = run_one(m, cfg, trans)
            except Exception as exc:  # noqa: BLE001
                r = {"verified": False, "state": "TRIAL_WRAPPER_EXCEPTION", "reason_code": f"{type(exc).__name__}: {exc}"[:200]}
            out.append({"id": rid, "config": cfg[0], "label": m["label"], "label_class": m["label_class"], "kind": m["kind"],
                        "family": m["family"], "level": m["level"], "problem_type": m.get("problem_type"), "canonical": m["canonical"],
                        "primary_text": trans[cfg[2]], "secondary_text": trans[cfg[3]], **r})
    json.dump(out, open(os.path.join(RES, "phase3_item_results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = collections.Counter((o["config"], o["label"], o["verified"]) for o in out)
    for cfg in CONFIGS:
        print(cfg[0], {k[1:]: v for k, v in c.items() if k[0] == cfg[0]})
    exc = [o for o in out if o["state"] == "TRIAL_WRAPPER_EXCEPTION"]
    print("wrapper exceptions", len(exc), [e["reason_code"] for e in exc[:3]])


if __name__ == "__main__":
    main()
