# trial_b_g2p_01.py -- 候補B(CMU未収録語をG2P=g2p_enで音素推定し、ASR語のCMU音素と照合)のオフライン検証。Trial専用・API 0。
# 参考: 過去にC3(綴りからの規則推定=G2P)は M1承認時に『不採用』(SSOT_DRAFT_01 L4, UDR #52)。ここは"不採用方式を再導入する"のではなく、効果と誤PASSを実測して比較表に載せるための検証。
import glob, json, sys, collections, difflib, re
sys.path.insert(0, ".")
import er109_stored_census_01 as C
import er006_preprod_hardening_01_validation as val
import er006_m1_multi_candidate_01 as m1
from g2p_en import G2p
g = G2p(); cache = {}
def g2p(w):
    if w not in cache: cache[w] = tuple(re.sub(r"\d", "", p) for p in g(w) if p.strip() and p != " ")
    return cache[w]
rows = []
for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
    if ".venv" in f: continue
    rows += C.rows_from_results(f)
seen = set(); acc = []; cnt = collections.Counter(); exact_vs_loose = collections.Counter()
for r in rows:
    if not r["asr"] or r["stored_cls"] in C.PASS_LABELS: continue
    k = (r["canonical"], r["asr"])
    if k in seen: continue
    seen.add(k)
    b = val.classify_asr_match(r["canonical"], r["asr"], segment_id=r["seg"])
    if b.should_pass or not b.protected.passed or len(b.protected.content_word_diffs) != 1: cnt["not_single_diff_or_pass"] += 1; continue
    d = b.protected.content_word_diffs[0]
    cw, aw = m1._tokens(d["canonical"]), m1._tokens(d["asr"])
    if d.get("type") != "replace" or len(cw) != 1 or len(aw) != 1: cnt["not_1to1"] += 1; continue
    c, a = cw[0], aw[0]
    if m1.default_cmu(c): cnt["canonical_in_cmu"] += 1; continue
    avs = [tuple(v) for v in m1.default_cmu(a)]
    if not avs: cnt["asr_not_in_cmu"] += 1; continue
    gp = g2p(c)
    ok = gp in avs
    cnt["tested"] += 1
    if ok:
        asr2 = m1._replace_tokens(r["asr"], {i: c for i, t in enumerate(m1._tokens(r["asr"])) if t == a})
        post = val.classify_asr_match(r["canonical"], asr2, segment_id=r["seg"])
        if post.should_pass:
            acc.append((c, a, gp, r["seg"], r["stored_cls"], r["final_status"]))
    else:
        # 母音1つだけ異なる等の『緩い一致』の件数(誤PASSリスクの目安): 音素数が同じで1音素のみ差
        for v in avs:
            if len(v) == len(gp) and sum(x != y for x, y in zip(v, gp)) == 1: exact_vs_loose["one_phoneme_apart"] += 1; break
print(dict(cnt)); print("G2P厳密一致で受理(再判定もPASS):", len(acc)); [print(" ", x) for x in acc]; print("1音素差(緩和すると誤受理し得る)件数:", dict(exact_vs_loose))
# gacha自体
print("g2p_en('gacha') =", g2p("gacha"), " CMU('gotcha') =", m1.default_cmu("gotcha"))
# G2P精度の目安: CMU収録語でg2pが辞書と一致する割合(代表1000語)
import cmudict, random
words = sorted(w for w in set(cmudict.words()) if re.fullmatch(r"[a-z]{5,9}", w))
random.Random(1).shuffle(words); ok = 0; n = 600
for w in words[:n]:
    ok += tuple(re.sub(r'\d', '', x) for x in g.predict(w)) in [tuple(x) for x in m1.default_cmu(w)]
print(f"G2P(g2p_en 神経網predictのみ。辞書収録語は学習データに含まれるため楽観値)がCMU辞書の発音と(ストレス除く)完全一致する割合: {ok}/{n} = {100*ok/n:.1f}% (OOV語ではこれより低い想定)")
