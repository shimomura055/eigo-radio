# 委任ログ: TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(修正1回目、2026-09-27)

以下はFableからSonnet実行層へ渡された委任文の全文(転記)。

---

管理ID: TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(修正1回目: 時刻表記コロンの既存仕様内是正。コード+テスト+fixtureのみ。**TTS実行なし・¥0**。Family X再TTSは別委任)。一時ファイル `docs/pm/ACTIVE_TASK_SYM4.md` / `docs/pm/RESULT_PACKET_SYM4.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_04.md` へ保存しcommitに含める。触ってよいのは `er003_audio_tts_asr_safety.py`(セクションGのNormalizer/Gate)とそのtest、fixture JSON、REPORT追記のみ。`er003_v1_n3_01_tts_generate.py`/`er006_*`/`er025_*`/`er019_*`は別Agentが編集中→触らない。SSOTは編集しない(記載案のみ)。編集は最小差分・1回で行い、直後に `python -c "import er003_audio_tts_asr_safety"` で確認(他Agentがimport中)。

## 既存資産照合(先頭で実施、分類を記載)
- CURRENT_SPEC「TTS記号正規化(全Family共通)」節(Grep)のルール: 「:; → ポーズとして処理、文字名として読ませない」「数値記号(% $ ¥)は可能な限り原稿生成時点で自然語表現」「固有名称等、記号が不可避な実例がある場合は勝手に一般化せず報告する」。
- 事象: Family X Hormuz `full_story_part2`(A2/B1B)本文中の時刻表記 "11:04 a.m." のコロンが、Normalizer(`normalize_colon_semicolon_pause_en`)で句読点化されず(または句読点化されて "11. 04" のように壊れず)、Gate `detect_prohibited_symbols`/`RESIDUAL_PLACEHOLDER_OR_PAUSE_SYMBOL` がTTS呼び出し前にSTOP(NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md §Stage 3c参照)。同じコロンはStage 3bの旧combined textにも存在(見出し分離とは無関係)。
- 分類: **A(既存仕様の実装範囲の穴)**。「:;→ポーズ」は句読点としてのコロンが対象で、時刻表記 `H:MM` のコロンは「記号が不可避な実例(数値表記)」に該当し、ユーザー仕様は「報告」を求めている。新仕様は作らない。

## 作業
1. 実装(最小差分): 英語・日本語Normalizerで、時刻パターン `\b\d{1,2}:\d{2}\b`(任意で後続の a.m./p.m./AM/PM)を**変換対象から除外(pass-through)**し、Gate側でも同パターンを禁止記号として検出しない(既存英語TTSは "11:04 a.m." を自然に読む前提。根拠: Family Aの既存記事に時刻表記を含む音声がOKで存在するかをGrepで確認し、あればREPORTに実例パスを記載。無ければ「未検証、Family X再TTS時に確認」と明記)。他の用途(比率 "3:1"、聖書引用等)は今回一般化せず、`H:MM`のみ。除外ロジックはfixture化。
2. fixture追加: "The plan changed at 11:04 a.m." / 「午前11:04に」/ 否定例 "Three reasons: budget" (従来どおり句点化)。unit testで決定論性・既存9 fixtureの無回帰。
3. REPORT `TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_REPORT.md` 末尾に「§12 修正1回目(2026-09-27): 時刻表記コロン」を追記(既存資産照合の分類、実例、diff、fixture、SSOT記載案=CURRENT_SPEC該当節へ「時刻表記 H:MM のコロンは数値表記として無変換(2026-09-27実例Hormuz)」の追記案、Family X Hormuz part2の再TTSは読み解決修正commit後の別委任で実施する旨)。
4. 回帰: `er003_audio_tts_asr_safety` 関連test+`er024`系fixture testの単独実行(全体regressionは他Agent並走のため次回closeoutで)。

Git: 変更ファイル・test・fixture・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。トレーラー `Management-ID: TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`。push origin main。reset/amend/rebase/force push禁止。

---

## 実施メモ(Sonnet実行層、実施後追記)

- er024系スクリプト(`er024_tts_symbol_normalization_all_family_production_
  wiring_01_fixtures.py`)は実TTS/実ASR APIを呼び出すruntime evidence
  scriptであり、本委任の明示制約(TTS実行なし・¥0)に反するため実行しな
  かった。単体test(`er003_test_audio_tts_asr_safety.py`、`.venv`のPython
  経由、100 tests OK)のみで回帰確認を行った。
- 詳細は`TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_REPORT.md`
  §12参照。
