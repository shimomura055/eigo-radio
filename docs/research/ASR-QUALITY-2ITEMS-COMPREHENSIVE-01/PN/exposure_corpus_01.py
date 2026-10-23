# -*- coding: utf-8 -*-
"""潜在露出の測定(API 0, read-only): 保存済みX/Z英語ナレーションsegment(canonical_text)中の「大文字始まり候補語」について、
現行PNAPの proper_noun_evidence が(segment内の出現位置で)根拠を出せるかを数える。= 誤認識時に受理(PASS_WITH_ALARM)できる語か、HR Lockになる語か。"""
import json, glob, os, re, sys, collections
sys.path.insert(0, ".")
import er103_proper_noun_alarm_policy_01 as pol
LEDGER = pol.ledger_surface_tokens()
files = glob.glob("er0*_output/**/tts_generation_results.json", recursive=True)
seen_text = {}
for f in files:
    fn = f.replace("\\", "/")
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    def walk(x, p):
        if isinstance(x, dict):
            t = x.get("canonical_text")
            if isinstance(t, str) and x.get("role") in pol.APPLICABLE_ROLES or (isinstance(t, str) and "segment_id" in x):
                role = x.get("role") or "FULL_STORY"
                if role in pol.APPLICABLE_ROLES and re.search(r"[A-Za-z]{3}", t) and not re.search(r"[぀-ヿ一-鿿]", t):
                    key = t.strip()
                    if key not in seen_text:
                        seen_text[key] = (fn, role)
            for k, v in x.items():
                if k in ("attempts", "attempts_log", "asr_judgement", "asr_judgement_inherited"): continue
                if isinstance(v, (dict, list)): walk(v, p)
        elif isinstance(x, list):
            for v in x:
                if isinstance(v, (dict, list)): walk(v, p)
    walk(d, "")
print("files", len(files), "distinct EN segments", len(seen_text))
STOPW = pol._FUNCTION_WORDS | set("i'm i'll i've i'd it's he's she's that's there's let's what's who's yes no oh well so but and then now when why how where what who which while after before once if though because since also still just even only really maybe perhaps today yesterday tomorrow monday tuesday wednesday thursday friday saturday sunday january february march april may june july august september october november december".split())
cands = collections.defaultdict(lambda: {"segs": 0, "ev": collections.Counter(), "ex": None, "midsentence": 0})
for text, (fn, role) in seen_text.items():
    done = set()
    for m in re.finditer(r"[A-Z][A-Za-z'’\-]*", text):
        w = m.group(0).strip("'’-")
        lw = pol._fold(w)
        if len(lw) < 2 or lw in STOPW or lw in done:
            continue
        done.add(lw)
        # 候補: CMU未収録 or zipf<4.0 (一般語でない) の大文字語
        if pol.is_general_word(lw):
            continue
        ok, ev = pol.proper_noun_evidence(lw, text, ledger_surfaces=LEDGER, role=role)
        c = cands[lw]
        c["segs"] += 1
        c["ev"][ev if ok else "NONE"] += 1
        if c["ex"] is None or (not ok and c["ex"][1] != "NONE"):
            c["ex"] = (text[max(0, m.start()-40):m.end()+30].replace("\n", " "), "NONE" if not ok else ev, fn.split("/")[1:4])
json.dump({k: {"segs": v["segs"], "ev": dict(v["ev"]), "ex": v["ex"]} for k, v in cands.items()}, open("docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/exposure_corpus_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = len(cands)
none_only = [k for k, v in cands.items() if set(v["ev"]) == {"NONE"}]
partial = [k for k, v in cands.items() if "NONE" in v["ev"] and len(v["ev"]) > 1]
print("distinct candidate tokens", tot, "evidence-none-in-all-segments", len(none_only), "partial", len(partial))
print("ev labels (token-level, any)", collections.Counter(l for v in cands.values() for l in v["ev"]).most_common())
print("NONE-only:", sorted(none_only))
