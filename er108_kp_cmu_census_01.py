# ============================================================
# er108_kp_cmu_census_01.py  (API 0 / 費用0 / 読み取りのみ。研究用script)
# KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_01 成果物1: 保存済みKey Phrase(最終英語phrase)の各語をCMU辞書で照合し、
# 『未登録率』と『誤除外になりうる型』(固有名詞・省略形・ハイフン・縮約・アクセント・数字)を集計する。
# 母集団A = 保存KP英語segment(各run audit/review_lock_state.json のkp{n}_en、canonical=tts_generation_results.text または keywords_canonicalized used_form。
#           AZURE_ITN_IMPACT_01の548 segmentと同じ列挙法)
# 母集団B = 全keywords_canonicalized.jsonのused_form(重複排除した句。旧選定方式[A/B/C・Strategy L等]を含む)
# 使い方: .venv\Scripts\python.exe er108_kp_cmu_census_01.py --out docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/cmu_census_01.json
# ============================================================
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, ".")
import er108_kp_cmu_lexicon_gate_01 as gate


def canon_map(audit_dir):
    p = os.path.join(audit_dir, "tts_generation_results.json")
    m = {}
    if os.path.exists(p):
        try:
            d = json.load(open(p, encoding="utf8"))
            for n, e in (d.get("key_phrases") or {}).items():
                t = ((e or {}).get("english") or {}).get("text")
                if t:
                    m[f"kp{n}_en"] = t
        except Exception:
            pass
    kc = os.path.join(os.path.dirname(audit_dir), "key_phrases", "keywords_canonicalized.json")
    if os.path.exists(kc):
        try:
            d = json.load(open(kc, encoding="utf8"))
            for it in d.get("items") or []:
                t = it.get("used_form") or it.get("key_phrase")
                if t and it.get("rank") and f"kp{it['rank']}_en" not in m:
                    m[f"kp{it['rank']}_en"] = t
        except Exception:
            pass
    return m


def word_type(tok: str, wc) -> str:
    """未登録語の型(誤除外になりうるか人手で見るための分類)。"""
    n = wc.normalized
    types = []
    if re.search(r"[À-ɏ]", tok):
        types.append("accent")
    if re.search(r"\d", tok):
        types.append("digit")
    if "-" in n:
        types.append("hyphen")
    if "'" in n:
        types.append("apostrophe")
    if "." in n.strip("."):
        types.append("abbrev_dot")
    if tok[:1].isupper() and not types:
        types.append("capitalized(proper_noun_candidate)")
    return "+".join(types) or "plain_oov(neologism/slang/proper?)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    # ---- 母集団A
    seg = {}
    for f in glob.glob("**/audit/review_lock_state.json", recursive=True):
        ad = os.path.dirname(f)
        try:
            d = json.load(open(f, encoding="utf8"))
        except Exception:
            continue
        cm = canon_map(ad)
        for k, v in (d.items() if isinstance(d, dict) else []):
            if re.fullmatch(r"kp\d_en", str(k)):
                seg[(ad, k)] = cm.get(k)
    popA = [(k, c) for k, c in seg.items() if c]
    # ---- 母集団B
    phrases = {}
    for f in glob.glob("**/keywords_canonicalized.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf8"))
        except Exception:
            continue
        for it in (d.get("items") or []):
            t = it.get("used_form") or it.get("key_phrase")
            if t:
                phrases.setdefault(t.strip().lower(), (t, f))

    def census(items, label):
        n_ph = len(items)
        bad_ph = []
        word_total = 0
        word_bad = collections.Counter()
        word_bad_types = {}
        route = collections.Counter()
        for ref, text in items:
            pc = gate.check_phrase(text)
            for w in pc.words:
                word_total += 1
                route[w.route or ("FAIL:" + w.reason)] += 1
                if not w.ok:
                    word_bad[w.token] += 1
                    word_bad_types[w.token] = word_type(w.token, w)
            if not pc.ok:
                bad_ph.append({"ref": ref if isinstance(ref, str) else "|".join(ref), "phrase": text, "unregistered": pc.unregistered})
        tcount = collections.Counter(word_bad_types.values())
        return {"population": label, "phrases": n_ph, "phrases_with_unregistered": len(bad_ph),
                "unregistered_rate": round(len(bad_ph) / max(1, n_ph), 4), "words_total": word_total,
                "words_unregistered_occurrences": sum(word_bad.values()), "distinct_unregistered_words": len(word_bad),
                "route_counts": dict(route), "unregistered_word_types": dict(tcount),
                "unregistered_words": [{"word": w, "n": n, "type": word_bad_types[w]} for w, n in word_bad.most_common()],
                "phrases_detail": bad_ph}

    out = {"generated_by": "er108_kp_cmu_census_01.py", "api_calls": 0, "cost_jpy": 0, "lexicon": gate.lexicon_info(),
           "A_stored_kp_segments": census([(k, c) for k, c in popA], "A: stored KP English segments(lock state)"),
           "B_distinct_used_forms_all_runs": census([(v[1], v[0]) for v in phrases.values()], "B: distinct used_form over all keywords_canonicalized.json")}
    out["A_stored_kp_segments"]["segments_total_in_lock_state"] = len(seg)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k in ("A_stored_kp_segments", "B_distinct_used_forms_all_runs"):
        o = out[k]
        print(k, o["phrases"], o["phrases_with_unregistered"], o["unregistered_rate"], o["distinct_unregistered_words"], o["unregistered_word_types"])


if __name__ == "__main__":
    main()
