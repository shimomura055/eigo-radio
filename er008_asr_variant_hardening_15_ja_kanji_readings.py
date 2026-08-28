# ============================================================
# er008_asr_variant_hardening_15_ja_kanji_readings.py
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part G/H:
# 日本語の「表記(漢字span)が持つ正当な読み候補一覧」を取得するための
# 最小実装。
# ============================================================
# No.8 A2 preview(canonical「ころ」/ASR「頃」)監査で判明した通り、既存
# の_reading_equal_allowing_voicing()(濁点の有無だけを除去して比較)は
# 「ころ」と「ごろ」を常に同一視してしまい、実際に読みが異なるケースを
# 区別できない設計だった。正しい判定は「ASR側の表記が辞書的に持ちうる
# 読み候補の中に、canonical側の期待読みが含まれるか」であるべき。
#
# 個別漢字ごとのハードコード表(1対1whitelist)は主方式にしない方針
# (CURRENT_SPEC既存の禁止事項、CMU Pronouncing Dictionary採用との一貫
# 性)のため、常用漢字を汎用的にカバーする静的参照データを使う。実装時に
# 確認した結果、**新規にKANJIDIC2等を追加する必要はなく、既存依存の
# pykakasiが同梱する漢和辞書データ(kanwadict4.db)がそのまま使える**
# ことを確認した(新規dependencyゼロ)。
#
# 既知の限界(正直に記録): 「頃」のように、単漢字として「ころ」「ごろ」
# 両方が辞書上の正当な読みとして登録されている文字がある(公开辞書データ
# 自体が、頻出する連濁形[「〜頃には」のごろ等]を独立した読みとして収録
# しているため)。このような文字については、本モジュールの候補一覧
# チェックだけでは「実際にどちらの読みで発話されたか」を音声無しに完全
# には区別できない(テキストだけからは原理的に確定できない)。この限界は
# ER-008-15完了報告のOpen Itemとして記録する。本モジュールは「無関係な
# 漢字・読みを誤って許容しない」ことを主目的とし、上記の限界がある文字
# については、Cascade側の追加条件(Primary/Secondary相互に異なるASR
# エンジンでの裏付けを要求する等、evaluate_attempt_ja_with_cascade_
# detail側の設計)で慎重に扱う。
from __future__ import annotations

import os
import pickle
import threading

_lock = threading.Lock()
_kanwa_data: dict | None = None
_load_failed = False


def _load_kanwadict() -> dict | None:
    global _kanwa_data, _load_failed
    if _kanwa_data is not None or _load_failed:
        return _kanwa_data
    with _lock:
        if _kanwa_data is not None or _load_failed:
            return _kanwa_data
        try:
            import pykakasi
            path = os.path.join(os.path.dirname(pykakasi.__file__), "data", "kanwadict4.db")
            with open(path, "rb") as f:
                _kanwa_data = pickle.load(f)
        except Exception:
            # データが読み込めない場合は安全側(判定不能=None)にする。
            # 呼び出し側はNoneを「候補が確認できない」として扱い、
            # 自動PASSしない設計になっている(D-2'の(B)経路と同じ思想)。
            _load_failed = True
            _kanwa_data = None
    return _kanwa_data


def reading_candidates_for_span(span: str) -> list[str] | None:
    """span(1文字以上の漢字を含む短い表記)が辞書上持ちうる読み候補の
    一覧を返す。spanがそのまま辞書のキー(単漢字、または既知の複合語)と
    して登録されている場合のみ候補を返す。登録が無い場合はNone(=候補
    不明。呼び出し側はこれを「安全に確認できない」として扱うこと)。"""
    if not span:
        return None
    data = _load_kanwadict()
    if data is None:
        return None
    try:
        bucket = data.get(ord(span[0]))
    except TypeError:
        return None
    if not bucket:
        return None
    entries = bucket.get(span)
    if not entries:
        return None
    readings = [reading for reading, _ in entries if reading]
    return readings or None


def reading_is_candidate(span: str, expected_reading: str) -> bool | None:
    """expected_readingが、spanの正当な読み候補一覧に含まれるかを判定
    する。候補一覧が取得できない場合はNone(判定不能、PASSの根拠には
    しないこと)。"""
    candidates = reading_candidates_for_span(span)
    if candidates is None:
        return None
    return expected_reading in candidates
