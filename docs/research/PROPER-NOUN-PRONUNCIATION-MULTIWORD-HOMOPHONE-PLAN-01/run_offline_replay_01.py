"""PNMH-PLAN-01: pairs_01.jsonl へ 現行(before) と 提案A試作(after) を再適用(API 0・read-only)。出力 replay_result_01.json"""
import sys, os, json, difflib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import proto_multiword_span_01 as P
val = P.val
import er006_secondary_asr_01 as sec
pairs = [json.loads(l) for l in open(os.path.join(HERE, "pairs_01.jsonl"), encoding="utf8")]

def judge(c, a):
    r = val.classify_asr_match(c, a)
    final = "PASS" if r.should_pass else None
    if final is None and (sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r)):
        lab = sec._step_alternate_pass(r)
        if lab: final = "PASS:" + lab
    return r.classification, (final or "NOT_PASS"), r

before = {}
for i, p in enumerate(pairs):
    cl, fin, _ = judge(p["canonical"], p["asr"])
    before[i] = (cl, fin)
spans = collections.OrderedDict()
for i, p in enumerate(pairs):
    ct, at = val.tokenize(p["canonical"]), val.tokenize(p["asr"])
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ct, at, autojunk=False).get_opcodes():
        if tag == "equal": continue
        cs, as_ = ct[i1:i2], at[j1:j2]
        if cs and as_ and (len(cs) == 1) != (len(as_) == 1) or (cs and as_ and len(cs) > 1 and len(as_) > 1):
            if len(cs) == 1 and len(as_) == 1: continue
            d = {}; ok = P.multiword_span_equivalent(cs, as_, detail=d)
            k = (" ".join(cs), " ".join(as_))
            e = spans.setdefault(k, {"canonical_span": k[0], "asr_span": k[1], "n": 0, "equal": ok, "why": d["why"], "engines": set(), "pairs": []})
            e["n"] += 1; e["engines"].update(p["engines"]); 
            if len(e["pairs"]) < 2: e["pairs"].append(i)
P.install_proto()
changes = []
for i, p in enumerate(pairs):
    cl, fin, r = judge(p["canonical"], p["asr"])
    if (cl, fin) != before[i]:
        changes.append({"idx": i, "canonical": p["canonical"], "asr": p["asr"], "engines": p["engines"], "n_src": p["n_src"],
                        "before": before[i], "after": (cl, fin), "diffs": r.protected.content_word_diffs, "src": p["sources"][:1]})
out = {"n_pairs": len(pairs), "n_changes": len(changes),
       "spans": [dict(v, engines=sorted(v["engines"])) for v in spans.values()],
       "changes": changes}
json.dump(out, open(os.path.join(HERE, ("replay_result_01_noguard.json" if os.environ.get("PNMH_NO_GUARDS") == "1" else "replay_result_01.json")), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
print("pairs", len(pairs), "changes", len(changes), "span_types", len(spans), "span_equal", sum(1 for v in spans.values() if v["equal"]))
for v in spans.values(): print(v["n"], v["equal"], v["why"], "|", v["canonical_span"], "->", v["asr_span"], v["engines"])
print("---- changes")
for c in changes: print(c["before"], "->", c["after"], "|", c["n_src"], c["engines"], "|", c["canonical"][:80], "||", c["asr"][:80], c["diffs"])
