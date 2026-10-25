# OPEN-333 E3/E4 適用後の初回run集計(読取専用・API 0。Production file/出力は一切変更しない)。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_12。
# 使い方: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open333_first_run_tally_01.py <run_dir> [<run_dir> ...]
# 集計(tts_generation_results*.json の attempts_log[*].asr_judgement / Z形式はsegment直下): attempts_scanned / PHONETIC_MATCH PASS件数(Candidate E以外も含む上限値) /
#   E3拒否が発火した件数(asr_judgement.candidate_e_full_diff) と拒否pair。異常値の目安: 1runで拒否が3件超ならrollback定数(er011.CANDIDATE_E_FULL_DIFF_CHECK)の判断をFableへ報告(自動rollbackはしない)。
# 【委任_14 OPEN-333 E4 / Opus M-2】E4(Candidate Eが残したカタカナ/略語・濁点差を即PASSにせずCascadeへ戻した)の発火 = asr_judgement.candidate_e_cascade_return。
#   e4_fired(件数・pair)と、発火したsegmentの最終結果区分 e4_outcomes: PASS_WITH_WARNING(同attemptでAzure一致=事後試聴対象) / REGEN_THEN_PASS(再生成後に合格) /
#   HR(segment.status=HUMAN_REVIEW_LOCKED) / STOP(STOPPED) / OTHER_NONPASS(その他の非合格)。
#   報告条件: (1) 1runでe4_fired が3件超 -> Fableへ報告(alert_e4_count)。 (2) E4発火行が1件でもHRに到達 -> 件数に関わらずFableへ報告(alert_e4_hr)。
#   (2)の正しい対処はE4のrollbackではない。原因は表記慣習差(例: ヴェラ/ベラ)でAzureも同じ転写をし再生成しても直らない場合であり、検討すべきは『表記正規化』
#   (ユーザー承認が必要な別件)。HEADでもカタカナ差だけの行は同じくHRに至る既存挙動で、E4の欠陥ではない。自動rollbackはしない。
import glob, json, os, sys

PASSING = ("PASS", "PASS_WITH_WARNING")


def tally(run_dirs):
    out = {"attempts_scanned": 0, "phonetic_match_pass": 0, "e3_fired": 0, "e3_pairs": [], "alert": False,
           "e4_fired": 0, "e4_pairs": [], "e4_outcomes": {"PASS_WITH_WARNING": 0, "REGEN_THEN_PASS": 0, "HR": 0, "STOP": 0, "OTHER_NONPASS": 0},
           "alert_e4_count": False, "alert_e4_hr": False}
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
                for idx, a in enumerate(alog):
                    j = a.get("asr_judgement")
                    if not isinstance(j, dict):
                        continue
                    out["attempts_scanned"] += 1
                    if j.get("state") in PASSING and (j.get("primary") or {}).get("label") == "PHONETIC_MATCH":
                        out["phonetic_match_pass"] += 1
                    e4 = j.get("candidate_e_cascade_return")
                    if e4:
                        out["e4_fired"] += 1
                        out["e4_pairs"].append({"segment": key, "run": os.path.basename(rd), "diffs": e4.get("diffs")})
                        later_pass = any(isinstance(b.get("asr_judgement"), dict) and b["asr_judgement"].get("state") in PASSING for b in alog[idx + 1:])
                        st = s.get("status")
                        if later_pass:
                            oc = "REGEN_THEN_PASS"
                        elif j.get("state") in PASSING:
                            oc = "PASS_WITH_WARNING"
                        elif st == "HUMAN_REVIEW_LOCKED":
                            oc = "HR"
                        elif st == "STOPPED":
                            oc = "STOP"
                        else:
                            oc = "OTHER_NONPASS"
                        out["e4_outcomes"][oc] += 1
                    f = j.get("candidate_e_full_diff")
                    if f:
                        out["e3_fired"] += 1
                        out["e3_pairs"].append({"segment": key, "run": os.path.basename(rd), "pairs": f.get("pairs")})
    out["alert"] = out["e3_fired"] > 3
    out["alert_e4_count"] = out["e4_fired"] > 3
    out["alert_e4_hr"] = out["e4_outcomes"]["HR"] > 0
    return out


if __name__ == "__main__":
    print(json.dumps(tally(sys.argv[1:]), ensure_ascii=False, indent=1))
