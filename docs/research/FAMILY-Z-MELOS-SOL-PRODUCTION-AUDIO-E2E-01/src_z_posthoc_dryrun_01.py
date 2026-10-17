# -*- coding: utf-8 -*-
"""委任_15 W7: SRC(Source Reference Contract) D1強化版「z_sentence_id_posthoc_v1」のオフライン解決dry-run。
JPY0・API呼出なし・Production code非接続(読み取りのみ。run dirへ書かない)。実装は#109(ユーザー判断)回答後。

方式(Opus R-C3 (d)):
  1. level本文(canonical article text)を er030_key_phrase_db_hybrid_core_01.build_sentence_units で S1..Sn に分割(X Production使用中の既存関数)
  2. 各KP itemの(source_sentence, source_span)を次の順で文IDへ解決: (i)正規化完全一致 (ii)唯一の包含関係(文がsource_sentenceに含まれ、かつspanを含む)
     (iii)spanを含む文が唯一(span offset一意)。曖昧(複数候補)または該当なしは STOP 扱い(自動採用しない)
  3. 解決した文IDから er030_..._source_reference_contract_01.restore_source_fields で source_sentence/source_span をPythonが復元(LLM自由記述に依存しない)
     context_sentence_idがNoneのときspanで代用するfallback(同:463-464)は本方式では禁止(STOP)
  4. 既存値と復元値の一致/差異を記録(差異=LLMのsource_sentenceが複数文にまたがる等)
label案: z_sentence_id_posthoc_v1(承認済みcandidate_id_v1ではない。『LLMに自由記述させない出力契約』の部分は非適用=Strategy L維持のため)
実行: .venv/Scripts/python.exe docs/research/FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01/src_z_posthoc_dryrun_01.py --run-dir <run> --out <json>"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import er003_key_words_min_unit as p2g                      # noqa: E402  (_normalize_for_match: SRC restoreと同じ正規化)
import er030_key_phrase_db_hybrid_core_01 as core           # noqa: E402
import er030_key_phrase_db_hybrid_source_reference_contract_01 as src  # noqa: E402

LABEL = "z_sentence_id_posthoc_v1"
LEVEL_TEXT = {"a2": "writer/std.md", "b1b": "writer/r2.md"}


def _body(md: str) -> str:
    """runnerのcanonical_article_text相当(タイトル行[# ...]を除き段落を空行区切りで連結)を最小再現。"""
    lines = md.splitlines()
    out = [ln for ln in lines if not ln.strip().startswith("#")]
    paras, cur = [], []
    for ln in out:
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(paras)


def resolve_item(units, item):
    """returns (method, [sentence_ids]) ; method in exact|unique_containment|unique_span|ambiguous|unresolved"""
    n = p2g._normalize_for_match
    ss, span = n(item.get("source_sentence") or ""), n(item.get("source_span") or item.get("used_form") or "")
    norm_units = [(f"S{i + 1}", n(u["raw_text"])) for i, u in enumerate(units)]
    exact = [sid for sid, t in norm_units if t == ss]
    if len(exact) == 1:
        return "exact", exact
    if len(exact) > 1:
        return "ambiguous", exact
    cont = [sid for sid, t in norm_units if t and t in ss and span and span in t]
    if len(cont) == 1:
        return "unique_containment", cont
    if len(cont) > 1:
        return "ambiguous", cont
    byspan = [sid for sid, t in norm_units if span and span in t]
    if len(byspan) == 1:
        return "unique_span", byspan
    if len(byspan) > 1:
        return "ambiguous", byspan
    return "unresolved", []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    report = {"label": LABEL, "run_dir": a.run_dir, "levels": {}, "totals": {}}
    tot = {"items": 0, "resolved": 0, "ambiguous": 0, "unresolved": 0, "restored_equal_existing": 0,
           "restored_differs_from_existing": 0, "methods": {}, "categories": {}}
    for lv, rel in LEVEL_TEXT.items():
        text = open(os.path.join(a.run_dir, rel), encoding="utf-8").read()
        units = core.build_sentence_units(_body(text))
        kp = json.load(open(os.path.join(a.run_dir, f"key_phrases/{lv}/keywords_canonicalized.json"), encoding="utf-8"))
        sentence_reference = {f"S{i + 1}": u["raw_text"] for i, u in enumerate(units)}
        quote_units = [f"S{i + 1}" for i, u in enumerate(units) if '"' in u["raw_text"]]
        # 元本文で引用符を含む文が、分割後に引用符が欠落/ずれていないかの粗い確認(閉じ引用符は build_sentence_units が剥がす)
        body_norm = p2g._normalize_for_match(_body(text))
        items_out, cand_map, req_items = [], {}, []
        for it in sorted(kp["items"], key=lambda x: x["rank"]):
            method, sids = resolve_item(units, it)
            rec = {"rank": it["rank"], "used_form": it.get("used_form"), "existing_source_span": it.get("source_span"),
                   "existing_source_sentence": it.get("source_sentence"), "method": method, "sentence_ids": sids,
                   "span_in_existing_sentence": p2g._normalize_for_match(it.get("source_span") or "") in
                   p2g._normalize_for_match(it.get("source_sentence") or "")}
            tot["items"] += 1
            tot["methods"][method] = tot["methods"].get(method, 0) + 1
            if method in ("exact", "unique_containment", "unique_span"):
                tot["resolved"] += 1
                cid = f"Z{lv}_{it['rank']}"
                cand_map[cid] = {"surface_form": it.get("source_span") or it.get("used_form"), "context_sentence_id": sids[0],
                                 "observed_surface_variants": []}
                req_items.append({"rank": it["rank"], "source_candidate_id": cid})
            elif method == "ambiguous":
                tot["ambiguous"] += 1
            else:
                tot["unresolved"] += 1
            items_out.append(rec)
        restored = src.restore_source_fields(req_items, cand_map, sentence_reference)
        by_rank = {r["rank"]: r for r in restored["items"]}
        for rec in items_out:
            r = by_rank.get(rec["rank"])
            if rec["method"] in ("exact", "unique_containment", "unique_span") and r:
                rec["restored_source_span"] = r.get("source_span")
                rec["restored_source_sentence"] = r.get("source_sentence")
                same = (p2g._normalize_for_match(r.get("source_sentence") or "") == p2g._normalize_for_match(rec["existing_source_sentence"] or "")
                        and p2g._normalize_for_match(r.get("source_span") or "") == p2g._normalize_for_match(rec["existing_source_span"] or ""))
                rec["restored_equals_existing"] = same
                an = lambda t: re.sub(r"[^a-z0-9]", "", p2g._normalize_for_match(t or ""))   # 句読点・引用符・空白を除いた比較
                ra, ea = an(r.get("source_sentence")), an(rec["existing_source_sentence"])
                rec["restored_equals_existing_modulo_punct"] = ra == ea
                # 既存source_sentenceが複数文/引用符内複数文にまたがり、復元値がその一部(1文)になる境界差
                rec["boundary_difference_restored_is_subset"] = (ra != ea) and (ra in ea)
                rec["span_preserved"] = (p2g._normalize_for_match(r.get("source_span") or "")
                                         == p2g._normalize_for_match(rec["existing_source_span"] or ""))
                cat = ("equal" if same else "equal_modulo_punct" if ra == ea else "boundary_subset" if ra in ea else "content_differs")
                rec["difference_category"] = cat
                tot["categories"][cat] = tot["categories"].get(cat, 0) + 1
                tot["restored_equal_existing" if same else "restored_differs_from_existing"] += 1
        report["levels"][lv] = {"text": rel, "sentence_units": len(units), "units_with_double_quote_after_split": quote_units,
                                "items": items_out, "restore_unresolved": restored.get("unresolved"),
                                "restore_mismatch_count": restored.get("mismatch_count")}
    report["totals"] = tot
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(tot, ensure_ascii=False))


if __name__ == "__main__":
    main()
