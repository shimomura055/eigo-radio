# OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01 委任_02 (2026-10-11、Sonnet実行層)

範囲: Opus独立レビュー(Fable照合済み)の必須1〜3・推奨5〜8の是正+是正後コードでのruntime evidence(a)〜(e)。branch `feature/scg-ja-secondary-01`(worktree `../eigo-radio-scg`)。mergeなし・SSOT編集なし。C2(同形異音語ガード)・推奨4(否定マーカー除外)はユーザー判断待ちのため未実装(設計案のみ`OPUS_REVIEW_FOLLOWUP_01.md`)。

## 是正
必須1: SCG除外にentity_like/reading_dictionary_mismatch/原稿側ラテン文字差分を追加。必須2: SCG専用`_azure_stt_strict`(Error cancel=UNAVAILABLE、共通関数無変更)。必須3: 本番条件(Resolver ON+LLM mock・expected_readings・実装関数で除外算出)のPhase 0回帰追加。推奨5: `classify_ja_asr_match(allow_reading_resolver)`でSecondary判定のResolver不呼出。推奨6: `length_ok`引数を4呼出元から渡しFalse時SCG不実行。推奨7: master store manifestに`audio_classification`/`scg_result`追記。推奨8: NORMALIZEDに既存承認済み正規化が含まれる旨を文書化。
副作用: Phase 0救済14件のうちg8(ガス->カス、entity_like)がC1で対象外(本番条件で救済13件)。C群NG 5件は不変。

## 検証
- `er007_ja_scg_test_01.py`/`er007_ja_scg_phase0_regression_test_01.py`: PASS(件数は最終報告参照)。全suite同一性・Dangling: 最終報告/`full_suite_*_02.txt`。
- runtime evidence: `er053_output/open258_scg_production_wiring_01/RUNTIME_EVIDENCE_01.md` + `runtime_evidence_01.jsonl`。見積合計約2.64円(上限5円内)、新規TTS 0。

## 課金・汚染
実行は`runtime_scg_01.py`のみ(Production外)。追跡ファイル汚染は実行後に`git status`/`git checkout --`で確認(下記)。

## 最終結果
- 新規/更新test: `er007_ja_scg_test_01.py` + `er007_ja_scg_phase0_regression_test_01.py` 計58件PASS。関連既存(`er006_master_audio_store_01_test.py`、er020 2ファイル)PASS。
- 全suite(`full_suite_summary_02.txt`、`full_suite_fail_set_scg_branch_02.txt`): 117 failed/5804 passed/9 errors。baselineとの差は無関係なer015収集時ERROR 1件(当該ファイルは本変更で未改変、委任_01の255ファイル対象外)のみ。failure集合同一。
- Phase 0回帰(本番条件): 救済13件PASS・C群5件NG維持(誤PASS 0)。g8はC1(entity_like)でNOT_APPLIED(救済14->13)。
- runtime evidence: (a)(b)(d)(e)=PASS、(c)はg11案でPrimary不再現(2回、根拠に数えず)のため実データ2ケース`c_g12`(SCG NG x3=attempt消費・合計3回STOPPED)/`c2`(fallbackでSCG PASS)へ分割してPASS。見積合計2.64円、新規TTS 0。
- 追跡/共有ファイル汚染: runtime実行(`runtime_scg_01.py`)による追記は0(`er011_output/attempt_history.jsonl`の差分はすべて全suite実行のtest theme行で、`git checkout --`で復元済み)。suite実行で生じた`_test_*`/`_test_scratch`未追跡ディレクトリも削除済み。
