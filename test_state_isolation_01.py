# ============================================================
# test_state_isolation_01.py
# HR-QUEUE-TEST-CONTAMINATION-FIX-01 委任_02 (2026-10-22, OPEN-447)
# ============================================================
# 単体testがProductionの監査ログ(er011_output/attempt_history.jsonl)へ
# test fixture行を追記する副作用を防ぐ共通helper。
# 使い方: test fileの先頭(他のproject moduleのimport後でも前でもよい)で
#     import test_state_isolation_01  # noqa: F401
# するだけで、import時にer011_human_review_lock_01.ATTEMPT_HISTORY_PATHを
# プロセス専用のtmpファイルへ差し替える(プロセス終了時にtmpを削除)。
# Production codeは一切変更しない。個別testが自前でpatchする場合はそちらが優先される
# (後からpatchするため)。HR queue(英/日)のpathもmoduleに存在すれば同様に差し替える。
# ============================================================
from __future__ import annotations

import atexit
import os
import shutil
import tempfile

PRODUCTION_ATTEMPT_HISTORY = "er011_output/attempt_history.jsonl"
_TMP_DIR = tempfile.mkdtemp(prefix="test_state_isolation_01_")
atexit.register(shutil.rmtree, _TMP_DIR, True)

ISOLATED_ATTEMPT_HISTORY = os.path.join(_TMP_DIR, "attempt_history.jsonl")
ISOLATED_HR_QUEUE_EN = os.path.join(_TMP_DIR, "human_review_queue_en.jsonl")
ISOLATED_HR_QUEUE_JA = os.path.join(_TMP_DIR, "human_review_queue_ja.jsonl")


def _redirect(module_name: str, attr: str, new_path: str, expected_default_suffix: str) -> None:
    try:
        mod = __import__(module_name)
    except Exception:
        return
    cur = getattr(mod, attr, None)
    # 既にtmpへ差し替え済み・別pathの場合は触らない(Productionの既定pathのときだけ差替え)
    if isinstance(cur, str) and cur.replace("\\", "/").endswith(expected_default_suffix):
        setattr(mod, attr, new_path)


def install() -> None:
    _redirect("er011_human_review_lock_01", "ATTEMPT_HISTORY_PATH", ISOLATED_ATTEMPT_HISTORY,
              "er011_output/attempt_history.jsonl")
    _redirect("er006_secondary_asr_01", "HUMAN_REVIEW_LOG_PATH", ISOLATED_HR_QUEUE_EN,
              "audio_retry_cascade_prod_01/human_review_queue.jsonl")
    _redirect("er007_ja_secondary_asr_01", "HUMAN_REVIEW_LOG_PATH_JA", ISOLATED_HR_QUEUE_JA,
              "ja_asr_cascade_01/human_review_queue.jsonl")


install()
