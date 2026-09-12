#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er011_tts_cooldown_observation_01.py

管理ID: TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01

## 背景・ユーザー決定(2026-09-12、原文要約)
`TTS-RETRY-TIMING-SELECTION-EFFECT-REANALYSIS-01_REPORT.md`により、既存データ
(3回連続NG→4回目)は全件(8/8, 15/15)が人的介入(`approve_regenerate()`明示
呼び出し等)を伴い、「時間を空ける」効果単独を判定できないと判明した
(REJECTED、根拠不足)。ユーザーはこれを受け、以下の条件でTrial限定の観測を
新規に実施するよう指示した:
  - 1〜3回目は通常どおり連続実行(Production cascadeそのまま、無変更)
  - 3回連続NGになったケースのみ対象
  - 3回目NG後、約20分待つ(TTS_COOLDOWN_SECONDS、既定1200秒)
  - 4回目を1回だけ実行
  - 待機中に原稿・Prompt・TTS設定・model・voice等を変更しない
  - 人的介入を入れない
  - Production retry仕様は変更しない
  - Trial限定の観測とする(数時間待つ方式は不採用)

## 本モジュールの役割
Production cascade(既存の3回連続NG→STOPPED判定ロジック、`er011_human_
review_lock_01.py`のReview Lock状態遷移含む)は一切変更しない。本モジュールは
その「直後」に外付けで差し込む、Trial限定の観測フックのみを提供する。

- 入力: 3回連続NGとなったsegmentの情報(canonical text、language、3回分の
  attempt記録[NG理由・failure type等]、4回目に渡す全パラメータ[voice/model/
  TTS設定/prompt等]、および4回目を実際に実行するための`single_attempt_fn`
  [呼び出し側が用意する、1回だけ生成する関数への参照])。
- 動作: `TTS_COOLDOWN_OBSERVATION=1`(既定OFF)のときのみ、
  1. 4回目に渡すパラメータ辞書のhashを取り、必要なら呼び出し側から渡された
     `capture_live_params_fn()`(現在有効なmodel/voice/prompt等のライブ設定を
     読み取るcallback)のhashも取る(待機前スナップショット)。
  2. 約20分(既定、`TTS_COOLDOWN_SECONDS`で調整可)待機する(実測秒数を記録)。
  3. 待機後、同じhashを再度取り、待機前後で完全一致するか機械的に照合する。
     不一致であれば「観測を無効化」し、4回目attempt自体を実行しない
     (コスト浪費防止。既にパラメータが変わっている以上、4回目を実行しても
     この観測の目的[時間経過単独の効果測定]には使えないため)。
  4. 一致していれば、`single_attempt_fn`を1回だけ呼び出す(=4回目)。
     ASR検証は`single_attempt_fn`の内部実装(呼び出し側が指定する既存の
     単発生成関数、既存のASR検証ロジックをそのまま含む)にすべて委譲する
     (本モジュール自身は新しいASR検証ロジックを実装しない)。
  5. 結果を`er011_output/tts_cooldown_observation_01/observations.jsonl`へ
     追記する(1行1観測、上書きしない)。
- `TTS_COOLDOWN_OBSERVATION`が"1"でない場合は常にno-op(待機・4回目生成の
  いずれも行わない、SKIPPED_DISABLEDレコードのみ追記して即return)。

## Production安全性(3点)
1. **Production cascade/Gate/Review Lockコードを一切import・変更しない**。
   `er011_human_review_lock_01.py`の`check_before_generation()`/
   `record_outcome()`/`approve_regenerate()`はこのモジュールから一度も
   呼ばない。よってProduction側の`review_lock_state.json`は本モジュールの
   実行によって一切変化しない(3回連続NG後の状態=STOPPEDのまま)。
2. **人的介入を入れない**。`approve_regenerate()`等、ユーザーの明示操作を
   模したAPIを一切呼ばない(`no_human_intervention: True`を記録レコードに
   機械的に刻む)。
3. **4回目がPASSしても自動採用しない**。`auto_adopted_to_production: False`
   を常に記録する。採用したい場合の手順は本ファイル末尾のdocstring
   `ADOPTION_PROCEDURE_NOTE`、および対応REPORT参照(既存Human Review機構
   [`approve_regenerate()`をユーザー承認のうえ明示的に呼ぶ]経由でのみ、
   ユーザーが個別に判断する)。
   呼び出し側は、4回目の出力先(`out_path`)をProduction成果物のwavパスとは
   別のTrial専用パスにすること(呼び出し側の責務。本モジュールは
   `single_attempt_fn`へパラメータをそのまま渡すだけで、書き込み先の妥当性
   検証は行わない)。

## 複数segment同時STOPPED時の待機設計(直列20分×Nを避ける)
`run_batch_observations()`は`concurrent.futures.ThreadPoolExecutor`で
segment毎に独立したworker threadを立て、各threadが個別に
`observe_after_three_consecutive_ng()`を実行する。待機(`time.sleep`)はI/O
待ちでGILを解放するため、スレッド並列化で複数segmentの20分待機を重ね合わせ
られる(合計待機時間は「20分+生成時間」のオーダーに収まり、segment数Nに
比例して増加しない)。

## 既知の限界
- `narration/attempts/*.json`(既存ログスキーマ)には、`style_prefix_
  override`/`safety_margin_seconds`/`asr_prompt`本文等、4回目の再現に必要な
  全パラメータが記録されていない(既存
  `TTS-RETRY-TIMING-OBSERVATION-MONITOR-01_REPORT.md`でも既知の欠落として
  記録済み)。そのため本モジュールはログからパラメータを自動復元せず、
  **呼び出し側(3回目attemptを実際に発生させたTrial harnessそのもの)が、
  3回目attemptで使ったのと同一のkwargs一式を明示的に`params`/
  `single_attempt_kwargs`として渡す**設計にしている(呼び出し側は3回目
  attemptを生成した直後の同一関数呼び出しコンテキスト内で本モジュールを
  呼ぶ想定であり、値の取り違えが起きにくい)。
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional

MANAGEMENT_ID = "TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01"

OUT_DIR = "er011_output/tts_cooldown_observation_01"
OBSERVATIONS_PATH = f"{OUT_DIR}/observations.jsonl"

# ユーザー決定(2026-09-12): まず20分程度空けることで効果があるか確認する
# (数時間待つ方式は開発速度を落とすため不採用)。
DEFAULT_COOLDOWN_SECONDS = 1200.0

ADOPTION_PROCEDURE_NOTE = (
    "4回目がPASSした場合でも、本モジュールはProduction側(review_lock_state."
    "json)を一切変更しません(STOPPEDのまま)。Production側で採用する場合は、"
    "(1) ユーザーが4回目の結果[観測記録のwav/ASR文字起こし]を確認し、"
    "(2) 採用してよいと判断した場合のみ、既存Human Review機構である"
    "review_lock.approve_regenerate(out_path, text, approved_by=...)を"
    "ユーザー自身の指示に基づき明示的に呼び出し、(3) その後Production側の"
    "cascade関数(3回連続NGを検出した既存の生成関数)を通常どおり再実行して"
    "REGENERATE_APPROVED状態を消費させてください。本モジュールが生成した"
    "4回目の音声ファイルをProduction成果物パスへ直接コピーする、といった"
    "Review Lockを迂回する手順は取らないでください。"
)


def _env_flag_enabled() -> bool:
    return os.environ.get("TTS_COOLDOWN_OBSERVATION") == "1"


def _cooldown_seconds_from_env() -> float:
    raw = os.environ.get("TTS_COOLDOWN_SECONDS")
    if raw is None:
        return DEFAULT_COOLDOWN_SECONDS
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_COOLDOWN_SECONDS


def _text_hash(text: Optional[str]) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _params_hash(params: dict) -> str:
    """パラメータ辞書を正規化(key sort、非ASCII保持)してhash化する。

    呼び出し側は、4回目生成に影響しうる値(voice/model/route/tts設定/
    instruction・prompt本文/safety_margin_seconds等)を漏れなくこの辞書へ
    含めること。本モジュールは中身の意味を一切解釈せず、機械的な同一性
    検証(待機前後で完全一致するか)のみを行う。"""
    normalized = json.dumps(params or {}, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _append_observation(record: dict) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OBSERVATIONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return record


def _summarize_three_ng(three_attempt_records: list) -> list:
    summary = []
    for idx, r in enumerate(three_attempt_records, start=1):
        asr_text = r.get("asr_text")
        summary.append({
            "sequence": idx,
            "ng_category": r.get("ng_category") or r.get("audio_classification"),
            "ng_subtype": r.get("ng_subtype"),
            "audio_classification": r.get("audio_classification"),
            "verified": r.get("verified"),
            "asr_text_sha256": _text_hash(asr_text) if isinstance(asr_text, str) else None,
            "route": r.get("route"),
            "model": r.get("model"),
            "voice": r.get("voice"),
        })
    return summary


def observe_after_three_consecutive_ng(
    *,
    level_dir: str,
    segment_id: str,
    canonical_text: str,
    language: str,
    three_attempt_records: list,
    params: dict,
    single_attempt_fn: Callable[..., dict],
    single_attempt_args: tuple = (),
    single_attempt_kwargs: Optional[dict] = None,
    capture_live_params_fn: Optional[Callable[[], dict]] = None,
    cooldown_seconds: Optional[float] = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    time_fn: Callable[[], float] = time.time,
    run_id: Optional[str] = None,
) -> dict:
    """3回連続NG直後のsegment1件について、Trial限定のcooldown観測を1回行う。

    引数:
      level_dir: Production narration wavの親ディレクトリ(記録用、書き込みは
        行わない)。
      segment_id: segment識別子(記録用)。
      canonical_text: このsegmentの正本テキスト(canonical text)。hashのみ
        記録し、本文自体はobservations.jsonlへ保存しない(証跡は既存
        attempts/*.jsonやtts_generation_results.json側を参照する設計)。
      language: "en"/"ja"等(記録用)。
      three_attempt_records: 3回連続NGとなった直近3回分のattempt記録
        (`narration/attempts/*.json`と同一スキーマを想定、`verified`は
        3件ともFalseであること)。
      params: 4回目に渡す全パラメータ(voice/model/route/tts設定/prompt本文
        等)。同一性検証のhash元。中身は呼び出し側の責務で漏れなく渡すこと。
      single_attempt_fn: 4回目を実際に1回だけ実行する呼び出し可能オブジェクト。
        戻り値は既存の生成関数と同じ形式の辞書(`status`/`asr_verified`/
        `reason`/`audio_classification`等)を想定する。本モジュールは
        ASR検証ロジックを一切実装せず、この関数の戻り値をそのまま解釈する
        だけ(既存のASR検証と完全に同一のロジックを再利用する設計)。
        **Production Review Lockデコレータ(`review_lock.guarded_generate*`)
        でラップされていない生の関数を渡すこと**(例:
        `er003_v1_repro01_main_generate.generate_narration_snippet_verified_
        strict.__wrapped__`)。デコレータ付きのまま渡すと、Production側の
        状態が既にHUMAN_REVIEW_REQUIREDであるため`check_before_generation()`
        がブロックし、観測不能になる(意図的な安全側動作。詳細は
        `er011_human_review_lock_01.py`参照)。
      single_attempt_args / single_attempt_kwargs: single_attempt_fn呼び出し時の
        位置引数・キーワード引数(3回目attemptで使ったのと同一の値を明示的に
        渡すこと。out_pathはProduction成果物とは別のTrial専用パスにすること)。
      capture_live_params_fn: 呼び出し時点の「ライブ設定」(model定数・voice
        定数・prompt fileの中身等)を辞書として返すcallback(任意)。待機前後
        で呼び出し、hashが変化していないかも追加検証する。省略した場合は
        `params`辞書自体の同一性(このプロセス内では不変なので常にTrue)のみ
        で判定する。
      cooldown_seconds: 待機秒数を明示指定する場合(省略時は環境変数
        `TTS_COOLDOWN_SECONDS`、さらに省略時はDEFAULT_COOLDOWN_SECONDS=1200)。
      sleep_fn / time_fn: テスト用の差し替えポイント(既定はtime.sleep/
        time.time)。

    戻り値: observations.jsonlへ追記したレコードと同一内容の辞書。
    """
    run_id = run_id or str(uuid.uuid4())
    single_attempt_kwargs = dict(single_attempt_kwargs or {})
    three_ng_summary = _summarize_three_ng(three_attempt_records)

    base = {
        "run_id": run_id,
        "management_id": MANAGEMENT_ID,
        "level_dir": level_dir,
        "segment_id": segment_id,
        "language": language,
        "canonical_text_sha256": _text_hash(canonical_text),
        "three_ng_summary": three_ng_summary,
        "no_human_intervention": True,
        "production_state_modified": False,
        "auto_adopted_to_production": False,
    }

    if len(three_attempt_records) != 3 or any(r.get("verified") is not False for r in three_attempt_records):
        return _append_observation({
            **base,
            "status": "INELIGIBLE_NOT_EXACTLY_THREE_CONSECUTIVE_NG",
            "note": "3回連続NG(verified=False x3)以外のケースのため対象外です。",
            "fourth_attempt_executed": False,
        })

    if not _env_flag_enabled():
        return _append_observation({
            **base,
            "status": "SKIPPED_DISABLED",
            "note": "TTS_COOLDOWN_OBSERVATION!=1のため、待機・4回目生成のいずれも行いませんでした"
                    "(既定OFF、no-op、追加API呼び出し0件)。",
            "fourth_attempt_executed": False,
        })

    wait_target_seconds = cooldown_seconds if cooldown_seconds is not None else _cooldown_seconds_from_env()

    pre_wait_params_hash = _params_hash(params)
    pre_wait_live_hash = _params_hash(capture_live_params_fn()) if capture_live_params_fn else None

    wait_started_at = time_fn()
    sleep_fn(wait_target_seconds)
    wait_ended_at = time_fn()
    actual_wait_seconds = wait_ended_at - wait_started_at

    post_wait_params_hash = _params_hash(params)
    post_wait_live_hash = _params_hash(capture_live_params_fn()) if capture_live_params_fn else None

    params_unchanged = (pre_wait_params_hash == post_wait_params_hash) and (
        (capture_live_params_fn is None) or (pre_wait_live_hash == post_wait_live_hash)
    )

    wait_and_hash_fields = {
        "requested_cooldown_seconds": wait_target_seconds,
        "actual_wait_seconds": round(actual_wait_seconds, 3),
        "params_hash_before_wait": pre_wait_params_hash,
        "params_hash_after_wait": post_wait_params_hash,
        "live_params_hash_before_wait": pre_wait_live_hash,
        "live_params_hash_after_wait": post_wait_live_hash,
        "params_unchanged_verified": params_unchanged,
    }

    if not params_unchanged:
        return _append_observation({
            **base,
            **wait_and_hash_fields,
            "status": "OBSERVATION_INVALIDATED_PARAM_CHANGE",
            "note": "待機前後でパラメータhashが一致しませんでした。この観測は時間経過単独の効果測定に"
                    "使えないため無効とし、コスト浪費防止のため4回目attempt自体を実行しませんでした。",
            "fourth_attempt_executed": False,
        })

    t0 = time_fn()
    fourth_result = single_attempt_fn(*single_attempt_args, **single_attempt_kwargs) or {}
    duration_seconds = time_fn() - t0

    fourth_pass = fourth_result.get("status") == "OK"
    fourth_status = "PASS" if fourth_pass else "NG"

    return _append_observation({
        **base,
        **wait_and_hash_fields,
        "status": "OBSERVED",
        "fourth_attempt_executed": True,
        "fourth_attempt_result_status": fourth_status,
        "fourth_attempt_raw_status_field": fourth_result.get("status"),
        "fourth_attempt_asr_verified": fourth_result.get("asr_verified"),
        "fourth_attempt_reason": fourth_result.get("reason"),
        "fourth_attempt_audio_classification": fourth_result.get("audio_classification"),
        "fourth_attempt_duration_seconds": round(duration_seconds, 3),
        "cost_note": "4回目attempt=通常のTTS 1回+ASR検証1回相当(single_attempt_fnの内部実装に依存、"
                     "本モジュール自身は追加のAPI呼び出しを行わない)。",
        "adoption_note": ADOPTION_PROCEDURE_NOTE,
    })


def run_batch_observations(segment_jobs: list, max_workers: Optional[int] = None) -> list:
    """複数segmentが同時にSTOPPEDになった場合の観測をバッチ実行する。

    各segmentの待機(約20分)は独立しており、直列実行(20分xN)にはしない。
    ThreadPoolExecutorでsegment毎に独立したworker threadを立て、待機
    (time.sleep、GILを解放するI/O待ち相当)を重ね合わせることで、合計
    wall-clock時間を「約20分+各segmentの生成時間」のオーダーに抑える
    (Nに比例して増加させない)。

    segment_jobs: `observe_after_three_consecutive_ng()`へのkwargs辞書のlist。
    戻り値: 各jobの結果レコードのlist(投入順を保持)。
    """
    if not segment_jobs:
        return []
    workers = max_workers or len(segment_jobs)
    results: list = [None] * len(segment_jobs)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_idx = {
            executor.submit(observe_after_three_consecutive_ng, **job): idx
            for idx, job in enumerate(segment_jobs)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            results[idx] = future.result()
    return results
