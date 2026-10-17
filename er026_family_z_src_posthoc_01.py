# -*- coding: utf-8 -*-
"""Family Z Source Reference Contract (SRC) 正式方式 D1「z_sentence_id_posthoc_v1」
(FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_16、ユーザー2026-10-17 #109 APPROVED_FOR_PRODUCTION)。

方式: Strategy L(shortlistなし全文選定)で選ばれたKP itemへ、Pythonが元英文(level本文)との照合で
文ID(S1..Sn)・source_span・source_sentenceを決定論的に事後付与する。
- 一意に解決できた場合のみ採用する(exact / unique_containment / unique_span)。
- 曖昧(複数一致)・不一致(0一致)は推測で補完せず FamilyZSourceReferenceStop(=STOP)。
- KP選定Prompt・優先順位・候補供給方式、既存Source Consistency Gate・canonicalization・gloss再整合には一切触れない
  (本Gateはそれらが全て終わった後の、install_kp_assets前の決定論的な出典付与/検証のみ)。
- 引用符内で文が分割される場合は、spanを含む1文のみを採用し quote_boundary_truncated をtelemetryに記録する(Fable決定F3)。
- Family X候補ID方式(M2P0/candidate_id_v1)は導入しない。

Trial/DEV専用経路ではない。正式runner(er026_family_z_fiction_production_runner_01.stage_kp)がimportして
ensure_stage(kp_<lv>)成功後・install_kp_assets前に呼ぶ(初回・再利用・--regenerate-stage・外側retry後・resume共通)。
冪等: 既にラベル付与済みのartifactを再適用しても同一内容になる(元のLLM source_sentenceは source_sentence_llm に保持)。
API呼出 0・LLM 0。"""
from __future__ import annotations

import json
import os
import re

import er003_key_words_min_unit as p2g
import er030_key_phrase_db_hybrid_core_01 as core

LABEL = "z_sentence_id_posthoc_v1"
AUDIT_REL = "audit/src_z_posthoc_01.json"
RESOLVED_METHODS = ("exact", "unique_containment", "unique_span")
_N = p2g._normalize_for_match


class FamilyZSourceReferenceStop(RuntimeError):
    """曖昧・不一致で出典を一意に特定できない(推測補完しない)。runner側でFamilyZE2EStopへ変換される。"""


def build_units(article_text: str) -> list:
    """level本文(canonical_article_text)を文S1..Snに分割(Family X Production使用中の既存関数を再利用)。"""
    return core.build_sentence_units(article_text)


def resolve_item(units: list, item: dict):
    """returns (method, [sentence_ids]) ; method in exact|unique_containment|unique_span|ambiguous|unresolved.
    (i)正規化完全一致 (ii)唯一の包含(文がLLM source_sentenceに含まれ、かつspanを含む) (iii)spanを含む文が唯一。"""
    ss = _N(item.get("source_sentence_llm") or item.get("source_sentence") or "")
    span = _N(item.get("source_span") or item.get("used_form") or "")
    norm_units = [(f"S{i + 1}", _N(u["raw_text"])) for i, u in enumerate(units)]
    _s = lambda t: t.strip(" .!?\"'")   # 終端句読点・外側の引用符はbuild_sentence_unitsが落とすため比較から除く
    exact = [sid for sid, t in norm_units if ss and _s(t) == _s(ss)]
    if len(exact) == 1:
        return "exact", exact
    if len(exact) > 1:
        return "ambiguous", exact
    cont = [sid for sid, t in norm_units if t and ss and t in ss and span and span in t]
    if len(cont) == 1:
        return "unique_containment", cont
    if len(cont) > 1:
        return "ambiguous", cont
    byspan = [sid for sid, t in norm_units if span and span in t]
    if len(byspan) == 1:
        return "unique_span", byspan
    if len(byspan) > 1:
        return "ambiguous", byspan
    return "unresolved", []


def _alnum(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _N(t))


def _body_norm(article_text: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKC", article_text)
    return t.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))


def _starts_inside_open_quote(units: list, article_text: str) -> dict:
    """各unit(S#)が、先行する引用符が開いたまま始まるか(引用符内で文が分割された後続文か)を順走査で判定。
    判定不能(本文中にunitが見つからない)はNone。"""
    body = _body_norm(article_text)
    cursor, out = 0, {}
    for i, u in enumerate(units):
        raw = u["raw_text"]
        idx = body.find(raw, cursor)
        sid = f"S{i + 1}"
        if idx < 0:
            out[sid] = None
            continue
        before = body[:idx]
        inside = before.count('"') % 2 == 1
        if idx > 0 and body[idx - 1] == '"' and body[:idx - 1].count('"') % 2 == 0:
            inside = False   # 直前の引用符はこの文自身の開き引用符
        out[sid] = inside
        cursor = idx + len(raw)
    return out


def apply_to_kp(kp: dict, article_text: str, level: str = "") -> dict:
    """KP artifact(dict)へ事後付与する純関数。曖昧/不一致があれば付与せず報告のみ返す(mutateしない)。
    returns report {label, level, status: PASS|STOP, items:[...], ambiguous:[rank], unresolved:[rank], quote_boundary_truncated_count, new_items}"""
    units = build_units(article_text)
    open_q = _starts_inside_open_quote(units, article_text)
    sentence_ref = {f"S{i + 1}": u["raw_text"] for i, u in enumerate(units)}
    recs, new_items, amb, unr = [], [], [], []
    for it in sorted(kp.get("items", []), key=lambda x: x["rank"]):
        method, sids = resolve_item(units, it)
        llm_sentence = it.get("source_sentence_llm") or it.get("source_sentence") or ""
        rec = {"rank": it["rank"], "used_form": it.get("used_form"), "source_span": it.get("source_span"),
               "llm_source_sentence": llm_sentence, "resolution_method": method, "candidate_sentence_ids": sids}
        if method in RESOLVED_METHODS:
            sid = sids[0]
            sent = sentence_ref[sid]
            span = it.get("source_span") or it.get("used_form") or ""
            if _N(span) not in _N(sent):
                # 到達不能のはず(解決条件がspan包含を要求)だが、防御としてSTOP扱い(推測補完しない)
                rec["resolution_method"] = "unresolved"
                unr.append(it["rank"])
                recs.append(rec)
                continue
            extends = bool(_alnum(llm_sentence)) and _alnum(sent) != _alnum(llm_sentence) and _alnum(sent) in _alnum(llm_sentence)
            llm_has_quote = '"' in _body_norm(llm_sentence)
            qsig = {"starts_inside_open_quote": open_q.get(sid), "llm_sentence_extends_beyond_unit_with_quote": bool(extends and llm_has_quote)}
            truncated = bool(qsig["starts_inside_open_quote"]) or qsig["llm_sentence_extends_beyond_unit_with_quote"]
            rec.update(source_sentence_id=sid, source_sentence=sent, quote_boundary_truncated=truncated, quote_signals=qsig,
                       llm_sentence_extends_beyond_adopted_unit=bool(extends))
            new = dict(it)
            new["source_sentence_llm"] = llm_sentence
            new["source_sentence_id"] = sid
            new["source_sentence"] = sent
            new["resolution_method"] = method
            new["quote_boundary_truncated"] = truncated
            new["source_reference_contract"] = LABEL
            new_items.append(new)
        elif method == "ambiguous":
            amb.append(it["rank"])
        else:
            unr.append(it["rank"])
        recs.append(rec)
    status = "PASS" if not amb and not unr and len(new_items) == len(kp.get("items", [])) else "STOP"
    return {"label": LABEL, "level": level, "status": status, "sentence_units": len(units), "items": recs,
            "ambiguous": amb, "unresolved": unr,
            "quote_boundary_truncated_count": sum(1 for r in recs if r.get("quote_boundary_truncated")),
            "new_items": new_items}


def _merge_audit(audit_path: str, level: str, report: dict) -> None:
    doc = {"label": LABEL, "levels": {}}
    if os.path.exists(audit_path):
        try:
            with open(audit_path, encoding="utf-8") as f:
                doc = json.load(f)
        except (OSError, ValueError):
            doc = {"label": LABEL, "levels": {}}
    lv = {k: v for k, v in report.items() if k != "new_items"}
    doc.setdefault("levels", {})[level] = lv
    os.makedirs(os.path.dirname(os.path.abspath(audit_path)), exist_ok=True)
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)


def gate(kp_json_path: str, article_text: str, level: str, out_dir: str) -> dict:
    """正式Gate。kp_json_path(keywords_canonicalized.json)へ文ID/source_sentence/span/方式/telemetryを決定論的に記録し、
    auditを書く。曖昧・不一致は artifact を変更せず audit(STOP)を書いて FamilyZSourceReferenceStop。
    既存のSource Consistency Gate/canonicalizationの判定には触れない(呼出順序・判定不変)。"""
    audit_path = os.path.join(out_dir, AUDIT_REL)
    with open(kp_json_path, encoding="utf-8") as f:
        kp = json.load(f)
    report = apply_to_kp(kp, article_text, level)
    _merge_audit(audit_path, level, report)
    if report["status"] != "PASS":
        raise FamilyZSourceReferenceStop(
            f"FAMILY_Z_SRC_UNRESOLVED({level}): ambiguous_ranks={report['ambiguous']} unresolved_ranks={report['unresolved']} "
            f"(出典を一意に特定できない。推測補完せずSTOP。audit={audit_path}。KP再選定は--regenerate-stage kp_{level})")
    new_kp = dict(kp)
    new_kp["items"] = report["new_items"]
    new_kp["source_reference_contract"] = LABEL
    old_s = json.dumps(kp, ensure_ascii=False, indent=2)
    new_s = json.dumps(new_kp, ensure_ascii=False, indent=2)
    if old_s != new_s:
        with open(kp_json_path, "w", encoding="utf-8") as f:
            f.write(new_s)
    return {k: v for k, v in report.items() if k != "new_items"}


def has_contract(kp: dict) -> bool:
    """下流(TTS/Gate/Assembly共有入力)がSRC未適用のKP成果物を通さないための確認。"""
    items = kp.get("items") or []
    return bool(items) and all(it.get("source_reference_contract") == LABEL and it.get("source_sentence_id") for it in items)
