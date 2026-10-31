"""ev01 補足: run_forced_eval.py のL3対象が上限8件で'put away'(★)に届かなかったため、'put away'のみ公式run_l3(GEN5->VER5->CHK5)を1回実行する。usage: python run_l3_put_away.py <repo_root>"""
import sys, os, json, glob
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
EV = os.path.join(ROOT, "docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/ev01")
CAP = float(os.environ.get("N5Q_CAP", "13.0"))
import er005_cost_logger as cl, er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5
import er062_family_z_structure_01 as st
import er105_kp_fulltext_selector_01 as ft
def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log*.jsonl"))
cl.install(f"{EV}/cost_log_l3_put_away.jsonl")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
text = fx["cases"]["untidi_b1b"]["text"]
if spent() + 1.0 > CAP: raise SystemExit("cost guard")
st.check_stop_sentinel("n5q_l3", EV)
ctx = n5.N5Ctx("B1_SUPPORT", tag="forced_l3_put_away", stop_check_fn=lambda w: st.check_stop_sentinel(w, EV), article_id="N5Q_untidi_b1b")
tg = []
for s in ["put away"]:
    c = {"span": s, "sentence": ""}; n5._fill_sentence(text, c)
    tg.append({"key": ft.phrase_key(s), "span": s, "sentence": c["sentence"], "prod_gloss": None, "n5_origin": "B1"})
with cl.logging_context("N5Q_audit", "forced_l3_put_away"):
    r = n5.run_l3(text, tg, ctx)
out = {"targets": tg, "kept": {k: n5.pack(v) for k, v in r["kept"].items()}, "dropped": r["dropped"], "metas": ctx.metas}
json.dump(out, open(f"{EV}/l3_put_away_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: (v.get("display_form"), v.get("gloss_ja"), (v.get("check") or {}).get("relation")) for k, v in out["kept"].items()}, ensure_ascii=False), out["dropped"]); print("DONE spent", round(spent(), 3))
