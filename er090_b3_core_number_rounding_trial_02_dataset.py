# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03 Phase0 データセット構築(API 0、Trial専用)。
既存の B3出力(research_ledger + storyline_b3)を ROOT/dataset/<id>/ へcopyし、Production決定論producer
(er053_b3_deterministic_producer_01.produce_annotated_b3、無改変)で中核数値を機械的に選定する。
ledger sha256が同じrun=同一記事(テーマ)として重複除去。1記事1 brief(中核数値が最多のもの、同数は優先リストの先頭)。
"""
import hashlib, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import er053_b3_deterministic_producer_01 as prod
import er090_b3_core_number_rounding_trial_01_overlay as ov
ROOT = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_02")
SCAN = ("er019_output", "er052_output", "er053_output", "er012_output", "er026_output")
PRIORITY = ("er019_output/",)   # Production run(Writer出力が残る)を優先


def sha_b(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def candidates():
    seen = {}
    for base in SCAN:
        for dp, _dn, fn in os.walk(os.path.join(HERE, base)):
            if dp.endswith("storyline_b3") and "selected_brief.md" in fn and "fact_selection_evidence.json" in fn:
                run = os.path.dirname(dp)
                if "failed" in run or "_before_regen" in run:
                    continue
                lp = os.path.join(run, "research_ledger", "verified_fact_ledger.txt")
                if os.path.exists(lp):
                    seen.setdefault(sha_b(lp), []).append(os.path.relpath(run, HERE).replace("\\", "/"))
    return seen


def main():
    seen = candidates()
    ddir = os.path.join(ROOT, "dataset")
    manifest = []
    for lsha, runs in sorted(seen.items(), key=lambda kv: kv[1][0]):
        best = None
        for run in sorted(runs, key=lambda r: (not r.startswith(PRIORITY), r)):
            tmp = os.path.join(ROOT, "_tmp_build")
            shutil.rmtree(tmp, ignore_errors=True)
            for sub in ("research_ledger", "storyline_b3"):
                shutil.copytree(os.path.join(HERE, run, sub), os.path.join(tmp, sub))
            try:
                prod.produce_annotated_b3(tmp)
            except Exception:
                continue
            sc = json.load(open(os.path.join(tmp, "storyline_b3", "annotation.json"), encoding="utf-8"))
            n = len(ov.core_concepts(sc))
            if best is None or n > best[0]:
                if best:
                    shutil.rmtree(best[2], ignore_errors=True)
                dst = os.path.join(ROOT, "_tmp_best_" + lsha[:8])
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(tmp, dst)
                best = (n, run, dst, sc)
        shutil.rmtree(os.path.join(ROOT, "_tmp_build"), ignore_errors=True)
        if not best:
            continue
        n, run, dst, sc = best
        aid = "art_" + lsha[:8]
        final = os.path.join(ddir, aid)
        shutil.rmtree(final, ignore_errors=True)
        os.makedirs(ddir, exist_ok=True)
        shutil.move(dst, final)
        theme = run.split("/")
        has = {k: os.path.exists(os.path.join(HERE, run, p)) for k, p in
               (("ja_r2", "ja_writer/revision2.md"), ("advanced", "b1b/article.md"), ("standard", "a2/article.md"))}
        manifest.append({"article_id": aid, "ledger_sha256": lsha, "source_run": run, "n_same_ledger_runs": len(runs),
                         "n_facts": len(sc["facts"]), "n_core_concepts": n, "n_core_surfaces": sum(1 for x in sc["numbers"] if x["class"] == "core"),
                         "n_peripheral": sum(1 for x in sc["numbers"] if x["class"] == "peripheral"), "existing_outputs": has,
                         "core": [{"concept": c["concept"], "kind": c["kind"], "surfaces": c["surfaces"], "ledger_ids": c["ledger_ids"]} for c in ov.core_concepts(sc)]})
    with open(os.path.join(ROOT, "dataset_manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("articles", len(manifest), "with_core", sum(1 for m in manifest if m["n_core_concepts"]), "concepts", sum(m["n_core_concepts"] for m in manifest))
    for m in manifest:
        print(m["article_id"], m["source_run"], m["n_facts"], m["n_core_concepts"], [c["surfaces"] for c in m["core"]])


if __name__ == "__main__":
    main()
