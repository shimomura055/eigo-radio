# -*- coding: utf-8 -*-
"""使い捨てtool(HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01 委任_02r、Fable判断M4)。

目的: Family Y「夫が妻の姓を選ぶとき」Standard(run_02 a2)で、ユーザーが原文§2で指示した『`old-fashioned about it` -> `old-fashioned`』の1点だけを、
Productionの全ゲートを再適用したうえで候補docに反映し、ユーザー選定(旧readable_a2.txt)のその他の選定を維持して確定レコードへ記録する。
**汎用opではない**: run_02 / level=a2 / 旧句`old-fashioned about it` / 新句`old-fashioned` に固定(任意文字列・他記事・他levelは拒否)。
Production関数を再利用し、独自の検査規則は作らない(新しい受理面を作らない)。

段階:
  requalify  : 候補の差替え(PENDING_REVIEW中のみ)。全ゲート再適用 -> 全てPASSなら候補doc・review.candidates_sha256を更新(review_lock配下)。
               ゲート = kc.validate_canonicalization_item(全文選定用引数・左端guard) / 本文連続span / cmu.canonicalized_check / 記号検出 / Human NG /
                        ft._recompute_item_fields / word_count・kind / er125.force_gloss_realign(gloss整合) / er125.qa_rejudge(QA 12項目すべてPASS) /
                        候補全体Redundancy QAの再実行(redundant_with再計算) / rv.presentation_blockers(提示集合の唯一の定義)が空
  confirm    : 旧readable(restore)のpayloadからrank5のtermだけを差替え(kind/gloss/candidates_shaも新docに合わせる)、cmd_from_formと同じ内部関数で確定。
               attestation="user_instruction_transcription"(フォーム送信の再現ではなくユーザー原文の転記)、actor=ACTOR_USER。由来を記録。
               capは再計算しない(Y Stdの単語capとの衝突を、フォームdata再生成ではなく確定集合の直接記録で回避。Fable判断M3)。
  --dry-run  : 前提条件と決定論ゲート(LLMなし)だけ検査し、何も書かない。実行は委任_03(本委任ではdry-run test fixtureまで)。

実行(委任_03): .venv\\Scripts\\python.exe docs\\research\\HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01\\tools\\apply_user_decision_surname_choice_01.py
        requalify|confirm --run <run_02 dir> --user-ref docs/pm/delegation_log/2026-10-29_HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01_USER.md --by <名> [--dry-run]
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from typing import Callable, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import er003_key_words_canonicalization as kc  # noqa: E402
import er003_v1_n3_01_scaffold_generate as sc  # noqa: E402
import er105_kp_fulltext_selector_01 as ft  # noqa: E402
import er108_kp_cmu_lexicon_gate_01 as cmu  # noqa: E402
import er119_kp_backfill_01 as bf  # noqa: E402
import er119_kp_human_review_01 as rv  # noqa: E402
import er125_kp_rescue_production_01 as er125  # noqa: E402

# ---- 固定条件(使い捨て: これ以外は拒否) ------------------------------------------------------------------------------
LOCKED_SLUG, LOCKED_FAMILY, LOCKED_LEVEL = "surname_choice", "y", "a2"
OLD_FORM, NEW_FORM = "old-fashioned about it", "old-fashioned"
USER_REF_TAIL = "2026-10-29_HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01_USER.md"
USER_SPEC_REF = "§2 変更後: `old-fashioned`(原文 docs/pm/delegation_log/" + USER_REF_TAIL + " の『今回の記事への適用』節 / §6 Standard)"
ATTESTATION = "user_instruction_transcription"
TOOL_ID = "apply_user_decision_surname_choice_01"


class ToolRefused(Exception):
    pass


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _find_cand(cands: dict) -> dict:
    hits = [c for c in cands.get("candidates") or [] if c.get("used_form") == OLD_FORM]
    if len(hits) != 1:
        raise ToolRefused(f"旧句{OLD_FORM!r}を持つ候補が{len(hits)}件です(1件のみ許可)")
    return hits[0]


def check_preconditions(kp_dir: str, user_ref: str) -> dict:
    """固定条件・状態の検査(何も書かない)。returns {"review","cands","cand"}。"""
    if not (user_ref or "").endswith(USER_REF_TAIL) or not os.path.exists(user_ref):
        raise ToolRefused(f"--user-ref は {USER_REF_TAIL} の実在pathのみ(ユーザー原文の転記tool)")
    review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
    if review is None or cands is None:
        raise ToolRefused("候補/reviewがありません")
    ak = review.get("article_key") or {}
    if (ak.get("slug"), (ak.get("family") or "").lower(), review.get("level")) != (LOCKED_SLUG, LOCKED_FAMILY, LOCKED_LEVEL):
        raise ToolRefused(f"対象外のrunです(固定: slug={LOCKED_SLUG}, family={LOCKED_FAMILY}, level={LOCKED_LEVEL}。実際: {ak}, level={review.get('level')})")
    if review["status"] != rv.ST_PENDING:
        raise ToolRefused(f"status={review['status']}。差替えはPENDING_REVIEWの間だけ(確定済みは対象外)")
    import er128_kp_confirmed_content_01 as cc
    if cc.load_record(kp_dir) is not None:
        raise ToolRefused("ユーザー確定レコードが既にあります(差替え不可)")
    if review["candidates_sha256"] != cands["candidates_sha256"]:
        raise ToolRefused("reviewと候補docのcandidates_sha256が不一致")
    return {"review": review, "cands": cands, "cand": _find_cand(cands)}


def deterministic_gates(cand: dict, text: str, ng_entries: list) -> dict:
    """LLMを使わない決定論ゲート(Production関数の再利用)。returns {"item": 差替え後item(gloss/QA未更新), "role_ok": frozenset}。失敗=ToolRefused。"""
    it = copy.deepcopy(cand["item"])
    role_ok = frozenset((it.get("person_role_repair") or {}).get("role_ok_poss") or [])
    span, display, sentence = it.get("source_span") or "", it.get("display_phrase") or "", it.get("source_sentence") or ""
    if re.sub(r"[^a-z0-9' -]+", "", NEW_FORM.lower()) not in re.sub(r"[^a-z0-9' -]+", "", sentence.lower()):
        raise ToolRefused(f"新句{NEW_FORM!r}が出典文に連続して存在しません: {sentence!r}")
    it["key_phrase"], it["used_form"] = NEW_FORM, NEW_FORM
    ft._recompute_item_fields(it, display, NEW_FORM, role_ok)
    v = kc.validate_canonicalization_item(NEW_FORM, display, span, it.get("normalization_reason"), original_span=span,
                                          allow_inflection_normalization=True, role_ok_poss=role_ok)
    if not v["ok"]:
        raise ToolRefused("validate_canonicalization_item不合格: " + " / ".join(v["reasons"]))
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
    return {"item": it, "role_ok": role_ok, "similar_to_ng": (mt == "similar") or (mo == "similar")}


def requalify(kp_dir: str, *, user_ref: str, by: str, text: str, gloss_factory: Optional[Callable], qa_call_fn: Optional[Callable],
              redundancy_fn: Optional[Callable], article_id: str, process: str, dry_run: bool = False, out_dir: Optional[str] = None) -> dict:
    """候補`old-fashioned about it` -> `old-fashioned` の差替え。全ゲートPASSのときだけ候補docを更新する(1つでもFAILなら何も書かず例外=ユーザー意図と不一致としてFableへ報告)。"""
    pre = check_preconditions(kp_dir, user_ref)
    review, cands, cand = pre["review"], pre["cands"], pre["cand"]
    ak = review.get("article_key") or {}
    ng_ent = rv.ng_entries_of(review, ak.get("family"), ak.get("slug"), review["level"])
    dg = deterministic_gates(cand, text, ng_ent)
    report = {"tool": TOOL_ID, "dry_run": dry_run, "candidate_id": cand["candidate_id"], "from": OLD_FORM, "to": NEW_FORM,
              "gates": {"preconditions": "PASS", "validate_canonicalization_item": "PASS", "span_in_sentence": "PASS", "cmu": "PASS", "symbol": "PASS", "human_ng": "PASS"}}
    if dry_run:
        report["note"] = "dry-run: 決定論ゲートまで検査(gloss整合/QA再判定/Redundancy QAは未実行)。何も書いていません"
        return report
    if gloss_factory is None or qa_call_fn is None or redundancy_fn is None:
        raise ToolRefused("gloss_factory / qa_call_fn / redundancy_fn が必要です(全ゲートを省略しません)")
    out_dir = out_dir or os.path.join(kp_dir, "requalify_old_fashioned")
    os.makedirs(out_dir, exist_ok=True)
    item2, role_ok, rank = dg["item"], dg["role_ok"], dg["item"].get("rank", cand["ai_rank"])
    # gloss再整合(承認済みgloss規則・Gate。対象を強制指定)
    ga_res = er125.force_gloss_realign({"items": [item2]}, [rank], text, gloss_factory, out_dir=out_dir, article_id=article_id)
    if ga_res["unresolved_ranks"]:
        raise ToolRefused(f"gloss整合が未解決(rank={ga_res['unresolved_ranks']})。ユーザー意図と不一致の可能性=Fableへ報告")
    item2 = ga_res["merged"]["items"][0]
    report["gates"]["gloss_realign"] = ga_res["status"]
    # QA 12項目の再判定(承認済みfulltext prompt/schema無変更)。全項目PASSのときだけ
    q = er125.qa_rejudge(text, [item2], qa_call_fn, {rank: role_ok})["by_rank"].get(rank) or {"status": er125.QA_NOT_REJUDGED, "qa": {}}
    report["gates"]["qa_rejudge"] = q["status"]
    report["qa_fields"] = q.get("qa")
    if q["status"] != er125.QA_REJUDGED_PASS or any(v != "PASS" for v in (q.get("qa") or {}).values()) or not q.get("qa"):
        raise ToolRefused(f"QA再判定がPASSではありません(status={q['status']}, FAIL項目={[k for k, v in (q.get('qa') or {}).items() if v != 'PASS']})。"
                          "『old-fashioned』は提示可能な候補にできません=ユーザー決定の実現不能。Fableへ報告(再選定はしません)")
    item2["qa"], item2["qa_overall_status"] = dict(q["qa"]), "PASS"
    # 候補の更新(候補IDは不変=selection_phraseを保持。由来を記録)
    new = copy.deepcopy(cand)
    new.update(used_form=NEW_FORM, japanese_gloss=item2.get("japanese_gloss"), word_count=ft.count_words(NEW_FORM), item=item2)
    new["kind"] = bf.kind_of_phrase(NEW_FORM)
    new["flags"] = {"qa_fail": False, "gloss_hr_pending": False, "similar_to_ng": bool(dg["similar_to_ng"]), "redundant_with": []}
    new["gates"] = dict(new.get("gates") or {}, canonicalization="PASS", gloss="ALIGNED")
    new["auto_eligible"] = not new["flags"]["similar_to_ng"]
    new["requalified"] = {"tool": TOOL_ID, "from": OLD_FORM, "to": NEW_FORM, "user_ref": user_ref, "user_spec": USER_SPEC_REF, "by": by,
                          "old_item_sha256": hashlib.sha256(json.dumps(cand["item"], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
                          "old_kind": cand.get("kind"), "new_kind": new["kind"], "old_gloss": cand.get("japanese_gloss")}
    blockers = rv.presentation_blockers(new)
    if blockers:
        raise ToolRefused("差替え後の候補が提示集合の条件を満たしません: " + " / ".join(b[1] for b in blockers))
    doc = copy.deepcopy(cands)
    doc["candidates"] = [new if c["candidate_id"] == cand["candidate_id"] else c for c in doc["candidates"]]
    # redundant_with再計算(候補全体Redundancy QAを生成時と同じ手順で再実行。旧結果は由来として保存)
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
    doc["requalify_provenance"] = {"tool": TOOL_ID, "user_ref": user_ref, "candidate_id": cand["candidate_id"], "from": OLD_FORM, "to": NEW_FORM,
                                   "previous_candidates_sha256": cands["candidates_sha256"], "previous_redundancy_qa": cands.get("redundancy_qa"),
                                   "presentable_filter_version": rv.PRESENTABLE_FILTER_VERSION}
    with rv.review_lock(kp_dir, rv.KIND_KP, by):
        review = rv.load_review(kp_dir)
        if review["status"] != rv.ST_PENDING or review["candidates_sha256"] != cands["candidates_sha256"]:
            raise ToolRefused("実行中にreview/候補が変更されました(再実行してください)")
        saved = rv.save_candidates(kp_dir, doc)
        review["candidates_sha256"] = saved["candidates_sha256"]
        review["last_human_op_at"] = rv._now()
        rv._event(review, "requalify_user_decision", by, {"candidate_id": cand["candidate_id"], "from": OLD_FORM, "to": NEW_FORM, "user_ref": user_ref,
                                                         "user_spec": USER_SPEC_REF, "old_candidates_sha256": cands["candidates_sha256"]})
        rv.save_review(kp_dir, review, expected_revision=review["revision"])
        rv.invalidate_gloss_snapshot(kp_dir)
    report.update(candidates_sha256=saved["candidates_sha256"], new_kind=new["kind"], new_gloss=new["japanese_gloss"], applied=True)
    return report


def patched_payload(restored: dict, kp_dir: str) -> dict:
    """旧readableから復元したpayloadの、`old-fashioned about it`の項目だけを新候補(term/kind/gloss/status)へ差替え、candidates_shaを新docに合わせる。
    他の選定・順序・文法・コメントは1文字も変えない。differenceは差替え1点のみであることを呼出側で検証する。"""
    cands = rv.load_candidates(kp_dir)
    cand = next(c for c in cands["candidates"] if c.get("requalified") and c["used_form"] == NEW_FORM)
    out = copy.deepcopy(restored)
    n = 0
    for grp in ("key_phrase", "extra_explanation", "meaning_display"):
        for rec in out["selection"][grp]:
            if rec["candidate_id"] == cand["candidate_id"]:
                rec["term"], rec["kind"], rec["ja_gloss"], rec["ja_gloss_status"] = NEW_FORM, cand["kind"], cand["japanese_gloss"], "official"
                n += 1
    if n != 1:
        raise ToolRefused(f"旧readable内の対象項目が{n}件です(1件のみ許可)")
    out["article"]["candidates_sha256"] = cands["candidates_sha256"]
    return out


def diff_payloads(a: dict, b: dict) -> list:
    """差分の列挙(candidates_sha256と対象項目のterm/kind/ja_gloss/ja_gloss_status以外に差があればそれも返す=検証用)。"""
    diffs = []
    def walk(x, y, path=""):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in sorted(set(x) | set(y)):
                walk(x.get(k), y.get(k), f"{path}/{k}")
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            for i, (p, q) in enumerate(zip(x, y)):
                walk(p, q, f"{path}[{i}]")
        elif x != y:
            diffs.append(path)
    walk(a, b)
    return diffs


def confirm(run: str, *, kp_dir: str, readable_path: str, user_ref: str, by: str, dry_run: bool = False, data_dir: Optional[str] = None) -> dict:
    """旧readable_a2.txtを復元 -> 差替え1点 -> cmd_from_form(同じ内部関数・同じ検査)で確定。確定レコードに由来を記録する。"""
    import er128_form_readable_restore_01 as fr
    import er128_kp_confirmed_content_01 as cc
    check_preconditions_for_confirm(kp_dir, user_ref)
    data_dir = data_dir or fr.DEFAULT_DATA_DIR
    raw, restored, notes = fr.load_restore(readable_path, data_dir)
    payload = patched_payload(restored, kp_dir)
    allowed = {"/article/candidates_sha256"}
    extra = [d for d in diff_payloads(restored, payload) if d not in allowed and not re.search(r"/selection/(key_phrase|extra_explanation|meaning_display)\[\d+\]/(term|kind|ja_gloss|ja_gloss_status)$", d)]
    if extra:
        raise ToolRefused("差替え対象以外の差分が検出されました(他の選定を変えない): " + str(extra))
    d_all = diff_payloads(restored, payload)
    prov = {"tool": TOOL_ID, "readable_sha256": _sha_bytes(raw), "readable_path": readable_path.replace("\\", "/"),
            "old_collation_code": (restored.get("restore_meta") or {}).get("collation_code"), "old_candidates_sha256": restored["article"]["candidates_sha256"],
            "new_candidates_sha256": payload["article"]["candidates_sha256"], "differences": d_all, "user_spec": USER_SPEC_REF,
            "user_ref": user_ref, "form_data_regenerated": False, "cap_recomputed": False}
    if dry_run:
        return {"dry_run": True, "differences": d_all, "provenance": prov, "summary": fr.summarize(payload, notes)}
    fd, tmp = tempfile.mkstemp(suffix=".json", prefix="user_decision_payload_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(fr.payload_bytes(payload))
        res = cc.cmd_from_form(run, LOCKED_LEVEL, tmp, by, user_ref, actor=cc.ACTOR_USER, attestation=ATTESTATION, origin_extra=prov)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    return {"confirmed": res, "provenance": prov}


def check_preconditions_for_confirm(kp_dir: str, user_ref: str) -> None:
    review, cands = rv.load_review(kp_dir), rv.load_candidates(kp_dir)
    if not review or not cands:
        raise ToolRefused("候補/reviewがありません")
    ak = review.get("article_key") or {}
    if (ak.get("slug"), (ak.get("family") or "").lower(), review.get("level")) != (LOCKED_SLUG, LOCKED_FAMILY, LOCKED_LEVEL):
        raise ToolRefused("対象外のrunです")
    if not (user_ref or "").endswith(USER_REF_TAIL) or not os.path.exists(user_ref):
        raise ToolRefused(f"--user-ref は {USER_REF_TAIL} の実在pathのみ")
    if not any(c.get("requalified") for c in cands["candidates"]):
        raise ToolRefused("先に requalify を実行してください(候補が差替え済みではありません)")


def _kp_dir(run: str) -> str:
    import er128_kp_confirmed_content_01 as cc
    return cc._kp_dir_for(run, LOCKED_LEVEL)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("requalify", "confirm"))
    ap.add_argument("--run", required=True)
    ap.add_argument("--user-ref", required=True)
    ap.add_argument("--by", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--readable", default=None, help="confirm: 旧readable_a2.txt(ユーザー送信済み。AIF1コード付き)")
    a = ap.parse_args(argv)
    try:
        kp_dir = _kp_dir(a.run)
        if a.cmd == "requalify":
            import er003_key_words_gloss_alignment as ga
            import er003_v1_n3_01_scaffold_generate as sc_
            import er006_model_routing_contract_01 as routing
            import er005_cost_logger as cl
            review = rv.load_review(kp_dir)
            text = _load_text(a.run, review)
            model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)

            def gloss_factory(msg):
                return ga.make_alignment_fn(msg, model=model)

            def qa_call(msg):
                with cl.logging_context("surname_choice_a2", "kp_requalify_qa_rejudge"):
                    return kc.make_canonicalization_fn(msg, model=model, schema=kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT)()
            out = requalify(kp_dir, user_ref=a.user_ref, by=a.by, text=text, gloss_factory=gloss_factory, qa_call_fn=qa_call,
                            redundancy_fn=sc_.run_key_phrase_redundancy_qa, article_id="family_y_surname_choice_a2", process="A2_SUPPORT", dry_run=a.dry_run)
        else:
            if not a.readable:
                raise ToolRefused("confirm には --readable が必要です")
            out = confirm(a.run, kp_dir=kp_dir, readable_path=a.readable, user_ref=a.user_ref, by=a.by, dry_run=a.dry_run)
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0
    except ToolRefused as e:
        print(f"[{TOOL_ID}][REFUSED] {e}", file=sys.stderr)
        return 2


def _load_text(run: str, review: dict) -> str:
    """KP候補生成に使われた本文(Y runnerと同じ `ys.canonical_body(<run>/translate/a2.md)`)。reviewのtext_sha256と一致しなければ停止(推測しない)。"""
    import er121_family_y_structure_01 as ys
    p = os.path.join(run, "translate", f"{LOCKED_LEVEL}.md")
    try:
        t = ys.canonical_body(open(p, encoding="utf-8").read())
    except OSError as e:
        raise ToolRefused(f"本文を読めません: {p} ({e})") from e
    if rv.sha256_text(t) != review["text_sha256"]:
        raise ToolRefused("reviewのtext_sha256と本文が一致しません(推測で別の本文を使いません)")
    return t


if __name__ == "__main__":
    sys.exit(main())
