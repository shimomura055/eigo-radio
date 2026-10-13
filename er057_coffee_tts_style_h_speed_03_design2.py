# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-03 Round2 設計(API呼出なし)。K01-K08、各Prompt一から記述。"""
import os, json, hashlib, re, difflib, itertools
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03", "round2"); os.makedirs(OUT, exist_ok=True)
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
R1 = json.load(open(os.path.join(ROOT, "er057_output/coffee_tts_style_h_speed_03/round1/prompts_r1.json"), encoding="utf-8"))
H0 = R1["baseline"]["H0"]["style"]; J = {k: v["style"] for k, v in R1["candidates"].items()}
C = [
("K01", "A gentle storyteller sharing a true story with a few friends, warm and bright, with a smile in the voice. Go slightly slower than usual, and let every sentence flow straight on into the one after it.",
 dict(speed="slightly slower(控えめ減速、1回のみ)", pause="肯定形の接続(flow straight on)", voice="落ち着いたストーリーテリング", strength="中", structure="速度+ポーズ肯定形"),
 "J10(raw速度が両レベルで揃った)の減速語を残し、J10で負けた『short silence』の否定的抑制をJ02型の肯定形接続に置換して、文末間増を防げるか。",
 "J10(slow系)とJ02(Do not pause系)の知見: 減速でStd文末+100〜200ms、肯定形ポーズ抑制はStdで有効", "減速に接続指示が負けて文末が再び伸びる/長無音が出る"),
("K02", "A bright, friendly presenter reading at a pace a little slower than a news bulletin, with lively intonation. Between sentences leave only the tiniest gap, and keep going.",
 dict(speed="相対速度(a little slower than a news bulletin、J13の中間化)", pause="極小の間(tiniest gap / keep going)", voice="ラジオ/プレゼンター+抑揚", strength="中(J13の強めを緩和)", structure="速度+ポーズ併記"),
 "J13はStd157.8/Adv177.6でAdvが+10.6速い。相対速度の強さをnoticeablyからa littleに弱め、Advを下げつつStdが過減速しないかを見る(強さ依存の確認)。",
 "J13(Std良好・Adv速すぎ)", "弱めすぎてStd/Adv両方とも速くなる可能性"),
("K03", "A steady, gentle voice, warm and clear, with a smile in it. Do not pause between sentences; keep the story moving from one to the next.",
 dict(speed="steady, gentle(slowを使わない弱形、数値なし)", pause="停止禁止(Do not pause、肯定の継続指示つき)", voice="自然な語りかけ", strength="中(J02のslowを緩和)", structure="速度語+ポーズ併記"),
 "J02(slow, steady+Do not pause)はStd 156.1/Adv 186.8でStdのみ効いた。slowを外しても減速が残るか、Advの過速が緩和するかを切り分ける。",
 "J02(Stdのみ有効、数値130は不信頼)", "slowを外すと減速効果自体が消えて両レベルが速くなる"),
("K04", "A calm, upbeat radio host with a warm, clear voice, speaking a touch slower than a news reader. Keep your breaths brief between thoughts, and never hold one.",
 dict(speed="a touch slower than a news reader(弱い相対減速)", pause="短い息継ぎ(brief breaths / never hold)", voice="ラジオニュース調寄り(host)", strength="控えめ", structure="速度+ポーズ併記"),
 "J07(calm+短い息継ぎ)はAdv 169.4で良好だがStd 168.3で速かった。弱い相対減速を一言だけ入れて、Advを保ちStdを下げられるか。",
 "J07(Advのみ合格、Stdが速い)", "Advまで遅くなる、またはStdが変わらない"),
("K05", "A friendly storyteller, warm and relaxed, with a smile in the voice. Tell it as one continuous story, so each sentence glides into the next without any stop.",
 dict(speed="relaxed(像として含意、速度指示なし)", pause="肯定形の連続(one continuous story / glides)", voice="落ち着いたストーリーテリング", strength="中", structure="ポーズ中心"),
 "J05(ニュース調像+Never long silence)は速度指示なしで速くなった。像をstorytellerに替え、肯定形の連続指示だけにして速度ずれと文末間が像で変わるか確認。",
 "J05(ポーズ指示のみで速度↑)、J06", "ポーズ短縮で全体が速くなる(Adv超過)"),
("K06", "A warm storyteller with a measured voice, clear and smiling. Pause only briefly at the end of each sentence, then go on.",
 dict(speed="measured単独(deliberateを除く)", pause="文末のみ短く(only briefly, then go on)", voice="落ち着いたストーリーテリング", strength="中", structure="速度+ポーズ併記"),
 "J03(measured, deliberate)はStd 152.9/Adv 173.3と減速に有効だが文末間・1030ms長無音が増えた。deliberateを除いたmeasured単独で間延びが切り分けられるか。",
 "J03(減速有効、間延び副作用)", "measured単独では減速が弱くStd/Adv速い、または間延びが残る"),
("K07", "A warm, trustworthy radio news presenter at a calm broadcast pace, clear and bright. Never stop between sentences; move straight on to the next.",
 dict(speed="calm broadcast pace", pause="停止禁止(Never stop / move straight on)", voice="ラジオニュース調固定", strength="中", structure="速度+ポーズ併記"),
 "J08(calm broadcast pace+short and connected)はStd 161.8/文末523ms、惜しかった。像はニュース調のまま、間抑制を強い禁止形にして文末を詰められるか。",
 "J08(Std惜しい、Adv 182速い)", "ニュース調でAdvが速いまま(+15)になる"),
("K08", "A warm, friendly storyteller with a bright, clear voice and a smile. Steady pace, brief pauses, expressive intonation.",
 dict(speed="steady pace(弱形)", pause="brief pauses", voice="自然な語りかけ+声質像(storyteller)", strength="控えめ", structure="簡潔統合(約20語、声質像つき)"),
 "J11(10語)は声質像不足で品質事故。声質像(bright, clear, expressive intonation)を残した約20語の短形で、最小指示の効果を見直す。",
 "J11(極短で品質劣化、AdvでASR挿入)", "短い指示が弱く両レベル速い、または抑揚指示が速度を上げる"),
]
def toks(t): return set(re.findall(r"[a-z']+", t.lower()))
def jac(a, b): ja, jb = toks(a), toks(b); return len(ja & jb) / len(ja | jb)
rows = {}
for cid, st, ax, di, basis, se in C:
    ns = len([s for s in re.split(r"(?<=[.!?])\s+", st.strip()) if s])
    assert H0 not in st and st not in H0 and st not in J.values(), cid
    assert 2 <= ns <= 3, cid
    mj = max(((k, round(jac(st, v), 3)) for k, v in J.items()), key=lambda x: x[1])
    rows[cid] = {"style": st, "chars": len(st), "words": len(st.split()), "sentences": ns, "sha256": sha(st), "axes": ax, "design_intent": di,
                 "round1_basis": basis, "expected_side_effects": se, "max_jaccard_vs_J": {"cand": mj[0], "jaccard": mj[1]},
                 "jaccard_vs_H0": round(jac(st, H0), 3), "seq_ratio_vs_max_J": round(difflib.SequenceMatcher(None, st, J[mj[0]]).ratio(), 3),
                 "contains_unhurried_slowly": bool(re.search(r"unhurried|slowly", st.lower())), "has_numeric_wpm": bool(re.search(r"\d", st))}
    assert not rows[cid]["has_numeric_wpm"] and not rows[cid]["contains_unhurried_slowly"]
assert len({r["sha256"] for r in rows.values()} | {sha(v) for v in J.values()} | {sha(H0)}) == 8 + len(J) + 1
ids = [c[0] for c in C]; sims = {}
for a, b in itertools.combinations(ids, 2): sims[f"{a}-{b}"] = round(jac(rows[a]["style"], rows[b]["style"]), 3)
mx = sorted(sims.items(), key=lambda kv: -kv[1])[:5]
check = {"duplicates": "K01-K08 sha全相異、J01-J13・H0ともsha相異(assert済)。K内最大jaccard: " + ", ".join(f"{k}={v}" for k, v in mx),
         "vs_J_H0": "J系/H0を部分文字列に含む・含まれる候補なし(assert済)。最大Jaccard(J系): " + ", ".join(f"{c}:{rows[c]['max_jaccard_vs_J']['cand']}={rows[c]['max_jaccard_vs_J']['jaccard']}" for c in ids) + " / H0: " + ", ".join(f"{c}={rows[c]['jaccard_vs_H0']}" for c in ids),
         "contradictions": "矛盾なし(K01/K02/K04/K06/K07は減速+間短縮の併記で、Round1で有効だった『強い形容1回の減速+肯定/禁止形の間抑制』構造の再検証)",
         "redundancy": "速度/間/声質を各1回ずつ。数値WPM・unhurried/slowly不使用(assert済)",
         "sentence_count": {c: rows[c]["sentences"] for c in ids}}
json.dump({"voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "method": "speech_metadata(Part.speech_metadata.style)",
           "baseline": {"H0": {"style": H0, "sha256": sha(H0), "note": "TRIAL-02 H0 Take1再利用(再生成なし)"}},
           "candidates": rows, "similarity_pairs": sims, "self_check": check}, open(os.path.join(OUT, "prompts_r2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
per = 1.236; n = 16
est = {"phase": "StepB", "calls_new": n, "breakdown": "8候補 x Take1 x Std/Adv", "per_call_jpy": per, "central_jpy": round(n * per, 2), "high_plus20pct_jpy": round(n * per * 1.2, 2),
       "cap_stepB_jpy": 24, "hard_stop_jpy": 26, "cap_stepC_jpy": 10, "cumulative_before_jpy": 32.43, "cap_id_jpy": 100,
       "round1_actual_per_call_jpy": round(32.43 / 26, 3), "source": "Round1実績 JPY32.43/26call=1.247/call、TRIAL-02/8way実績1.236/call",
       "fits_cap_central": n * per <= 24, "fits_cap_high": n * per * 1.2 <= 24}
json.dump({"estimate": est}, open(os.path.join(OUT, "cost_r2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in ids: print(c, rows[c]["words"], rows[c]["sentences"], rows[c]["sha256"][:8], rows[c]["max_jaccard_vs_J"], rows[c]["jaccard_vs_H0"])
print(check["duplicates"]); print(est["central_jpy"], est["high_plus20pct_jpy"], est["fits_cap_high"])
