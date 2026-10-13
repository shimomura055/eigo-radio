# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-02 委任_01(設計のみ・API呼出なし・費用0)。"""
import os, sys, json, hashlib, re, difflib, itertools
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_02"); os.makedirs(OUT, exist_ok=True)
PREV = json.load(open(os.path.join(ROOT, "er057_output/coffee_tts_style_8way_01/prompts_8way_01.json"), encoding="utf-8"))
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
H0 = PREV["candidates"]["H"]["style"]; assert sha(H0).startswith("49af7437")
C = {
 "H0": ("前回H完全同一(Baseline、Take1/2再利用+Take3新規)", H0,
        "前回高評価Take1の再現基準。速度指示なし、『breathe naturally』のみ。",
        "速度指示なし(息継ぎ指示のみ)", "前回実測: Adv T差20.6、Std T2 ASR警告。速度ばらつきが課題。"),
 "H1": ("自然なニュース朗読速度を明示", 
        "A warm daytime radio news presenter sharing a human-interest story, clear, credible and approachable, with a smile in the voice. Read at a natural, steady news-broadcast pace, grouping words into meaningful phrases and breathing only between ideas.",
        "速度の基準を『報道の標準朗読速度』という既知の話し方に固定し、Hの声質文は短縮のみで維持。",
        "名詞句で速度基準を明示(natural, steady news-broadcast pace)",
        "報道調が硬さを増し明るさ低下の恐れ。news paceが元々速い基準で速度が下がらない可能性。"),
 "H2": ("落ち着いた会話テンポ",
        "A bright, friendly radio presenter telling a human-interest story to one listener in a calm conversational tempo. Keep the voice clear, credible and smiling, and let each phrase flow into the next.",
        "キャスター像を『1人のリスナーへの会話』に置換し、テンポをcalm conversationalで指定。8wayでC/G(会話系)のStdのT差が小さかった点を根拠にする。",
        "テンポ語1つ(calm conversational tempo)+流れの接続1つ(flow into the next)",
        "会話調になり報道の信頼感(Hの核)が薄れる恐れ。Gのように熱量不足の懸念。"),
 "H3": ("急がず、意味の変わり目でのみ間",
        "A warm radio news presenter with a smile in the voice, clear and credible. Tell this human-interest story without rushing, linking each phrase smoothly to the next and pausing only where the meaning changes.",
        "速度を否定形1語(without rushing)で穏やかに抑え、間は肯定形『meaning changesでのみ』に限定。A(unhurried重複で間増加)の轍を避け、減速語は1回のみ。",
        "否定形の緩い抑制1つ(without rushing)",
        "8wayでAのunhurried系が文中/文末無音を増やした前例。単発でも間増加・語尾の伸びの恐れ(リスク最大候補、検知対象)。"),
 "H4": ("文章全体のリズム均一化(take間ばらつき対策)",
        "A warm radio news presenter telling a human-interest story, clear, credible and smiling. Hold one even rhythm from the first sentence to the last, with phrases grouped by meaning and breaths only between ideas.",
        "速度の絶対値ではなく『最初から最後まで一定のリズム』を指定し、文ごとの加速・減速(take間差の主因と推定)を抑える。",
        "リズム一定の指示1つ(one even rhythm)",
        "平板・機械的に聞こえる恐れ(抑揚低下)。速度の絶対値は動かず、全体が速いまま均一化するだけの可能性。"),
 "H5": ("最小限(速度指示なしでTTSに委ねる)",
        "A warm, composed radio news presenter telling a human-interest story: clear, credible and approachable, with a smile in the voice.",
        "H0から語句構造指示(Group words/phrasing/breathe)を全て外し、声質像のみ。速度・間はモデルの自然な読みに委ねる(D最短の知見の再検証、ただし声質像を維持)。",
        "速度指示なし(persona の『composed』のみが示唆)",
        "8wayのD(最短)はAdv T差19.5で不安定。H0と同等以上に速い/ばらつく可能性。語数は40未満(短さ優先の例外)。"),
}
def toks(t): return set(re.findall(r"[a-z']+", t.lower()))
def nsent(t): return len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s])
rows = {}
for k, (lab, st, di, sp, se) in C.items():
    rows[k] = {"label": lab, "style": st, "chars": len(st), "words": len(st.split()), "sentences": nsent(st), "sha256": sha(st),
               "design_intent": di, "speed_control_method": sp, "expected_side_effects": se,
               "contains_unhurried_slowly": bool(re.search(r"unhurried|slowly", st.lower()))}
sims = {}
for a, b in itertools.combinations(C, 2):
    ja, jb = toks(C[a][1]), toks(C[b][1])
    sims[f"{a}-{b}"] = {"token_jaccard": round(len(ja & jb) / len(ja | jb), 3), "char_seq_ratio": round(difflib.SequenceMatcher(None, C[a][1], C[b][1]).ratio(), 3)}
# 追記方式でないことの確認: H0を部分文字列として含む候補がないか
for k in rows:
    if k != "H0": assert H0 not in C[k][1] and C[k][1] not in H0, k
JA = {k: v["token_jaccard"] for k, v in sims.items()}
H0pairs = {k: v for k, v in JA.items() if k.startswith("H0-")}
others = {k: v for k, v in JA.items() if not k.startswith("H0-")}
check = {  # 速度指示は1つか / 間の指示と矛盾しないか / Hの声質要素(warm, clear, credible, smile)
 "H1": ("1つ(natural, steady news-broadcast pace)", "矛盾なし(息継ぎ=ideas間のみ)", "warm/clear/credible/approachable/smile 全保持"),
 "H2": ("1つ(calm conversational tempo)。flow は接続指示で速度語ではない", "矛盾なし", "bright/friendly/clear/credible/smile。warmはfriendlyで代替、approachable脱落(会話像で含意)"),
 "H3": ("1つ(without rushing)", "矛盾なし(pause only where meaning changes は意味上の間を残す)", "warm/clear/credible/smile。approachable脱落"),
 "H4": ("0〜1(one even rhythm=リズム均一、絶対速度語なし)", "矛盾なし", "warm/clear/credible/smiling。approachable脱落"),
 "H5": ("0(速度指示なし)", "間の指示なし(矛盾なし)", "warm/composed/clear/credible/approachable/smile 全保持"),
}
json.dump({"voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "method": "speech_metadata(Part.speech_metadata.style)", "candidates": rows,
           "similarity_pairs": sims, "max_jaccard_H1_to_H5": max(v for k, v in others.items()),
           "self_check": {k: dict(zip(("speed_instruction_count", "pause_consistency", "H_voice_elements"), v)) for k, v in check.items()}},
          open(os.path.join(OUT, "prompts_h_speed_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# cost
n_new = 32; per_call = 39.551 / 32
cen = n_new * per_call; hi = cen * 1.2; retry = 4 * per_call * 1.2
cost = {"calls_new": n_new, "breakdown": "H1-H5 x 3take x Std/Adv = 30 + H0 Take3 x Std/Adv = 2", "reused_calls_H0_take1_take2": 4,
        "per_call_jpy_8way_actual": round(per_call, 4), "central_jpy": round(cen, 2), "high_plus20pct_jpy": round(hi, 2),
        "tech_retry_allowance_4calls_jpy": round(retry, 2), "high_plus_retry_jpy": round(hi + retry, 2),
        "conservative_prior_estimate_high_plus_retry_jpy": 57.55, "budget_cap_jpy": 60,
        "fits_cap": (hi + retry) <= 60 and 57.55 <= 60,
        "source": "8way実績 er057_output/coffee_tts_style_8way_01/cost_02.json: 32call JPY39.551(TTS 32.423+ASR推定7.128)。prompt語数はH0〜H5が8wayのA(65語)より短く入力token同等以下。保守側 cost_estimate_01.json high_plus_retry 57.55。",
        "pricing": "gemini-3.8-flash-lite-tts Standard $0.5/$6.0 per 1M, USD/JPY 160(er005_output/cost_baseline_01/pricing_snapshot.json)",
        "excluded": "ローカルfaster-whisper測定、Std減速後ASR(必要時+約JPY4)", "elapsed_estimate_s": "約50-60(8way 32call/並列8実績50s)"}
json.dump(cost, open(os.path.join(OUT, "cost_estimate_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, r in rows.items(): print(k, r["words"], r["sentences"], r["sha256"][:8], r["contains_unhurried_slowly"])
print("H0 pairs", H0pairs); print("others", others); print(json.dumps(cost, ensure_ascii=False))
