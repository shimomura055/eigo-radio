# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-TTS-STYLE-8WAY-AB-TRIAL-01 委任_01(設計のみ・API呼出なし・費用0)。
prompts_8way_01.json / cost_estimate_01.json / similarity を生成する。TTS/LLM/ASR呼出なし。"""
import os, sys, json, hashlib, re, difflib, itertools
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "er057_output", "coffee_tts_style_8way_01")
import er019_family_x_style_profile_01 as P
def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()
CANDS = {
 "A": ("現行P8 Baseline(完全同一条件)", P.P8_TEXT),
 "B": ("P8の最小修正(減速語のみ肯定形の流れ指定へ置換、他は逐語維持)",
       "Warm, bright, cozy storytelling in the manner of a well-loved radio feature: at an easy, flowing pace, richly expressive, with full vowels and gentle emphasis, never flat or sleepy. Let the pitch rise and fall a little more on key words. Add a touch more brightness and a hint of a smile in the voice, with each phrase flowing smoothly into the next. Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard."),
 "C": ("不要な間の削減を明示(この1候補のみ)",
       "Warm, bright storytelling with a friendly smile in the voice. Do not pause after every sentence: take a breath only where the meaning truly needs one, and let one sentence lead straight into the next. Keep consonants distinct and word endings clean."),
 "D": ("最短Prompt(過剰制御の回避)",
       "Warm, bright and clear, like a friendly radio host chatting naturally with one listener."),
 "E": ("テンポ・文間のつながりを肯定形で指定(F5系の友人への語り+lively rhythm)",
       "Tell this like a short story to a friend: a lively, natural rhythm in which every sentence picks up right where the last one left off, so the whole passage sounds like one continuous thought. Warm, friendly and upbeat, with clear, credible news narration."),
 "F": ("明るさ・抑揚を少し強める(演技過剰は避ける)",
       "Bright, warm and smiling, with lively, melodic intonation: let the pitch lift on key words and numbers and settle gently at the end of each idea. Expressive but natural, never theatrical. Crisp consonants and clean word endings."),
 "G": ("明瞭さと自然な会話速度の両立(Podcastホスト像)",
       "An engaging podcast host explaining an interesting news story to a curious listener at a natural conversational pace: every word easy to catch, with a smooth, steady rhythm and a warm, friendly tone. Consonants distinct, word endings complete."),
 "H": ("PD1系(報道キャスター調、実測最速)+PD8の温かさの組合せ",
       "A warm, composed daytime radio news presenter telling a human-interest story: clear, credible and approachable, with a smile in the voice. Group words into meaningful phrases, keep the phrasing smooth and connected, and breathe naturally between ideas."),
}
DESIGN = {  # 設計意図 / 想定副作用 / 減速語の扱い
 "A": ("比較基準。P8逐語(sha 3eadf4f6)。", "v5実測どおり: 文中の小無音多め、Std Part1に局所長無音、take間リズム差大。", "unhurried 2回(減速語あり=現状)。"),
 "B": ("単一変数の検証: 『unhurried』が文中小無音(+55%)の原因かを、P8の他要素(声質・抑揚・明瞭さ)を保ったまま切り分ける。", "文末の間は残る可能性。『flowing』で語尾が流れて明瞭さが落ちる懸念(明瞭さ文は維持)。", "unhurriedを削除し『easy, flowing pace』『flowing smoothly into the next』へ。減速語を使わず速度は自然に委ねる(180目安に近づく想定)。"),
 "C": ("唯一、不要な間の削減を直接指示。意味上の息継ぎは『meaning truly needs』で残す。", "命令(Do not pause)の副作用: 息継ぎ不足、早口化、聞き疲れ、文末の語尾が詰まる。", "減速語なし。速度語も書かず、間の削減のみで全体が速くなる可能性(180を超える懸念をWPMで確認)。"),
 "D": ("指示を最小化しモデル本来の自然な語りに任せる。過剰制御による不自然な間・抑揚を避ける。", "明瞭さ・明るさの保証が弱い。take間差が大きい可能性。", "減速語なし。chatting naturallyで会話速度。"),
 "E": ("文と文を一続きの考えとして繋げる肯定形のテンポ指示。F5の『lively natural rhythm』を継承。", "友人調で口語化し、ニュース報道の信頼感が落ちる可能性(credible news narrationで補強)。", "not hurriedを含めず『lively, natural rhythm』で速度を暗示。減速語なし。"),
 "F": ("明るさ・抑揚の底上げ(目標2・4)。語尾を落ち着かせて抑揚の起伏で文の終わりを作る。", "演技過剰・大げさ、数字強調で不自然な上昇調。間への直接効果は限定的。", "速度語なし。『settle gently』は語尾の抑揚指示で、減速語ではない。"),
 "G": ("明瞭さ(目標3)と自然速度(目標5)の両立。PD4系Podcast像+P8の明瞭さ文を要約。", "平板化・熱量不足、明るさがP8より下がる懸念。", "減速語なし。『natural conversational pace』『smooth, steady rhythm』で180目安に整合。"),
 "H": ("PD1(報道キャスター調、実測WPM最速186.8)の落ち着いた信頼感+PD8系の smile を統合。意味単位でまとめ文中の細かい止まりを減らす。", "硬い・淡々とした印象で明るさ不足、抑揚が控えめ。", "減速語なし。『breathe naturally between ideas』で息継ぎを意味の切れ目に限定。"),
}
def toks(t): return set(re.findall(r"[a-z']+", t.lower()))
def sim(a, b):
    ja, jb = toks(a), toks(b)
    return round(len(ja & jb) / len(ja | jb), 3), round(difflib.SequenceMatcher(None, a, b).ratio(), 3)
def main():
    os.makedirs(OUT, exist_ok=True)
    assert CANDS["A"][1] == P.P8_TEXT and sha(P.P8_TEXT) == P.P8_SHA256
    rows = {k: {"label": v[0], "style": v[1], "chars": len(v[1]), "words": len(v[1].split()), "sha256": sha(v[1]),
                "design_intent": DESIGN[k][0], "expected_side_effects": DESIGN[k][1], "decel_word_policy": DESIGN[k][2],
                "contains_unhurried": "unhurried" in v[1].lower()} for k, v in CANDS.items()}
    sims = {}
    for a, b in itertools.combinations(CANDS, 2):
        j, s = sim(CANDS[a][1], CANDS[b][1]); sims[f"{a}-{b}"] = {"token_jaccard": j, "char_seq_ratio": s}
    json.dump({"voice": "Aoede", "model": "gemini-3.8-flash-lite-tts", "method": "speech_metadata(Part.speech_metadata.style)", "candidates": rows,
               "similarity_pairs": sims, "max_jaccard_excluding_A_B": max(v["token_jaccard"] for k, v in sims.items() if k != "A-B")},
              open(os.path.join(OUT, "prompts_8way_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, r in rows.items(): print(k, r["chars"], r["words"], r["sha256"][:8], r["contains_unhurried"])
    top = sorted(sims.items(), key=lambda x: -x[1]["token_jaccard"])[:6]; print("top similar", top)
    # cost
    PI, PO, FX, AI, AO = 0.5, 6.0, 160.0, 1.25, 5.0
    ref = {"std": {"in": 143, "out": 1139, "dur": 45.53, "chars": 657}, "adv": {"in": 157, "out": 1177, "dur": 47.08, "chars": 731}}
    def tts(i, o): return (i * PI + o * PO) / 1e6 * FX
    def asr(d, ch): return (d * 10 * AI + ch / 4.0 * AO) / 1e6 * FX
    res = {}
    for lv, r in ref.items():
        c = tts(r["in"], r["out"]); a = asr(r["dur"], r["chars"])
        hi = tts(r["in"] + 40, int(r["out"] * 1.2)); ah = asr(r["dur"] * 1.2, r["chars"])
        res[lv] = {"tts_central": round(c, 4), "asr_central": round(a, 4), "tts_high": round(hi, 4), "asr_high": round(ah, 4)}
    cen = 16 * sum(res[l]["tts_central"] + res[l]["asr_central"] for l in res)
    high = 16 * sum(res[l]["tts_high"] + res[l]["asr_high"] for l in res)
    pace = 33.656 / 24
    out = {"calls": 32, "per_level": res, "total_central_jpy": round(cen, 2), "total_high_jpy_(out+20%)": round(high, 2),
           "cross_check_pace_trial_02_jpy_per_call": round(pace, 3), "cross_check_total_32calls": round(pace * 32, 2),
           "tech_failure_retry_allowance_4calls_jpy": round(4 * (high / 32), 2), "high_plus_retry_jpy": round(high + 4 * high / 32, 2),
           "budget_cap_jpy": 60, "fits_cap": (high + 4 * high / 32) <= 60,
           "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json gemini-3.8-flash-lite-tts Standard in $0.5/1M, out $6.0/1M(25tok/s), USD/JPY 160; ASR gpt-4o-mini-transcribe in $1.25/1M, out $5/1M(er057_tone_trial_final_build_03.py asr_and_judge推定式)",
           "token_reference": "er057_output/coffee_final_v4/generation_log_v4.jsonl std_part1 in143/out1139, adv_part1 in157/out1177; cost_actual_02.json 24call JPY33.656",
           "excluded": "ローカルfaster-whisper small測定(費用0)、Std減速後ASR再実施なし(必要時+約JPY4)"}
    json.dump(out, open(os.path.join(OUT, "cost_estimate_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))
if __name__ == "__main__": main()
