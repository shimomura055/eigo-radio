# ============================================================
# er104_nonkp_before_after_01.py  (API 0 / 費用0)
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02: 保存4,032ペア(PNMH-PLAN-01 pairs_02.jsonl)を、**KP以外の呼出**(vote_required無し)として
# adapter(evaluate_attempt_with_cascade_detail)へ通した出力の署名をjsonlへ書く。配線前commit(baseline)と配線後(after)でそれぞれ実行し
# 行ごとに完全一致(差分0)であることを確認する(Family A/B/C・KP以外のASR判定が3-ASR配線で変わらない証拠)。
#   Primary転写=保存ASR転写、Secondary=mock(同じ転写)、Whisper=呼ばれない(vote_requiredなし)。HR/telemetry/lookupはspy(実書込0)。
# 使い方: python er104_nonkp_before_after_01.py --out <jsonl> [--limit N]
# ============================================================
import argparse
import hashlib
import json
import os
import re
import sys
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
if os.environ.get("KP3V_OVERLAY"):   # 配線前commitのProduction .pyを先頭に置く(同一data環境でbefore/afterを取るため)
    sys.path.insert(0, os.environ["KP3V_OVERLAY"])
import er006_asr_provider_routing_01 as routing
import er006_secondary_asr_01 as sec
import er103_proper_noun_alarm_policy_01 as pol

PAIRS = os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "pairs_02.jsonl")
_JA = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    wav = os.path.join(os.environ.get("TMP", "."), "kp3v_nonkp_silence.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(1); w.setframerate(8000); w.writeframes(b"\x00" * 8000)
    hr, lookups, tel = [], [], []
    sec._resolve_unresolved_entity_for_review = lambda span: lookups.append(span) or {"pronunciation_hint": "", "confidence": "unconfirmed", "sources": []}
    sec._log_human_review = lambda d: hr.append(d)
    sec.semantic_equivalence.append_telemetry_log = lambda *x, **k: tel.append(1)
    routing.transcribe = lambda *x, **k: (_ for _ in ()).throw(RuntimeError("Primary#2 forbidden"))
    pairs = [json.loads(l) for l in open(PAIRS, encoding="utf-8") if l.strip()]
    if a.limit:
        pairs = pairs[:a.limit]
    n = 0
    with open(a.out, "w", encoding="utf-8") as fo:
        for i, p in enumerate(pairs):
            canon, asr = p["canonical"], p["asr"]
            ja = bool(_JA.search(canon))
            for scope_on, seg in ((False, "japanese_title" if ja else "full_story_part1"), (True, "japanese_title" if ja else "full_story_part1"),
                                  (False, None)):
                sec.get_full_text_via_azure_stt_with_phrase_list = lambda w, language="en-US", phrases=None, **kw: (asr, None)
                sec.reset_secondary_cache()
                pol._RUN_SCOPE = None
                try:
                    if scope_on:
                        with pol.run_scope("X"):
                            d = sec.evaluate_attempt_with_cascade_detail(canon, asr, [], wav, language=("ja-JP" if ja else "en-US"), cascade_enabled=True,
                                                                          segment_id=seg, attempt_ctx={"slot": 1, "is_last_slot": True})
                    else:
                        d = sec.evaluate_attempt_with_cascade_detail(canon, asr, [], wav, language=("ja-JP" if ja else "en-US"), cascade_enabled=True,
                                                                      segment_id=seg, attempt_ctx={"slot": 1, "is_last_slot": True})
                    c = d["classification"]
                    aj = d.get("asr_judgement") or {}
                    sig = {"verified": bool(d["verified"]), "stop": bool(d["stop_retrying"]), "cls": c.classification, "hr": bool(d.get("human_review_required")),
                           "state": aj.get("state"), "reason": aj.get("reason_code"), "tech": bool(d.get("technical_stop")),
                           "warnings": aj.get("warnings"), "steps": [(s.get("step"), s.get("text"), s.get("classification")) for s in d.get("steps", [])],
                           "final_status": d.get("final_status"), "keys": sorted(aj.keys())}
                except Exception as exc:  # noqa: BLE001
                    sig = {"error": f"{type(exc).__name__}: {exc}"}
                key = f"{i}|scope={int(scope_on)}|seg={seg}"
                fo.write(json.dumps({"k": key, "sig": sig}, ensure_ascii=False, sort_keys=True) + "\n")
                n += 1
    sys.stdout.write(f"rows={n} hr_spy={len(hr)} lookups={len(lookups)} out_sha256={hashlib.sha256(open(a.out, 'rb').read()).hexdigest()}\n")


if __name__ == "__main__":
    main()
