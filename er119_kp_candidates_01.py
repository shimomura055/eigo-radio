# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02: KP候補の生成(Opus M-1/M-7/R-1/R-2)。
KP-PHRASE7-WORD5-PRODUCTION-01 委任_02(2026-10-27 APPROVED_FOR_PRODUCTION): 候補は**フレーズ最大7(P7)+単語最大5(W5')=最大12件**。
call1=P7、call2=W5'(KP含有語は除外・1語のみ=not_single_word Gate)。補完は種類別(フレーズ=P7・単語=W5'、直列、各1回)。旧Prompt 2/2-Vは残置(新経路では使わない)。

- 候補生成は <kp_dir>/kp_candidates/round_<n>/work/ で行う(M-1)。既存関数(canonicalization等)が書く keywords_canonicalized.json は
  この作業dirのものであり、後段が読む <kp_dir>/keywords_canonicalized.json は finalize(er119_kp_human_review_01)だけが書く。
- 1 call目=P7(最大7件・順位付け・理由つき)、2 call目=W5'(単語最大5件・理由つき)。(旧: Prompt 2で3件+Prompt 2-Vで最大5件。本文は残置)
- Gate基準は既存のまま(validate / CMU / canonicalization / gloss再整合 / CMU post-canon / 記号 / 人称整合[Z] / SRC D1[Z] / Redundancy QA)。
  扱いだけを「attempt全体INVALID」から「そのitemだけ除外」へ(M-7: INVALIDはitem_reasonsのitemを除いた残りで再実行し全体PASSのみ受理)。
- Gate除外候補の補完(KP-GATE-DROP-BACKFILL-PRODUCTION-01、ユーザー正式採用): AIが選んだitemのうち最終的にGate除外された件数Eが1以上のとき、1回だけ種類別の空きとE_kindの小さい方まで
  P7(フレーズ)/W5'(単語)で追加探索し、同一Gateを通して末尾へ追加する。初回に合格した候補は保持(入れ替えない)。flag EIGO_KP_BACKFILL(既定ON、er119_kp_backfill_01)。
- 外側retry(M-7c): 補完ON(既定)では候補0件と技術失敗のretryだけ。補完OFF(EIGO_KP_BACKFILL=0)では従来どおり『AUTO採用できる有効件数が3未満かつGate除外または救済済みauto不可が発生』
  の場合も候補list全体を置き換える(roundに内mergeしない)。
- 共有関数 sc.run_key_phrases は呼ばない。sc.run_key_phrase_selection / canonicalization / redundancy_qa は既存のまま再利用する。
- KP一般化N5方式(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01、2026-10-30ユーザー正式決定 APPROVED_FOR_PRODUCTION、er138): 既定ON・flagなし。
  L1=call1(P7)直後に『P7∪B1過剰生成 -> 既存Gate -> SEL(塊価値判定) -> pick(cap7)』(`_generate_candidates_impl`、補完は`_run_backfill`内でSEL+pick)。
  L3=`_gate_chain`内でcanonicalization直後・CMU post-canonの前に GEN5->VER5->CHK5(N5形=used_form=key_phrase、本文根拠=source_span)。除外はstage=n5_*(Opus M1/M3)。
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
import er119_kp_difficulty_01 as dg
import er119_kp_human_review_01 as rv
import er119_kp_prompt_2v_01 as p2v
import er119_kp_p7w5_prompts_01 as p7w5
import er138_kp_n5_generalization_01 as n5      # KP-GENERALIZATION-N5-PRODUCTION-WIRING-01: Key Phrase一般化N5方式(既定ON・flagなし・X/Y/Z共通の1配線点)

# R-5: 補完の人称整合(Z)の出力先を初回と分ける。person_repair_fnを返す側(er026のrunner等)は触らず、make_person_repair_fnが実行時にこの値を読む
# (補完のGate連鎖の実行中だけ_run_backfillがセットし、終了時に必ず戻す)。既定None=従来のdir。
_person_repair_subdir: contextvars.ContextVar = contextvars.ContextVar("kp_person_repair_subdir", default=None)

MAX_CANON_RERUN = 2   # M-7a: item除外後のcanonicalization再実行の上限(承認済みGateの受理条件=全体PASSは変えない)


def _containment(a_key: str, b_key: str) -> bool:
    ta, tb = a_key.split(), b_key.split()
    return bool(ta and tb) and (rv._is_subseq_tokens(ta, tb) or rv._is_subseq_tokens(tb, ta))


def run_vocab_selection(text: str, units: list, already_items: list, excluded: list, *, process: Optional[str] = None,
                        make_call_fn: Optional[Callable] = None, sleep_fn: Optional[Callable] = None,
                        max_attempts: int = ft.MAX_ATTEMPTS, shown_phrases: Optional[list] = None, note: Optional[str] = None,
                        spec: Optional["p7w5.PromptSpec"] = None) -> dict:
    """2 call目(既定=Prompt 2-V。spec指定時はW5'(単語)/P7(フレーズ補完)=1回call・item単位除外。KP-PHRASE7-WORD5-PRODUCTION-01 Opus M-3)。item単位でvalidate / 重複(前記3件との同一・包含)/ 明示除外 / CMU を適用し、通ったものだけ返す。
    技術/parse失敗は最大max_attempts回。全て失敗ならstatus=FAILED(呼出側が外側retryへ)。0件はOK(適切な候補が不足=shortfall)。
    M-5/M-7(補完): shown_phrases=LLMに見せる『すでに選ばれた表現』(未指定=already_itemsのdisplay_phrase=従来どおり)。包含比較先(duplicate_of_top3)は
    常にalready_items(=call1の選定結果)のまま=Gateの意味を変えない。note=本文後置の既存exclusion note(2-V本文のshaは不変)。"""
    sleep_fn = sleep_fn if sleep_fn is not None else time.sleep
    max_items = p2v.SELECTOR_2V_MAX_ITEMS if spec is None else spec.max_items
    already = [it["display_phrase"] for it in already_items]
    already_keys = [ft.phrase_key(p) for p in already]            # 包含比較先(duplicate_of_top3)。表示用とは分離(M-5)
    shown = list(shown_phrases) if shown_phrases is not None else already
    ex_keys = {ft.phrase_key(e["phrase"]): e for e in (excluded or [])}
    model = None if make_call_fn is not None else ft.resolve_model(process)
    attempts, messages = [], []
    for attempt in range(1, max_attempts + 1):
        if spec is None:
            msg = p2v.build_user_message(text, shown, diagnostic_note=note)
            assert p2v.prompt_prefix_intact(msg), "Prompt 2-Vが改変されている"
        else:
            msg = spec.build_message(text, shown, note)
            assert spec.prefix_intact(msg), f"{spec.prompt_id}が改変されている"
        messages.append(msg)
        if make_call_fn is not None:
            fn = make_call_fn(msg)
        else:
            fn = p2v.make_vocab_selector_fn(msg, model=model) if spec is None else spec.make_call(msg, model)
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
            if not reasons and spec is not None and spec.single_word_only and ft.count_words(phrase) != 1:
                # D3(Fable確定): Key Word絶対条件2『1語』のGate化。validate(救済後の句)→not_single_word→duplicate_of_top3の順。Eには単語(kind=word)として数える
                reasons, stage = [f"Key Wordは1語のみ(実際: {ft.count_words(phrase)}語)"], bf.STAGE_NOT_SINGLE_WORD
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
        if len(kept) > max_items:
            for k in kept[max_items:]:
                dropped.append({"raw_rank": k["raw_rank"], "phrase": k["resolved"]["phrase"], "stage": "overflow",
                                "reasons": [f"最大{max_items}件を超過(下位のため除外)"], "origin": "call2"})
            kept = kept[:max_items]
        attempts.append({"attempt": attempt, "status": "OK", "model": model_id, "response_id": response_id,
                         "n_selected": len(selected), "n_kept": len(kept), "n_dropped": len(dropped)})
        return {"status": "OK", "kept": kept, "dropped": dropped, "model_id": model_id, "response_id": response_id,
                "attempts": attempts, "messages": messages, "raw_text": raw}
    return {"status": "FAILED", "kept": [], "dropped": [], "model_id": None, "response_id": None, "attempts": attempts, "messages": messages}


def _make_pool_screen(ng_entries: list, excluded: list) -> Callable:
    """N5 L1のB1過剰生成候補に課すHuman NG/累積除外の照合(Opus M2)。screen(phrase)-> 理由 or None。選定済みP7候補に課す`_screen_human_ng`・excluded照合と同じ基準。"""
    ex_keys = {ft.phrase_key(e["phrase"]) for e in (excluded or [])}

    def screen(phrase: str):
        if ft.phrase_key(phrase) in ex_keys:
            return "除外指定の語句(Human NG/累積除外)"
        if rv.match_ng({"candidate_id": rv.candidate_id_for(phrase), "selection_phrase": phrase, "used_form": ""}, ng_entries) == "exact":
            return "Humanが不適切(NG)と指定済み"
        return None
    return screen


def _n5_person_factory(process: Optional[str]) -> Callable:
    """N5後の(表示形, 訳)への既存人称整合の修復で使うLLM factory(X/Y用。Zはrunnerが渡すperson_repair_fnを使う)。Zの`_person_repair_factory`と同じrouting
    (process=A2_SUPPORT/B1_SUPPORT -> SUPPORT_MODEL)。modelはcall時に確定する(不整合が無ければ呼ばれない=API 0)。"""
    import er006_model_routing_contract_01 as routing

    def factory(msg: str):
        return ga.make_alignment_fn(msg, model=routing.require_model(process, routing.SUPPORT_MODEL))
    return factory


def _n5_l3_summary(res: dict, applied: list) -> dict:
    """L3(GEN5->VER5->CHK5)の1回分の監査要約(doc.generalization / stages telemetry用)。"""
    lg = res.get("log") or {}
    rel, flags, rec = {}, {}, {}
    for c in (res.get("kept") or {}).values():
        r = (c.get("check") or {}).get("relation") or "NONE"   # NONE=CHK5対象外(revert済み等)。keyをstrに統一(doc保存はsort_keys=Trueでありkey=Noneは保存不可)
        rel[r] = rel.get(r, 0) + 1
        rc = c.get("reconcile") or "NONE"
        rec[rc] = rec.get(rc, 0) + 1
        for f in c.get("flags") or []:
            flags[f] = flags.get(f, 0) + 1
    by_stage = {}
    for d in res.get("dropped") or []:
        by_stage[d["stage"]] = by_stage.get(d["stage"], 0) + 1
    kept = list((res.get("kept") or {}).values())
    return {"targets": len(applied) + len(res.get("dropped") or []), "kept": len(kept), "dropped_by_stage": by_stage,
            "reverted": sum(1 for c in kept if c.get("reverted")), "check_relation": rel, "flags": flags, "reconcile": rec,
            "form_changed_vs_span": sum(1 for c in kept if " ".join((c["display_form"] or "").lower().split()) != " ".join((c["span"] or "").lower().split())),
            "verify_missing": lg.get("verify_missing", 0), "check_missing_retry": lg.get("check_missing_retry"),
            "check_missing_dropped": len(lg.get("check_missing_dropped") or []), "max_words_dropped": len(lg.get("max_words_dropped") or [])}


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
                stages: dict, stage_prefix: str = "", n5_ctx: Optional["n5.N5Ctx"] = None, n5_l3_fn: Optional[Callable] = None,
                n5_state: Optional[dict] = None) -> dict:
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
    # ---- N5 L3(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 Opus M1): canonicalization直後・CMU post-canonの前に GEN5->VER5->CHK5(初回・補完とも同じこの1か所)。
    # 対象=L1を通ったフレーズ(meta.n5_target)。単語(W5')は対象外。N5形=used_form=key_phrase、本文根拠(source_span)は無変更。除外はstage=n5_*(drop_rank)。
    # n5_ctx=None(=N5段を呼ばない)は内部関数の直接呼出し(test)専用。正式経路(generate_candidates/_run_backfill)は必ずn5_ctxを渡す(静的testで固定)。
    n5_applied = []
    if n5_ctx is not None and items:
        tg = []
        for it in items:
            m = meta[idx_of[it["rank"]]]
            if not m.get("n5_target"):
                continue
            tg.append({"key": it["rank"], "span": m["selection_phrase"], "sentence": it.get("source_sentence") or "",
                       "prod_gloss": (it.get("japanese_gloss") if m.get("n5_origin") != "B1" else None), "n5_origin": m.get("n5_origin") or "P7"})
        if tg:
            try:
                res = (n5_l3_fn or n5.run_l3)(text, tg, n5_ctx)
            except n5.N5TechnicalFailure as e:
                return {"status": "CANON_FAILED", "canon_fail": f"N5_TECHNICAL_FAILURE: {str(e)[:300]}"}
            for d in res["dropped"]:
                if any(x["rank"] == d["key"] for x in items):
                    drop_rank(d["key"], d["stage"], d["reasons"])
            by_rank = {x["rank"]: x for x in items}
            for rank, c in res["kept"].items():
                if rank in by_rank:
                    n5.apply_to_item(by_rank[rank], c, display_phrase=by_rank[rank].get("display_phrase"))
                    n5_applied.append(rank)
            summ = _n5_l3_summary(res, n5_applied)
            stages[f"{stage_prefix}n5_l3"] = summ
            if n5_state is not None:
                n5_state.setdefault("l3", []).append({"prefix": stage_prefix or "initial", "summary": summ, "log": {k: v for k, v in (res.get("log") or {}).items() if k != "stages"}})
    # CMU post-canon
    chk = cmu.canonicalized_check(items)
    for b in chk["bad"]:
        drop_rank(b["rank"], "cmu_post_canon", ["基本形化・一般化後「%s」にCMU未登録語 %s" % (b["used_form"], ", ".join(b["unregistered"] or []))])
    # 記号
    findings = sc.detect_key_phrase_symbol_findings(items)
    for rank in sorted({f["rank"] for f in findings if sc.safety.symbol_gate_requires_stop([f])}):
        drop_rank(rank, "symbol", [f"音声化禁止記号: {f.get('token')}" for f in findings if f["rank"] == rank])
    # 人称整合(Z=runnerのperson_repair_fn。X/Yは N5後の(表示形, 訳)の組に同じ既存人称整合[決定論check+必要時のみ既存align_glosses修復]を共通適用=Opus M5。
    # gloss kill switch[EIGO_KP_GLOSS_ALIGNMENT=0]のときはX/Yの追加修復は行わない=従来のZと同じ扱い)
    pr_fn = person_repair_fn
    if pr_fn is None and n5_ctx is not None and n5_applied and ga.flag_enabled():
        pr_fn = make_person_repair_fn(text, _n5_person_factory(process), work, article_id, subdir="n5_person_repair")
    if pr_fn is not None and items:
        before_gloss = {x["rank"]: x.get("japanese_gloss") for x in items}
        mdoc = pr_fn({"items": items})
        by = {x["rank"]: x for x in mdoc["items"]}
        items = [by.get(x["rank"], x) for x in items]
        n_rw = 0
        for x in items:       # Opus M5: 人称整合の修復がN5(VER5/CHK5)確認済みglossを書き換えた件数を記録
            if x.get("n5") and x.get("japanese_gloss") != before_gloss.get(x["rank"]):
                x["n5"]["person_repair"] = {"gloss_before": before_gloss.get(x["rank"]), "gloss_after": x.get("japanese_gloss"),
                                            "gloss_alignment_status": x.get("gloss_alignment_status")}
                x["n5"]["gloss_ja"] = x.get("japanese_gloss")   # 不変条件 japanese_gloss==n5.gloss_ja の維持(旧値はperson_repair.gloss_beforeに残す)
                n_rw += 1
        if n5_ctx is not None:
            stages[f"{stage_prefix}n5_person_repair"] = {"n5_items": len(n5_applied), "n5_gloss_rewritten": n_rw}
            if n5_state is not None:
                n5_state.setdefault("person", []).append({"prefix": stage_prefix or "initial", "n5_gloss_rewritten": n_rw})
    # SRC D1(Z)
    if src_fn is not None and items:
        new_by, drop_by = src_fn(items)
        for rank, reasons in drop_by.items():
            if any(x["rank"] == rank for x in items):
                drop_rank(rank, "src_d1", reasons)
        items = [new_by.get(x["rank"], x) for x in items]
    # 候補ID・NG(基本形化後のused_form照合)
    cands = []
    pf_checked, pf_dropped = 0, {}       # 仕様①telemetry: 品質検査(presentable filter)の検査件数と除外件数(コード別)
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
        # 仕様①(HR-SELECTION-FLOW-QA-FIRST、2026-10-29): 品質検査を人間への提示前に完結させる。canonicalization QA不合格(REVIEW_REQUIRED・判定欠落)・
        # 救済後の未検査・gloss未確定/正式でない候補は旗付きで残さず**除外**する(Human NG除外と同型)。除外はGate除外として数えられ、既存の補完(backfill)が
        # 代替を補う(新しいretry/上限は作らない)。品質基準(11 QAフィールド・閾値)は不変。提示集合の定義は rv.presentation_blockers の1か所。
        pf_checked += 1
        blockers = rv.presentation_blockers(cand)
        if blockers:
            for b in blockers:
                pf_dropped[b[0]] = pf_dropped.get(b[0], 0) + 1
            dropped.append({"raw_rank": m["raw_rank"], "phrase": m["selection_phrase"], "stage": rv.blocker_stage(blockers),
                            "reasons": [b[1] for b in blockers], "origin": m["origin"], "blocker_codes": [b[0] for b in blockers]})
            continue
        cands.append(cand)
    stages[f"{stage_prefix}presentable_filter"] = {"version": rv.PRESENTABLE_FILTER_VERSION, "checked": pf_checked, "dropped": sum(pf_dropped.values()),
                                                  "dropped_by_code": pf_dropped}
    return {"status": "OK", "cands": cands}


def select_p7(text: str, work: str, article_id: str, source_level: str, process: Optional[str] = None, diagnostic_note: Optional[str] = None,
              kp_backend: Optional[str] = None, *, excluded_phrases: Optional[list] = None, make_call_fn: Optional[Callable] = None,
              sleep_fn: Optional[Callable] = None, synthetic: bool = False) -> dict:
    """call1(P7・フレーズ最大7件)の既定select_fn(KP-PHRASE7-WORD5-PRODUCTION-01)。`er105.run_fulltext_selection`をP7パラメータで呼ぶ
    (再選定ループMAX_ATTEMPTS=2・本文一致/1〜5語/CMU/除外句/救済の各Gateは従来のcall1と共通=承認済み仕様の維持。Trial-02のP7[ループなし]とは別方式)。
    戻り値は`sc.run_key_phrase_selection`と同形。sc経由にしない(scは`prompt_sha256=PROMPT_2_SHA256`を固定記録するため)。代わりにP7のshaつきのtelemetryを
    ここで1行記録する(Opus M-9)。kp_backend名は`fulltext_p2`(全文選定backendの識別。R-2)のまま、Promptの識別はprompt_id/shaで行う。"""
    if kp_backend is not None and kp_backend != sc.FULLTEXT_BACKEND_ID:
        raise ValueError(f"select_p7は全文選定backend({sc.FULLTEXT_BACKEND_ID})専用(実際: {kp_backend!r})")
    if make_call_fn is None:
        model = ft.resolve_model(process)
        make_call_fn = lambda msg: p7w5.make_p7_selector_fn(msg, model=model)   # noqa: E731
    result = ft.run_fulltext_selection(text, work, article_id, source_level, process=process, diagnostic_note=diagnostic_note,
                                       make_call_fn=make_call_fn, sleep_fn=sleep_fn, excluded_phrases=excluded_phrases,
                                       prompt_text=p7w5.P7_TEXT, max_items=p7w5.KP_PHRASE_MAX, parse_fn=p2v.parse_selection,
                                       prompt_id=p7w5.P7_ID, prompt_sha256=p7w5.P7_SHA256)
    sc._log_kp_backend_telemetry(
        article_id, source_level, requested_backend=sc.FULLTEXT_BACKEND_ID, backend_used=sc.FULLTEXT_BACKEND_ID,
        final_status=result.get("status"), fallback_triggered=False, model_id=result.get("model_id"),
        cost_jpy=None, synthetic=synthetic, source_reference_contract=ft.FULLTEXT_SOURCE_REF_ID,
        kp_attempts=result.get("kp_attempts"), shortfall=result.get("shortfall"),
        prompt_id=p7w5.P7_ID, prompt_sha256=p7w5.P7_SHA256)
    return result


def _enforce_kind_caps(cands: list, dropped: list) -> list:
    """種類別上限(フレーズ7・単語5)の強制(承認済み上限の維持。新規抽出規則ではない)。used_formのkindで数え、超過分は下位(通し順の後ろ)から
    dropped(stage=overflow_kind)へ。overflow同様Eに数えない(bf.NOT_COUNTED_STAGES)。順序は維持。"""
    cap = {bf.KIND_PHRASE: bf.PHRASE_CAP, bf.KIND_WORD: bf.WORD_CAP}
    n = {bf.KIND_PHRASE: 0, bf.KIND_WORD: 0}
    keep = []
    for c in cands:
        k = c.get("kind") or bf.kind_of_phrase(c.get("used_form") or "")
        if n[k] >= cap[k]:
            dropped.append({"raw_rank": c["raw_rank"], "phrase": c["selection_phrase"], "stage": "overflow_kind",
                            "reasons": [f"{'Key Phrase' if k == bf.KIND_PHRASE else 'Key Word'}の種類別上限{cap[k]}件を超過(下位のため除外)"], "origin": c["origin"]})
            continue
        n[k] += 1
        keep.append(c)
    return keep


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
                        vocab_call_fn: Optional[Callable] = None, sleep_fn: Optional[Callable] = None,
                        phrase_call_fn: Optional[Callable] = None, difficulty_fn: Optional[Callable] = None,
                        n5_pool_fn: Optional[Callable] = None, n5_l3_fn: Optional[Callable] = None) -> dict:
    """returns {"ok": True, "doc": 候補doc(candidates_sha256未付与)} | {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": [...]}。
    作業はすべて <kp_dir>/kp_candidates/round_<n>/work/ 配下。<kp_dir>/keywords_canonicalized.json には触れない(M-1)。"""
    import er030_key_phrase_db_hybrid_core_01 as core
    select_fn = select_fn or select_p7
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
    n5_attempts = []        # N5の監査(attemptごとのL1/L3/人称整合/呼出meta[actual model・model_version・費用])。最終attemptをdoc.generalizationへ
    backfill_on = bf.backfill_enabled()      # 単一読取。生成1回につき1回だけ読み、docへ記録する(途中で変わっても同一生成内は不変)
    while True:
        outer += 1
        if stop_check_fn is not None:
            stop_check_fn(f"kp_candidates:{article_id}:round{round_no}:attempt{outer}")
        entry = {"outer_attempt": outer, "excluded_in": [e["phrase"] for e in excluded], "stages": {}}
        last = outer >= max_outer
        note = ft.build_exclusion_note(excluded, limit=p7w5.KP_PHRASE_MAX) if excluded else None
        sel_kwargs = {"excluded_phrases": [dict(e) for e in excluded]} if excluded else {}
        # ---- call 1: P7(フレーズ最大7件・順位付け・理由つき)
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
        # M-1: call1(P7)の最終attemptでitem単位に除外された句(CMU未登録・除外指定の再選択)もEに数える。er105は無変更でmetadataから読む
        call1_dropped = bf.read_call1_dropped(work, excluded) if backfill_on else []
        # ---- N5 L1(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 Opus M2): P7候補∪B1過剰生成 -> 既存Gate(本文一致/語数/CMU/NG) -> SEL -> pick(cap7)。
        # 選ばれたフレーズ集合が以降のW5'(already_items)・補完(call1引数)・canonicalization・L3の入力になる。N5選別による除外はEに数えない(n5_pool/n5_select/n5_pick)。
        n5_state = {"attempt": outer, "ctx": n5.N5Ctx(process, tag=f"round{round_no}:attempt{outer}:initial", stop_check_fn=stop_check_fn, sleep_fn=sleep_fn,
                                                      article_id=article_id), "seen": set(), "l1": [], "l3": [], "person": []}
        n5_attempts.append(n5_state)
        try:
            l1 = (n5_pool_fn or n5.pool_and_select)(text, call1, n5_state["ctx"], include_b1=True, units=units,
                                                    screen_fn=_make_pool_screen(ng_entries, excluded), seen_keys=n5_state["seen"])
        except n5.N5TechnicalFailure as e:
            entry["failure"] = "n5_select_failed"
            entry["n5_error"] = str(e)[:300]
            log.append(entry)
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        n5_state["seen"] = set(l1.get("seen_keys") or set())
        n5_state["l1"].append(l1["record"])
        call1_p7 = call1
        call1 = [p["item"] for p in l1["picked"]]
        call1_dropped = list(call1_dropped) + list(l1["dropped"])
        entry["n5_l1"] = {"p7_in": len(call1_p7), "picked": len(call1), "picked_origin": (l1["record"] or {}).get("picked_origin")}
        # ---- call 2: W5'(Key Word最大5件+理由。KP含有語は除外・1語のみ=not_single_word Gate)
        v2 = run_vocab_selection(text, units, call1, excluded, process=process, make_call_fn=vocab_call_fn, sleep_fn=sleep_fn,
                                 spec=p7w5.SPEC_W5P)
        entry["call2_status"] = v2["status"]
        if v2["status"] != "OK":
            entry["failure"] = "call2_selection_failed"
            log.append(entry)
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        originals, meta, dropped = [], [], list(call1_dropped) + list(v2["dropped"])
        for n, (it, pk) in enumerate(zip(call1, l1["picked"]), start=1):
            o = dict(it)
            originals.append(o)
            meta.append({"origin": "call1", "raw_rank": n, "reason_ja": pk.get("reason_ja") or it.get("reason_ja", ""), "selection_phrase": it["display_phrase"],
                         "n5_target": True, "n5_origin": pk.get("n5_origin") or "P7"})
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
        n5_state["ctx"].tag = f"round{round_no}:attempt{outer}:initial"
        chain = _gate_chain(text, work, article_id, process, originals, meta, live, dropped, ng_entries=ng_entries, canon_fn=canon_fn,
                            src_fn=src_fn, person_repair_fn=person_repair_fn, stages=entry["stages"], n5_ctx=n5_state["ctx"],
                            n5_l3_fn=n5_l3_fn, n5_state=n5_state)
        if chain["status"] != "OK":
            entry["failure"] = f"canonicalization_{chain['canon_fail']}"
            log.append(entry)
            dropped_all += dropped
            if last:
                return {"ok": False, "status": "OUTER_RETRY_EXHAUSTED", "outer_retry_log": log}
            continue
        cands = chain["cands"]
        # 種類別cap(フレーズ7・単語5)の強制 → ai_rank(Gate通過後の連番。call1[P7]の順→call2[W5']の順)
        cands = _enforce_kind_caps(cands, dropped)
        for n, c in enumerate(cands, start=1):
            c["ai_rank"] = n
        gate_dropped = [d for d in dropped if d["stage"] not in bf.GATE_DROP_EXEMPT_STAGES]      # M-2: NOT_COUNTED_STAGES参照に統一(overflow_kindを含む)
        # ---- Gate除外候補の補完(承認済み仕様。配線位置=ai_rank付番後・Redundancy QAの前 [R-10])。初回の候補は不変・補完分は末尾へ追加・1周1回だけ
        if backfill_on:
            backfill_rec, new_cands, bdropped = _run_backfill(
                text=text, units=units, work=work, article_id=article_id, process=process, round_no=round_no, outer=outer, cands=cands,
                dropped=dropped, call1=call1, excluded=excluded, ng_entries=ng_entries, canon_fn=canon_fn, src_fn=src_fn,
                person_repair_fn=person_repair_fn, stop_check_fn=stop_check_fn, vocab_call_fn=vocab_call_fn, phrase_call_fn=phrase_call_fn,
                sleep_fn=sleep_fn, stages=entry["stages"], n5_state=n5_state, n5_pool_fn=n5_pool_fn, n5_l3_fn=n5_l3_fn)
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
    # KP-DIFFICULTY-4LEVEL-DISPLAY-01(APPROVED_FOR_PRODUCTION 2026-10-30): 最終候補集合へ難易度4段階を**追加fieldとして**付与する(1 generate=1 call)。
    # Gateではない: 候補の除外・並べ替え・件数変更をしない(candidatesのid/順序/他fieldは不変)。判定失敗は`unknown`でfail-open。付与位置が最終段1か所のため
    # 初回/外側retry/補完(backfill)/再選定roundのどの候補にも付く。routing違反・STOPは伝播(他の段と同じ)。
    if stop_check_fn is not None:
        stop_check_fn(f"kp_difficulty:{article_id}:round{round_no}")
    difficulty_rec = (difficulty_fn or dg.apply_to_candidates)(cands, level, process=process)
    doc = {"level": level, "prompt_ids": {"call1": p7w5.P7_ID, "call2": p7w5.W5P_ID},
           "prompt_sha256": {"call1": p7w5.P7_SHA256, "call2": p7w5.W5P_SHA256},
           "model_requested": ft.SELECTION_MODEL_ID, "model_id": {"call1": sel.get("model_id"), "call2": v2.get("model_id")},
           "generated_at": rv._now(), "round": round_no, "candidates": cands, "dropped": dropped, "redundancy_qa": red,
           "shortfall": len(cands) < rv.KP_CANDIDATE_MAX, "outer_attempts": outer, "outer_retry_log": log,
           "rescue_provenance": er125.provenance(),      # R2: 辞書sha・lexicon_status・rescue_enabled・schema(resume時にドリフトをlogのみ)
           "backfill": backfill_rec,                     # F-2: 補完の記録(enabled/triggered/status/E[種類別]/N/added/surplus/dropped/sha/model_id)
           "presentable_filter": _presentable_telemetry(cands, dropped, log[-1] if log else {}),   # 仕様①telemetry(0件でも記録)
           "shortfall_detail": _shortfall_detail(cands, backfill_rec),
           "difficulty_grading": difficulty_rec,      # KP-DIFFICULTY-4LEVEL-DISPLAY-01: 難易度判定の監査record(version/prompt sha/model_id/件数/fail-open)
           "generalization": _generalization_record(n5_attempts)}      # KP-GENERALIZATION-N5-PRODUCTION-WIRING-01: N5方式marker・model/Prompt/設定・L1/L3記録(resume時のmarker検査に使う)
    with open(f"{work}/outer_retry_log.json", "w", encoding="utf-8") as f:
        json.dump({"attempts": log, "excluded_phrases": excluded}, f, ensure_ascii=False, indent=2)
    return {"ok": True, "doc": doc}


def _generalization_record(attempts: list) -> dict:
    """doc.generalization: 方式id・要求model・Prompt/schema sha・FLAGS_V1 hash(audit_record)+ 全attemptのL1/L3/人称整合/LLM呼出meta(actual model_id・Gemini model_version・
    stage別token/費用・JSON途切れ再試行)。最終attempt=採用された候補の元。旧方式(N5前)で作られた候補docにはこのkeyが無い=resume時に検出できる。"""
    rec = n5.audit_record()
    rec["attempts"] = [{"outer_attempt": a.get("attempt"), "l1": a.get("l1"), "l3": a.get("l3"), "person_repair": a.get("person"),
                        "llm_calls": a["ctx"].metas} for a in attempts]
    rec["n_llm_calls"] = sum(len(a["ctx"].metas) for a in attempts)
    rec["cost_jpy_by_stage"] = {}
    for a in attempts:
        for m in a["ctx"].metas:
            k = m.get("stage")
            rec["cost_jpy_by_stage"][k] = round(rec["cost_jpy_by_stage"].get(k, 0.0) + (m.get("cost_jpy") or 0.0), 4)
    return rec


def _presentable_telemetry(cands: list, dropped: list, last_entry: dict) -> dict:
    """候補生成ごとのrun監査(HR-SELECTION-FLOW-QA-FIRST、Opus telemetry): QA検査した件数(初回+補完)・canonicalization_qa除外件数・提示可能件数・filter版。0件でも記録。
    検査件数/除外件数は最終attemptの_gate_chain(初回+補完)が`stages`へ記録した値の合計。"""
    st = (last_entry or {}).get("stages") or {}
    pf = [v for k, v in st.items() if k.endswith("presentable_filter") and isinstance(v, dict)]
    by_stage = {}
    for d in dropped:
        by_stage[d.get("stage")] = by_stage.get(d.get("stage"), 0) + 1
    return {"version": rv.PRESENTABLE_FILTER_VERSION, "checked": sum(x.get("checked", 0) for x in pf),
            "canonicalization_qa_dropped": by_stage.get("canonicalization_qa", 0), "gloss_unresolved_dropped": by_stage.get("gloss_unresolved", 0),
            "dropped_by_code": {c: sum((x.get("dropped_by_code") or {}).get(c, 0) for x in pf) for c in sorted({c for x in pf for c in (x.get("dropped_by_code") or {})})},
            "presentable": len(rv.presentable_candidates(cands)), "n_candidates": len(cands)}


def _shortfall_detail(cands: list, rec: dict) -> dict:
    """F-2: 上限未達の内訳(フォームが『何件足りず、なぜか』を表示できる)。shortfall(bool)は従来どおり別に持つ。"""
    e = rec.get("E") or {}
    added = rec.get("added") or []
    n_add = {bf.KIND_PHRASE: sum(1 for a in added if a.get("kind") == bf.KIND_PHRASE), bf.KIND_WORD: sum(1 for a in added if a.get("kind") == bf.KIND_WORD)}
    n_by = {k: sum(1 for c in cands if c.get("kind") == k) for k in (bf.KIND_PHRASE, bf.KIND_WORD)}
    cap_by = {bf.KIND_PHRASE: bf.PHRASE_CAP, bf.KIND_WORD: bf.WORD_CAP}
    return {"n_candidates": len(cands), "cap": rv.KP_CANDIDATE_MAX, "missing": max(0, rv.KP_CANDIDATE_MAX - len(cands)),
            "cap_by_kind": cap_by, "missing_by_kind": {k: max(0, cap_by[k] - n_by[k]) for k in cap_by},
            "E_total": e.get("total"), "backfilled": len(added),
            "unfilled_by_kind": ({bf.KIND_PHRASE: max(0, (e.get("phrase") or 0) - n_add[bf.KIND_PHRASE]),
                                  bf.KIND_WORD: max(0, (e.get("word") or 0) - n_add[bf.KIND_WORD])} if rec.get("triggered") else None)}


def _by_stage(dropped: list) -> dict:
    out: dict = {}
    for d in dropped:
        out[d.get("stage")] = out.get(d.get("stage"), 0) + 1
    return out


def _keys_of(c: dict) -> list:
    """候補の比較用キー(基本形化後のused_formと選定表層形)。"""
    return [k for k in (ft.phrase_key(c.get("used_form") or ""), ft.phrase_key(c.get("selection_phrase") or "")) if k]


def _contains_any(a: dict, b: dict) -> bool:
    """候補a・bの語がトークン部分列として一方が他方に含まれるか(used_form/選定表層形のどの組合せでも)。Key Phrase含有語の除外判定(受入条件3)に使う。"""
    return any(_containment(x, y) for x in _keys_of(a) for y in _keys_of(b))


def _run_backfill(*, text: str, units: list, work: str, article_id: str, process: Optional[str], round_no: int, outer: int, cands: list,
                  dropped: list, call1: list, excluded: list, ng_entries: list, canon_fn: Callable, src_fn: Optional[Callable],
                  person_repair_fn: Optional[Callable], stop_check_fn: Optional[Callable], vocab_call_fn: Optional[Callable],
                  sleep_fn: Optional[Callable], stages: dict, phrase_call_fn: Optional[Callable] = None, n5_state: Optional[dict] = None,
                  n5_pool_fn: Optional[Callable] = None, n5_l3_fn: Optional[Callable] = None) -> tuple:
    """Gate除外候補の補完(ユーザー正式採用 §3-1〜3-3、DESIGN_02 + KP-PHRASE7-WORD5-PRODUCTION-01 DESIGN_02)。
    returns (backfill記録, 追加候補[ai_rank付き], 補完側のdropped)。初回の cands / dropped は変更しない(初回合格候補の保持)。
    補完は**種類別・直列・各1回**: フレーズ=P7(quota_phrase>0のとき)→単語=W5'(quota_word>0のとき)。各callは`run_vocab_selection`の一般化経路で
    item単位に除外し、内容不適合で再callしない(技術/parse失敗の再試行のみ既存2回まで)。er105のattempt loopもmetadata書込みも使わない(Opus M-3)。
    直列の理由: 共有state(contextvars=救済文脈、er005 cost loggerのglobal _CONTEXT)の引継ぎを避ける・発火が低頻度(Opus M-7)。
    片方の種類だけ失敗しても成功した種類は採用し、prompts[kind].statusに失敗を記録する。両方失敗/live 0/canonicalization全体失敗は status=FAILED で
    初回候補で続行する(M-6)。FulltextSelectionError(routing違反等)とSTOP(M-4)は握らず伝播させる(R-8)。"""
    counts = bf.count_exclusions(dropped, cands)
    if counts["total"] == 0:
        return bf.not_triggered_record(counts, "E=0"), [], []                 # LLM 0
    n_phrase = sum(1 for c in cands if c.get("kind") == bf.KIND_PHRASE)
    n_word = sum(1 for c in cands if c.get("kind") == bf.KIND_WORD)
    plan = bf.plan_quota(counts, n_phrase, n_word)
    if not cands or plan["total"] <= 0:
        return bf.not_triggered_record(counts, "no_candidate" if not cands else "no_room"), [], []
    if stop_check_fn is not None:                                              # M-4: 新しい課金点でもSTOP通知を迂回しない(try外=伝播)
        stop_check_fn(f"kp_backfill:{article_id}:round{round_no}:attempt{outer}")
    kinds = ((bf.KIND_PHRASE, p7w5.SPEC_P7, phrase_call_fn), (bf.KIND_WORD, p7w5.SPEC_W5P, vocab_call_fn))
    rec = {"enabled": True, "triggered": True, "status": bf.ST_FAILED, "failure": None, "E": bf.e_public(counts),
           "N": {k: plan[k] for k in ("room", "total", "phrase_wanted", "word_wanted", "capped", "quota_phrase", "quota_word")},
           "prompt_id": "per_kind", "prompt_sha256": "per_kind",              # 旧スカラー読取の互換(値は種類別。実体はprompts)
           "prompts": {kd: {"id": sp.prompt_id, "sha256": sp.sha256, "quota": plan[f"quota_{kd}"], "status": "SKIPPED", "failure": None,
                            "model_id": None, "response_id": None} for kd, sp, _ in kinds},
           "model_id": None, "response_id": None, "attempts": [], "added": [], "surplus": [], "dropped_by_stage": {}}
    bdropped: list = []
    try:
        shown = bf.shown_phrases(cands)
        originals, meta = [], []
        n_ok = 0
        for kd, sp, call_fn in kinds:
            if plan[f"quota_{kd}"] <= 0:
                continue                                                       # その種類は空きなし/E=0 → call 0
            pr = rec["prompts"][kd]
            try:
                rejected = bf.rejected_entries(excluded, dropped, for_kind=kd)
                vb = run_vocab_selection(text, units, call1, rejected + bf.existing_entries(cands), process=process, make_call_fn=call_fn,
                                         sleep_fn=sleep_fn, shown_phrases=shown, spec=sp,
                                         note=(ft.build_exclusion_note(rejected, limit=sp.max_items) or None))
            except Exception as e:   # noqa: BLE001  R-8: 技術失敗だけ握る(種類単位)。routing違反(FulltextSelectionError)・STOPは伝播
                if bf.is_propagating_exception(e):
                    raise
                pr.update(status=bf.ST_FAILED, failure=f"technical:{type(e).__name__}: {e}")
                continue
            rec["attempts"] += [dict(a, kind=kd) for a in vb["attempts"]]
            pr.update(model_id=vb["model_id"], response_id=vb["response_id"])
            if vb["model_id"]:
                rec["model_id"], rec["response_id"] = vb["model_id"], vb["response_id"]
            if vb["status"] != "OK":
                pr.update(status=bf.ST_FAILED, failure="selection_failed")
                continue
            extra = ft.build_original_items([k["resolved"] for k in vb["kept"]])
            picks = None
            if kd == bf.KIND_PHRASE and n5_state is not None:
                # N5 L1(補完): P7補完が返したフレーズにSEL+pickのみ(B1過剰生成は初回のみ)。初回にjudge済み/採用済みの句は再判定しない(seen)。単語(W5')は対象外。
                n5_state["ctx"].tag = f"round{round_no}:attempt{outer}:backfill"
                try:
                    l1b = (n5_pool_fn or n5.pool_and_select)(text, extra, n5_state["ctx"], include_b1=False, units=units,
                                                             screen_fn=_make_pool_screen(ng_entries, excluded), seen_keys=n5_state["seen"], origin_label="P7")
                except n5.N5TechnicalFailure as e:
                    pr.update(status=bf.ST_FAILED, failure=f"technical:n5_select: {str(e)[:200]}")
                    continue
                n5_state["seen"] = set(l1b.get("seen_keys") or set())
                n5_state["l1"].append(l1b["record"])
                picks = l1b["picked"]
                bdropped += [dict(d, origin="backfill") for d in l1b["dropped"]]
            pr.update(status=bf.ST_OK, n_kept=len(vb["kept"]), n_dropped=len(vb["dropped"]))
            n_ok += 1
            bdropped += [dict(d, origin="backfill") for d in vb["dropped"]]
            if picks is None:
                for k, it in zip(vb["kept"], extra):
                    originals.append(dict(it))
                    meta.append({"origin": "backfill", "raw_rank": k["raw_rank"], "reason_ja": k["reason_ja"], "selection_phrase": it["display_phrase"]})
            else:
                for n, pk in enumerate(picks, start=1):
                    originals.append(dict(pk["item"]))
                    meta.append({"origin": "backfill", "raw_rank": n, "reason_ja": pk.get("reason_ja") or "", "selection_phrase": pk["item"]["display_phrase"],
                                 "n5_target": True, "n5_origin": pk.get("n5_origin") or "P7"})
        if n_ok == 0:                           # 呼んだ種類が全て失敗
            rec["failure"] = "call_selection_failed"
            return rec, [], []
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
            if n5_state is not None:
                n5_state["ctx"].tag = f"round{round_no}:attempt{outer}:backfill"
            chain = _gate_chain(text, bwork, article_id, process, originals, meta, live, bdropped, ng_entries=ng_entries, canon_fn=canon_fn,
                                src_fn=src_fn, person_repair_fn=person_repair_fn, stages=stages, stage_prefix="backfill_",
                                n5_ctx=(n5_state["ctx"] if n5_state is not None else None), n5_l3_fn=n5_l3_fn, n5_state=n5_state)
        finally:
            _person_repair_subdir.reset(token)
        if chain["status"] != "OK":
            rec.update(failure=f"canonicalization_{chain['canon_fail']}", dropped_by_stage=_by_stage(bdropped))
            return rec, [], bdropped
        # R-3: 基本形化後のused_formが既存候補(または先に採った補完候補)と完全一致=重複として捨てる(Nに数えない・再callしない)。candidate_id衝突も同様
        # M-4(Opus): Key Phraseに含まれるKey Wordは候補にしない(受入条件3)。既存候補は保持し、**新規の補完候補の方を落とす**:
        #   補完フレーズが既存/先着のKey Wordを含む → 補完フレーズを落とす / 補完単語が既存・先着のKey Phraseに含まれる → 補完単語を落とす。いずれもNに数えない
        have_ids = {c["candidate_id"] for c in cands}
        have_forms = {ft.phrase_key(c.get("used_form") or "") for c in cands}
        acc_phrases = [c for c in cands if c.get("kind") == bf.KIND_PHRASE]
        acc_words = [c for c in cands if c.get("kind") == bf.KIND_WORD]
        uniq = []
        for c in chain["cands"]:
            uk = ft.phrase_key(c.get("used_form") or "")
            why = None
            if c["candidate_id"] in have_ids or uk in have_forms:
                why = "基本形化後の表現が既存候補と同一"
            elif c.get("kind") == bf.KIND_PHRASE and any(_contains_any(w, c) for w in acc_words):
                why = "既存のKey Wordを含む補完フレーズ(Key Phraseに含まれる単語はKey Word候補から除外する仕様のため、補完フレーズを除外)"
            elif c.get("kind") == bf.KIND_WORD and any(_contains_any(c, p) for p in acc_phrases):
                why = "Key Phraseに含まれる単語(Key Word候補から除外)"
            if why:
                bdropped.append({"raw_rank": c["raw_rank"], "phrase": c["selection_phrase"], "stage": "backfill_duplicate",
                                 "reasons": [why], "origin": "backfill"})
                continue
            have_ids.add(c["candidate_id"])
            have_forms.add(uk)
            (acc_phrases if c.get("kind") == bf.KIND_PHRASE else acc_words).append(c)
            uniq.append(c)
        taken, surplus = bf.pick_backfill(uniq, counts, plan)                  # 種類別quota(plan.quota_phrase/quota_word)の先頭N件(M-1)。余りは候補にしない
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
        # mock/hook経路(旧kp_fn adapter、呼出側がCANONICALIZATION_PASSを確認済み)専用: per-itemの qa_overall_status を持たない旧hookのitemはPASS受理済みとして扱う
        # (正式生成経路は_gate_chainが実際のQA判定を持つitemだけを候補にする=この補完は通らない。仕様①の提示前QAはREVIEW_REQUIREDを除外する)
        it2.setdefault("qa_overall_status", "PASS")
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
