# -*- coding: utf-8 -*-
"""KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02: Gate除外候補の補完(ユーザー正式採用 APPROVED_FOR_PRODUCTION §3-1〜3-3)の純粋部品。

LLM呼出・ファイル書込を持たない(例外: call1メタデータの読取/削除)。呼出側=er119_kp_candidates_01(X/Y/Z共通の1配線点)。
- 単一flag読取関数 backfill_enabled()(環境変数 EIGO_KP_BACKFILL、既定ON=承認済み仕様。"0"のときだけ補完無効かつ外側retry条件も現行へ完全復帰)。
- 除外件数Eの計数(R-1 種類別 / R-4 phrase_key重複除去 / M-1 call1最終attemptの除外)。
- 補完候補の採用規則(種類別の先頭N件、R-2/R-3)。
A/B/C(strategy_l経路)はこのmoduleをimportしない(er119_isolation_test_01と同じ方針)。
"""
from __future__ import annotations

import json
import os
from typing import Optional

import er119_kp_human_review_01 as rv   # er105を直接importしない(er105の隔離test: Productionからの参照はer119_kp_candidates系のみ)

KILL_SWITCH_ENV = "EIGO_KP_BACKFILL"
BACKFILL_MAX_CALL_ITEMS = 5          # Prompt 2-Vの最大件数(SELECTOR_2V_MAX_ITEMS)。N>5は5で打ち切る(capped)
NOT_COUNTED_STAGES = ("overflow",)   # Prompt上限超過の切捨て=Gate除外ではない(現行も外側retry判定から除外、DESIGN_01 §2)
ST_NOT_TRIGGERED, ST_OK, ST_FAILED, ST_DISABLED = "NOT_TRIGGERED", "OK", "FAILED", "DISABLED"
KIND_PHRASE, KIND_WORD = "phrase", "word"


def backfill_enabled() -> bool:
    """単一の読取関数(既定ON=ユーザー正式採用)。起動script/.env/mode/関数引数からONへ迂回しない。生成1回につき1回だけ呼び、結果をdocへ記録する。"""
    return os.environ.get(KILL_SWITCH_ENV, "1").strip() != "0"


def kind_of_phrase(phrase: str) -> str:
    """R-1: 構成英単語が1語なら単語、それ以外はフレーズ(スペース区切り。Prompt 2の語数規則と同じ)。"""
    return KIND_WORD if len([t for t in (phrase or "").strip().split() if t]) == 1 else KIND_PHRASE      # er105.count_wordsと同じスペース区切り


def is_propagating_exception(e: BaseException) -> bool:
    """R-8: 補完側の『技術失敗』として握ってよい例外か。FulltextSelectionError(routing違反等)とSTOP系は握らず従来どおり伝播させる。"""
    if isinstance(e, (KeyboardInterrupt, SystemExit)) or any(c.__name__ == "FulltextSelectionError" for c in type(e).__mro__):
        return True
    n = type(e).__name__
    return "Stop" in n or "Sentinel" in n


# ---- M-1: call1(Prompt 2)の最終attemptでitem単位に除外された句 -------------------------------------------------------------
def metadata_path(work_dir: str) -> str:
    return f"{work_dir}/keywords_runtime_metadata.json"


def clear_call1_metadata(work_dir: str) -> None:
    """call1の呼出前に前周のmetadataを消す(外側retryで前周の除外を誤読しないため)。作業dir内の成果物で、select呼出が必ず書き直す。"""
    try:
        os.remove(metadata_path(work_dir))
    except FileNotFoundError:
        pass


def read_call1_dropped(work_dir: str, excluded: Optional[list] = None) -> list:
    """er105/er108が最終attemptで除外したitem(cmu_excluded / exclusion_dropped)を、call2のdroppedと同じ形で返す。metadataが無ければ[](注入select_fn等)。"""
    path = metadata_path(work_dir)
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, ValueError):
        return []
    ad = meta.get("attempts_detail") or []
    if not ad:
        return []
    last = ad[-1]
    ex = {rv.phrase_key(e["phrase"]): e for e in (excluded or [])}
    out = []
    for c in last.get("cmu_excluded") or []:
        out.append({"raw_rank": int(c.get("index", 0)) + 1, "phrase": c["phrase"], "stage": "cmu",
                    "reasons": ["CMU未登録語: " + ", ".join(c.get("unregistered") or [])], "origin": "call1"})
    for h in last.get("exclusion_dropped") or []:
        e = ex.get(rv.phrase_key(h["phrase"])) or {}
        pr = h.get("prior_reasons") or e.get("reasons") or ["不適合"]
        out.append({"raw_rank": int(h.get("index", 0)) + 1, "phrase": h["phrase"], "stage": e.get("source") or "excluded",
                    "reasons": ["除外指定の語句(" + " / ".join(pr) + ")"], "origin": "call1"})
    return out


# ---- 除外件数Eの計数 ---------------------------------------------------------------------------------------------------------
def _rescue_originals(c: dict) -> list:
    rs = c.get("rescue") or {}
    return [p for p in ((rs.get("selection") or {}).get("original_phrase"), (rs.get("canonicalization") or {}).get("display_phrase")) if p]


def _cand_keys(cands: list) -> set:
    keys = set()
    for c in cands:
        keys.add(rv.phrase_key(c.get("selection_phrase") or ""))
        for p in _rescue_originals(c):
            keys.add(rv.phrase_key(p))
    keys.discard("")
    return keys


def count_exclusions(dropped: list, cands: list) -> dict:
    """E = AIが選定したitemのうち、候補組立後の最終処分がdroppedの『数えるstage』であるものの数(DESIGN_01 §2)。
    救済成立(dropped前に成立=candsに残る)・HR限定候補・Redundancy旗は構造的に含まれない。二重防御: duplicate_of_top3以外で、現存候補の選定句/救済前元句と
    phrase_keyが一致するdropped(同じ句が既に候補として残っている)は数えない。R-4: phrase_keyで重複を除いてから数える。overflowは数えない。
    human_ng / excluded(Humanが不適切とした句・累積除外句をAIが再び選んだもの)は数え、別カウンタにも出す(Opus P2)。"""
    live_keys = _cand_keys(cands)
    seen, items = set(), []
    by_stage: dict = {}
    for d in dropped:
        st = d.get("stage")
        if st in NOT_COUNTED_STAGES:
            continue
        k = rv.phrase_key(d.get("phrase") or "")
        if not k or k in seen:
            continue
        if st != "duplicate_of_top3" and k in live_keys:
            continue
        seen.add(k)
        items.append({"phrase": d.get("phrase"), "kind": kind_of_phrase(d.get("phrase")), "stage": st, "origin": d.get("origin")})
        by_stage[st] = by_stage.get(st, 0) + 1
    n_word = sum(1 for i in items if i["kind"] == KIND_WORD)
    return {"total": len(items), "phrase": len(items) - n_word, "word": n_word, "by_stage": by_stage,
            "human_ng": by_stage.get("human_ng", 0), "excluded": by_stage.get("excluded", 0), "items": items}


def plan_quota(counts: dict, n_cands: int, cap: int) -> dict:
    """補完件数Nの上限。N = min(E, cap-現存, 2-Vの最大5)。単語のE_wordは単語、フレーズのE_phraseはフレーズで補う(R-1)。現存候補が上限以上(room<=0)なら0。"""
    room = max(0, cap - n_cands)
    want = counts["phrase"] + counts["word"]
    total = min(want, room, BACKFILL_MAX_CALL_ITEMS)
    return {"room": room, "total": total, "phrase_wanted": counts["phrase"], "word_wanted": counts["word"], "capped": want > total}


def pick_backfill(cands_new: list, counts: dict, plan: dict) -> tuple:
    """補完候補(Gate全段通過・LLM応答順)から、種類別の先頭E_phrase件・E_word件を採り、合計はplan.total以内。返り値=(採用, 余り)。
    不足は不足のまま(種類をまたいだ数合わせはしない。§3-1「適切な候補が不足する場合は上限未達を許容」)。余りは候補にしない(surplus)。"""
    quota = {KIND_PHRASE: counts["phrase"], KIND_WORD: counts["word"]}
    taken, surplus = [], []
    for c in cands_new:
        k = c.get("kind") or kind_of_phrase(c.get("used_form"))
        if quota.get(k, 0) > 0 and len(taken) < plan["total"]:
            quota[k] -= 1
            taken.append(c)
        else:
            surplus.append(c)
    return taken, surplus


# ---- 補完call用の入力(M-5: LLMに見せる『選ばない一覧』と、duplicate_of_top3の包含比較先を分離する) ----------------------------------
def shown_phrases(cands: list) -> list:
    """LLMに見せる『すでに選ばれた表現』= 現存候補の選定句と、救済前の元句(重複して選び直されないため)。順序は候補順、重複なし。"""
    out, seen = [], set()
    for c in cands:
        for p in [c.get("selection_phrase")] + _rescue_originals(c):
            if p and rv.phrase_key(p) not in seen:
                seen.add(rv.phrase_key(p))
                out.append(p)
    return out


def rejected_entries(excluded: list, dropped: list) -> list:
    """note(理由付き『選ばない』)と機械除外に使う不適合確定句。Human NG・累積除外(excluded)+この周のdropped(overflowは不適合でないので除く)。phrase_key重複なし。"""
    out, seen = [], set()
    for e in excluded or []:
        k = rv.phrase_key(e["phrase"])
        if k not in seen:
            seen.add(k)
            out.append({"phrase": e["phrase"], "reasons": list(e.get("reasons") or ["不適合"]), "source": e.get("source") or "excluded"})
    for d in dropped:
        if d.get("stage") in NOT_COUNTED_STAGES:
            continue
        k = rv.phrase_key(d.get("phrase") or "")
        if k and k not in seen:
            seen.add(k)
            out.append({"phrase": d["phrase"], "reasons": list(d.get("reasons") or ["不適合"]), "source": "excluded"})   # 補完側dropped上の表示=excluded(元stageはreasonsに残る)
    return out


def existing_entries(cands: list) -> list:
    """機械除外専用(noteには出さない)。現存候補の選定句・救済前元句と一致する補完候補は捨てる(R-3。Nに数えない)。"""
    return [{"phrase": p, "reasons": ["現存候補と同一"], "source": "existing_candidate"} for p in shown_phrases(cands)]


def disabled_record() -> dict:
    return {"enabled": False, "triggered": False, "status": ST_DISABLED}


def e_public(counts: dict) -> dict:
    return {"total": counts["total"], "phrase": counts["phrase"], "word": counts["word"], "human_ng": counts["human_ng"],
            "excluded": counts["excluded"], "by_stage": dict(counts["by_stage"]), "items": list(counts["items"])}


def not_triggered_record(counts: dict, reason: str) -> dict:
    return {"enabled": True, "triggered": False, "status": ST_NOT_TRIGGERED, "reason": reason, "E": e_public(counts)}
