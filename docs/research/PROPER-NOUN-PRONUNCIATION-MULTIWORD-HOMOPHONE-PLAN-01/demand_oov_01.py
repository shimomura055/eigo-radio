"""PNMH-PLAN-01: #133(発音供給)の需要測定(API 0)。保存済みペアのcontent_word_diffsのうち canonical側がCMU辞書外(OOV)の語を集計。"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import proto_multiword_span_01 as P
val = P.val
import er006_secondary_asr_01 as sec
import pronouncing
pairs = [json.loads(l) for l in open(os.path.join(HERE, "pairs_01.jsonl"), encoding="utf8")]
cnt = collections.Counter(); kinds = collections.Counter(); real = collections.Counter()
tot_diff_pairs = 0
for p in pairs:
    r = val.classify_asr_match(p["canonical"], p["asr"])
    ds = r.protected.content_word_diffs
    if r.should_pass or not ds: continue
    tot_diff_pairs += 1
    real_src = any(e in ("primary", "secondary") for e in p["engines"])
    for d in ds:
        cw = d["canonical"].split()
        oov = [w for w in cw if not pronouncing.phones_for_word(w)]
        k = ("entity_like" if d["entity_like"] else "homophone" if d["homophone_candidate"] else "other") + ("+canonOOV" if oov else "+canonInCMU")
        kinds[k] += 1
        if oov:
            for w in oov:
                cnt[w] += 1
                if real_src: real[w] += 1
out = {"pairs_with_content_diffs_not_passed": tot_diff_pairs, "diff_kinds": dict(kinds),
       "canonical_OOV_words_all": cnt.most_common(40), "canonical_OOV_words_real_runs_only": real.most_common(40)}
json.dump(out, open(os.path.join(HERE, "demand_oov_result_01.json"), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
