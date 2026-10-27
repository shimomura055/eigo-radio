# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03 兼 PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03 兼 GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02:
Part 2「Grammar & Sentence Structure」のHuman Review(er119共通核に kind="grammar" で接続)。決定論(API 0)。

- 状態/操作の実体はここ。署名・NG registry・排他lock・不在宣言の読取は er119_kp_human_review_01(共通核)を使う:
    署名      = rv.selection_signature(kind=grammar) -> er120.grammar_selection_signature(単一関数。schema別式。突合test: TestSignatureSingleSource)
    NG        = rv.store_*(family+slug+level[+kind=grammar]) の共有registry(run dirに依存しない=copy-runが自動引継ぎ)・書込は排他lock
    不在宣言  = rv.read_mode_declaration(単一読取点。dict形はer120.normalize_modeが受ける形)。環境変数/引数/hooksからautoにならない
    status    = REVIEWED / UNREVIEWED_AUTO_ADOPTED / NO_CANDIDATE_UNREVIEWED だけが下流を進める。
                PENDING_REVIEW / RESELECT_EXHAUSTED / REEXTRACT_REQUESTED / RESELECTION_REQUESTED / STALE は下流fail-closed
- LLM呼出は注入関数のみ(Step A'' の抽出とreextractのみ)。Step B(解説)は er120_part2_wiring_01.pregen_stage だけが呼ぶ(Top1/Top2の2候補分の事前生成)。CLI操作(Human)はAPI 0。
- ファイル(study_dir): grammar_candidates.json / grammar_explanations.json(事前生成物) / grammar_human_review.json / grammar_human_review.lock / grammar_human_review_request.md /
  grammar_translation_issue.json・grammar_translation_ack.json(Part 1訳との食い違いISSUEとユーザー了承)
- GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02: levelは全APIの必須引数('b1b'=Advanced / 'a2'=Standard)。`b1b`の暗黙既定値(旧モジュール定数)は撤去。review v2は最大1件選択(2026-10-27改訂: 旧2件=撤去)・0件可・提示はTop1/Top2のみ
  (契約=docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/SCHEMA_CONTRACT_01.md)。v1 reviewは読取互換(確定済みv1は書換えない)。
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Callable, Optional

import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g

KIND = rv.KIND_GRAMMAR
CLI = "py er119_kp_human_review_cli_01.py"
TRANSLATION_ISSUE_FILENAME = "grammar_translation_issue.json"
TRANSLATION_ACK_FILENAME = "grammar_translation_ack.json"


def paths(study_dir: str) -> dict:
    p = dict(rv.paths(study_dir, KIND))
    p["explanations"] = f"{study_dir}/{g.EXPLANATIONS_FILENAME}"
    p["translation_issue"] = f"{study_dir}/{TRANSLATION_ISSUE_FILENAME}"
    p["translation_ack"] = f"{study_dir}/{TRANSLATION_ACK_FILENAME}"
    return p


def _atomic_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def load_candidates(study_dir: str) -> Optional[dict]:
    return g.load_json(paths(study_dir)["candidates"])


def load_review(study_dir: str) -> Optional[dict]:
    return rv.load_review(study_dir, KIND)


def load_explanations(study_dir: str) -> Optional[dict]:
    return g.load_json(paths(study_dir)["explanations"])


def save_candidates_doc(study_dir: str, doc: dict) -> dict:
    """候補docを保存(er120形式のまま=schema/candidates_sha256を書き換えない)。直前のdocがあればSUPERSEDEDへ退避する(消さない)。"""
    pth = paths(study_dir)
    cur = g.load_json(pth["candidates"])
    if cur is not None and cur.get("candidates_sha256") != doc.get("candidates_sha256"):
        rv.archive_if_exists(pth["candidates"], "SUPERSEDED")
    _atomic_json(pth["candidates"], doc)
    _atomic_json(f"{study_dir}/grammar_candidates/round_{doc.get('round', 1)}_{doc['candidates_sha256'][:10]}.json", doc)
    return doc


def _ng_entry(c: dict, reason: str, by: str, source: str) -> dict:
    e = g.ng_entry_from_candidate(c, reason=reason, by=by, source=source)
    e["sentence_key"] = g._norm_sentence(c["sentence"])
    return e


def _event(review: dict, event: str, by: str, detail: Optional[dict] = None) -> None:
    review.setdefault("history", []).append({"at": rv._now(), "event": event, "by": by, "detail": detail or {}})


def _level_of(review: dict, doc: Optional[dict] = None) -> str:
    """共有NG registry等のlevelキー('b1b'|'a2')。reviewのarticle_key.level(生成時に記録)を使い、候補docのlevel欄と一致することを確認する(不一致=fail-closed)。
    欠落時に既定値へ落とさない。"""
    lv = (review.get("article_key") or {}).get("level")
    g.level_name(lv)
    if doc is not None:
        g.check_doc_level(doc, lv)
    return lv


def new_pending_review(doc: dict, *, article_key: dict, prev: Optional[dict] = None, reason: str = "candidates_generated") -> dict:
    """候補docに対する未確定review(**v2**)。docが尽きていればRESELECT_EXHAUSTED(自動確定しない)、それ以外はPENDING_REVIEW。
    prev(前のreview)のhistory・reselect_count・last_human_op_at・NGを引き継ぐ(Human操作の記録を失わない)。"""
    g.check_doc_level(doc, article_key.get("level"))
    status = rv.ST_RESELECT_EXHAUSTED if doc.get("exhausted") else rv.ST_PENDING
    r = {"schema": g.SCHEMA_REVIEW_V2, "kind": KIND, "level": doc["level"], "text_sha256": doc["text_sha256"],
         "candidates_sha256": doc["candidates_sha256"], "round": doc.get("round", 1), "status": status, "revision": 0,
         "article_key": article_key, "mode_declaration": None, "selection": {}, "accept_ai_default": False,
         "accepted_candidates_sha256": None, "verdicts": {}, "ng": list(doc.get("ng", [])),
         "reselect_count": doc.get("reselect_count", 0), "reextract_count": doc.get("reextract_count", 0), "decision": None,
         "last_human_op_at": (prev or {}).get("last_human_op_at"), "history": list((prev or {}).get("history") or []),
         "selection_signature": None}
    _event(r, reason, "runner", {"round": r["round"], "candidates_sha256": r["candidates_sha256"], "status": status})
    return r


def _replace_review(study_dir: str, new_review: dict, old: Optional[dict]) -> dict:
    """旧reviewがあればSUPERSEDEDへ退避して、版番号を引き継いで新reviewを書く(呼出側がreview_lockを保持)。"""
    pth = paths(study_dir)
    if old is not None:
        new_review["revision"] = old["revision"]
        rv.archive_if_exists(pth["review"], "SUPERSEDED")
        # archive後は現ファイルが無いので新規作成扱い(版番号は引き継ぐ)
        out = rv.save_review(study_dir, new_review, expected_revision=None, kind=KIND)
        out["revision"] = old["revision"] + 1
        _atomic_json(pth["review"], out)
        return out
    return rv.save_review(study_dir, new_review, expected_revision=None, kind=KIND)


def _finalized_record(doc: dict, sel: dict, *, review: dict, decision: Optional[dict], by: str) -> dict:
    """確定record。review(置換元)がv1ならv1形(単一選定。確定済みv1の進行中run用)、v2ならv2形(最大1件)。"""
    if review.get("schema") == g.SCHEMA_REVIEW:
        sel1 = dict(sel, candidate=(sel["selected"][0] if sel.get("selected") else sel.get("candidate")))
        rec = g.finalize_review_record(doc, sel1, decision=decision, by=by, prior_history=review.get("history"))
        rec["decision"] = ({k: decision.get(k) for k in ("choice", "candidates_sha256", "reason", "by", "accept_ai")} if decision else None)
    else:
        rec = g.finalize_review_record_v2(doc, sel, decision=decision, by=by, prior_history=review.get("history"))
    for k in ("article_key", "round", "last_human_op_at", "revision"):
        rec[k] = review.get(k)
    return rec


def registry_ng(family: str, slug: str, level: str) -> list:
    g.level_name(level)
    return rv.store_load_ng(family, slug, level, KIND)


def pending_summary(study_dir: str, review: dict) -> dict:
    return {"kind": "grammar", "level": review.get("level"), "dir": study_dir, "request_md": paths(study_dir)["request"],
            "status": review["status"], "candidates_sha256": review["candidates_sha256"]}


def _rebind_grammar_text(study_dir: str, state: dict, doc: dict, review: dict, paragraphs: list, label: str) -> None:
    """M8(文法): 本文が変わったが、ユーザー確定済みの文法の選定文が新本文の同じ段落に逐語で存在し candidate_id も一致する場合、候補doc.text_sha256・
    extract_signature とreview.text_sha256(署名)をAPI 0で更新する。存在しなければISSUE(Part2Stale。確定内容は変更しない)。"""
    ids = {it.get("id") for it in state["sidecar"].get("items") or []}
    conf = [c for c in doc.get("candidates") or [] if c.get("candidate_id") in ids]
    ok = bool(conf) and all(g.verify_single_span({"body": paragraphs}, c["para"], c["sentence"]) and g.candidate_id(c["para"], c["sentence"]) == c["candidate_id"] for c in conf)
    if not ok or review is None:
        cc = rv._cc()
        cc._write_issue(state["kp_dir"], kind="CONFIRMED_CONTENT_ISSUE",
                        summary="本文が変わり、ユーザー確定済みの文法(Part 2)の選定文が新本文に逐語で残っていません。確定内容を黙って破棄/再抽出しません。",
                        diffs=[{"candidate_id": c.get("candidate_id"), "field": "grammar.sentence", "confirmed": c.get("sentence"), "observed": "(新本文に逐語で存在しない)",
                                "where": "text_sha256変更"} for c in conf] or [{"candidate_id": None, "field": "grammar", "confirmed": sorted(ids), "observed": "(確定した文法が候補docに無い)", "where": "text_sha256変更"}],
                        next_steps=[f"{cc._cli(state['kp_dir'], 'revoke')} --level {state['level']} --by <名> --user-ref <ユーザー発言> --reason '本文変更に伴う選び直し'"],
                        proposal=["選定文を変更した場合は新しい文で文法を選び直す(revoke→再選択)か、本文の当該文を元に戻してください"])
        raise g.Part2Stale("本文が変わり、ユーザー確定済みの文法の選定文が新本文に逐語で残っていません(CONFIRMED_CONTENT_ISSUE。再確認が必要)")
    pth = paths(study_dir)
    with rv.review_lock(study_dir, KIND, "er128"):
        old_t, old_sig = doc.get("text_sha256"), review.get("selection_signature")
        rv.archive_if_exists(pth["candidates"], "REBOUND_SUPERSEDED")
        doc2 = dict(doc)
        doc2["text_sha256"] = g.text_sha256(paragraphs)
        doc2["extract_signature"] = g.extract_signature(paragraphs, label)
        _atomic_json(pth["candidates"], doc2)
        review = load_review(study_dir)
        review["text_sha256"] = doc2["text_sha256"]
        _event(review, "rebind_text", "er128", {"old_text_sha256": old_t, "new_text_sha256": doc2["text_sha256"], "old_selection_signature": old_sig,
                                                 "note": "確定した選定文が新本文に逐語で存在(API 0)"})
        rv.save_review(study_dir, review, expected_revision=review["revision"], kind=KIND)


# ============================================================
# 事前生成物との接続: 検証 / 依頼書(Top1/Top2の文法名+解説全文) / stale表示
# ============================================================
def explanations_state(study_dir: str, doc: dict, *, level: str) -> tuple:
    """(ready: bool, ex|None, reason)。事前生成物が完全で整合していればready。例外を出さない判定用(依頼書を書くか否か等)。"""
    ex = load_explanations(study_dir)
    try:
        g.validate_explanations(ex, doc, level=level)
    except g.Part2Stale as e:
        return False, ex, str(e)
    return True, ex, ""


def require_explanations(study_dir: str, doc: dict, *, level: str) -> dict:
    """HR/フォーム/grammar-showが解説を見せる入口。不完全・不整合ならデータを出さずエラー(Opus O-9。candidates_available扱いにしない)。part2_failed.jsonがあれば明示。"""
    ex = load_explanations(study_dir)
    failed = g.load_json(f"{study_dir}/{g.FAILED_FILENAME}")
    if failed and str(failed.get("stage", "")).startswith("part2_expl"):
        raise rv.KpReviewError(f"文法解説の事前生成が失敗しています(part2_failed.json: {failed.get('error')})。制作を同じコマンドで再実行して未生成分を作ってください")
    try:
        return g.validate_explanations(ex, doc, level=level, next_command="制作コマンドを同じまま再実行(未生成の文法解説だけを事前生成します。提示はTop1/Top2のみ)")
    except g.Part2Stale as e:
        raise rv.KpReviewError(str(e)) from e


def _stale_request_md(doc: dict, review: dict, why: str) -> str:
    return ("# Part 2 文法解説 Human Review 依頼 — 古い/未完成(操作しないでください)\n\n"
            f"- 状態: {review.get('status')} / 理由: {why}\n"
            "- 文法候補が更新された、または解説の事前生成が完了していません。**制作コマンドを同じまま再実行**すると、解説を事前生成して依頼書を作り直します。"
            "この文書の内容では選択しないでください。\n")


def write_request_for_state(study_dir: str, doc: dict, review: dict, *, level: str, run_hint: str) -> str:
    """依頼書を書く。v2で解説の事前生成が完了・整合していれば全候補の解説全文付き、そうでなければ『古い/未完成』を明示(古い依頼書を残さない)。"""
    ready, ex, why = explanations_state(study_dir, doc, level=level)
    text = render_request_md(doc, review, run_hint=run_hint, explanations=ex) if ready else _stale_request_md(doc, review, why)
    _atomic_text(paths(study_dir)["request"], text)
    return text


# ============================================================
# runner側: 候補抽出(Step A'')と待機/自動確定の評価(再実行しても冪等・resumeはAPI 0)
# ============================================================
def ensure_grammar_review(study_dir: str, *, level: str, run_dir: str, family: str, slug: str, paragraphs: list, label: str, run_hint: Optional[str] = None,
                          extract_call_fn: Optional[Callable] = None, client=None, budget_guard: Optional[Callable] = None,
                          force_extract: bool = False) -> dict:
    """候補抽出(または保存済み候補の再利用)→(Human確認 / 明示宣言のAUTO / 適格0件の即確定)。KP候補生成と同じ待機点の前に実行する。
    **この後・待機(rc=4)に入る前に必ず事前生成(wiring.pregen_stage)を通すこと**(解説全文を見せてから選ばせる)。
    returns {"state":"READY"|"PENDING","review":{...},"doc":{...},"pending":{...}|None,"generated":bool}
    - level: 'b1b'|'a2' 必須。候補docのlevel欄と一致しなければfail-closed
    - 保存済み候補が現在の本文・label・Prompt・modelと一致 → Step A'' 0 call(M-7)。共有registryのNGは再適用(変われば新reviewへ)
    - REEXTRACT_REQUESTED(Humanがreextractを選んだ)のときだけ Step A'' を再度呼ぶ(上限1回、再選定合計2回)
    - force_extract=True(--regenerate-stage part2_cand_<level>): 旧候補/reviewをSUPERSEDEDへ退避して再抽出(NGは保持)
    - 未確定のv1 reviewはv2へ置換(履歴を引き継ぐ)。確定済みv1は書換えない(進行中run互換)"""
    g.level_name(level)
    pth = paths(study_dir)
    os.makedirs(study_dir, exist_ok=True)
    article_key = {"family": family, "slug": slug, "level": level}
    run_hint = run_hint or run_dir
    ng = registry_ng(family, slug, level)
    cached, review = load_candidates(study_dir), load_review(study_dir)
    if (cached is None) != (review is None):
        raise rv.KpReviewInconsistent("文法の候補ファイルとreviewの片方だけがあります(手動削除の疑い)。fail-closed。状況をFableへ報告してください")
    g.check_doc_level(cached, level)
    generated = False
    carry = review
    # 確定内容保護(M6/M8): ユーザー確定済みの文法がある場合は再抽出しない。--regenerate-stage part2_cand_<level> はrevoke必須。
    # Prompt/model/routingの変更(extract_signatureの変化)では失効させない。本文が変わった場合は、確定した選定文が新本文に逐語で残るなら候補doc/review を
    # API 0 で再バインドし、残らなければISSUE(Part2Stale)。
    cc = rv._cc()
    frozen_state = cc.grammar_state(study_dir)
    if frozen_state is not None:
        if force_extract:
            try:
                cc.guard_grammar(study_dir, f"--regenerate-stage part2_cand_{level}(再抽出)")
            except rv.ConfirmedContentLocked as e:
                raise g.Part2Stale(str(e)) from e
        if cached is not None and cached.get("text_sha256") != g.text_sha256(paragraphs):
            _rebind_grammar_text(study_dir, frozen_state, cached, review, paragraphs, label)
            cached, review = load_candidates(study_dir), load_review(study_dir)
    sig_ok = cached is not None and (cached.get("extract_signature") == g.extract_signature(paragraphs, label)
                                     or (frozen_state is not None and cached.get("text_sha256") == g.text_sha256(paragraphs)))
    if force_extract or (cached is not None and not sig_ok):
        why = "regenerate_stage" if force_extract else "text_or_prompt_changed"
        rv.archive_if_exists(pth["candidates"], "SUPERSEDED")
        carry = dict(review or {})
        carry["history"] = list(carry.get("history") or []) + [{"at": rv._now(), "event": f"superseded_{why}", "by": "runner", "detail": {}}]
        rv.archive_if_exists(pth["review"], "SUPERSEDED")
        cached, review = None, None
    if review is not None and review["status"] == rv.ST_REEXTRACT_REQUESTED:
        last = next((h for h in reversed(review.get("history") or []) if h.get("event") == "reextract"), {})
        why = (last.get("detail") or {}).get("reason") or "human_reextract"
        doc = g.reextract_candidates(cached, paragraphs, label, reason=why, by=last.get("by") or "human", ng_registry=ng, call_fn=extract_call_fn,
                                     client=client, budget_guard=budget_guard)
        save_candidates_doc(study_dir, doc)
        with rv.review_lock(study_dir, KIND, "runner"):
            rv_new = new_pending_review(doc, article_key=article_key, prev=review, reason="reextracted")
            review = _replace_review(study_dir, rv_new, review)
        cached, generated = doc, True
    elif cached is None:
        doc = g.resolve_candidates(paragraphs, label, None, level=level, call_fn=extract_call_fn, client=client, budget_guard=budget_guard, ng=ng)
        save_candidates_doc(study_dir, doc)
        with rv.review_lock(study_dir, KIND, "runner"):
            review = _replace_review(study_dir, new_pending_review(doc, article_key=article_key, prev=carry), None)
        cached, generated = doc, True
    else:
        doc = g.resolve_candidates(paragraphs, label, cached, level=level, ng=ng, allow_extract=False, frozen=frozen_state is not None)   # API 0。共有registryのNGを再適用
        if doc["candidates_sha256"] != cached["candidates_sha256"]:   # 新しいNGで候補が変わった: 古いreviewは対象外(STALE扱いで新review)
            save_candidates_doc(study_dir, doc)
            with rv.review_lock(study_dir, KIND, "runner"):
                review = _replace_review(study_dir, new_pending_review(doc, article_key=article_key, prev=review, reason="ng_registry_changed"), review)
        cached = doc
    doc = cached
    if review["candidates_sha256"] != doc["candidates_sha256"]:
        raise rv.KpReviewInconsistent("文法のreviewと候補docのcandidates_sha256が一致しません(手編集の疑い)。fail-closed")
    if review.get("schema") == g.SCHEMA_REVIEW and review["status"] not in rv.FORWARD_STATUSES_BY_KIND[KIND]:
        # 未確定のv1 review(旧フローで途中だったrun)はv2へ置換する(履歴は引き継ぐ。確定前なので確定内容は書換えない)
        with rv.review_lock(study_dir, KIND, "runner"):
            review = _replace_review(study_dir, new_pending_review(doc, article_key=article_key, prev=review, reason="upgraded_v1_to_v2"), review)
    if review["status"] in rv.FORWARD_STATUSES_BY_KIND[KIND]:
        return {"state": "READY", "review": review, "doc": doc, "pending": None, "generated": generated}
    # --- 未確定の評価 ---
    if not doc["candidates"] and not doc.get("exhausted"):
        # 適格0件: Humanに判断対象が無いので待たずに確定(NO_CANDIDATE_UNREVIEWED。REVIEWEDにしない)
        sel = g.select_from_candidates_v2(doc, None, "wait")
        with rv.review_lock(study_dir, KIND, "runner"):
            review = load_review(study_dir)
            rec = _finalized_record(doc, sel, review=review, decision=None, by="runner")
            review = rv.save_review(study_dir, rec, expected_revision=review["revision"], kind=KIND)
        return {"state": "READY", "review": review, "doc": doc, "pending": None, "generated": generated}
    if review["status"] == rv.ST_PENDING:
        decl = rv.read_mode_declaration(run_dir, level=level, review=review, round_no=review.get("round", 1), cands_sha=doc["candidates_sha256"])
        if decl is not None and doc["candidates"]:
            sel = g.select_from_candidates_v2(doc, None, decl)   # normalize_modeがdict形を検証(文字列autoは不可)。autoはTOP1のみ
            with rv.review_lock(study_dir, KIND, "runner"):
                review = load_review(study_dir)
                rec = _finalized_record(doc, sel, review=review, decision=None, by="runner")
                rv._event(rec, "auto_adopted", "runner", {"declaration_id": decl.get("declaration_id"), "selection": rec["selection"]})
                review = rv.save_review(study_dir, rec, expected_revision=review["revision"], kind=KIND)
            return {"state": "READY", "review": review, "doc": doc, "pending": None, "generated": generated}
    # 待機: 依頼書を書く(解説の事前生成が完了していれば全候補の解説全文付き。未完了なら『未完成』と明示=古い依頼書を残さない。候補が尽きたときも同様。自動ZEROにしない)
    write_request_for_state(study_dir, doc, review, level=level, run_hint=run_hint)
    return {"state": "PENDING", "review": review, "doc": doc, "pending": pending_summary(study_dir, review), "generated": generated}


def _atomic_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


# ============================================================
# Human操作(CLI。API 0。決定入力dictは er120 の {choice,candidates_sha256,reason,by,accept_ai[,candidate_ids,explanation_sha_by_id,channel]})
# ============================================================
def _need_by(by: str) -> None:
    if not (by or "").strip():
        raise rv.KpReviewError("--by(操作者)が必須です")


def _load_pair(study_dir: str):
    review, doc = load_review(study_dir), load_candidates(study_dir)
    if review is None or doc is None:
        raise rv.KpReviewError("文法の候補/reviewがありません(まず制作を実行して候補を生成してください)")
    if review["candidates_sha256"] != doc["candidates_sha256"]:
        raise rv.KpReviewError("reviewと候補docのcandidates_sha256が一致しません")
    if review["status"] == rv.ST_STALE:
        raise rv.KpReviewError("status=STALEのため操作できません(制作を再実行して候補を再生成してください)")
    return review, doc


def _guard_pick(study_dir: str, op: str, ids: list) -> None:
    """確定内容保護(M6): ユーザー確定済みの文法があれば、確定した集合と同じ候補を選ぶ pick/top1/top2 以外は拒否(revoke必須)。"""
    cc = rv._cc()
    st = cc.grammar_state(study_dir)
    if st is not None:
        confirmed = {it.get("id") for it in st["sidecar"].get("items") or []}
        if set(ids) != confirmed:
            cc.guard_grammar(study_dir, f"{op}(確定集合と不一致)", candidate_id=None)
        return
    cc.guard_grammar(study_dir, op, candidate_id=ids[0] if ids else None)


def _decision_dict(doc: dict, ex: Optional[dict], *, choice: str, candidates_sha256: str, reason: str, by: str, accept_ai: bool,
                   ids: Optional[list], channel: str) -> dict:
    d = {"choice": choice, "candidates_sha256": candidates_sha256, "reason": reason, "by": by, "accept_ai": bool(accept_ai), "channel": channel}
    if ids is not None:
        d["candidate_ids"] = list(ids)
    if ex is not None:
        d["explanation_sha_by_id"] = g.explanation_sha_by_id(ex, [c["candidate_id"] for c in doc["candidates"][:g.PREGEN_MAX]])
    return d


def op_decide(study_dir: str, *, choice: str, candidates_sha256: str, reason: str = "", by: str, accept_ai: bool = False,
              ids: Optional[list] = None, channel: str = "cli") -> dict:
    """Humanの決定。choice=pick(ids 1件。2件は拒否・0件はomit) / top1|top2(単件ショートカット) / omit / reselect(API 0で次順位の新候補一覧、NGを共有registryへ) /
    reextract(枯渇時のみ。次回起動でStep A'' 1 call)。AI推奨(TOP1のみ)以外のpick・top2/reselect/omit/reextractはreason必須(er120が検証)。candidates_sha256が現docと違えばstale拒否。
    v2のreviewでは、解説の事前生成が完了・整合していることを必須とし(提示するTop1/Top2の解説を見て決める要件。未完了ならデータなしでエラー)、提示した解説のid別shaを記録する。
    確定済み(AUTO含む)からの事後Reviewも可(downstreamはselection_signatureで再finalizeを要求する)。"""
    _need_by(by)
    with rv.review_lock(study_dir, KIND, by):
        review, doc = _load_pair(study_dir)
        level = _level_of(review, doc)
        ak = review.get("article_key") or {}
        v2 = review.get("schema") == g.SCHEMA_REVIEW_V2
        if choice == "pick" and not v2:
            raise rv.KpReviewError("このreviewはv1(単一選定)です。制作を再実行してv2へ移行するか、top1/top2/omitで選んでください")
        if choice in ("pick", "top1", "top2", "omit") and v2 and doc.get("candidates"):
            ex = require_explanations(study_dir, doc, level=level)    # Top1/Top2の解説が揃ってから決める
        else:
            ex = None
        decision = _decision_dict(doc, ex, choice=choice, candidates_sha256=candidates_sha256, reason=reason, by=by, accept_ai=accept_ai, ids=ids, channel=channel)
        _cands = doc.get("candidates") or []
        if choice == "pick":
            _guard_pick(study_dir, "decide(pick)", list(ids or []))
        elif choice in ("top1", "top2"):
            i = 0 if choice == "top1" else 1
            _guard_pick(study_dir, f"decide({choice})", [_cands[i]["candidate_id"]] if i < len(_cands) else [])
        else:
            rv._cc().guard_grammar(study_dir, f"decide({choice})")
        if choice == "reselect":
            if candidates_sha256 != doc["candidates_sha256"]:
                raise g.Part2ReviewError("reviewが古い候補listに対するものです(candidates_sha256不一致)。再レビューが必要です")
            if doc.get("exhausted") or not doc["candidates"]:
                raise g.Part2ReviewError("再選定できる候補がありません(omit か reextract を選んでください)")
            sel = g.select_from_candidates_v2(doc, decision, "wait")   # 検証(reason必須・上限・sha)。status=RESELECT_REQUESTED
            assert sel["status"] == "RESELECT_REQUESTED"
            doc2 = g.reselect_candidates(doc, None, reason=reason, by=by)
            old_ids = {e.get("candidate_id") for e in doc.get("ng", [])}
            for e in doc2["ng"]:
                if e.get("candidate_id") not in old_ids:
                    e.setdefault("sentence_key", g._norm_sentence(e["sentence"]))
                    if ak.get("family"):
                        rv.store_add_ng(ak["family"], ak["slug"], level, e, KIND)
            save_candidates_doc(study_dir, doc2)
            new = new_pending_review(doc2, article_key=ak, prev=review, reason="reselect")
            new["last_human_op_at"] = rv._now()
            _event(new, "reselect", by, {"reason": reason, "from_candidates_sha256": doc["candidates_sha256"], "round": doc2.get("round"),
                                          "rejected": [d for d in (doc2.get("reselect_log") or [])[-1:]]})
            out = _replace_review(study_dir, new, review)
            _atomic_text(paths(study_dir)["request"], _stale_request_md(doc2, out, "候補が更新されました(選び直し)。新候補の解説を事前生成してから提示します"))   # 古い依頼書を残さない
            return out
        if choice == "reextract":
            sel = g.select_from_candidates_v2(doc, decision, "wait")   # exhausted以外・上限超過・reason欠落は例外
            assert sel["status"] == "REEXTRACT_REQUESTED"
            review.update(status=rv.ST_REEXTRACT_REQUESTED, selection={}, decision=decision, last_human_op_at=rv._now())
            _event(review, "reextract", by, {"reason": reason, "candidates_sha256": doc["candidates_sha256"]})
            return rv.save_review(study_dir, review, expected_revision=review["revision"], kind=KIND)
        if choice in ("pick", "top1", "top2", "omit"):
            sel = g.select_from_candidates_v2(doc, decision, "wait")
            review["last_human_op_at"] = rv._now()
            rec = _finalized_record(doc, sel, review=review, decision=decision, by=by)
            rec["last_human_op_at"] = review["last_human_op_at"]
            return rv.save_review(study_dir, rec, expected_revision=review["revision"], kind=KIND)
        raise g.Part2ReviewError(f"choiceは pick/top1/top2/omit/reselect/reextract のいずれか: {choice!r}")


def apply_form_selection(study_dir: str, *, ids: list, by: str, user_ref: str = "", candidates_sha256: Optional[str] = None) -> dict:
    """フォーム確定(KCP from-form)用: 文法reviewへ pick(ids) を適用する。ids=[] は**同じロック内で omit**(zero_reason=form_submission_no_grammar。0件の確定も記録する)。
    呼出し順(Opus O-4): 検証を全て済ませる → KPロック → 本関数(文法ロック) → sidecar → KPレコード保存(commit点)。冪等: 既に同じ内容で確定済みなら変更しない。
    解説の事前生成が完了・整合していなければエラー(フォームに出した解説=確定=公開の一致の前提)。v1確定済みrunからでもv2 recordへ置換する(履歴は引き継ぐ)。"""
    _need_by(by)
    ids = list(ids or [])
    with rv.review_lock(study_dir, KIND, by):
        review, doc = _load_pair(study_dir)
        level = _level_of(review, doc)
        if candidates_sha256 is not None and candidates_sha256 != doc["candidates_sha256"]:
            raise g.Part2ReviewError("フォームの文法候補が古い候補listに対するものです(candidates_sha256不一致)。フォームを作り直してください")
        ex = require_explanations(study_dir, doc, level=level) if doc.get("candidates") else None
        want_ids = [c["candidate_id"] for c in g.order_by_text([c for c in doc.get("candidates", []) if c["candidate_id"] in set(ids)])]
        if len(want_ids) != len(set(ids)) or len(ids) != len(set(ids)):
            raise g.Part2ReviewError(f"フォームの文法idが候補docにない/重複しています: {ids}")
        if len(ids) > g.GRAMMAR_MAX:
            raise g.Part2ReviewError(f"文法は{g.GRAMMAR_MAX}件だけ選べます(2件同時選択は禁止。0件は省略=omit): {len(ids)}件")
        zero = not ids
        if zero and not doc.get("candidates") and not doc.get("exhausted"):
            return review        # 候補0件=既にNO_CANDIDATE_UNREVIEWEDで確定(何もしない=冪等)
        cur = review
        if cur["status"] in rv.FORWARD_STATUSES_BY_KIND[KIND] and cur.get("schema") == g.SCHEMA_REVIEW_V2:
            sel_cur = cur.get("selection") or {}
            same = (zero and sel_cur.get("choice") == "omit" and cur["status"] == rv.ST_REVIEWED) or (not zero and sel_cur.get("choice") == "pick" and sel_cur.get("candidate_ids") == want_ids
                                                                                                      and cur["status"] == rv.ST_REVIEWED)
            if same:
                return cur
        if zero:
            _guard_pick(study_dir, "from-form(文法0件)", [])
            decision = _decision_dict(doc, ex, choice="omit", candidates_sha256=doc["candidates_sha256"], reason="form_submission_no_grammar", by=by, accept_ai=False, ids=[], channel="form")
        else:
            _guard_pick(study_dir, "from-form(文法)", want_ids)
            decision = _decision_dict(doc, ex, choice="pick", candidates_sha256=doc["candidates_sha256"], reason=f"form_submission:{user_ref}".strip(":"), by=by,
                                      accept_ai=False, ids=want_ids, channel="form")
        sel = g.select_from_candidates_v2(doc, decision, "wait")
        review["last_human_op_at"] = rv._now()
        v2_base = dict(review, schema=g.SCHEMA_REVIEW_V2)
        rec = _finalized_record(doc, sel, review=v2_base, decision=decision, by=by)
        rec["last_human_op_at"] = review["last_human_op_at"]
        rv._event(rec, "form_submission", by, {"user_ref": user_ref, "candidate_ids": want_ids})
        return rv.save_review(study_dir, rec, expected_revision=review["revision"], kind=KIND)


def op_ng(study_dir: str, *, rank: int, reason: str, by: str) -> dict:
    """候補をNGにする(選択はしない)。候補listから除かれ(candidates_sha256が変わる)、共有registryに入る。以後の宣言は失効する。"""
    _need_by(by)
    if not (reason or "").strip():
        raise rv.KpReviewError("NG指定には理由が必要です")
    with rv.review_lock(study_dir, KIND, by):
        review, doc = _load_pair(study_dir)
        level = _level_of(review, doc)
        rv._cc().guard_grammar(study_dir, "ng")   # 確定内容保護(M6)
        c = next((x for x in doc["candidates"] if x["rank"] == rank), None)
        if c is None:
            raise rv.KpReviewError(f"番号{rank}の候補がありません")
        ak = review.get("article_key") or {}
        ent = _ng_entry(c, reason, by, "human_ng")
        doc2 = g.apply_ng(doc, [ent])
        doc2["reselect_log"] = list(doc2.get("reselect_log", [])) + [{"at": rv._now(), "event": "ng", "by": by, "reason": reason, "kind": "ng",
                                                                       "rejected": [g.rejection_detail(doc, c)]}]
        if ak.get("family"):
            rv.store_add_ng(ak["family"], ak["slug"], level, ent, KIND)
        save_candidates_doc(study_dir, doc2)
        new = new_pending_review(doc2, article_key=ak, prev=review, reason="ng")
        new["last_human_op_at"] = rv._now()
        _event(new, "ng", by, {"rank": rank, "candidate_id": c["candidate_id"], "reason": reason})
        out = _replace_review(study_dir, new, review)
        _atomic_text(paths(study_dir)["request"], _stale_request_md(doc2, out, "候補が更新されました(NG指定)。新候補の解説を事前生成してから提示します"))
        return out


def op_unng(study_dir: str, *, sentence: Optional[str] = None, candidate_id: Optional[str] = None, reason: str, by: str) -> list:
    """NG解除(理由・記録必須)。共有registryのentryをactive=falseにする(削除でなく記録を残す)。現在の候補listへは戻らない(次の新規抽出/reextractから効く)。
    NG済みの候補は現在のlistに番号が無いため、--sentence(英文)か --candidate-id で指定する。"""
    _need_by(by)
    skey = g._norm_sentence(sentence) if sentence else None
    if not (skey or candidate_id):
        raise rv.KpReviewError("unngの対象(--sentence か --candidate-id)が必要です")
    with rv.review_lock(study_dir, KIND, by):
        review = load_review(study_dir)
        if review is None:
            raise rv.KpReviewError("reviewがありません")
        level = _level_of(review, load_candidates(study_dir))
        rv._cc().guard_grammar(study_dir, "unng")   # 確定内容保護(M6)
        ak = review.get("article_key") or {}
        removed = rv.store_remove_ng(ak["family"], ak["slug"], level, candidate_id=candidate_id, reason=reason, by=by, kind=KIND, sentence_key=skey)
        review["last_human_op_at"] = rv._now()
        _event(review, "unng", by, {"removed": sorted(set(removed)), "reason": reason, "sentence": sentence})
        rv.save_review(study_dir, review, expected_revision=review["revision"], kind=KIND)
        return sorted(set(removed))


# ============================================================
# Part 1訳との食い違い(ISSUE)の解消手段: ユーザー了承(Opus O-1 / Fable判定。`--user-ref`必須・記録が残る・再送は冪等)
# ============================================================
def write_translation_issue(study_dir: str, issues: list, *, level: str) -> str:
    """食い違い(translation_issues)をISSUEファイルへ記録(rc=4の案内用)。解消手段=別候補を選ぶ/省略する、またはユーザー了承(op_accept_translation_diff)。"""
    doc = {"schema": "grammar_translation_issue_v1", "level": g.level_name(level), "at": rv._now(), "issues": issues,
           "resolutions": ["別の文法候補を選ぶ、または省略(omit)する(grammar-select)",
                           "ユーザーが食い違いを了承して現状のまま進める: op_accept_translation_diff(--user-ref必須。記録が残る)"]}
    _atomic_json(paths(study_dir)["translation_issue"], doc)
    return paths(study_dir)["translation_issue"]


def load_translation_acks(study_dir: str) -> dict:
    """{candidate_id: [ack...]}"""
    d = g.load_json(paths(study_dir)["translation_ack"]) or {}
    out: dict = {}
    for a in d.get("acks") or []:
        out.setdefault(a.get("candidate_id"), []).append(a)
    return out


def op_accept_translation_diff(study_dir: str, *, ids: list, by: str, user_ref: str, reason: str) -> list:
    """ISSUEファイル(grammar_translation_issue.json)に記録された食い違いのうち ids のものを、ユーザー了承として記録する(Step B訳とPart 1訳のshaを固定)。
    `--user-ref`(ユーザー発言の参照)と理由が必須。同じ内容の再送は冪等(重複記録しない)。ISSUEに無いidは拒否。戻り値=今回新規に記録したcandidate_id。"""
    _need_by(by)
    if not (user_ref or "").strip() or not (reason or "").strip():
        raise rv.KpReviewError("了承には --user-ref(ユーザー発言の参照)と理由が必須です")
    issue = g.load_json(paths(study_dir)["translation_issue"])
    if not issue or not issue.get("issues"):
        raise rv.KpReviewError("了承の対象となるISSUE(grammar_translation_issue.json)がありません")
    by_id = {i["candidate_id"]: i for i in issue["issues"]}
    bad = [i for i in ids if i not in by_id]
    if not ids or bad:
        raise rv.KpReviewError(f"ISSUEに無い/未指定の文法idです: {bad or 'なし'}")
    with rv.review_lock(study_dir, KIND, by):
        cur = g.load_json(paths(study_dir)["translation_ack"]) or {"schema": "grammar_translation_ack_v1", "acks": []}
        added = []
        for cid in ids:
            sb = hashlib.sha256(str(by_id[cid]["step_b_ja"]).encode("utf-8")).hexdigest()
            p1 = hashlib.sha256(str(by_id[cid]["part1_ja"]).encode("utf-8")).hexdigest()
            if any(a.get("candidate_id") == cid and a.get("step_b_ja_sha256") == sb and a.get("part1_ja_sha256") == p1 for a in cur["acks"]):
                continue
            cur["acks"].append({"candidate_id": cid, "step_b_ja_sha256": sb, "part1_ja_sha256": p1, "by": by, "user_ref": user_ref, "reason": reason, "at": rv._now()})
            added.append(cid)
        _atomic_json(paths(study_dir)["translation_ack"], cur)
        return added


# ============================================================
# 提示(依頼書)・状態一覧
# ============================================================
def render_request_md(doc: dict, review: dict, *, run_hint: str, explanations: Optional[dict] = None, study_dir: Optional[str] = None) -> str:
    """v2: Top1/Top2(<=PREGEN_MAX=2)の『文法名+解説全文』を順位順に載せる(3位以降は非表示・件数のみ『他N件』)。解説(事前生成物)が無い/不整合ならデータを出さずエラー(grammar-showのfail-closed)。
    explanations か study_dir(事前生成物を読んで検証)のどちらかを渡す。v1 reviewは従来の2件枠(読取互換)。"""
    if review.get("schema") == g.SCHEMA_REVIEW:
        return _render_request_md_v1(doc, review, run_hint=run_hint)
    level = _level_of(review, doc)
    if explanations is None and study_dir is None:   # CLI(grammar-show)互換: run dirとlevelからstudy dirを特定(候補doc[sha・level]が一致する1つだけ。曖昧ならエラー)
        same = [d for d in discover_dirs(run_hint, level) if (load_candidates(d) or {}).get("candidates_sha256") == doc["candidates_sha256"]]
        if len(same) == 1:
            study_dir = same[0]
    if explanations is None and study_dir is not None:
        explanations = require_explanations(study_dir, doc, level=level)
    if explanations is None:
        raise rv.KpReviewError("文法解説の事前生成物を渡してください(解説なしで候補だけを出しません)。制作を再実行して事前生成を完了してください")
    try:
        g.validate_explanations(explanations, doc, level=level)
    except g.Part2Stale as e:
        raise rv.KpReviewError(str(e)) from e
    req = g.review_request_v2(doc, explanations)
    sha = doc["candidates_sha256"]
    L = [f"# Part 2 文法解説 Human Review 依頼({doc['level']}) round {doc.get('round', 1)}", "",
         f"- 状態: {review.get('status')} / candidates_sha256: `{sha[:16]}` / 本文sha: `{doc['text_sha256'][:12]}` / 再選定 {req['reselect_count']}/{g.MAX_RESELECT}回・再抽出 {req['reextract_count']}/{g.MAX_REEXTRACT}回",
         f"- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**{g.GRAMMAR_MAX}件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。", ""]
    if req["exhausted"]:
        L += ["- **全候補をNGにして尽きました**。選べる操作: " + " / ".join(req["choices"]) + "(omit=今回は解説を出さない、reextract=本文から候補を再抽出[Step A'' 1 call・上限1回])", ""]
    elif not req["candidates"]:
        L += ["- 適格な候補がありません(待たずに0件で確定します)。", ""]
    for t in req["candidates"]:
        mark = "AI推奨(Top1)" if t["candidate_id"] == req["ai_recommended"] else "Top2"
        L += [f"## {mark}: {t['title']} [{t['tier']} / {t['feature_class']}] 段落{t['para']}  (評価順位{t['rank']} / id: `{t['candidate_id']}`)", "", f"> {t['sentence']}", "",
              f"- 教える価値: {t['teaching_value_ja']}", f"- 読み違えやすい点: {t['misread_ja']}", "", "### 解説(学習ページに載る全文)", "", t["explanation_md"], ""]
    if req["n_not_generated"]:
        L += [f"(他{req['n_not_generated']}件は非表示: AI評価のTop1/Top2(先頭{g.PREGEN_MAX}件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)", ""]
    L += ["## 操作(コマンド。`--by` は操作者名。`--level`は必須)", ""]
    lv = (review.get("article_key") or {}).get("level")
    base = f"{CLI} grammar-select --run {run_hint} --level {lv} --candidates-sha {sha} --by <名前>"
    if "pick" in req["choices"]:
        top = req["ai_recommended"]
        L.append(f"- AI推奨(候補1)だけを選ぶ(了承): `{base} --choice pick --ids {top} --accept-ai`")
        L.append(f"- {g.GRAMMAR_MAX}件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `{base} --choice pick --ids <id> --reason <理由>`")
    if "reselect" in req["choices"]:
        L.append(f"- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `{base} --choice reselect --reason <理由>`")
    if "omit" in req["choices"]:
        L.append(f"- 今回は文法解説を出さない(理由必須): `{base} --choice omit --reason <理由>`")
    if "reextract" in req["choices"]:
        L.append(f"- 再抽出(枯渇時のみ・理由必須): `{base} --choice reextract --reason <理由>`")
    L += [f"- 状況: `{CLI} status --run {run_hint}` / 表示: `{CLI} grammar-show --run {run_hint} --level {lv}`",
          f"- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `{CLI} declare-absent --runs {run_hint} --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`",
          "", "再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。"]
    return "\n".join(L) + "\n"


def _render_request_md_v1(doc: dict, review: dict, *, run_hint: str) -> str:
    """v1 review(旧フロー。TOP1/TOP2の2件枠)の依頼書(読取互換)。"""
    req = g.review_request(doc)
    sha = doc["candidates_sha256"]
    L = [f"# Part 2 文法解説 Human Review 依頼({doc['level']}) round {doc.get('round', 1)}", "",
         f"- 状態: {review.get('status')} / candidates_sha256: `{sha[:16]}` / 本文sha: `{doc['text_sha256'][:12]}` / 再選定 {req['reselect_count']}/{g.MAX_RESELECT}回・再抽出 {req['reextract_count']}/{g.MAX_REEXTRACT}回",
         "- あなたの作業: 本文の中で解説する英文を1つ選びます(AI推奨=TOP1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。", ""]
    if req["exhausted"]:
        L += ["- **全候補をNGにして尽きました**。選べる操作: " + " / ".join(req["choices"]) + "(omit=今回は解説を出さない、reextract=本文から候補を再抽出[Step A'' 1 call・上限1回])", ""]
    elif not req["top"]:
        L += ["- 適格な候補がありません(待たずに0件で確定します)。", ""]
    for t in req["top"]:
        mark = "AI推奨(TOP1)" if t["candidate_id"] == req["ai_recommended"] else "TOP2"
        L += [f"## {mark}: 候補{t['rank']} [{t['tier']} / {t['feature_class']}] 段落{t['para']}", "", f"> {t['sentence']}", "",
              f"- 構文: {t['construct_ja']}", f"- 教える価値: {t['teaching_value_ja']}", f"- 読み違えやすい点: {t['misread_ja']}", ""]
    if req["n_more"]:
        L += [f"(TOP2の次に控えがあと{req['n_more']}件。reselectすると次順位が新しいTOP1/TOP2になります)", ""]
    L += ["## 操作(コマンド。`--by` は操作者名)", ""]
    lv = (review.get("article_key") or {}).get("level")
    base = f"{CLI} grammar-select --run {run_hint} --level {lv} --candidates-sha {sha} --by <名前>"
    if "top1" in req["choices"]:
        L.append(f"- AI推奨(TOP1)を了承: `{base} --choice top1 --accept-ai`")
        L.append(f"- TOP1を選ぶ: `{base} --choice top1`")
    if "top2" in req["choices"]:
        L.append(f"- TOP2を選ぶ(理由必須): `{base} --choice top2 --reason <理由>`")
    if "reselect" in req["choices"]:
        L.append(f"- 選び直し(TOP1/TOP2をNGにして次順位へ。理由必須・上限あり): `{base} --choice reselect --reason <理由>`")
    if "omit" in req["choices"]:
        L.append(f"- 今回は解説を出さない(理由必須): `{base} --choice omit --reason <理由>`")
    if "reextract" in req["choices"]:
        L.append(f"- 再抽出(枯渇時のみ・理由必須): `{base} --choice reextract --reason <理由>`")
    L += [f"- 状況: `{CLI} status --run {run_hint}` / 表示: `{CLI} grammar-show --run {run_hint} --level {lv}`",
          f"- 不在として進める(明示宣言。このrun・この候補round限り): `{CLI} declare-absent --runs {run_hint} --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`",
          "", "再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・supportの再生成は行われません)。"]
    return "\n".join(L) + "\n"


def status_of(study_dir: str) -> dict:
    review, doc = load_review(study_dir), load_candidates(study_dir)
    if review is None:
        return {"study_dir": study_dir, "kind": "grammar", "status": "NO_REVIEW"}
    ex = load_explanations(study_dir)
    return {"study_dir": study_dir, "kind": "grammar", "level": review.get("level"), "schema": review.get("schema"), "status": review["status"], "round": review.get("round"),
            "reselect_count": review.get("reselect_count"), "reextract_count": review.get("reextract_count"),
            "candidates_sha256": review.get("candidates_sha256"), "selection": review.get("selection"),
            "mode_declaration": review.get("mode_declaration"), "revision": review.get("revision"),
            "n_candidates": len((doc or {}).get("candidates") or []), "exhausted": bool((doc or {}).get("exhausted")),
            "n_explanations": len((ex or {}).get("items") or []), "selection_signature": review.get("selection_signature")}


def discover_dirs(run_dir: str, level: Optional[str] = None) -> list:
    """文法のreview/候補ファイルのあるstudy dir。
    level指定: そのlevelのdirだけ(b1b=<run>/b1b/study_text[X]・<run>/study_text[Y/Z]、a2=<run>/a2/study_text)。候補docの`level`欄と一致することを確認し、
    不一致・候補docなしでreviewだけ、はfail-closed(pathから推定しない)。
    level=None: 全levelのdirを返す(status表示用の列挙のみ。選択・sidecar書込みには使わない=呼出側が必ずlevel指定を使う)。"""
    cand = {"b1b": [f"{run_dir}/b1b/study_text", f"{run_dir}/study_text"], "a2": [f"{run_dir}/a2/study_text"]}
    keys = [level] if level is not None else ["b1b", "a2"]
    if level is not None:
        g.level_name(level)
    out = []
    for lv in keys:
        for d in cand[lv]:
            p = paths(d)
            if not (os.path.exists(p["review"]) or os.path.exists(p["candidates"])):
                continue
            if level is not None:
                doc = g.load_json(p["candidates"])
                if doc is None:
                    raise g.Part2Stale(f"{d}: 文法の候補doc(grammar_candidates.json)がありません(levelの確認不可=fail-closed)")
                g.check_doc_level(doc, level)
            if d not in out:
                out.append(d)
    return out
