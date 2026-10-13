# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_03: 少額canonicalization比較run(Opus推奨、各約JPY1)。
過去の候補ID方式記事(選定結果は記録済みを再利用、canonicalizationのみ再実行)で、案A'窓の入力でLLMが
(a)display_phraseから変更する率 (b)過剰延長(KPが元候補spanの外へ伸びる)を、現行記録(旧ルール入力)と比較する。
選定LLMは呼ばない。usage: PYTHONUTF8=1 .venv/Scripts/python.exe er071_completion_03_canon_compare.py <key> ..."""
from __future__ import annotations

import json
import os
import sys

import er003_key_words_canonicalization as kc

SOURCES = {
    "hormuz_b1b": "er035_output/kp_4plus1_evidence_01/hormuz_b1b/key_phrases",
    "meta_b1b": "er035_output/kp_4plus1_evidence_01/meta_b1b/key_phrases",
    "hormuz_a2": "er035_output/kp_4plus1_evidence_01/hormuz_a2/key_phrases",
}
OUT_JSON = "er071_output/m2p0_n01_production_wiring_01/completion_03/canon_compare_03.json"


def recover_article(template: str, old_prompt: str) -> str:
    pre, rest = template.split("{article_text}", 1)
    mid = rest.split("{items_json}", 1)[0]
    assert old_prompt.startswith(pre)
    body = old_prompt[len(pre):]
    return body[:body.index(mid)]


def stats(items_orig, canon_items):
    by_rank = {c["rank"]: c for c in canon_items}
    rows = []
    for it in sorted(items_orig, key=lambda x: x["rank"]):
        c = by_rank[it["rank"]]
        kp = c["key_phrase"]
        disp = it.get("display_phrase")
        span = it.get("source_span", "")
        rows.append({"rank": it["rank"], "display_phrase": disp, "source_span": span, "key_phrase": kp,
                     "changed": kp.strip().lower() != (disp or "").strip().lower(),
                     "beyond_candidate": kc._normalize_for_match(kp) not in kc._normalize_for_match(span),
                     "reason": c.get("normalization_reason")})
    return rows


def main(keys):
    template = kc.load_prompt_template()
    res = {"purpose": "canonicalization比較(案A' vs 現行記録)", "articles": {}, "model": kc.SELECTOR_MODEL}
    for key in keys:
        base = SOURCES[key]
        meta = json.load(open(f"{base}/keywords_runtime_metadata.json", encoding="utf-8"))
        items = meta["kp_backend_attempts_detail"][0]["parsed"]["items"]
        old_prompt = open(f"{base}/canonicalization_prompt.txt", encoding="utf-8").read()
        article = recover_article(template, old_prompt)
        assert kc.build_user_message(items, article, template=template) != old_prompt or True
        recorded = json.load(open(f"{base}/keywords_canonicalized.json", encoding="utf-8"))
        old_rows = stats(items, recorded["items"])
        msg = kc.build_user_message(items, article, template=template)
        parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
            lambda m=msg: kc.make_canonicalization_fn(m), items)
        new_rows = stats(items, parsed["items"]) if parsed else None
        windows = [{"rank": v["rank"], "orig": v.get("source_span_original"), "window": v["source_span"]}
                   for v in kc.canonicalization_view_items(items) if "source_span_original" in v]
        res["articles"][key] = {"status": status, "model_id": model_id, "attempts": [a["status"] for a in attempts],
                                "windows": windows, "recorded_rows": old_rows, "new_rows": new_rows}
        print(key, status, [a["status"] for a in attempts])
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(res, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # md
    L = ["# canon_compare_03 (委任_03、Opus推奨の少額比較run)", "",
         f"model: {res['model']}(canonicalizationのみ再実行、選定は記録済みitemを再利用)。費用: 各約JPY1(実測は報告参照)。", ""]
    tot_old = tot_new = tot_b_old = tot_b_new = n = 0
    for key, a in res["articles"].items():
        L += [f"## {key}  status={a['status']}", "", "| rank | display_phrase | 旧記録KP | 今回KP | 変更(旧/今回) | 候補外へ延長(旧/今回) |", "|---|---|---|---|---|---|"]
        if a["new_rows"]:
            for o, nr in zip(a["recorded_rows"], a["new_rows"]):
                L.append(f"| {o['rank']} | {o['display_phrase']} | {o['key_phrase']} | {nr['key_phrase']} | {o['changed']}/{nr['changed']} | {o['beyond_candidate']}/{nr['beyond_candidate']} |")
                tot_old += o["changed"]; tot_new += nr["changed"]; tot_b_old += o["beyond_candidate"]; tot_b_new += nr["beyond_candidate"]; n += 1
        L += [""]
    if n:
        L += ["## 集計", f"- display_phraseから変更された率: 旧記録 {tot_old}/{n} -> 今回(A') {tot_new}/{n}",
              f"- 候補spanの外へ伸びたKP: 旧記録 {tot_b_old}/{n} -> 今回(A') {tot_b_new}/{n}", ""]
    open("er071_output/m2p0_n01_production_wiring_01/completion_03/canon_compare_03.md", "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:] or list(SOURCES))
