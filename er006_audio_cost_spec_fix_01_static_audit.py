# ============================================================
# er006_audio_cost_spec_fix_01_static_audit.py
# ER-006-AUDIO-COST-SPEC-FIX-01: Drift Prevention Static Audit
# ============================================================
# 目的: ER-006-AUDIO-COST-PILOT-02/PRONUNCIATION-LEDGER-SECONDARY-ASR-01/
# AUDIO-RETRY-CASCADE-PROD-01/VALIDATOR-NUMERIC-COST-RECONCILE-01で決定・
# 配線した内容が、将来のcommitで気づかれずに古い経路へ後退(drift)して
# いないかを機械的に確認する。
#
# 対象を「Production到達可能ファイル」に限定する(legacy/experimental
# scriptは対象外、下記PRODUCTION_AUDIO_FILES参照)。
#
# 重要: このscriptは「古い経路が残っていないか」の否定確認(FAILすべき
# でない)と、「未配線のまま残っている既知gap」の状況報告(現時点では
# 意図的にFAILの状態を正直に記録する)の両方を含む。後者はassertion
# failureにはせず、KNOWN_GAPとして明示的に区別して出力する
# (ER-006-AUDIO-COST-SPEC-FIX-01タスク仕様の「honest reporting」要求に
# 対応するため。詳細はCURRENT_SPEC.md「Audio Production Pipeline」節・
# OPEN_ITEMS.mdのOPEN-50を参照)。
from __future__ import annotations

import re

PRODUCTION_AUDIO_FILES = [
    "er003_v1_crosslevel_audio_02_common.py",
    "er003_v1_repro01_main_generate.py",
    "er003_v1_sing01_news_tail_fix.py",
    "er003_v1_sing01_point_headings_aoede.py",
    "er003_v1_sing01_voice01_generate.py",
    "er003_v1_n3_01_tts_generate.py",
]

# Sol model checkの対象は、上記Audio生成6ファイルに加え、ER-006で新設した
# Pronunciation/ASR/Master Audio系の全SSOT・実装モジュールも含める
# (Writer/Support系のSol残存有無はer006_model_routing_contract_01_static_audit.py
# が既に別途カバーしているため、ここでは重複対象にしない)。
SOL_CHECK_FILES = PRODUCTION_AUDIO_FILES + [
    "er006_secondary_asr_01.py",
    "er006_asr_provider_routing_01.py",
    "er006_pronunciation_ledger_01.py",
    "er006_pronunciation_research_01.py",
    "er006_proper_noun_extraction_01.py",
    "er006_master_audio_store_01.py",
    "er006_pronunciation_tts_injection_01.py",
]

OLD_AZURE_ENGLISH_PRIMARY_MARKER = "get_full_text_via_azure_stt_continuous"
OLD_VALIDATOR_DIRECT_CALL_MARKER = "audio_validation.evaluate_attempt("
CASCADE_MARKER = "secondary_asr.evaluate_attempt_with_cascade("
ROUTING_TRANSCRIBE_MARKER = "routing.transcribe("
LEDGER_PHRASES_MARKER = "ledger_phrases="
SHARED_NARRATION_MARKERS = [
    "ensure_all_shared_narration_b1(",
    "ensure_all_shared_narration_a2(",
]
BATCH_CREATE_MARKER = "batches.create"
STANDARD_TTS_MARKER = "make_tts_call_fn"


def _read(filename: str) -> str:
    with open(filename, encoding="utf-8") as f:
        return f.read()


def check_no_azure_english_primary_direct_call() -> list[str]:
    """(a) 英語ASRがAzureへ直接依存する古い経路が、Production 6ファイルに
    残っていないことを確認する(英語Primary ASRはSSOT経由でOpenAIへ
    routingされているはずで、旧Azure直接呼び出し関数名がsource中に
    一切現れないことを機械的に確認する)。"""
    failures = []
    for filename in PRODUCTION_AUDIO_FILES:
        text = _read(filename)
        found = OLD_AZURE_ENGLISH_PRIMARY_MARKER in text
        status = "FAIL" if found else "OK"
        print(f"[{status}] {filename}: '{OLD_AZURE_ENGLISH_PRIMARY_MARKER}' 不使用")
        if found:
            failures.append(f"{filename}: 旧Azure直接ASR関数が残存")
    return failures


def check_no_old_validator_direct_call() -> list[str]:
    """(c) Production leaf pathが旧Validator(audio_validation.evaluate_attempt)
    を直接呼ばず、Secondary ASR Cascade経由(内部で新Validatorの
    classify_asr_matchを使う)になっていることを確認する。"""
    failures = []
    for filename in PRODUCTION_AUDIO_FILES:
        text = _read(filename)
        found = OLD_VALIDATOR_DIRECT_CALL_MARKER in text
        status = "FAIL" if found else "OK"
        print(f"[{status}] {filename}: '{OLD_VALIDATOR_DIRECT_CALL_MARKER}' 不使用(Cascade経由)")
        if found:
            failures.append(f"{filename}: 旧Validatorへの直接呼び出しが残存")
    return failures


def check_no_old_retry_loop_bypass() -> list[str]:
    """(d) 英語ASR検証(routing.transcribe(..., language="en-US"/asr_language))
    の呼び出し箇所が、必ず直後でsecondary_asr.evaluate_attempt_with_cascade()
    へ渡されており、ASR不確実性からTTSへ直接retryする古い経路が
    復活していないことを確認する。日本語(ja-JP)呼び出しはCascade対象外
    (設計上、Cascadeは英語固有名詞のASR不確実性向け)のため除外する。"""
    failures = []
    # コメント行や中間のlength_ok計算等を挟んでもCascade呼び出しを検出できる
    # よう、十分広い窓を取る(実測: 変数language=asr_language分岐+コメント込みで
    # 最大約450文字の間隔があるケースを確認済み)。
    window = 1000
    for filename in PRODUCTION_AUDIO_FILES:
        text = _read(filename)
        for m in re.finditer(re.escape(ROUTING_TRANSCRIBE_MARKER), text):
            line_no = text.count("\n", 0, m.start()) + 1
            call_end = text.index(")", m.start())
            call_args = text[m.start():call_end + 1]
            if 'language="ja-JP"' in call_args:
                continue  # 日本語はCascade対象外、正常
            after = text[m.start():m.start() + window]
            has_cascade = CASCADE_MARKER in after
            status = "OK" if has_cascade else "FAIL"
            print(f"[{status}] {filename}:{line_no} routing.transcribe(...) 直後にCascade経由あり={has_cascade}")
            if not has_cascade:
                failures.append(f"{filename}:{line_no}: 英語ASR呼び出しがCascade経由でない(旧retry loop復活の疑い)")
    return failures


def check_master_audio_not_bypassed() -> list[str]:
    """(f) 固定/完全一致再利用可能な音声(shared narration)の生成が、
    Master Audio Store経由の関数(ensure_all_shared_narration_b1/a2)を
    経由しており、segment生成のたびに無条件で毎回TTSし直す古い経路へ
    後退していないことを確認する。"""
    failures = []
    filename = "er003_v1_n3_01_tts_generate.py"
    text = _read(filename)
    for marker in SHARED_NARRATION_MARKERS:
        found = marker in text
        status = "OK" if found else "FAIL"
        print(f"[{status}] {filename}: '{marker}' 呼び出しあり(Master Audio Store経由)")
        if not found:
            failures.append(f"{filename}: {marker} 呼び出しが見つからない(Master Audio bypassの疑い)")
    return failures


def check_no_sol_model() -> list[str]:
    """(e) N3/Pool Audio関連ファイルにgpt-5.6-solのliteralが復活していない
    ことを確認する(Writer/Support系は別途er006_model_routing_contract_01_
    static_audit.pyでカバー済みのため、ここではAudio/Pronunciation系
    モジュールを対象にする)。"""
    failures = []
    for filename in SOL_CHECK_FILES:
        text = _read(filename)
        found = "gpt-5.6-sol" in text
        status = "FAIL" if found else "OK"
        print(f"[{status}] {filename}: 'gpt-5.6-sol' literal not present")
        if found:
            failures.append(f"{filename}: gpt-5.6-sol literal found")
    return failures


def check_pronunciation_route_not_ignored() -> list[str]:
    """(g、一部) Secondary ASR Cascade呼び出しが、必ずPronunciation
    Ledgerから取得したledger_phrasesを伴っており、発音情報が機械的に
    無視されていないことを確認する(空リストを渡すこと自体は正常な
    ケース足りうるが、キーワード自体が消えている=呼び出し経路から
    Pronunciation Ledgerが完全に切り離された、という後退を検出する)。"""
    failures = []
    window = 400
    for filename in PRODUCTION_AUDIO_FILES:
        text = _read(filename)
        for m in re.finditer(re.escape(CASCADE_MARKER), text):
            line_no = text.count("\n", 0, m.start()) + 1
            call_end = text.index(")", m.start())
            # 複数行呼び出しに対応するため、閉じ括弧の探索を簡易的に拡張
            depth = 0
            i = text.index("(", m.start())
            for j in range(i, len(text)):
                if text[j] == "(":
                    depth += 1
                elif text[j] == ")":
                    depth -= 1
                    if depth == 0:
                        call_end = j
                        break
            call_args = text[m.start():call_end + 1]
            has_ledger = LEDGER_PHRASES_MARKER in call_args
            status = "OK" if has_ledger else "FAIL"
            print(f"[{status}] {filename}:{line_no} Cascade呼び出しにledger_phrases引数あり={has_ledger}")
            if not has_ledger:
                failures.append(f"{filename}:{line_no}: Cascade呼び出しがPronunciation Ledgerを経由していない")
    return failures


def report_tts_batch_wiring_gap() -> None:
    """(b、既知gapとして状況報告のみ・assertion failureにはしない):
    Gemini TTS Batch APIをProduction標準として採用する、というDecisionは
    確定している(CURRENT_SPEC.md「Audio Production Pipeline」節参照)。
    しかし実際のProduction 6ファイルのTTS生成呼び出しは、いずれも
    Standard同期呼び出し(gclient.make_tts_call_fn() -> client.models.
    generate_content())のままであり、Batch(client.batches.create())への
    配線は未実装である。これは新しいドリフトではなく、以前から続く
    既知の未実装事項であり、OPEN_ITEMS.mdのOPEN-50として追跡する。
    このタスク(ER-006-AUDIO-COST-SPEC-FIX-01)のスコープは仕様SSOTの
    整合であり、新規のBatch配線実装は§13により明示的にスコープ外の
    ため、ここでは正直な状態報告のみ行い、AssertionErrorは送出しない。"""
    print("\n=== 既知GAP報告(assertion対象外、OPEN-50で追跡): Gemini TTS Batch配線 ===")
    for filename in PRODUCTION_AUDIO_FILES:
        text = _read(filename)
        uses_standard = STANDARD_TTS_MARKER in text
        uses_batch = BATCH_CREATE_MARKER in text
        print(f"[GAP] {filename}: Standard呼び出し(make_tts_call_fn)使用={uses_standard}, "
              f"Batch呼び出し(batches.create)使用={uses_batch}")
    print("[GAP] 結論: Batch APIはApproved Production方式として確定済みだが、"
          "実際のTTS生成call siteへの配線は未実装(現状は全てStandard)。"
          "新規実装は本タスクのスコープ外、OPEN-50で追跡。")


def run():
    failures = []
    failures += check_no_azure_english_primary_direct_call()
    print()
    failures += check_no_old_validator_direct_call()
    print()
    failures += check_no_old_retry_loop_bypass()
    print()
    failures += check_master_audio_not_bypassed()
    print()
    failures += check_no_sol_model()
    print()
    failures += check_pronunciation_route_not_ignored()

    report_tts_batch_wiring_gap()

    print("\n=== 静的に確認不能な項目(runtime telemetryでのみ確認可能) ===")
    print("[N/A] Secondary ASR Cascadeの実効性・発動率(OPEN-48/49): 実運用ログでのみ測定可能")
    print("[N/A] Pronunciation Research cache-hit率(OPEN-49): 実運用ログでのみ測定可能")
    print("[N/A] Master Audio Storeの実際の再利用率: reuse_telemetry.jsonlの運用蓄積でのみ測定可能")

    if failures:
        raise AssertionError(f"{len(failures)}件のstatic audit checkが失敗した:\n" + "\n".join(f"  - {f}" for f in failures))
    print(f"\nOK: Drift Prevention static audit 全チェックPASS(既知GAP=Batch配線は別途OPEN-50で追跡、assertion対象外)")


if __name__ == "__main__":
    run()
