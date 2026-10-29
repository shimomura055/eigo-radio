# -*- coding: utf-8 -*-
"""使い捨てtool C(FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 委任_05。由来=ユーザー原文USER_03 §2)。

目的: Family Y「夫が妻の姓を選ぶとき」Advanced(b1b)の学習表現(Part 1の第3項目。確定区分=②追加解説)`hold one's son back` を一般形 `hold someone back` へ変更する。
本文の原表現 `hold my son back`(出典文S35)は不変(display_phrase/source_span=`hold my son back`のまま。見出し・意味・解説だけ一般形に整合)。
**汎用opではない**: slug=surname_choice / run_02 / level=b1b / candidate_id=p_bb5820f386 / 旧句`hold one's son back` / 新句`hold someone back` に固定(任意文字列・他記事・他levelは拒否)。
注: この項目は音声化されるKey Phrase(①、3件=take offense/let go of/adopted)ではなく②追加解説。よってKP音声・KP英語解説は再生成しない(入力が変わらない=runnerの来歴で確認)。

免除は1点だけ(tool B[take offense]と同様): kc.validate_canonicalization_item の Rule7(人称代名詞の1対1置換でも連続部分文字列でもない別の辞書形を生成しない)が
`my son`->`someone`(目的語の不定代名詞化)を拒否する場合に限り、**このtool内の閉じた定数ペア(p_bb5820f386, hold one's son back -> hold someone back)**を
ユーザー原文USER_03 §2を根拠に免除し、候補item・確定レコードのorigin.transcriptionに記録する(Production側へ汎用免除を足さない=編集0)。
他の全ゲート(CMU・記号検出・Human NG・gloss再整合・QA 12項目[全PASS必須]・候補全体Redundancy QA・presentation_blockers)は再適用する。不合格は回避せず拒否(Fableへ報告)。

段階: revoke -> requalify(LLMゲート) -> confirm(attestation=user_instruction_transcription) -> 再finalize・assets install・kp_b1b来歴付替え -> 部分再生成(kp_part1_b1bの当該rowのみ)
-> part2_b1b再finalize(LLM 0) -> 事後検査。--dry-run=LLM 0・書込み0。失敗時は退避から全復元(cost_logは追記のみ=戻さない)。
実行: .venv\\Scripts\\python.exe docs\\research\\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\\tools\\apply_user_decision_surname_choice_03.py apply|dry-run --by <名> [--rehearsal-dir <root>] --budget-jpy <円>
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import apply_user_decision_surname_choice_02 as T2  # noqa: E402  (Spend/build_real_ctx/llm_callables/diff_payloads/part2_ready_checkを共有)
import apply_v1_intro_patch_01 as A  # noqa: E402

ROOT = A.ROOT
TOOL_ID = "apply_user_decision_surname_choice_03"
LOCKED_SLUG, LOCKED_RUN, LOCKED_LEVEL = "surname_choice", "run_02", "b1b"
CAND_ID = "p_bb5820f386"
OLD_FORM, NEW_FORM = "hold one's son back", "hold someone back"
SURFACE = "hold my son back"                       # 本文の原表現(display_phrase/source_span/selection_phrase。不変)
USER_REF = "docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER_03.md"
USER_REF_SHA256 = "30fd4011ca6d6f7a131025e5497f03c7f2193ea132c8c59982ac2da3cbffd5ab"
USER_SPEC = "§2 Advanced学習表現の修正(`hold one's son back` -> `hold someone back`。本文の原表現は不変、見出し・意味・解説を一般形に整合)"
ATTESTATION = "user_instruction_transcription"
SOURCE_PAYLOAD_REL = "key_phrases/b1b/confirmed_selection_source/rev4_payload.json"      # 変更前の確定(rev4=take offense反映済み)の原本フォーム送信
SOURCE_PAYLOAD_SHA256 = "bb809e8b4dfc9ce907c04ec39134ded358fd7e368e95261577fe0c77f4e5615e"
RULE7_MARK = "Rule7"
MUTABLE_SUBTREES = T2.MUTABLE_SUBTREES
MUTABLE_FILES = T2.MUTABLE_FILES
REGEN_SEQUENCE = ("kp_part1_b1b", "part2_b1b")     # part2_b1b=確定文法の再書込み(cmd_from_form)で凍結ファイルが退避されるため再finalize(LLM 0)


class ToolRefused(Exception):
    pass


A.ToolRefused = ToolRefused
T2.ToolRefused = ToolRefused


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha_json(o) -> str:
    return _sha_bytes(json.dumps(o, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def find_cand(cands: dict, *, expect_form: str) -> dict:
    hits = [c for c in cands.get("candidates") or [] if c.get("candidate_id") == CAND_ID]
    if len(hits) != 1:
        raise ToolRefused(f"candidate_id={CAND_ID} が{len(hits)}件です(1件のみ許可)")
    c = hits[0]
    if c.get("used_form") != expect_form or (c.get("item") or {}).get("used_form") != expect_form:
        raise ToolRefused(f"候補{CAND_ID}の現在のused_formが{expect_form!r}ではありません: {c.get('used_form')!r}")
    return c


def check_preconditions(kp_dir: str, stage: str) -> dict:
    import er119_kp_human_review_01 as rv
    cc = rv._cc()
    review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
    if review is None or cands is None:
        raise ToolRefused("候補/reviewがありません")
    ak = review.get("article_key") or {}
    if (ak.get("slug"), (ak.get("family") or "").lower(), review.get("level")) != (LOCKED_SLUG, "y", LOCKED_LEVEL):
        raise ToolRefused(f"対象外のrunです(固定: slug={LOCKED_SLUG}, family=y, level={LOCKED_LEVEL}。実際: {ak}, level={review.get('level')})")
    if review["status"] != rv.ST_REVIEWED:
        raise ToolRefused(f"review.status={review['status']}(REVIEWEDのみ対象)")
    if review["candidates_sha256"] != cands["candidates_sha256"]:
        raise ToolRefused("reviewと候補docのcandidates_sha256が不一致")
    rec = cc.load_record(kp_dir)
    if rec is None:
        raise ToolRefused("確定レコードがありません")
    live = cc.live_user_record(kp_dir)
    if stage == "pre_revoke":
        if live is None:
            raise ToolRefused("ユーザー確定(live)がありません(既に取消済み/適用済みの可能性)")
        it1 = [i for i in live["items"] if i["candidate_id"] == CAND_ID]
        if len(it1) != 1 or it1[0]["used_form"] != OLD_FORM or it1[0].get("slot") != "vocab" or it1[0].get("category") != 2:
            raise ToolRefused(f"確定レコードの{CAND_ID}が想定(vocab slot, category 2, used_form={OLD_FORM!r})と一致しません: {it1}")
        find_cand(cands, expect_form=OLD_FORM)
    else:
        if live is not None:
            raise ToolRefused("まだliveの確定レコードがあります(先にrevoke)")
        find_cand(cands, expect_form=OLD_FORM)
    return {"review": review, "cands": cands, "rec": rec}


def deterministic_gates(cand: dict, text: str, ng_entries: list) -> dict:
    import er003_key_words_canonicalization as kc
    import er003_v1_n3_01_scaffold_generate as sc
    import er105_kp_fulltext_selector_01 as ft
    import er108_kp_cmu_lexicon_gate_01 as cmu
    import er119_kp_human_review_01 as rv
    it = copy.deepcopy(cand["item"])
    role_ok = frozenset((it.get("person_role_repair") or {}).get("role_ok_poss") or [])
    span, display, sentence = it.get("source_span") or "", it.get("display_phrase") or "", it.get("source_sentence") or ""
    if cand.get("candidate_id") != CAND_ID or display != SURFACE or span != SURFACE or cand.get("selection_phrase") != SURFACE:
        raise ToolRefused(f"固定条件(候補{CAND_ID}, display/source_span/selection_phrase={SURFACE!r})と一致しません")
    if SURFACE not in sentence or SURFACE not in text:
        raise ToolRefused(f"本文の原表現{SURFACE!r}が出典文/本文に連続して存在しません(本文は変更しない)")
    it["key_phrase"], it["used_form"] = NEW_FORM, NEW_FORM
    ft._recompute_item_fields(it, display, NEW_FORM, role_ok)
    it["changed_from_display_phrase"] = True
    v = kc.validate_canonicalization_item(NEW_FORM, display, span, it.get("normalization_reason"), original_span=span,
                                          allow_inflection_normalization=True, role_ok_poss=role_ok)
    exemption = None
    if not v["ok"]:
        other = [r for r in v["reasons"] if RULE7_MARK not in r]
        if other or not v["reasons"]:
            raise ToolRefused("validate_canonicalization_item不合格(Rule7以外の理由を含む=免除対象外): " + " / ".join(v["reasons"]))
        exemption = {"rule": "er003_key_words_canonicalization.validate_canonicalization_item Rule7", "reasons": v["reasons"], "pair": [OLD_FORM, NEW_FORM],
                     "candidate_id": CAND_ID, "scope": "このtool内の閉じた定数ペア1点のみ。Production側の受理面は変更なし", "user_ref": USER_REF, "user_spec": USER_SPEC}
    chk = cmu.canonicalized_check([dict(it, rank=it.get("rank", 1))])
    if chk["bad"]:
        raise ToolRefused("CMU未登録語: " + str(chk["bad"]))
    findings = sc.detect_key_phrase_symbol_findings([dict(it, rank=it.get("rank", 1))])
    if any(sc.safety.symbol_gate_requires_stop([f]) for f in findings):
        raise ToolRefused("音声化禁止記号を含みます")
    probe = {"candidate_id": cand["candidate_id"], "selection_phrase": cand["selection_phrase"], "used_form": NEW_FORM}
    mt = rv.match_ng(probe, ng_entries)
    if mt == "exact":
        raise ToolRefused("Human NGと一致します")
    return {"item": it, "role_ok": role_ok, "exemption": exemption, "similar_to_ng": mt == "similar", "validate": v}


ALLOWED_DIFFS = re.compile(r"^(/article/candidates_sha256|/article/text_sha256|/selection/extra_explanation\[0\]/(term|ja_gloss))$")


def patched_payload(source: dict, cands_after: Optional[dict], *, text_sha: str, new_gloss: str) -> dict:
    out = copy.deepcopy(source)
    n = 0
    for grp in ("key_phrase", "extra_explanation", "meaning_display"):
        for rec in out["selection"][grp]:
            if rec["candidate_id"] == CAND_ID:
                if rec["term"] != OLD_FORM or rec.get("selection_phrase") != SURFACE:
                    raise ToolRefused(f"原本payloadの{CAND_ID}が想定外です: {rec}")
                rec["term"] = NEW_FORM
                rec["ja_gloss"] = new_gloss
                n += 1
    if n != 1:
        raise ToolRefused(f"原本payload内の対象項目が{n}件です(1件のみ許可)")
    if cands_after is not None:
        out["article"]["candidates_sha256"] = cands_after["candidates_sha256"]
    out["article"]["text_sha256"] = text_sha
    return out


def requalify(kp_dir: str, *, by: str, text: str, gloss_factory, qa_call_fn, redundancy_fn, article_id: str, process: str, out_dir: str) -> dict:
    import er125_kp_rescue_production_01 as er125
    import er105_kp_fulltext_selector_01 as ft
    import er119_kp_backfill_01 as bf
    import er119_kp_human_review_01 as rv
    pre = check_preconditions(kp_dir, "post_revoke")
    review, cands = pre["review"], pre["cands"]
    cand = find_cand(cands, expect_form=OLD_FORM)
    ak = review.get("article_key") or {}
    ng_ent = rv.ng_entries_of(review, ak.get("family"), ak.get("slug"), review["level"])
    dg = deterministic_gates(cand, text, ng_ent)
    report = {"candidate_id": CAND_ID, "from": OLD_FORM, "to": NEW_FORM, "gates": {"preconditions": "PASS", "surface_in_text": "PASS", "cmu": "PASS", "symbol": "PASS", "human_ng": "PASS"},
              "exemption": dg["exemption"]}
    report["gates"]["validate_canonicalization_item"] = "PASS" if dg["exemption"] is None else "EXEMPT(Rule7のみ・閉じた定数ペア)"
    os.makedirs(out_dir, exist_ok=True)
    item2, role_ok, rank = dg["item"], dg["role_ok"], dg["item"].get("rank", cand["ai_rank"])
    ga_res = er125.force_gloss_realign({"items": [item2]}, [rank], text, gloss_factory, out_dir=out_dir, article_id=article_id)
    if ga_res["unresolved_ranks"]:
        raise ToolRefused(f"gloss整合が未解決(rank={ga_res['unresolved_ranks']})。ユーザー意図と不一致の可能性=Fableへ報告")
    item2 = ga_res["merged"]["items"][0]
    report["gates"]["gloss_realign"] = ga_res["status"]
    report["gloss_after"] = item2.get("japanese_gloss")
    qres = er125.qa_rejudge(text, [item2], qa_call_fn, {rank: role_ok})
    report["qa_model_id"], report["qa_response_id"] = qres.get("model_id"), qres.get("response_id")
    q = qres["by_rank"].get(rank) or {"status": er125.QA_NOT_REJUDGED, "qa": {}}
    report["gates"]["qa_rejudge"] = q["status"]
    report["qa_fields"] = q.get("qa")
    if q["status"] != er125.QA_REJUDGED_PASS or any(v != "PASS" for v in (q.get("qa") or {}).values()) or not q.get("qa"):
        raise ToolRefused(f"QA再判定がPASSではありません(status={q['status']}, FAIL項目={[k for k, v in (q.get('qa') or {}).items() if v != 'PASS']})。"
                          "`hold someone back`は提示可能な候補にできません=ユーザー決定の実現不能。回避せずFableへ報告")
    item2["qa"], item2["qa_overall_status"] = dict(q["qa"]), "PASS"
    new = copy.deepcopy(cand)
    new.update(used_form=NEW_FORM, japanese_gloss=item2.get("japanese_gloss"), word_count=ft.count_words(NEW_FORM), item=item2)
    new["kind"] = bf.kind_of_phrase(NEW_FORM)
    new["flags"] = dict(cand.get("flags") or {}, qa_fail=False, gloss_hr_pending=False, similar_to_ng=bool(dg["similar_to_ng"]), redundant_with=[])
    new["gates"] = dict(new.get("gates") or {}, canonicalization="USER_INSTRUCTED_QA_REJUDGED_PASS", gloss="ALIGNED")
    rs = copy.deepcopy(cand.get("rescue") or (cand.get("item") or {}).get("rescue") or {})
    rs.setdefault("schema", "kp_rescue_v1")
    rs["gloss"] = {"status": er125.GLOSS_REALIGNED, "by": TOOL_ID}
    rs["qa"] = {"status": er125.QA_REJUDGED_PASS, "by": TOOL_ID, "model_id": report.get("qa_model_id")}
    rs["user_instruction"] = {"tool": TOOL_ID, "from": OLD_FORM, "to": NEW_FORM, "user_ref": USER_REF, "exemption": dg["exemption"]}
    new["rescue"], item2["rescue"] = rs, copy.deepcopy(rs)
    new["rescue_note"] = f"ユーザー指示USER_03 §2で `{OLD_FORM}` -> `{NEW_FORM}`(gloss再整合・QA再判定済み)"
    new["auto_eligible"] = not new["flags"]["similar_to_ng"]
    new["requalified"] = {"tool": TOOL_ID, "from": OLD_FORM, "to": NEW_FORM, "user_ref": USER_REF, "user_ref_sha256": USER_REF_SHA256, "user_spec": USER_SPEC, "by": by,
                          "exemption": dg["exemption"], "old_item_sha256": _sha_json(cand["item"]), "old_kind": cand.get("kind"), "new_kind": new["kind"],
                          "old_gloss": cand.get("japanese_gloss"), "display_phrase_kept": item2.get("display_phrase"), "source_span_kept": item2.get("source_span")}
    if item2.get("display_phrase") != SURFACE or item2.get("source_span") != SURFACE or new["item"].get("used_form") != NEW_FORM or new["item"].get("key_phrase") != NEW_FORM:
        raise ToolRefused("差替え後itemのdisplay/source_span/used_form/key_phraseが想定と異なります")
    blockers = rv.presentation_blockers(new)
    if blockers:
        raise ToolRefused("差替え後の候補が提示集合の条件を満たしません: " + " / ".join(b[1] for b in blockers))
    doc = copy.deepcopy(cands)
    doc["candidates"] = [new if c["candidate_id"] == CAND_ID else c for c in doc["candidates"]]
    old_red = {c["candidate_id"]: list((c.get("flags") or {}).get("redundant_with") or []) for c in cands["candidates"]}
    ritems = []
    for c in doc["candidates"]:
        it = json.loads(json.dumps(c["item"]))
        it["rank"] = c["ai_rank"]
        ritems.append(it)
    rr = redundancy_fn(text, ritems, out_dir, article_id, process=process)
    if rr.get("status") not in ("REDUNDANCY_PASS", "REDUNDANCY_NG"):
        raise ToolRefused(f"候補全体Redundancy QAが判定不能です(status={rr.get('status')})。何も書きません(判定器の故障)")
    by_rank = {c["ai_rank"]: c for c in doc["candidates"]}
    for c in doc["candidates"]:
        c["flags"]["redundant_with"] = []
    for p in rr.get("duplicate_pairs") or []:
        a, b = by_rank.get(p.get("rank_a")), by_rank.get(p.get("rank_b"))
        if a and b:
            a["flags"]["redundant_with"].append(b["candidate_id"])
            b["flags"]["redundant_with"].append(a["candidate_id"])
    doc["redundancy_qa"] = {"status": rr.get("status"), "duplicate_pairs": rr.get("duplicate_pairs") or [], "model_id": rr.get("model_id")}
    new_red = {c["candidate_id"]: list(c["flags"]["redundant_with"]) for c in doc["candidates"]}
    report["redundant_with_changed"] = {k: {"old": old_red.get(k), "new": new_red[k]} for k in new_red if sorted(old_red.get(k) or []) != sorted(new_red[k])}
    doc["requalify_provenance"] = {"tool": TOOL_ID, "user_ref": USER_REF, "candidate_id": CAND_ID, "from": OLD_FORM, "to": NEW_FORM,
                                   "previous_candidates_sha256": cands["candidates_sha256"], "previous_redundancy_qa": cands.get("redundancy_qa"),
                                   "presentable_filter_version": rv.PRESENTABLE_FILTER_VERSION}
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        review = rv.load_review(kp_dir)
        if review["status"] != rv.ST_REVIEWED or review["candidates_sha256"] != cands["candidates_sha256"]:
            raise ToolRefused("実行中にreview/候補が変更されました(再実行してください)")
        saved = rv.save_candidates(kp_dir, doc)
        review["candidates_sha256"] = saved["candidates_sha256"]
        review["last_human_op_at"] = rv._now()
        rv._event(review, "requalify_user_decision", by, {"candidate_id": CAND_ID, "from": OLD_FORM, "to": NEW_FORM, "user_ref": USER_REF, "user_spec": USER_SPEC,
                                                         "old_candidates_sha256": cands["candidates_sha256"], "exemption": dg["exemption"]})
        rv.save_review(kp_dir, review, expected_revision=review["revision"])
        rv.invalidate_gloss_snapshot(kp_dir)
    report.update(candidates_sha256=saved["candidates_sha256"], new_kind=new["kind"], new_gloss=new["japanese_gloss"], applied=True)
    return report


def confirm(run_dir: str, kp_dir: str, *, by: str, dry_run: bool = False, new_gloss: Optional[str] = None) -> dict:
    import er119_kp_human_review_01 as rv
    import er128_form_readable_restore_01 as fr
    cc = rv._cc()
    sp = os.path.join(kp_dir, "confirmed_selection_source", "rev4_payload.json")
    raw = open(sp, "rb").read()
    if _sha_bytes(raw) != SOURCE_PAYLOAD_SHA256:
        raise ToolRefused("原本payload(rev4_payload.json)のfile shaが定数と一致しません")
    source = json.loads(raw.decode("utf-8"))
    cands = rv.load_candidates(kp_dir)
    gloss = new_gloss or find_cand(cands, expect_form=NEW_FORM).get("japanese_gloss")
    payload = patched_payload(source, cands, text_sha=cands["text_sha256"], new_gloss=gloss)
    d_all = T2.diff_payloads(source, payload)
    extra = [d for d in d_all if not ALLOWED_DIFFS.match(d)]
    if extra:
        raise ToolRefused("差替え対象以外の差分が検出されました(他の選定を変えない): " + str(extra))
    prov = {"tool": TOOL_ID, "source_payload": {"path": SOURCE_PAYLOAD_REL, "sha256": SOURCE_PAYLOAD_SHA256}, "differences": d_all, "user_ref": USER_REF,
            "user_ref_sha256": USER_REF_SHA256, "user_spec": USER_SPEC, "form_data_regenerated": False, "cap_recomputed": False,
            "new_candidates_sha256": cands["candidates_sha256"], "exemption": (find_cand(cands, expect_form=NEW_FORM).get("requalified") or {}).get("exemption")}
    if dry_run:
        return {"dry_run": True, "differences": d_all, "provenance": prov}
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="user_decision_payload_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(fr.payload_bytes(payload))
        res = cc.cmd_from_form(run_dir, LOCKED_LEVEL, tmp, by, USER_REF, actor=cc.ACTOR_USER, attestation=ATTESTATION, origin_extra=prov)
    finally:
        with contextlib.suppress(OSError):
            os.remove(tmp)
    return {"confirmed": res, "provenance": prov}


class Part1RowRegen:
    """kp_part1_b1bの再生成を、変わった1行(CAND_IDのrow)だけに限定するtool内shim(Production module編集0)。他行は前回の承認済み出力を保持する。
    runnerの`_ensure`・来歴・stale化はそのまま通る。部分再生成であることは出力docのaudit.partial_regenerationに記録する。"""

    def __init__(self, R, old_part1: dict, changed_rank: int):
        import er003_kp_general_explanation_01 as p1
        self.R, self.p1, self.old, self.changed_rank = R, p1, old_part1, changed_rank
        self.orig = p1.generate_for_kp_items
        self.log = None

    def _part1(self, items, call_fn=None, client=None, level=None):
        p1, old, cr = self.p1, self.old, self.changed_rank
        lv = level or p1.LEVEL_B1B
        sitems = p1.sorted_items(items)
        phrases = p1.strict_phrases(sitems)
        changed = [it for it in sitems if it["rank"] == cr]
        if len(changed) != 1:
            raise ToolRefused(f"変更rank={cr}のPart 1 itemが{len(changed)}件です")
        for pos, it in enumerate(sitems):
            if it["rank"] == cr:
                continue
            if it["rank"] not in old["ranks"] or old["phrases"][old["ranks"].index(it["rank"])] != phrases[pos]:
                raise ToolRefused(f"Part 1 rank={it['rank']} の表現が旧docと異なります(変更対象はrank{cr}のみ)。部分再生成できません")
        res = self.orig(changed, call_fn=call_fn, client=client, level=lv)
        rows = []
        for pos, it in enumerate(sitems):
            if it["rank"] == cr:
                row = copy.deepcopy(res["items"][0])
                row["rank_index"] = pos + 1
            else:
                row = copy.deepcopy(old["items"][old["ranks"].index(it["rank"])])
            rows.append(row)
        out = {"schema": old["schema"], "phrases_signature": p1.phrases_signature(sitems, level=lv), "phrases": phrases, "ranks": [it["rank"] for it in sitems],
               "items": rows, "audit": copy.deepcopy(res["audit"])}
        if lv != p1.LEVEL_B1B:
            out["level"] = lv
        out["audit"]["partial_regeneration"] = {"tool": TOOL_ID, "regenerated_ranks": [cr], "retained_ranks": [it["rank"] for it in sitems if it["rank"] != cr],
                                                "reason": "ユーザー原文USER_03 §2: 変更と無関係な学習項目は再生成しない", "retained_audit": old.get("audit")}
        self.log = out["audit"]["partial_regeneration"]
        return out

    def __enter__(self):
        self.p1.generate_for_kp_items = self._part1
        return self

    def __exit__(self, *a):
        self.p1.generate_for_kp_items = self.orig


def kp_prepare(R, ctx, text: str) -> dict:
    kp_dir = R._kp_src_dir(ctx, LOCKED_LEVEL)
    review_res = R._kp_review_step(ctx, LOCKED_LEVEL, text)
    kr = review_res.get("kp_review") or {}
    if kr.get("state") in ("PENDING", "FAILED") or not kr.get("signature"):
        raise ToolRefused(f"再確定後のKP review stepが確定済みで返りません: {kr}")
    R.install_kp_assets(ctx, LOCKED_LEVEL)
    prov = R._prov(ctx)
    input_sha = R._sha(f"{text}|{kr['signature']}")
    entry_before = copy.deepcopy(prov.stage_entry(f"kp_{LOCKED_LEVEL}"))
    ev = R._rebind_kp_on_confirmation(ctx, prov, LOCKED_LEVEL, text, kr, input_sha)
    if ev is None:
        raise ToolRefused("kp_b1b来歴の付替えが成立しませんでした(runnerの条件: 旧署名で再計算した入力shaが記録と一致/現在のassetsが新しい確定と一致)。付替えません")
    prov = R._prov(ctx)
    e = prov.stage_entry(f"kp_{LOCKED_LEVEL}")
    e["rebinds"][-1]["tool_context"] = {"tool_id": TOOL_ID, "user_ref": USER_REF, "user_ref_sha256": USER_REF_SHA256, "user_spec": USER_SPEC,
                                        "change": f"{OLD_FORM} -> {NEW_FORM}", "candidate_id": CAND_ID,
                                        "note": "ユーザー指示による②追加解説の変更(署名変化+vocab assets更新)。kp_b1b_result.json(出力)は不変のまま来歴の入力/署名だけ付替え"}
    prov.save()
    return {"signature": kr["signature"], "input_sha_from": entry_before["input_sha256"], "input_sha_to": input_sha, "rebind_event": ev}


def regen_sequence(R, ctx) -> dict:
    w62 = R._m().w62
    log = []
    for i, target in enumerate(REGEN_SEQUENCE):
        ctx.regenerate_stage = target
        nxt = REGEN_SEQUENCE[i + 1] if i + 1 < len(REGEN_SEQUENCE) else None
        try:
            res = R.stage_kp(ctx)
            log.append({"regenerate": target, "result": "completed", "summary": json.loads(json.dumps(res, default=str))})
        except w62.FamilyZProvenanceMismatchStop as e:
            if nxt is None or not str(e).startswith(f"{nxt}:"):
                raise
            log.append({"regenerate": target, "result": f"expected_stop_at_{nxt}", "message": str(e)[:200]})
    ctx.regenerate_stage = None
    res = R.stage_kp(ctx)
    log.append({"regenerate": None, "result": "completed(all reused expected)", "summary": json.loads(json.dumps(res, default=str))})
    return {"log": log, "final": log[-1]["summary"]}


def _snapshot_other_items(rec: dict) -> dict:
    return {i["candidate_id"]: {k: i.get(k) for k in ("slot", "category", "used_form", "display_phrase", "key_phrase", "japanese_gloss")} for i in rec["items"] if i["candidate_id"] != CAND_ID}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("apply", "dry-run"))
    ap.add_argument("--by", required=True)
    ap.add_argument("--rehearsal-dir", default=None)
    ap.add_argument("--budget-jpy", type=float, default=5.0, help="このtoolが使うLLM費用の上限(円)。超える見込みなら新規API呼出の前に停止")
    ap.add_argument("--report", default=None)
    a = ap.parse_args(argv)
    dry = a.cmd == "dry-run"
    run_dir = A.run_dir_of(a.rehearsal_dir)
    report = {"tool": TOOL_ID, "cmd": a.cmd, "run_dir": run_dir, "rehearsal": bool(a.rehearsal_dir), "at": _now()}
    lock_taken, st, backup_dir = False, None, None
    try:
        if not os.path.isdir(run_dir):
            raise ToolRefused(f"run dirがありません: {run_dir}")
        if _sha_bytes(open(USER_REF, "rb").read()) != USER_REF_SHA256:
            raise ToolRefused("ユーザー原文(USER_03)のfile shaが定数と一致しません")
        import er119_kp_human_review_01 as rv
        import er121_family_y_structure_01 as ys
        cc = rv._cc()
        with A._quiet():
            R0, ctx0 = A.build_ctx(a.rehearsal_dir)
        st = R0._m().st
        st.check_stop_sentinel("tool:start", run_dir)
        kp_dir = R0._kp_src_dir(ctx0, LOCKED_LEVEL)
        text = ys.canonical_body(open(os.path.join(run_dir, "translate", f"{LOCKED_LEVEL}.md"), encoding="utf-8").read())
        live0 = cc.live_user_record(kp_dir)
        if live0 is not None and any(i["candidate_id"] == CAND_ID and i.get("used_form") == NEW_FORM for i in live0["items"]):
            find_cand(rv.load_candidates(kp_dir), expect_form=NEW_FORM)
            report.update(result="NO_OP_ALREADY_APPLIED", note=f"{CAND_ID}は既に `{NEW_FORM}` で確定済み。何もしません")
            print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
            return 0
        pre = check_preconditions(kp_dir, "pre_revoke")
        if rv.sha256_text(text) != pre["review"]["text_sha256"]:
            raise ToolRefused("reviewのtext_sha256と本文(translate/b1b.md)が一致しません")
        ng_ent = rv.ng_entries_of(pre["review"], "y", LOCKED_SLUG, LOCKED_LEVEL)
        cand0 = find_cand(pre["cands"], expect_form=OLD_FORM)
        dg = deterministic_gates(cand0, text, ng_ent)
        report["deterministic_gates"] = {"exemption": dg["exemption"], "normalization_reason": dg["item"].get("normalization_reason"),
                                         "changed_from_display_phrase": dg["item"].get("changed_from_display_phrase"), "validate": dg["validate"]}
        raw = open(os.path.join(kp_dir, "confirmed_selection_source", "rev4_payload.json"), "rb").read()
        if _sha_bytes(raw) != SOURCE_PAYLOAD_SHA256:
            raise ToolRefused("原本payload(rev4_payload.json)のfile shaが定数と一致しません")
        pp = patched_payload(json.loads(raw.decode("utf-8")), pre["cands"], text_sha=pre["cands"]["text_sha256"], new_gloss="<requalify後に確定>")
        dd = T2.diff_payloads(json.loads(raw.decode("utf-8")), pp)
        report["payload_diff"] = dd
        if [d for d in dd if not ALLOWED_DIFFS.match(d)]:
            raise ToolRefused(f"原本payloadの差分が許容集合外: {dd}")
        p1_items = R0._part1_items(ctx0, LOCKED_LEVEL)
        ranks = [it["rank"] for it in p1_items if it.get("candidate_id") == CAND_ID]
        if len(ranks) != 1:
            raise ToolRefused(f"Part 1 itemに{CAND_ID}が{len(ranks)}件です")
        part1_rank = ranks[0]
        report["part1_rank"] = part1_rank
        kp_ids = [i["candidate_id"] for i in cc.live_user_record(kp_dir)["items"] if i.get("slot") == "kp"]
        report["is_audio_kp"] = CAND_ID in kp_ids
        if CAND_ID in kp_ids:
            raise ToolRefused("この項目は音声化されるKP(①)です。本toolは②追加解説専用です")
        if dry:
            report["result"] = "DRY_RUN_OK(LLM 0・何も書いていません)"
            print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
            return 0

        st.acquire_run_lock(run_dir, sys.argv)
        lock_taken = True
        A.MUTABLE_SUBTREES, A.MUTABLE_FILES = MUTABLE_SUBTREES, MUTABLE_FILES
        before_manifest = A.tree_manifest(run_dir)
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(run_dir), f"_backup_{TOOL_ID}_{stamp}")
        report["backup"] = {"dir": backup_dir.replace("\\", "/"), "n_files": len(A.backup_run(run_dir, backup_dir))}
        cost_log_before = open(os.path.join(run_dir, "cost_log.jsonl"), "rb").read() if os.path.exists(os.path.join(run_dir, "cost_log.jsonl")) else b""
        before_prov = json.loads(json.dumps(R0._prov(ctx0).data))
        other_before = _snapshot_other_items(pre["rec"])
        frozen_before = {f: (A._sha_bytes(A._read_bytes(os.path.join(run_dir, f))) if os.path.exists(os.path.join(run_dir, f)) else None)
                         for f in ("study_text/confirmed_grammar.json", "study_text/confirmed_grammar_frozen.json")}
        kp_art_before = json.load(open(os.path.join(kp_dir, "keywords_canonicalized.json"), encoding="utf-8"))
        expl_before = A._sha_bytes(A._read_bytes(os.path.join(kp_dir, "kp_explanations.json")))
        R, ctx, spend = T2.build_real_ctx(a.rehearsal_dir, a.budget_jpy)
        report["budget_cap_jpy"] = a.budget_jpy
        old_part1 = json.load(open(R._part1_path(ctx, LOCKED_LEVEL), encoding="utf-8"))
        old_part1_ja = A._sha_bytes(A._read_bytes(R._part1_ja_path(ctx, LOCKED_LEVEL)))
        report["revoke"] = cc.cmd_revoke(run_dir, LOCKED_LEVEL, a.by, USER_REF, f"{USER_SPEC} に基づく学習表現の変更(ユーザー原文USER_03 §2)")
        article_id = f"family_y_{A.SLUG}_{LOCKED_LEVEL}"
        gloss_factory, qa_call, red_fn, process, model = T2.llm_callables(ctx, article_id)
        report["model_used"] = {"process": process, "model": model, "note": "Production同一route(B1_SUPPORT)。評価用途ではない"}
        report["requalify"] = requalify(kp_dir, by=a.by, text=text, gloss_factory=gloss_factory, qa_call_fn=qa_call, redundancy_fn=red_fn, article_id=article_id,
                                        process=process, out_dir=os.path.join(kp_dir, "requalify_hold_someone_back"))
        report["spent_after_requalify_jpy"] = spend.used()
        report["confirm"] = confirm(run_dir, kp_dir, by=a.by, new_gloss=report["requalify"]["new_gloss"])
        report["kp_prepare"] = kp_prepare(R, ctx, text)
        with Part1RowRegen(R, old_part1, part1_rank) as pr:
            rg = regen_sequence(R, ctx)
        report["partial_regen"] = pr.log
        report["regen"] = rg["log"]
        report["part2_ready"] = T2.part2_ready_check(R, ctx)
        report["spent_total_jpy"] = spend.used()

        rec = cc.live_user_record(kp_dir)
        if rec is None:
            raise ToolRefused("再確定後のliveレコードがありません")
        it1 = [i for i in rec["items"] if i["candidate_id"] == CAND_ID]
        if len(it1) != 1 or it1[0]["used_form"] != NEW_FORM or it1[0]["display_phrase"] != SURFACE or it1[0]["key_phrase"] != NEW_FORM or it1[0].get("slot") != "vocab" or it1[0].get("category") != 2:
            raise ToolRefused(f"再確定後の{CAND_ID}が想定外: {it1}")
        if _snapshot_other_items(rec) != other_before:
            raise ToolRefused("他の確定項目が変わりました")
        new_part1 = json.load(open(R._part1_path(ctx, LOCKED_LEVEL), encoding="utf-8"))
        pos = old_part1["ranks"].index(part1_rank)
        rows_old, rows_new = old_part1["items"], new_part1["items"]
        ret = {"part1_other_rows_identical": all(rows_old[i] == rows_new[i] for i in range(len(rows_old)) if i != pos),
               "part1_changed_row_phrase": rows_new[pos].get("phrase"), "part1_changed_row_changed": rows_new[pos] != rows_old[pos],
               "keywords_canonicalized_unchanged": json.load(open(os.path.join(kp_dir, "keywords_canonicalized.json"), encoding="utf-8")).get("items") == kp_art_before.get("items"),
               "kp_explanations_unchanged": A._sha_bytes(A._read_bytes(os.path.join(kp_dir, "kp_explanations.json"))) == expl_before,
               "part1_ja_unchanged": A._sha_bytes(A._read_bytes(R._part1_ja_path(ctx, LOCKED_LEVEL))) == old_part1_ja}
        report["retained_items_check"] = ret
        if not (ret["part1_other_rows_identical"] and ret["part1_changed_row_changed"] and ret["part1_changed_row_phrase"] == NEW_FORM
                and ret["keywords_canonicalized_unchanged"] and ret["kp_explanations_unchanged"]):
            raise ToolRefused(f"保持すべき項目が変わった、または変更すべき項目が変わっていません: {ret}")
        frozen_after = {f: (A._sha_bytes(A._read_bytes(os.path.join(run_dir, f))) if os.path.exists(os.path.join(run_dir, f)) else None) for f in frozen_before}
        report["grammar_frozen_unchanged"] = frozen_before == frozen_after
        report["grammar_frozen_sha"] = {"before": frozen_before, "after": frozen_after}
        after_prov = R._prov(ctx).data
        report["provenance_changes"] = sorted(n for n in set(before_prov["downstream_stages"]) | set(after_prov["downstream_stages"])
                                              if {k: v for k, v in (before_prov["downstream_stages"].get(n) or {}).items() if k != "rebinds"}
                                              != {k: v for k, v in (after_prov["downstream_stages"].get(n) or {}).items() if k != "rebinds"})
        report["downstream_stale"] = after_prov["downstream_stale"]
        with A._quiet():
            hl = R._resolve_highlights_or_stop(ctx, "tool:hold_someone_back", (LOCKED_LEVEL,))
        report["highlight_resolution_b1b"] = {"returned": type(hl).__name__}
        with A._quiet():
            report["tts_regeneration_plan"] = A.tts_regeneration_plan(R, ctx)
        if any(report["tts_regeneration_plan"].values()):
            raise ToolRefused(f"TTS再生成が必要なsegmentが想定外に出ました(②追加解説は音声なし): {report['tts_regeneration_plan']}")
        after_manifest = A.tree_manifest(run_dir)
        changed = sorted(r for r in set(before_manifest) | set(after_manifest) if before_manifest.get(r) != after_manifest.get(r))
        outside = [r for r in changed if not A._in_mutable(r) and r != "cost_log.jsonl"]
        cl_new = open(os.path.join(run_dir, "cost_log.jsonl"), "rb").read() if os.path.exists(os.path.join(run_dir, "cost_log.jsonl")) else b""
        report["cost_log_append_only"] = cl_new.startswith(cost_log_before)
        if not report["cost_log_append_only"]:
            raise ToolRefused("cost_log.jsonlが追記のみではありません")
        report["changed_files"] = {"n": len(changed), "outside_mutable_area": outside}
        if outside:
            raise ToolRefused(f"想定外の領域のfileが変わりました: {outside[:10]}")
        report["result"] = "APPLIED"
        if a.report:
            with open(a.report, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=1, default=str)
        print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
        return 0
    except BaseException as e:   # noqa: BLE001
        restored = False
        if backup_dir and os.path.isdir(backup_dir):
            try:
                A.restore_run(run_dir, backup_dir)
                restored = True
            except Exception as e2:   # noqa: BLE001
                print(f"[{TOOL_ID}][RESTORE_FAILED] {e2.__class__.__name__}: {e2}", file=sys.stderr)
        kind = "REFUSED" if isinstance(e, ToolRefused) else "FAILED"
        print(f"[{TOOL_ID}][{kind}] {e.__class__.__name__}: {e}  (restored={restored})", file=sys.stderr)
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        return 2
    finally:
        if lock_taken and st is not None:
            st.release_run_lock(run_dir)


if __name__ == "__main__":
    sys.exit(main())
