# -*- coding: utf-8 -*-
"""Trial専用: 方式A2(統合+screening)・方式C2(既存P7候補 -> 1 call 区分判定+一般化 -> 検証)。"""
import kpg01_llm as L
import kpg01_validate as V
from kpg01_methods import *   # noqa: F401,F403
from kpg01_methods import (BODY, CHUNK_DEFS, GEN_RULES, A_SCHEMA, B4_SCHEMA, prompt_A, prompt_B4, prod_p7_cands)

SCREEN_PROPS = {"span": {"type": "string"}, "cls": {"type": "string", "enum": ["W", "F", "C"]},
                "difficulty": {"type": "string", "enum": ["advanced", "upper_intermediate", "easy"]}, "note_ja": {"type": "string"}}
A2_SCHEMA = {"name": "kp_cards2", "schema": {"type": "object", "additionalProperties": False, "required": ["screening", "items", "word_candidates"], "properties": {
    "screening": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": list(SCREEN_PROPS), "properties": SCREEN_PROPS}},
    "items": A_SCHEMA["schema"]["properties"]["items"], "word_candidates": {"type": "array", "items": {"type": "string"}}}}}


def prompt_A2(text):
    return prompt_A(text).replace(
        "学習用の形(display_form)まで仕上げてください。",
        "学習用の形(display_form)まで仕上げてください。手順: まずscreeningに、本文から見つけた表現候補(最大14個。2〜5語の連続した語句)を、"
        "W/F/Cの区分・難易度・短い所見つきで列挙し、次に、Cでeasyでないものから最大7件をitemsに仕上げる"
        "(特に、比喩・慣用的に使われた表現と、字面だけで意味が取れる表現の見分けに注意)。", 1)


def run_A2(case, *, model="gpt-6.1-sol", effort="low", tag="A2"):
    log = {"stages": [], "tag": tag}
    o, m = L.call(model, prompt_A2(case["text"]), A2_SCHEMA, effort=effort, tag=f"{case['id']}:{tag}")
    log["stages"].append({"stage": "A2_integrated", **{k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}})
    items, dropped = [], []
    for c in o["items"]:
        c["display_form"] = V.strip_trailing_slot(c["display_form"])
        ok1 = V.span_in_text(c["source_span"], case["text"])
        ok2, why = V.display_check(c["display_form"], c["source_span"])
        if ok1 and ok2:
            items.append(c)
        else:
            dropped.append({"span": c["source_span"], "display_form": c["display_form"], "why": (["本文不一致"] if not ok1 else []) + why})
    log["validator_dropped"] = dropped
    log["word_candidates"] = o.get("word_candidates")
    log["screening"] = o["screening"]
    return {"items": items[:7], "log": log}


RG_SCHEMA = {"name": "kp_rg", "schema": {"type": "object", "additionalProperties": False, "required": ["judgements"], "properties": {
    "judgements": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "cls", "chunk_type", "chunk_reason_ja", "difficulty", "keep", "display_form", "gloss_ja", "sense_note_ja", "generalization_note_ja"],
        "properties": {"id": {"type": "integer"}, "cls": {"type": "string", "enum": ["W", "F", "C"]},
                       "chunk_type": {"type": "string", "enum": ["idiom", "phrasal_verb", "collocation", "fixed_phrase", "compound_noun", "none"]},
                       "chunk_reason_ja": {"type": "string"}, "difficulty": {"type": "string", "enum": ["advanced", "upper_intermediate", "easy"]},
                       "keep": {"type": "boolean"}, "display_form": {"type": "string"}, "gloss_ja": {"type": "string"},
                       "sense_note_ja": {"type": "string"}, "generalization_note_ja": {"type": "string"}}}}}}}


def prompt_RG(text, cands):
    lines = [f"{i}. {c['span']}\n   文: {c['sentence']}" for i, c in enumerate(cands, 1)]
    return ("次は英語記事から抽出された学習候補フレーズです。各候補を評価し、ユーザーが修正せずに選べる候補だけをkeep=trueにし、"
            "keep=trueの候補には学習用の一般形まで仕上げてください。\n\n"
            + CHUNK_DEFS + "\n\n## 判定手順\n各候補について(1)W/F/Cの区分、(2)Cなら塊の種類と『なぜひと塊で覚える価値があるか』の1文説明(40字以内)、"
            "(3)難易度(advanced/upper_intermediate/easy)を判定する。"
            "keep=trueにできるのは、区分がCで、難易度がeasyでなく、本文語義でのまとまりとして成立し、他の候補と意味・用法が重ならないものだけ。候補が不足してもkeepを甘くしない。\n"
            "keep=falseの候補のdisplay_form等は空文字でよい。keep=trueの候補のdisplay_form/gloss_ja/sense_note_ja/generalization_note_jaは次の規則で書く。\n\n"
            + GEN_RULES + "\n\n【候補】\n" + "\n".join(lines) + BODY + text)


def run_C2(case, *, m_rg="gpt-6.1-sol", eff="low", cands_override=None, tag="C2", verify_think=1024, do_verify=True, m_verify="gemini-3.8-flash", cap=7):
    text = case["text"]
    log = {"stages": [], "tag": tag}
    cands = cands_override if cands_override is not None else prod_p7_cands(case)
    cands = [dict(c, sentence=c.get("sentence") or "") for c in cands]
    o, m = L.call(m_rg, prompt_RG(text, cands), RG_SCHEMA, effort=eff, tag=f"{case['id']}:{tag}:RG")
    log["stages"].append({"stage": "RG", **{k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}})
    rankmap = {"advanced": 0, "upper_intermediate": 1, "easy": 2}
    log["judged"] = []
    kept = []
    for j in o["judgements"]:
        if not (1 <= j["id"] <= len(cands)):
            continue
        c = dict(cands[j["id"] - 1], **{k: j[k] for k in j if k != "id"})
        log["judged"].append({k: c.get(k) for k in ("span", "cls", "chunk_type", "difficulty", "keep", "chunk_reason_ja")})
        if j["keep"] and j["cls"] == "C" and j["difficulty"] != "easy" and j["display_form"].strip():
            kept.append(c)
    kept.sort(key=lambda c: rankmap[c["difficulty"]])
    kept = kept[:cap]
    vd = {}
    if do_verify and kept:
        o2, m = L.call(m_verify, prompt_B4(text, kept), B4_SCHEMA, tag=f"{case['id']}:{tag}:V", think_budget=verify_think)
        log["stages"].append({"stage": "verify", **{k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}})
        vd = {x["id"]: x for x in o2["verdicts"]}
    final = []
    for i, c in enumerate(kept, 1):
        v = vd.get(i, {})
        c["verify"] = v
        if v.get("verdict") == "REJECT":
            log.setdefault("verify_dropped", []).append({"span": c["span"], "issue": v.get("issue")})
            continue
        if v.get("verdict") == "FIX":
            if v.get("fix_display_form"):
                c["display_form_pre_fix"] = c["display_form"]
                c["display_form"] = v["fix_display_form"]
            if v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        c["display_form"] = V.strip_trailing_slot(c["display_form"])
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why})
            continue
        final.append(c)
    return {"items": [dict(source_span=c["span"], source_sentence=c["sentence"], display_form=c["display_form"], gloss_ja=c["gloss_ja"],
                           chunk_type=c["chunk_type"], chunk_reason_ja=c["chunk_reason_ja"], difficulty=c["difficulty"],
                           sense_note_ja=c["sense_note_ja"], generalization_note_ja=c["generalization_note_ja"], verify=c.get("verify"),
                           display_form_pre_fix=c.get("display_form_pre_fix")) for c in final], "log": log}


def _contains(a, b):
    ta, tb = V.toks(a), V.toks(b)
    n, m = len(ta), len(tb)
    return any(ta[i:i + m] == tb for i in range(n - m + 1)) or any(tb[i:i + n] == ta for i in range(m - n + 1))


def run_C3(case, *, m_rg="gpt-6-luna", eff=None, tag="C3", **kw):
    """C3: 既存P7候補 ∪ 過剰生成(luna, 最大14) を 1 call(区分判定+一般化) -> 検証。"""
    from kpg01_methods import prompt_B1, B1_SCHEMA
    text = case["text"]
    base = [dict(c, sentence=c.get("sentence") or "") for c in prod_p7_cands(case)]
    o, m = L.call("gpt-6-luna", prompt_B1(text), B1_SCHEMA, tag=f"{case['id']}:{tag}:B1")
    extra = [c for c in o["candidates"] if V.span_in_text(c["span"], text)]
    merged = list(base)
    for c in extra:
        if not any(_contains(c["span"], b["span"]) for b in merged):
            merged.append(c)
    r = run_C2(case, m_rg=m_rg, eff=eff, cands_override=merged, tag=tag, **kw)
    r["log"]["stages"].insert(0, {"stage": "B1_overgen", **{k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}})
    r["log"]["cands_total"] = len(merged)
    r["log"]["cands_added_by_overgen"] = [c["span"] for c in merged[len(base):]]
    return r
