# OPEN-517 適用後の初回run集計(R-3。読取専用・API 0。Production file/出力は一切変更しない)。JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A。
# 使い方: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/open517_first_run_tally_01.py <run_dir> [<run_dir> ...]
#   <run_dir> = 適用後の最初の本番run(X/Z/Y/legacy の JA)の出力dir(`tts_generation_results*.json` と任意で `review_lock_state.json` を含む)。
# 集計(attempts_log[*].asr_judgement から):
#   (a) F1: reason_code=="final_gate_value_diff"/"final_gate_negation_diff" かつ primary.equivalence_basis=="READING_MATCH" の件数
#   (b) F1: reason_code=="primary_pass_demoted_ambiguous_value" かつ READING_MATCH の件数(P3降格)
#   (c) (a)(b)のうち当該segmentが最終slot到達でHR Lock入りしたもの(review_lock_state.json に segment key があるもの)
#   (d) F2発動: value_guard.kana_unify.fired==True の件数、およびPASS_WITH_WARNING で JA_NUMERIC_IRREGULAR_READING が付いた件数
#   (e) OPEN-524/523由来: value_guard.primary.pairs の reason に kana_numeral_part_of_larger_reading を含む件数 / 弱いかな数詞を含む pair の DIFF 件数
# R-5(委任_09)追加: `asr_judgement.r5`(er078 `_r5_record`。判定確定後の読取専用記録)があれば、その項目も集計する(旧run=r5なしでも動く):
#   r5_present / r5_f1_rejected(f1.final_gate_rejected) / r5_f1_demoted(f1.demoted_p3) / r5_f2_enabled / r5_f2_fired / r5_o523_weak_diff / r5_o524_part_of_larger /
#   r5_measurement_errors / r5_secondary_provenance_incomplete(secondary.provenance_complete==False) / r5_models(primary/secondary model の出現数)
# 異常値の目安: (a)が1runで3件超ならrollback定数(er078_asr_unified_judge_01.READING_MATCH_FINAL_GATE)の検討をFableへ報告(自動rollbackはしない)。
import glob, json, os, sys

PASSING = ("PASS", "PASS_WITH_WARNING")


def tally(run_dirs):
    out = {"a_final_gate_diff": 0, "b_demote_p3": 0, "c_hr_lock": 0, "d_f2_fired": 0, "d_warn_irregular": 0, "e_part_of_larger": 0, "e_weak_diff": 0,
           "attempts_scanned": 0, "reading_match_attempts": 0, "details": [],
           "r5_present": 0, "r5_f1_rejected": 0, "r5_f1_demoted": 0, "r5_f2_enabled": 0, "r5_f2_fired": 0, "r5_o523_weak_diff": 0, "r5_o524_part_of_larger": 0,
           "r5_measurement_errors": 0, "r5_secondary_provenance_incomplete": 0, "r5_models": {}, "head_evidence": {}}
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
                # X/Y/legacy形式=attempts_log[*].asr_judgement。Z形式(er063 build_entry)=segment直下の asr_judgement(attempts_logなし)。
                # asr_judgement_inherited(前回run継承。今回判定ではない)は数えない。
                _alog = [a for a in (s.get("attempts_log") or []) if isinstance(a, dict)]
                if not any(isinstance(a.get("asr_judgement"), dict) for a in _alog) and isinstance(s.get("asr_judgement"), dict):
                    _alog = [{"attempt": None, "asr_judgement": s["asr_judgement"]}]
                for a in _alog:
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
                    r5 = j.get("r5")
                    if isinstance(r5, dict):
                        out["r5_present"] += 1
                        f1, f2 = r5.get("f1") or {}, r5.get("f2") or {}
                        out["r5_f1_rejected"] += int(bool(f1.get("final_gate_rejected")))
                        out["r5_f1_demoted"] += int(bool(f1.get("demoted_p3")))
                        out["r5_f2_enabled"] += int(bool(f2.get("enabled")))
                        out["r5_f2_fired"] += int(bool(f2.get("fired")))
                        out["r5_o523_weak_diff"] += int(r5.get("o523_weak_kana_diff_pairs") or 0)
                        out["r5_o524_part_of_larger"] += int(r5.get("o524_part_of_larger_pairs") or 0)
                        out["r5_measurement_errors"] += int(bool(r5.get("measurement_error")))
                        for side, m in (r5.get("models") or {}).items():
                            if isinstance(m, dict):
                                mk = side + ":" + str(m.get("model") or m.get("model_id"))
                                out["r5_models"][mk] = out["r5_models"].get(mk, 0) + 1
                        out["head_evidence"]["READING_MATCH_FINAL_GATE"] = (f1 or {}).get("rollback_const_READING_MATCH_FINAL_GATE")
                    if (j.get("secondary") or {}).get("provenance_complete") is False:
                        out["r5_secondary_provenance_incomplete"] += 1
                    if hit or ku.get("fired"):
                        out["details"].append({"file": p.replace("\\", "/"), "segment": key, "attempt": a.get("attempt"), "hit": hit, "reason": rs,
                                               "canon": s.get("canonical_text") or s.get("text"), "asr": (j.get("primary") or {}).get("text")})
    out["alert_rollback_review"] = out["a_final_gate_diff"] > 3
    out["alert_demote_review"] = out["b_demote_p3"] > 3   # 07A開示リスク: 期待読み表に無い正しい読みのDEMOTEが1 runで3件超 -> Fableへ即報告
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    r = tally(sys.argv[1:])
    print(json.dumps(r, ensure_ascii=False, indent=1))
