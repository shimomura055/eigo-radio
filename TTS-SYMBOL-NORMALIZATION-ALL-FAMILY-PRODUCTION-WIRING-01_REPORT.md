# TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01 Phase 2: 実装+配線+runtime evidence

Status起点: `APPROVED_FOR_PRODUCTION`(ユーザー承認済み)。本REPORTは実装・配線・
runtime evidenceを報告するものであり、**`PRODUCTION_WIRED`の最終判定はFableが行う**
(Sonnetは自己判定しない)。Phase 1 recon: `docs/pm/recon_tts_symbol_normalization_01.md`
(Fable修正2026-09-27annotationを本Phaseで追記済み)。

---

## 0. Fableの9項目設計修正(適用結果の要約)

Phase 1 recon案からの主な変更点(詳細は各節、recon doc「Fable修正(2026-09-27)」節参照):

1. 〜/～は**全位置**で「なになに」に統一(Key Phrase gloss含む、非対称設計を撤回)
2. 範囲/数値placeholderは個別判断せず、Writer Prompt側で「〜/～を使わない」予防のみ
3. 英語%/$/¥はPrompt予防が主、Validatorは検出・ログのみ(生成は止めない)
4. 3層→4層(Prompt予防/Writer-output Validator[既存retryへ統合]/TTS直前Normalizer/TTS直前残存記号Gate)
5. `<short pause>`はASR観測Trial実施(2回、採用はしない)
6. 既存artifactの遡及書き換えなし
7. コロン/セミコロン: 実コーパス分類実施(英語本文=実使用あり→有効化、JA Key Phrase gloss=fixtureのみ)
8. 固有名称の記号は個別報告のみ(一般化しない)
9. Family Z dangling note記録、Family Bは英語のみ確認、Family Cの実Writerを特定して適用

---

## 1. 変更ファイル一覧・diff要約

```
docs/pm/recon_tts_symbol_normalization_01.md       |  74 ++++++++ (Fable修正annotation追記)
er003_audio_tts_asr_safety.py                      | 201 +++++++++++++++++++++ (新設セクションG)
er003_key_words_canonicalization.py                |  43 +++--  (convert_display_gloss_to_tts_textをsafety委譲へ)
er003_test_audio_tts_asr_safety.py                 | 169 +++++++++++++++++ (新規test 5クラス)
er003_test_key_words_canonicalization.py           |  49 +++--  (期待値更新: 全位置変換に追随)
er003_v1_n3_01_articles_generate.py                |  78 ++++++--  (Prompt追加+Family A retryループへLayer2/4統合)
er003_v1_n3_01_scaffold_generate.py                |  46 ++++-  (Key Phrase redundancy retryへLayer2統合)
er003_v1_n3_01_tts_generate.py                     |  55 +++++-  (tts_safe_ja/en拡張=Layer3 Normalizer本体)
er003_v1_repro01_main_generate.py                  |  15 ++   (Layer4 Gate、Key Phrase/crosslevel英語共有関数)
er003_v1_sing01_news_tail_fix.py                   |  12 ++   (Layer4 Gate、Family A/B/C共有news本文関数)
er003_v1_sing01_point_headings_aoede.py            |  12 ++   (Layer4 Gate、Point見出し関数)
er003_v1_sing01_voice01_generate.py                |  14 ++   (Layer4 Gate、英語Charon関数)
er011_output/.../fixtures/common_block_baseline_*.txt (3ファイル、Prompt追加を反映した既存baseline再生成)
er011_point_role_planning_focus_connection_trial_04.py       |  59 ++++--  (Gate4機械的再構成の追随、safety import追加)
er011_point_role_planning_focus_connection_trial_04_test_01.py |   6 +   (BARE_NAMESへ新関数名追加)
er013_family_c_future_writer_08.py                 |   9 +   (Family C A2実Writer、Prompt予防のみ)
er013_family_c_future_writer_08_b1.py              |   9 +   (Family C B1実Writer、Prompt予防のみ)
er019_family_x_audio_production_runner_01.py       | 147 ++++++++++-----  (OK segment再利用ヘルパー追加)
er019_family_x_b3_production_wiring_01_test_01.py  |   6 +-   (mock fixtureの括弧誤爆を修正)
er019_family_x_ja_writer_o_r1_r2_01.py             |  99 +++++++++-  (original/r2段にLayer2 must-fix retryを追加)

22 files changed, 1014 insertions(+), 119 deletions(-)
```

新規runtime evidenceスクリプト(er0XX命名規則に合わせて`er024_`を新規採番、
Trial中の他Agent配下`er022`[TTS Trial]/`er023`[Key Phrase Trial]とは独立):
`er024_tts_symbol_normalization_all_family_production_wiring_01_fixtures.py`、
`er024_tts_symbol_normalization_all_family_production_wiring_01_pause_tag_observation.py`、
出力先`er024_output/tts_symbol_normalization_all_family_production_wiring_01/`。

---

## 2. 3層(実質4層)ワイヤリング表(path × layer)

| Family/経路 | Layer 1 Prompt予防 | Layer 2 Writer-output Validator(既存retry統合) | Layer 3 TTS直前Normalizer | Layer 4 TTS直前残存記号Gate |
|---|---|---|---|---|
| Family A 本文Writer(`er003_v1_n3_01_articles_generate.py`) | `COMMON_BLOCK_TEMPLATE`に禁止記号6項目追加 | `run_one_pattern()`のPoint Overlap retryループ(既存`POINT_OVERLAP_ARTICLE_RETRY_MAX=2`)へ`detect_prohibited_symbols`(見出し行除外・英語本文scan)を統合、`symbol_flagged`をvalue_qa/lexicalと合成 | `tts_safe_en`/`tts_safe_ja`(下記) | 下記の各生成関数 |
| Family A Key Phrase(`er003_v1_n3_01_scaffold_generate.py`) | 選定Prompt側は既存規約のまま(変更なし、Fable修正#1でNormalizer側が全位置対応するため個別Prompt追加不要) | `run_key_phrases()`のKey Phrase Set Redundancy QA retry(既存`KEY_PHRASE_REDUNDANCY_RETRY_MAX`)へ`detect_key_phrase_symbol_findings`を統合 | `convert_display_gloss_to_tts_text`(→`normalize_tilde_placeholder_ja`委譲) | `generate_charon_japanese_with_reading_safety`(下記と共通) |
| Family X ja_writer(`er019_family_x_ja_writer_o_r1_r2_01.py`) | `SYMBOL_PREVENTION_BLOCK_JA`(verbatim監査対象のR0_PROMPT等とは別枠) | original/r2段に独立したmust-fix once retryを新設(既存`JAFactCheckStopError`パターンを踏襲、Fact Checkの有無に関わらず動作) | 同上(`tts_safe_ja`経由) | 同上 |
| Family C A2実Writer(`er013_family_c_future_writer_08.py`) | 禁止記号6項目のPromptブロック追加 | **未実装**(下記STOP項目参照) | `tts_safe_en`(Family B経由で共有) | Family B/C共有のTTS関数群 |
| Family C B1実Writer(`er013_family_c_future_writer_08_b1.py`) | 同上 | 同上(未実装) | 同上 | 同上 |
| Family B(Editorial Voices) | Family Bは日本語segmentが存在しない(英語のみ)ことを確認済み(Phase 1 recon 1.4節)。Family Aと同じ`tts_safe_en`/`generate_charon_english`等を`er012_b_family_voices_production_01.py`経由でimport | 専用Writerを持たないため対象外 | `tts_safe_en`(共有、Layer3) | `generate_charon_english`(共有、Layer4) |
| 共有TTS入口(`er003_v1_n3_01_tts_generate.py`) | - | - | `tts_safe_ja`: `normalize_tilde_placeholder_ja`+`normalize_ellipsis_pause_ja`+`normalize_colon_semicolon_pause_ja`。`tts_safe_en`: `normalize_ellipsis_pause_en`+`normalize_colon_semicolon_pause_en` | - |
| Layer 4 Gate配置先(全て`detect_prohibited_symbols`+`symbol_gate_requires_stop`) | - | - | - | `er003_v1_n3_01_tts_generate.py`(`generate_charon_japanese_with_reading_safety`/`generate_a2_japanese_with_reading_safety`)、`er003_v1_sing01_voice01_generate.py`(`generate_charon_english`)、`er003_v1_sing01_news_tail_fix.py`(`generate_news_narration_wide_margin`)、`er003_v1_sing01_point_headings_aoede.py`(`generate`)、`er003_v1_repro01_main_generate.py`(`generate_narration_snippet_verified_strict`、Key Phrase・crosslevel英語共有) |

**中核Normalizer新設関数**(`er003_audio_tts_asr_safety.py`セクションG):
`normalize_tilde_placeholder_ja`、`normalize_ellipsis_pause_ja`/`_en`、
`normalize_colon_semicolon_pause_ja`/`_en`、`detect_prohibited_symbols`、
`symbol_gate_requires_stop`、`build_symbol_violation_prompt_note`。

---

## 3. Fixture結果表(実TTS+実ASR、`TTS_EXECUTION_MODE=STANDARD`)

証跡: `er024_output/tts_symbol_normalization_all_family_production_wiring_01/fixture_results.json`

| ケース | 入力 | Normalizer後(TTS入力) | ASR結果 | status |
|---|---|---|---|---|
| ja_tilde_leading | ～を示す | なになにを示す | 何々を示す | OK |
| ja_tilde_mid | 地元の店を〜と結びつける | 地元の店をなになにと結びつける | 地元の店を何々と結びつける。 | OK |
| ja_tilde_range | 中〜高強度 | 中なになに高強度 | 中何々光強度 | OK |
| ja_ellipsis_mid | それは…違う | それは、違う | それは違う。 | OK |
| ja_ellipsis_end | それは違う… | それは違う。 | それは違う。 | OK |
| ja_colon | 理由は3つ:予算、人手、時間 | 理由は3つ。予算、人手、時間 | 理由は三つ。予算、人手、時間。 | OK |
| en_ellipsis_mid | Wait... that's wrong. | Wait, that's wrong. | Wait, that's wrong. | OK |
| en_colon | Three reasons: budget, staff, time. | Three reasons. budget, staff, time. | Three reasons: budget, staff, time. | OK |
| en_semicolon | Argentina advanced; England were sent home. | Argentina advanced. England were sent home. | Argentina advanced, England were sent home. | OK |

9/9 OK(実TTS音声化+実ASR照合のPASS)。tilde全位置(先頭/中間/範囲表記)で
「なになに」変換が正しく発話・認識されることを確認(範囲表記「中〜高強度」も
Fable修正#1どおり個別判断せず機械的に変換、意味の妥当性はWriter Prompt予防
[recon doc Fable修正§7-1]に委ねる設計であることをruntime evidenceとして記録)。

**`<short pause>`タグ観測Trial**(観測のみ、採用しない): 証跡
`er024_output/.../pause_tag_observation_results.json`。2ケースとも、タグは
文字通り読み上げられず、ASRはタグ位置に自然な文区切り(句点)を認識した
(例: 「それは正しいです。でも待ってください。」)。現行Production採用
モデル(gemini-3.1-flash-tts-preview)でのタグの正確な意味論(真のpause指示
として機能しているか、単に無視されているか)はこの小規模観測だけでは
断定できない。**結論は「句読点への決定論的置換」を引き続き正式採用**
(Fable決定#5どおり、Layer 3 Normalizerが既にこの方式)。

---

## 4. 回帰テスト結果

証跡: `er024_output/tts_symbol_normalization_all_family_production_wiring_01/regression_full.log`,
`regression_summary.json`(全変更適用後に実行、`run_project_regression.py`)。

```
collected=3291 passed=3283 failed=6 errors=2 skipped=0
```

**6 FAIL + 2 ERRORの内訳(全て既存/期待済み、本タスクによる機能的regressionではない)**:

| 種別 | テスト | 原因 |
|---|---|---|
| ERROR(無関係・既存) | `er003_test_p2j_investigate.PerFileCountsTests.test_per_file_counts_sum_matches_pattern_discovery` | 下記er015 import失敗の連鎖(このタスクとは無関係な既存Trialファイルの自己STOP) |
| ERROR(無関係・既存) | `er015_standard_a2_6000_generation_first_trial_01_test_01`(loader failure) | `er015_standard_a2_6000_generation_first_trial_01.py`がimport時に独自の`RuntimeError([STOP] Production STANDARD_A2_PROMPT_V5...)`を送出(本タスクで一切触れていない別Trialファイル、pre-existing) |
| FAIL(件数集計bookkeeping) | `test_combined_equals_sum_of_er002_and_er003`(3291≠1878) | 新規test追加(このタスク+他)でtotal件数が変化したことによる、履歴baseline数値の陳腐化(機能regressionではない) |
| FAIL(件数集計bookkeeping) | `test_p2h_reported_count_matches_er002_plus_er003_at_that_time`(1037≠1032) | 同上 |
| FAIL(件数集計bookkeeping) | `test_p2i_reported_count_matches_er003_at_p2i_era`(665≠660) | 同上 |
| FAIL(git diff guard、commit待ち) | `er019_family_x_pointless_01_test_01.test_family_a_files_have_no_working_tree_diff` | `er003_v1_n3_01_scaffold_generate.py`に未commitの差分があるため(本タスクの正常な変更、commit後に解消見込み) |
| FAIL(git diff guard、commit待ち) | `er020_tts_cooldown_local_rewrite_trial_01_test_01.test_production_modules_have_no_uncommitted_diff_caused_by_this_trial` | 同上パターン(Production module未commit) |
| FAIL(git diff guard、commit待ち) | `er020_tts_local_rewrite_natural_english_qa_trial_02_test_01.test_production_modules_have_no_uncommitted_diff_caused_by_this_trial` | 同上 |

git diff guard 3件は本REPORT公開後のcommitで解消見込み(commit後に本ファイル
自体は再実行確認していない、次回regressionで自然解消)。件数集計bookkeeping
3件は、履歴baseline定数の更新が必要(このタスクの範囲外の別管理、Fableへ報告)。

---

## 5. Runtime evidence(Meta run再実行、実データ)

対象: `er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01/`
(既存`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01`のStage 3a runtime evidence用
out_dirを再利用。**重要**: この記事[Meta「Muse human concierge」]自体は
`OPEN-183`により記事内容[Storyline/Fact選定/本文]のユーザー確認が
`USER_DECISION_REQUIRED`のまま維持されている。ただし`OPEN-183`本体に
「配線[audio production wiring]が進んでもStage 3runtime evidence実行中
という扱いは変更しない、Blockingは記事内容の公開判断[音声化"以降"の
後工程]に限る」旨が明記されており、本タスクの再実行は既存Stage 3活動の
延長(Symbol Normalization配線の正しさをこの既存test caseで検証する行為)
であり、記事の公開・採用を進めるものではない。)

| segment | 修正前(既存記録) | 修正後(本タスク再実行) |
|---|---|---|
| `b1b/kp1_japanese`(Key Phrase gloss「〜」) | STOPPED(未変換のplaceholder記号残存) | **OK**(なになに変換→実TTS+実ASR PASS、実API呼び出し1回のみ、既存OK segmentは再課金なし) |
| `a2/japanese_title`(「…」) | STOPPED(placeholder gate) | placeholder gate自体は解消(「…」はNormalizerで句読点化されるため)。ただし**別の既存Gate**(`ER-009-JA-FOREIGN-TOKEN-GATE-01`)が"Muse"という未登録外来語トークンをHUMAN_REVIEWとして新たに検出し、STOPPEDのまま(詳細は§6 STOP項目) |

**Assembly**: B1Bは`key_phrase_source_gate`のarticle_text未解決(下記STOP項目、
データのみのfix適用)を解消後、Assembly完走(`Family_X_Audio_B1_...wav`生成、
`player.html`生成)。A2はjapanese_titleがSTOPPEDのままのため
`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で正しくブロック(Audio Validation Gate
は無変更のまま正常動作、Gate回避は一切行っていない)。

**machine-verification(Point Notification/ポイント解説の不在)**:
`b1b/audit/timeline.json`(41 segments)を機械的に列挙した結果、
`Notification 1/2/3`(正当な区切りSE)は存在するが、`point_explanation`/
`ポイント解説`に相当するsegmentは1件も存在しないことを確認(Family Xの
既存仕様どおり)。

---

## 6. 費用(実測、`raw_usage_log.jsonl`を`pricing_snapshot.json`で換算)

| 項目 | 内訳 | JPY |
|---|---|---|
| Fixture 9件+pause-tag観測2件(tracked) | 11ペア(TTS+ASR)、一部Cascade fallback呼び出し含む | ¥5.02 |
| pause-tag観測の意図せぬ3回目呼び出し(下記STOP項目参照) | 結果取得スクリプトのbugにより`pause_tag_mid_2`と同一テキストを別pathで再送信(untracked、同等呼び出しからの推定) | 約¥0.46 |
| Meta run再実行の限界費用 | `kp1_japanese`のみ新規TTS+ASR(他は既存OK再利用、再課金なし) | ¥0.45 |
| **合計** | | **約¥5.93** |

¥200報告閾値・¥250上限のいずれも大幅に下回る。

---

## 7. Gate 3チェックリスト(PM_GOVERNANCE.md準拠、Fable最終判定用の自己申告)

| 項目 | 状況 |
|---|---|
| Production正式初回経路 | Family A/X/B/Cいずれも既存Production関数(`tts_safe_ja`/`tts_safe_en`/各generate_*)を直接拡張、新規並行経路は作らず |
| retry・fallback・regenerationとの整合 | 既存retry予算([Point Overlap article retry max2]/[JA Fact Check must-fix once]/[Key Phrase Redundancy retry])を再利用、新規Lock/上限は追加していない |
| DEV・Trial-onlyではないこと | 全変更はProduction関数自体への直接編集(Trialアダプタ経由ではない) |
| Production runtimeでの実発火 | §5 Meta run再実行(実API)で実際にLayer3/4が発火し、既存STOPが解消したことを確認 |
| 必要testのPASS | §4回帰3283/3291 PASS(残り8件は無関係/bookkeeping/commit待ちのみ、機能regressionなし) |
| runtime evidence | §3(fixture 9件+pause-tag2件、実TTS+実ASR)、§5(Meta run実データ) |
| 実際のmodel_id・routing確認 | fixture/pause-tag結果内に`model_id`記録済み(`gemini-3.1-flash-tts-preview`[JA]/`gemini-2.5-pro-preview-tts`[EN]、既存Production採用モデルと一致) |
| コスト影響評価 | §6(合計約¥5.93、¥250上限内) |
| CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md反映 | **本Phaseでは未実施**(委任文の指示どおりSSOT編集はFableに委ねる。§8にdraft entryのみ提示) |
| 必要なGit反映 | 本REPORT提出後にpath指定commit+push実施予定(§9) |
| approved specとProduction挙動の一致 | §3/§5のruntime evidenceがFable設計修正9項目と一致することを確認済み |

**Gate 4(Dangling Reference Check)**: 新設関数(`detect_prohibited_symbols`等)は
全て`er003_audio_tts_asr_safety.py`という既存の共有安全モジュールに実装し、
未承認・未実装のTrial専用仕様への参照は作っていない。Family C Layer 2
(Writer-output Validator)は意図的に未実装であり、これは「未実装のまま
放置されているdangling reference」ではなく、実Writer[er013_family_c_
future_writer_08*.py]がFamily A/Xのような既存retryループを持たないため
(§8 STOP項目3参照)。

---

## 8. SSOT draft entries(Fableへの提案、本Phaseでは未反映)

**CURRENT_SPEC.md draft追記案**(「TTS記号正規化」節、新設):

> TTS記号正規化(全Family共通、TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-
> PRODUCTION-WIRING-01、2026-09-27 PRODUCTION_WIRED[Fable判定待ち]):
> 波ダッシュ「〜」「～」は位置に関わらず全て「なになに」へ機械的に変換する
> (Key Phrase glossを含む、OPEN-117の「先頭・読点直後のみ」変換ルールを
> 撤回・全位置ルールへ統合)。「…」「……」は文末相当なら句点、それ以外は
> 読点へ変換する。コロン「:」「：」・セミコロン「;」「；」は句点へ変換する
> (数字直前直後は対象外)。英語%/$/¥はWriter Prompt予防のみ、Validatorは
> 検出・ログのみで生成を止めない。上記4種はTTS直前の使い捨てNormalizer
> (`er003_audio_tts_asr_safety.py`)で決定論的に処理し、canonical text自体は
> 変更しない。加えて、括弧/スラッシュ/URL・email/絵文字/未変換の残存記号は
> TTS直前の決定論的Gate(`symbol_gate_requires_stop`)で検出しSTOPする。
> Family Cの実Writerは`er013_family_c_future_writer_08.py`(A2)/`_08_b1.py`
> (B1)であり、Prompt予防のみ適用済み(Writer-output Validatorは未実装、
> 理由は下記OPEN-XXX参照)。Family Bは日本語segmentが存在しないため対象外。
> Family Z構築時は同じPrompt予防+Normalizer+Gateの適用が必要(未着手)。

**DECISION_LOG.md draft追記案**:

> 2026-09-27 TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01
> Phase 2実装完了。Fableが9項目の設計修正(Phase 1 recon案の一部撤回、
> 特にKey Phrase glossの非対称設計撤回)を行い、Sonnetがそれに従い実装。
> OPEN-117(2026-09-06 PRODUCTION_WIRED、先頭・読点直後のみ変換)は本タスク
> により**全位置変換ルールへ統合・置き換え**(Key Phrase gloss側の既存
> 「〜/～は許容」という緩和が撤回された点に注意)。実装詳細・runtime
> evidence・費用は`TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01_
> REPORT.md`参照。

**OPEN_ITEMS.md draft追記案**(新規Open Item、番号はFableが採番):

> [新規] Family C(`er013_family_c_future_writer_08.py`/`_08_b1.py`)には
> Family A/Xのような既存Writer-output retryループが存在しないため、
> Symbol Normalizationの Layer 2(Writer出力に対するValidator+retry)を
> 未実装のままとした(Prompt予防[Layer1]+Normalizer[Layer3]+Gate[Layer4]
> のみ)。Family Cで将来Fact Check/QA retryループが新設された際に、同じ
> `detect_prohibited_symbols`をそこへ統合することを推奨する。
>
> [新規] Family X `a2/japanese_title`(Meta「Muse human concierge」記事)で、
> Symbol Normalization適用後に**別の既存Gate**(`ER-009-JA-FOREIGN-TOKEN-
> GATE-01`)が"Muse"という未登録外来語をHUMAN_REVIEWとして検出し、
> STOPPEDのままであることを新規発見した(本タスクのGateではなく、本タスク
> の修正が正しく機能した結果、その先にあった別Gateが可視化されたもの)。
> "Muse"を読み方辞書へ追加するか、Human Reviewで個別確認するかは編集判断
> であり、本タスクの範囲外(記号正規化ではなく固有名詞判定の問題)。
>
> [新規] `KEY_PHRASE_SOURCE_GATE_ARTICLE_TEXT_UNAVAILABLE`(b1b Assembly
> blocker、本タスクで発見): audio production out_dirに`article.md`が
> コピーされていなかったため、既存Gateのfallback解決が失敗していた。
> 既存の`article.md`(無変更)をout_dirへ配置するデータのみの回避で解消
> したが、runner側で自動コピーする改善は本タスクの範囲外として未実装
> (別途検討推奨)。

---

## 9. STOP項目(判断不能・範囲外として報告するのみ)

1. **Family C Layer 2(Writer-output Validator)は未実装**: Family A(Point
   Overlap article retry)・Family X(JA Fact Check must-fix)・Key Phrase
   (Redundancy QA retry)のような既存retryループがFamily Cの実Writer
   (`er013_family_c_future_writer_08.py`/`_08_b1.py`)には存在しない
   (Fact QA自体は別関数`er013_family_c_future_qa*.py`群にあるが、記号
   検知を統合するには新規retry配線の設計判断が必要になり、「既存retry
   ループへの統合」という委任の前提を満たせないため、本タスクでは
   Prompt予防のみに留めた。新規Loop創設はSTOP対象[既存安全機構の独自
   拡張は行わない])。
2. **`a2/japanese_title`の"Muse"HUMAN_REVIEW新規発見**: §5・§8参照。
   固有名称の記号は個別報告のみ(一般化しない)という委任の指示どおり、
   一般ルール化はしていない。
3. **`KEY_PHRASE_SOURCE_GATE_ARTICLE_TEXT_UNAVAILABLE`**: §8参照。データ
   配置のみで解消、runner改修は範囲外として未実施。
4. **pause-tag観測で意図せぬ3回目API呼び出しが発生**(§6参照): 結果
   抽出スクリプトのbugにより、`pause_tag_mid_2`と同一内容を別out_pathで
   再送信してしまった(実害は約¥0.46の追加費用のみ)。「2回だけ」という
   指示に対し実際には3回相当のTTS+ASR呼び出しとなったことを正直に報告する。
5. **コロン/セミコロンのFamily A運用リスク**: 実コーパス分類の結果、
   英語本文側で実使用が確認されたため有効化したが、これによりFamily A
   のPoint Overlap article retryループの発火頻度が増える可能性がある
   (既存のretry上限[2回]は変更していないため、安全機構としての後退は
   ないが、運用上の再生成コスト増加リスクとして記録する)。

---

## 10. Dangling Reference Check(Phase 1 recon §10を継承)

新設した`detect_prohibited_symbols`/`symbol_gate_requires_stop`/
`build_symbol_violation_prompt_note`は、全て承認済み・実装済みの既存
モジュール(`er003_audio_tts_asr_safety.py`)内に配置し、未承認Trial仕様
への参照は作っていない。Family C Layer2の意図的な未実装は上記STOP項目1
のとおりdangling referenceではない(Family C側は元々そのretryループを
持たない)。

---

## 証跡パス一覧

- `docs/pm/recon_tts_symbol_normalization_01.md`(Fable修正annotation込み)
- `er024_output/tts_symbol_normalization_all_family_production_wiring_01/`
  (fixture_results.json, pause_tag_observation_results.json,
  raw_usage_log.jsonl, regression_full.log, regression_summary.json,
  narration/[wav除きjson]、audit/review_lock_state.json)
- `er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01/`
  (b1b/player.html, b1b/audit/timeline.json, a2/audit/tts_generation_results.json 他)

---

## 11. Fable評価・最終Status(2026-09-27)

**判定**: `PRODUCTION_WIRED`(適用範囲: Family A本文Writer/Key Phrase/Family X
`ja_writer`/Family B・C共有TTS層[Layer 1・3・4])。**例外**: Family C
Layer 2(Writer出力Validator)は既存retryループ不在のため未実装のまま
(新規OPEN-191で追跡、Family Cで将来Fact Check/QAループが新設された際に
統合を推奨)。Meta A2 `japanese_title`の"Muse"HUMAN_REVIEWは、本配線の
未達ではなく既存`ER-009-JA-FOREIGN-TOKEN-GATE-01`の正常動作(§5・§8・
OPEN-183備考7参照)。

**回帰確定(Phase 3、commit`19e638b5`後の単独再実行)**:
`er024_output/tts_symbol_normalization_all_family_production_wiring_01/
regression_post_commit.log`。

| 種別 | §4(commit前) | Phase 3(commit後、単独再実行) |
|---|---|---|
| collected/passed/failed/errors | 3291/3283/6/2 | 3291/3286/3/2 |
| git diff guard 3件(er019_family_a_files_have_no_working_tree_diff等) | FAIL | **解消(PASS)** — commit後の再実行で予測どおり消滅を確認 |
| 件数集計bookkeeping 3件(test_combined_equals_sum_of_er002_and_er003等) | FAIL | FAIL継続。2026-09-04(`er011_output/23_full_regression.log`)・2026-09-11(`er011_output/25_full_regression.log`)の既存logで同一3件が同一原因(baseline定数陳腐化)で既にFAILしていたことを確認、**pre-existing**と確定(修正せず、新規OPEN-192へ記録) |
| er015 loader ERROR / er003_test_p2j PerFileCounts ERROR | ERROR | ERROR継続。本タスクの変更(commit`19e638b5`の変更ファイル一覧)に該当2ファイルは含まれておらず、無関係な既存Trialファイル自身の自己guard(意図的RuntimeError・import連鎖)によるものと確認、**pre-existing/無関係** |

機能的regression(上記4分類以外のFAIL/ERROR)は0件。

**pause-tag観測の意図せぬ3回目呼び出し**(§9-4): 約¥0.46の追加費用を軽微
(minor)として記録。今後同様の抽出スクリプトbugが再発しないよう、観測系
Trialスクリプトのout_path重複チェックを推奨するが、Productionコードには
影響しないため追加対応なし。

**en_colon fixtureの観測**: 英語コロンfixture(例: "Three reasons. budget"
のように文中コロンが句点化される変換結果)は、ASR一致・意味理解に問題なし
(fixture_results.json実測)。将来的に文中コロンを句点ではなく読点へ変換する
方が自然な場合があるかは、実際のFamily A本文でのコロン使用パターンが
蓄積してから再検討する観測事項として記録する(新規Production変更は今回
実施しない)。

**SSOT反映**: `CURRENT_SPEC.md`「TTS記号正規化(全Family共通)」節新設
(OPEN-117関連の旧記述は上書きせず「拡張前の記述」として残置)、
`DECISION_LOG.md`本管理IDエントリ追加、`OPEN_ITEMS.md`(OPEN-117・
OPEN-118へ拡張済み追記、OPEN-183備考7、新規OPEN-191〜194)、
`docs/pm/REPORT_LEDGER.md`本管理ID行追加。
