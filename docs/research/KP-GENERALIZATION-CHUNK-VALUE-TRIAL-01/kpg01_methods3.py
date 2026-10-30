# -*- coding: utf-8 -*-
"""Trial専用: 方式D(最終設計候補)= 候補源(既存P7 ± 過剰生成) -> 塊価値判定(選定) -> 構造化一般化(トークン分類) -> 別系列検証/修正 -> 決定論検査。
選定(B2)と一般化(G2)を別責務の別callにし、それぞれ独立に差し替え・検証できる。"""
import kpg01_llm as L
import kpg01_validate as V
import kpg01_gen2 as G
from kpg01_methods import prompt_B1, B1_SCHEMA, prompt_B2, B2_SCHEMA, prompt_B4, B4_SCHEMA, prod_p7_cands
from kpg01_methods2 import _contains


def _meta(m):
    return {k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}


def run_D(case, *, source="p7+overgen", m_sel="gpt-6-luna", eff_sel=None, m_gen="gpt-6-luna", eff_gen=None, m_verify="gemini-3.8-flash",
          verify_think=512, do_verify=True, tag="D", cap=7, wn_hints=True, cands_override=None, force_keep=False):
    text = case["text"]
    log = {"stages": [], "tag": tag}
    base = [dict(c, sentence=c.get("sentence") or "") for c in prod_p7_cands(case)] if (case.get("before") and "p7" in source) else []
    cands = list(base)
    if "overgen" in source:
        o, m = L.call("gpt-6-luna", prompt_B1(text), B1_SCHEMA, tag=f"{case['id']}:{tag}:B1")
        log["stages"].append({"stage": "B1_overgen", **_meta(m)})
        for c in o["candidates"]:
            if V.span_in_text(c["span"], text) and not any(_contains(c["span"], b["span"]) for b in cands):
                cands.append(c)
    if cands_override is not None:
        cands = cands_override
    # 本文中の文が欠けた候補(旧データ)は、spanを含む文を本文から補う
    for c in cands:
        if not c.get("sentence"):
            for sent in text.replace("\n", " ").split(". "):
                if V.span_in_text(c["span"], sent):
                    c["sentence"] = sent.strip()
                    break
    log["cands"] = [c["span"] for c in cands]
    log["cands_from_p7"] = [c["span"] for c in base]
    # --- 選定: 区分(W/F/C)・難易度・塊の理由 ---
    rankmap = {"advanced": 0, "upper_intermediate": 1, "easy": 2}
    if force_keep:   # 一般化段の単体評価用: 選定を行わず全候補をCとして一般化段へ(選定と一般化を独立に評価するため)
        kept = [dict(c, cls="C", chunk_type="n/a", chunk_reason_ja="(一般化段の単体評価。選定なし)", difficulty="upper_intermediate", keep=True) for c in cands]
        log["judged"] = []
    else:
        o, m = L.call(m_sel, prompt_B2(text, cands, wn_hints), B2_SCHEMA, effort=eff_sel, tag=f"{case['id']}:{tag}:SEL")
        log["stages"].append({"stage": "SEL", **_meta(m)})
        sel = []
        for j in o["judgements"]:
            if 1 <= j["id"] <= len(cands):
                c = dict(cands[j["id"] - 1])
                c.update(cls=j["cls"], chunk_type=j["chunk_type"], chunk_reason_ja=j["chunk_reason_ja"], difficulty=j["difficulty"], keep=j["keep"])
                sel.append(c)
        log["judged"] = [{k: c[k] for k in ("span", "cls", "chunk_type", "difficulty", "keep", "chunk_reason_ja")} for c in sel]
        kept = [c for c in sel if c["keep"] and c["cls"] == "C" and c["difficulty"] != "easy"]
        kept.sort(key=lambda c: rankmap[c["difficulty"]])
    kept = kept[:cap]
    if not kept:
        return {"items": [], "log": log}
    # --- 一般化: トークン分類 -> display_form(決定論組立) ---
    o, m = L.call(m_gen, G.prompt_G2(text, kept), G.G2_SCHEMA, effort=eff_gen, tag=f"{case['id']}:{tag}:GEN")
    log["stages"].append({"stage": "GEN", **_meta(m)})
    gm = {x["id"]: x for x in o["items"]}
    items = []
    for i, c in enumerate(kept, 1):
        x = gm.get(i)
        if not x:
            log.setdefault("gen_missing", []).append(c["span"])
            continue
        df, err = G.assemble(c["span"], x["tokens"])
        if df is None:
            log.setdefault("assemble_failed", []).append({"span": c["span"], "err": err})
            continue
        items.append(dict(c, display_form=df, gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], generalization_note_ja=x["note_ja"],
                          tokens=[(t["n"], t["label"], t["lemma"]) for t in x["tokens"]]))
    # --- 検証/修正(別系列) ---
    vd = {}
    if do_verify and items:
        o, m = L.call(m_verify, prompt_B4(text, items), B4_SCHEMA, tag=f"{case['id']}:{tag}:VER", think_budget=verify_think)
        log["stages"].append({"stage": "VERIFY", **_meta(m)})
        vd = {x["id"]: x for x in o["verdicts"]}
    final = []
    for i, c in enumerate(items, 1):
        v = vd.get(i, {})
        c["verify"] = v
        if v.get("verdict") == "REJECT":
            log.setdefault("verify_dropped", []).append({"span": c["span"], "issue": v.get("issue")})
            continue
        if v.get("verdict") == "FIX":
            fx = V.strip_trailing_slot((v.get("fix_display_form") or "").replace(" / ", " ").strip())
            if fx:
                okf, whyf = V.display_check(fx, c["span"])
                if okf:
                    c["display_form_pre_fix"] = c["display_form"]
                    c["display_form"] = fx
                else:
                    log.setdefault("fix_rejected_by_validator", []).append({"span": c["span"], "fix": fx, "why": whyf})
            if v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why})
            continue
        final.append(c)
    return {"items": [dict(source_span=c["span"], source_sentence=c["sentence"], display_form=c["display_form"], gloss_ja=c["gloss_ja"],
                           chunk_type=c["chunk_type"], chunk_reason_ja=c["chunk_reason_ja"], difficulty=c["difficulty"],
                           sense_note_ja=c["sense_note_ja"], generalization_note_ja=c["generalization_note_ja"], verify=c.get("verify"),
                           display_form_pre_fix=c.get("display_form_pre_fix"), tokens=c.get("tokens")) for c in final], "log": log}
