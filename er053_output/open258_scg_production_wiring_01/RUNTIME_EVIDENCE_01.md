# RUNTIME_EVIDENCE_01 (OPEN-258 SCG Production配線 委任_02、是正後コード)

実行日: 2026-10-11 / worktree `C:/Users/tensh/eigo-radio-scg`(branch `feature/scg-ja-secondary-01`) / script: `runtime_scg_01.py`(Production外、TTSのみ保存済みwavへ差替、新規TTS=0) / 生証跡: `runtime_evidence_01.jsonl`(1行=1実行、全イベント・転写全文付き)。
サービス: Primary=OpenAI `gpt-4o-mini-transcribe`(`routing.transcribe`実呼出。最新世代の最上位系ではなく既存Production Primary route固定=本番ライン評価のため意図的な例外)、Secondary=Azure Speech STT(region japanwest、Speech SDK 1.50.0、ja-JP、連続認識、Phrase Listなし)。Reading Resolver=本番ON(実LLM)。
費用は実測請求ではなく登録単価換算の見積(Azure $1/h x160円/USD 秒切上げ、OpenAI ASR $0.003/min、Resolver LLMは1回0.05円の上限見積)。

## 結果表

| case | 内容 | 期待 | 実測 | 判定 | 見積費用(円) |
|---|---|---|---|---|---|
| a | Production関数evaluate_attempt_ja_with_cascade_detailへMETA japanese_title attempt1保存wavを実呼出(実Primary+実Azure、Resolver本番ON) | TCM->SCG->PASS(SECONDARY_CONFIRMED_PRIMARY_FALSE_NG) | Primary=「AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。」(TRUE_CONTENT_MISMATCH) -> final=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG, scg_result=PASS, Azure SCG 1回, Secondary=「AIの電話に人間が出演。問題はキャスト変更のお知らせでした。」 | PASS | 0.4601 |
| e | JA_SCG_ENABLED=0(kill switch)でMETA音声。Azure呼出0回・従来動作(TCMのまま) | Azure呼出0回、scg_result=DISABLED_BY_FLAG、verified=False(従来のTRUE_CONTENT_MISMATCH) | Primary=「AIの電話に人間が出現。問題はキャスト変更のお知らせでした。」(TRUE_CONTENT_MISMATCH) -> final=TRUE_CONTENT_MISMATCH, scg_result=DISABLED_BY_FLAG, Azure SCG 0回 | PASS | 0.149 |
| b | n3.generate_a2_japanese_with_reading_safety(実)->repro01 loop(実)->guarded_generate(実)、TTSのみ保存wav差替(META japanese_title) | PASSでattempt1完了、TTS差替呼出1回(=再生成0)、SCG PASS | status=OK, attempt1 Primary=「AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。」 class=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG scg=PASS, TTS差替1回(再生成0), Azure SCG 1回 | PASS | 0.4601 |
| c | n3経路: 標準1〜2回目=g11音声(SCG NG想定)、fallback=g11良音声(SCG PASS想定)。TTSのみ差替、attempt消費とfallback SCGを確認 | 標準2回消費(SCG NG x2)->fallback 1回(SCG PASS)->OK(fallback_used=True)、合計3回上限内 | status=OK, 標準TTS1回, Primary=「理屈の上では」 class=EXACT_MATCH, SCG不発火(PrimaryがPASS) | FAIL_OR_NOT_REPRODUCED(Primary/Azureの出力が想定と異なる。観測値をそのまま記録) | 0.0155 |
| d | voice01.generate_charon_japanese(B系日本語、実)、TTSのみMETA保存wavのPCMに差替 | SCG PASSで標準attempt1完了(TTS差替1回) | status=OK, attempt1 Primary=「AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。」 class=SECONDARY_CONFIRMED_PRIMARY_FALSE_NG scg=PASS, TTS差替1回(再生成0), Azure SCG 1回 | PASS | 0.4601 |
| c | n3経路: 標準1〜2回目=g11音声(SCG NG想定)、fallback=g11良音声(SCG PASS想定)。TTSのみ差替、attempt消費とfallback SCGを確認 | 標準2回消費(SCG NG x2)->fallback 1回(SCG PASS)->OK(fallback_used=True)、合計3回上限内 | status=OK, 標準TTS1回, Primary=「理屈の上では」 class=EXACT_MATCH, SCG不発火(PrimaryがPASS) | FAIL_OR_NOT_REPRODUCED(Primary/Azureの出力が想定と異なる。観測値をそのまま記録) | 0.0155 |
| c_g12 | n3経路: 標準1〜2回目・fallbackとも g12音声(SCG NG想定)。TTSのみ差替 | SCG NGでattempt消費(標準2+fallback1=合計3回)->STOPPED、誤PASSなし、Azure 3回 | status=STOPPED, 標準SCG=['NG', 'NG'], fallback SCG=['NG'], TTS差替2+1回, Azure SCG 3回, Primary=「縛られる、自由になれる感じの」 | PASS | 0.6198 |
| c2 | n3 fallback attemptのSCG: 標準2回=TTS失敗(差替)でattempt消費、fallback=META音声 | 標準2回消費->fallback 1回目でSCG PASS->OK(fallback_used=True) | status=OK, fallback_used=True, 標準TTS失敗2回(消費)->fallback SCG=['PASS'], Azure SCG 1回 | PASS | 0.4601 |

実行8回の見積費用合計: **2.64円**(上限5円内)。新規TTS 0。

## 解釈・注意

- (a)(b)(d)(e)は想定どおり。(a)(b)(d)はPrimary「出現」(TRUE_CONTENT_MISMATCH)->Azure「出演」->`SECONDARY_CONFIRMED_PRIMARY_FALSE_NG`で、そのattemptで完了(attempt消費・再生成0)。(e)は`JA_SCG_ENABLED=0`でAzure呼出0回・従来のTRUE_CONTENT_MISMATCHのまま。
- (c)当初案(g11の悪音声x2+良音声)はPrimaryがg11 a2音声を今回正しく転写(「理屈の上では」)したため不一致が再現せず、SCG不発火(行`c`が2行、根拠に数えない)。Primaryの結果は実行ごとに変わり得るためそのまま記録した。代わりに実データで同じ観点を確認できる2ケースへ分けた: `c_g12`(g12音声: 標準2回+fallback1回とも「縛られる」と転写=SCG NGでattempt消費、合計3回でSTOPPED=上限不変・誤PASSなし)、`c2`(標準2回=TTS失敗で消費、fallback=META音声でSCG PASS=fallback attemptにもSCGが効く)。
- `c`/`c_g12`/`c2`のTTS差替は標準経路`p9a.generate_narration_snippet`とfallback`_generate_a2_japanese_minimal_instruction`のみ。ASR・Azure・Reading Safety・repro01 loop・guarded_generate・save_tts_attempt_audioは実物。(d)はvoice01が`resolve_tts_call_and_prompt`経由でPCMを得るため、そのcall_fnのみ保存wavのPCMへ差替(trim/ASR/SCGは実物)。
- 推奨8: SCG PASSのNORMALIZED_MATCHには既存承認済み正規化(variant layer Candidate C: カタカナ語末長音省略4文字以上、D-1: 位取り漢数字)が含まれる。SCGはこれを新規に緩和しておらず、PHONETIC_MATCHは自動PASSに含めない。
- c_g12でAzureは「縛られる」と転写(否定「ず」を丸めず)。否定マーカー除外(推奨4)はユーザー判断待ちで未実装(`OPUS_REVIEW_FOLLOWUP_01.md`)。
- 追跡/共有ファイルの汚染確認結果は委任ログ参照。
