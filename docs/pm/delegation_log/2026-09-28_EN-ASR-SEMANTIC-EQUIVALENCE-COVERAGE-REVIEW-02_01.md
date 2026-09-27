管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(ユーザー指示 2026-09-28。**Phase 1=原因分析+coverage再監査+設計案まで。¥0、API呼び出しなし、Production code変更なし、SSOT編集なし**(記載案のみ)。設計後にMandatory Opus L2をFableが発火)。一時ファイル `docs/pm/ACTIVE_TASK_ASR2.md` / `docs/pm/RESULT_PACKET_ASR2.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_01.md` に保存しcommitに含める。

## 背景(ユーザー指示逐語要旨)
既に EN-ASR-SEMANTIC-EQUIVALENCE(REVIEW-01 22項目レビュー→Phase A+B Production配線、Phase C未着手、OPEN-184/186)で包括対策を設計・Trial・配線済み。にもかかわらず canonical "Act One" vs ASR "Act 1" が等価扱いされず、TTS品質問題ではないのにValidator NG→retry→cool-down→Local Rewrite(本文改変 "The first act")→合格、が現行モデル・Flash-Lite双方で再現した。以前の目的は「個別ケースを見つけるたびに追加修正」ではなく「ASR表記ゆれを包括的に吸収し、同種の誤判定を量産時に繰り返さない」こと。**Act Oneの個別fixture追加だけでcloseしてはならない。**

## 先出しRead
`EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`(22項目、Fable批判レビュー)、Phase A/B配線REPORT(`EN-ASR-SEMANTIC-EQUIVALENCE-*PRODUCTION*_REPORT.md` をGlob)、OPEN-184/186、`er021_en_asr_semantic_equivalence_production_01.py`(`_TOKEN_RE`、`_preprocess_raw`、`tier1_numeric_equivalence`、`_try_spoken_time`、role gate)、`er006_preprod_hardening_01_validation.py`(`_convert_cardinal_words`、`protected_check`、`classify_asr_match`、数値/否定検出)、`er003_v1_n3_01_tts_generate.py`(`_EN_NUMBER_WORDS`、`tts_safe_number_words_en`、`tts_safe_news_en`)、`er003_audio_tts_asr_safety.py`(数値抽出)、`er020_tts_retry_local_rewrite_01`(Local Rewrite前後の判定)、`er006_secondary_asr_01`(cascade)、`er011_human_review_lock_01`、Flash-Lite Wiring REPORT Phase 3節+Opus L2所見(論点3: `_TOKEN_RE` catch-allで "U.S." が4 atomに分裂しatom数不一致→Tier 1がfail-closed、"one" は代名詞衝突のため単独変換しない設計、baselineでも attempt1 "Act 1" NG/attempt2 "Act one" OK)、evidence `er019_output/.../hormuz__run_03_baseline/b1b/narration/attempts/full_story_part1_attempt*.json`、`hormuz__run_04_parallel_a/b1b/audit/tts_generation_results.json`、`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`(全NG記録、read-only)。

## E-1 原因分析(「fixtureに無かった」で終わらせない)
なぜ現行Productionで救済されなかったかを、仕様漏れ / 実装漏れ / Trial corpus・fixture不足 / coverage設計そのものの不足 のどれか(複数可)に**証拠付きで**帰着。Phase A/B/Cのどこに本来属すべきだったか。過去レビュー(REVIEW-01)で数字語↔数字表記を扱っていたのに、この文脈(番号ラベル+"one"+atom数不一致の複合)が抜けた理由(例: Tier 1のatom完全一致要件、`_TOKEN_RE` の略語分裂、"one" 除外設計、role gate、corpusに番号ラベルが無かった等)を分解。既存telemetryの全NG記録をオフライン再分類し、同系統(表記差のみ)の発生率・カテゴリ分布を母数付きで出す(read-only)。

## E-2 coverage matrix(カテゴリ×文脈)
cardinal / ordinal / Act・Part・Chapter・Section・Phase・Version等の番号ラベル / year / date / time / decimal / thousand・million・billion / currency / percent / fraction / Roman numeral / 番号付き固有表現 / hyphenated numeric / No.・number / alphanumeric / capitalization / whitespace・tokenization / apostrophe・possessive / punctuation・quotes・dash / abbreviation・acronym / ASRが数字化しても意味差でないケース / 数字正規化が意味差を隠すnegative case。各セルに: canonical例 / ASR例 / 現行判定(実コード追跡で確定) / 期待判定 / 根拠(既存fixture・telemetry実例・未検証)。既知例whitelistではなく体系表。

## E-3 設計原則・設計案
表記文字列の個別置換ではなく、canonicalとASRを**安全な共通意味表現へparseして比較**する方向を優先(例: 数値ラベル "Act One"→(label=act, n=1)、略語 "U.S."→単一atom、序数 "13th"→(13, ordinal))。false accept防止最優先: 数量差・否定差・単位差・通貨差・million/billion差・概数vs正確値・日時の意味差・固有名詞の別物化は吸収しない(negative test設計)。案は「既存Tier 1の前処理拡張(atom数不一致の解消)」「意味parse層の追加」等を、false reject耐性 / false acceptリスク / 変更範囲 / 全経路一貫性 / コスト(E-6: 決定論的正規化>既存Validator内等価判定>既存telemetry活用>追加ASR/LLM。継続コスト増は採用しない)で比較し推奨案を示す。

## E-4 全経路確認
同じ等価判定が initial / retry / fallback / regeneration / Local Rewrite前 / Local Rewrite後 / Secondary ASR / Human Review Lock直前 で一貫して使われるかを呼び出しチェーン表で確認。「表記差だけで retry→cooldown→Local Rewrite→Human Review へ落ちる構造」が残る箇所を特定。

## 分類(Existing Spec Check)
提案を (A)既承認範囲内の明白な実装漏れ修正(例: 略語atom分裂の前処理、既存Tier 1の対象role・atom整合)/ (B)新しい意味等価ルール・false accept境界拡張・継続コスト増・外部call・retry回数増(=**USER_DECISION_REQUIRED**、採用しない)に分ける。(B)には追加コスト/記事・月間想定・latency・発火率の見積を付ける。

## 成果物
`docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`(E-1〜E-4、matrix、設計案比較、分類A/B、positive/negative test設計、Opus L2申し送り: 単発か構造的か / 他の同系統の抜け / 包括対策と呼べるか / 量産false reject耐性 / false accept / retry・fallback・Local Rewrite整合 / Phase A+Bとの重複・矛盾 / Dangling Reference)、REPORT `EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md` 新設(Phase 1要約、SSOT記載案、Status候補)。

## ユーザー向け表記ルール(A-1、REPORT/設計書内でも遵守)
学習レベルは Standard / Advanced と表記(A2/B1/B1Bは内部ID・artifact名のみ)。TTS実行方式は 同期実行 / バッチ実行 と表記(内部名STANDARD/BATCHは括弧内のコード名としてのみ)。

Git: 設計書・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er030_*, er003_v1_*, er006_preprod_*, er025_*, SSOT]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02`。push origin main。RESULT_PACKETにroot cause要約・matrix規模・推奨案・分類A/B一覧・コスト影響を記載。
