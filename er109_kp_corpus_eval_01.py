# er109_kp_corpus_eval_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01: 既知の『発音が異なるNG例(問題音声21件: take part→Take Tart、er091問題8件)』を負例セットとして固定し、
# KP保存コーパス(OPEN-458でP/S/Whisper転写が保存された96行: 正常28+未ラベル27+NG3 12+問題21+presumed_normal 8)に対し、
# 提案層 er109 が (a)問題音声を誤って同値にしない(誤同値0が要件) (b)偽NGを新たに救済する件数 を測る。API 0・読取専用。
# 入力: docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/noguard_reeval_01.json の table(canonical/p/s/A_whisper)。
import argparse
import json
import sys

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er109_asr_orthographic_equivalence_01 as e109

SRC = "docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/noguard_reeval_01.json"


def existing_pass(canon, text):
    if not text:
        return False
    cls = val.classify_asr_match(canon, text)           # KP/Whisper票と同じ(segment_idなし=Tier1非適用)
    return bool(cls.should_pass or S._step_alternate_pass(cls))


def run():
    t = json.load(open(SRC, encoding="utf-8"))["table"]
    rows, new_accept, problem_new_accept = [], [], []
    for r in t:
        problem = str(r["label"]).startswith("problem")
        for who, text in (("P", r["p"]), ("S", r["s"]), ("W", r.get("A_whisper"))):
            if not text:
                continue
            ex = existing_pass(r["canonical"], text)
            eq = e109.evaluate(r["canonical"], text)
            rec = {"corpus": r["corpus"], "id": r["id"], "label": r["label"], "who": who, "canonical": r["canonical"], "text": text,
                   "existing_pass": ex, "e109_equiv": eq.equivalent, "rules": eq.rules, "reason": eq.reason}
            rows.append(rec)
            if eq.equivalent and not ex:
                new_accept.append(rec)
                if problem:
                    problem_new_accept.append(rec)
    n_problem_rows = sum(1 for r in rows if str(r["label"]).startswith("problem"))
    summary = {
        "vote_texts_evaluated": len(rows), "problem_label_texts": n_problem_rows,
        "problem_texts_e109_equiv_total": sum(1 for r in rows if str(r["label"]).startswith("problem") and r["e109_equiv"]),
        "problem_texts_new_accept(要件0)": len(problem_new_accept),
        "new_accept_total(existing不合格→e109同値)": len(new_accept),
        "new_accept_by_label": {k: sum(1 for x in new_accept if x["label"] == k) for k in sorted({x["label"] for x in new_accept})},
    }
    return summary, new_accept, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/kp_corpus_eval_01.json")
    a = ap.parse_args()
    s, na, rows = run()
    json.dump({"generated_by": "er109_kp_corpus_eval_01.py", "api_calls": 0, "cost_jpy": 0, "summary": s, "new_accept": na, "rows": rows},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(s, ensure_ascii=False, indent=1))
    for x in na:
        print(x["label"], x["who"], repr(x["canonical"]), "<-", repr(x["text"]), x["rules"])
