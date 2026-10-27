# -*- coding: utf-8 -*-
"""GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05: evidence run用 フォームpayload(v2)組立(API 0)。
既存の確定(またはauto採用)済みKP選定を再現し、文法は事前生成物(form_grammar_bundle)の全文付きで --grammar-ids の件数だけ載せる。
actorは呼出側で evidence(ユーザー確定ではない)。使い方: gpg5_payload_01.py --run <run> --level a2|b1b --grammar-ids id1[,id2] --out payload.json
  --grammar-ids none=文法0件(omit) / --list=提示Top1/Top2の一覧のみ表示"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
import er119_kp_human_review_01 as rv  # noqa: E402
import er119_grammar_review_01 as gr  # noqa: E402
import er120_part2_wiring_01 as p2w  # noqa: E402
import er128_kp_confirmed_content_01 as cc  # noqa: E402


def build(run, level, gids):
    kp = cc._kp_dir_for(run, level)
    cands, review = rv.load_candidates(kp), rv.load_review(kp)
    cm = {c["candidate_id"]: c for c in cands["candidates"]}
    sel = review["selection"]
    kp_ids = list(sel.get("kp") or [])
    extra = [i for i in (sel.get("vocab") or []) if i not in kp_ids] if level == "b1b" else []

    def item(cid, cat):
        c = cm[cid]
        return {"term": c["item"]["used_form"], "category": cat, "category_label": f"cat{cat}", "ja_gloss": c["item"]["japanese_gloss"],
                "ja_gloss_status": "official", "candidate_id": cid, "kind": c.get("kind") or "phrase"}
    grammar = []
    if gids:
        sd = gr.discover_dirs(run, level)[0]
        bundle = p2w.form_grammar_bundle(sd, level=level)
        by = {i["id"]: i for i in bundle["items"]}
        for gid in gids:
            if gid in by:
                b = by[gid]
                grammar.append({k: b[k] for k in ("id", "candidate_id", "title", "explanation_full", "explanation_status", "explanation_sha256", "example")})
            else:   # Top1/Top2外などを故意に載せる(拒否の実証用): 最小限の項目だけ
                grammar.append({"id": gid, "title": "?", "explanation_status": "provided", "explanation_full": ""})
    return {"schema": "eigo_radio_selection_result_v2", "schema_version": 2, "schema_minor": 1,
            "article": {"slug": (review.get("article_key") or {}).get("slug"), "level": level, "text_sha256": cands["text_sha256"], "candidates_sha256": cands["candidates_sha256"]},
            "selection": {"key_phrase": [item(i, 1) for i in kp_ids], "extra_explanation": [item(i, 2) for i in extra], "meaning_display": [], "grammar": grammar},
            "comment": "[EVIDENCE_RUN] ユーザー確定ではない。GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05のruntime evidence用(actor=evidence)", "ai_reference": {"for_reference_only": True, "items": []},
            "evidence_run": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True); ap.add_argument("--level", required=True, choices=("a2", "b1b"))
    ap.add_argument("--grammar-ids", default="none"); ap.add_argument("--out"); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        sd = gr.discover_dirs(a.run, a.level)[0]
        b = p2w.form_grammar_bundle(sd, level=a.level)
        print(json.dumps({"status": b["grammar_status"], "items": [{"id": i["id"], "rank": i["rank"], "title": i["title"]} for i in b["items"]]}, ensure_ascii=False, indent=1))
        return 0
    gids = [] if a.grammar_ids == "none" else a.grammar_ids.split(",")
    pl = build(a.run, a.level, gids)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(pl, f, ensure_ascii=False, indent=2)
    print(json.dumps({"payload": a.out, "kp": [i["term"] for i in pl["selection"]["key_phrase"]], "extra": [i["term"] for i in pl["selection"]["extra_explanation"]],
                      "grammar": [g["id"] for g in pl["selection"]["grammar"]]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
