# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-03 Round3 設計(API呼出なし)。L01-L06、全て一から記述。"""
import os, json, hashlib, re, difflib, itertools
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03", "round3"); os.makedirs(OUT, exist_ok=True)
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
R1 = json.load(open(os.path.join(ROOT, "er057_output/coffee_tts_style_h_speed_03/round1/prompts_r1.json"), encoding="utf-8"))
R2 = json.load(open(os.path.join(ROOT, "er057_output/coffee_tts_style_h_speed_03/round2/prompts_r2.json"), encoding="utf-8"))
H0 = R1["baseline"]["H0"]["style"]; J = {k: v["style"] for k, v in R1["candidates"].items()}; K = {k: v["style"] for k, v in R2["candidates"].items()}
PRIOR = {**J, **K}
C = [
("L01", "A warm, bright storyteller with a smile in the voice, going slightly slower than usual. Let each sentence end softly and begin the next at once.",
 dict(speed="slightly slower(像側の控えめ減速、1回のみ)", pause="語尾を柔らかく終えて即次へ(語尾処理+肯定形)", voice="落ち着いたストーリーテリング", strength="中", structure="速度+語尾処理"),
 "K01(slightly slower)はraw 167.8/172.6で最良級だがStdの文末後800ms超が3本。『flow straight on』の接続指示を、語尾処理(softly end / at once)という別軸に置換して長無音が減るかを見る。",
 "K01(減速有効、Std長無音3本)", "語尾処理が効かず長無音が残る、または語尾が弱まって聞き取りにくい"),
("L02", "A clear, friendly narrator sharing a true story at a slightly slower pace than usual. Do not wait between sentences; begin each new one right away, as one connected telling.",
 dict(speed="slightly slower(相対ペース、1回のみ)", pause="待たない禁止+肯定の即開始+一続きの語り", voice="ナレーター(明瞭・親しみ)", strength="中〜やや強", structure="速度+禁止/肯定併記(1文に集約)"),
 "K01の肯定接続にK07/K03型の禁止形を併記して接続を強める。減速語は同じslightly slowerを残しStd長無音と文末間が詰まるかを確認。",
 "K01(長無音)・K07(禁止形で文末詰まる)・K03(禁止形でも減速は残る)", "禁止形が強すぎて全体が速くなる(Adv超過)"),
("L03", "A warm, measured voice, bright and clear, carrying the story along. Carry each sentence into the next without a break in the flow.",
 dict(speed="measured voice(像としての減速、deliberateなし)", pause="肯定形の運び(carry into the next)", voice="落ち着いた語り", strength="中", structure="速度+ポーズ肯定形"),
 "K06(measured)はStd合格だがAdv文末636ms・1040ms長無音。『Pause only briefly』(間を意識させる文)を、間に言及しない肯定形の運びに置換して、間への注意誘発を避ける。",
 "K06(Std合格・Adv間延び)・K01(肯定接続)", "間に言及しないため文末が伸びる/measuredだけでは減速が足りない"),
("L04", "A friendly storyteller with a measured, even rhythm, warm and clear. Take short, quick breaths between sentences, all about the same length.",
 dict(speed="measured, even rhythm(リズム均一化語)", pause="短く均一な息継ぎ", voice="落ち着いたストーリーテリング", strength="中", structure="速度+ポーズ(均一化)"),
 "減速と間の均一化を『even rhythm』『同じ長さの息継ぎ』で同時に狙う。長無音(外れ値)を均一化で抑えられるかを見る(K01/K06の外れ値型長無音への対策)。",
 "K06(measuredで減速)・J07(短い息継ぎでAdv良好)", "均一化指示が機械的な抑揚になる(ピッチ幅低下)"),
("L05", "A bright, warm storyteller who takes it a bit slower than most people do, with a smile in the voice. Each sentence leads right into the next.",
 dict(speed="a bit slower(指示でなく像側に埋め込み)", pause="肯定形の連結(leads right into)", voice="ストーリーテラー像に減速を内包", strength="中", structure="像に速度を内包+ポーズ肯定形"),
 "指示文の相反(『遅く』と『間を詰める』)を避け、減速を話者像の性格として与える。像が速度を決め、指示は連結だけに絞る。",
 "K01(指示型減速)・K05(像のみでは速くなる=像に速度語が無かった)", "像側の減速語が弱く、K05同様に速くなる"),
("L06", "A warm, friendly voice, easy and even, never rushed, never dragging, with a smile in it. Keep the story rolling from sentence to sentence.",
 dict(speed="never rushed, never dragging(両側否定でペース中庸)", pause="肯定形(keep rolling)", voice="自然な語りかけ", strength="中", structure="速度(両側否定)+ポーズ肯定形"),
 "unhurried/slowly不使用の制約下で、速すぎ(rushed)と間延び(dragging)を両側否定でペース中庸に誘導。間延びを明示的に否定することで文末間・長無音を抑える。",
 "K03/K08(弱形速度語で減速消失)・K06(間延び)", "中庸指示では減速が弱く両レベル速い"),
]
def toks(t): return set(re.findall(r"[a-z']+", t.lower()))
def jac(a, b): ja, jb = toks(a), toks(b); return len(ja & jb) / len(ja | jb)
rows = {}
for cid, st, ax, di, basis, se in C:
    ns = len([s for s in re.split(r"(?<=[.!?])\s+", st.strip()) if s])
    assert H0 not in st and st not in H0 and st not in PRIOR.values(), cid
    assert 2 <= ns <= 3, cid
    mj = max(((k, round(jac(st, v), 3)) for k, v in PRIOR.items()), key=lambda x: x[1])
    rows[cid] = {"style": st, "chars": len(st), "words": len(st.split()), "sentences": ns, "sha256": sha(st), "axes": ax, "design_intent": di,
                 "prior_basis": basis, "expected_side_effects": se, "max_jaccard_vs_JK": {"cand": mj[0], "jaccard": mj[1]},
                 "jaccard_vs_H0": round(jac(st, H0), 3), "seq_ratio_vs_max": round(difflib.SequenceMatcher(None, st, PRIOR[mj[0]]).ratio(), 3),
                 "contains_unhurried_slowly": bool(re.search(r"unhurried|slowly", st.lower())), "has_numeric_wpm": bool(re.search(r"\d", st))}
    assert not rows[cid]["has_numeric_wpm"] and not rows[cid]["contains_unhurried_slowly"]
assert len({r["sha256"] for r in rows.values()} | {sha(v) for v in PRIOR.values()} | {sha(H0)}) == 6 + len(PRIOR) + 1
ids = [c[0] for c in C]; sims = {}
for a, b in itertools.combinations(ids, 2): sims[f"{a}-{b}"] = round(jac(rows[a]["style"], rows[b]["style"]), 3)
mx = sorted(sims.items(), key=lambda kv: -kv[1])[:5]
check = {"duplicates": "L01-L06 sha全相異、J01-J13・K01-K08・H0ともsha相異(assert済)。L内最大Jaccard: " + ", ".join(f"{k}={v}" for k, v in mx),
         "vs_prior": "J/K/H0を部分文字列に含む・含まれる候補なし(assert済)。最大Jaccard(J/K): " + ", ".join(f"{c}:{rows[c]['max_jaccard_vs_JK']['cand']}={rows[c]['max_jaccard_vs_JK']['jaccard']}" for c in ids) + " / H0: " + ", ".join(f"{c}={rows[c]['jaccard_vs_H0']}" for c in ids),
         "contradictions": "矛盾なし。L05は減速を像に内包し指示文の相反を避ける設計。L06は両側否定。",
         "redundancy": "速度/間/声質を各1回。数値WPM・unhurried/slowly不使用(assert済)",
         "sentence_count": {c: rows[c]["sentences"] for c in ids}}
json.dump({"voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "method": "speech_metadata(Part.speech_metadata.style)",
           "baseline": {"H0": {"style": H0, "sha256": sha(H0)}}, "candidates": rows, "similarity_pairs": sims, "self_check": check},
          open(os.path.join(OUT, "prompts_r3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
per = 1.254; n = 16
est = {"phase": "StepB", "calls_new": n, "breakdown": "B-1: L01-L06 x Take1 x Std/Adv=12call; B-2: K01,K06 Take2 x Std/Adv=4call", "per_call_jpy": per,
       "central_jpy": round(n * per, 2), "high_plus20pct_jpy": round(n * per * 1.2, 2), "cap_stepB_jpy": 23, "hard_stop_jpy": 26, "cap_stepC_jpy": 10,
       "cumulative_before_jpy": 52.50, "cap_id_jpy": 100, "source": "Round2実績 JPY20.07/16call=1.254/call", "fits_cap_central": n * per <= 23,
       "fits_hard_stop_high": n * per * 1.2 <= 26}
json.dump({"estimate": est}, open(os.path.join(OUT, "cost_r3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in ids: print(c, rows[c]["words"], rows[c]["sentences"], rows[c]["sha256"][:8], rows[c]["max_jaccard_vs_JK"], rows[c]["jaccard_vs_H0"])
print(check["duplicates"]); print(est)
