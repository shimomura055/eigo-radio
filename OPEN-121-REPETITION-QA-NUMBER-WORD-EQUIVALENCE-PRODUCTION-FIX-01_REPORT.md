# OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01

**管理ID**: OPEN-121-REPETITION-QA-NUMBER-WORD-EQUIVALENCE-PRODUCTION-FIX-01
**種別**: Production Gate最小修正 + 回帰テスト + 遡及再判定(¥0) + part2再判定・採用
**実行者**: sonnet-worker(Fable委任、初回)
**日付**: 2026-09-12
**ユーザー承認**: 2026-09-12(本文冒頭引用のとおり、数字↔数詞同値化のProduction実装・A-Family遡及監査・B1 full_story_part2再判定を承認)
**費用**: ¥0(ローカルfaster-whisper再実行・オフライン計算・既存wavファイルの複製のみ。新規TTS/ASR API呼び出しは一切なし)

## 冒頭要点(5行)

1. `er011_open121_repetition_qa_production_01.py`へ、綴り小数(two~twelve)↔算用数字の同値化を`_normalize_token_numeric_equiv()`として実装し、canonical側(`_normalize_tokens()`)・ASR側(`detect_ngram_repetition()`)の両方に一様適用した。閾値(`canon_count>=2`)・判定意味・`%`/`percent`は無変更。
2. 回帰テスト35件(既存30件+新規5件)PASS、依存する`OPEN-128`テスト9件PASS、プロジェクト全体回帰(`run_project_regression.py`、2309件収集)は既知fail3件(`er003_test_p2j_investigate.py`、テスト件数集計の恒常的なズレ、本修正と無関係)のみで新規failなし。
3. 遡及再判定(¥0、機械的)により、今回の修正で解消される誤flagは**3件**(タオルTrial-11 B1B `full_story_part2`、`pool_n4_supermarket` A2/B1B `full_story_part2`)で、RECONCILE-02調査結果と完全一致。既知真陽性2件("A wash is not just clean or dirty."・"Young travelers are not one single market...")は数値変更後も引き続きflagされたまま(退行なし)。
4. タオルTrial-11 B1B `full_story_part2`は本バグにより実際にHUMAN_REVIEW_REQUIRED/STOPPEDへ到達していた。内容一致していた4取り(attempt2,3,5,6)全てが新QAでPASSしたため、ユーザー事前承認どおり試聴なしで既存の採用規則(最初にPASSした取り)に従いattempt2を`full_story_part2.wav`へ採用し、`review_lock_state.json`をRESOLVEDへ更新した(TTS再生成なし、¥0)。
5. `pool_n4_supermarket`(既存Production A-Family音声)側は、生成当時Repetition QAが未配線だったため実際には音声のretry・差し替えは発生していない(純粋な診断sweep上の誤flag、`OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01`で「要人間試聴確認」と未決のまま記録されていたもの)。今回の修正でこの特定パターンによる要確認は解消したが、音声ファイル自体には触れていない。

---

## 1. 実装(最小修正)

対象: `er011_open121_repetition_qa_production_01.py`(`_normalize_tokens()`直前・`detect_ngram_repetition()`内、2箇所)

- `_NUM_WORD_TO_DIGIT_EN`辞書(two~twelve、`tts_safe_number_words_en()`の`_EN_NUMBER_WORDS`と完全に同一語彙)を追加。
- `_normalize_token_numeric_equiv(word)`: 既存`dq18._normalize_token()`のあとにこの辞書でlookupするだけの薄いラッパー。
- `_normalize_tokens()`(canonical側)・`detect_ngram_repetition()`のASR側token生成、の2箇所を`dq18._normalize_token`直呼びから`_normalize_token_numeric_equiv`経由へ置き換え。
- `_canonical_repeat_count()`・閾値(`>=2`)・`find_repeated_spans()`・方式D/D'は無変更。
- `%`/`percent`は対象外(辞書に含めていない、コードコメントで明記)。
- モジュール直接import不可の理由(`er003_v1_n3_01_tts_generate`→`er003_v1_sing01_news_tail_fix`→本モジュールという既存の循環importが既にあるため逆方向importは不可)を踏まえ、辞書は複製(キー集合を`_EN_NUMBER_WORDS`と同一に保つ設計、コードコメントに明記)。

## 2. 回帰テスト

- 新規テストクラス`NumberWordDigitEquivalenceTests`(`er011_open121_repetition_qa_production_wiring_01_test_01.py`)を5件追加:
  (a) "two"/"2"混在の並行構文→`canonical_repeat_count=2`で非flag、
  (b) canonical1回/ASR2回の真陽性→引き続きflag、
  (c) 数詞を含まない4サンプルでtoken出力が修正前と完全一致(byte不変)、
  (d) "45%"/"percent"/"5%"は無変換のままpin、
  (e) 範囲境界("one"無変換、"twelve"→"12"、"thirteen"無変換、既存算用数字はそのまま)。
- コマンド: `.venv/Scripts/python.exe -m unittest er011_open121_repetition_qa_production_wiring_01_test_01 -v`
  → **35 tests, OK**(既存30件+新規5件、実行時間約90秒、実音声fixture含む)。
- 依存テスト: `.venv/Scripts/python.exe -m unittest er011_open128_method_d_local_asr_confirm_production_wiring_01_test_01 -v` → **9 tests, OK**。
- プロジェクト全体回帰: `.venv/Scripts/python.exe run_project_regression.py --json-summary ...`
  → **collected=2309 passed=2306 failed=3 errors=0**。失敗3件はすべて`er003_test_p2j_investigate.py`(テストファイル総数の集計値が実ファイル数の増加に伴い恒常的にズレる既知の環境依存fail、今回の変更と無関係)。新規failなし。

## 3. 遡及再判定(¥0、機械的)

抽出範囲: `er0*_output/**/audit/tts_generation_results.json`(110ファイル、method_a_ngramのmatch 58件)+ `er011_output/open121_existing_audio_dprime_sweep_01/results/{method_a.json, classified_table.json}`(既存Production音声への横断diagnostic sweep、422キー/1654件、うちFLAG_A 19件)。

比較方法: 「stored(記録済み)」「prefix(今回の修正を除いた現行コード基準、OPEN-127 em dash修正は含む)」「postfix(今回の修正込み)」の3値を再計算し、**今回の修正だけによる差分**(prefix→postfix)と、**既に別修正(OPEN-127)で解消済みの古い記録の残存差分**(stored→prefixのズレ、今回の修正とは無関係)を区別した。

| 記録ID/テーマ | segment | 旧flag(prefix) | 新flag(postfix) | 変化理由 |
|---|---|---|---|---|
| `discovery_generalization_towels_trial_11/b1b`(attempt2,3) | full_story_part2 | flagged(count=0) | 非flag(count=2) | 数詞同値化で解消(false positive解消)。span="after two months" |
| `pool_pilot_01/pool_n4_supermarket/a2`(既存Production音声) | full_story_part2 | flagged(count=0) | 非flag(count=2) | 数詞同値化で解消。span="After three months, sales" |
| `pool_pilot_01/pool_n4_supermarket/b1b`(既存Production音声) | full_story_part2 | flagged(count=0) | 非flag(count=2) | 数詞同値化で解消。span="After three months," |
| `discovery_generalization_towels_trial_11/a2` | point_two | flagged(count=1) | flagged(count=1、変化なし) | 真陽性維持。span="A wash is not just clean or dirty."(数詞なし、対象外) |
| `open112_trial13`等/point_two("real_point_two_buggy"系、複数コピー) | point_two | flagged(count=1) | flagged(count=1、変化なし) | 真陽性維持。span="Young travelers are not one single market..."(span中の"one"は対象外、"29"は既に算用数字で無変換) |
| `pool_n9_tip_screens`(a2 point_one/point_two) | — | flagged(count=0) | flagged(count=0、変化なし) | "%"記号隣接span、対象外としてpin(範囲拡張は別途ユーザー判断) |
| `pool_n18_notifications`(b1b point_one) | — | flagged(count=0) | flagged(count=0、変化なし) | "108"(既に算用数字、範囲外)、対象外 |
| `er012_laneb_trial08`等"do not need"複数件 | point_two | **stale**: stored時点count=1だが、現行prefix基準では既にcount=2・非flag | 非flag(変化なし) | OPEN-127(em dash修正、既にPRODUCTION_WIRED)で解消済みの旧記録。**今回の修正とは無関係**(誤って本修正の成果として報告しないよう区別) |

**真陽性が消えていないことの個別確認**(本文とASRを引用):
- span "A wash is not just clean or dirty.": canonical本文中この句は1回のみ→`canonical_repeat_count`は修正前後とも1のまま、flagged維持。
- span "Young travelers are not one single market. Women aged 29 and under still showed strong interest in famous tourist places.": canonical本文中この句は1回のみ(該当箇所は1箇所のみ)→`canonical_repeat_count`は修正前後とも1のまま、flagged維持。span中の"29"は既に算用数字(無変換)、"one"は代名詞曖昧性のため対象外辞書に含めていない。

## 4. 影響範囲

- **タオルTrial-11 B1B `full_story_part2`**: 本バグにより実際に`HUMAN_REVIEW_REQUIRED`/`final_status=STOPPED`(6回TTS試行・6回ASR呼び出し)へ到達していた(現に音声のretryが繰り返し発生・ブロックされていた対象)。詳細は5節。
- **`pool_n4_supermarket`(A-Family、既存Production配線)A2/B1B `full_story_part2`**: `OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01`(過去タスク)が既存wavへ事後的にMethod Aを再実行した**診断sweepの結果のみ**であり、この音声が生成された時点ではRepetition QAは配線されていなかったため、実際のretry・差し替え・Human Review Lockには一度も到達していない(同レポート内「review_lock記録なし」)。当該レポートは「短い汎用語句の誤検知リスクがあり人間試聴確認が必須」として未着手のまま記録していたが、今回の修正でこの特定パターン(綴り小数由来)は解消したため、その未決の試聴確認ニーズはこの2件について解消(moot)である。**音声ファイル自体は今回変更していない**(元々差し替え対象ではなかったため)。
- 上記以外にProduction採用済み・現在flag中の音声で、今回の数詞同値化により状態が変わるものは見つからなかった(残りの記録は真陽性維持、対象外パターン[%/108]で変化なし、またはOPEN-127既修正のstale記録)。

## 5. `full_story_part2`再判定・採用(タオルTrial-11 B1B)

- 6取り中、内容一致(`NORMALIZED_MATCH`/`HIGH_SIMILARITY_SAFE`)だった4取り(attempt2, 3, 5, 6。attempt1・4は`TRUE_CONTENT_MISMATCH`で元々別理由により対象外)へ、修正後の`evaluate_repetition_qa()`(ローカルfaster-whisper再実行、方式A+D+D'全て)を実施。
  - 結果: **attempt2, 3, 5, 6 全て `flagged=False`**(A=False, D=False, D'=False)でPASS。
- ユーザー事前承認(「内容一致しているtakeが新QAでPASSするなら、ユーザー試聴は不要」)に従い、試聴なしで既存の採用規則(retry loop内で最初に`verified=True`となる取り=時系列で最初にPASSした取り)どおりattempt2を採用。
  - `full_story_part2_attempt2_englishstyleprefixwidemargin.wav`を`full_story_part2.wav`へ複製(TTS API呼び出しなし、¥0)。
  - `review_lock_state.json`の`full_story_part2`エントリを`state=HUMAN_REVIEW_REQUIRED/final_status=STOPPED`から`state=RESOLVED/final_status=OK`へ更新し、採用理由・採用元attemptファイルパスを`reason`/`adopted_attempt_audio_path`へ記録(他segmentのエントリ・`full_story_part1`は無変更)。
- `tts_generation_results.json`の該当エントリ(attempt別`verified`/`repetition_qa_evidence`)は**同期していない**(歴史的な実測記録として当時のロジックでの結果をそのまま保持する方針とし、本タスクでは変更対象外とした)。**同期要否はFable/ユーザー判断が必要**(監査上、旧ロジックでの`flagged=true`記録と、採用結果`RESOLVED`が同一ファイル内で一見矛盾して見えるため、`review_lock_state.json`の新しい`reason`欄で経緯を追跡可能にはしてあるが、`tts_generation_results.json`側にも同様の注記を追加するかは要判断)。

## Closeout情報

- 変更ファイル: `er011_open121_repetition_qa_production_01.py`、`er011_open121_repetition_qa_production_wiring_01_test_01.py`、`er011_output/discovery_generalization_towels_trial_11/b1b/audit/review_lock_state.json`(JSON、追記のみ)。`full_story_part2.wav`(gitignore対象、git管理外)。
- 詳細証跡(scratchpad、読み取り専用元データ+再計算スクリプト、参考保存): `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\scratchpad\repqa\`(`retro_sweep.py`/`retro_sweep_all.json`/`retro_sweep_changed_by_fix.json`/`retro_sweep_stale_unrelated.json`/`part2_rejudge.py`/`part2_rejudge_results.json`)。
- Git操作: 未実施(本タスクの禁止事項どおり、commit/pushはFableが統合)。
- 未決事項: `tts_generation_results.json`同期要否(上記5節)、`%`/`percent`同値化の範囲拡張要否(今回スコープ外、ユーザー判断待ち)。
