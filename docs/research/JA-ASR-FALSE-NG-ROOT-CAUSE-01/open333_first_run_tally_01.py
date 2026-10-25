# OPEN-333 E3 適用後の初回run集計(読取専用・API 0。Production file/出力は一切変更しない)。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_12。
# 使い方: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_first_run_tally_01.py <run_dir> [<run_dir> ...]
# 集計(tts_generation_results*.json の attempts_log[*].asr_judgement / Z形式はsegment直下): attempts_scanned / PHONETIC_MATCH PASS件数(Candidate E以外も含む上限値) /
#   E3拒否が発火した件数(asr_judgement.candidate_e_full_diff) と拒否pair。異常値の目安: 1runで拒否が3件超ならrollback定数(er011.CANDIDATE_E_FULL_DIFF_CHECK)の判断をFableへ報告(自動rollbackはしない)。
import glob, json, os, sys

PASSING = ("PASS", "PASS_WITH_WARNING")


def tally(run_dirs):
    out = {"attempts_scanned": 0, "phonetic_match_pass": 0, "e3_fired": 0, "e3_pairs": [], "alert": False}
    for rd in run_dirs:
        for p in sorted(glob.glob(os.path.join(rd, "**", "tts_generation_results*.json"), recursive=True)):
            try:
                d = json.load(open(p, encoding="utf8"))
            except Exception:
                continue
            segs = d.get("segments") if isinstance(d, dict) else None
            if not isinstance(segs, dict):
                continue
            for key, s in segs.items():
                if not isinstance(s, dict):
                    continue
                alog = [a for a in (s.get("attempts_log") or []) if isinstance(a, dict)]
                if not any(isinstance(a.get("asr_judgement"), dict) for a in alog) and isinstance(s.get("asr_judgement"), dict):
                    alog = [{"asr_judgement": s["asr_judgement"]}]
                for a in alog:
                    j = a.get("asr_judgement")
                    if not isinstance(j, dict):
                        continue
                    out["attempts_scanned"] += 1
                    if j.get("state") in PASSING and (j.get("primary") or {}).get("label") == "PHONETIC_MATCH":
                        out["phonetic_match_pass"] += 1
                    f = j.get("candidate_e_full_diff")
                    if f:
                        out["e3_fired"] += 1
                        out["e3_pairs"].append({"segment": key, "run": os.path.basename(rd), "pairs": f.get("pairs")})
    out["alert"] = out["e3_fired"] > 3
    return out


if __name__ == "__main__":
    print(json.dumps(tally(sys.argv[1:]), ensure_ascii=False, indent=1))
