# -*- coding: utf-8 -*-
"""voice_acceptance_check_01: Voice変更の受入用・読取専用check(FZ-TELL-TALE-HEART-NARRATOR-VOICE-01 委任_03)。
計画voice(audit/tts_generation_results.json)・attempt JSON voice・SDK境界の送信記録(cost_log.jsonl の tts_voice_sent)を
clip単位で機械照合する。Gate判定は変えない(Z run_audio_gate等へは接続しない)。API 0・ファイル書込なし。
usage: python voice_acceptance_check_01.py <run_dir> --clips id1,id2,... [--levels a2,b1b] [--since ISO8601]
rc: 0=全clip一致 / 1=不一致あり(重大NG候補) / 2=未計測あり(送信記録なし等。一致とは扱わない)"""
import argparse, glob, json, os, sys


def check(run_dir, clips, levels=("a2", "b1b"), since=None):
    sent = {}   # (level_stage, segment) -> [voice,...]
    for line in open(f"{run_dir}/cost_log.jsonl", encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("provider") != "gemini" or "TTS" not in str(d.get("api")) or not d.get("success"):
            continue
        if since and str(d.get("timestamp", "")) < since:
            continue
        st = {"tts_a2": "a2", "tts_b1b": "b1b"}.get(d.get("stage"))
        if st:
            sent.setdefault((st, d.get("segment")), []).append(d.get("tts_voice_sent"))
    rows = []
    for lv in levels:
        res = json.load(open(f"{run_dir}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
        for cid in clips:
            e = res.get(cid)
            if e is None:
                rows.append({"level": lv, "clip": cid, "status": "UNMEASURED", "why": "results entryなし"}); continue
            planned = e.get("voice")
            sv = sent.get((lv, cid), [])
            att = []
            for f in glob.glob(f"{run_dir}/{lv}/narration/attempts/{cid}_attempt*.json"):
                j = json.load(open(f, encoding="utf-8"))
                if j.get("route") == "post_slowdown":
                    continue   # 減速後処理の記録(TTS送信ではない=voice欄なしが仕様)
                att.append(j.get("voice"))
            reasons, status = [], "OK"
            if not sv or any(v is None for v in sv):
                status, reasons = "UNMEASURED", [f"tts_voice_sent欠落(送信記録{len(sv)}件)"]
            elif set(sv) != {planned}:
                status, reasons = "MISMATCH", [f"送信{sorted(set(sv))}≠計画{planned}"]
            if att and set(att) != {planned}:
                status = "MISMATCH"; reasons.append(f"attempt JSON voice{sorted(set(map(str, att)))}≠計画{planned}")
            rows.append({"level": lv, "clip": cid, "planned": planned, "sent": sorted(set(map(str, sv))), "n_sent": len(sv),
                         "attempt_json": sorted(set(map(str, att))), "status": status, "why": "; ".join(reasons)})
    rc = 1 if any(r["status"] == "MISMATCH" for r in rows) else (2 if any(r["status"] == "UNMEASURED" for r in rows) else 0)
    return rows, rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir"); ap.add_argument("--clips", required=True)
    ap.add_argument("--levels", default="a2,b1b"); ap.add_argument("--since")
    a = ap.parse_args()
    rows, rc = check(a.run_dir, a.clips.split(","), tuple(a.levels.split(",")), a.since)
    for r in rows:
        print(json.dumps(r, ensure_ascii=False))
    print("RESULT:", {0: "ALL_MATCH", 1: "MISMATCH", 2: "UNMEASURED"}[rc])
    return rc


if __name__ == "__main__":
    sys.exit(main())
