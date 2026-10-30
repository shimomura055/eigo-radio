# -*- coding: utf-8 -*-
"""使い捨てtool(FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01 委任_03)。Family X ⑭(jwst_mystery_emission_line)のKey Phrase表現をユーザー指示どおり変更する。

ユーザー指示(HR回答原文 自由コメント。docs/pm/delegation_log/2026-10-30_FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01_USER_HR_01.md):
  Std : `narrow down the source` -> `narrow down` / `turn the usual steps around` -> `turn something around`
  Adv : `narrow down the source` -> `narrow down`
  (equivalent width の意味 -> 「等価幅」は既存CLI `er128 confirm-revise --gloss` で反映。本toolは表現変更のみ)
先例: FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 `apply_user_decision_surname_choice_02.py`(同じ requalify ゲート群を再利用)。本toolは確定前のため音声・解説は未生成。
汎用opではない: slug/run/候補ID/旧句/新句を固定定数にし、それ以外は拒否する。Production module(er119/er125/er128/er003)は編集しない(関数の呼出しのみ)。
ゲート: 決定論(出典文内の表層形・validate_canonicalization_item[Rule7のみ閉じた定数ペアに限り免除、記録]・CMU・記号・Human NG)
        + gloss再整合(LLM 1回/level) + QA 12項目再判定(LLM 1回/level、全PASS必須) + 候補全体Redundancy QA(LLM 1回/level)。
        1つでも不合格なら回避せず拒否(何も書かない)。
実行: .venv\\Scripts\\python.exe <本file> dry-run|apply --by <名> [--budget-jpy N]
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

TOOL_ID = "fx4c_revise_expression_jwst"
SLUG = "jwst_mystery_emission_line"
RUN_DIR = f"er019_output/family_x_audio_production_wiring_01/{SLUG}__run_fx4_01"
USER_REF = "docs/pm/delegation_log/2026-10-30_FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01_USER_HR_01.md"
USER_SPEC = "HR回答 自由コメント(⑭): narrow down the source->narrow down(Std/Adv)、turn the usual steps around->turn something around(Std)"
# level -> [(candidate_id, 旧句, 新句)]
CHANGES = {
    "a2": [("p_a72939f319", "narrow down the source", "narrow down"),
           ("p_a052ec5e7e", "turn the usual steps around", "turn something around")],
    "b1b": [("p_a72939f319", "narrow down the source", "narrow down")],
}
RULE7_MARK = "Rule7"


class ToolRefused(Exception):
    pass


def _sha_json(o) -> str:
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _cand(cands: dict, cid: str) -> dict:
    hits = [c for c in cands.get("candidates") or [] if c.get("candidate_id") == cid]
    if len(hits) != 1:
        raise ToolRefused(f"candidate_id={cid} が{len(hits)}件")
    return hits[0]


def deterministic(cand: dict, old: str, new: str, text: str, ng_entries: list) -> dict:
    import er003_key_words_canonicalization as kc
    import er003_v1_n3_01_scaffold_generate as sc
    import er105_kp_fulltext_selector_01 as ft
    import er108_kp_cmu_lexicon_gate_01 as cmu
    import er119_kp_human_review_01 as rv
    import er125_kp_rescue_production_01 as er125
    it = copy.deepcopy(cand["item"])
    if cand.get("used_form") != old or it.get("used_form") != old:
        raise ToolRefused(f"{cand['candidate_id']} の現在のused_formが{old!r}ではありません: {cand.get('used_form')!r}")
    role_ok = frozenset((it.get("person_role_repair") or {}).get("role_ok_poss") or [])
    span, display, sentence = it.get("source_span") or "", it.get("display_phrase") or "", it.get("source_sentence") or ""
    if span not in sentence and re.sub(r"\s+", " ", span) not in re.sub(r"\s+", " ", sentence):
        raise ToolRefused(f"source_span {span!r} が出典文にありません")
    it["key_phrase"], it["used_form"] = new, new
    ft._recompute_item_fields(it, display, new, role_ok)
    it["normalization_reason"] = it.get("normalization_reason") or "lemma_normalization"
    it["changed_from_display_phrase"] = True
    v = kc.validate_canonicalization_item(new, display, span, it.get("normalization_reason"), original_span=span,
                                          allow_inflection_normalization=True, role_ok_poss=role_ok)
    exemption = None
    if not v["ok"]:
        other = [r for r in v["reasons"] if RULE7_MARK not in r]
        if other or not v["reasons"]:
            raise ToolRefused("validate_canonicalization_item不合格(Rule7以外を含む=免除対象外): " + " / ".join(v["reasons"]))
        exemption = {"rule": "er003_key_words_canonicalization.validate_canonicalization_item Rule7", "reasons": v["reasons"], "pair": [old, new],
                     "candidate_id": cand["candidate_id"], "scope": "このtool内の閉じた定数ペアのみ。Production側の受理面は変更なし", "user_ref": USER_REF, "user_spec": USER_SPEC}
    chk = cmu.canonicalized_check([dict(it, rank=it.get("rank", 1))])
    if chk["bad"]:
        raise ToolRefused("CMU未登録語: " + str(chk["bad"]))
    findings = sc.detect_key_phrase_symbol_findings([dict(it, rank=it.get("rank", 1))])
    if any(sc.safety.symbol_gate_requires_stop([f]) for f in findings):
        raise ToolRefused("音声化禁止記号を含みます")
    probe = {"candidate_id": cand["candidate_id"], "selection_phrase": cand["selection_phrase"], "used_form": new}
    mt = rv.match_ng(probe, ng_entries)
    if mt == "exact":
        raise ToolRefused("Human NGと一致します")
    return {"item": it, "role_ok": role_ok, "exemption": exemption, "similar_to_ng": mt == "similar", "validate": v}


def llm_callables(article_id: str, theme_tag: str):
    import er003_key_words_canonicalization as kc
    import er003_key_words_gloss_alignment as ga
    import er003_v1_n3_01_scaffold_generate as sc
    import er005_cost_logger as cl
    import er006_model_routing_contract_01 as routing
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)

    def gloss_factory(msg):
        return ga.make_alignment_fn(msg, model=model)

    def qa_call(msg):
        with cl.logging_context(theme_tag, "kp_requalify_qa_rejudge"):
            res = kc.make_canonicalization_fn(msg, model=model, schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)()
        os.makedirs("er019_output/family_x_audio_production_wiring_01/_fx4c_qa_debug", exist_ok=True)
        with open(f"er019_output/family_x_audio_production_wiring_01/_fx4c_qa_debug/{article_id}_qa_{dt.datetime.now():%H%M%S}.json", "w", encoding="utf-8") as fh:
            json.dump({"msg": msg, "raw": res[0], "model_id": res[1], "response_id": res[2]}, fh, ensure_ascii=False, indent=1)
        return res
    return gloss_factory, qa_call, sc.run_key_phrase_redundancy_qa, "B1_SUPPORT", model


def revise_level(level: str, by: str, dry: bool, article_id: str) -> dict:
    import er119_kp_backfill_01 as bf
    import er105_kp_fulltext_selector_01 as ft
    import er119_kp_human_review_01 as rv
    import er125_kp_rescue_production_01 as er125
    import er128_kp_confirmed_content_01 as cc
    kp_dir = cc._kp_dir_for(RUN_DIR, level)
    review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
    rec = cc.load_record(kp_dir)
    if review is None or cands is None or rec is None or rec.get("state") != cc.STATE_LIVE:
        raise ToolRefused(f"{level}: 候補/review/liveの確定レコードがありません(先に8件のconfirmを完了してください)")
    ak = review.get("article_key") or {}
    if ak.get("slug") != SLUG:
        raise ToolRefused(f"対象外のslug: {ak}")
    live_ids = {i["candidate_id"]: i for i in rec["items"]}
    # 本文は候補docのtext_sha256と照合して読む(翻訳済み本文 = er019_output/<slug>/run_fx4_01/<level>/article.md)
    art = f"er019_output/{SLUG}/run_fx4_01/{level}/article.md"
    text = open(art, encoding="utf-8").read()
    if rv.sha256_text(text) != cands.get("text_sha256"):
        raise ToolRefused(f"{level}: 本文({art})のshaが候補docのtext_sha256と一致しません")
    ng_ent = rv.ng_entries_of(review, ak.get("family"), ak.get("slug"), level)
    out = {"level": level, "changes": []}
    new_items = {}
    for cid, old, new in CHANGES[level]:
        li = live_ids.get(cid)
        if li is None or li.get("used_form") != old:
            raise ToolRefused(f"{level}: 確定レコードの{cid}が想定({old!r})と一致しません: {li}")
        c = _cand(cands, cid)
        dg = deterministic(c, old, new, text, ng_ent)
        out["changes"].append({"candidate_id": cid, "from": old, "to": new, "exemption": dg["exemption"], "gates": "deterministic PASS" if dg["exemption"] is None else "deterministic PASS(Rule7のみ免除・記録)",
                               "span": dg["item"].get("source_span"), "display": dg["item"].get("display_phrase")})
        new_items[cid] = (c, dg, old, new)
    if dry:
        return out
    gloss_factory, qa_call, red_fn, process, model = llm_callables(article_id, SLUG)
    out["model"] = {"process": process, "model": model}
    items = []
    for cid, (c, dg, old, new) in new_items.items():
        it = dg["item"]
        it["rank"] = c["ai_rank"]
        items.append(it)
    ranks = [it["rank"] for it in items]
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        ga_res = er125.force_gloss_realign({"items": items}, ranks, text, gloss_factory, out_dir=os.path.join(kp_dir, "requalify_fx4c"), article_id=article_id)
        if ga_res["unresolved_ranks"]:
            raise ToolRefused(f"{level}: gloss整合が未解決(rank={ga_res['unresolved_ranks']})")
        merged = {m["rank"]: m for m in ga_res["merged"]["items"]}
        role_by_rank = {it["rank"]: dg_role for it, dg_role in ((new_items[cid][1]["item"], new_items[cid][1]["role_ok"]) for cid in new_items)}
        qres = er125.qa_rejudge(text, [merged[r] for r in ranks], qa_call, role_by_rank)
        doc = copy.deepcopy(cands)
        for cid, (c, dg, old, new) in new_items.items():
            rank = c["ai_rank"]
            item2 = merged[rank]
            q = qres["by_rank"].get(rank) or {"status": er125.QA_NOT_REJUDGED, "qa": {}}
            if q["status"] != er125.QA_REJUDGED_PASS or not q.get("qa") or any(v != "PASS" for v in q["qa"].values()):
                raise ToolRefused(f"{level} {new!r}: QA再判定がPASSではありません(status={q['status']}, FAIL={[k for k, v in (q.get('qa') or {}).items() if v != 'PASS']})。ユーザー決定の実現不能=Fableへ報告")
            item2["qa"], item2["qa_overall_status"] = dict(q["qa"]), "PASS"
            nc = copy.deepcopy(c)
            nc.update(used_form=new, japanese_gloss=item2.get("japanese_gloss"), word_count=ft.count_words(new), item=item2)
            nc["kind"] = bf.kind_of_phrase(new)
            nc["flags"] = dict(c.get("flags") or {}, qa_fail=False, gloss_hr_pending=False, similar_to_ng=bool(dg["similar_to_ng"]), redundant_with=[])
            nc["gates"] = dict(nc.get("gates") or {}, canonicalization="RESCUED_QA_REJUDGED_PASS", gloss="ALIGNED")
            rs = copy.deepcopy(c.get("rescue") or (c.get("item") or {}).get("rescue") or {})
            rs["gloss"] = {"status": er125.GLOSS_REALIGNED, "by": TOOL_ID}
            rs["qa"] = {"status": er125.QA_REJUDGED_PASS, "by": TOOL_ID, "model_id": qres.get("model_id")}
            rs["user_instruction"] = {"tool": TOOL_ID, "from": old, "to": new, "user_ref": USER_REF, "exemption": dg["exemption"]}
            nc["rescue"], item2["rescue"] = rs, copy.deepcopy(rs)
            nc["rescue_note"] = f"修正済み(元: {old}。ユーザー指示で `{new}`)・QA再判定済み"
            nc["auto_eligible"] = not nc["flags"]["similar_to_ng"]
            nc["requalified"] = {"tool": TOOL_ID, "from": old, "to": new, "user_ref": USER_REF, "user_spec": USER_SPEC, "by": by, "exemption": dg["exemption"],
                                 "old_item_sha256": _sha_json(c["item"]), "old_kind": c.get("kind"), "new_kind": nc["kind"], "old_gloss": c.get("japanese_gloss"),
                                 "display_phrase_kept": item2.get("display_phrase"), "source_span_kept": item2.get("source_span")}
            blockers = rv.presentation_blockers(nc)
            if blockers:
                raise ToolRefused(f"{level} {new!r}: 提示集合の条件を満たしません: " + " / ".join(b[1] for b in blockers))
            doc["candidates"] = [nc if x["candidate_id"] == cid else x for x in doc["candidates"]]
            out["changes"] = [dict(ch, gloss_after=nc["japanese_gloss"], gloss_before=c.get("japanese_gloss"), qa=nc["item"]["qa"], gloss_status=ga_res["status"]) if ch["candidate_id"] == cid else ch for ch in out["changes"]]
        ritems = []
        for c in doc["candidates"]:
            it = json.loads(json.dumps(c["item"]))
            it["rank"] = c["ai_rank"]
            ritems.append(it)
        rr = red_fn(text, ritems, os.path.join(kp_dir, "requalify_fx4c"), article_id, process=process)
        if rr.get("status") not in ("REDUNDANCY_PASS", "REDUNDANCY_NG"):
            raise ToolRefused(f"{level}: 候補全体Redundancy QAが判定不能({rr.get('status')})。何も書きません")
        old_red = {c["candidate_id"]: sorted((c.get("flags") or {}).get("redundant_with") or []) for c in cands["candidates"]}
        by_rank = {c["ai_rank"]: c for c in doc["candidates"]}
        for c in doc["candidates"]:
            c["flags"]["redundant_with"] = []
        for p in rr.get("duplicate_pairs") or []:
            a, b = by_rank.get(p.get("rank_a")), by_rank.get(p.get("rank_b"))
            if a and b:
                a["flags"]["redundant_with"].append(b["candidate_id"])
                b["flags"]["redundant_with"].append(a["candidate_id"])
        doc["redundancy_qa"] = {"status": rr.get("status"), "duplicate_pairs": rr.get("duplicate_pairs") or [], "model_id": rr.get("model_id")}
        out["redundancy_qa"] = doc["redundancy_qa"]
        out["redundant_with_changed"] = {c["candidate_id"]: {"old": old_red.get(c["candidate_id"]), "new": sorted(c["flags"]["redundant_with"])} for c in doc["candidates"]
                                         if old_red.get(c["candidate_id"]) != sorted(c["flags"]["redundant_with"])}
        doc["requalify_provenance"] = {"tool": TOOL_ID, "user_ref": USER_REF, "changes": [(cid, o, n) for cid, (_, _, o, n) in new_items.items()],
                                       "previous_candidates_sha256": cands["candidates_sha256"], "previous_redundancy_qa": cands.get("redundancy_qa"),
                                       "presentable_filter_version": rv.PRESENTABLE_FILTER_VERSION}
        # ---- 保存(cmd_revise と同形: 候補doc -> review候補sha -> 確定レコード版数+1[revised] -> 確定物退避 -> 再finalize)
        saved = rv.save_candidates(kp_dir, doc)
        review = rv.load_review(kp_dir)
        review["candidates_sha256"] = saved["candidates_sha256"]
        rv._event(review, "requalify_user_decision", by, {"changes": [(cid, o, n) for cid, (_, _, o, n) in new_items.items()], "user_ref": USER_REF, "user_spec": USER_SPEC,
                                                          "old_candidates_sha256": cands["candidates_sha256"]})
        review = rv.save_review(kp_dir, review, expected_revision=review["revision"])
        rv.invalidate_gloss_snapshot(kp_dir)
        sel = review["selection"]
        items2 = cc.build_items(saved, rv.sel_ids(sel, "kp"), rv.sel_ids(sel, "vocab") if rv.vocab_enabled(level, review) else [])
        new_rec = cc._new_record(kp_dir=kp_dir, review=review, cands=saved, items=items2, actor=(rec.get("confirmed_by") or {}).get("actor") or cc.ACTOR_USER,
                                 origin=dict(rec["origin"]), by=by, attestation="user_instruction_transcription", user_ref=USER_REF, comment=rec.get("comment") or "",
                                 unconsumed=copy.deepcopy(rec.get("unconsumed") or []), prev=rec, event="revised",
                                 reason=USER_SPEC, confirmation_id=rec["confirmation_id"])
        new_rec["history"][-1]["extra"] = {"expression_before": {cid: o for cid, (_, _, o, _) in new_items.items()}, "expression_after": {cid: n for cid, (_, _, _, n) in new_items.items()},
                                           "tool": TOOL_ID}
        new_rec["history"][-1]["entry_sha256"] = cc._entry_sha(new_rec["history"][-1])
        cc.save_record(kp_dir, new_rec)
        out["archived"] = cc._archive_final_outputs(kp_dir, "REVISE_SUPERSEDED")
    out["refinalized"] = cc._try_refinalize(kp_dir, level)
    out["record_revision"] = new_rec["revision"]
    out["candidates_sha256"] = saved["candidates_sha256"]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("dry-run", "apply"))
    ap.add_argument("--by", required=True)
    ap.add_argument("--levels", default="a2,b1b")
    ap.add_argument("--budget-jpy", type=float, default=3.0)
    a = ap.parse_args(argv)
    dry = a.cmd == "dry-run"
    report = {"tool": TOOL_ID, "cmd": a.cmd, "at": dt.datetime.now().isoformat(timespec="seconds"), "levels": {}}
    try:
        if not dry:
            from dotenv import load_dotenv
            load_dotenv()
            import er005_cost_logger as cl
            cl.install(f"{RUN_DIR}/raw_usage_log.jsonl")
        for lv in a.levels.split(","):
            report["levels"][lv] = revise_level(lv, a.by, dry, f"family_x_{SLUG}_{lv}")
        report["result"] = "DRY_RUN_OK(LLM 0・何も書いていません)" if dry else "APPLIED"
        print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
        return 0
    except ToolRefused as e:
        print(f"[{TOOL_ID}][REFUSED] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
