# ============================================================
# er011_human_review_lock_01.py
# ER-011-HUMAN-REVIEW-COST-GUARD-01
# ============================================================
# 背景(2026-08-27深夜、監査で発見): No.5(pool_n5_cafes)のB1修正作業中、
# Human Review Queueへ到達した(または繰り返しSTOPPEDになった)segment
# (full_story_part1/2)に対し、同じ生成スクリプト(`er009_pool_n5_b1_
# fix_01.py`)を手動で繰り返し実行してしまい、full_story_part1で
# TTS 18回・ASR 59回、full_story_part2でTTS 12回という異常なAPI消費が
# 発生した。原因は2つ: (1) 呼び出し側スクリプトが`results["segments"]
# [name] = r`で毎回結果を無条件に上書きし、過去の試行履歴・Human Review
# 到達状態を一切引き継がない設計だったこと、(2) Human Review Queue
# (英語側er006_output/audio_retry_cascade_prod_01/human_review_queue.
# jsonl、日本語側er007_output/ja_asr_cascade_01/human_review_queue.
# jsonl)へ到達した後も、それを検知して新規TTS/ASR呼び出しをブロックする
# 仕組みが存在しなかった。
#
# 本モジュールは、segment単位のReview Lock状態を導入し、Human Review
# (またはSTOPPED)へ到達したsegmentに対する再生成を、明示的な承認
# (REGENERATE_APPROVED)が無い限りAPIレベルで機械的にブロックする。
#
# 状態遷移(Part C):
#   AUTO_PROCESSING(既定、lock未設定)
#     -> 通常のTTS/ASR retryを許可する
#   HUMAN_REVIEW_REQUIRED(cascadeがHuman Reviewへ回した場合、または
#                          STOPPEDで試行を使い果たした場合)
#     -> それ以降の呼び出しはTTS/ASR呼び出しを一切行わず、既存の
#        lock情報をそのまま返す(0 API call)
#   HUMAN_APPROVED(既存のrecord_human_approval()[er003_v1_n3_01_
#                  assemble.py]と同じ判定を、canonical_text一致の
#                  場合のみ流用する)
#     -> HUMAN_REVIEW_REQUIREDと同様にブロックする(既に承認済みの
#        音声を保持したまま、新規TTS/ASRは行わない)
#   REGENERATE_APPROVED(ユーザーの明示的操作でのみ設定される)
#     -> 次の1回の呼び出しに限り通常のAUTO_PROCESSINGを許可する
#        (呼び出し完了後、結果に応じてRESOLVED/HUMAN_REVIEW_REQUIRED
#        のいずれかへ自動的に遷移し、REGENERATE_APPROVEDのまま残らない
#        =「もう一度スクリプトを実行しただけ」では再度解除されない)
#   RESOLVED(status=="OK"で確定した場合)
#     -> それ以降の呼び出しは同じcanonical_textである限りブロックする
#        (既に成功しているsegmentへの無意味な再生成を防ぐ)
#
# 台本(text)が変わった場合は、SHA256ハッシュの不一致により自動的に
# 「新しいsegmentのバージョン」として扱われ、過去のlockは無効になる
# (既存のrecord_human_approval()のtext変更時無効化と同じ設計思想)。
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from functools import wraps

# ============================================================
# Part F: 累積budget guard
# ============================================================
# 根拠: 既存のTTS retry上限はmax_attempts=6(News/Charon等)または8
# (Point headings)が実測値。ASR Cascade(Primary#1-2+Secondary#1-2)は
# 1 TTS attemptあたり最大4回のASR呼び出しを追加しうる。1回の正常な
# generate呼び出し(1 script実行)であれば、TTS<=8・ASR<=32程度に収まる
# 想定。本guardは「複数回のscript再実行」を跨いだ累積を検知する第二
# 防衛線と位置づける(第一防衛線はHUMAN_REVIEW_REQUIRED到達時点での
# 即時ブロック)。既存max_attempts(6〜8)の目安2周分弱を累積上限とし、
# 実際の事故(TTS18回/ASR59回)より確実に低い値で発火するようにする。
MAX_CUMULATIVE_TTS_ATTEMPTS = 15
MAX_CUMULATIVE_ASR_CALLS = 60

# ============================================================
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part B: TTS retry上限
# ============================================================
# ユーザー正式決定(2026-08-28): 同一segmentのTTS生成総試行回数上限を
# 3回とする(初回を含め最大3回、「初回+3 retry」ではない)。No.8
# wait/weightのように、Validator側の問題やASR表記揺れが原因の場合、
# 6回生成しても同じ結果を繰り返すだけで無駄という監査結果を受けた変更。
# 全Production generate関数(er003_v1_repro01_main_generate.py等)の
# max_attempts既定値はこの定数を参照する(SSOT、CURRENT_SPEC.md参照)。
PRODUCTION_MAX_TTS_ATTEMPTS = 3

# ============================================================
# ER-011-TTS-STANDARD2-MINIMAL1-PRODUCTION-WIRING-25 Part B: 内訳の固定
# ============================================================
# ユーザー正式決定(2026-09-04): 「標準経路+fallback経路合計でmax_attempts
# 回」という設計(Part B、上記)は、標準経路のループが早期returnせずに
# 最後まで回ると`len(attempts_log) == max_attempts`になるため、
# fallback側の残り予算(`max_attempts - len(attempts_log)`)が構造的に
# 常に0になり、minimal instruction fallbackが実質的に発火しない不具合を
# 生んでいた(日本語側で2件の実Production incidentを確認、OPEN-103の
# 英語Key Phrase側と同根)。内訳を明示的に固定し、標準経路には
# PRODUCTION_STANDARD_TTS_ATTEMPTS回しか予算を与えないことで、必ず
# PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS回分がfallbackへ残るようにする。
# この2定数は「標準経路のみ・fallback経路を持たない」既存の呼び出し
# (generate_narration_snippet_verified_strictの直接呼び出し等)には
# 影響しない — 対象は標準+fallbackの2段構成を持つ関数
# (generate_charon_japanese/generate_a2_japanese_with_fallback/
# generate_english_segment_with_fallback)のみ。
# Key Phrase英語Component専用の4回構成(KEY_PHRASE_MINIMAL_MAX_ATTEMPTS+
# KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS、er003_v1_repro01_main_generate.py)
# はこの定数を参照しない、既存の独立した正式仕様のまま(勝手に変更しない)。
PRODUCTION_STANDARD_TTS_ATTEMPTS = 2
PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS = 1
assert PRODUCTION_STANDARD_TTS_ATTEMPTS + PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS == PRODUCTION_MAX_TTS_ATTEMPTS

VALID_STATES =("AUTO_PROCESSING", "HUMAN_REVIEW_REQUIRED", "HUMAN_APPROVED",
                "REGENERATE_APPROVED", "RESOLVED")

# Part E: 追記型(append-only)attempt history。既存のtts_generation_
# results.json(segment単位で上書きされる正)は変更せず、別ファイルへ
# 追記するだけ(既存フォーマットを壊さない)。
ATTEMPT_HISTORY_PATH = "er011_output/attempt_history.jsonl"


def _text_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _has_valid_narration_layout(out_path: str) -> bool:
    """out_pathが".../<theme>/<level>/narration/<segment>.wav"という
    既存の命名慣習に従っているかを確認する。従っていない場合(単体テスト
    のダミーパス"dummy_out.wav"、他プロジェクトの一時ファイル等)は、
    theme/level/segmentが一意に定まらず、異なる呼び出し同士が同じ
    (空文字列ベースの)store pathへ衝突しうる。安全側として、この場合は
    Review Lock機構全体を無効化する(常にproceedし、store読み書きも
    一切行わない)。実際にこのチェックが無かった場合、複数のunittest
    (例: er007_ja_tts_retry_path_fix_test_01.py、いずれも"dummy_out.wav"
    かつ同一canonical_text"テスト文"を使う2つのtest method)が同じ
    store pathを共有してしまい、片方のtest実行で書き込まれたHUMAN_
    REVIEW_REQUIREDが、もう片方のtestを誤ってブロックする実バグを
    regression実行で発見した(ER-011実装時)。"""
    norm = out_path.replace("\\", "/")
    parts = [p for p in norm.split("/") if p]
    if len(parts) < 4:
        return False
    return parts[-2] == "narration"


def derive_segment_key(out_path: str) -> tuple[str, str, str]:
    """narration wavパス(例: ".../pool_n5_cafes/b1b/narration/
    full_story_part1.wav")から(theme_id, level, segment_id)を機械的に
    導出する。既存の全テーマが共通で使う".../<theme>/<level>/narration/
    <segment>.wav"という命名慣習に依存する(呼び出し側の関数シグネチャを
    一切変更しなくて済むよう、out_pathから逆算する設計)。"""
    norm = out_path.replace("\\", "/")
    segment_id = os.path.splitext(os.path.basename(norm))[0]
    narration_dir = os.path.dirname(norm)
    level_dir = os.path.dirname(narration_dir)
    level = os.path.basename(level_dir)
    theme_dir = os.path.dirname(level_dir)
    theme_id = os.path.basename(theme_dir)
    return theme_id, level, segment_id


def _lock_store_path(level_out_dir: str) -> str:
    return f"{level_out_dir}/audit/review_lock_state.json"


def _level_out_dir_from_out_path(out_path: str) -> str:
    norm = out_path.replace("\\", "/")
    return os.path.dirname(os.path.dirname(norm))  # narration/の親


def _load_store(level_out_dir: str) -> dict:
    path = _lock_store_path(level_out_dir)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_store(level_out_dir: str, store: dict) -> None:
    path = _lock_store_path(level_out_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def _human_approved(level_out_dir: str, segment_id: str, text: str) -> bool:
    """既存のrecord_human_approval()(er003_v1_n3_01_assemble.py)による
    承認記録を、重複実装せずそのまま流用する。"""
    path = f"{level_out_dir}/audit/human_approved_segments.json"
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        approvals = json.load(f)
    approval = approvals.get(segment_id)
    if approval is None:
        return False
    return approval.get("canonical_text_sha256") == _text_hash(text)


def _append_attempt_history(record: dict) -> None:
    os.makedirs(os.path.dirname(ATTEMPT_HISTORY_PATH), exist_ok=True)
    with open(ATTEMPT_HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def check_before_generation(out_path: str, text: str, language: str) -> dict:
    """TTS/ASR呼び出しの前に必ず呼ぶゲート判定。

    戻り値:
      {"proceed": True, ...}
        -> 通常通りAUTO_PROCESSINGしてよい(このrun中はREGENERATE_
           APPROVEDを消費するrunであるかどうかも"consuming_regenerate_
           approval"で示す)
      {"proceed": False, "status": ..., "reason": ..., "locked_entry": {...}}
        -> 呼び出し側はTTS/ASR呼び出しを一切行わず、この情報を使って
           既存状態をそのまま返すこと(0 API call、Part H fixture 2)
    """
    if not _has_valid_narration_layout(out_path):
        return {"proceed": True, "bypassed": True,
                "note": "out_path does not match the standard .../<theme>/<level>/narration/<segment>.wav "
                        "layout; Review Lock is skipped for this call to avoid an unsafe shared key."}
    theme_id, level, segment_id = derive_segment_key(out_path)
    level_out_dir = _level_out_dir_from_out_path(out_path)
    store = _load_store(level_out_dir)
    entry = store.get(segment_id)

    if _human_approved(level_out_dir, segment_id, text):
        return {"proceed": False, "status": "HUMAN_APPROVED",
                "reason": "既存のrecord_human_approval()により人間承認済みです。再生成には該当しません。",
                "locked_entry": entry or {"state": "HUMAN_APPROVED"},
                "theme_id": theme_id, "level": level, "segment_id": segment_id}

    if entry is None:
        return {"proceed": True, "theme_id": theme_id, "level": level, "segment_id": segment_id}

    text_matches = entry.get("canonical_text_sha256") == _text_hash(text)
    if not text_matches:
        # 台本が変わった -> 新しいsegmentのバージョンとして扱う(過去のlockは無効)。
        return {"proceed": True, "note": "canonical_text changed since last lock; treated as new version",
                "theme_id": theme_id, "level": level, "segment_id": segment_id}

    state = entry.get("state")
    if state == "REGENERATE_APPROVED":
        return {"proceed": True, "consuming_regenerate_approval": True,
                "theme_id": theme_id, "level": level, "segment_id": segment_id}
    if state == "HUMAN_REVIEW_REQUIRED":
        return {"proceed": False, "status": state, "reason": entry.get("reason"),
                "locked_entry": entry, "theme_id": theme_id, "level": level, "segment_id": segment_id}
    # RESOLVED(status=OKで確定済み)は監査用の記録に留め、ブロックはしない。
    # 理由: A2 6% slowdown retry(generate_a2_segment_with_slowdown、
    # ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11)は、内側のgenerate_english_
    # segment_with_fallback()がstatus=OKを返した直後に、post-process後の
    # ASR再検証が別途不一致となり、同じ内側関数を最大3回まで正当に取り
    # 直す既存の設計を持つ。ここでRESOLVEDをブロック対象にすると、この
    # 既存の正当なretryまで機械的に止めてしまう(実害のある誤検知)。
    # 本Guardが実際に防ぐべきなのは「Human Review/繰り返し失敗への機械的
    # 再挑戦」であり、「一度成功したsegmentへの正当な再挑戦」ではない。
    # AUTO_PROCESSING等、その他の状態も安全側でproceedを許可する。
    return {"proceed": True, "theme_id": theme_id, "level": level, "segment_id": segment_id}


def record_outcome(out_path: str, text: str, language: str, result: dict, run_id: str = None,
                    duration_seconds: float = None) -> dict:
    """generate関数の実行完了後に必ず呼ぶ。戻り値のstatusに応じて次の
    lock状態を決定し、attempt historyへ追記する(Part E)。budget guard
    (Part F)もここで評価する。"""
    if not _has_valid_narration_layout(out_path):
        return {"state": "AUTO_PROCESSING", "bypassed": True}
    theme_id, level, segment_id = derive_segment_key(out_path)
    level_out_dir = _level_out_dir_from_out_path(out_path)
    store = _load_store(level_out_dir)
    prior = store.get(segment_id) or {}
    text_hash = _text_hash(text)
    text_matches_prior = prior.get("canonical_text_sha256") == text_hash

    status = result.get("status")
    attempts_log = result.get("attempts_log") or result.get("standard_attempts_log") or []
    tts_attempts_this_call = len(attempts_log) if isinstance(attempts_log, list) else 0
    asr_calls_this_call = sum(
        1 for a in attempts_log if isinstance(a, dict) and a.get("asr_text") is not None
    ) if isinstance(attempts_log, list) else 0
    # fallback_attempts_log等も存在すれば加算する(cascade内部呼び出しの近似カウント)。
    for extra_key in ("fallback_attempts_log",):
        extra = result.get(extra_key)
        if isinstance(extra, list):
            tts_attempts_this_call += len(extra)
            asr_calls_this_call += sum(1 for a in extra if isinstance(a, dict) and a.get("asr_text") is not None)

    cumulative_tts = (prior.get("cumulative_tts_attempts", 0) if text_matches_prior else 0) + tts_attempts_this_call
    cumulative_asr = (prior.get("cumulative_asr_calls", 0) if text_matches_prior else 0) + asr_calls_this_call

    budget_guard_triggered = (cumulative_tts > MAX_CUMULATIVE_TTS_ATTEMPTS
                              or cumulative_asr > MAX_CUMULATIVE_ASR_CALLS)

    if status == "OK" and not budget_guard_triggered:
        new_state = "RESOLVED"
        reason = "status=OKで確定しました。"
    else:
        new_state = "HUMAN_REVIEW_REQUIRED"
        if budget_guard_triggered:
            reason = (f"BUDGET_GUARD_TRIGGERED: 累積TTS試行={cumulative_tts}"
                      f"(上限{MAX_CUMULATIVE_TTS_ATTEMPTS})、累積ASR呼び出し={cumulative_asr}"
                      f"(上限{MAX_CUMULATIVE_ASR_CALLS})。segment単位の累積コストが異常なため、"
                      "明示的なREGENERATE_APPROVEDが無い限りこれ以上の自動再生成をブロックします。")
        else:
            reason = f"最終status={status}。{result.get('reason') or ''}".strip()

    # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part L: Human Review
    # Lock発動後、attempts_log(実際のASR文字起こし等を含む試行履歴)が
    # 空配列で上書きされ続けてしまう問題をNo.8監査で発見した(呼び出し
    # 側スクリプトが結果を無条件に上書きするたび、_blocked_result()の
    # 空attempts_logがtts_generation_results.json側の正しい履歴を
    # 覆ってしまう)。record_outcome()はこの呼び出しで実際に得られた
    # attempts_log/fallback_attempts_logをlock storeへ保存しておき、
    # 以降ブロックされた呼び出しでも_blocked_result()がこれを復元して
    # 返せるようにする(既存フィールドへの追加のみ、フォーマット破壊
    # なし。過去に既に空配列で上書きされてしまった分の復元は対象外)。
    last_attempts_log = attempts_log if isinstance(attempts_log, list) and attempts_log else None
    if last_attempts_log is None:
        extra = result.get("fallback_attempts_log")
        if isinstance(extra, list) and extra:
            last_attempts_log = extra
    if last_attempts_log is None and text_matches_prior:
        # このcallで新規試行が無かった場合(例: budget guard即発動等)、
        # 直前までの履歴を保持する(空で上書きしない)。
        last_attempts_log = prior.get("last_attempts_log")

    new_entry = {
        "state": new_state,
        "canonical_text_sha256": text_hash,
        "language": language,
        "theme_id": theme_id, "level": level, "segment_id": segment_id,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "reason": reason,
        "final_status": status,
        "wav_path": out_path,
        "cumulative_tts_attempts": cumulative_tts,
        "cumulative_asr_calls": cumulative_asr,
        "budget_guard_triggered": budget_guard_triggered,
        "last_attempts_log": last_attempts_log or [],
    }
    store[segment_id] = new_entry
    _save_store(level_out_dir, store)

    _append_attempt_history({
        "run_id": run_id or str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "theme_id": theme_id, "level": level, "segment_id": segment_id, "language": language,
        "canonical_text_sha256": text_hash,
        "action": "PROCEED",
        "tts_attempts_this_call": tts_attempts_this_call,
        "asr_calls_this_call": asr_calls_this_call,
        "cumulative_tts_attempts": cumulative_tts,
        "cumulative_asr_calls": cumulative_asr,
        "result_status": status,
        "human_review_reached": new_state == "HUMAN_REVIEW_REQUIRED",
        "final_lock_state": new_state,
        "budget_guard_triggered": budget_guard_triggered,
        "duration_seconds": duration_seconds,
    })
    return new_entry


def approve_regenerate(out_path: str, text: str, approved_by: str = "user") -> dict:
    """ユーザーの明示的な指示でのみ呼ぶこと(Part D)。「同じスクリプトを
    もう一度実行しただけ」では絶対に到達しない経路であることを、
    呼び出し元(このAPIを叩くのは対話的なオペレーター操作のみ)で保証する。
    REGENERATE_APPROVEDへ遷移し、次の1回の呼び出しに限り再生成を許可する。"""
    if not _has_valid_narration_layout(out_path):
        raise ValueError(f"out_path '{out_path}' は標準的なnarrationパス規約に従っていないため、"
                          "Review Lockの対象にできません。")
    theme_id, level, segment_id = derive_segment_key(out_path)
    level_out_dir = _level_out_dir_from_out_path(out_path)
    store = _load_store(level_out_dir)
    store[segment_id] = {
        "state": "REGENERATE_APPROVED",
        "canonical_text_sha256": _text_hash(text),
        "theme_id": theme_id, "level": level, "segment_id": segment_id,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "reason": f"ユーザー({approved_by})による明示的な再生成承認",
        "approved_by": approved_by,
        "cumulative_tts_attempts": (store.get(segment_id) or {}).get("cumulative_tts_attempts", 0),
        "cumulative_asr_calls": (store.get(segment_id) or {}).get("cumulative_asr_calls", 0),
    }
    _save_store(level_out_dir, store)
    _append_attempt_history({
        "run_id": str(uuid.uuid4()), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "theme_id": theme_id, "level": level, "segment_id": segment_id,
        "action": "REGENERATE_APPROVED_GRANTED", "approved_by": approved_by,
    })
    return store[segment_id]


def _blocked_result(check: dict, out_path: str) -> dict:
    locked = check.get("locked_entry") or {}
    theme_id, level, segment_id = check.get("theme_id"), check.get("level"), check.get("segment_id")
    _append_attempt_history({
        "run_id": str(uuid.uuid4()), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "theme_id": theme_id, "level": level, "segment_id": segment_id,
        "action": f"BLOCKED_{check.get('status')}",
        "tts_attempts_this_call": 0, "asr_calls_this_call": 0,
        "result_status": None, "human_review_reached": True,
        "final_lock_state": check.get("status"),
    })
    return {
        "status": "HUMAN_REVIEW_LOCKED", "human_review_lock_status": check.get("status"),
        "reason": (f"[ER-011-HUMAN-REVIEW-COST-GUARD-01] このsegmentは既に{check.get('status')}状態です。"
                   f"明示的なapprove_regenerate()呼び出しが無い限り、TTS/ASRは一切呼び出しません"
                   f"(0 API call)。詳細: {check.get('reason')}"),
        "path": out_path, "asr_verified": False,
        "locked_entry": locked,
        # ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part L: 過去にrecord_
        # outcome()が保存した実際の試行履歴を復元する(record_outcome()側
        # の修正より前にlockされたsegmentは"last_attempts_log"フィールド
        # 自体が無いため、その場合のみ従来通り空配列になる)。
        "attempts_log": locked.get("last_attempts_log") or [],
    }


# ============================================================
# Part G: Human Review Queue重複防止
# ============================================================
def is_duplicate_queue_entry(queue_path: str, wav_path: str, canonical_text: str) -> bool:
    """同一(wav_pathから導出されるsegment)・同一canonical_textの
    エントリが既にqueueに存在するかを確認する。英語側(er006_secondary_
    asr_01.py)・日本語側(er007_ja_secondary_asr_01.py)の_log_human_
    review()から共通で呼ぶ。"""
    if not os.path.exists(queue_path):
        return False
    target_hash = _text_hash(canonical_text)
    with open(queue_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("wav_path") == wav_path and _text_hash(record.get("canonical_text") or "") == target_hash:
                return True
    return False


# ============================================================
# OPEN-105 fix(ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-
# RETRY-ACCOUNTING-FIX-19): guarded_generate二重会計バグの修正
# ============================================================
# 発見(2026-09-01前タスク監査): generate_key_phrase_component_verified()
# (@review_lock.guarded_generate("en"))が、内部で
# generate_narration_snippet_verified_strict()
# (@review_lock.guarded_generate_with_language_arg)を直接呼び出している。
# 両方とも独立にcheck_before_generation()/record_outcome()を実行する
# ため、実TTS試行3回の1回の論理的生成操作が、内側のrecord_outcome()で
# cumulative_tts_attempts=3として記録された直後、外側のrecord_outcome()
# が同じ3試行分をresult["standard_attempts_log"]経由で再度読み取り、
# cumulative_tts_attempts=6として上書きしてしまっていた
# (er011_output/attempt_history.jsonlの同一timestamp2エントリで確認済み)。
#
# generate_narration_snippet_verified_strict()は他の呼び出し元
# (stage_c_generate_new_narrations()等)からも直接・単独で呼ばれるため、
# そちらのデコレータ自体は残す必要がある。修正は「同一out_pathに対する
# guarded呼び出しが既に進行中の場合、ネストした内側の呼び出しは
# check_before_generation/record_outcomeを行わずfnへそのまま委譲する」
# というreentrancy guardをデコレータ内部に追加する形で行う(呼び出し側の
# コード・関数シグネチャ・fallback_budget計算等は一切変更しない)。
_ACTIVE_GUARDED_OUT_PATHS: set[str] = set()


def guarded_generate(language: str):
    """(text, out_path, *args, **kwargs) -> dict という共通シグネチャを
    持つ既存のTTS retry-loop関数(Cascade呼び出し元)へ、Review Lockの
    事前チェック・事後記録を追加するデコレータ。関数内部のロジックは
    一切変更しない(呼び出しの前後をラップするだけ)。

    OPEN-105 fix: 同一out_pathに対して既に外側のguarded呼び出しが進行中
    (ネストした2重guard)の場合、check_before_generation/record_outcomeを
    スキップしfnへ直接委譲する(1回の論理的な生成操作=1回のrecordを保証)。"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(text, out_path, *args, **kwargs):
            if out_path in _ACTIVE_GUARDED_OUT_PATHS:
                return fn(text, out_path, *args, **kwargs)
            check = check_before_generation(out_path, text, language)
            if not check["proceed"]:
                return _blocked_result(check, out_path)
            run_id = str(uuid.uuid4())
            t0 = time.time()
            _ACTIVE_GUARDED_OUT_PATHS.add(out_path)
            try:
                result = fn(text, out_path, *args, **kwargs)
            finally:
                _ACTIVE_GUARDED_OUT_PATHS.discard(out_path)
            record_outcome(out_path, text, language, result, run_id=run_id,
                           duration_seconds=round(time.time() - t0, 2))
            return result
        return wrapper
    return decorator


def guarded_generate_with_language_arg(fn):
    """(text, language, out_path, *args, **kwargs) -> dict という
    シグネチャを持つ関数(repro01.generate_narration_snippet_verified_
    strict等、1つの関数がen/ja両方を扱う)向けの変種。languageは実引数
    から取得する(デコレータ引数として固定しない)。

    OPEN-105 fix: guarded_generate()と同じreentrancy guardを適用する。"""
    @wraps(fn)
    def wrapper(text, language, out_path, *args, **kwargs):
        if out_path in _ACTIVE_GUARDED_OUT_PATHS:
            return fn(text, language, out_path, *args, **kwargs)
        check = check_before_generation(out_path, text, language)
        if not check["proceed"]:
            return _blocked_result(check, out_path)
        run_id = str(uuid.uuid4())
        t0 = time.time()
        _ACTIVE_GUARDED_OUT_PATHS.add(out_path)
        try:
            result = fn(text, language, out_path, *args, **kwargs)
        finally:
            _ACTIVE_GUARDED_OUT_PATHS.discard(out_path)
        record_outcome(out_path, text, language, result, run_id=run_id,
                       duration_seconds=round(time.time() - t0, 2))
        return result
    return wrapper
