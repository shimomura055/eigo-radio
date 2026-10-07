# -*- coding: utf-8 -*-
"""STAGE2-01 委任_02 測定(5): 人間確認パック(human_review_priority_v1.mdの規則)の生成。API無し。
  - 記事単位スコア(候補の最大スコア)の降順で上位10%(切上げ・最低1)の記事の候補文
  - 重大候補全件(V=contradicts / 現行BLOCKINGの既知NGが新構成で非BLOCKINGへ / guard対象の既知NGで格下げが成立したまま)
  - 分かれた文(現行[保存済み]と新構成でBLOCKING有無が分かれた文、2nd opinionがsplitした文)
Checker側の重大度は伏せる(パック本文に出さない)。対応表は eval/_private/HUMAN_PACK_MAP.json。
使い方: python make_pack.py --dev-tag v2 [--heldout-tag final]"""
import argparse
import glob
import json
import math
import pathlib

import replay_lib as L

runner, OUT = L.runner, L.OUT


def norm(s):
    return " ".join((s or "").split())


def load(kind, tag):
    res = {}
    base = OUT / ("replay_heldout" if kind == "heldout" else "replay_dev") / tag
    for f in sorted(glob.glob(str(base / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        if "results" in d:
            res[d["run"]] = d
    return res


def score(x, other_beliefs):
    nw = x["new"]
    rb = nw.get("reader_belief") or {}
    v = rb.get("belief_vs_ledger")
    sc, why = 0, []
    if nw.get("guard_target"):
        sc += 1
        why.append("T:guard_target(" + ",".join(nw.get("guard_types") or []) + ")")
    vv = {"contradicts": 4, "unclear": 3, "unsupported_new_claim": 2}.get(v, 0)
    if vv:
        sc += vv
        why.append(f"V:{v}")
    so = nw.get("so") or {}
    s_a = bool(so.get("belief_only") and (so.get("split") or (so.get("first_belief") != so.get("second_belief"))))
    if s_a:
        sc += 2
        why.append("S-A:2nd_opinion_mismatch")
    beliefs = [b for b in other_beliefs if b]
    s_b = (len(set(beliefs)) > 1) or ("unclear" in beliefs)
    if s_b:
        sc += 2
        why.append("S-B:belief_varies_across_calls")
    if nw["materiality"] != "BLOCKING" and (s_a or s_b):
        sc += 1
        why.append("+1:downgraded_but_uncertain")
    return sc, why


def public_reasons(reasons):
    """Checker側の重大度判定(現行/新構成のどちらがBLOCKINGか)を伏せるため、区分名だけを出す。詳細は非公開の対応表に残す。"""
    out = []
    for r in reasons:
        k = "上位10%記事" if r.startswith("上位10%") else ("重大候補" if r.startswith("重大候補") else "分かれた文")
        if k not in out:
            out.append(k)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev-tag", default="v2")
    ap.add_argument("--dev-other", default="v1")
    ap.add_argument("--heldout-tag", default=None)
    a = ap.parse_args()
    batches = {"dev": (load("dev", a.dev_tag), load("dev", a.dev_other))}
    if a.heldout_tag:
        batches["heldout"] = (load("heldout", a.heldout_tag), {})
    stab = {}
    sp = OUT / "eval" / f"stability_{a.dev_tag}.json"
    if sp.exists():
        for r in json.loads(sp.read_text(encoding="utf-8"))["rows"]:
            stab[(r["run"], norm(r["claim"]))] = r["beliefs"]
    known = {}
    for kind in batches:
        for it in L.dev_items(kind):
            if it.get("matched_claim"):
                known[(it["run"], norm(it["matched_claim"]))] = it
    entries, private = [], []
    for kind, (new, other) in batches.items():
        cand = []
        for run, d in new.items():
            for x in d["results"]:
                ob = []
                o = next((y for y in (other.get(run) or {"results": []})["results"] if norm(y["claim_text"]) == norm(x["claim_text"])), None)
                if o:
                    ob.append((o["new"].get("reader_belief") or {}).get("belief_vs_ledger"))
                ob.append((x["new"].get("reader_belief") or {}).get("belief_vs_ledger"))
                ob += stab.get((run, norm(x["claim_text"])[:120]), [])
                sc, why = score(x, ob)
                cand.append({"kind": kind, "run": run, "x": x, "score": sc, "why": why})
        by_art = {}
        for c in cand:
            by_art.setdefault(c["run"], []).append(c)
        art_rank = sorted(by_art, key=lambda r: (-max(c["score"] for c in by_art[r]), -len(by_art[r]), r))
        top_n = max(1, math.ceil(0.10 * len(art_rank)))
        top_arts = set(art_rank[:top_n])
        for c in cand:
            x, nw = c["x"], c["x"]["new"]
            rb = nw.get("reader_belief") or {}
            reasons = []
            if c["run"] in top_arts and c["score"] > 0:
                reasons.append("上位10%記事")
            if rb.get("belief_vs_ledger") == "contradicts":
                reasons.append("重大候補:belief=contradicts")
            k = known.get((c["run"], norm(x["claim_text"])))
            if k and x["saved"]["materiality"] == "BLOCKING" and nw["materiality"] != "BLOCKING":
                reasons.append("重大候補:現行BLOCKINGの既知NGが新構成で非BLOCKING")
            if k and nw["materiality"] != "BLOCKING" and nw.get("guard_target") and k.get("guard_type") in ("主体", "全称", "否定・不在", "数値", "方向・極性"):
                reasons.append("重大候補:ガード対象型の既知NGが格下げ成立")
            if (x["saved"]["materiality"] == "BLOCKING") != (nw["materiality"] == "BLOCKING"):
                reasons.append("分かれた文(現行と新構成でBLOCKING有無が相違)")
            so = nw.get("so") or {}
            if so.get("split"):
                reasons.append("分かれた文(2nd opinion split)")
            if reasons:
                c["reasons"] = reasons
                entries.append(c)
    entries.sort(key=lambda c: (c["kind"], c["run"], norm(c["x"]["claim_text"])))
    lines = ["# 人間確認パック(STAGE2-01 委任_02 段階2)", "",
             "位置づけ: 人間が独立に重大度を付ける確認用。**Checker側の重大度判定は伏せてある**(対応表は非公開 `eval/_private/HUMAN_PACK_MAP.json`)。",
             "確認の順位付けであり重大の判定ではない。人間確認の結果は副指標(上位10%内の重大捕捉率)の評価に使う(合否ラインには含めない)。", "",
             "記入欄: 重大度 = 重大 / 軽微 / 問題なし のいずれか、コメントは自由。", ""]
    for i, c in enumerate(entries, 1):
        x, nw = c["x"], c["x"]["new"]
        rb = nw.get("reader_belief") or {}
        run, ledger, art = L.load_run(c["run"]) if c["kind"] == "dev" else L.load_run(c["run"])
        fid = x.get("related_fact_id")
        block = runner.floor_verify_fact_block(ledger, fid) or "(該当factなし)"
        para = next((p for p in art.split("\n\n") if norm(x["claim_text"])[:40] in norm(p)), "")
        pid = f"HR-{i:03d}"
        private.append({"id": pid, "kind": c["kind"], "run": c["run"], "claim": x["claim_text"], "saved_materiality": x["saved"]["materiality"],
                        "new_materiality": nw["materiality"], "score": c["score"], "reasons": c["reasons"], "why": c["why"],
                        "floor_reason": nw.get("floor_reason")})
        lines += [f"## {pid}", f"- 該当文: {x['claim_text']}", f"- 文脈段落: {para[:600]}", f"- 関連Ledger({fid}): {block[:500]}",
                  f"- reader_belief(新構成のLLM記述): {rb.get('reader_belief') or '(なし)'}",
                  f"- contradicting_fact_ids: {rb.get('contradicting_fact_ids') or []}",
                  f"- 使った信号: {', '.join(c['why']) or 'なし'}", f"- パックに入れた区分: {', '.join(public_reasons(c['reasons']))}",
                  "- 重大度(人間記入): ____", "- コメント: ____", ""]
    (OUT / "eval").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / "_private").mkdir(exist_ok=True, parents=True)
    (OUT / "eval" / "HUMAN_REVIEW_PACK_STAGE2.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "eval" / "_private" / "HUMAN_PACK_MAP.json").write_text(json.dumps(private, ensure_ascii=False, indent=1), encoding="utf-8")
    print("entries", len(entries), {k: sum(1 for p in private if p["kind"] == k) for k in batches})


if __name__ == "__main__":
    main()
