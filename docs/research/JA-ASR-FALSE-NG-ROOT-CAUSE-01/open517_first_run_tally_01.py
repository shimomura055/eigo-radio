# OPEN-517 適用後の初回run集計(R-3。読取専用・API 0。Production file/出力は一切変更しない)。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A。
# 使い方: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_first_run_tally_01.py <run_dir> [<run_dir> ...]
#   <run_dir> = 適用後の最初の本番run(X/Z/Y/legacy の JA)の出力dir(`tts_generation_results*.json` と任意で `review_lock_state.json` を含む)。
# 集計(attempts_log[*].asr_judgement から):
#   (a) F1: reason_code=="final_gate_value_diff"/"final_gate_negation_diff" かつ primary.equivalence_basis=="READING_MATCH" の件数
#   (b) F1: reason_code=="primary_pass_demoted_ambiguous_value" かつ READING_MATCH の件数(P3降格)
#   (c) (a)(b)のうち当該segmentが最終slot到達でHR Lock入りしたもの(review_lock_state.json に segment key があるもの)
#   (d) F2発動: value_guard.kana_unify.fired==True の件数、およびPASS_WITH_WARNING で JA_NUMERIC_IRREGULAR_READING が付いた件数
#   (e) OPEN-524/523由来: value_guard.primary.pairs の reason に kana_numeral_part_of_larger_reading を含む件数 / 弱いかな数詞を含む pair の DIFF 件数
# 異常値の目安: (a)が1runで3件超ならrollback定数(er078_asr_unified_judge_01.READING_MATCH_FINAL_GATE)の検討をFableへ報告(自動rollbackはしない)。
import glob, json, os, sys

PASSING = ("PASS", "PASS_WITH_WARNING")


def tally(run_dirs):
    out = {"a_final_gate_diff": 0, "b_demote_p3": 0, "c_hr_lock": 0, "d_f2_fired": 0, "d_warn_irregular": 0, "e_part_of_larger": 0, "e_weak_diff": 0,
           "attempts_scanned": 0, "reading_match_attempts": 0, "details": []}
    for rd in run_dirs:
        locked = set()
        for lp in glob.glob(os.path.join(rd, "**", "review_lock_state.json"), recursive=True):
            try:
                st = json.load(open(lp, encoding="utf8"))
            except Exception:
                continue
            blob = json.dumps(st, ensure_ascii=False)
            locked.add(blob)
        locked_text = "\n".join(locked)
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
                for a in s.get("attempts_log") or []:
                    j = a.get("asr_judgement")
                    if not isinstance(j, dict):
                        continue
                    out["attempts_scanned"] += 1
                    basis = (j.get("primary") or {}).get("equivalence_basis")
                    vgp = ((j.get("value_guard") or {}).get("primary") or {})
                    rs = j.get("reason_code") or ""
                    if basis == "READING_MATCH":
                        out["reading_match_attempts"] += 1
                    hit = None
                    if basis == "READING_MATCH" and rs in ("final_gate_value_diff", "final_gate_negation_diff"):
                        out["a_final_gate_diff"] += 1
                        hit = "a"
                    if basis == "READING_MATCH" and (rs == "primary_pass_demoted_ambiguous_value" or j.get("p3_entry") == "primary_pass_demoted_ambiguous_value"):
                        out["b_demote_p3"] += 1
                        hit = hit or "b"
                    if hit and key in locked_text:
                        out["c_hr_lock"] += 1
                    ku = (j.get("value_guard") or {}).get("kana_unify") or {}
                    if ku.get("fired"):
                        out["d_f2_fired"] += 1
                        if "JA_NUMERIC_IRREGULAR_READING" in (j.get("warnings") or []) and j.get("state") in PASSING:
                            out["d_warn_irregular"] += 1
                    pairs = vgp.get("pairs") or []
                    if any("kana_numeral_part_of_larger_reading" in str(q.get("reason")) for q in pairs):
                        out["e_part_of_larger"] += 1
                    if any(q.get("verdict") == "DIFF" and any(w in str(q.get("src")) + str(q.get("hyp")) for w in ("なのか", "ようか", "とお")) for q in pairs):
                        out["e_weak_diff"] += 1
                    if hit or ku.get("fired"):
                        out["details"].append({"file": p.replace("\\", "/"), "segment": key, "attempt": a.get("attempt"), "hit": hit, "reason": rs,
                                               "canon": s.get("canonical_text") or s.get("text"), "asr": (j.get("primary") or {}).get("text")})
    out["alert_rollback_review"] = out["a_final_gate_diff"] > 3
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    r = tally(sys.argv[1:])
    print(json.dumps(r, ensure_ascii=False, indent=1))
