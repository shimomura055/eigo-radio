# AUW(ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01) 委任_05: Production runnerのTTS生成stage入口に付けるrun scope。
#
# `with_secondary_run`: stage実行中だけ er006_secondary_asr_01.begin_secondary_run() を有効にする
#   (run単位のSecondaryCache = 同一wavの重複Secondary呼出0 / circuit breaker = 連続障害でそのrunのSecondaryを止め技術STOP。
#    技術STOPはHuman Review Lockではない: DESIGN_02_ADDENDUM_01 §4/§7)。終了時(例外時も)必ず破棄し、別run/別testへ状態を持ち越さない。
#   既にrun scopeが有効な場合(入れ子)は外側のscopeを再利用し、内側では開始も破棄もしない。
#   Prompt/閾値/回数/判定は一切変えない(cache+breakerの有効化のみ)。EN adapter(er006)とJA adapter(er007: _shared_run_cache_and_state)が共有する。
# er006_secondary_asr_01は**呼出時に遅延import**する(本moduleをimportしても重い依存を引かない/循環importを作らない)。
from __future__ import annotations

import functools


def _secondary_module():
    import er006_secondary_asr_01 as secondary_asr
    return secondary_asr


def run_scope_active() -> bool:
    return _secondary_module()._RUN_STATE is not None


def with_secondary_run(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        sec = _secondary_module()
        if sec._RUN_STATE is not None:
            return fn(*args, **kwargs)
        sec.begin_secondary_run()
        try:
            return fn(*args, **kwargs)
        finally:
            sec.end_secondary_run()
    wrapper.__secondary_run_scoped__ = True
    return wrapper
