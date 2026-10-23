"""ASR-TIME-NUMERAL-EQUIVALENCE-01 replay基盤(2/2): pairs_01.jsonl の各対を正式経路の純関数で判定して結果jsonを保存する。
  value_guard (er078 _guard_en), classify_asr_match (er006), tier1_numeric_equivalence (er021) の3層を記録。
  --modules DIR : 候補(修正案)のmodule複製を置いたdirを sys.path 先頭へ置いて import する(未指定=HEAD=ベースライン)。
  比較: py replay_compare_01.py base.json cand.json
API 0・読み取り専用。
"""
import sys, os, json, argparse
ap = argparse.ArgumentParser(); ap.add_argument("--pairs", default="pairs_01.jsonl"); ap.add_argument("--out", required=True); ap.add_argument("--modules", default=None); ap.add_argument("--repo", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")); a = ap.parse_args()
a.pairs = os.path.abspath(a.pairs); a.out = os.path.abspath(a.out)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(a.repo))
if a.modules: sys.path.insert(0, os.path.abspath(a.modules))
sys.path.append(HERE)
os.chdir(os.path.abspath(a.repo))
import er078_asr_value_guard_01 as vg
import er006_preprod_hardening_01_validation as val
import er021_en_asr_semantic_equivalence_production_01 as t1
import judge_sim_01 as js
print("modules:", vg.__file__, t1.__file__, flush=True)
out = {}; err = 0
for l in open(a.pairs, encoding="utf-8"):
    r = json.loads(l); c, x = r["canon"], r["asr"]
    try: g = vg.value_guard(c, x, "en").kind
    except Exception as e: g = "ERR"; err += 1
    try:
        m = val.classify_asr_match(c, x); cl = ["P" if m.should_pass else "N", getattr(m, "classification", None)]
    except Exception as e: cl = ["ERR", str(e)[:40]]
    try: t = t1.tier1_numeric_equivalence(c, x) is not None
    except Exception: t = "ERR"
    try: st, rc, _ = js.judge_primary(c, x)
    except Exception as e: st, rc = "ERR", str(e)[:40]
    out[r["id"]] = {"vg": g, "cls": cl, "tier1": t, "state": st, "reason": rc}
json.dump(out, open(a.out, "w"), ensure_ascii=False)
print("judged", len(out), "errors", err)
