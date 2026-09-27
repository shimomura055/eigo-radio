管理ID: TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(修正2回目、ユーザー承認済み 2026-09-27。**¥0、TTS/LLM API呼び出しなし**)。一時ファイル `docs/pm/ACTIVE_TASK_SYM5.md` / `docs/pm/RESULT_PACKET_SYM5.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_05.md` に保存しcommitに含める。

## 先出しRead
- `TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_REPORT.md` §12(修正1回目、commit 9bc458d0)
- `er003_audio_tts_asr_safety.py` セクションG(約860-1080行): `_TIME_HMM_COLON_RE`, `detect_prohibited_symbols`, `_SYMBOL_STOP_CATEGORIES`, `build_symbol_violation_prompt_note`, `_JA_COLON_SEMICOLON_RE`
- `er019_family_x_ja_writer_o_r1_r2_01.py` `SYMBOL_PREVENTION_BLOCK_JA`(約83-93行)、`er003_v1_n3_01_articles_generate.py` 約181行(Layer 1 Promptのコロン禁止文)
- CURRENT_SPEC.md「TTS記号正規化(全Family共通)」節(Grepで該当節のみ、約1605-1665行)

## Opus L2所見(ユーザー承認済みの修正対象。既存仕様の実装穴として処理、新仕様は作らない)
- **SF-1(a)**: JA Layer 1 Prompt(`SYMBOL_PREVENTION_BLOCK_JA` 等、Family X JA Writer。Family A側のJA Promptに同種ブロックがあれば同様に)へ「時刻は『午前11時4分』のように日本語で書く(11:04 のような記号表記を使わない)」を明記。**SF-1(b)(er007 ASR側にH:MM等価判定を追加する)は採用しない。**
- **SF-2**: `_TIME_HMM_COLON_RE` を全角コロン「：」・全角数字にも対応(`(?<![0-9０-９])[0-9０-９]{1,2}([:：])[0-9０-９]{2}(?![0-9０-９])`)、Gate内判定を `in (":", "：")` へ。Normalizer除外条件(`_JA_COLON_SEMICOLON_RE` の数字隣接除外)とGate除外条件の定義一致を確認。fixture/testに全角ケース追加。
- **SF-3**: H:MM除外したコロンをSTOPせず **observe finding として記録**(新カテゴリ例 `TIME_COLON_ALLOWED_OBSERVE`、`_SYMBOL_STOP_CATEGORIES` には入れない)。同時に `build_symbol_violation_prompt_note()` が **stop対象カテゴリのみ**をWriterへ伝えるようフィルタ(既存の %$¥ observe も含めて誤って「直せ」と伝えない)。既存呼び出し元(Layer 2: er003_v1_n3_01_articles_generate / er019 / scaffold_generate、Layer 4: er003_v1_repro01_main_generate / er003_v1_n3_01_tts_generate)でobserve findingがSTOP判定に混入しないことを確認(`symbol_gate_requires_stop` の挙動を維持)。
- **N-3**: Layer 1 Prompt(EN/JA両方)の「コロンは使わない」を現行Normalizer/Gate仕様と整合(「文中のコロン・セミコロンは使わない。時刻は英語では `11:04 a.m.` 形のみ可/日本語では『午前11時4分』と書く」等、Promptの方が厳しい方向は維持しつつ揺れを解消)。
- N-4(iv): REPORT §12のSSOT追記案の「比率表記は自然に対象外」は実態(分2桁の比率 "1:20" は通る)より強い表現なので補正。
- N-1のSTOP理由文へ「数字に隣接するコロンで時刻表記でないものは人手確認が必要」を明示(小)。

## 作業
1. 上記を最小差分で実装。編集は他Agent(読み解決Phase 2: `er019_family_x_audio_production_runner_01.py`/`er025_*`/`er006_*` を編集中)と衝突しないファイルのみ。`er019_family_x_ja_writer_o_r1_r2_01.py` は今回対象だが、編集前に `git status`/`git diff --stat` で他Agentの未commit差分が無いことを確認し、差分があればPrompt変更はREPORTに案として記載しcommitしない(RESULT_PACKETに理由)。
2. test: `er003_test_audio_tts_asr_safety.py` に全角時刻・observe記録・prompt noteフィルタ・非時刻コロンSTOP維持の4件以上追加。全Family Layer 2/4呼び出し元のunit test(存在するもの)を実行。`er024_..._fixtures.py` は実API呼び出しのため**実行しない**。
3. SSOT: CURRENT_SPEC「TTS記号正規化」節へ最小追記(時刻表記H:MM(半角/全角)は数値表記として無変換・observe記録、JAはWriter段で日本語表記、Layer 1 Prompt整合、2026-09-27修正1・2回目、Opus L2所見反映)。DECISION_LOG に本修正のエントリ(ユーザー承認2026-09-27、SF-1(b)不採用を明記)。OPEN_ITEMS: 新規登録不要(既存OPEN-194に「時刻コロン修正1・2回目実施」を1行追記)。
4. REPORT §13「修正2回目」: Opus所見(BLOCKER 0/SF-1〜3/N-1〜4)との照合表(各項目: 対応/不採用/対象外+理由)、diff要約、test結果、SSOT反映箇所、残課題(Hormuz本文2再TTSは読み解決Phase 2 commit後の別委任)。
5. 直後に `python -c "import er003_audio_tts_asr_safety, er019_family_x_ja_writer_o_r1_r2_01"` でimport確認。

Git: 変更ファイルのみpath指定add(`git add -A`禁止、他Agentのstageを外さない、index.lockリトライ)。トレーラー `Management-ID: TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに commit hash・変更ファイル・test件数・Opus照合表の要約を記載。
