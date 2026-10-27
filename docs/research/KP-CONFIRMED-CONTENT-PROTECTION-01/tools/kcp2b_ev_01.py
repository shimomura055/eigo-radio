# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B: runtime evidence用の小道具(API 0・決定論)。
既存の確定済みrunを**コピーしたdir**に対して、(1)フォームpayload(v2)の組立 (2)確定後の改変試行(→BLOCKの記録) (3)Part 2 MODEL patch (4)STALE を行う。
元run・公開済みの成果物は変更しない(コピーdirのみ操作)。レコードのactorは `evidence`(ユーザー確定ではない)。

使い方(リポジトリrootで .venv\\Scripts\\python.exe):
  kcp2b_ev_01.py payload  --run <copy> --level b1b|a2 [--grammar] --out <payload.json>
  kcp2b_ev_01.py g1       --run <copy> --level b1b|a2 [--assets <keywords_canonicalized.json>]     # require_final_consistent(G1)の結果をJSONで出力
  kcp2b_ev_01.py tamper   --run <copy> --level b1b|a2 --case <name> [--assets ...] [--tts ...] [--pages ...] ...   # 1件改変→G1〜G4→BLOCK記録→必ず元へ戻す
  kcp2b_ev_01.py stale    --run <copy> --level ... --family x|y|z --slug S --case rebind|issue
  kcp2b_ev_01.py part2    --run <copy> --study-dir <dir> --label L    # MODEL patchでも再抽出/再解説しない
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)

import er119_kp_human_review_01 as rv  # noqa: E402
import er128_kp_confirmed_content_01 as cc  # noqa: E402


def jl(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def jd(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=2)


def kp_dir_of(run, level):
    return cc._kp_dir_for(run, level)


def build_payload(run, level, with_grammar):
    kp = kp_dir_of(run, level)
    cands, review = rv.load_candidates(kp), rv.load_review(kp)
    cm = {c["candidate_id"]: c for c in cands["candidates"]}
    sel = review["selection"]
    kp_ids = list(sel.get("kp") or [])
    vocab_extra = [i for i in (sel.get("vocab") or []) if i not in kp_ids] if level == "b1b" else []

    def item(cid, cat):
        c = cm[cid]
        return {"term": c["item"]["used_form"], "category": cat, "category_label": f"cat{cat}", "ja_gloss": c["item"]["japanese_gloss"], "ja_gloss_status": "official",
                "candidate_id": cid, "kind": c.get("kind") or "phrase"}
    grammar = []
    if with_grammar:
        import er119_grammar_review_01 as gr
        sds = gr.discover_dirs(run)
        if sds:
            gd, grev = gr.load_candidates(sds[0]), gr.load_review(sds[0])
            cid = (grev.get("selection") or {}).get("candidate_id")
            gc = next((c for c in gd["candidates"] if c["candidate_id"] == cid), None)
            if gc:
                grammar.append({"id": cid, "title": gc.get("construct_ja"), "explanation_status": "missing", "explanation_full": None})
    return {"schema": "eigo_radio_selection_result_v2", "schema_version": 2, "schema_minor": 1,
            "article": {"slug": (review.get("article_key") or {}).get("slug"), "level": level, "text_sha256": cands["text_sha256"], "candidates_sha256": cands["candidates_sha256"]},
            "selection": {"key_phrase": [item(i, 1) for i in kp_ids], "extra_explanation": [item(i, 2) for i in vocab_extra], "meaning_display": [], "grammar": grammar},
            "comment": "[EVIDENCE_RUN] ユーザー確定ではない。runtime evidence用に、既存の確定済み選択をフォームpayload形式で再現したもの", "ai_reference": {"for_reference_only": True, "items": []},
            "evidence_run": True}


def g1(run, level, assets=None):
    kp = kp_dir_of(run, level)
    try:
        rv.require_final_consistent(kp, level=level, require_src_contract=False, assets_json=assets)
        return {"result": "PASS"}
    except rv.ConfirmedContentIssue as e:
        return {"result": "ISSUE(rc=4)", "class": type(e).__name__, "message": str(e)[:400]}
    except rv.ConfirmedContentIntegrityViolation as e:
        return {"result": "BLOCK(INTEGRITY, rc=3)", "class": type(e).__name__, "message": str(e)[:600], "issue": _issue(kp)}
    except rv.KpReviewError as e:
        return {"result": "BLOCK(" + type(e).__name__ + ")", "message": str(e)[:600]}


def _issue(kp):
    p = cc.paths_of(kp)["issue_json"]
    return jl(p) if os.path.exists(p) else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("payload")
    p.add_argument("--run", required=True)
    p.add_argument("--level", required=True)
    p.add_argument("--grammar", action="store_true")
    p.add_argument("--out", required=True)
    p = sub.add_parser("g1")
    p.add_argument("--run", required=True)
    p.add_argument("--level", required=True)
    p.add_argument("--assets", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "payload":
        pl = build_payload(a.run, a.level, a.grammar)
        jd(a.out, pl)
        print(json.dumps({"payload": a.out, "kp": [i["term"] for i in pl["selection"]["key_phrase"]], "extra": [i["term"] for i in pl["selection"]["extra_explanation"]],
                          "grammar": pl["selection"]["grammar"]}, ensure_ascii=False))
    elif a.cmd == "g1":
        print(json.dumps(g1(a.run, a.level, a.assets), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
