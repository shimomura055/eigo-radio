# -*- coding: utf-8 -*-
"""Production判定(evaluate_attempt_with_cascade_detail)をoffline注入で呼ぶ薄いadapter(判定ロジックは無変更)。

Primary転写(asr_text)は引数で注入。Secondary(Azure)は`er006_secondary_asr_01.get_full_text_via_azure_stt_with_phrase_list`
を**このprocess内だけ**で記録済み転写を返す関数に差し替える(Production fileは書換えない。API 0)。
HR log/attempt_history等のProduction側副作用ファイルを書かないよう、detail版(ログ書込なし)を使い、
実行前後でgit tracked対象のHR logの行数が変わらないことをtestで確認する。
"""
import er006_secondary_asr_01 as sec


def judge_offline(canonical_text: str, primary_text: str, secondary_text, wav_path: str,
                  ledger_phrases=("Melos",), segment_id: str = "plw_trial") -> dict:
    calls = {"n": 0}

    def fake_azure(path, language="en-US", phrases=None, timeout_seconds=90.0):
        calls["n"] += 1
        if secondary_text is None:
            return None, "plw_trial: secondary text unavailable"
        return secondary_text, None

    orig = sec.get_full_text_via_azure_stt_with_phrase_list
    sec.get_full_text_via_azure_stt_with_phrase_list = fake_azure
    try:
        sec.reset_secondary_cache()
        detail = sec.evaluate_attempt_with_cascade_detail(
            canonical_text, primary_text, [], wav_path, language="en-US",
            ledger_phrases=list(ledger_phrases), cascade_enabled=True, segment_id=segment_id)
    finally:
        sec.get_full_text_via_azure_stt_with_phrase_list = orig
    j = detail.get("asr_judgement")
    cls = detail.get("classification")
    return {
        "verified": detail.get("verified"),
        "human_review_required": detail.get("human_review_required"),
        "stop_retrying": detail.get("stop_retrying"),
        "classification": getattr(cls, "audio_classification", None) or getattr(cls, "classification", None) or str(cls)[:120],
        "state": j.get("state") if isinstance(j, dict) else str(j)[:60],
        "reason_code": j.get("reason_code") if isinstance(j, dict) else None,
        "fake_azure_calls": calls["n"],
    }
