"""KP-RESCUE-REJUDGE-REVERT-SURFACE-FIX-01 ev01: 救済済み項目のQA再判定を、永続化された実run記録(work/keywords_canonicalized.json)から公式経路
(er125.finalize_rescued_items -> qa_rejudge)でreplayする。記事・音声の再生成なし、canonicalization/gloss/選定のAPI呼出なし。
fixed=修正後(wt)の実API 1 call/ファイル。old=origin/mainの修正前er125に『同じ生応答』を与えて判定(API 0)。
usage: python run_replay_rejudge.py <repo_root> <main_tree_root> <old_er125_path>"""
import sys, os, json, glob, re, importlib.util, hashlib
ROOT = os.path.abspath(sys.argv[1]); MAIN = os.path.abspath(sys.argv[2]); OLD = os.path.abspath(sys.argv[3])
sys.path.insert(0, ROOT); os.chdir(ROOT)
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
EV = os.path.join(ROOT, "docs/research/KP-RESCUE-REJUDGE-REVERT-SURFACE-FIX-01/ev01")
CAP = float(os.environ.get("RRF_CAP", "10.0"))
import er005_cost_logger as cl
import er003_key_words_canonicalization as kc
import er006_model_routing_contract_01 as routing
import er062_family_z_structure_01 as st
import er119_kp_human_review_01 as rv
import er125_kp_rescue_production_01 as new125
spec = importlib.util.spec_from_file_location("er125_old", OLD); old125 = importlib.util.module_from_spec(spec); spec.loader.exec_module(old125)
assert not hasattr(old125, "_revert_origin_key") and hasattr(new125, "_revert_origin_key")
os.environ["EIGO_KP_RESCUE"] = "1"

def spent():
    # 費用はPython側で集計せず(er053の依存連鎖がsparse checkoutで読めない)、件数ガードで代替: 1 call/ケース(4ケース)で上限固定。実費はer053で後から集計(cost_summary.json)
    return 0.0

cl.install(f"{EV}/cost_log_replay.jsonl")
BASE = "er019_output/family_x_audio_production_wiring_01"
CASES = {
    "ai_chat_b1b__counted_as_having_failed": f"{BASE}/ai_chat_sponsored_persuasion__run_fx4_01/b1b/key_phrases/kp_candidates/round_1/work",
    "jwst_a2__limited_the_search_to": f"{BASE}/jwst_mystery_emission_line__run_fx4_01/a2/key_phrases/kp_candidates/round_1/work",
    "untidi_a2__gets_heated_relied": f"{BASE}/untidiness_family_resource__run_fx4_01/a2/key_phrases/kp_candidates/round_1/work",
    "untidi_b1b_backfill__gets_heated": f"{BASE}/untidiness_family_resource__run_fx4_01/b1b/key_phrases/kp_candidates/round_1/work/backfill_1",
}
model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
out = {"model": model, "cases": {}}
for name, rel in CASES.items():
    d = os.path.join(MAIN, rel)
    merged = json.load(open(os.path.join(d, "keywords_canonicalized.json"), encoding="utf-8"))
    prompt = open(os.path.join(d, "canonicalization_prompt.txt"), encoding="utf-8").read()
    m = re.search(r"【記事本文\(参考、文脈確認用\)】\n(.*?)\n\n【Key Phrase候補\(JSON\)】", prompt, re.S)
    text = m.group(1)
    canon = {it["rank"]: it["rescue"]["canonicalization"] for it in merged["items"] if (it.get("rescue") or {}).get("canonicalization")}
    sel = {it["rank"]: it["rescue"]["selection"] for it in merged["items"] if (it.get("rescue") or {}).get("selection")}
    parsed = {"items": [{"rank": rk, "kp_rescue": canon[rk]} for rk in sorted(canon)]}
    originals = [{"rank": rk, "selection_rescue": sel[rk]} for rk in sorted(sel)]
    persisted = {rk: next(it for it in merged["items"] if it["rank"] == rk)["rescue"] for rk in canon}
    if spent() + 0.5 > CAP: raise SystemExit("cost guard")
    st.check_stop_sentinel("rrf_replay", EV)
    cap = {}
    def qa_call(msg, cap=cap, name=name):
        with cl.logging_context("RRF_fix01", "replay_" + name):
            r = kc.make_canonicalization_fn(msg, model=model, schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)()
        cap["raw"], cap["model"], cap["rid"] = r
        return r
    fixed = new125.finalize_rescued_items(merged, parsed, originals, text, qa_call_fn=qa_call)
    raw = cap["raw"]
    old = old125.finalize_rescued_items(merged, parsed, originals, text, qa_call_fn=lambda msg: (raw, cap["model"], cap["rid"]))   # 同じ生応答を修正前コードへ(API 0)
    by_llm = {x.get("rank"): x for x in (kc.parse_canonicalization_json(raw).get("items") or [])}
    rows = []
    for n, rk in enumerate(sorted(canon), start=1):
        fi = next(it for it in fixed["items"] if it["rank"] == rk); oi = next(it for it in old["items"] if it["rank"] == rk)
        llm = by_llm.get(n) or {}
        qa_fail = [f for f in kc.QA_FIELDS if llm.get(f) == "FAIL"]
        # 提示可否(Production fail-closedの当該部分): gloss再整合は永続化済みの値を使い、rescue_unverified以外の要因は評価しない
        def blk(item):
            rs = dict(item["rescue"]); rs["gloss"] = persisted[rk].get("gloss")
            c = {"item": {"qa_overall_status": item.get("qa_overall_status", "PASS"), "qa": item.get("qa") or {}, "rescue": rs},
                 "japanese_gloss": "x", "gates": {"gloss": "ALIGNED"}, "flags": {}}
            return [b[0] for b in rv.presentation_blockers(c)]
        rows.append({"rank": rk, "key_phrase_surface": fi["key_phrase"], "display_phrase": fi.get("display_phrase"), "rescue_code": canon[rk]["code"],
                     "rescue_llm_key_phrase(見出し形)": canon[rk].get("llm_key_phrase"), "qa_llm_returned_key_phrase": llm.get("key_phrase"),
                     "persisted_in_run": {"qa_status": persisted[rk]["qa"]["status"], "error": persisted[rk]["qa"].get("error")},
                     "before_fix_replay": {"qa_status": oi["rescue"]["qa"]["status"], "error": oi["rescue"]["qa"].get("error"), "blockers": blk(oi)},
                     "after_fix": {"qa_status": fi["rescue"]["qa"]["status"], "error": fi["rescue"]["qa"].get("error"), "qa_overall_status": fi.get("qa_overall_status"),
                                   "qa_fail_fields": [k for k, v in (fi.get("qa") or {}).items() if v == "FAIL"], "blockers": blk(fi)}})
    out["cases"][name] = {"dir": rel, "model_id": cap["model"], "response_id": cap["rid"], "raw_response_text": raw, "n_rescued_ranks": len(canon), "rows": rows}
    print(name, [(r["display_phrase"], r["rescue_code"], r["before_fix_replay"]["qa_status"], "->", r["after_fix"]["qa_status"], r["after_fix"]["blockers"]) for r in rows], "spent", round(spent(), 3)); sys.stdout.flush()
json.dump(out, open(f"{EV}/replay_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("DONE spent", round(spent(), 3))
