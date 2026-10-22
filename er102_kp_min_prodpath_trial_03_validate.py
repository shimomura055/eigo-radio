# -*- coding: utf-8 -*-
"""KPMP3 機械検証(API 0)。Arm A/Bの最終keywords_canonicalized.json(Production関数列の最終出力)を読み、
語数・本文一致(source_span)・重複・5件充足・既存Production KPとの一致・A/B一致・例示追跡を集計。"""
import json, re, statistics, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "er102_output" / "kp_min_prodpath_trial_03"
MAN = ROOT / "er098_output" / "kp_six_model_trial_01" / "inputs" / "manifest.json"
EXAMPLES = {"think up what happens next": ["think up"], "formal agreements with their creators": ["agreements", "agreement"], "alone caused the different results": ["caused", "cause"]}

def nz(s): return re.sub(r"\s+", " ", re.sub(r"[“”\"'‘’]", "", (s or "")).strip().rstrip(".,;:!?")).lower()
def words(s): return len((s or "").split())
def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else None

def arm_set(arm, uid):
    rd = OUT / "runs" / arm / uid
    rr = load(rd / "result.json")
    kp = load(rd / "key_phrases" / "keywords_canonicalized.json")
    info = {"arm": arm, "unit_id": uid, "has_result": rr is not None}
    if rr is None: info["status"] = "NO_RESULT"; info["items"] = []; return info
    res = rr["result"]
    sel = res.get("selection") or {}
    canon = res.get("canonicalization") or {}
    info.update(status=res.get("status") or canon.get("status") or sel.get("status") or res.get("exception"),
                selection_status=sel.get("status"), canon_status=canon.get("status"),
                redundancy_status=(res.get("redundancy_qa") or {}).get("status"),
                redundancy_attempts=res.get("redundancy_retry_attempts"), retry_log=res.get("redundancy_retry_log"),
                kp_backend_used=sel.get("kp_backend_used"), m2_fallback_events=res.get("m2_fallback_events"),
                elapsed_s=rr.get("elapsed_s"), exception=res.get("exception"))
    info["items"] = (kp or {}).get("items") or []
    # canonicalizationが失敗(INVALID等)したrunでは、ディスク上のkeywords_canonicalized.jsonは前attempt(Redundancy retry前)の残骸になり得る。
    # Production最終出力としては採用しない(statusが正)。残骸の存在だけ記録する。
    if info.get("canon_status") not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED") or info.get("selection_status") not in (None, "KEY_WORDS_STRUCTURE_PASS"):
        info["stale_disk_items"] = len(info["items"]); info["items"] = []
    return info

def main():
    man = json.loads(MAN.read_text(encoding="utf-8")); units = man["units"]
    out = {"units": {}, "summary": {}}
    for u in units:
        uid = u["unit_id"]; art = (ROOT / u["copy_path"]).read_text(encoding="utf-8"); art_n = nz(art)
        prod = u["production_kp"]
        d = {"production": [dict(rank=p["rank"], key_phrase=p["key_phrase"], display_phrase=p["display_phrase"], source_span=p["source_span"], role=p.get("role")) for p in prod]}
        for arm in ("A", "B"):
            s = arm_set(arm, uid); rows = []
            seen = set()
            for it in s["items"]:
                kpz = nz(it.get("key_phrase")); dup = kpz in seen; seen.add(kpz)
                rows.append(dict(rank=it["rank"], source_span=it.get("source_span"), display_phrase=it.get("display_phrase"), key_phrase=it.get("key_phrase"),
                                 role=it.get("key_phrase_role"), gloss=it.get("japanese_gloss"),
                                 words_display=words(it.get("display_phrase")), words_key=words(it.get("key_phrase")), words_span=words(it.get("source_span")),
                                 span_in_text=nz(it.get("source_span")) in art_n, display_le5=words(it.get("display_phrase")) <= 5, key_le5=words(it.get("key_phrase")) <= 5,
                                 duplicate=dup, changed_by_canon=(nz(it.get("key_phrase")) != nz(it.get("display_phrase"))), candidate_id=it.get("source_candidate_id")))
            s["rows"] = rows; del s["items"]; d[arm] = s
        # 一致
        pset_k = {nz(p["key_phrase"]) for p in prod}; pset_s = {nz(p["source_span"]) for p in prod}
        pset_d = {nz(p["display_phrase"]) for p in prod}
        for arm in ("A", "B"):
            rows = d[arm]["rows"]
            d[arm]["match_prod_key"] = sum(nz(r["key_phrase"]) in pset_k for r in rows)
            d[arm]["match_prod_span"] = sum(nz(r["source_span"]) in pset_s for r in rows)
            d[arm]["match_prod_display"] = sum(nz(r["display_phrase"]) in pset_d for r in rows)
        ra, rb = d["A"]["rows"], d["B"]["rows"]
        d["AB_match_key"] = len({nz(r["key_phrase"]) for r in ra} & {nz(r["key_phrase"]) for r in rb})
        d["AB_match_span"] = len({nz(r["source_span"]) for r in ra} & {nz(r["source_span"]) for r in rb})
        out["units"][uid] = d
    # summary
    def stat(vals):
        return None if not vals else dict(n=len(vals), mean=round(statistics.mean(vals), 3), median=statistics.median(vals), dist={k: vals.count(k) for k in range(1, 8)}, share5=round(vals.count(5) / len(vals), 3), le2=round(sum(1 for v in vals if v <= 2) / len(vals), 3))
    S = {}
    for arm in ("A", "B"):
        rows = [r for d in out["units"].values() for r in d[arm]["rows"]]
        sets = [d[arm] for d in out["units"].values()]
        S[arm] = dict(sets_ok=sum(1 for s in sets if s["rows"]), sets_5=sum(1 for s in sets if len(s["rows"]) == 5), status={k: sum(1 for s in sets if s["status"] == k) for k in {s["status"] for s in sets}},
                      display_words=stat([r["words_display"] for r in rows]), key_words=stat([r["words_key"] for r in rows]), span_words=stat([r["words_span"] for r in rows]),
                      over5_display=sum(not r["display_le5"] for r in rows), over5_key=sum(not r["key_le5"] for r in rows), span_not_in_text=sum(not r["span_in_text"] for r in rows),
                      duplicates=sum(r["duplicate"] for r in rows), changed_by_canon=sum(r["changed_by_canon"] for r in rows),
                      match_prod_key=sum(d[arm]["match_prod_key"] for d in out["units"].values()), match_prod_span=sum(d[arm]["match_prod_span"] for d in out["units"].values()),
                      match_prod_display=sum(d[arm]["match_prod_display"] for d in out["units"].values()),
                      fallback=sum(1 for s in sets if s.get("kp_backend_used") not in (None, "db_hybrid")), retries=sum(1 for s in sets if (s.get("redundancy_attempts") or 0) > 0),
                      roles={k: sum(1 for r in rows if r["role"] == k) for k in ("important", "topic")})
    common = [uid for uid, d in out["units"].items() if d["A"]["rows"] and d["B"]["rows"]]
    S["paired_units"] = common
    for arm in ("A", "B"):
        rows = [r for uid in common for r in out["units"][uid][arm]["rows"]]
        S["paired_" + arm] = dict(n=len(rows), display_words=stat([r["words_display"] for r in rows]), key_words=stat([r["words_key"] for r in rows]), span_words=stat([r["words_span"] for r in rows]),
                                  match_prod_span=sum(out["units"][uid][arm]["match_prod_span"] for uid in common), match_prod_key=sum(out["units"][uid][arm]["match_prod_key"] for uid in common))
    S["paired_AB_match_span"] = sum(out["units"][uid]["AB_match_span"] for uid in common)
    prow = [p for u in man["units"] for p in u["production_kp"]]
    S["production"] = dict(display_words=stat([words(p["display_phrase"]) for p in prow]), key_words=stat([words(p["key_phrase"]) for p in prow]), span_words=stat([words(p["source_span"]) for p in prow]), n=len(prow))
    S["AB_match_key"] = sum(d["AB_match_key"] for d in out["units"].values()); S["AB_match_span"] = sum(d["AB_match_span"] for d in out["units"].values())
    # 例示
    ex = {}
    for name, toks in EXAMPLES.items():
        ex[name] = {}
        for arm in ("A", "B", "production"):
            hits = []
            for uid, d in out["units"].items():
                rows = d[arm]["rows"] if arm != "production" else d["production"]
                for r in rows:
                    blob = nz(r.get("source_span")) + " | " + nz(r.get("display_phrase")) + " | " + nz(r.get("key_phrase"))
                    if any(t in blob for t in toks) and any(nz(name).split()[0] in blob for _ in [0]):
                        hits.append(dict(unit=uid, source_span=r.get("source_span"), display=r.get("display_phrase"), key=r.get("key_phrase")))
            ex[name][arm] = hits
    S["examples"] = ex
    out["summary"] = S
    (OUT / "validation.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(S, ensure_ascii=False, indent=1))
if __name__ == "__main__": sys.exit(main())
