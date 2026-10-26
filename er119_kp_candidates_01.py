# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02: KP候補(TOP 8)の生成(Opus M-1/M-7/R-1/R-2)。

- 候補生成は <kp_dir>/kp_candidates/round_<n>/work/ で行う(M-1)。既存関数(canonicalization等)が書く keywords_canonicalized.json は
  この作業dirのものであり、後段が読む <kp_dir>/keywords_canonicalized.json は finalize(er119_kp_human_review_01)だけが書く。
- 1 call目=Prompt 2(承認済み・無変更)で上位3件、2 call目=Prompt 2-V(er119_kp_prompt_2v_01)で追加最大5件(R-1)。
- Gate基準は既存のまま(validate / CMU / canonicalization / gloss再整合 / CMU post-canon / 記号 / 人称整合[Z] / SRC D1[Z] / Redundancy QA)。
  扱いだけを「attempt全体INVALID」から「そのitemだけ除外」へ(M-7: INVALIDはitem_reasonsのitemを除いた残りで再実行し全体PASSのみ受理)。
- Gate除外候補の補完(KP-GATE-DROP-BACKFILL-PRODUCTION-01、ユーザー正式採用): AIが選んだitemのうち最終的にGate除外された件数Eが1以上のとき、1回だけ最大E件を
  Prompt 2-V(再利用・本文無変更)で追加探索し、同一Gateを通して末尾へ追加する。初回に合格した候補は保持(入れ替えない)。flag EIGO_KP_BACKFILL(既定ON、er119_kp_backfill_01)。
- 外側retry(M-7c): 補完ON(既定)では候補0件と技術失敗のretryだけ。補完OFF(EIGO_KP_BACKFILL=0)では従来どおり『AUTO採用できる有効件数が3未満かつGate除外または救済済みauto不可が発生』
  の場合も候補list全体を置き換える(roundに内mergeしない)。
- 共有関数 sc.run_key_phrases は呼ばない。sc.run_key_phrase_selection / canonicalization / redundancy_qa は既存のまま再利用する。
"""
from __future__ import annotations

import contextvars
import functools
import json
import os
import shutil
import time
from typing import Callable, Optional

import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er105_kp_fulltext_selector_01 as ft
import er108_kp_cmu_lexicon_gate_01 as cmu
import er125_kp_rescue_production_01 as er125
import er119_kp_backfill_01 as bf
import er119_kp_human_review_01 as rv
import er119_kp_prompt_2v_01 as p2v

# R-5: 補完の人称整合(Z)の出力先を初回と分ける。person_repair_fnを返す側(er026のrunner等)は触らず、make_person_repair_fnが実行時にこの値を読む
# (補完のGate連鎖の実行中だけ_run_backfillがセットし、終了時に必ず戻す)。既定None=従来のdir。
_person_repair_subdir: contextvars.ContextVar = contextvars.ContextVar("kp_person_repair_subdir", default=None)

MAX_CANON_RERUN = 2   # M-7a: item除外後のcanonicalization再実行の上限(承認済みGateの受理条件=全体PASSは変えない)


def _containment(a_key: str, b_key: str) -> bool:
    ta, tb = a_key.split(), b_key.split()
    return bool(ta and tb) and (rv._is_subseq_tokens(ta, tb) or rv._is_subseq_tokens(tb, ta))


def run_vocab_selection(text: str, units: list, already_items: list, excluded: list, *, process: Optional[str] = None,
                        make_call_fn: Optional[Callable] = None, sleep_fn: Optional[Callable] = None,
                        max_attempts: int = ft.MAX_ATTEMPTS, shown_phrases: Optional[list] = None, note: Optional[str] = None) -> dict:
    """2 call目(Prompt 2-V)。item単位でvalidate / 重複(前記3件との同一・包含)/ 明示除外 / CMU を適用し、通ったものだけ返す。
    技術/parse失敗は最大max_attempts回。全て失敗ならstatus=FAILED(呼出側が外側retryへ)。0件はOK(適切な候補が不足=shortfall)。
    M-5/M-7(補完): shown_phrases=LLMに見せる『すでに選ばれた表現』(未指定=already_itemsのdisplay_phrase=従来どおり)。包含比較先(duplicate_of_top3)は
    常にalready_items(=call1の選定結果)のまま=Gateの意味を変えない。note=本文後置の既存exclusion note(2-V本文のshaは不変)。"""
    sleep_fn = sleep_fn if sleep_fn is not None else time.sleep
    already = [it["display_phrase"] for it in already_items]
    already_keys = [ft.phrase_key(p) for p in already]            # 包含比較先(duplicate_of_top3)。表示用とは分離(M-5)
    shown = list(shown_phrases) if shown_phrases is not None else already
    ex_keys = {ft.phrase_key(e["phrase"]): e for e in (excluded or [])}
    model = None if make_call_fn is not None else ft.resolve_model(process)
    attempts, messages = [], []
    for attempt in range(1, max_attempts + 1):
        msg = p2v.build_user_message(text, shown, diagnostic_note=note)
        assert p2v.prompt_prefix_intact(msg), "Prompt 2-Vが改変されている"
        messages.append(msg)
        fn = make_call_fn(msg) if make_call_fn is not None else p2v.make_vocab_selector_fn(msg, model=model)
        try:
            raw, model_id, response_id = fn()
        except ft.FulltextSelectionError as e:
            if isinstance(e, ft.ModelMismatchError):
                attempts.append({"attempt": attempt, "status": ft.STATUS_TECHNICAL_FAILED, "error": str(e)})
                if attempt < max_attempts:
                    sleep_fn(2)
                continue
            raise
        except Exception as e:   # noqa: BLE001  通信等の技術的失敗(retry対象)
            attempts.append({"attempt": attempt, "status": ft.STATUS_TECHNICAL_FAILED, "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                sleep_fn(2)
            continue
        try:
            selected = p2v.parse_selection(raw)
        except ft.ParseError as e:
            attempts.append({"attempt": attempt, "status": ft.STATUS_PARSE_FAILED, "error": str(e), "raw_text": raw})
            if attempt < max_attempts:
                sleep_fn(2)
            continue
        v = ft.validate_and_resolve([{"phrase": s["phrase"], "declared_word_count": s["declared_word_count"]} for s in selected], units)
        kept, dropped = [], []
        item_reasons = {ir["index"]: ir["reasons"] for ir in v["item_reasons"]}
        for rec in v["resolved"]:
            idx = rec["index"]
            phrase = rec["phrase"]
            pk = ft.phrase_key(phrase)
            reasons = list(item_reasons.get(idx) or [])
            stage = "validate" if reasons else None
            if not reasons and any(pk == k or _containment(pk, k) for k in already_keys):
                reasons, stage = ["前記の選定済み表現と同一または包含関係(重複)"], "duplicate_of_top3"
            opk = ft.phrase_key((rec.get("selection_rescue") or {}).get("original_phrase") or "") if rec.get("selection_rescue") else None
            if not reasons and opk and opk in ex_keys and pk not in ex_keys:       # R6: 救済前の元句が除外指定(Human NG/外側retry)なら救済形も除外
                pk = opk
            if not reasons and pk in ex_keys:
                e = ex_keys[pk]
                reasons, stage = ["除外指定の語句(" + (" / ".join(e.get("reasons") or ["不適合"])) + ")"], e.get("source") or "excluded"
            if not reasons:
                cr = cmu.reasons_for_phrase(phrase)
                if cr:
                    reasons, stage = cr, "cmu"
            if reasons:
                dropped.append({"raw_rank": idx + 1, "phrase": phrase, "stage": stage, "reasons": reasons, "origin": "call2"})
            else:
                kept.append({"resolved": rec, "reason_ja": selected[idx]["reason_ja"], "raw_rank": idx + 1})
        if len(kept) > p2v.SELECTOR_2V_MAX_ITEMS:
            for k in kept[p2v.SELECTOR_2V_MAX_ITEMS:]:
                dropped.append({"raw_rank": k["raw_rank"], "phrase": k["resolved"]["phrase"], "stage": "overflow",
                                "reasons": [f"最大{p2v.SELECTOR_2V_MAX_ITEMS}件を超過(下位のため除外)"], "origin": "call2"})
            kept = kept[:p2v.SELECTOR_2V_MAX_ITEMS]
        attempts.append({"attempt": attempt, "status": "OK", "model": model_id, "response_id": response_id,
                         "n_selected": len(selected), "n_kept": len(kept), "n_dropped": len(dropped)})
        return {"status": "OK", "kept": kept, "dropped": dropped, "model_id": model_id, "response_id": response_id,
                "attempts": attempts, "messages": messages, "raw_text": raw}
    return {"status": "FAILED", "kept": [], "dropped": [], "model_id": None, "response_id": None, "attempts": attempts, "messages": messages}


def _canon_item_failures(work_dir: str) -> dict:
    """canonicalization INVALIDの項目別理由 {rank: [reasons]}。最終attemptのitem_reasonsのうちrankが特定できるものだけ(特定できない=構造不正はgate retryに任せる)。"""
    attempts = sc._kp_canon_reasons(work_dir) or []
    if not attempts:
        return {}
    out = {}
    for ir in attempts[-1].get("item_reasons") or []:
        if ir.get("rank") is not None:
            out[ir["rank"]] = list(ir.get("reasons") or [])
    return out


def make_z_src_fn(text: str, level: str) -> Callable:
    """Z限定のSRC D1(z_sentence_id_posthoc_v1)を候補単位に写す(M-7b)。returns fn(items)->(new_by_rank, dropped_by_rank)。
    apply_to_kp(既存)のreportのうち、解決できたitemはnew_itemsへ、曖昧/未解決のrankは該当候補だけ除外(dropped stage=src_d1)。"""
    def fn(items: list):
        import er026_family_z_src_posthoc_01 as srcz
        rep = srcz.apply_to_kp({"items": items}, text, level)
        new = {it["rank"]: it for it in rep["new_items"]}
        drop = {}
        for r in rep["ambiguous"]:
            drop[r] = ["SRC D1: 出典文が一意に決まらない(曖昧)"]
        for r in rep["unresolved"]:
            drop[r] = ["SRC D1: 出典文を特定できない(未解決)"]
        return new, drop
    return fn


def make_person_repair_fn(text: str, factory: Callable, work_dir: str, article_id: str, subdir: str = "gloss_person_repair") -> Callable:
    """Z限定の人称整合(_gloss_person_gate相当)を候補単位に適用(M-7b)。決定論checkで不整合のitemだけ既存align_glossesで修復し、
    修復できなければ gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED のまま返す(候補に gloss_hr_pending 旗が付く)。"""
    def fn(merged: dict) -> dict:
        mism = ga.select_person_mismatches(merged["items"])
        if not mism:
            return merged
        ranks = [it["rank"] for it in mism]
        sub = _person_repair_subdir.get()
        aligned = ga.align_glosses(merged, text, factory, out_dir=f"{work_dir}/{subdir}" + (f"_{sub}" if sub else ""), article_id=article_id,
                                   enabled=True, only_ranks=ranks)
        return aligned["merged"]
    return fn


def _hr_pending(item: dict) -> bool:
    return item.get("gloss_alignment_status") in (ga.STATUS_HR_REQUIRED, ga.STATUS_OLD_FAILED)


def _screen_human_ng(originals: list, meta: list, ng_entries: list, dropped: list) -> list:
    """選定表層形でHuman NGを再照合し、通った項目のindex listを返す(NG一致はdroppedへstage=human_ng)。"""
    live = []
    for i, (o, m) in enumerate(zip(originals, meta)):
        if rv.match_ng({"candidate_id": rv.candidate_id_for(m["selection_phrase"]), "selection_phrase": m["selection_phrase"], "used_form": ""},
                       ng_entries) == "exact":
            dropped.append({"raw_rank": m["raw_rank"], "phrase": m["selection_phrase"], "stage": "human_ng",
                            "reasons": ["Humanが不適切(NG)と指定済み"], "origin": m["origin"]})
        else:
            live.append(i)
    return live


def _gate_chain(text: str, work: str, article_id: str, process: Optional[str], originals: list, meta: list, live: list, dropped: list, *,
                ng_entries: list, canon_fn: Callable, src_fn: Optional[Callable], person_repair_fn: Optional[Callable],
                stages: dict, stage_prefix: str = "") -> dict:
    """canonicalization(+gloss再整合)以降のGate連鎖(初回・補完で共通。R-6の純抽出)。外側ループの制御(continue/return)は持たず、statusを返す(M-6)。
    droppedは呼出側のlistへ破壊的に追記する(順序・内容は抽出前と同一)。
    returns {"status": "OK", "cands": [ai_rank未付与の候補]} | {"status": "CANON_FAILED", "canon_fail": canonicalization status}。"""
    # ---- canonicalization(+gloss再整合)。INVALIDはitem_reasonsのitemを除外し、残りで再実行。全体PASS/REVIEW_REQUIREDのみ受理(M-7a)
    canon, merged, canon_fail = None, None, None
    for rerun in range(MAX_CANON_RERUN + 1):
        items_for_canon = [dict(originals[i], rank=n) for n, i in enumerate(live, start=1)]
        canon = canon_fn(text, items_for_canon, work, article_id, process=process)
        st = canon.get("status")
        stages[f"{stage_prefix}canonicalization_{rerun}"] = st
        if st in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            merged = canon["merged"]
            break
        bad = _canon_item_failures(work) if st == "CANONICALIZATION_INVALID" else {}
        if bad and rerun < MAX_CANON_RERUN and len(bad) < len(live):
            new_live = []
            for n, i in enumerate(live, start=1):
                if n in bad:
                    dropped.append({"raw_rank": meta[i]["raw_rank"], "phrase": meta[i]["selection_phrase"],
                                    "stage": "canonicalization", "reasons": bad[n], "origin": meta[i]["origin"]})
                else:
                    new_live.append(i)
            live = new_live
            continue
        canon_fail = st
        break
    if merged is None:
        return {"status": "CANON_FAILED", "canon_fail": canon_fail}
    items = [json.loads(json.dumps(x)) for x in merged["items"]]   # rank 1..len(live)
    idx_of = {it["rank"]: live[it["rank"] - 1] for it in items}      # rank -> originals index

    def drop_rank(rank, stage, reasons):
        nonlocal items
        i = idx_of[rank]
        dropped.append({"raw_rank": meta[i]["raw_rank"], "phrase": meta[i]["selection_phrase"], "stage": stage,
                        "reasons": list(reasons), "origin": meta[i]["origin"]})
        items = [x for x in items if x["rank"] != rank]
    # CMU post-canon
    chk = cmu.canonicalized_check(items)
    for b in chk["bad"]:
        drop_rank(b["rank"], "cmu_post_canon", ["基本形化・一般化後「%s」にCMU未登録語 %s" % (b["used_form"], ", ".join(b["unregistered"] or []))])
    # 記号
    findings = sc.detect_key_phrase_symbol_findings(items)
    for rank in sorted({f["rank"] for f in findings if sc.safety.symbol_gate_requires_stop([f])}):
        drop_rank(rank, "symbol", [f"音声化禁止記号: {f.get('token')}" for f in findings if f["rank"] == rank])
    # 人称整合(Z)
    if person_repair_fn is not None and items:
        mdoc = person_repair_fn({"items": items})
        by = {x["rank"]: x for x in mdoc["items"]}
        items = [by.get(x["rank"], x) for x in items]
    # SRC D1(Z)
    if src_fn is not None and items:
        new_by, drop_by = src_fn(items)
        for rank, reasons in drop_by.items():
            if any(x["rank"] == rank for x in items):
                drop_rank(rank, "src_d1", reasons)
        items = [new_by.get(x["rank"], x) for x in items]
    # 候補ID・NG(基本形化後のused_form照合)
    cands = []
    for it in items:
        i = idx_of[it["rank"]]
        m = meta[i]
        cand = {"candidate_id": rv.candidate_id_for(m["selection_phrase"]), "selection_phrase": m["selection_phrase"],
                "used_form": it.get("used_form") or it.get("key_phrase"), "japanese_gloss": it.get("japanese_gloss"),
                "source_sentence": it.get("source_sentence"), "source_sentence_id": it.get("source_sentence_id"),
                "word_count": ft.count_words(it.get("used_form") or ""), "reason_ja": m["reason_ja"], "origin": m["origin"],
                "raw_rank": m["raw_rank"], "item": it}
        cand["kind"] = bf.kind_of_phrase(cand["used_form"] or "")     # F-2/R-1: 単語(1語)/フレーズ。HR依頼書・フォームの種類別表示用
        mt = rv.match_ng(cand, ng_entries)
        mo = er125.ng_match_originals(cand, ng_entries, rv.match_ng, rv.candidate_id_for) if it.get("rescue") else None    # 救済前の元句もHuman NG照合
        if mt == "exact" or mo == "exact":
            dropped.append({"raw_rank": m["raw_rank"], "phrase": m["selection_phrase"], "stage": "human_ng",
                            "reasons": ["基本形化後の表現がNG指定と一致" if mt == "exact" else "救済前の元の表現がNG指定と一致"], "origin": m["origin"]})
            continue
        if mt is None and mo == "similar":
            mt = "similar"
        qa_fail = it.get("qa_overall_status") == "REVIEW_REQUIRED"
        hr = _hr_pending(it)
        sim = mt == "similar"
        cand["flags"] = {"qa_fail": qa_fail, "gloss_hr_pending": hr, "similar_to_ng": sim, "redundant_with": []}
        cand["gates"] = {"validate": "PASS", "cmu": "PASS", "canonicalization": "REVIEW_REQUIRED" if qa_fail else "PASS",
                         "gloss": "HR_PENDING" if hr else "ALIGNED", "symbol": "PASS",
                         "src_d1": "PASS" if src_fn is not None else "NA"}
        cand["auto_eligible"] = not (qa_fail or hr or sim)
        cand["human_selectable"] = True
        er125.annotate_candidate(cand)     # [H4] 救済の旗・gates・rescueメタ。auto_eligibleは緩めない(AND のみ)
        cands.append(cand)
    return {"status": "OK", "cands": cands}


def generate_candidates(*args, **kwargs) -> dict:
    """KP候補生成の入口(X/Y/Z共通)。KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02(Opus M2): 救済フロー(H1/H2)は本関数の実行中
    (er125.rescue_context)だけ有効。終了時(例外含む)に必ず無効へ戻す。引数・戻り値は_generate_candidates_impl(従来の本体)と同一。"""
    with er125.rescue_context():
        return _generate_candidates_impl(*args, **kwargs)


def _generate_candidates_impl(text: str, kp_dir: str, article_id: str, source_level: str, level: str, round_no: int, ng_entries: list, *,
                        process: Optional[str] = None, stop_check_fn: Optional[Callable] = None,
                        max_outer: int = sc.KP_OUTER_RETRY_MAX, src_fn: Optional[Callable] = None,
                        person_repair_fn: Optional[Callable] = None, select_fn: Optional[Callable] = None,
                        canon_fn: Optional[Callable] = None, redundancy_fn: Optional[Callable] = None,
                        vocab_call_fn: Optional[Callable] = None, sleep_fn: Optional[Callable] = None) -> dict:
    """returns {"ok": True, "doc": 候補doc(candidates_sha256未付与)} | {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": [...]}。
    作業はすべて <kp_dir>/kp_candidates/round_<n>/work/ 配下。<kp_dir>/keywords_canonicalized.json には触れない(M-1)。"""
    import er030_key_phrase_db_hybrid_core_01 as core
    select_fn = select_fn or sc.run_key_phrase_selection
    if canon_fn is None:
        # [H3'] 救済有効(文脈内かつkill switch未OFF)のときだけ rescue=True を明示。無効ならこれまでと同一の関数をそのまま使う。test注入のcanon_fnは影響を受けない
        canon_fn = functools.partial(sc.run_key_phrase_canonicalization, rescue=True) if er125.rescue_active() else sc.run_key_phrase_canonicalization
    redundancy_fn = redundancy_fn or sc.run_key_phrase_redundancy_qa
    work = f"{kp_dir}/kp_candidates/round_{round_no}/work"
    os.makedirs(work, exist_ok=True)
    units = core.build_sentence_units(text)
    excluded = [{"phrase": e.get("phrase") or e.get("phrase_key"), "reasons": ["Humanが不適切(NG)と指定: " + (e.get("reason") or "")],
                 "source": "human_ng"} for e in ng_entries]
    log, dropped_all = [], []
    cands_final = None
    outer = 0
    backfill_on = bf.backfill_enabled()      # 単一読取。生成1回につき1回だけ読み、docへ記録する(途中で変わっても同一生成内は不変)
    while True:
        outer += 1
        if stop_check_fn is not None:
            stop_check_fn(f"kp_candidates:{article_id}:round{round_no}:attempt{outer}")
        entry = {"outer_attempt": outer, "excluded_in": [e["phrase"] for e in excluded], "stages": {}}
        last = outer >= max_outer
        note = ft.build_exclusion_note(excluded) if excluded else None
        sel_kwargs = {"excluded_phrases": [dict(e) for e in excluded]} if excluded else {}
        # ---- call 1: Prompt 2(承認済み・無変更)で上位3件
        if backfill_on:
            bf.clear_call1_metadata(work)    # M-1: 前周のmetadataを読み違えない
        sel = select_fn(text, work, article_id, source_level, process=process, diagnostic_note=(note or None),
                        kp_backend=sc.FULLTEXT_BACKEND_ID, **sel_kwargs)
        entry["call1_status"] = sel.get("status")
        if sel.get("status") != "KEY_WORDS_STRUCTURE_PASS":
            entry["failure"] = "call1_selection_failed"
            log.append(entry)
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        call1 = list(sel["original_items"])
        # M-1: call1(Prompt 2)の最終attemptでitem単位に除外された句(CMU未登録・除外指定の再選択)もEに数える。er105は無変更でmetadataから読む
        call1_dropped = bf.read_call1_dropped(work, excluded) if backfill_on else []
        # ---- call 2: Prompt 2-V(追加最大5件+理由)
        v2 = run_vocab_selection(text, units, call1, excluded, process=process, make_call_fn=vocab_call_fn, sleep_fn=sleep_fn)
        entry["call2_status"] = v2["status"]
        if v2["status"] != "OK":
            entry["failure"] = "call2_selection_failed"
            log.append(entry)
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        originals, meta, dropped = [], [], list(call1_dropped) + list(v2["dropped"])
        for n, it in enumerate(call1, start=1):
            o = dict(it)
            originals.append(o)
            meta.append({"origin": "call1", "raw_rank": n, "reason_ja": "", "selection_phrase": it["display_phrase"]})
        extra = ft.build_original_items([k["resolved"] for k in v2["kept"]])
        for k, it in zip(v2["kept"], extra):
            originals.append(dict(it))
            meta.append({"origin": "call2", "raw_rank": k["raw_rank"], "reason_ja": k["reason_ja"], "selection_phrase": it["display_phrase"]})
        # call 1の件は選定後にHuman NGで落ちることはない(excluded_phrasesで除外済み)。念のため選定表層形でNG再照合
        live = _screen_human_ng(originals, meta, ng_entries, dropped)
        if not live:
            entry["failure"] = "no_live_items"
            log.append(entry)
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        # ---- canonicalization(+gloss再整合)以降のGate連鎖(初回・補完で共通の_gate_chain)
        chain = _gate_chain(text, work, article_id, process, originals, meta, live, dropped, ng_entries=ng_entries, canon_fn=canon_fn,
                            src_fn=src_fn, person_repair_fn=person_repair_fn, stages=entry["stages"])
        if chain["status"] != "OK":
            entry["failure"] = f"canonicalization_{chain['canon_fail']}"
            log.append(entry)
            dropped_all += dropped
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        cands = chain["cands"]
        # ai_rank(Gate通過後の連番。call1の順→call2の順)
        for n, c in enumerate(cands, start=1):
            c["ai_rank"] = n
        gate_dropped = [d for d in dropped if d["stage"] not in ("human_ng", "overflow", "duplicate_of_top3", "excluded")]
        # ---- Gate除外候補の補完(承認済み仕様。配線位置=ai_rank付番後・Redundancy QAの前 [R-10])。初回の候補は不変・補完分は末尾へ追加・1周1回だけ
        if backfill_on:
            backfill_rec, new_cands, bdropped = _run_backfill(
                text=text, units=units, work=work, article_id=article_id, process=process, round_no=round_no, outer=outer, cands=cands,
                dropped=dropped, call1=call1, excluded=excluded, ng_entries=ng_entries, canon_fn=canon_fn, src_fn=src_fn,
                person_repair_fn=person_repair_fn, stop_check_fn=stop_check_fn, vocab_call_fn=vocab_call_fn, sleep_fn=sleep_fn,
                stages=entry["stages"])
            cands = cands + new_cands
            dropped = dropped + bdropped
        else:
            backfill_rec = bf.disabled_record()
        entry["backfill"] = {"triggered": backfill_rec["triggered"], "status": backfill_rec["status"],
                             "E": (backfill_rec.get("E") or {}).get("total"), "added": len(backfill_rec.get("added") or [])}
        # Redundancy QA(候補全体1回=提示用の旗。確定集合にはfinalizeで別途再適用=M-8)
        red = {"status": "SKIPPED", "duplicate_pairs": []}
        if len(cands) >= 2:
            ritems = []
            for c in cands:
                it = json.loads(json.dumps(c["item"]))
                it["rank"] = c["ai_rank"]
                ritems.append(it)
            r = redundancy_fn(text, ritems, work, article_id, process=process)
            red = {"status": r.get("status"), "duplicate_pairs": r.get("duplicate_pairs") or [], "model_id": r.get("model_id")}
            by_rank = {c["ai_rank"]: c for c in cands}
            for p in red["duplicate_pairs"]:
                a, b = by_rank.get(p.get("rank_a")), by_rank.get(p.get("rank_b"))
                if a and b:
                    a["flags"]["redundant_with"].append(b["candidate_id"])
                    b["flags"]["redundant_with"].append(a["candidate_id"])
        entry["stages"]["redundancy_qa"] = red["status"]
        n_auto = sum(1 for c in cands if c["auto_eligible"])
        # M3: 救済済みだがauto不可(gloss再整合/QA再判定が未達)の候補はdroppedに入らないため、別途retry条件に数える。F1累積除外には入れない(再選定されてもHR候補として残る)
        rescued_not_auto = [c["candidate_id"] for c in cands if er125.rescue_blocks_auto(c)]
        entry.update({"n_candidates": len(cands), "n_auto_eligible": n_auto, "n_gate_dropped": len(gate_dropped),
                      "n_rescued": sum(1 for c in cands if c.get("rescue")), "rescued_not_auto": rescued_not_auto})
        log.append(entry)
        dropped_all += dropped
        # 外側retry条件(M-7c): AUTO採用可能件数<3 かつ Gate除外が発生 かつ 回数が残っている場合のみ。候補list全体を置き換える。
        # 補完ON(既定)ではこの脚を撤去(M-2/M-3): 初回に合格した候補を保持し入れ替えない(ユーザー§3-1)。除外分は上の補完(1回)で埋める。
        # 候補0件(下のnot cands)と技術失敗(call1/call2/live0/canon全体失敗)のretryは存続。EIGO_KP_BACKFILL=0では現行条件へ完全復帰。
        if (not backfill_on) and n_auto < rv.KP_FINAL_MAX and (gate_dropped or rescued_not_auto) and not last:
            seen = {ft.phrase_key(e["phrase"]) for e in excluded}
            for d in gate_dropped:
                if ft.phrase_key(d["phrase"]) not in seen:
                    excluded.append({"phrase": d["phrase"], "reasons": list(d["reasons"]), "source": d["stage"]})
                    seen.add(ft.phrase_key(d["phrase"]))
            dropped_all = []
            continue
        if not cands:
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        cands_final = (cands, red, dropped, v2, sel, backfill_rec)
        break
    cands, red, dropped, v2, sel, backfill_rec = cands_final
    doc = {"level": level, "prompt_ids": {"call1": "kp_prompt_2", "call2": p2v.PROMPT_2V_ID},
           "prompt_sha256": {"call1": ft.PROMPT_2_SHA256, "call2": p2v.PROMPT_2V_SHA256},
           "model_requested": ft.SELECTION_MODEL_ID, "model_id": {"call1": sel.get("model_id"), "call2": v2.get("model_id")},
           "generated_at": rv._now(), "round": round_no, "candidates": cands, "dropped": dropped, "redundancy_qa": red,
           "shortfall": len(cands) < rv.KP_CANDIDATE_MAX, "outer_attempts": outer, "outer_retry_log": log,
           "rescue_provenance": er125.provenance(),      # R2: 辞書sha・lexicon_status・rescue_enabled・schema(resume時にドリフトをlogのみ)
           "backfill": backfill_rec,                     # F-2: 補完の記録(enabled/triggered/status/E[種類別]/N/added/surplus/dropped/sha/model_id)
           "shortfall_detail": _shortfall_detail(cands, backfill_rec)}
    with open(f"{work}/outer_retry_log.json", "w", encoding="utf-8") as f:
        json.dump({"attempts": log, "excluded_phrases": excluded}, f, ensure_ascii=False, indent=2)
    return {"ok": True, "doc": doc}


def _shortfall_detail(cands: list, rec: dict) -> dict:
    """F-2: 上限未達の内訳(フォームが『何件足りず、なぜか』を表示できる)。shortfall(bool)は従来どおり別に持つ。"""
    e = rec.get("E") or {}
    added = rec.get("added") or []
    n_add = {bf.KIND_PHRASE: sum(1 for a in added if a.get("kind") == bf.KIND_PHRASE), bf.KIND_WORD: sum(1 for a in added if a.get("kind") == bf.KIND_WORD)}
    return {"n_candidates": len(cands), "cap": rv.KP_CANDIDATE_MAX, "missing": max(0, rv.KP_CANDIDATE_MAX - len(cands)),
            "E_total": e.get("total"), "backfilled": len(added),
            "unfilled_by_kind": ({bf.KIND_PHRASE: max(0, (e.get("phrase") or 0) - n_add[bf.KIND_PHRASE]),
                                  bf.KIND_WORD: max(0, (e.get("word") or 0) - n_add[bf.KIND_WORD])} if rec.get("triggered") else None)}


def _by_stage(dropped: list) -> dict:
    out: dict = {}
    for d in dropped:
        out[d.get("stage")] = out.get(d.get("stage"), 0) + 1
    return out


def _run_backfill(*, text: str, units: list, work: str, article_id: str, process: Optional[str], round_no: int, outer: int, cands: list,
                  dropped: list, call1: list, excluded: list, ng_entries: list, canon_fn: Callable, src_fn: Optional[Callable],
                  person_repair_fn: Optional[Callable], stop_check_fn: Optional[Callable], vocab_call_fn: Optional[Callable],
                  sleep_fn: Optional[Callable], stages: dict) -> tuple:
    """Gate除外候補の補完(ユーザー正式採用 §3-1〜3-3、DESIGN_02)。returns (backfill記録, 追加候補[ai_rank付き], 補完側のdropped)。
    初回の cands / dropped は変更しない(初回合格候補の保持)。補完は1回だけ(内容起因の再callなし。技術/parse失敗の再試行は2-Vの既存2回まで)。
    補完側の失敗(call失敗・live 0・canonicalization全体失敗・技術例外)は status=FAILED として初回候補で続行する(M-6)。
    FulltextSelectionError(routing違反等)とSTOP(M-4)は握らず伝播させる(R-8)。"""
    counts = bf.count_exclusions(dropped, cands)
    if counts["total"] == 0:
        return bf.not_triggered_record(counts, "E=0"), [], []                 # LLM 0
    plan = bf.plan_quota(counts, len(cands), rv.KP_CANDIDATE_MAX)
    if not cands or plan["total"] <= 0:
        return bf.not_triggered_record(counts, "no_candidate" if not cands else "no_room"), [], []
    if stop_check_fn is not None:                                              # M-4: 新しい課金点でもSTOP通知を迂回しない(try外=伝播)
        stop_check_fn(f"kp_backfill:{article_id}:round{round_no}:attempt{outer}")
    rec = {"enabled": True, "triggered": True, "status": bf.ST_FAILED, "failure": None, "E": bf.e_public(counts),
           "N": {k: plan[k] for k in ("room", "total", "phrase_wanted", "word_wanted", "capped")},
           "prompt_id": p2v.PROMPT_2V_ID, "prompt_sha256": p2v.PROMPT_2V_SHA256, "model_id": None, "response_id": None,
           "attempts": [], "added": [], "surplus": [], "dropped_by_stage": {}}
    bdropped: list = []
    try:
        rejected = bf.rejected_entries(excluded, dropped)
        v2b = run_vocab_selection(text, units, call1, rejected + bf.existing_entries(cands), process=process, make_call_fn=vocab_call_fn,
                                  sleep_fn=sleep_fn, shown_phrases=bf.shown_phrases(cands), note=(ft.build_exclusion_note(rejected) or None))
        rec["attempts"], rec["model_id"], rec["response_id"] = v2b["attempts"], v2b["model_id"], v2b["response_id"]
        if v2b["status"] != "OK":
            rec["failure"] = "call2_selection_failed"
            return rec, [], []
        bdropped = [dict(d, origin="backfill") for d in v2b["dropped"]]
        originals, meta = [], []
        extra = ft.build_original_items([k["resolved"] for k in v2b["kept"]])
        for k, it in zip(v2b["kept"], extra):
            originals.append(dict(it))
            meta.append({"origin": "backfill", "raw_rank": k["raw_rank"], "reason_ja": k["reason_ja"], "selection_phrase": it["display_phrase"]})
        if not originals:                       # 適切な候補が無い(LLMが0件/全てGate不合格)=上限未達を許容(§3-2)
            rec.update(status=bf.ST_OK, dropped_by_stage=_by_stage(bdropped))
            return rec, [], bdropped
        live = _screen_human_ng(originals, meta, ng_entries, bdropped)
        if not live:
            rec.update(failure="no_live_items", dropped_by_stage=_by_stage(bdropped))
            return rec, [], bdropped
        bwork = f"{work}/backfill_1"
        os.makedirs(bwork, exist_ok=True)
        token = _person_repair_subdir.set("backfill")        # R-5: 補完の人称整合は別dirへ(初回の監査用成果物を上書きしない)
        try:
            chain = _gate_chain(text, bwork, article_id, process, originals, meta, live, bdropped, ng_entries=ng_entries, canon_fn=canon_fn,
                                src_fn=src_fn, person_repair_fn=person_repair_fn, stages=stages, stage_prefix="backfill_")
        finally:
            _person_repair_subdir.reset(token)
        if chain["status"] != "OK":
            rec.update(failure=f"canonicalization_{chain['canon_fail']}", dropped_by_stage=_by_stage(bdropped))
            return rec, [], bdropped
        # R-3: 基本形化後のused_formが既存候補(または先に採った補完候補)と完全一致=重複として捨てる(Nに数えない・再callしない)。candidate_id衝突も同様
        have_ids = {c["candidate_id"] for c in cands}
        have_forms = {ft.phrase_key(c.get("used_form") or "") for c in cands}
        uniq = []
        for c in chain["cands"]:
            uk = ft.phrase_key(c.get("used_form") or "")
            if c["candidate_id"] in have_ids or uk in have_forms:
                bdropped.append({"raw_rank": c["raw_rank"], "phrase": c["selection_phrase"], "stage": "backfill_duplicate",
                                 "reasons": ["基本形化後の表現が既存候補と同一"], "origin": "backfill"})
                continue
            have_ids.add(c["candidate_id"])
            have_forms.add(uk)
            uniq.append(c)
        taken, surplus = bf.pick_backfill(uniq, counts, plan)                  # 種類別の先頭E_phrase/E_word件(R-1)。余りは候補にしない
        for n, c in enumerate(taken, start=len(cands) + 1):
            c["ai_rank"] = n
        rec.update(status=bf.ST_OK, dropped_by_stage=_by_stage(bdropped),
                   added=[{"candidate_id": c["candidate_id"], "kind": c["kind"], "used_form": c["used_form"], "ai_rank": c["ai_rank"]} for c in taken],
                   surplus=[{"candidate_id": c["candidate_id"], "kind": c["kind"], "used_form": c["used_form"]} for c in surplus])
        return rec, taken, bdropped
    except Exception as e:      # noqa: BLE001  R-8: 技術失敗だけ握る。routing違反(FulltextSelectionError)・STOPは伝播
        if bf.is_propagating_exception(e):
            raise
        rec.update(status=bf.ST_FAILED, failure=f"technical:{type(e).__name__}: {e}", dropped_by_stage=_by_stage(bdropped))
        return rec, [], []


def make_generate_fn(text: str, kp_dir: str, article_id: str, source_level: str, level: str, process: str, **kw) -> Callable:
    def generate(round_no: int, ng_entries: list) -> dict:
        return generate_candidates(text, kp_dir, article_id, source_level, level, round_no, ng_entries, process=process, **kw)
    return generate


def make_redundancy_fn(text: str, kp_dir: str, article_id: str, process: str, *, redundancy_fn: Optional[Callable] = None) -> Callable:
    """確定集合のRedundancy QA(M-8)。出力は <kp_dir>/final_redundancy_qa/<set>/ へ(kp_dir直下を汚さない)。"""
    fn = redundancy_fn or sc.run_key_phrase_redundancy_qa

    def redundancy(items: list, name: str) -> dict:
        d = f"{kp_dir}/final_redundancy_qa/{name}"
        os.makedirs(d, exist_ok=True)
        return fn(text, items, d, article_id, process=process)
    return redundancy


def candidate_doc_from_items(items: list, level: str, *, round_no: int = 1, reasons: Optional[list] = None,
                             origin_split: int = 3) -> dict:
    """test/mock用: 完成したKP item(canonicalization・gloss済みの形)のlistから候補docを作る(LLM 0)。
    実の生成(generate_candidates)と同じスキーマ。先頭origin_split件=call1、残り=call2。"""
    cands, seen_ids = [], set()
    for n, it in enumerate(items, start=1):
        sp = it.get("source_span") or it.get("display_phrase") or it.get("used_form")
        it2 = json.loads(json.dumps(it))
        it2["rank"] = n
        cid = rv.candidate_id_for(sp)
        if cid in seen_ids:   # fixture用: 同一句が複数あっても候補IDは一意にする
            cid = f"{cid}_{n}"
        seen_ids.add(cid)
        qa_fail = it2.get("qa_overall_status") == "REVIEW_REQUIRED"   # 実の生成(generate_candidates)と同じ旗: HR/QA FAILはAUTO対象外
        hr = _hr_pending(it2)
        cands.append({"candidate_id": cid, "selection_phrase": sp, "used_form": it2.get("used_form") or it2.get("key_phrase"),
                      "japanese_gloss": it2.get("japanese_gloss"), "source_sentence": it2.get("source_sentence"),
                      "source_sentence_id": it2.get("source_sentence_id"), "word_count": ft.count_words(it2.get("used_form") or ""),
                      "reason_ja": (reasons or [""] * len(items))[n - 1], "origin": "call1" if n <= origin_split else "call2",
                      "raw_rank": n if n <= origin_split else n - origin_split,
                      "flags": {"qa_fail": qa_fail, "gloss_hr_pending": hr, "similar_to_ng": False, "redundant_with": []},
                      "gates": {"validate": "PASS", "cmu": "PASS", "canonicalization": "REVIEW_REQUIRED" if qa_fail else "PASS",
                                "gloss": "HR_PENDING" if hr else "ALIGNED", "symbol": "PASS", "src_d1": "NA"},
                      "auto_eligible": not (qa_fail or hr), "human_selectable": True, "ai_rank": n, "item": it2,
                      "kind": bf.kind_of_phrase(it2.get("used_form") or it2.get("key_phrase") or "")})
    return {"level": level, "prompt_ids": {"call1": "mock", "call2": "mock"}, "prompt_sha256": {}, "model_requested": "mock",
            "model_id": {}, "generated_at": rv._now(), "round": round_no, "candidates": cands, "dropped": [],
            "redundancy_qa": {"status": "SKIPPED", "duplicate_pairs": []}, "shortfall": len(cands) < rv.KP_CANDIDATE_MAX,
            "outer_attempts": 1, "outer_retry_log": []}
