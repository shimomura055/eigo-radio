# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04 Round5 設計(API呼出なし)。N01-N04。"""
import os, json, hashlib, re, difflib, itertools
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round5"); os.makedirs(OUT, exist_ok=True)
BASE = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03")
R4 = json.load(open(os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round4", "prompts_r4.json"), encoding="utf-8"))
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
PRIOR = {}
for r in (1, 2, 3):
    P = json.load(open(os.path.join(BASE, f"round{r}", f"prompts_r{r}.json"), encoding="utf-8"))
    if r == 1: H0 = P["baseline"]["H0"]["style"]
    PRIOR.update({k: v["style"] for k, v in P["candidates"].items()})
PRIOR.update({k: v["style"] for k, v in R4["candidates"].items()})
assert len(PRIOR) == 33
M05 = PRIOR["M05"]
C = [
("N01", "A cheerful, kind storyteller sharing a true story at a pace a little slower than usual. Bring each sentence to its natural close, then go directly on to the next, including where the story takes a turn.",
 dict(speed="a little slower than usual(M05のslightly slowerを別表現、1回)", pause="文を自然な終わりまで言い切り→直接次へ。話の転換でも同様(肯定形、M05と別表現)", voice="陽気で優しい語り手", strength="中", structure="像+ペース+言い切り→次へ(話題転換節あり)"),
 "M05の言い切り→次へ直行を別表現に書き換え、構造の頑健性を確認(話題転換節は維持)。", "M05(Std全指標圏内、Adv数値圏内でASRのみ不合格)", "別表現でM05の効きが再現しない/Advが速い"),
("N02", "A warm, bright storyteller telling a true story, going slightly slower than usual. Finish every sentence fully, then move straight on to the next one.",
 dict(speed="slightly slower(M05と同一語、1回)", pause="語尾を最後まで言い切って次へ直行(肯定形、話題転換節なし)", voice="温かく明るい語り手", strength="中", structure="像+減速+言い切り→次へ(話題転換節を除去した切除比較。M05に対し1語'on'のみ差、部分文字列回避)"),
 "M05から話題転換節(even when the story changes direction)を除き、その節が寄与しているかを切除比較する。", "M05、Step A/Round4(話題転換指示は長無音を減らさない)", "話題転換節の除去で文末が長くなる/変化なし"),
("N03", "A warm, bright storyteller telling a true story, going slightly slower than usual. Read the text word for word exactly as written, finish every sentence fully, then move straight to the next one, even when the story changes direction.",
 dict(speed="slightly slower(M05同一語、1回)", pause="言い切り→次へ直行(M05同一)", voice="温かく明るい語り手", strength="中", structure="M05+書かれた通りに一語ずつ読む肯定形指示(want→wanna対策、新軸=忠実読み)"),
 "M05のAdv ASR不合格(want→wanna)に対し、書かれた通りに読む肯定形指示でASR一致が改善するかを見る。", "Round4 M05/M06 Adv(want→wanna)", "忠実読み指示が1語ずつの区切りを生み文中無音が増える/Stdが遅くなる"),
("N04", "A friendly, bright narrator telling a true story at a measured pace. Finish each sentence fully, then go on to the next at once.",
 dict(speed="measured pace(1回)", pause="言い切って即次へ(肯定形、話題転換節なし)", voice="親しみのある明るいナレーター", strength="中", structure="像+measured+言い切り→次へ(M05構造のmeasured版、話題転換節なし、2文)"),
 "M06のStd文末長・長無音を、話題転換節なしのmeasured+言い切り→次へで改善できるか、Adv速度安定を見る。", "M06(Std 535ms/長無音1)、M05", "measuredの減速力が弱くAdvが速い"),
]
def toks(t): return set(re.findall(r"[a-z']+", t.lower()))
def jac(a, b): ja, jb = toks(a), toks(b); return len(ja & jb) / len(ja | jb)
rows = {}
for cid, st, ax, di, basis, se in C:
    ns = len([s for s in re.split(r"(?<=[.!?])\s+", st.strip()) if s])
    assert H0 not in st and st not in H0 and all(st not in v and v not in st for v in PRIOR.values()), cid
    assert 2 <= ns <= 3, cid
    mj = max(((k, round(jac(st, v), 3)) for k, v in PRIOR.items()), key=lambda x: x[1])
    rows[cid] = {"style": st, "chars": len(st), "words": len(st.split()), "sentences": ns, "sha256": sha(st), "axes": ax, "design_intent": di,
                 "prior_basis": basis, "expected_side_effects": se, "max_jaccard_vs_prior": {"cand": mj[0], "jaccard": mj[1]},
                 "jaccard_vs_M05": round(jac(st, M05), 3), "jaccard_vs_H0": round(jac(st, H0), 3),
                 "seq_ratio_vs_max": round(difflib.SequenceMatcher(None, st, PRIOR[mj[0]]).ratio(), 3),
                 "contains_unhurried_slowly": bool(re.search(r"unhurried|slowly", st.lower())), "has_numeric_wpm": bool(re.search(r"\d", st)),
                 "contains_position_words": bool(re.search(r"delay|International|continue|Department|Agriculture|Coffee Organization", st)),
                 "negation": bool(re.search(r"\b(do not|dont|never|not|no)\b", st.lower())), "speed_word_count": len(re.findall(r"slower|measured", st.lower()))}
    r = rows[cid]
    assert not r["has_numeric_wpm"] and not r["contains_unhurried_slowly"] and not r["contains_position_words"] and not r["negation"] and r["speed_word_count"] == 1, cid
assert len({r["sha256"] for r in rows.values()} | {sha(v) for v in PRIOR.values()} | {sha(H0)}) == 4 + 33 + 1
ids = [c[0] for c in C]; sims = {}
for a, b in itertools.combinations(ids, 2): sims[f"{a}-{b}"] = round(jac(rows[a]["style"], rows[b]["style"]), 3)
mx = sorted(sims.items(), key=lambda kv: -kv[1])[:6]
check = {"duplicates": "N01-N04 sha全相異、J/K/L/M/H0とsha相異(assert済)。N内最大Jaccard: " + ", ".join(f"{k}={v}" for k, v in mx),
         "vs_prior": "J/K/L/M/H0を部分文字列に含む・含まれる候補なし(assert済)。最大Jaccard: " + ", ".join(f"{c}:{rows[c]['max_jaccard_vs_prior']['cand']}={rows[c]['max_jaccard_vs_prior']['jaccard']}" for c in ids) + " / H0: " + ", ".join(f"{c}={rows[c]['jaccard_vs_H0']}" for c in ids),
         "contradictions": "矛盾なし。N02はM05からの意図的切除比較で語彙がM05に極めて近い(Jaccard高)が1語差で部分文字列ではない。N03はM05構造+忠実読み指示。",
         "redundancy": "速度語は各1回(slower/measured)、数値WPM・unhurried/slowly・否定形・位置語なし(assert済)", "sentence_count": {c: rows[c]["sentences"] for c in ids}}
json.dump({"voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "method": "speech_metadata(Part.speech_metadata.style)",
           "baseline": {"H0": {"style": H0, "sha256": sha(H0)}, "M05": {"style": M05, "sha256": sha(M05)}}, "candidates": rows, "similarity_pairs": sims, "self_check": check},
          open(os.path.join(OUT, "prompts_r5.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
per = 1.273; n = 12
est = {"phase": "StepB", "calls_new": n, "breakdown": "M05 T2/T3 x Std/Adv=4call + N01-N04 T1 x Std/Adv=8call", "per_call_jpy": per, "central_jpy": round(n * per, 2), "high_plus20pct_jpy": round(n * per * 1.2, 2),
       "cap_stepB_jpy": 16, "hard_stop_stepB_jpy": 18, "cap_stepC_jpy": 9, "cumulative_before_jpy": 88.27, "cap_total_jpy": 300, "hard_stop_total_jpy": 290,
       "source": "Round4実績 JPY15.28/12call=1.273/call", "fits_cap_central": n * per <= 16, "fits_hard_stop_high": n * per * 1.2 <= 18,
       "cumulative_after_central_jpy": round(88.27 + n * per, 2), "stepC_max_call": 4, "stepC_central_jpy": round(4 * per, 2)}
json.dump({"estimate": est}, open(os.path.join(OUT, "cost_r5.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in ids: print(c, rows[c]["words"], rows[c]["sentences"], rows[c]["sha256"][:8], rows[c]["max_jaccard_vs_prior"], rows[c]["jaccard_vs_M05"], rows[c]["jaccard_vs_H0"])
print(check["duplicates"]); print(est)
