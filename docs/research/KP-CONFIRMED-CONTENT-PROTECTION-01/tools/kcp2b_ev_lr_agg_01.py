# -*- coding: utf-8 -*-
"""既存のLocal Rewrite(LR)発火記録(er011_output/local_rewrite_recovery)について、LRが書き換えた語範囲と同一runのKP(keywords_canonicalized.json)との重なりを
er128.lr_overlap で集計する(API 0・read-only)。LRの挙動は変更しない。"""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
import er128_kp_confirmed_content_01 as cc  # noqa: E402

BS = chr(92)
rows, total, no_run, resolved = [], 0, 0, 0
for f in sorted(glob.glob("er011_output/local_rewrite_recovery/**/*.json", recursive=True)):
    f = f.replace(BS, "/")
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(d, dict) or d.get("status") != "RESOLVED_BY_LOCAL_REWRITE":
        continue
    total += 1
    before = d.get("canonical_text") or ""
    after = ((d.get("selection") or {}).get("selected") or {}).get("rewritten_segment") or (d.get("retts_result") or {}).get("text") or ""
    path = ((d.get("retts_result") or {}).get("path") or "").replace(BS, "/")
    lv = "a2" if "/a2/" in path else ("b1b" if "/b1b/" in path else None)
    run = path.split("/" + lv + "/")[0] if lv else None
    kwf = [p for p in (f"{run}/key_phrases/{lv}/keywords_canonicalized.json", f"{run}/{lv}/key_phrases/keywords_canonicalized.json") if run and os.path.exists(p)] if lv else []
    if not kwf:
        no_run += 1
        continue
    resolved += 1
    items = [{"candidate_id": f"{it.get('rank')}", "used_form": it.get("used_form"), "display_phrase": it.get("display_phrase"), "key_phrase": it.get("key_phrase")}
             for it in (json.load(open(kwf[0], encoding="utf-8")).get("items") or [])]
    ov = cc.lr_overlap(items, before, after)
    rows.append({"file": f, "segment": d.get("segment_id"), "run": run, "level": lv, "kp_count": len(items), "overlap": [{"form": o["form"], "before_snippet": o["before_snippet"]} for o in ov]})
hit = [r for r in rows if r["overlap"]]
print(json.dumps({"lr_resolved_records_total": total, "mapped_to_run_with_kp": resolved, "run_not_resolvable(path無し等)": no_run, "records_with_kp_overlap": len(hit), "overlap_rate": (round(len(hit) / resolved, 3) if resolved else None),
                  "overlap_examples": hit[:12]}, ensure_ascii=False, indent=1))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence_runs", "lr_overlap_aggregate.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
