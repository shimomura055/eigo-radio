# er109_known_ng_recheck_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02 D: ユーザーが聞いて指摘した『発音が異なるNG音声』の転写が、是正後のer109で新たにPASSにならないことの確認(API 0)。
# 対象: (1) noguard_reeval_01.json の問題音声21件(take_part_problem_13 + er091 problem 8)・take part A(正常)・byUs presumed_normal 7・ng3_case 12 のP/S/Whisper転写
#       (2) 固定の既知NG対(take part B『Take Tart』/ Melos母音・子音誤読 / byUs blurt『Blur.』ほか)
# 判定: 『現行Production判定が不合格 かつ er109.equivalent』= 新規PASS。問題音声・既知NG対で0が要件。
import json
import sys

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er109_asr_orthographic_equivalence_01 as e109

SRC = "docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/noguard_reeval_01.json"
FIXED = [("take part", "Take Tart."), ("take part", "Take tart"), ("take part", "take apart"), ("take part", "Take Part?"),
         ("Melos", "Mellows"), ("Melos", "Mello"), ("Melos", "Melo"), ("Melos drank", "Mellows drank"), ("Melos", "Melos's"),
         ("blurt", "Blur."), ("blurt", "blur"), ("think up", "Think."), ("by us", "bias"), ("by us", "bus"),
         ("pump one's fist", "pump its fist"), ("pump one's fist", "Pump fist."), ("novelty minaudière", "novelty minaudiere"),
         ("novelty minaudière", "novelty mini odd year")]


def off_pass(c, a):
    cls = val.classify_asr_match(c, a)
    return bool(cls.should_pass or S._step_alternate_pass(cls))


def main():
    t = json.load(open(SRC, encoding="utf-8"))["table"]
    rows, new_pass = [], []
    for r in t:
        for who, text in (("P", r["p"]), ("S", r["s"]), ("W", r.get("A_whisper"))):
            if not text:
                continue
            ex = off_pass(r["canonical"], text)
            eq = e109.evaluate(r["canonical"], text)
            rec = {"corpus": r["corpus"], "id": r["id"], "label": r["label"], "who": who, "canonical": r["canonical"], "text": text,
                   "off_pass": ex, "e109_equiv": eq.equivalent, "verdict": eq.verdict, "rules": eq.rules, "warnings": eq.warnings}
            rows.append(rec)
            if eq.equivalent and not ex:
                new_pass.append(rec)
    fixed = []
    for c, a in FIXED:
        eq = e109.evaluate(c, a)
        fixed.append({"canonical": c, "text": a, "off_pass": off_pass(c, a), "e109_equiv": eq.equivalent, "reason": eq.reason})
    problem = [r for r in rows if str(r["label"]).startswith("problem")]
    s = {"transcripts_evaluated": len(rows), "problem_audio_transcripts": len(problem), "problem_new_pass(要件0)": sum(1 for r in new_pass if str(r["label"]).startswith("problem")),
         "all_new_pass": len(new_pass), "new_pass_by_label": {k: sum(1 for x in new_pass if x["label"] == k) for k in sorted({x["label"] for x in new_pass})},
         "fixed_known_ng_pairs": len(fixed), "fixed_known_ng_new_pass(要件0)": sum(1 for x in fixed if x["e109_equiv"] and not x["off_pass"]),
         "fixed_known_ng_e109_equiv_total": sum(1 for x in fixed if x["e109_equiv"])}
    out = {"generated_by": "er109_known_ng_recheck_01.py", "api_calls": 0, "cost_jpy": 0, "layer_version": e109.LAYER_VERSION, "summary": s,
           "new_pass": new_pass, "fixed": fixed}
    path = "docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/known_ng_recheck_02.json"
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(s, ensure_ascii=False, indent=1))
    for x in new_pass:
        print("NEWPASS", x["label"], x["who"], repr(x["canonical"]), "<-", repr(x["text"]), x["rules"], x["warnings"])
    for x in fixed:
        if x["e109_equiv"]:
            print("FIXED-EQUIV", x)


if __name__ == "__main__":
    main()
