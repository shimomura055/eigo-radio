# KP-IDIOM Phase A PROTOTYPE (diagnostic only, NOT production, no API/network).
# Idea (a): expand Wiktionary titles that contain placeholders (one's / someone's / someone / oneself / something)
# and match them against article n-grams with possessive/object-pronoun slots + verb lemma matching.
import sys, os, re, json, glob
sys.path.insert(0, os.getcwd())
import er023_key_phrase_db_extraction as ext
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er030_key_phrase_db_hybrid_core_01 as core

POSS = {"my", "your", "his", "her", "its", "their", "our"}
OBJ = {"me", "you", "him", "her", "it", "them", "us"}
REFL = {"myself", "yourself", "himself", "herself", "itself", "themselves", "ourselves", "oneself"}
PLACE = {"one's": "POSS", "someone's": "POSS", "somebody's": "POSS", "someone": "OBJ", "somebody": "OBJ",
         "one": "OBJ", "oneself": "REFL", "something": "THING"}

def build_index(dbs):
    idx = {}  # first-content-signature -> list of patterns
    pats = []
    for key, ent in dbs["wiktionary"].items():
        toks = key.split()
        if not any(t in PLACE for t in toks) or len(toks) > 6 or len(toks) < 2:
            continue
        if "," in key:
            continue
        pats.append({"title": key, "toks": toks, "cats": ent["categories"]})
    return pats

from functools import lru_cache
@lru_cache(maxsize=None)
def _lem(t):
    return frozenset(ext.lemma_candidates_for_word(t)) | frozenset([s1v2.irregular_base_form(t) or ""])

def tok_match(pt, t):
    t = t.lower()
    if pt in PLACE:
        k = PLACE[pt]
        if k == "POSS": return t in POSS or t.endswith("'s")
        if k == "OBJ": return t in OBJ
        if k == "REFL": return t in REFL
        if k == "THING": return t in {"it", "that", "this", "them", "these", "those"}
    if t == pt: return True
    return pt in _lem(t)

def match_sentence(toks, pats):
    hits = []
    lowset = set(t.lower() for t in toks)
    lemset = set()
    for t in lowset: lemset |= _lem(t)
    lemset |= lowset
    for p in pats:
        L = len(p["toks"])
        lits = [x for x in p["toks"] if x not in PLACE]
        if lits and not all(x in lemset for x in lits): continue
        for i in range(0, len(toks) - L + 1):
            if all(tok_match(pt, t) for pt, t in zip(p["toks"], toks[i:i + L])):
                # require >=1 literal (non placeholder) token that is not a closed-class word, to avoid junk
                lit = [x for x in p["toks"] if x not in PLACE and x not in core._CLOSED]
                if lit:
                    hits.append({"title": p["title"], "surface": " ".join(toks[i:i + L]), "cats": p["cats"]})
    return hits

def baseline_hit(surface, dbs):
    ng = {"n": len(surface.split()), "surface_tokens": surface.split(), "surface_form": surface}
    return s1v2.match_candidate_with_irregular_rescue(ng, dbs)["db_match_count"] > 0

if __name__ == "__main__":
    OUT = "er064_output/kp_idiom_trial_01/phase_a"
    dbs = core.load_group1_dbs(); pats = build_index(dbs)
    out = {"placeholder_title_count": len(pats), "placeholder_title_sample": [p["title"] for p in pats[:6]]}
    # A) target articles
    tgt = {}
    for lv in ["std", "adv"]:
        text = open(f"{OUT}/inputs/v4_{lv}_article.md", encoding="utf8").read()
        units = core.build_sentence_units(text)
        hs = []
        for u in units: hs += [dict(h, sentence=u["raw_text"][:90]) for h in match_sentence(u["tokens"], pats)]
        tgt[lv] = {"proto_hits": hs, "contains_pump_fist": any("pump" in h["title"] for h in hs),
                   "contains_mark_date": any(h["title"].startswith("mark") for h in hs)}
    out["v4_target_articles"] = tgt
    # B) hand-made probes (self-written sentences; no API)
    probes = ["Please don't spill the beans about the party.", "She bit her tongue and said nothing.",
              "He pumped his fist in the air.", "You are pulling my leg.", "We should call it a day.",
              "She lost her temper at the meeting.", "It cost an arm and a leg.", "Mark the date on your calendar.",
              "Tom keeps an eye on his sister.", "They went the extra mile for us."]
    pr = []
    for s in probes:
        toks = core.build_sentence_units(s)[0]["tokens"]
        ngram_hits = []
        for ng in ext.generate_ngrams([toks], min_n=2, max_n=5):
            m = s1v2.match_candidate_with_irregular_rescue(ng, dbs)
            if m["db_match_count"] > 0 and m["unit_type"] != "word":
                ngram_hits.append(ng["surface_form"] + "[" + m["unit_type"] + "]")
        pr.append({"sentence": s, "current_pipeline_multiword_hits": ngram_hits,
                   "proto_hits": [(h["surface"], h["title"]) for h in match_sentence(toks, pats)]})
    out["probe_sentences"] = pr
    # C) side-effect: other saved articles
    import hashlib
    allf = sorted(glob.glob("er0*_output/**/article.md", recursive=True))
    files, seenh = [], set()
    for f in allf:  # dedupe by content hash; skip non-English-looking/short files
        try: t = open(f, encoding="utf8").read()
        except Exception: continue
        h = hashlib.sha256(t.encode("utf8")).hexdigest()
        if h in seenh or len(t.split()) < 150: continue
        seenh.add(h); files.append(f)
    stats = {"files": 0, "new_candidates_total": 0, "per_file": [], "examples": []}
    seen_ex = {}
    for f in files[:400]:
        try: text = open(f, encoding="utf8").read()
        except Exception: continue
        units = core.build_sentence_units(text)
        newc = set(); allp = set()
        for u in units:
            for h in match_sentence(u["tokens"], pats):
                allp.add(h["surface"].lower())
                if not baseline_hit(h["surface"], dbs): newc.add((h["surface"].lower(), h["title"]))
        stats["files"] += 1; stats["new_candidates_total"] += len(newc)
        stats["per_file"].append(len(newc))
        for s, t in newc: seen_ex.setdefault(t, s)
    stats["examples"] = [f"{s} <= {t}" for t, s in list(seen_ex.items())[:60]]
    stats["files_with_zero_new"] = sum(1 for x in stats["per_file"] if x == 0)
    stats["max_new_in_one_file"] = max(stats["per_file"]) if stats["per_file"] else 0
    stats["mean_new_per_file"] = round(stats["new_candidates_total"] / max(1, stats["files"]), 2)
    stats.pop("per_file")
    out["side_effect_scan"] = stats
    json.dump(out, open(f"{OUT}/proto_placeholder_match_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1)[:7000])
