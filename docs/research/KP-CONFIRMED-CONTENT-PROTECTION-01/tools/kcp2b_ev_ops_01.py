# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_02B: 実artifact(コピーdir)に対する STALE(再バインド/ISSUE)・resume・操作ガード・Part 2 MODEL patch の evidence(API 0)。
各ケースの前に kp_dir/mirror/study_text を退避し、ケース後に必ず元へ戻す。generate_fn/redundancy_fn は呼ばれたら失敗する(=API 0の証明)。

  kcp2b_ev_ops_01.py --family x|y|z --run <copy> --text-<lv> <path|canon:y|canon:z> --out <json>
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)

import er119_kp_human_review_01 as rv  # noqa: E402
import er128_kp_confirmed_content_01 as cc  # noqa: E402


def jl(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class Called(AssertionError):
    pass


def _gen(*a, **k):
    raise Called("generate_fn(候補生成API)が呼ばれた")


RED_CALLS = []


def _red(items, name):
    """確定集合へのRedundancy QA(既存仕様M-8。finalizeのたびに実runnerでは約¥0.06の1回呼出)。evidenceではstub(PASS)で呼出回数だけ数える。"""
    RED_CALLS.append(name)
    return {"status": "REDUNDANCY_PASS", "duplicate_pairs": [], "model_id": "stub-evidence"}


@contextlib.contextmanager
def snapshot(*dirs_files):
    tmp = tempfile.mkdtemp(prefix="kcp2b_snap_")
    saved = []
    for i, p in enumerate(dirs_files):
        if p and os.path.exists(p):
            dst = os.path.join(tmp, str(i))
            (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, dst)
            saved.append((p, dst))
    try:
        yield
    finally:
        for p, dst in saved:
            if os.path.isdir(p):
                shutil.rmtree(p)
                shutil.copytree(dst, p)
            else:
                shutil.copy2(dst, p)
        shutil.rmtree(tmp, ignore_errors=True)


def load_text(spec):
    if spec.startswith("canon:y"):
        import er121_family_y_structure_01 as ys
        return ys.canonical_body(open(spec.split(":", 2)[2], encoding="utf-8").read())
    if spec.startswith("canon:z"):
        import er026_family_z_fiction_production_runner_01 as zr
        return zr.canonical_article_text(open(spec.split(":", 2)[2], encoding="utf-8").read())
    return open(spec, encoding="utf-8").read()


def ensure(kp, run, family, slug, lv, text):
    return rv.ensure_kp_review(kp, run_dir=run, family=family, slug=slug, level=lv, text=text, generate_fn=_gen, redundancy_fn=_red)


def case(fn):
    del RED_CALLS[:]
    try:
        v = fn()
        if isinstance(v, dict):
            v["generate_fn_calls"] = 0   # 呼ばれれば例外(Called)になる
            v["redundancy_qa_stub_calls"] = len(RED_CALLS)
        return {"ok": True, "value": v}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error_class": type(e).__name__, "error": str(e)[:400]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--text", action="append", default=[], help="<level>=<spec>")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = []
    for ts in a.text:
        lv, spec = ts.split("=", 1)
        kp = cc._kp_dir_for(a.run, lv)
        text = load_text(spec)
        pth = cc.paths_of(kp)
        rec0 = cc.load_record(kp)
        snaps = (kp, os.path.dirname(pth["mirror"]), os.path.join(a.run, lv, "study_text"), os.path.join(a.run, "study_text"))

        def add(name, r):
            res.append({"family": a.family, "level": lv, "case": name, **r})

        # (c1) resume: 同一本文でensure → FINALIZED/API 0/レコード不変
        with snapshot(*snaps):
            def resume():
                r = ensure(kp, a.run, a.family, a.slug, lv, text)
                rec1 = cc.load_record(kp)
                return {"state": r["state"], "record_sha_unchanged": rec1["record_sha256"] == rec0["record_sha256"] if "record_sha256" in rec0 else rec1 == rec0,
                        "revision": rec1["revision"]}
            add("resume(同一本文・API 0)", case(resume))
        # (c2) rebind: 出典文に触れない追記 → 再バインド(API 0・確定内容不変・revision+1)
        with snapshot(*snaps):
            def rebind():
                r = ensure(kp, a.run, a.family, a.slug, lv, text.rstrip("\n") + "\n\nThis added closing line does not touch any confirmed source sentence.\n")
                rec1 = cc.load_record(kp)
                g1 = None
                try:
                    rv.require_final_consistent(kp, level=lv, require_src_contract=False)
                    g1 = "PASS"
                except Exception as e:  # noqa: BLE001
                    g1 = type(e).__name__
                return {"state": r["state"], "revision_before": rec0["revision"], "revision_after": rec1["revision"], "content_sha256_unchanged": rec1["content_sha256"] == rec0["content_sha256"],
                        "last_event": rec1["history"][-1]["event"], "g1_after": g1}
            add("STALE再バインド(出典文以外の本文変更・API 0)", case(rebind))
        # (c3) ISSUE: 確定項目の出典文を変更 → ISSUE(PENDING confirmed_content_issue)・確定内容不変
        with snapshot(*snaps):
            def issue():
                cands = rv.load_candidates(kp)
                cm = {c["candidate_id"]: c for c in cands["candidates"]}
                sent = cc._source_sentence_of(cm[rec0["items"][0]["candidate_id"]])
                w = max((x for x in cc._norm_ws(sent).replace(",", " ").split() if x.isalpha()), key=len)   # 出典文中の最長の語を本文全体で書換え
                new_text = text.replace(w, w + "XX")
                assert new_text != text and cc._norm_ws(sent) not in cc._norm_ws(new_text), "fixture: 出典文が実際に変わっていない"
                r = ensure(kp, a.run, a.family, a.slug, lv, new_text)
                rec1 = cc.load_record(kp)
                iss = jl(pth["issue_json"]) if os.path.exists(pth["issue_json"]) else None
                return {"state": r["state"], "reason": (r.get("pending") or {}).get("reason"), "record_unchanged": rec1 == rec0,
                        "issue_kind": (iss or {}).get("kind"), "issue_fields": [d["field"] for d in (iss or {}).get("diffs") or []]}
            add("STALE ISSUE(確定項目の出典文を変更・黙って破棄しない)", case(issue))
        # (d) 操作ガード: select/reselect/ng/resolve-gloss/declare-absent を CLI から呼ぶ
        for op in ("select", "reselect", "ng", "resolve-gloss", "declare-absent", "revoke-needed"):
            if op == "revoke-needed":
                continue
            with snapshot(*snaps):
                def g(op=op):
                    cc.guard(kp, op)
                    return "(拒否されなかった)"
                add(f"操作ガード {op}", case(g))
        # (e) ISSUE rc=4: 仮訳(provisional)のgloss付きフォームの confirm は ISSUE
        with snapshot(*snaps):
            def prov():
                import copy
                pl = jl(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence_runs", a.family, f"payload_{lv}.json"))
                pl = copy.deepcopy(pl)
                pl["selection"]["key_phrase"][0]["ja_gloss"] = "仮の訳"
                pl["selection"]["key_phrase"][0]["ja_gloss_status"] = "provisional"
                tmpf = os.path.join(tempfile.mkdtemp(prefix="kcp2b_pl_"), "payload_prov.json")
                json.dump(pl, open(tmpf, "w", encoding="utf-8"), ensure_ascii=False)
                # 既にユーザー確定済みなので confirm --from-form 自体が拒否される(上書きしない)。revoke後ならISSUE。ここでは「確定済みへの再confirm拒否」を記録
                return cc.cmd_from_form(a.run, lv, tmpf, "evidence-runner", "docs/pm/ACTIVE_TASK.md", actor=cc.ACTOR_EVIDENCE)
            add("再confirm(確定済みへの上書き)拒否", case(prov))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    for r in res:
        print(f"{r['family']} {r['level']} | {r['case']} => " + (json.dumps(r.get('value'), ensure_ascii=False) if r["ok"] else f"{r['error_class']}: {r['error'][:180]}"))


if __name__ == "__main__":
    main()
