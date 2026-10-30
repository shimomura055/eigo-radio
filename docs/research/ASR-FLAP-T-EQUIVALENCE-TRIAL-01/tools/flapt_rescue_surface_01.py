# ASR-FLAP-T-EQUIVALENCE-TRIAL-01 委任_01: M1が『救済しうる語ペア』の全体像(rescue surface)をCMU辞書全体から列挙。API 0。
# 目的: 偽救済リスクの上限を、辞書全体の語ペア数・意味反転語・高頻度語の有無で定量化する。
import argparse, collections, json, os, re, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cmudict
import flapt_equivalence_proto_01 as fl

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    d = cmudict.dict()
    words = {w: v for w, v in d.items() if re.fullmatch(r"[a-z]{3,}", w)}
    groups = collections.defaultdict(set)
    nread = collections.Counter()
    for w, vs in words.items():
        rd = {fl._s2(tuple(v)) for v in vs}
        if len(rd) != 1:
            nread["multi_reading_skipped"] += 1
            continue
        ph = next(iter(rd))
        key = tuple("DX" if (fl._base(p) in ("T", "D") and fl.flap_env(ph, i)[0]) else p for i, p in enumerate(ph))
        if "DX" in key:
            groups[key].add(w)
    pairs = []
    for key, ws in groups.items():
        for x, y in itertools.combinations(sorted(ws), 2):
            r = fl.judge_pair(x, y)
            if r.decision in ("RESCUE", "REQUIRES_EXTRA_EVIDENCE"):
                pairs.append((x, y, r.decision, r.reason))
    c = collections.Counter(p[2] for p in pairs)
    out = {"cmu_words_alpha_ge3": len(words), "single_reading_skipped_multi": nread["multi_reading_skipped"],
           "flap_groups_with_ge2_words": sum(1 for ws in groups.values() if len(ws) >= 2),
           "pair_counts": dict(c), "rescue_pairs_total": c.get("RESCUE", 0)}
    sample = [p for p in pairs if p[2] == "RESCUE"]
    out["rescue_pairs_sample_first60"] = sample[:60]
    sensitive = {"not", "no", "never", "none", "nor", "cannot"}
    out["negation_words_in_pairs"] = [p for p in pairs if p[0] in sensitive or p[1] in sensitive]
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("cmu_words_alpha_ge3", "single_reading_skipped_multi", "flap_groups_with_ge2_words", "pair_counts", "negation_words_in_pairs")}, ensure_ascii=False))
    print(sample[:40])

if __name__ == "__main__":
    main()
