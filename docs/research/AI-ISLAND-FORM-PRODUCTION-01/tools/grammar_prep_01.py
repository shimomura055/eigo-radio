# -*- coding: utf-8 -*-
# AI-ISLAND-FORM-PRODUCTION-01 委任_01: 今回記事限りの暫定事前生成(Standard/Advanced。正式配線とは区別)。
# Production関数(origin/main commit固定版 ER_REV=b27d88309: er119_kp_human_review_01 / er119_grammar_review_01 / er120_part2_grammar_production_01 / er120_part2_wiring_01)を
# 無変更でimportし、候補抽出(Step A'')→全候補Step B解説(PREGEN_MAX=8, ref_ja=None)→フォーム用bundleを書く。Prompt/model/閾値は不変。
# 書込みは --out 配下のみ(既存のproduction run dirは読取専用)。並行Agentの作業ツリー編集の影響を避けるため git show で固定版を読む。
import argparse, hashlib, json, os, shutil, subprocess, sys, time, types
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
ER_REV = os.environ.get("ER_REV", "b27d88309")
MODS = ["er119_kp_human_review_01", "er119_grammar_review_01", "er120_part2_grammar_production_01", "er120_part2_wiring_01"]
BLOBS = {}
for name in MODS:
    src = subprocess.run(["git", "show", f"{ER_REV}:{name}.py"], capture_output=True, check=True).stdout
    BLOBS[name] = hashlib.sha256(src).hexdigest()
    m = types.ModuleType(name)
    m.__file__ = os.path.join(ROOT, name + ".py")
    sys.modules[name] = m
    exec(compile(src.decode("utf-8"), f"git:{ER_REV}:{name}.py", "exec"), m.__dict__)
g = sys.modules["er120_part2_grammar_production_01"]
gr = sys.modules["er119_grammar_review_01"]
w = sys.modules["er120_part2_wiring_01"]

SRC_RUN = "er019_output/ai_island_temple/run_ai_01"
OLD_STUDY = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01/b1b/study_text"   # 旧Adv候補(Step A''済・未提示/未確定)。再利用=API 0
FAMILY, SLUG = "x", "ai_island_temple"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True, choices=("a2", "b1b"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, default=12.0)
    ap.add_argument("--reuse-old-adv", action="store_true", help="b1b: 旧run_ai_01の候補doc(同一本文・同一signature)を再利用しStep A''を呼ばない")
    a = ap.parse_args()
    level = a.level
    article = open(f"{SRC_RUN}/{level}/article.md", encoding="utf-8").read()
    paragraphs, label = g.paragraphs_from_article_md(article), w.label_for(article)
    sd = f"{a.out}/{level}/study_text"
    os.makedirs(sd, exist_ok=True)
    if a.reuse_old_adv and level == "b1b":
        for fn in ("grammar_candidates.json", "grammar_human_review.json"):
            if not os.path.exists(f"{sd}/{fn}"):
                shutil.copy2(f"{OLD_STUDY}/{fn}", f"{sd}/{fn}")
    state = {"calls": 0}
    def guard(stage, est):
        state["calls"] += 1
        if state["calls"] * 0.9 > a.budget_jpy:     # 実測上限0.88/call
            raise SystemExit(f"BUDGET_GUARD: calls={state['calls']} cap={a.budget_jpy}")
    t0 = time.time()
    res = w.candidate_and_pregen_stage(sd, level=level, run_dir=a.out, family=FAMILY, slug=SLUG, paragraphs=paragraphs, label=label,
                                       next_command=f"py docs/research/AI-ISLAND-FORM-PRODUCTION-01/tools/grammar_prep_01.py --level {level} --out {a.out}",
                                       run_hint=a.out, budget_guard=guard)
    bundle = w.form_grammar_bundle(sd, level=level)
    json.dump(bundle, open(f"{sd}/form_grammar_bundle.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    doc = gr.load_candidates(sd)
    ex = gr.load_explanations(sd)
    cost = {"step_a": (doc.get("audit") or {}).get("total_cost_jpy"), "step_b": [(i["candidate_id"], (i.get("audit") or {}).get("total_cost_jpy")) for i in ex["items"]]}
    step_a_new = (cost["step_a"] or 0) if res.get("generated") else 0.0      # 再利用した候補docのStep A''費用は過去runで計上済み(今回の新規費用に数えない)
    total = round(step_a_new + sum(c or 0 for _, c in cost["step_b"]), 4)
    summ = {"level": level, "er_rev": ER_REV, "blob_sha256": BLOBS, "stepa_prompt_sha256": g.STEPA_PROMPT_SHA256, "stepb_prompt_sha256": g.STEPB_PROMPT_SHA256,
            "model": g.MODEL, "text_sha256": doc["text_sha256"], "candidates_sha256": doc["candidates_sha256"], "n_candidates": len(doc["candidates"]),
            "n_explanations": len(ex["items"]), "generated": res["pregen"]["generated"], "reused": res["pregen"]["reused"], "extract_generated": res.get("generated"),
            "grammar_status": bundle["grammar_status"], "cost": cost, "step_a_new_jpy": step_a_new, "total_cost_jpy": total, "elapsed_sec": round(time.time() - t0, 1),
            "ref_ja": None, "provisional_note": "今回記事限りの暫定事前生成(正式Production配線=GRAMMAR-PREGEN-ALL-LEVELS-01 とは別。ユーザー指示2026-10-27 §4)"}
    json.dump(summ, open(f"{a.out}/summary_{level}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(f"{a.out}/raw_usage_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S%z"), level=level, cost_jpy=total, detail=cost, model=g.MODEL), ensure_ascii=False) + "\n")
    print(json.dumps({k: summ[k] for k in ("level", "n_candidates", "n_explanations", "generated", "reused", "extract_generated", "total_cost_jpy", "grammar_status")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
