# -*- coding: utf-8 -*-
"""KCP委任_03 evidence用(コピーdirのみ・API 0): 旧run(KP Human Review導入前)のZ a2に、既存のa2 KP成果物(keywords_canonicalized.json)を
「候補生成の結果」として注入してKP review(候補+review)を作る。実runnerの `--stages kp` が新記事のa2で行う候補生成→pending を、
LLMなし(generate_hookに既存KPを返す)で再現する。再現した後に `confirm --from-form --actor evidence` で確定し、実runnerを回す。
使い方: .venv python kcp3_ev_z_a2_seed_01.py --run <copy> --slug melos"""
import argparse, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
import er119_kp_candidates_01 as kcand  # noqa: E402
import er119_kp_wiring_01 as kw  # noqa: E402
import er026_family_z_fiction_production_runner_01 as zr  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--level", default="a2")
    a = ap.parse_args()
    run = a.run.replace("\\", "/").rstrip("/")
    lv = a.level
    text = zr.canonical_article_text(open(f"{run}/writer/r2.md", encoding="utf-8").read()) if False else None
    import er062_family_z_writer_01 as w62
    text = zr.canonical_article_text(w62.rd(w62.level_text_path(run, lv)))
    items = json.load(open(f"{run}/key_phrases/{lv}/keywords_canonicalized.json", encoding="utf-8"))["items"]

    def gen(round_no, ng_entries):
        return {"ok": True, "doc": kcand.candidate_doc_from_items(items, lv, round_no=round_no)}

    def red(items_, name):
        return {"status": "REDUNDANCY_PASS", "duplicate_pairs": [], "model_id": None, "response_id": None, "attempts_detail": [], "skipped": "evidence seed: API 0"}
    res = kw.run_kp_with_review(text=text, kp_dir=f"{run}/key_phrases/{lv}", run_dir=run, family="z", slug=a.slug, level=lv,
                                article_id=f"family_z_{a.slug}_{w62.LEVEL_DIR[lv]}", stop_run_dir=run, generate_hook=gen, redundancy_hook=red,
                                src_fn=None, person_repair_fn=None, run_hint=run, stop_check_fn=lambda w: None, guard_fn=None)
    print(json.dumps({"state": (res.get("kp_review") or {}).get("state"), "status": res.get("status"), "n_items": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
