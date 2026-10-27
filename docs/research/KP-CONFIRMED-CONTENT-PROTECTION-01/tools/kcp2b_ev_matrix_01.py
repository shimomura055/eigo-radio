# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B: 改変マトリクス(API 0・決定論)。
確定済みのコピーdirで、確定後に成果物を1件ずつ書換え → G1〜G4が止める(BLOCK/INTEGRITY rc=3相当)ことを記録し、必ず元のバイト列へ戻す。
元run・公開済み成果物は触らない(コピーdirのみ)。

  kcp2b_ev_matrix_01.py --family x|y|z --run <copy> --out <json>
"""
from __future__ import annotations

import argparse
import json
import os
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


class Tamper:
    """ファイルを退避し、改変→チェック→必ず復元する。"""

    def __init__(self, *paths):
        self.paths = [p for p in paths if p]
        self.bak = {}

    def __enter__(self):
        for p in self.paths:
            with open(p, "rb") as f:
                self.bak[p] = f.read()
        return self

    def __exit__(self, *a):
        for p, b in self.bak.items():
            with open(p, "wb") as f:
                f.write(b)


def outcome(fn):
    try:
        fn()
        return {"result": "PASS(止まらない)"}
    except rv.ConfirmedContentIssue as e:
        return {"result": "ISSUE(rc=4)", "class": type(e).__name__, "message": str(e)[:300]}
    except rv.ConfirmedContentIntegrityViolation as e:
        return {"result": "BLOCK(INTEGRITY rc=3)", "class": type(e).__name__, "message": str(e)[:200], "diff": _first_diff(e)}
    except Exception as e:  # noqa: BLE001
        return {"result": "BLOCK(" + type(e).__name__ + ")", "message": str(e)[:300]}


def _first_diff(e):
    msg = str(e)
    return msg[msg.find("["):][:300] if "[" in msg else msg[:300]


def run_family(fam, run):
    res = []
    out_levels = []
    if fam == "x":
        cfg = {"a2": dict(kp=f"{run}/a2/key_phrases", tts=f"{run}/a2/audit/tts_generation_results.json", pages=[f"{run}/player.html"], assets=None),
               "b1b": dict(kp=f"{run}/b1b/key_phrases", tts=f"{run}/b1b/audit/tts_generation_results.json", vocab_pages=[f"{run}/player.html"],
                           study=f"{run}/b1b/study_text/part1_vocabulary_expressions.json", sdir=f"{run}/b1b/study_text", assets=None)}
    elif fam == "y":
        cfg = {"a2": dict(kp=f"{run}/key_phrases/a2", tts=f"{run}/a2/audit/tts_generation_results.json", pages=[f"{run}/pages/index.html"],
                          assets=f"{run}/a2/key_phrases/keywords_canonicalized.json"),
               "b1b": dict(kp=f"{run}/key_phrases/b1b", tts=f"{run}/b1b/audit/tts_generation_results.json", assets=f"{run}/b1b/key_phrases/keywords_canonicalized.json")}
    else:
        cfg = {"b1b": dict(kp=f"{run}/key_phrases/b1b", tts=f"{run}/b1b/audit/tts_generation_results.json", vocab_pages=[f"{run}/pages_ev/index.html"],
                           study=f"{run}/study_text/part1_vocabulary_expressions.json", sdir=f"{run}/study_text",
                           assets=f"{run}/b1b/key_phrases/keywords_canonicalized.json")}
    for lv, c in cfg.items():
        kp = c["kp"]
        rec = cc.load_record(kp)
        if rec is None:
            res.append({"level": lv, "case": "(no record)", "result": "SKIP"})
            continue
        rp = rv.paths(kp)
        items = [i for i in rec["items"] if i["slot"] == "kp"]
        first = items[0]

        def g1():
            rv.require_final_consistent(kp, level=lv, require_src_contract=False, assets_json=c.get("assets"))

        def add(gate, case, r):
            res.append({"level": lv, "gate": gate, "case": case, **r})

        add("G1", "baseline(改変なし)", outcome(g1))
        # --- G1 ---
        for gate, case, path, mut in [
            ("G1", "kp英語(used_form)を書換え", rp["kp"], lambda d: _set_item(d, first["candidate_id"], "used_form", lambda v: v + " XX")),
            ("G1", "kp日本語訳(japanese_gloss)を書換え", rp["kp"], lambda d: _set_item(d, first["candidate_id"], "japanese_gloss", lambda v: (v or "") + "改変")),
        ]:
            with Tamper(path):
                d = jl(path)
                mut(d)
                jd(path, d)
                add(gate, case, outcome(g1))
        if os.path.exists(rp["vocab"]) and lv == "b1b":
            with Tamper(rp["vocab"]):
                d = jl(rp["vocab"])
                _set_item(d, first["candidate_id"], "japanese_gloss", lambda v: (v or "") + "改変")
                jd(rp["vocab"], d)
                add("G1", "vocab日本語訳(Part 1入力)を書換え", outcome(g1))
        # category: reviewのkp集合から1件外す(=カテゴリ変更)。署名は再計算して保存(署名で止まるのではなくレコード突合で止まることを示す)
        with Tamper(rp["review"]):
            r = jl(rp["review"])
            ks = list(r["selection"]["kp"])
            r["selection"]["kp"] = ks[1:]
            r["selection_signature"] = rv.selection_signature(r)
            jd(rp["review"], r)
            add("G1", "category(KP→対象外/説明語)変更(review選定を書換え+署名再計算)", outcome(g1))
        if c.get("assets") and os.path.exists(c["assets"]):
            with Tamper(c["assets"]):
                d = jl(c["assets"])
                if any(i.get("candidate_id") == first["candidate_id"] for i in d.get("items") or []):
                    _set_item(d, first["candidate_id"], "japanese_gloss", lambda v: (v or "") + "改変")
                    jd(c["assets"], d)
                    add("G1", "assets copy(Y/Z)の日本語訳を書換え", outcome(g1))
        # --- G2 ---
        if os.path.exists(c["tts"]):
            def g2():
                cc.verify_outputs(kp, lv, tts_results_path=c["tts"])
            add("G2", "baseline", outcome(g2))
            k1 = str(_rank_of(rp["kp"], first["candidate_id"]))
            with Tamper(c["tts"]):
                d = jl(c["tts"])
                ent = (d.get("key_phrases") or {}).get(k1) or {}
                e = ent.get("english") or {}
                for kk in ("text", "canonical_text"):
                    if kk in e:
                        e[kk] = e[kk] + " XX"
                jd(c["tts"], d)
                add("G2", "TTS recordの英語を書換え", outcome(g2))
            if lv == "a2":
                with Tamper(c["tts"]):
                    d = jl(c["tts"])
                    jm = ((d.get("key_phrases") or {}).get(k1) or {}).get("japanese_meaning") or {}
                    for kk in ("text", "canonical_text"):
                        if kk in jm:
                            jm[kk] = "別の訳"
                    jd(c["tts"], d)
                    add("G2", "TTS recordの日本語(japanese_meaning)を別訳へ", outcome(g2))
        # --- G3 ---
        if lv == "a2" and c.get("pages"):
            pg = c["pages"][0]

            def g3():
                cc.verify_outputs(kp, lv, page_paths=c["pages"])
            add("G3", "baseline(ページに確定訳が出ている)", outcome(g3))
            with Tamper(pg):
                t = open(pg, encoding="utf-8").read()
                n = t.count(first["japanese_gloss"])
                t2 = t.replace(first["japanese_gloss"], "【別の訳】")
                open(pg, "w", encoding="utf-8").write(t2)
                r = outcome(g3)
                r["replaced_occurrences"] = n
                add("G3", "ページの日本語訳を別訳へ", r)
        if lv == "b1b" and c.get("vocab_pages") and c.get("study") and os.path.exists(c["study"]):
            def g3b():
                cc.verify_outputs(kp, lv, study_text_json=c["study"], vocab_page_paths=c["vocab_pages"])
            add("G3", "baseline(Part 1が描画)", outcome(g3b))
            with Tamper(c["study"]):
                d = jl(c["study"])
                for rw in d.get("rows") or []:
                    if rw.get("english_expression") == first["used_form"]:
                        rw["meaning_in_text_ja"] = "別の訳"
                jd(c["study"], d)
                add("G3", "Part 1行(meaning_in_text_ja)を別訳へ", outcome(g3b))
        # --- G4 ---
        if lv == "b1b" and c.get("sdir") and os.path.exists(f"{c['sdir']}/part2_result.json"):
            pr = f"{c['sdir']}/part2_result.json"

            def g4():
                cc.verify_part2(c["sdir"], jl(pr))
            add("G4", "baseline", outcome(g4))
            with Tamper(pr):
                d = jl(pr)
                d["explanation_md"] = (d.get("explanation_md") or "") + "\n(確定後に書換え)"
                jd(pr, d)
                add("G4", "文法の解説全文(explanation_md)を書換え", outcome(g4))
            with Tamper(pr):
                d = jl(pr)
                if d.get("translation_ja") is not None:
                    d["translation_ja"] = "別の訳"
                jd(pr, d)
                add("G4", "文法の日本語訳(translation_ja)を書換え", outcome(g4))
            with Tamper(pr):
                d = jl(pr)
                (d.get("selection") or {})["sentence"] = ((d.get("selection") or {}).get("sentence") or "") + " X"
                jd(pr, d)
                add("G4", "文法の選定文を書換え", outcome(g4))
        add("G1", "全復元後のbaseline(改変の復元確認)", outcome(g1))
    return res


def _rank_of(kp_json, cid):
    for i in jl(kp_json).get("items") or []:
        if i.get("candidate_id") == cid:
            return i.get("rank")
    return None


def _set_item(doc, cid, field, fn):
    for i in doc.get("items") or []:
        if i.get("candidate_id") == cid:
            i[field] = fn(i.get(field))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run_family(a.family, a.run)
    jd(a.out, res)
    for r in res:
        print(f"{r.get('level')} {r.get('gate')} | {r.get('case')} => {r.get('result')}" + (f" | {r.get('diff')[:120]}" if r.get("diff") else ""))


if __name__ == "__main__":
    main()
