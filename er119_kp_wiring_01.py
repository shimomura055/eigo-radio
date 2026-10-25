# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02: X/Z runnerから呼ぶ薄い接続層。

共有関数 sc.run_key_phrases は呼ばない/変更しない(A/B/C・Y Trialは従来の3件経路のまま)。
本moduleは「候補生成→Human確認 or 明示の不在宣言→finalize」(er119_kp_human_review_01.ensure_kp_review)を呼び、
結果を sc.run_key_phrases 互換の戻り値dict(selection/canonicalization/redundancy_qa/status/...)へ整形して返す。
返り値の kp_review.state: FINALIZED / PENDING(Human確認待ち。rc=4) / FAILED(OUTER_RETRY_EXHAUSTED。従来と同じKP stage失敗)。
"""
from __future__ import annotations

import os
from typing import Callable, Optional

import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv

STATUS_PENDING = "KP_REVIEW_PENDING"


def review_resume_valid(kp_dir: str, text: str) -> bool:
    """M-4: review/候補ファイルが有効(本文shaが一致)か。Trueなら通常のscaffold/allでsupport(有料)を再生成しない。"""
    c = rv.load_candidates(kp_dir)
    r = rv.load_review(kp_dir)
    return c is not None and r is not None and c.get("text_sha256") == rv.sha256_text(text)


def declare_from_runner_args(out_dir: str, *, by: str, reason: str, user_ref: str = "") -> list:
    """runner引数 `--kp-review auto` の記録化。明示引数が与えられたときだけ呼ぶ(宣言ファイルへ書く=単一読取点が読む)。"""
    return rv.add_declaration(run_dirs=[out_dir], by=by, reason=reason, user_ref=user_ref, source="runner_arg", rounds=[1])


def _shape_final(kp_dir: str, article_id: str, level: str, step: dict) -> dict:
    fin = step["final"]
    review = fin["review"]
    doc = rv._read_json(rv.paths(kp_dir)["kp"])
    events = []
    ev = ga.emit_human_review_notice(kp_dir, article_id, level, doc)   # 最終artifactに対する従来どおりのgloss HR報告(確定物にHRが残る場合のみ)
    if ev is not None:
        events.append(ev)
    cands = rv.load_candidates(kp_dir) or {}
    res = {
        "selection": {"status": "KEY_WORDS_STRUCTURE_PASS", "kp_backend_used": "fulltext_p2", "kp_review_status": review["status"],
                      "kp_attempts": cands.get("outer_attempts")},
        "canonicalization": {"status": "CANONICALIZATION_PASS", "merged": doc, "gloss_alignment_status": None, "gloss_alignment_metrics": None},
        "redundancy_qa": review.get("final_qa"), "redundancy_retry_log": [], "redundancy_retry_attempts": 0,
        "outer_retry_log": cands.get("outer_retry_log") or [],
        "gloss_alignment_human_review_events": events,
        "gloss_alignment_run_status": ga.STOPPED_STATUS if events else None,
        "kp_review": {"state": "FINALIZED", "status": review["status"], "signature": fin["signature"], "round": review.get("round", 1),
                      "candidates_sha256": review["candidates_sha256"], "wrote": fin["wrote"]},
    }
    if events:
        res["status"] = ga.STOPPED_STATUS
    return res


def run_kp_with_review(*, text: str, kp_dir: str, run_dir: str, family: str, slug: str, level: str, article_id: str,
                       stop_run_dir: Optional[str] = None, generate_hook: Optional[Callable] = None,
                       redundancy_hook: Optional[Callable] = None, src_fn: Optional[Callable] = None,
                       person_repair_fn: Optional[Callable] = None, run_hint: Optional[str] = None,
                       stop_check_fn: Optional[Callable] = None, guard_fn: Optional[Callable] = None) -> dict:
    """X/Z共通。generate_hook/redundancy_hookはtest/mock用の注入(省略時は実の候補生成/Redundancy QA)。
    guard_fn(note): 有料呼出の直前に呼ぶ予算guard(Zの_guard)。"""
    ga.preflight()   # OF-229: gloss規則の抽出失敗は記事内容に依存しない設定不備なので最初のAPI呼出前に停止(run_key_phrasesと同じ)
    source_level, process = ("A2", "A2_SUPPORT") if level == "a2" else ("B1", "B1_SUPPORT")
    stop_check_fn = stop_check_fn or sc.make_stop_check(stop_run_dir or run_dir)
    base_gen = generate_hook or kcand.make_generate_fn(
        text, kp_dir, article_id, source_level, level, process, stop_check_fn=stop_check_fn, src_fn=src_fn, person_repair_fn=person_repair_fn)

    def gen(round_no, ng_entries):
        if guard_fn is not None:
            guard_fn(f"kp_{level}_candidates_round{round_no}")
        return base_gen(round_no, ng_entries)

    red = redundancy_hook or kcand.make_redundancy_fn(text, kp_dir, article_id, process)

    def red_g(items, name):
        if guard_fn is not None:
            guard_fn(f"kp_{level}_final_redundancy_{name}")
        return red(items, name)

    step = rv.ensure_kp_review(kp_dir, run_dir=run_dir, family=family, slug=slug, level=level, text=text,
                               generate_fn=gen, redundancy_fn=red_g, run_hint=run_hint or run_dir)
    if step["state"] == "PENDING":
        return {"selection": {"status": STATUS_PENDING}, "canonicalization": None, "redundancy_qa": None, "status": STATUS_PENDING,
                "gloss_alignment_human_review_events": [], "gloss_alignment_run_status": None,
                "kp_review": {"state": "PENDING", "pending": step["pending"]}}
    if step["state"] == "FAILED":
        st = step.get("status") or "OUTER_RETRY_EXHAUSTED"
        return {"selection": {"status": st}, "canonicalization": None, "redundancy_qa": None, "status": st,
                "gloss_alignment_human_review_events": [], "gloss_alignment_run_status": None,
                "outer_retry_log": (step.get("detail") or {}).get("outer_retry_log"),
                "kp_review": {"state": "FAILED", "status": st}}
    return _shape_final(kp_dir, article_id, level, step)


def pending_banner(pending: list, *, restart_command: str) -> str:
    """rc=4時のstdout(正確な再開コマンドを1つだけ出す=M-4)。"""
    lines = [f"{rv.PENDING_MARKER} KP Human Review待ちです(失敗ではありません。有料の後続工程には進みません)。"]
    for p in pending:
        lines.append(f"  - level={p.get('level')}: 依頼書 {p.get('request_md')}")
    lines.append("  次の一手: 依頼書の表を見て `py er119_kp_human_review_cli_01.py select ...` で選ぶ(または明示の `declare-absent`)。")
    lines.append(f"  再開コマンド(同じコマンドを1つだけ再実行): {restart_command}")
    lines.append("  注意: 直近5分以内に同じrunを3回起動するとRESTART_STORM保護で自動停止します(select/reselect後は数分あけて再開)。")
    return "\n".join(lines)
