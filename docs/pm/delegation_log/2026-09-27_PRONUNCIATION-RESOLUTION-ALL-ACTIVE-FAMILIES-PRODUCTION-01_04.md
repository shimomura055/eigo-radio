管理ID: PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正2回目=closeout。Guardrail ¥60、TTS/ASRは下記2のみ)。一時ファイル `docs/pm/ACTIVE_TASK_PRN4.md` / `docs/pm/RESULT_PACKET_PRN4.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_04.md` に保存しcommitに含める。**必ず `TTS_EXECUTION_MODE=STANDARD` を設定してから実行**(前回JA-1でBatch実行した手順ミスの再発防止。実行コマンドと環境変数設定をRESULT_PACKETに逐語記録)。APIキーは環境変数のみ、key本文を表示・log・commit・報告に書かない。

## 先出しRead
- `PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01_REPORT.md` §14〜§21(修正1回目 commit 1aead031、SSOT記載案は§21)
- `docs/pm/PM_GOVERNANCE.md` Gate 3チェックリスト(Grep「Gate 3」)
- CURRENT_SPEC.md の読み解決/Pronunciation該当節(Grep「Pronunciation」「読み解決」で該当節のみ)

## Fable Gate 3 判定(前提として渡す)
修正1回目の成果はOpus BLOCKER-1/2是正・Stage 3c誤注入0件・Muse機構evidence(3回とも正発話)・Hormuz Candidate E PHONETIC_MATCH・Melos seed cache hit・regression既知6件のみ、で受入条件を満たす。**PRODUCTION_WIRED確定にはSSOT反映とMuse 2回目(cache hit)evidenceが未了**。本委任でそれを完了する。判定文言はFableが最終決定するので、REPORTには「Fable Gate 3判定待ち」のまま書く。

## 作業
1. **SSOT反映**(§21記載案をベースに最小差分):
   - CURRENT_SPEC.md 読み解決節: Phase 2確定内容(語境界一致Ledger検索、cascade_unresolved_entityのTTS注入除外、`tts_injection_disabled`隔離、LedgerKey source_context一般機構、`seed_work_canon_reading()`、negative cache 6h+run単位web lookup上限5、`ALLOW_PRONUNCIATION_WEB_LOOKUP` test switch、ledger_health_check、telemetry path)。JA確定読みのTTS直接伝達は別Phase(ユーザー既決)と明記。
   - DECISION_LOG.md: 修正1回目エントリ(ユーザー承認2026-09-27、Opus L2所見反映、Melos人名=resolver work_canon seed[ユーザー判断ではない]、EN `generate_english_component_minimal_instruction` 配線deferred)。
   - OPEN_ITEMS.md 新規登録(いずれもPM追跡、USER_DECISION_REQUIREDにしない): (a) 本番`ledger.json`への複数Agent同時書き込み競合リスク(§21観測、ロック/原子的書込み未実装)、(b) Family X B1B英語segment(`generate_charon_english`経路)でEN resolver未配線、(c) EN minimal_instruction配線deferred、(d) JA ASR Validatorの句読点正規化ギャップ(Meta A2 `japanese_title`: 全角「？」・中点・引用符「"人"」がASR書き起こしに再現されずTRUE_CONTENT_MISMATCH。**既存Validator仕様の実装範囲の穴として分類、修正は別委任**)、(e) `er006_kp5_canonical_bug_01_test_py` のtilde test 2件が承認済み全位置変換仕様(commit 19e638b5)に未追従+`_test.py`命名でregression discover対象外(別委任で更新)。既存OPEN(JA読み→TTS直接伝達別Phase等)があれば重複登録せず追記。
   - `docs/pm/REPORT_LEDGER.md` 本管理ID行更新(Opus発火: L2 1回)。
2. **JA-1 Muse 2回目evidence(STANDARD mode、¥10前後)**: `er019_family_x_audio_production_runner_01.py --slug family_x_b3_production_wiring_01 --run run_01 --level a2 --stage tts` を **a2/japanese_title のみ**対象に再実行(runnerにsegment限定オプションが無ければ、resolver部分だけを同runnerの関数呼び出しで再現し、その旨明記)。確認項目: web lookup **0回**(cache hit)、reading_dictionary経由でREADING_DICTIONARY分類、TTS発話「ミューズ」。総合判定が句読点要因でSTOPPEDでも本項の合否には含めない(差分文字を全件列挙してOPEN(d)へ記録)。Human Review Lock(`approve_regenerate()`)は実行しない。
3. REPORT §22「修正2回目(closeout)」: 1・2の結果、Gate 3チェックリスト各項目のevidence表(Production初回path/retry・fallback・regeneration/runtime evidence/実モデル・routing/regression/validator・integration tests/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER/Git/Dangling Reference Check/Family A/B/C未更新)。
4. Dangling Reference Check: REPORT・SSOTから参照するファイル・関数名が実在することをGrepで確認。

Git: 変更ファイルのみpath指定add(`git add -A`禁止、他Agent[Flash-Lite Stage 3: er022_*]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用・commit hash・変更ファイル・Gate 3表の要約を記載。
