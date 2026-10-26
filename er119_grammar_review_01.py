# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03 兼 PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03:
Part 2「Grammar & Sentence Structure」のHuman Review(er119共通核に kind="grammar" で接続)。決定論(API 0)。

- 状態/操作の実体はここ。署名・NG registry・排他lock・不在宣言の読取は er119_kp_human_review_01(共通核)を使う:
    署名      = rv.selection_signature(kind=grammar) -> er120.grammar_selection_signature(単一関数。突合test: TestSignatureSingleSource)
    NG        = rv.store_*(family+slug+level[+kind=grammar]) の共有registry(run dirに依存しない=copy-runが自動引継ぎ)・書込は排他lock
    不在宣言  = rv.read_mode_declaration(単一読取点。dict形はer120.normalize_modeが受ける形)。環境変数/引数/hooksからautoにならない
    status    = REVIEWED / UNREVIEWED_AUTO_ADOPTED / NO_CANDIDATE_UNREVIEWED だけが下流を進める。
                PENDING_REVIEW / RESELECT_EXHAUSTED / REEXTRACT_REQUESTED / RESELECTION_REQUESTED / STALE は下流fail-closed
- LLM呼出は注入関数のみ(Step A'' の抽出とreextractのみ。Step Bは er120_part2_wiring_01.finalize_stage)。CLI操作(Human)はAPI 0。
- ファイル(study_dir): grammar_candidates.json / grammar_human_review.json / grammar_human_review.lock / grammar_human_review_request.md
"""
from __future__ import annotations

import json
import os
from typing import Callable, Optional

import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g

KIND = rv.KIND_GRAMMAR
LEVEL_KEY = "b1b"                      # 共有NG registryのlevel(Part 2はAdvancedのみ)
CLI = "py er119_kp_human_review_cli_01.py"


def paths(study_dir: str) -> dict:
    return rv.paths(study_dir, KIND)


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


def new_pending_review(doc: dict, *, article_key: dict, prev: Optional[dict] = None, reason: str = "candidates_generated") -> dict:
    """候補docに対する未確定review。docが尽きていればRESELECT_EXHAUSTED(自動確定しない)、それ以外はPENDING_REVIEW。
    prev(前のreview)のhistory・reselect_count・last_human_op_at・NGを引き継ぐ(Human操作の記録を失わない)。"""
    status = rv.ST_RESELECT_EXHAUSTED if doc.get("exhausted") else rv.ST_PENDING
    r = {"schema": g.SCHEMA_REVIEW, "kind": KIND, "level": g.LEVEL, "text_sha256": doc["text_sha256"],
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
    rec = g.finalize_review_record(doc, sel, decision=decision, by=by, prior_history=review.get("history"))
    for k in ("article_key", "round", "last_human_op_at", "revision"):
        rec[k] = review.get(k)
    rec["decision"] = ({k: decision.get(k) for k in ("choice", "candidates_sha256", "reason", "by", "accept_ai")} if decision else None)
    return rec


def registry_ng(family: str, slug: str) -> list:
    return rv.store_load_ng(family, slug, LEVEL_KEY, KIND)


def pending_summary(study_dir: str, review: dict) -> dict:
    return {"kind": "grammar", "level": "Advanced", "dir": study_dir, "request_md": paths(study_dir)["request"],
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
# runner側: 候補抽出(Step A'')と待機/自動確定の評価(再実行しても冪等・resumeはAPI 0)
# ============================================================
def ensure_grammar_review(study_dir: str, *, run_dir: str, family: str, slug: str, paragraphs: list, label: str, run_hint: Optional[str] = None,
                          extract_call_fn: Optional[Callable] = None, client=None, budget_guard: Optional[Callable] = None,
                          force_extract: bool = False) -> dict:
    """候補抽出(または保存済み候補の再利用)→(Human確認 / 明示宣言のAUTO / 適格0件の即確定)。KP候補生成と同じ待機点の前に実行する。
    returns {"state":"READY"|"PENDING","review":{...},"doc":{...},"pending":{...}|None,"generated":bool,"api_calls_expected":int}
    - 保存済み候補が現在の本文・label・Prompt・modelと一致 → Step A'' 0 call(M-7)。共有registryのNGは再適用(変われば新reviewへ)
    - REEXTRACT_REQUESTED(Humanがreextractを選んだ)のときだけ Step A'' を再度呼ぶ(上限1回、再選定合計2回)
    - force_extract=True(--regenerate-stage part2_cand_b1b): 旧候補/reviewをSUPERSEDEDへ退避して再抽出(NGは保持)"""
    pth = paths(study_dir)
    os.makedirs(study_dir, exist_ok=True)
    article_key = {"family": family, "slug": slug, "level": LEVEL_KEY}
    run_hint = run_hint or run_dir
    ng = registry_ng(family, slug)
    cached, review = load_candidates(study_dir), load_review(study_dir)
    if (cached is None) != (review is None):
        raise rv.KpReviewInconsistent("文法の候補ファイルとreviewの片方だけがあります(手動削除の疑い)。fail-closed。状況をFableへ報告してください")
    generated = False
    carry = review
    # 確定内容保護(M6/M8): ユーザー確定済みの文法がある場合は再抽出しない。--regenerate-stage part2_cand_b1b はrevoke必須。
    # Prompt/model/routingの変更(extract_signatureの変化)では失効させない。本文が変わった場合は、確定した選定文が新本文に逐語で残るなら候補doc/review を
    # API 0 で再バインドし、残らなければISSUE(Part2Stale)。
    cc = rv._cc()
    frozen_state = cc.grammar_state(study_dir)
    if frozen_state is not None:
        if force_extract:
            try:
                cc.guard_grammar(study_dir, "--regenerate-stage part2_cand_b1b(再抽出)")
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
        doc = g.resolve_candidates(paragraphs, label, None, call_fn=extract_call_fn, client=client, budget_guard=budget_guard, ng=ng)
        save_candidates_doc(study_dir, doc)
        with rv.review_lock(study_dir, KIND, "runner"):
            review = _replace_review(study_dir, new_pending_review(doc, article_key=article_key, prev=carry), None)
        cached, generated = doc, True
    else:
        doc = g.resolve_candidates(paragraphs, label, cached, ng=ng, allow_extract=False, frozen=frozen_state is not None)   # API 0。共有registryのNGを再適用
        if doc["candidates_sha256"] != cached["candidates_sha256"]:   # 新しいNGで候補が変わった: 古いreviewは対象外(STALE扱いで新review)
            save_candidates_doc(study_dir, doc)
            with rv.review_lock(study_dir, KIND, "runner"):
                review = _replace_review(study_dir, new_pending_review(doc, article_key=article_key, prev=review, reason="ng_registry_changed"), review)
        cached = doc
    doc = cached
    if review["candidates_sha256"] != doc["candidates_sha256"]:
        raise rv.KpReviewInconsistent("文法のreviewと候補docのcandidates_sha256が一致しません(手編集の疑い)。fail-closed")
    if review["status"] in rv.FORWARD_STATUSES_BY_KIND[KIND]:
        return {"state": "READY", "review": review, "doc": doc, "pending": None, "generated": generated}
    # --- 未確定の評価 ---
    if not doc["candidates"] and not doc.get("exhausted"):
        # 適格0件: Humanに判断対象が無いので待たずに確定(NO_CANDIDATE_UNREVIEWED。REVIEWEDにしない)
        sel = g.select_from_candidates(doc, None, "wait")
        with rv.review_lock(study_dir, KIND, "runner"):
            review = load_review(study_dir)
            rec = _finalized_record(doc, sel, review=review, decision=None, by="runner")
            review = rv.save_review(study_dir, rec, expected_revision=review["revision"], kind=KIND)
        return {"state": "READY", "review": review, "doc": doc, "pending": None, "generated": generated}
    if review["status"] == rv.ST_PENDING:
        decl = rv.read_mode_declaration(run_dir, level=LEVEL_KEY, review=review, round_no=review.get("round", 1), cands_sha=doc["candidates_sha256"])
        if decl is not None and doc["candidates"]:
            sel = g.select_from_candidates(doc, None, decl)   # normalize_modeがdict形を検証(文字列autoは不可)
            with rv.review_lock(study_dir, KIND, "runner"):
                review = load_review(study_dir)
                rec = _finalized_record(doc, sel, review=review, decision=None, by="runner")
                rv._event(rec, "auto_adopted", "runner", {"declaration_id": decl.get("declaration_id"), "selection": rec["selection"]})
                review = rv.save_review(study_dir, rec, expected_revision=review["revision"], kind=KIND)
            return {"state": "READY", "review": review, "doc": doc, "pending": None, "generated": generated}
    # 待機: 依頼書を書く(候補が尽きたときも同様。自動ZEROにしない)
    _atomic_text(pth["request"], render_request_md(doc, review, run_hint=run_hint))
    return {"state": "PENDING", "review": review, "doc": doc, "pending": pending_summary(study_dir, review), "generated": generated}


def _atomic_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


# ============================================================
# Human操作(CLI。API 0。決定入力dictは er120 の {choice,candidates_sha256,reason,by,accept_ai})
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


def op_decide(study_dir: str, *, choice: str, candidates_sha256: str, reason: str = "", by: str, accept_ai: bool = False) -> dict:
    """Humanの決定。choice=top1|top2|omit(確定) / reselect(API 0で次順位の新TOP1/TOP2、NGを共有registryへ) / reextract(枯渇時のみ。次回起動でStep A'' 1 call)。
    top2/reselect/omit/reextractはreason必須(er120が検証)。candidates_sha256が現docと違えばstale拒否。
    確定済み(AUTO含む)からの事後Reviewも可(downstreamはselection_signatureで再finalizeを要求する)。"""
    _need_by(by)
    decision = {"choice": choice, "candidates_sha256": candidates_sha256, "reason": reason, "by": by, "accept_ai": bool(accept_ai)}
    with rv.review_lock(study_dir, KIND, by):
        review, doc = _load_pair(study_dir)
        ak = review.get("article_key") or {}
        # 確定内容保護(M6): ユーザー確定済みの文法があれば、確定した文法と同じ候補を選ぶ top1/top2 以外(省略・再選定・再抽出・別候補)は拒否(revoke必須)
        _cands = doc.get("candidates") or []
        _chosen = _cands[0]["candidate_id"] if choice == "top1" and _cands else (_cands[1]["candidate_id"] if choice == "top2" and len(_cands) > 1 else None)
        rv._cc().guard_grammar(study_dir, f"decide({choice})", candidate_id=_chosen)
        if choice == "reselect":
            if candidates_sha256 != doc["candidates_sha256"]:
                raise g.Part2ReviewError("reviewが古い候補listに対するものです(candidates_sha256不一致)。再レビューが必要です")
            if doc.get("exhausted") or not doc["candidates"]:
                raise g.Part2ReviewError("再選定できる候補がありません(omit か reextract を選んでください)")
            sel = g.select_from_candidates(doc, decision, "wait")   # 検証(reason必須・上限・sha)。status=RESELECT_REQUESTED
            assert sel["status"] == "RESELECT_REQUESTED"
            doc2 = g.reselect_candidates(doc, None, reason=reason, by=by)
            old_ids = {e.get("candidate_id") for e in doc.get("ng", [])}
            for e in doc2["ng"]:
                if e.get("candidate_id") not in old_ids:
                    e.setdefault("sentence_key", g._norm_sentence(e["sentence"]))
                    if ak.get("family"):
                        rv.store_add_ng(ak["family"], ak["slug"], LEVEL_KEY, e, KIND)
            save_candidates_doc(study_dir, doc2)
            new = new_pending_review(doc2, article_key=ak, prev=review, reason="reselect")
            new["last_human_op_at"] = rv._now()
            _event(new, "reselect", by, {"reason": reason, "from_candidates_sha256": doc["candidates_sha256"], "round": doc2.get("round"),
                                          "rejected": [d for d in (doc2.get("reselect_log") or [])[-1:]]})
            return _replace_review(study_dir, new, review)
        if choice == "reextract":
            sel = g.select_from_candidates(doc, decision, "wait")   # exhausted以外・上限超過・reason欠落は例外
            assert sel["status"] == "REEXTRACT_REQUESTED"
            review.update(status=rv.ST_REEXTRACT_REQUESTED, selection={}, decision=decision, last_human_op_at=rv._now())
            _event(review, "reextract", by, {"reason": reason, "candidates_sha256": doc["candidates_sha256"]})
            return rv.save_review(study_dir, review, expected_revision=review["revision"], kind=KIND)
        if choice in ("top1", "top2", "omit"):
            sel = g.select_from_candidates(doc, decision, "wait")
            review["last_human_op_at"] = rv._now()
            rec = _finalized_record(doc, sel, review=review, decision=decision, by=by)
            rec["last_human_op_at"] = review["last_human_op_at"]
            return rv.save_review(study_dir, rec, expected_revision=review["revision"], kind=KIND)
        raise g.Part2ReviewError(f"choiceは top1/top2/omit/reselect/reextract のいずれか: {choice!r}")


def op_ng(study_dir: str, *, rank: int, reason: str, by: str) -> dict:
    """候補をNGにする(選択はしない)。候補listから除かれ(candidates_sha256が変わる)、共有registryに入る。以後の宣言は失効する。"""
    _need_by(by)
    if not (reason or "").strip():
        raise rv.KpReviewError("NG指定には理由が必要です")
    with rv.review_lock(study_dir, KIND, by):
        review, doc = _load_pair(study_dir)
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
            rv.store_add_ng(ak["family"], ak["slug"], LEVEL_KEY, ent, KIND)
        save_candidates_doc(study_dir, doc2)
        new = new_pending_review(doc2, article_key=ak, prev=review, reason="ng")
        new["last_human_op_at"] = rv._now()
        _event(new, "ng", by, {"rank": rank, "candidate_id": c["candidate_id"], "reason": reason})
        return _replace_review(study_dir, new, review)


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
        rv._cc().guard_grammar(study_dir, "unng")   # 確定内容保護(M6)
        ak = review.get("article_key") or {}
        removed = rv.store_remove_ng(ak["family"], ak["slug"], LEVEL_KEY, candidate_id=candidate_id, reason=reason, by=by, kind=KIND, sentence_key=skey)
        review["last_human_op_at"] = rv._now()
        _event(review, "unng", by, {"removed": sorted(set(removed)), "reason": reason, "sentence": sentence})
        rv.save_review(study_dir, review, expected_revision=review["revision"], kind=KIND)
        return sorted(set(removed))


# ============================================================
# 提示(依頼書)・状態一覧
# ============================================================
def render_request_md(doc: dict, review: dict, *, run_hint: str) -> str:
    req = g.review_request(doc)
    sha = doc["candidates_sha256"]
    L = [f"# Part 2 文法解説 Human Review 依頼(Advanced) round {doc.get('round', 1)}", "",
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
    base = f"{CLI} grammar-select --run {run_hint} --candidates-sha {sha} --by <名前>"
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
    L += [f"- 状況: `{CLI} status --run {run_hint}` / 表示: `{CLI} grammar-show --run {run_hint}`",
          f"- 不在として進める(明示宣言。このrun・この候補round限り): `{CLI} declare-absent --runs {run_hint} --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`",
          "", "再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・supportの再生成は行われません)。"]
    return "\n".join(L) + "\n"


def status_of(study_dir: str) -> dict:
    review, doc = load_review(study_dir), load_candidates(study_dir)
    if review is None:
        return {"study_dir": study_dir, "kind": "grammar", "status": "NO_REVIEW"}
    return {"study_dir": study_dir, "kind": "grammar", "status": review["status"], "round": review.get("round"),
            "reselect_count": review.get("reselect_count"), "reextract_count": review.get("reextract_count"),
            "candidates_sha256": review.get("candidates_sha256"), "selection": review.get("selection"),
            "mode_declaration": review.get("mode_declaration"), "revision": review.get("revision"),
            "n_candidates": len((doc or {}).get("candidates") or []), "exhausted": bool((doc or {}).get("exhausted")),
            "selection_signature": review.get("selection_signature")}


def discover_dirs(run_dir: str) -> list:
    """X: <run>/b1b/study_text / Z: <run>/study_text。文法のreview/候補ファイルのあるdirだけ返す。"""
    out = []
    for d in (f"{run_dir}/b1b/study_text", f"{run_dir}/study_text"):
        p = paths(d)
        if os.path.exists(p["review"]) or os.path.exists(p["candidates"]):
            out.append(d)
    return out
