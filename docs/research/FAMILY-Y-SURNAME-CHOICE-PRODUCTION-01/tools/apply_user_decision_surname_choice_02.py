# -*- coding: utf-8 -*-
"""使い捨てtool B(FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 委任_04B。Opus条件Aレビュー M8 反映)。

目的: Family Y「夫が妻の姓を選ぶとき」Advanced(b1b)のKey Phrase rank1 `taking offense` を、ユーザー原文§5の指示どおり `take offense` へ変更する
(Advanced KP rank1のみ。本文の `without taking offense` は前置詞の後で文法上必要な形のため**維持**。KP2・3、Standard、他の学習項目は変えない)。
**汎用opではない**: slug=surname_choice / level=b1b / candidate_id=p_85cbe0223d / 旧句`taking offense` / 新句`take offense` に固定(任意文字列・他記事・他levelは拒否)。

M8(免除は1点だけ): kc.validate_canonicalization_item の Rule7(『source_span内の連続部分文字列でも人称代名詞一般化でもない別の辞書形を生成しない』)が
`take offense`(動詞+裸名詞の原形化)を拒否する。これを、**このtool内の閉じた定数ペア(p_85cbe0223d, taking offense -> take offense)に限り**、ユーザー原文§5を根拠に免除する。
免除は(1) Rule7の不合格理由だけ(他の理由が1つでもあれば拒否) (2) 候補item・確定レコードのorigin.transcription に `exemption` として記録する。
Production側(runner/er003/er105/er119/er128)には汎用の免除参照を足さない(編集0)。他の全ゲート(CMU・記号検出・Human NG・gloss再整合・QA 12項目[全PASS必須]・
候補全体Redundancy QA・presentation_blockers)は再適用する。1つでも不合格なら**回避せず**拒否(ユーザー決定の実現不能=Fableへ報告)。

順序(M8): A(`apply_v1_intro_patch_01.py`)を先に適用 -> 本tool。段階: revoke -> requalify(LLMゲート) -> confirm -> 再生成(kp_expl_b1b / kp_part1_b1b。単一regen制約に合わせ
runnerのstage_kpをregenerate_stage別に順に呼ぶ。期待する『次の再生成対象の親sha不一致』だけをSTOPとして許容し、それ以外は失敗) -> 事後検査。
LLM: requalify(gloss再整合1・QA再判定1・Redundancy QA1) + kp解説1 + Part 1 1〜2 = 想定¥2〜4。--dry-runはLLM 0・何も書かない。失敗時は退避から全復元。

実行: .venv\\Scripts\\python.exe docs\\research\\FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01\\tools\\apply_user_decision_surname_choice_02.py apply|dry-run --by <名> [--rehearsal-dir <root>] --budget-jpy <円>
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
import apply_v1_intro_patch_01 as A  # noqa: E402  (退避/復元/manifest/atomic書込/quiet を共有。importでcwd=repo rootになる)

ROOT = A.ROOT

TOOL_ID = "apply_user_decision_surname_choice_02"
LOCKED_SLUG, LOCKED_RUN, LOCKED_LEVEL = "surname_choice", "run_02", "b1b"
CAND_ID = "p_85cbe0223d"
OLD_FORM, NEW_FORM = "taking offense", "take offense"
USER_REF, USER_REF_SHA256 = A.USER_REF, A.USER_REF_SHA256
USER_SPEC = "§5 学習表現の変更(`taking offense` -> `take offense`。本文はoffense表記・前置詞後のため維持、見出し・説明・音声等を基本形に整合)"
ATTESTATION = "user_instruction_transcription"
# 変更前に確定した原本フォーム送信(ユーザー確定 rev1)。これを土台に rank1 の term だけを差替える
SOURCE_PAYLOAD_REL = "key_phrases/b1b/confirmed_selection_source/rev1_payload.json"
SOURCE_PAYLOAD_SHA256 = "fe4e47d1f8dccc8b8149d822be272285a5a3195fb7c2e35a23caafa960f78c31"
RULE7_MARK = "Rule7"
# 変更が起き得る領域(退避対象)
MUTABLE_SUBTREES = ("key_phrases", "b1b/key_phrases", "study_text", "b1b/audit", "audit")
MUTABLE_FILES = ("provenance.json", "kp_review_pending.json", "study_text_slots.json", "voice_assignment.json")
# 再生成の順序(単一regen制約: stage_kpをregenerate_stage別に順に呼ぶ)
REGEN_SEQUENCE = ("kp_expl_b1b", "kp_part1_b1b", "part2_b1b")       # part2_b1b=確定文法の再書込み(cmd_from_form)で凍結ファイルが退避されるため再finalize(LLM 0)で凍結を再作成


class ToolRefused(Exception):
    pass


A.ToolRefused = ToolRefused        # Aの関数が投げる例外を同じ型にそろえる


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha_json(o) -> str:
    return _sha_bytes(json.dumps(o, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 前提・決定論ゲート
# ------------------------------------------------------------------------------------------------------------------------------------------------
def find_cand(cands: dict, *, expect_form: str) -> dict:
    hits = [c for c in cands.get("candidates") or [] if c.get("candidate_id") == CAND_ID]
    if len(hits) != 1:
        raise ToolRefused(f"candidate_id={CAND_ID} が{len(hits)}件です(1件のみ許可)")
    c = hits[0]
    if c.get("used_form") != expect_form or (c.get("item") or {}).get("used_form") != expect_form:
        raise ToolRefused(f"候補{CAND_ID}の現在のused_formが{expect_form!r}ではありません: {c.get('used_form')!r}")
    return c


def check_preconditions(kp_dir: str, stage: str) -> dict:
    """stage = 'pre_revoke' | 'post_revoke'。何も書かない。"""
    import er119_kp_human_review_01 as rv
    cc = rv._cc()
    review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
    if review is None or cands is None:
        raise ToolRefused("候補/reviewがありません")
    ak = review.get("article_key") or {}
    if (ak.get("slug"), (ak.get("family") or "").lower(), review.get("level")) != (LOCKED_SLUG, "y", LOCKED_LEVEL):
        raise ToolRefused(f"対象外のrunです(固定: slug={LOCKED_SLUG}, family=y, level={LOCKED_LEVEL}。実際: {ak}, level={review.get('level')})")
    if review["status"] != rv.ST_REVIEWED:
        raise ToolRefused(f"review.status={review['status']}(REVIEWEDのみ対象。ユーザー確定済みのKPの事後変更)")
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
        if len(it1) != 1 or it1[0]["used_form"] != OLD_FORM or it1[0].get("slot") != "kp":
            raise ToolRefused(f"確定レコードの{CAND_ID}が想定(kp slot, used_form={OLD_FORM!r})と一致しません: {it1}")
        find_cand(cands, expect_form=OLD_FORM)
    else:
        if live is not None:
            raise ToolRefused("まだliveの確定レコードがあります(先にrevoke)")
        find_cand(cands, expect_form=OLD_FORM)
    return {"review": review, "cands": cands, "rec": rec}


def deterministic_gates(cand: dict, text: str, ng_entries: list) -> dict:
    """LLMを使わないゲート(Production関数の再利用)。Rule7だけ閉じた定数ペアに限り免除(M8)。"""
    import er003_key_words_canonicalization as kc
    import er003_v1_n3_01_scaffold_generate as sc
    import er105_kp_fulltext_selector_01 as ft
    import er108_kp_cmu_lexicon_gate_01 as cmu
    import er119_kp_human_review_01 as rv
    import er125_kp_rescue_production_01 as er125
    it = copy.deepcopy(cand["item"])
    role_ok = frozenset((it.get("person_role_repair") or {}).get("role_ok_poss") or [])
    span, display, sentence = it.get("source_span") or "", it.get("display_phrase") or "", it.get("source_sentence") or ""
    if cand.get("candidate_id") != CAND_ID or display != OLD_FORM or span != OLD_FORM:
        raise ToolRefused(f"固定条件(候補{CAND_ID}, display/source_span={OLD_FORM!r})と一致しません")
    # 本文(出典文)に表層形が連続して存在すること(ハイライトは source_span で解決される。本文は変更しない)
    if re.sub(r"[^a-z0-9' -]+", "", OLD_FORM.lower()) not in re.sub(r"[^a-z0-9' -]+", "", sentence.lower()):
        raise ToolRefused(f"表層形{OLD_FORM!r}が出典文に連続して存在しません: {sentence!r}")
    if OLD_FORM not in text:
        raise ToolRefused(f"本文に表層形{OLD_FORM!r}がありません")
    it["key_phrase"], it["used_form"] = NEW_FORM, NEW_FORM
    ft._recompute_item_fields(it, display, NEW_FORM, role_ok)
    if it.get("normalization_reason") not in ("lemma_normalization",):
        it["normalization_reason"] = "lemma_normalization"       # 動詞の原形化(原文§5)。_recompute_item_fieldsは語形差から再計算するが、明示してから検証する
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
    mo = er125.ng_match_originals(dict(probe, rescue=cand.get("rescue")), ng_entries, rv.match_ng, rv.candidate_id_for) if cand.get("rescue") else None
    if mt == "exact" or mo == "exact":
        raise ToolRefused("Human NGと一致します")
    return {"item": it, "role_ok": role_ok, "exemption": exemption, "similar_to_ng": (mt == "similar") or (mo == "similar")}


def patched_payload(source: dict, cands_after: Optional[dict], *, text_sha: str) -> dict:
    """原本フォーム送信(rev1)の p_85... の term だけを新句へ。candidates_sha256/text_sha256を現在docに合わせる。他は1文字も変えない。"""
    out = copy.deepcopy(source)
    n = 0
    for grp in ("key_phrase", "extra_explanation", "meaning_display"):
        for rec in out["selection"][grp]:
            if rec["candidate_id"] == CAND_ID:
                if rec["term"] != OLD_FORM:
                    raise ToolRefused(f"原本payloadの{CAND_ID}のtermが{OLD_FORM!r}ではありません: {rec['term']!r}")
                rec["term"] = NEW_FORM
                n += 1
    if n != 1:
        raise ToolRefused(f"原本payload内の対象項目が{n}件です(1件のみ許可)")
    if cands_after is not None:
        out["article"]["candidates_sha256"] = cands_after["candidates_sha256"]
    out["article"]["text_sha256"] = text_sha
    return out


def diff_payloads(a, b, path="") -> list:
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            diffs += diff_payloads(a.get(k), b.get(k), f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            diffs += diff_payloads(x, y, f"{path}[{i}]")
    elif a != b:
        diffs.append(path)
    return diffs


ALLOWED_DIFFS = re.compile(r"^(/article/candidates_sha256|/article/text_sha256|/selection/key_phrase\[0\]/term)$")


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 手続き
# ------------------------------------------------------------------------------------------------------------------------------------------------
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
    report = {"candidate_id": CAND_ID, "from": OLD_FORM, "to": NEW_FORM, "gates": {"preconditions": "PASS", "span_in_sentence": "PASS", "cmu": "PASS", "symbol": "PASS", "human_ng": "PASS"},
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
                          "`take offense`は提示可能な候補にできません=ユーザー決定の実現不能。回避せずFableへ報告")
    item2["qa"], item2["qa_overall_status"] = dict(q["qa"]), "PASS"
    new = copy.deepcopy(cand)
    new.update(used_form=NEW_FORM, japanese_gloss=item2.get("japanese_gloss"), word_count=ft.count_words(NEW_FORM), item=item2)
    new["kind"] = bf.kind_of_phrase(NEW_FORM)
    new["flags"] = dict(cand.get("flags") or {}, qa_fail=False, gloss_hr_pending=False, similar_to_ng=bool(dg["similar_to_ng"]), redundant_with=[])
    new["gates"] = dict(new.get("gates") or {}, canonicalization="RESCUED_QA_REJUDGED_PASS", gloss="ALIGNED")
    # 救済メタ(rescue): 本ツールのgloss再整合・QA再判定(全12項目PASS)の結果で更新(presentation_blockersの『救済後の表現が未検査』を満たす正規の記録)。
    # 旧canonicalization記録(llm_key_phrase=take offense が Rule7で REVERT_SURFACEされた経緯)は履歴として残し、ユーザー指示による確定を追記する
    rs = copy.deepcopy(cand.get("rescue") or (cand.get("item") or {}).get("rescue") or {})
    rs["gloss"] = {"status": er125.GLOSS_REALIGNED, "by": TOOL_ID}
    rs["qa"] = {"status": er125.QA_REJUDGED_PASS, "by": TOOL_ID, "model_id": report.get("qa_model_id")}
    rs["user_instruction"] = {"tool": TOOL_ID, "from": OLD_FORM, "to": NEW_FORM, "user_ref": USER_REF, "exemption": dg["exemption"]}
    new["rescue"], item2["rescue"] = rs, copy.deepcopy(rs)
    new["rescue_note"] = f"修正済み(元: {OLD_FORM} / REVERT_SURFACE。ユーザー指示§5で `{NEW_FORM}`)・QA再判定済み"
    new["auto_eligible"] = not new["flags"]["similar_to_ng"]
    new["requalified"] = {"tool": TOOL_ID, "from": OLD_FORM, "to": NEW_FORM, "user_ref": USER_REF, "user_ref_sha256": USER_REF_SHA256, "user_spec": USER_SPEC, "by": by,
                          "exemption": dg["exemption"], "old_item_sha256": _sha_json(cand["item"]), "old_kind": cand.get("kind"), "new_kind": new["kind"],
                          "old_gloss": cand.get("japanese_gloss"), "display_phrase_kept": item2.get("display_phrase"), "source_span_kept": item2.get("source_span")}
    if item2.get("display_phrase") != OLD_FORM or item2.get("source_span") != OLD_FORM or new["item"].get("used_form") != NEW_FORM or new["item"].get("key_phrase") != NEW_FORM:
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


def confirm(run_dir: str, kp_dir: str, *, by: str, dry_run: bool = False) -> dict:
    import er119_kp_human_review_01 as rv
    import er128_form_readable_restore_01 as fr
    cc = rv._cc()
    sp = os.path.join(kp_dir, "confirmed_selection_source", "rev1_payload.json")
    raw = open(sp, "rb").read()
    if _sha_bytes(raw) != SOURCE_PAYLOAD_SHA256:
        raise ToolRefused("原本payload(rev1_payload.json)のfile shaが定数と一致しません")
    source = json.loads(raw.decode("utf-8"))
    cands = rv.load_candidates(kp_dir)
    payload = patched_payload(source, cands, text_sha=cands["text_sha256"])
    d_all = diff_payloads(source, payload)
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


# ------------------------------------------------------------------------------------------------------------------------------------------------
# runner context(LLMあり。予算は引数で上限)
# ------------------------------------------------------------------------------------------------------------------------------------------------
class Spend:
    def __init__(self, cost_log: str, cap_jpy: float):
        import er019_family_x_audio_production_runner_01 as xr
        self.xr, self.cost_log, self.cap = xr, cost_log, float(cap_jpy)
        self.base = self.total()

    def total(self) -> float:
        return float(self.xr.compute_cost_jpy_so_far(self.cost_log)[0]) if os.path.exists(self.cost_log) else 0.0

    def used(self) -> float:
        return round(self.total() - self.base, 4)


def build_real_ctx(rehearsal_dir: Optional[str], cap_jpy: float):
    import er121_family_y_runner_01 as R
    root = rehearsal_dir if rehearsal_dir else A.REAL_RUN_ROOT
    ctx = R.YContext(slug=A.SLUG, run=A.RUN, mode="real", run_root=root, theme_package_path=A.THEME_PKG, reuse_manifest_path=A.REUSE_MANIFEST)
    cost_log = f"{ctx.out_dir}/cost_log.jsonl"
    spend = Spend(cost_log, cap_jpy)
    ctx.budget = R.E2EBudget(cap_jpy, 100.0, spent_fn=lambda: spend.used(), ack_warn=True)      # このtoolの追加支出だけをcapに数える
    st = R._m().st
    st.check_stop_sentinel("tool:build_real_ctx", ctx.out_dir)
    R.resolve_style_profile(ctx, write=False)
    from dotenv import load_dotenv
    load_dotenv()
    import er005_cost_logger as cl
    cl.install(cost_log)
    st.install_api_stop_guard()
    import er003_v1_en_direct_vfl_01_generate as vfl01
    ctx.llm_client = vfl01.get_client()
    return R, ctx, spend


def llm_callables(ctx, article_id: str):
    import er003_key_words_canonicalization as kc
    import er003_key_words_gloss_alignment as ga
    import er003_v1_n3_01_scaffold_generate as sc
    import er005_cost_logger as cl
    import er006_model_routing_contract_01 as routing
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)

    def gloss_factory(msg):
        return ga.make_alignment_fn(msg, model=model)

    def qa_call(msg):
        with cl.logging_context(ctx.theme_tag, "kp_requalify_qa_rejudge"):
            return kc.make_canonicalization_fn(msg, model=model, schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)()
    return gloss_factory, qa_call, sc.run_key_phrase_redundancy_qa, "B1_SUPPORT", model


CHANGED_RANKS = frozenset({1})       # 変更するのはKP rank1のみ(ユーザー原文§5: 他のKey Phrase・Word・学習項目は変更しない)


class PartialRegen:
    """KP英語解説(kp_expl_b1b)とPart 1(kp_part1_b1b)の再生成を、変わったrank(=1)だけに限定する(tool内shim。Production moduleは編集しない)。

    runnerのstage_kpは入力が変わったunitを全itemまとめて再生成する(LLMの非決定で、変更しないKP2・3の解説文やPart 1の他行の文言まで変わり、
    その音声も作り直しになる)。ユーザー原文§5『他のKey Phrase・Word・学習項目は変更しません』のため、変わったrankだけをLLMに作らせ、残りは前回の承認済み出力を
    そのまま保持する。runnerの`_ensure`(regenerate・来歴・stale化)と保存処理はそのまま通る。部分再生成であることは出力docの audit に記録する。"""

    def __init__(self, R, old_kp_items: list, old_expl: dict, old_part1: dict):
        import er003_kp_general_explanation_01 as p1
        import er019_family_x_kp_explanation_01 as kexp
        self.R, self.p1, self.kexp = R, p1, kexp
        self.old_kp = {it["rank"]: it for it in old_kp_items}
        self.old_expl, self.old_part1 = old_expl, old_part1
        self.orig_expl, self.orig_p1 = kexp.generate_kp_explanations, p1.generate_for_kp_items
        self.log = {"kp_expl": None, "part1": None}

    def _expl(self, items, call_fn=None, client=None):
        changed = [it for it in items if it["rank"] in CHANGED_RANKS]
        for it in items:
            if it["rank"] in CHANGED_RANKS:
                continue
            o = self.old_kp.get(it["rank"])
            if o is None or (self.kexp.explanation_phrase(o), o.get("japanese_gloss", ""), o.get("source_sentence", "")) != (it["display_phrase"], it.get("japanese_gloss", ""), it["source_sentence"]):
                raise ToolRefused(f"KP rank={it['rank']} の解説入力が旧確定と異なります(変更対象はrank1のみ)。部分再生成できません")
            if str(it["rank"]) not in self.old_expl["items"] or self.old_expl["items"][str(it["rank"])].get("status") != "OK":
                raise ToolRefused(f"保持すべきrank={it['rank']}の旧解説がOKではありません")
        res = self.orig_expl(changed, call_fn=call_fn, client=client)
        items_out = {}
        for it in items:
            items_out[it["rank"]] = res["items"][it["rank"]] if it["rank"] in CHANGED_RANKS else copy.deepcopy(self.old_expl["items"][str(it["rank"])])
        audit = copy.deepcopy(res["audit"])
        audit["partial_regeneration"] = {"tool": TOOL_ID, "regenerated_ranks": sorted(CHANGED_RANKS), "retained_ranks": sorted(r for r in items_out if r not in CHANGED_RANKS),
                                         "reason": "ユーザー原文§5: 他のKey Phrase・学習項目は変更しない", "retained_audit": self.old_expl.get("audit")}
        self.log["kp_expl"] = audit["partial_regeneration"]
        return {"items": items_out, "audit": audit}

    def _part1(self, items, call_fn=None, client=None, level=None):
        p1 = self.p1
        lv = level or p1.LEVEL_B1B
        sitems = p1.sorted_items(items)
        phrases = p1.strict_phrases(sitems)
        old = self.old_part1
        changed = [it for it in sitems if it["rank"] in CHANGED_RANKS]
        for pos, it in enumerate(sitems):
            if it["rank"] in CHANGED_RANKS:
                continue
            if it["rank"] not in old["ranks"] or old["phrases"][old["ranks"].index(it["rank"])] != phrases[pos]:
                raise ToolRefused(f"Part 1 rank={it['rank']} の表現が旧docと異なります(変更対象はrank1のみ)。部分再生成できません")
        res = self.orig_p1(changed, call_fn=call_fn, client=client, level=lv)
        rows = []
        for pos, it in enumerate(sitems):
            if it["rank"] in CHANGED_RANKS:
                row = copy.deepcopy(res["items"][[c["rank"] for c in changed].index(it["rank"])])
                row["rank_index"] = pos + 1
            else:
                row = copy.deepcopy(old["items"][old["ranks"].index(it["rank"])])
            rows.append(row)
        out = {"schema": old["schema"], "phrases_signature": p1.phrases_signature(sitems, level=lv), "phrases": phrases, "ranks": [it["rank"] for it in sitems],
               "items": rows, "audit": copy.deepcopy(res["audit"])}
        if lv != p1.LEVEL_B1B:
            out["level"] = lv
        out["audit"]["partial_regeneration"] = {"tool": TOOL_ID, "regenerated_ranks": sorted(CHANGED_RANKS),
                                                "retained_ranks": [it["rank"] for it in sitems if it["rank"] not in CHANGED_RANKS],
                                                "reason": "ユーザー原文§5: 他のKey Phrase・学習項目は変更しない", "retained_audit": old.get("audit")}
        self.log["part1"] = out["audit"]["partial_regeneration"]
        return out

    def __enter__(self):
        self.kexp.generate_kp_explanations = self._expl
        self.p1.generate_for_kp_items = self._part1
        return self

    def __exit__(self, *a):
        self.kexp.generate_kp_explanations = self.orig_expl
        self.p1.generate_for_kp_items = self.orig_p1


def kp_prepare(R, ctx, text: str) -> dict:
    """再確定後の確定物の再finalize(runnerの_kp_review_step=ensure_kp_review。確定集合のRedundancy QAはcacheが無ければ1 call)→KP assetsのinstall→
    kp_b1b来歴の付替え(runner自身の_rebind_kp_on_confirmation。内容が変わる確定では、先にassetsを新しい確定へ揃えないと条件『現在のKP assetsが新しい確定と一致』を満たせない)。"""
    import er119_kp_human_review_01 as rv
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
                                        "note": "ユーザー指示による確定内容の変更(署名変化+assets更新)。kp_b1b_result.json(出力)は不変のまま来歴の入力/署名だけ付替え"}
    prov.save()
    return {"signature": kr["signature"], "input_sha_from": entry_before["input_sha256"], "input_sha_to": input_sha, "rebind_event": ev}


def part2_ready_check(R, ctx) -> dict:
    """TTS前提(API 0): Part 2 b1b/a2が現在の本文・確定・凍結と一致(runnerの使う側の入口と同じ検査)。a2は本tool対象外だが、A適用後の状態で崩していないことを確認する。"""
    out = {}
    with A._quiet():
        out["b1b"] = bool(R._assert_study_ready(ctx, "tool:take_offense"))
        out["a2"] = bool(R._assert_std_study_ready(ctx, "tool:take_offense"))
    import er128_kp_confirmed_content_01 as cc
    out["frozen_grammar_present"] = bool(cc.load_frozen_grammar_items(R._part2_dir(ctx, LOCKED_LEVEL)))
    if not out["frozen_grammar_present"]:
        raise ToolRefused("文法の凍結(confirmed_grammar_frozen.json)がありません")
    return out


def regen_sequence(R, ctx) -> dict:
    """単一regen制約: stage_kpを regenerate_stage 別に順に呼ぶ。期待する『次の再生成対象の親sha不一致』だけを許容(それ以外のSTOPは失敗)。"""
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
    res = R.stage_kp(ctx)       # 最後に再生成指定なしで全stageがreusedになること
    log.append({"regenerate": None, "result": "completed(all reused expected)", "summary": json.loads(json.dumps(res, default=str))})
    return {"log": log, "final": log[-1]["summary"]}


# ------------------------------------------------------------------------------------------------------------------------------------------------
# 本体
# ------------------------------------------------------------------------------------------------------------------------------------------------
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
            raise ToolRefused("ユーザー原文(USER_02)のfile shaが定数と一致しません")
        import er119_kp_human_review_01 as rv
        import er121_family_y_structure_01 as ys
        cc = rv._cc()
        with A._quiet():
            R0, ctx0 = A.build_ctx(a.rehearsal_dir)         # API 0 ctx(読取・dry-run用)
        st = R0._m().st
        st.check_stop_sentinel("tool:start", run_dir)
        kp_dir = R0._kp_src_dir(ctx0, LOCKED_LEVEL)
        text = ys.canonical_body(open(os.path.join(run_dir, "translate", f"{LOCKED_LEVEL}.md"), encoding="utf-8").read())
        live0 = cc.live_user_record(kp_dir)
        if live0 is not None and any(i["candidate_id"] == CAND_ID and i.get("used_form") == NEW_FORM for i in live0["items"]):
            c0 = rv.load_candidates(kp_dir)
            find_cand(c0, expect_form=NEW_FORM)             # 候補docも新句であること(確定だけ新句の不整合は拒否)
            report.update(result="NO_OP_ALREADY_APPLIED", note=f"{CAND_ID}は既に `{NEW_FORM}` で確定済み(候補doc・確定レコードとも)。何もしません")
            print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
            return 0
        pre = check_preconditions(kp_dir, "pre_revoke")
        if rv.sha256_text(text) != pre["review"]["text_sha256"]:
            raise ToolRefused("reviewのtext_sha256と本文(translate/b1b.md)が一致しません(Aを先に適用/整合させてください)")
        report["a_applied"] = any(ev.get("tool_id") == A.TOOL_ID for ev in (R0._prov(ctx0).stage_entry("translate_b1b") or {}).get("rebinds") or [])
        ng_ent = rv.ng_entries_of(pre["review"], "y", LOCKED_SLUG, LOCKED_LEVEL)
        cand0 = find_cand(pre["cands"], expect_form=OLD_FORM)
        dg = deterministic_gates(cand0, text, ng_ent)
        report["deterministic_gates"] = {"exemption": dg["exemption"], "normalization_reason": dg["item"].get("normalization_reason"),
                                         "changed_from_display_phrase": dg["item"].get("changed_from_display_phrase")}
        # 原本payloadの差替え差分(要: 差替え後の候補doc。dry-runでは候補shaは旧のまま計算)
        raw = open(os.path.join(kp_dir, "confirmed_selection_source", "rev1_payload.json"), "rb").read()
        if _sha_bytes(raw) != SOURCE_PAYLOAD_SHA256:
            raise ToolRefused("原本payload(rev1_payload.json)のfile shaが定数と一致しません")
        pp = patched_payload(json.loads(raw.decode("utf-8")), pre["cands"], text_sha=pre["cands"]["text_sha256"])
        dd = diff_payloads(json.loads(raw.decode("utf-8")), pp)
        report["payload_diff"] = dd
        if [d for d in dd if not ALLOWED_DIFFS.match(d)]:
            raise ToolRefused(f"原本payloadの差分が許容集合外: {dd}")
        if dry:
            report["result"] = "DRY_RUN_OK(LLM 0・何も書いていません)"
            print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
            return 0

        # ---- 適用 ----
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
        R, ctx, spend = build_real_ctx(a.rehearsal_dir, a.budget_jpy)
        report["budget_cap_jpy"] = a.budget_jpy
        kp_paths = rv.paths(kp_dir)
        old_kp_items = json.load(open(kp_paths["kp"], encoding="utf-8"))["items"]
        old_expl = json.load(open(os.path.join(kp_dir, "kp_explanations.json"), encoding="utf-8"))
        old_part1 = json.load(open(R._part1_path(ctx, LOCKED_LEVEL), encoding="utf-8"))
        # 1) revoke
        report["revoke"] = cc.cmd_revoke(run_dir, LOCKED_LEVEL, a.by, USER_REF, f"{USER_SPEC} に基づくKey Phrase表記の変更(ユーザー原文§5)")
        # 2) requalify(LLMゲート)
        article_id = f"family_y_{A.SLUG}_{LOCKED_LEVEL}"
        gloss_factory, qa_call, red_fn, process, model = llm_callables(ctx, article_id)
        report["model_used"] = {"process": process, "model": model, "latest_rule": "検証用ではなくProduction同一route(B1_SUPPORT)。評価用途ではない"}
        report["requalify"] = requalify(kp_dir, by=a.by, text=text, gloss_factory=gloss_factory, qa_call_fn=qa_call, redundancy_fn=red_fn, article_id=article_id,
                                        process=process, out_dir=os.path.join(kp_dir, "requalify_take_offense"))
        report["spent_after_requalify_jpy"] = spend.used()
        # 3) confirm
        report["confirm"] = confirm(run_dir, kp_dir, by=a.by)
        # 4) 再finalize・assets install・kp_b1b来歴付替え -> 再生成(kp_expl_b1b -> kp_part1_b1b)
        report["kp_prepare"] = kp_prepare(R, ctx, text)
        with PartialRegen(R, old_kp_items, old_expl, old_part1) as pr:
            rg = regen_sequence(R, ctx)
        report["partial_regen"] = pr.log
        report["regen"] = rg["log"]
        report["part2_ready"] = part2_ready_check(R, ctx)
        report["spent_total_jpy"] = spend.used()
        # 5) 事後検査
        rec = cc.live_user_record(kp_dir)
        if rec is None:
            raise ToolRefused("再確定後のliveレコードがありません")
        it1 = [i for i in rec["items"] if i["candidate_id"] == CAND_ID]
        if len(it1) != 1 or it1[0]["used_form"] != NEW_FORM or it1[0]["display_phrase"] != OLD_FORM or it1[0]["key_phrase"] != NEW_FORM or it1[0].get("slot") != "kp":
            raise ToolRefused(f"再確定後の{CAND_ID}が想定外: {it1}")
        if _snapshot_other_items(rec) != other_before:
            raise ToolRefused("他の確定項目(KP2・3、追加解説)が変わりました")
        kp_art = json.load(open(rv.paths(kp_dir)["kp"], encoding="utf-8"))
        report["kp_artifact_rank1"] = {k: next(i for i in kp_art["items"] if i["rank"] == 1).get(k) for k in ("used_form", "key_phrase", "display_phrase", "japanese_gloss", "source_span")}
        frozen_after = {f: (A._sha_bytes(A._read_bytes(os.path.join(run_dir, f))) if os.path.exists(os.path.join(run_dir, f)) else None) for f in frozen_before}
        new_expl = json.load(open(os.path.join(kp_dir, "kp_explanations.json"), encoding="utf-8"))
        new_part1 = json.load(open(R._part1_path(ctx, LOCKED_LEVEL), encoding="utf-8"))
        ret = {"kp_expl_ranks_2_3_identical": all(new_expl["items"][k] == old_expl["items"][k] for k in ("2", "3")),
               "kp_expl_rank1_status_ok": new_expl["items"]["1"].get("status") == "OK",      # 解説文が旧と同一になることもある(LLMが同じ文を返す)ため『変わった』は要求しない
               "kp_expl_rank1_regenerated_in_this_run": bool((new_expl.get("audit") or {}).get("partial_regeneration")) and (new_expl.get("audit") or {}).get("calls") is not None,
               "part1_rows_2_5_identical": new_part1["items"][1:] == old_part1["items"][1:],
               "part1_row1_changed": new_part1["items"][0] != old_part1["items"][0], "part1_row1_phrase": new_part1["items"][0].get("phrase")}
        report["retained_items_check"] = ret
        if not (ret["kp_expl_ranks_2_3_identical"] and ret["part1_rows_2_5_identical"] and ret["kp_expl_rank1_status_ok"] and ret["kp_expl_rank1_regenerated_in_this_run"] and ret["part1_row1_changed"] and ret["part1_row1_phrase"] == NEW_FORM):
            raise ToolRefused(f"保持すべき項目が変わった、または変更すべき項目が変わっていません: {ret}")
        report["grammar_frozen_unchanged"] = frozen_before == frozen_after
        report["grammar_frozen_sha"] = {"before": frozen_before, "after": frozen_after}
        after_prov = R._prov(ctx).data
        report["provenance_changes"] = sorted(n for n in set(before_prov["downstream_stages"]) | set(after_prov["downstream_stages"])
                                              if {k: v for k, v in (before_prov["downstream_stages"].get(n) or {}).items() if k != "rebinds"}
                                              != {k: v for k, v in (after_prov["downstream_stages"].get(n) or {}).items() if k != "rebinds"})
        report["downstream_stale"] = after_prov["downstream_stale"]
        report["tts_stale"] = {n: (n in after_prov["downstream_stale"]) for n in ("tts_b1b",)}
        if "tts_b1b" not in after_prov["downstream_stale"]:
            raise ToolRefused("tts_b1bがstaleになっていません(kp_expl_b1b再生成で子孫がstale化されるはず)。fail-closedが効いていません")
        # TTS前に通る見込みの検査(API 0): ハイライト解決
        with A._quiet():
            hl = R._resolve_highlights_or_stop(ctx, "tool:take_offense", (LOCKED_LEVEL,))
        report["highlight_resolution_b1b"] = {"returned": type(hl).__name__}
        with A._quiet():
            report["tts_regeneration_plan"] = A.tts_regeneration_plan(R, ctx)
        plan_b1b = set(report["tts_regeneration_plan"]["b1b"])
        if "kp1_english" not in plan_b1b or plan_b1b & {"kp2_english", "kp3_english", "kp2_explanation", "kp3_explanation"}:
            raise ToolRefused(f"04Cで再生成が必要なKP segmentが想定(kp1_englishを含み、kp2・kp3を含まない)と異なります: {sorted(plan_b1b)}")
        after_manifest = A.tree_manifest(run_dir)
        changed = sorted(r for r in set(before_manifest) | set(after_manifest) if before_manifest.get(r) != after_manifest.get(r))
        outside = [r for r in changed if not A._in_mutable(r) and r != "cost_log.jsonl"]     # cost_log.jsonlはLLM費用の追記(退避・復元の対象外=費用記録を消さない)
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
    except BaseException as e:   # noqa: BLE001  失敗=全復元(費用は戻らない)
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
