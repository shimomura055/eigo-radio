# e2_acceptable_pairs_01.py -- OF-OOV-03: E2が(条件上)受理しうる『Ledger候補 x CMU語』の全件リスト(API 0・読取専用)。
# 再生成: .venv\Scripts\python.exe docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/e2_acceptable_pairs_01.py [--ledger <path>] [--out-md <path>] [--out-json <path>]
# 条件(trial_direct_ledger_phoneme_01 と同一): ledger_disabled無/sources非空/canonical_spelling==surface/単語1語/ja_reading_katakana除外/
#   surfaceがCMU未収録/IPA->ARPAbet変換可/confidence medium以上/音素列3以上。ASR語側=CMU語の代表発音(rank0)が候補と完全一致。
import argparse, collections, json, sys
sys.path.insert(0, ".")
import pronouncing
import er006_m1_multi_candidate_01 as m1
ap = argparse.ArgumentParser()
ap.add_argument("--ledger", default="er006_output/pronunciation_ledger_01/ledger.json")
ap.add_argument("--out-md", default="docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/E2_ACCEPTABLE_PAIRS_01.md")
ap.add_argument("--out-json", default="docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/e2_acceptable_pairs_01_result.json")
a = ap.parse_args()
L = json.load(open(a.ledger, encoding="utf-8"))
pronouncing.init_cmu()
rep = collections.defaultdict(list)  # rank0 pron(ストレス除去) -> words
first = {}
for w, ph in pronouncing.pronunciations:
    if w not in first:
        first[w] = tuple(m1._strip_stress(x) for x in ph.split())
for w, p in first.items():
    rep[p].append(w)
ENTITY_ALLOWED_CONF = ("medium", "high")
rows, excluded = [], collections.Counter()
for key, e in L.items():
    surf = m1._norm_surface(e.get("surface", ""))
    why = None
    if " " in surf: why = "multi_word"
    elif e.get("entity_type") == "ja_reading_katakana": why = "ja_reading_katakana"
    elif e.get("ledger_disabled"): why = "ledger_disabled"
    elif (m1._norm_surface(e.get("canonical_spelling", "")) or surf) != surf: why = "canonical_spelling_differs"
    elif not (e.get("sources") or []): why = "sources_empty"
    elif m1.default_cmu(surf): why = "surface_in_cmu(C2対象外)"
    elif e.get("confidence") not in ENTITY_ALLOWED_CONF: why = "confidence_%s" % e.get("confidence")
    if why:
        excluded[why] += 1; continue
    raws = [("expected", e.get("expected_pronunciation_ipa") or "")] + [("alt", x) for x in (e.get("alternate_pronunciations") or [])]
    seen = set()
    for src, raw in raws:
        for seg, w_ in m1._ipa_segments(raw):
            if w_: continue
            p = m1.ipa_to_arpa(seg)
            if p is None or p in seen: continue
            seen.add(p)
            if len(p) < 3:
                excluded["pron_lt_3_phonemes"] += 1; continue
            hits = sorted(rep.get(tuple(p), []))
            rows.append({"ledger_key": key, "surface": e.get("surface"), "entity_type": e.get("entity_type"), "confidence": e.get("confidence"),
                         "evidence_tier": e.get("evidence_tier"), "n_sources": len(e.get("sources") or []), "reading_src": src,
                         "ipa_seg": seg, "pron": " ".join(p), "cmu_words": hits, "updated_at": e.get("updated_at")})
n_hit = sum(1 for r in rows if r["cmu_words"])
md = ["# E2_ACCEPTABLE_PAIRS_01 (OF-OOV-03) E2が受理しうる『Ledger読み x CMU語』全件", "",
      f"生成: `e2_acceptable_pairs_01.py`(API 0)。Ledger={a.ledger}({len(L)} entry)。条件=ledger_disabled無/sources非空/canonical_spelling==surface/surface CMU未収録/medium以上/3音素以上。",
      f"CMU語の代表発音(rank0)と完全一致する語がある候補読み: **{n_hit}件**/対象候補読み{len(rows)}件。除外内訳: {dict(excluded)}", "",
      "| ledger_key | surface | entity_type | conf | evidence_tier | 読みの別 | IPA | 音素 | 一致するCMU語 |", "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['ledger_key']} | {r['surface']} | {r['entity_type']} | {r['confidence']} | {r['evidence_tier']} | {r['reading_src']} | {r['ipa_seg']} | {r['pron']} | {', '.join(r['cmu_words']) or '(なし=E2が発火しない)'} |")
md += ["", "## 再生成手順(Ledger増加時)", "`.venv\Scripts\python.exe docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/e2_acceptable_pairs_01.py`(Ledger path引数で別snapshotも可)。Production化後は、Ledger登録のたびに自動再生成するか、新規entryの一致CMU語を登録時に監査ログへ残すことを推奨。"]
open(a.out_md, "w", encoding="utf-8").write("\n".join(md) + "\n")
json.dump({"ledger": a.ledger, "n_entries": len(L), "excluded": dict(excluded), "rows": rows}, open(a.out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("entries", len(L), "candidate readings", len(rows), "with CMU homophone", n_hit, "excluded", dict(excluded))
for r in rows:
    if r["cmu_words"]: print(r["surface"], r["pron"], r["cmu_words"])
