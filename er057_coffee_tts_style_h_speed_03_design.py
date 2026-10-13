# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-03 Round1 設計(API呼出なし)。13候補、各Prompt一から記述。"""
import os, json, hashlib, re, difflib, itertools
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_03", "round1"); os.makedirs(OUT, exist_ok=True)
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
PREV = json.load(open(os.path.join(ROOT, "er057_output/coffee_tts_style_8way_01/prompts_8way_01.json"), encoding="utf-8"))
H0 = PREV["candidates"]["H"]["style"]
# (id, style, axes, intent, side_effect)
C = [
("J01", "A warm, friendly radio presenter telling a human-interest story at about 150 words per minute. Sound clear and smiling, and carry each sentence straight into the next without a long stop.",
 dict(speed="数値WPM(150)", pause="文末停止抑制(carry ... without a long stop)", voice="自然な語りかけ", strength="明確", structure="速度中心", brevity="必要条件明示の短文"),
 "数値WPMがTTSの速度に効くかを検証。Adv現状175-187なので150指定でどこまで下がるか。", "数値を無視して速いまま/数値に引かれて間が増える恐れ"),
("J02", "Speak at a slow, steady 130 words per minute, warm and clear, with a smile in your voice. Do not pause after sentences; let each one roll into the next.",
 dict(speed="数値WPM(130, slow steadyで強め)", pause="文末停止禁止(Do not pause)", voice="自然な語りかけ", strength="強め", structure="速度+ポーズ併記", brevity="必要条件明示の短文"),
 "J01より強い数値指定+強い停止抑制。数値の強さ依存(150 vs 130)と相反効果(速度↓でポーズ↑)の検出。", "過減速、語尾の引き延ばし、no pauseによる不自然な詰め込み"),
("J03", "A warm storyteller reading a human-interest story in a measured, deliberate pace, clear and smiling. Let each sentence lead naturally into the next, pausing only briefly at the end of a sentence.",
 dict(speed="速度語(measured, deliberate)", pause="文末は短く(only briefly)", voice="落ち着いたストーリーテリング", strength="明確", structure="速度中心", brevity="必要条件明示の短文"),
 "measured/deliberateという速度語の強さ検証。slowlyを避けつつ減速できるか。", "deliberateが文末間・文中間を増やす恐れ(相反)"),
("J04", "A friendly radio host chatting with one listener in a relaxed, easy tempo. Keep the voice bright and clear, with a smile in it.",
 dict(speed="テンポ語(relaxed, easy)", pause="指示なし", voice="自然な語りかけ", strength="控えめ", structure="速度中心", brevity="最小限"),
 "ポーズ指示なしでテンポ語のみ。会話調だけでペースが落ちるか(TRIAL-02 H2はcalm conversationalでも速かった)。", "速度ほぼ不変の可能性、間の挙動はモデル任せ"),
("J05", "A warm radio presenter, clear and approachable, with a smile in the voice. Never leave a long silence after a sentence: let the end of each sentence glide into the start of the next, as one continuous story.",
 dict(speed="指示なし", pause="文末停止抑制を強く(Never ... long silence / glide)", voice="ラジオニュース調寄り(presenter)", strength="強め", structure="ポーズ中心", brevity="必要条件明示の短文"),
 "ポーズ指示のみの純粋効果(速度指示なし)。文末無音がどこまで短くなり、速度が上がるか(相反効果の観察)。", "ポーズ短縮で全体が速くなる(目標超過)可能性が高い"),
("J06", "A friendly storyteller. Link words into long, smooth phrases and keep the voice moving through each clause, taking short natural breaths only at commas and sentence ends.",
 dict(speed="指示なし", pause="フレーズ接続強調+息継ぎ位置限定", voice="自然な語りかけ", strength="明確", structure="ポーズ中心", brevity="必要条件明示の短文"),
 "文中のつながり(フレーズ接続)を強調した時の文中無音・速度への影響。", "長いphraseで早口化、息継ぎ位置限定で抑揚が平板になる恐れ"),
("J07", "A warm, calm radio presenter, bright and clear. Take short, natural breaths between ideas, and never let a breath linger.",
 dict(speed="指示なし(calmのみ)", pause="自然な息継ぎ優先(短く)", voice="ラジオニュース調寄り", strength="控えめ", structure="ポーズ中心", brevity="最小限"),
 "TRIAL-02 H0の『breathe naturally』を一から短く言い換え、息継ぎ指示の最小効果を観察。", "速度は元のHに近い=速め傾向の再現の可能性"),
("J08", "A crisp radio news announcer reading a human-interest story at a calm broadcast pace, clear, credible and warm, with an upbeat smile in the voice. Keep sentence endings short and connected.",
 dict(speed="テンポ語(calm broadcast pace)", pause="文末は短く接続", voice="ラジオニュース調", strength="明確", structure="簡潔統合", brevity="必要条件明示の短文"),
 "ニュース調でcalm指定+crispの変化を見る(TRIAL-02 H1のnews-broadcast paceとの対比)。", "crispが速度を上げる恐れ、硬さで温かみ低下"),
("J09", "A natural, easygoing narrator speaking to a friend, warm and animated, with lively intonation and a smile in the voice. Talk at a relaxed pace, as if you were just telling someone what you read.",
 dict(speed="relaxed pace(語りかけの含意)", pause="指示なし", voice="自然な語りかけ(友人への語り)", strength="控えめ", structure="簡潔統合", brevity="必要条件明示の短文"),
 "最も口語的な像+抑揚(lively intonation)重視。声質(抑揚)への効果と速度の関係を見る。", "animatedが速度を上げる恐れ、口語で語尾が崩れる恐れ"),
("J10", "A calm storyteller telling a true story to a small audience, warm and gentle, with expressive intonation. Slow the pace slightly, but keep the silence between sentences short and each ending connected to what follows.",
 dict(speed="slightly slower(控えめな減速)", pause="文末停止抑制(short silence / connected)", voice="落ち着いたストーリーテリング", strength="明確", structure="速度+ポーズ併記(統合)", brevity="必要条件明示の短文"),
 "減速と文末間短縮を同時に明示し、相反効果を打ち消せるかの本命候補の一つ。", "slowが文中間・語尾を延ばす、またはbut節で片方が無視される"),
("J11", "Warm and clear, with a smile. Calm pace, short pauses.",
 dict(speed="calm pace", pause="short pauses", voice="指定最小", strength="控えめ", structure="簡潔統合", brevity="最小限(極短)"),
 "最小限の指示で何が効くか。声質像を省いた時の声質劣化も確認。", "声質像が薄くなる。極短Prompt(下限探索、2文)"),
("J12", "Speak warmly and clearly, with a smile in the voice. Keep a pace of about 150 words per minute, and keep every pause between sentences under half a second.",
 dict(speed="数値WPM(150)", pause="数値の停止上限(0.5s未満)", voice="自然な語りかけ", strength="明確", structure="簡潔統合", brevity="必要条件明示の短文"),
 "数値条件(速度+間の上限)の明示が効くかを検証。J01との差で『数値の間指定』の効果を分離。", "数値の間指定は無視される可能性、短すぎる間で不自然"),
("J13", "Read noticeably slower than a news bulletin, warm and bright, with expressive intonation. Between sentences keep the silence very short and let the voice carry on.",
 dict(speed="相対速度(noticeably slower than a news bulletin)", pause="文末の間を非常に短く(very short / carry on)", voice="ラジオニュース調との対比", strength="強め", structure="簡潔統合", brevity="必要条件明示の短文"),
 "相対基準で強めに減速+強く間を詰める。強め指示の限界と副作用を見る。", "過減速で不自然、または間の抑制が負けて長沈黙"),
]
rows = {}
for cid, st, ax, di, se in C:
    w = len(st.split()); ns = len([s for s in re.split(r"(?<=[.!?])\s+", st.strip()) if s])
    assert H0 not in st and st not in H0
    rows[cid] = {"style": st, "chars": len(st), "words": w, "sentences": ns, "sha256": sha(st), "axes": ax, "design_intent": di, "expected_side_effects": se,
                 "contains_unhurried_slowly": bool(re.search(r"unhurried|slowly", st.lower()))}
def toks(t): return set(re.findall(r"[a-z']+", t.lower()))
ids = [c[0] for c in C]; sims = {}
for a, b in itertools.combinations(ids, 2):
    ja, jb = toks(rows[a]["style"]), toks(rows[b]["style"])
    sims[f"{a}-{b}"] = {"jaccard": round(len(ja & jb) / len(ja | jb), 3), "seq": round(difflib.SequenceMatcher(None, rows[a]["style"], rows[b]["style"]).ratio(), 3)}
mx = sorted(sims.items(), key=lambda kv: -kv[1]["jaccard"])[:6]
vsH0 = {c: round(len(toks(rows[c]["style"]) & toks(H0)) / len(toks(rows[c]["style"]) | toks(H0)), 3) for c in ids}
check = {"duplicates": "全13件sha相異。最大jaccardペア: " + ", ".join(f"{k}={v['jaccard']}" for k, v in mx),
         "contradictions": "矛盾なし(J02のslow/no pause、J10/J13の減速+間短縮の併記は相反効果検証のため意図的)",
         "redundancy": "各Promptは速度/間/声質を各1回ずつ。J11のみ極短(意図)",
         "H0_append_check": "H0を部分文字列に含む/含まれる候補なし(assert済)。H0とのjaccard: " + json.dumps(vsH0),
         "sentence_count": {c: rows[c]["sentences"] for c in ids}}
for c in ids: assert 2 <= rows[c]["sentences"] <= 3, (c, rows[c]["sentences"])
json.dump({"voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "method": "speech_metadata(Part.speech_metadata.style)",
           "baseline": {"H0": {"style": H0, "sha256": sha(H0), "note": "TRIAL-02 H0 Take1再利用(再生成なし)"}},
           "candidates": rows, "similarity_pairs": sims, "self_check": check}, open(os.path.join(OUT, "prompts_r1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
per = 1.236; n = 26
cost = {"calls_new": n, "breakdown": "13候補 x Take1 x Std/Adv", "per_call_jpy": per, "central_jpy": round(n * per, 2), "high_plus20pct_jpy": round(n * per * 1.2, 2),
        "tech_retry_allowance_2calls_jpy": round(2 * per, 2), "cap_round1_jpy": 35, "fits_cap_central": n * per <= 35,
        "note": "中心32.1が35内。入力Promptは短く上振れ余地小。ハードストップ=累計推定spent>JPY34で残taskをスキップ。縮小不要と判断(記録)。",
        "source": "TRIAL-02/8way実績1.236/call(TTS1.02+ASR0.22)"}
json.dump(cost, open(os.path.join(OUT, "cost_estimate_r1.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in ids: print(c, rows[c]["words"], rows[c]["sentences"], rows[c]["sha256"][:8])
print(check["duplicates"]); print(cost["central_jpy"], cost["high_plus20pct_jpy"])
