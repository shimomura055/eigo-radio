# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04 Round4 設計(API呼出なし)。M01-M06、全て一から記述。"""
import os, json, hashlib, re, difflib, itertools
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_04", "round4"); os.makedirs(OUT, exist_ok=True)
BASE = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03")
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
PRIOR = {}
for r in (1, 2, 3):
    P = json.load(open(os.path.join(BASE, f"round{r}", f"prompts_r{r}.json"), encoding="utf-8"))
    if r == 1: H0 = P["baseline"]["H0"]["style"]
    PRIOR.update({k: v["style"] for k, v in P["candidates"].items()})
assert len(PRIOR) == 27
C = [
("M01", "A gentle friend telling a true story across the table, bright and warm, smiling as you speak. Go slightly slower than usual; when the story turns to a new point, start it as easily as you start any sentence.",
 dict(speed="slightly slower(K01型、指示文として1回)", pause="話題転換(新しい要点)でも通常の文頭と同じ入り方(肯定形)", voice="親しい語り手(K01の穏やか+明るい構造を保持)", strength="中", structure="K01構造(像+減速指示+接続指示)の接続指示を話題転換の扱いへ置換"),
 "K01(raw167.8/172.6)の構造を保ち、flow straight onの代わりに話題転換点の扱いを指示。Std長無音3本(約18/33秒付近)が減るかを見る。",
 "K01(減速有効・Std長無音3本)、Step A(S05/S09に長無音が集中)", "接続指示が文頭全般を詰めてAdvが速くなる"),
("M02", "A friendly, clear narrator relating a true story at a slightly slower pace than usual. Take up each new point just as you take up any sentence, starting right after the last word, as one connected telling.",
 dict(speed="slightly slower pace than usual(L02型、1回)", pause="新しい要点も他の文と同じく直前語の直後から開始(肯定形)", voice="ナレーター(明瞭・親しみ)", strength="中〜やや強", structure="L02構造(ナレーター+相対ペース+一続きの語り)の禁止形を肯定の開始位置指示+話題転換へ置換"),
 "L02(raw165.0/171.5、Std文末563ms・長無音870ms1本)の構造を保ち、待たない(禁止形)を直前語の直後から開始の肯定形+話題転換の扱いに置換。",
 "L02(Std/Adv速度が揃う)、Step A", "right after the last wordが文末全体を詰めすぎてAdv超過、または息継ぎ不足"),
("M03", "A bright, warm voice with a smile in it, telling a true story to a friend. Read slightly slower than usual, and treat every change of topic as just another sentence break.",
 dict(speed="slightly slower(像に埋めず独立の指示文として置換)", pause="話題の変わり目=普通の文の切れ目と同じ扱い(肯定形)", voice="明るく温かい声", strength="中", structure="像(速度語なし)+速度指示文+話題転換指示文"),
 "L05(像に減速を埋めて不発)の逆で、減速語を話者像から外し独立した指示文にして効きを確保。話題転換を通常の文末と同等に扱わせる。",
 "L05(像埋込は不発)、K01/L02(指示としての減速は有効)、Step A", "3要素(声/速度/話題転換)の指示分離で話題転換指示が薄まる"),
("M04", "A friendly radio presenter, calm and clear, sharing a true story. Let your pace be measured. When the story moves on to something new, go into it as lightly as into any other sentence.",
 dict(speed="measured(指示文として1回、K06/L04型の語を別文に置く)", pause="話題転換でも他の文頭と同じ軽さで入る(肯定形)", voice="落ち着いた明瞭なラジオ進行役", strength="中", structure="像+独立の速度文(measured)+話題転換文(3文)"),
 "measuredをK06の話者像内ではなく独立の短い指示文に置き直す。K06はStd文末478/486msで再現済み、Advで長無音1040ms/ASR揺れがあり、話題転換の指示で補えるかを見る。",
 "K06(Std合格2/2、Advで長無音)、Step A", "短い独立文でmeasuredの減速力が出ない/Advが速い"),
("M05", "A warm, bright storyteller telling a true story, going slightly slower than usual. Finish every sentence fully, then move straight to the next one, even when the story changes direction.",
 dict(speed="slightly slower(像側ではなく進行の描写、1回)", pause="語尾を最後まで言い切って次へ直行、話の方向が変わるときも同様(肯定形)", voice="温かく明るい語り手", strength="中", structure="像+減速+語尾言い切り→次へ(話題転換を含む)"),
 "L01(語尾を柔らかく終えて即次へ、不発)を最後まで言い切って次へに変え、話題転換の扱いを併記して再検証。",
 "L01(Std長無音0だが速度ずれ)、Step A", "言い切りの強調で文末が長くなる/Advが速すぎる(L01型)"),
("M06", "A calm, friendly voice with a smile in it, speaking at a measured pace. Say each sentence ending clearly and carry on at once, giving a change of subject the same short stop as every other sentence.",
 dict(speed="measured pace(指示文内の語として1回)", pause="語尾を明瞭に言い切って即続行、話題転換にも他と同じ短い間(肯定形)", voice="穏やかで親しみのある声", strength="中", structure="像+速度+語尾明瞭→続行+話題転換の間の統一"),
 "語尾を落とさず次へ系の2案目。M05と異なり減速語をmeasuredにし、話題転換の間を他と同じ短い間と明示して長無音を均す。",
 "L04(均一化の逆効果。ここでは長さでなく短さの統一を指示)、K06、Step A", "同じ短い間が機械的な均一さを生む(L04型)"),
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
                 "jaccard_vs_H0": round(jac(st, H0), 3), "seq_ratio_vs_max": round(difflib.SequenceMatcher(None, st, PRIOR[mj[0]]).ratio(), 3),
                 "contains_unhurried_slowly": bool(re.search(r"unhurried|slowly", st.lower())), "has_numeric_wpm": bool(re.search(r"\d", st)),
                 "contains_position_words": bool(re.search(r"delay|International|continue|Department|Agriculture|Coffee Organization", st))}
    assert not rows[cid]["has_numeric_wpm"] and not rows[cid]["contains_unhurried_slowly"] and not rows[cid]["contains_position_words"]
assert len({r["sha256"] for r in rows.values()} | {sha(v) for v in PRIOR.values()} | {sha(H0)}) == 6 + 27 + 1
ids = [c[0] for c in C]; sims = {}
for a, b in itertools.combinations(ids, 2): sims[f"{a}-{b}"] = round(jac(rows[a]["style"], rows[b]["style"]), 3)
mx = sorted(sims.items(), key=lambda kv: -kv[1])[:5]
check = {"duplicates": "M01-M06 sha全相異、J01-J13・K01-K08・L01-L06・H0ともsha相異(assert済)。M内最大Jaccard: " + ", ".join(f"{k}={v}" for k, v in mx),
         "vs_prior": "J/K/L/H0を部分文字列に含む・含まれる候補なし(assert済)。最大Jaccard(J/K/L): " + ", ".join(f"{c}:{rows[c]['max_jaccard_vs_prior']['cand']}={rows[c]['max_jaccard_vs_prior']['jaccard']}" for c in ids) + " / H0: " + ", ".join(f"{c}={rows[c]['jaccard_vs_H0']}" for c in ids),
         "contradictions": "矛盾なし(減速語は各1回、接続は話題転換の扱いに限定)。paragraphの語は使わない(tts_inputに段落区切りが無いため。silence_positions_r4.md)。",
         "redundancy": "速度語は各1回、数値WPM・unhurried/slowly不使用・位置の語を直接指定していない(assert済)。全て肯定形(not/never/do not不使用、assert済)",
         "sentence_count": {c: rows[c]["sentences"] for c in ids}}
assert not any(re.search(r"\b(do not|dont|never|not)\b", rows[c]["style"].lower()) for c in ids)
json.dump({"voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "method": "speech_metadata(Part.speech_metadata.style)",
           "baseline": {"H0": {"style": H0, "sha256": sha(H0)}}, "candidates": rows, "similarity_pairs": sims, "self_check": check},
          open(os.path.join(OUT, "prompts_r4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
per = 1.281; n = 12
est = {"phase": "StepC", "calls_new": n, "breakdown": "M01-M06 x Take1 x Std/Adv=12call", "per_call_jpy": per, "central_jpy": round(n * per, 2), "high_plus20pct_jpy": round(n * per * 1.2, 2),
       "cap_stepC_jpy": 20, "hard_stop_jpy": 23, "cap_stepD_jpy": 20, "cumulative_before_jpy": 72.99, "cap_total_jpy": 300, "hard_stop_total_jpy": 290,
       "source": "Round3実績 JPY20.49/16call=1.281/call", "fits_cap_central": n * per <= 20, "fits_hard_stop_high": n * per * 1.2 <= 23,
       "cumulative_after_central_jpy": round(72.99 + n * per, 2), "stepD_max_call": 8, "stepD_central_jpy": round(8 * per, 2)}
json.dump({"estimate": est}, open(os.path.join(OUT, "cost_r4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in ids: print(c, rows[c]["words"], rows[c]["sentences"], rows[c]["sha256"][:8], rows[c]["max_jaccard_vs_prior"], rows[c]["jaccard_vs_H0"])
print(check["duplicates"]); print(est)
