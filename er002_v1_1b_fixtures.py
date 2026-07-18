# ============================================================
# er002_v1_1b_fixtures.py
# ER-002-v1.1B-I1: 回帰テストfixtureローダ
# ============================================================
# er002_v1_1b_fixtures/ 配下のJSONは、ER-002-v1.1A-S1のA01実API実行
# (実行開始コミット86b99bb)から抽出した実データ(fact registry・
# Editorial Brief・台本試行1/2・旧編集品質QA応答・PM1のclaim_grounding_
# table)。APIキー・使用量ログ・元記事全文・秘密情報は含まない。
#
# このモジュールは実APIを一切呼び出さない(ファイル読み込みのみ)。

from __future__ import annotations

import json
import os

_FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er002_v1_1b_fixtures")


def _load(filename: str):
    with open(os.path.join(_FIXTURE_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def load_fact_registry() -> dict:
    """{"F01": fact_text, ..., "F05": fact_text} を返す。"""
    return _load("fact_registry.json")


def load_editorial_brief() -> dict:
    return _load("editorial_brief.json")


def load_script_attempt(n: int) -> dict:
    if n not in (1, 2):
        raise ValueError("台本試行はattempt 1または2のみ保存されている")
    return _load(f"script_attempt_{n}.json")


def load_old_quality_response(n: int) -> dict:
    """v1.1A(修正前)の編集品質QA生応答。誤検知の実例として回帰テストで使う。"""
    if n not in (1, 2):
        raise ValueError("編集品質QA応答はattempt 1または2のみ保存されている")
    return _load(f"old_quality_response_attempt_{n}.json")


def load_pm1_claim_grounding_table() -> dict:
    return _load("pm1_claim_grounding_table.json")
