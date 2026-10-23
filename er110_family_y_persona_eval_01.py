# -*- coding: utf-8 -*-
"""er110_family_y_persona_eval_01.py -- Family Y Persona Trial 評価(DEV/Trial専用、Gate化しない観測)。
E1 blind claim extraction / E2 blind speaker attribution(全文版・冒頭2文版)/ E3 抽象語率 / E5 感情 / E6 文のリズム差・締めの型 /
E9 芝居 / E10 具体物 / E11 Tension文長 / E12 Comment・見出し / E13補助(LLM対比較、最終はOpus・ユーザー)/ blind対比較ファイル生成。
LLM判定(E1/E2/E13補助)はgpt-6-luna(同系列モデルの判定でバイアスあり=補助。OPEN-218)。
"""
import argparse
import json
import os
import random
import re
import statistics as st

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_text_trial_01 as p

ROOT = "er110_output/family_y_persona_trial_01/school_phone_ban"
OLD_RUN = "er110_output/family_y_trial_01/school_phone_ban"
JUDGE = y0.MODEL_CHEAP

ABSTRACT = ["責任", "判断", "根拠", "優先", "基準", "価値", "尊厳", "余地", "視点", "観点", "目的", "方針", "配分", "効果", "学力", "環境", "仕組み", "重さ", "納得", "立場",
            "意味", "自分", "他者", "必要", "理由", "大切", "守り"]
EMOTION = ["怖", "こわ", "嫌", "いや", "腹が立", "むかつ", "悔し", "うれし", "嬉し", "ほっと", "不安", "つらい", "辛い", "しんどい", "情けな", "恥ずかし", "寂し", "さみし",
           "悲し", "安心", "焦", "イライラ", "ありがた", "助か", "申し訳", "罪悪", "笑", "泣", "くやし", "心配", "疲れ", "気まず", "迷", "困"]
QUESTION_END = re.compile(r"(だろう|でしょう|のか|かな|かしら|ない[?？]|だろうか|んだろう|ますか|だよね)[。？?]?$")
PROFILES_EN = {"A": "A father who works as a site supervisor and has a daughter in high school.",
               "B": "A high school nurse-teacher (school nurse) who sees students in the nurse's office in the morning.",
               "C": "A 19-year-old who works in a warehouse in the daytime and goes to a night (part-time) high school."}
PROFILE_OF_SLOT = {"voice_1": "A", "voice_2": "B", "voice_3": "C"}


def sents_ja(t):
    return [s for s in re.split(r"(?<=[。！？!?])", t) if s.strip()]


def ja_metrics(t: str) -> dict:
    s = sents_ja(t)
    L = [len(x) for x in s]
    n = max(1, len(t))
    return {"chars": len(t), "sentences": len(s), "mean_sent_len": round(st.mean(L), 1) if L else 0, "sd_sent_len": round(st.pstdev(L), 1) if len(L) > 1 else 0,
            "short_sentences_le12": sum(1 for x in L if x <= 12), "long_sentences_ge35": sum(1 for x in L if x >= 35),
            "abstract_per_100": round(100 * sum(t.count(w) for w in ABSTRACT) / n, 2), "emotion_hits": sum(t.count(w) for w in EMOTION),
            "question_like_sentences": sum(1 for x in s if QUESTION_END.search(x.strip())), "question_marks": t.count("？") + t.count("?"),
            "exclamations": t.count("！") + t.count("!"), "ends_with_nda": sum(1 for x in s if re.search(r"んだ。$", x.strip()))}


def _chat_json(client, prompt, schema, stage, effort="medium"):
    resp = y0.chat(client, model=JUDGE, effort=effort, user=prompt, schema=schema, stage=stage)
    return json.loads(resp.output_text), y0.resp_meta(resp)


EXTRACT_SCHEMA = {"name": "e1_extract", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["label", "main_point"],
                                           "properties": {"label": {"type": "string"}, "main_point": {"type": "string"}}}}}}}
MATCH_SCHEMA = {"name": "e1_match", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["label", "verdict", "reason"],
                                           "properties": {"label": {"type": "string"}, "verdict": {"type": "string", "enum": ["MATCH", "PARTIAL", "NO"]},
                                                          "reason": {"type": "string"}}}}}}}
ATTR_SCHEMA = {"name": "e2_attr", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["items"], "properties": {
    "items": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["label", "profile", "confidence"],
                                           "properties": {"label": {"type": "string"}, "profile": {"type": "string", "enum": ["A", "B", "C"]},
                                                          "confidence": {"type": "string", "enum": ["high", "medium", "low"]}}}}}}}
PAIR_SCHEMA = {"name": "e13_pair", "strict": True, "schema": {"type": "object", "additionalProperties": False,
                                                              "required": ["more_real_person", "more_polite_explaining", "reason"],
                                                              "properties": {"more_real_person": {"type": "string", "enum": ["Text 1", "Text 2"]},
                                                                             "more_polite_explaining": {"type": "string", "enum": ["Text 1", "Text 2"]},
                                                                             "reason": {"type": "string"}}}}


def e1(client, voices: dict, lang: str, tag: str, seed: int) -> dict:
    labels = ["X", "Y", "Z"]
    order = list(p.VOICE_SLOTS)
    random.Random(seed).shuffle(order)
    blocks = "\n\n".join(f"[{lab}]\n{voices[s]}" for lab, s in zip(labels, order))
    ex, m1 = _chat_json(client, f"Below are three first-person monologues from three different people ({lang}). For each, write ONE sentence in English: "
                        f"the single thing the speaker most wants to say. Use only what is in the text.\n\n{blocks}", EXTRACT_SCHEMA, f"yp_e1_extract_{tag}", "low")
    by = {x["label"]: x["main_point"] for x in ex["items"]}
    intended = "\n".join(f"[{lab}] intended claim (Japanese): {p.SHEETS[s]['claim']}\n[{lab}] extracted: {by.get(lab, '')}" for lab, s in zip(labels, order))
    mt, m2 = _chat_json(client, "For each person, judge whether the extracted one-sentence point captures the intended claim (MATCH = same main claim; PARTIAL = related but "
                        "misses or blurs the core; NO = different).\n\n" + intended, MATCH_SCHEMA, f"yp_e1_match_{tag}", "low")
    verdict = {}
    for lab, s in zip(labels, order):
        v = next((x for x in mt["items"] if x["label"] == lab), {})
        verdict[s] = {"extracted": by.get(lab), "verdict": v.get("verdict"), "reason": v.get("reason")}
    return {"order": order, "per_voice": verdict, "match_count": sum(1 for v in verdict.values() if v["verdict"] == "MATCH"), "meta": [m1, m2]}


def e2(client, paras: dict, tag: str, seed: int, first2: bool) -> dict:
    labels = ["P", "Q", "R"]
    order = list(p.VOICE_SLOTS)
    random.Random(seed).shuffle(order)

    def cut(t):
        ss = [x for x in re.split(r"(?<=[.!?。！？])\s*", t.strip()) if x.strip()]
        return " ".join(ss[:2]) if first2 else t
    blocks = "\n\n".join(f"[{lab}]\n{cut(paras[s])}" for lab, s in zip(labels, order))
    profs = "\n".join(f"{k}: {v}" for k, v in PROFILES_EN.items())
    res, m = _chat_json(client, f"Three monologues by three different people are given in shuffled order. Match each monologue to one profile (each profile used exactly once).\n\n"
                        f"Profiles:\n{profs}\n\nMonologues:\n{blocks}", ATTR_SCHEMA, f"yp_e2_{tag}", "low")
    per = {}
    for lab, s in zip(labels, order):
        x = next((i for i in res["items"] if i["label"] == lab), {})
        per[s] = {"predicted": x.get("profile"), "correct": x.get("profile") == PROFILE_OF_SLOT[s], "confidence": x.get("confidence")}
    return {"first2_only": first2, "per_voice": per, "correct_count": sum(1 for v in per.values() if v["correct"]), "meta": m}


def closing_type_of(ja: str, slot: str) -> str:
    last = sents_ja(ja)[-1].strip() if sents_ja(ja) else ""
    if QUESTION_END.search(last) or "？" in last:
        return "question"
    if "ほしい" in last or "約束" in last:
        return "promise_request"
    if "俺は" in last or "だ、俺" in last:
        return "self_deprecating_assertion"
    return "other"


def cmd_eval(a):
    rd = f"{ROOT}/{a.iter}"
    ed = f"{rd}/english"
    cl.install(f"{rd}/raw_usage_log_eval.jsonl")
    client = vfl01.get_client()
    voices_ja = {s: w1.rdt(f"{rd}/voices/{s}.txt").strip() for s in p.VOICE_SLOTS} if not os.path.exists(f"{rd}/gate_voices/final_texts.json") else json.load(open(f"{rd}/gate_voices/final_texts.json", encoding="utf-8"))
    tension_ja = json.load(open(f"{rd}/gate_tension/final_texts.json", encoding="utf-8"))["tension"]
    en = {lvl: p.split_en_article(w1.rdt(f"{ed}/{lvl}/article.md")) for lvl in ("a2", "b1b")}
    out = {"iter": a.iter, "judge": f"{JUDGE}(補助。同系列バイアスあり、最終はOpus/Fable/ユーザー)", "levels": {}}
    # ---- 決定論メトリクス ----
    out["ja_metrics"] = {s: ja_metrics(voices_ja[s]) for s in p.VOICE_SLOTS}
    out["ja_metrics"]["tension"] = ja_metrics(tension_ja)
    vm = [out["ja_metrics"][s] for s in p.VOICE_SLOTS]
    out["E6_ja"] = {"mean_sent_len_range": round(max(x["mean_sent_len"] for x in vm) - min(x["mean_sent_len"] for x in vm), 1),
                    "first_person_kinds": len({p.SHEETS[s]["first_person"] for s in p.VOICE_SLOTS}),
                    "opening_types": [re.split(r"[、。]", voices_ja[s])[0][:14] for s in p.VOICE_SLOTS],
                    "closing_types": {s: closing_type_of(voices_ja[s], s) for s in p.VOICE_SLOTS},
                    "closing_type_kinds": len({closing_type_of(voices_ja[s], s) for s in p.VOICE_SLOTS})}
    out["E3_abstract_voice_max"] = max(x["abstract_per_100"] for x in vm)
    out["E3_abstract_tension"] = out["ja_metrics"]["tension"]["abstract_per_100"]
    out["E5_emotion_hits"] = {s: out["ja_metrics"][s]["emotion_hits"] for s in p.VOICE_SLOTS}
    out["E9"] = {s: {"exclamations": out["ja_metrics"][s]["exclamations"], "role_words": p.ROLE_WORD_RE.findall(voices_ja[s])} for s in p.VOICE_SLOTS}
    out["E11"] = p.tension_monitors(tension_ja)
    out["E14_safety"] = {"numbers_in_voices": {s: p.NUM_RE.findall(voices_ja[s]) for s in p.VOICE_SLOTS}, "interview_expr": {s: p.INTERVIEW_RE.findall(voices_ja[s]) for s in p.VOICE_SLOTS},
                         "first_person_kept": {s: p.SHEETS[s]["first_person"] in voices_ja[s] for s in p.VOICE_SLOTS}, "four_parts": True}
    # E10: Tensionの具体物(英語・日本語)
    objs = {"basket_living_room": r"(basket|charging|living room)", "pillow_nurse_screen": r"(pillow|nurse|bed)", "shift_messages": r"(shift|break)"}
    for lvl in ("a2", "b1b"):
        t = en[lvl]["paragraphs"][3]
        out.setdefault("E10", {})[lvl] = {k: bool(re.search(v, t, re.I)) for k, v in objs.items()}
    # ---- 英語の文長・リズム(E6英語) ----
    for lvl in ("a2", "b1b"):
        out["levels"][lvl] = {"en_monitors": p.en_monitors(w1.rdt(f"{ed}/{lvl}/article.md"))}
    # ---- LLM判定(補助): E1/E2 ----
    for lvl in ("a2", "b1b"):
        paras = {s: en[lvl]["paragraphs"][i] for i, s in enumerate(p.VOICE_SLOTS)}
        out["levels"][lvl]["E1"] = e1(client, paras, "English", f"{a.iter}_{lvl}", seed=11)
        out["levels"][lvl]["E2_full"] = e2(client, paras, f"{a.iter}_{lvl}_full", seed=21, first2=False)
        out["levels"][lvl]["E2_first2"] = e2(client, paras, f"{a.iter}_{lvl}_first2", seed=31, first2=True)
    # ---- E13補助: 前回R0g(JA)との順序ランダム対比較(盲検) ----
    old = y0.parse_article(w1.rdt(f"{OLD_RUN}/y_writer/gate_r0/article_final.md"))["paragraphs"]
    old_v = "\n\n".join(old[1:4])
    new_v = "\n\n".join(voices_ja[s] for s in p.VOICE_SLOTS)
    pairs = []
    for k, seed in enumerate((101, 202)):
        flip = random.Random(seed).random() < 0.5
        t1, t2 = (new_v, old_v) if flip else (old_v, new_v)
        res, m = _chat_json(client, "Below are two texts (Japanese), each containing three people speaking in the first person about whether schools should ban phones. "
                            "Answer: (1) in which text do the people sound more like real people speaking about their own lives? (2) in which text does it sound more like a "
                            "well-behaved student politely explaining an opinion?\n\nText 1:\n" + t1 + "\n\nText 2:\n" + t2, PAIR_SCHEMA, f"yp_e13_aux_{a.iter}_{k}", "low")
        new_label = "Text 1" if flip else "Text 2"
        pairs.append({"seed": seed, "new_is": new_label, "more_real_person_is_new": res["more_real_person"] == new_label,
                      "more_polite_explaining_is_new": res["more_polite_explaining"] == new_label, "reason": res["reason"], "meta": m})
    out["E13_aux_llm_pairs"] = {"note": "補助(LLM、同系列バイアス)。主評価はOpus/Fableのblind対比較とユーザー試聴", "pairs": pairs,
                                "new_more_real_count": sum(1 for x in pairs if x["more_real_person_is_new"]),
                                "new_less_polite_count": sum(1 for x in pairs if not x["more_polite_explaining_is_new"])}
    w1.wj(f"{rd}/eval_01.json", out)
    print(json.dumps({"E6_ja": out["E6_ja"], "E1": {l: out["levels"][l]["E1"]["match_count"] for l in out["levels"]},
                      "E2_full": {l: out["levels"][l]["E2_full"]["correct_count"] for l in out["levels"]},
                      "E2_first2": {l: out["levels"][l]["E2_first2"]["correct_count"] for l in out["levels"]},
                      "E13aux": out["E13_aux_llm_pairs"]["new_more_real_count"], "E10": out["E10"]}, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("eval",))
    ap.add_argument("--iter", default="it1")
    a = ap.parse_args()
    cmd_eval(a)


if __name__ == "__main__":
    main()
