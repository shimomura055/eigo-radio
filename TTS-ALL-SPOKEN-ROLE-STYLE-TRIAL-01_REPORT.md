# TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md

性質: Trial(Production実装なし)。委任元: Fable(sandwich-pm)。実行: Sonnet。
日時: 2026-09-28。委任文: `docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_01.md`
(check結果: FAIL、コマンド行2件の書式記法のみ、内容不備なし)。
設計書: `docs/pm/design_tts_all_spoken_role_style_trial_01.md`。

## 1. Existing Spec / Prior Trial確認結果

- 既存6-role(`er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN`)は
  TOPIC_INTRO/PREVIEW/COMMENT/FULL_STORY/HEADING_READOUT/IN_ONE_LINEの6つのみ、
  Family X(Flash-Lite)専用。
- 既知Gap(`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_REPORT.md:725`、
  Opus L2所見): shell segment(welcome/preview_intro/key_phrases_intro/
  full_story_intro/num_one〜five/point_explanation)がrole styleを一切持たない
  仕様未充足状態であることを確認済み。本Trialの主対象。
- **Advanced Key Phrase既存仕様の確認(二重実装回避)**: コード実測の結果、
  現行Productionでは Standard(A2)・Advanced(B1B)いずれも Key Phrase音声は
  「英語Key Phrase+日本語意味」の同一構成であり、**Advanced固有の英語解説
  トラックは存在しない**(`er019_family_x_audio_production_runner_01.
  _generate_key_phrase_segments_b1/_a2`が同じ`japanese_gloss_tts`を両者へ
  渡すのみ、KP canonicalized schemaにも英語解説フィールドなし)。過去Trial
  `KEY-PHRASE-LEVEL-SPEC-TRIAL-01`(Standard=JA解説/Advanced=EN解説という
  LLM Prompt方式)は**REJECTED**(Prompt v1、狙いのPhrase再現率25%、未配線)。
  よって「Advanced=英語Key Phrase+英語解説」という既存Production仕様・
  既存テキストartifactは存在せず、二重実装ではない。本Trialは
  `KEY_PHRASE_EXPLANATION_EN`というRoleを定義のみ行い、既存テキストartifact
  が無いため実音声は生成しない(新規Key Phrase解説テキストの創作はscope外、
  design doc §1-3)。
- 過去Trial重複確認: OPEN-201に「role別styleはStage3の6-role最小案を初期
  仕様採用」とあるのみで、全spoken要素への拡張Trialは過去実施記録なし。

## 2. 実施Pattern(Role表・style表)

Role漏れ0棚卸し(design doc §2、baseline実データ`tts_generation_results.json`
のsegment集合との1:1突合を`test_role_coverage_no_gap_b1b/a2`で機械検証・
PASS): PROGRAM_SECTION_INTRO(welcome/preview_intro)/KEY_PHRASE_INTRO/
FULL_STORY_INTRO/NUMBER_LABEL(num_one〜five、+A2のpoint_explanation[JA])/
TOPIC_INTRO/TITLE(A2 japanese_title)/PREVIEW/COMMENT/FULL_STORY/HEADING/
IN_ONE_LINE/KEY_PHRASE_EN/KEY_PHRASE_JA/KEY_PHRASE_EXPLANATION_EN(定義のみ)。

Trial Role style表(逐語、design doc §3、既存6-roleの値は無変更のまま流用):

| Role | EN style | JA style(該当segmentのみ) |
|---|---|---|
| TOPIC_INTRO | "brief, clear, engaging news topic introduction"(既存無変更) | – |
| PREVIEW | "calm, conversational"(既存無変更) | "落ち着いた、自然な話し言葉で" |
| COMMENT | "calm, conversational"(既存無変更) | "落ち着いた、自然な話し言葉で" |
| FULL_STORY | "calm, steady news narration"(既存無変更) | – |
| HEADING | "brief and clear"(既存HEADING_READOUTと同値) | – |
| IN_ONE_LINE | "concise, clear"(既存無変更) | – |
| PROGRAM_SECTION_INTRO | "warm, brief, welcoming" | – |
| KEY_PHRASE_INTRO | "brief, clear, inviting" | – |
| FULL_STORY_INTRO | "brief, clear, transitional" | – |
| NUMBER_LABEL | "brief, clear, neutral" | "簡潔に、はっきりと" |
| TITLE | – | "はっきりと、聞き取りやすく" |
| KEY_PHRASE_EN | "clear, precise, unhurried" | – |
| KEY_PHRASE_JA | – | "はっきりと、落ち着いて" |
| KEY_PHRASE_EXPLANATION_EN | "clear, precise, explanatory"(定義のみ、未使用) | – |

実装方式(design doc §4): EN側は既存`style_prefix_override`パラメータが
最下層まで正しく機能するため既存Production関数を無変更のまま呼ぶ。JA側は
実測の結果、`p9a.generate_narration_snippet`の`language=="ja"`分岐が
`style_prefix_override`を一切参照しないdead parameterであること
(`er003_b1_p9a_audio.py:227-229`)、`voice01.generate_charon_japanese`は
そもそもこのパラメータ自体を持たないことを確認したため、最下層関数
(`resolve_tts_call_and_prompt`)を同一引数で直接呼ぶ専用関数
(`generate_ja_role_style`)を実装した。既存の発音/記号/placeholder安全処理・
ASR Cascade・fallback(既存`generate_charon_japanese_minimal_instruction`/
`_generate_a2_japanese_minimal_instruction`を無変更のまま再利用)・3回上限
契約は維持。

## 3. Baselineとの差

- Style: 既存6-roleは値無変更、shell/KP/TITLE等の新規14 Roleにのみ短い
  descriptorを追加。
- Standard(A2): `A2_SLOWER_PACE_INSTRUCTION`(自然言語の「わずかに遅く」)を
  一切連結せず、Trial Role style単独+既存6% time-stretch post-process
  (`generate_a2_segment_with_slowdown`内蔵、無変更)のみを適用
  (`test_generate_a2_main_segments_does_not_concatenate_slower_instruction`
  でmock検証PASS)。
- Advanced(B1B): slowdown対象外のまま無変更(Baselineと同じ)。
- 日本語shell/KP/PREVIEW/COMMENT/TITLEへ、英語と意味的に対応するRole style
  を新規付与(Baselineは既存共通JAPANESE_STYLE_PREFIXのまま)。

## 4. 成果物

- Trial script: `er038_tts_all_spoken_role_style_trial_01.py`
- 単体test: `er038_tts_all_spoken_role_style_trial_01_test_01.py`(13件、全PASS)
- 設計書: `docs/pm/design_tts_all_spoken_role_style_trial_01.md`
- out-dir: `er038_output/tts_all_spoken_role_style_trial_01/hormuz/{a2,b1b}/`
  (audit/tts_generation_results.json・run_summary_tts.json・
  run_summary_assemble.json・parts.json・article.md・key_phrases/。
  wavは非commit)
- 試聴ページ: `user_test/tts_all_role_style_trial_01/index.html`
  (GitHub Pages公開URL: 後述commit/push後に記載)

## 5. 定量結果

| Level | 主記事segment | Key Phrase(EN+JA) | 共有narration | Assembly |
|---|---|---|---|---|
| Advanced(B1B) | 12/12 OK | 10/10 OK | **7/9 OK**(num_two/num_three: HUMAN_REVIEW_LOCKED) | **BLOCKED**(既存Gate) |
| Standard(A2) | 13/13 OK | 10/10 OK | 10/10 OK | **OK**(331.19秒) |

Standard duration比較: Trial 331.19秒 vs Baseline 331.78秒(修正前)/329.45秒
(修正後実測、`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_REPORT.md:505/931`)。
**slow instruction除去後もほぼ同一duration**(差0.6秒未満)であり、6%
post-processのみで既存と同等のペース差を維持できることを示唆する定量evidence。

コスト実測(Gemini TTS+OpenAI ASR、実API、b1b+a2合計): **¥23.41**
(gemini ¥19.17 + openai_asr ¥4.24)。Guardrail¥45以内。b1b単体¥9.57、
a2単体(差分)¥13.84(delegation想定例¥10.8/levelとほぼ整合)。

## 6. 品質評価

主観評価(声色・テンポ・Role差の自然さ・日本語style自然さ等)は
Sonnetが試聴できないため**ユーザー試聴待ち**(§3評価観点10項目表を
試聴ページに掲載、機械判定可能な4項目のみ記入済み)。機械判定分:
- Role漏れ0: PASS(test_role_coverage_no_gap_b1b/a2)。
- Standard slow instruction除去: PASS(styleへ"slightly slower"混入なし)。
- Key Phrase EN/JA ASR一致: 全20件(b1b 10+a2 10)`asr_verified=True`。
- instruction leakage: ASR実測textに演技指示文の混入なし(全件目視は
  ユーザー試聴待ち)。

## 7. Regression

- Role漏れ0テスト: PASS(2件)。
- Production style定数不変テスト: PASS(FAMILY_X_ROLE_STYLE_EN/FALLBACKの
  値がTrial実行前後で完全一致することを確認)。
- 全13 unit test PASS(`run_project_regression.py --pattern "er038*_test_*.py"`
  実行結果: collected=13 passed=13 failed=0 errors=0)。
- instruction leakage検出: 個別ASR実測textの目視確認で異常なし(全件は
  ユーザー試聴待ち)。
- **num_two/num_three(Advanced共有narration)がHuman Review Lockへ到達**
  (詳細§9)。これはRegressionというより既存Production安全装置の正常動作
  (Gate通過を許可しなかった)であり、独自判断で回避・無効化していない。

## 8. コスト実測

合計¥23.41(実API、Gemini TTS + OpenAI ASR)。Guardrail¥45以内(§5参照)。
delegationの「--budget-jpy 22」はper-level想定だったが、両levelで同一
`--out-dir`を使ったため`raw_usage_log.jsonl`(cost log)が共有され、2回目
(a2)実行時の累積チェックが「23.41 > 22」で発火・RuntimeErrorで停止した
(**ただしTTS生成自体は完了済みの状態で停止**、budget guardは"after tts"の
事後チェックのため実害なし)。これは本Trial scriptの実装上の粒度問題
(level別に出力先を分けなかったこと)であり、異常なAPI消費やretry
暴走ではない(内訳: gemini ¥19.17 / openai_asr ¥4.24、想定範囲内)。
総額¥23.41はユーザー指定の総合Guardrail¥45を十分に下回っている。

## 9. 新しく判明した問題

1. **Advanced Key Phrase音声に既存の英語解説トラックが存在しない**
   (§1既述)。ユーザーが想定していた「Advanced=EN句+EN解説」という
   Production仕様は現状存在せず、現行Advanced KP音声はStandardと同じ
   「EN句+JA意味」構成である。`KEY_PHRASE_EXPLANATION_EN`実装には新規KP
   解説テキスト生成(LLM Prompt設計含む)が必要で、過去Trial
   (KEY-PHRASE-LEVEL-SPEC-TRIAL-01)はREJECTED実績がある。
2. **極短context-free単語("Two."/"Three.")のFlash-Lite品質限界が、
   Production既存fallback style("natural, clear, conversational")とは
   異なるTrial style("brief, clear, neutral")でも再現した**(B1Bのみ、
   3回試行後Human Review Lock到達)。ASR実測(`review_lock_state.json`):
   num_two 3attempt全て`asr_text`が英語にならず(`'Tu'`→`'二'`→`'二'`、
   classification=TRUE_CONTENT_MISMATCH)、num_threeも同様(3attempt
   全て`'三'`)。Production既報告(OPEN-201、ASR='Ту'キリル文字)と同型の、
   CJK文字への言語ドリフトという非決定的挙動。同一テキストはA2側では
   attempt1で成功しており、style文言そのものの問題ではなく、より一般的な
   Flash-Liteの短文脈限界の可能性が高い。
3. Master Audio Store(`er006_master_audio_store_01.py`)はSTORE_DIR等を
   モジュールグローバル定数として保持し、パラメータ化されていないため、
   実行時モンキーパッチでのみ隔離可能(§12で詳細、Production側の設計
   改善候補として記録するに留め、本Trialでは変更していない)。
4. `er011_human_review_lock_01.ATTEMPT_HISTORY_PATH`
   (`er011_output/attempt_history.jsonl`)および英語/日本語Human Review
   Queue(`er006_output/audio_retry_cascade_prod_01/human_review_queue.
   jsonl`等)も同様にモジュールグローバルの共有固定pathであり、
   Master Audio Storeとは異なりTrialでは意図的に隔離していない
   (delegationがMaster Audio Storeのみを明示指定していたため)。本Trial
   実行により、これら共有append-only監査ログへTrialのentryが追記された
   可能性がある(Gate判定・Production音声出力そのものには影響しない
   append-only telemetryだが、他タスクの未commit差分と混在するため本
   タスクでは一切commitしない。透明性のため報告)。

## 10. Status案

**USER_DECISION_REQUIRED**(試聴待ちを主因とする)。補助的所見:
- Standard(A2): 定量的には良好(全件OK、duration Baseline同等、cost想定内)。
- Advanced(B1B): 定量的には概ね良好(29/31 spoken要素OK)だが、共有
  narration2件がHuman Review Lockに到達しフル episode 組立て不可
  (§9-2)。これは**REJECTED要因ではなく既存Production安全装置の正常動作**
  であり、Trial Role style自体の欠陥という証拠ではない(同一textがA2では
  成功)。
- 主観品質(声色・テンポ・Role差・JA styleの自然さ)は必ずユーザー試聴が
  必要。

## 11. ユーザー判断が必要な事項

1. Advanced(B1B) num_two/num_three をHuman Review Lock経由で明示的に
   REGENERATE_APPROVEDとし再試行するか(既存安全装置の正規手続きに従う、
   Sonnetは自動承認しない)。承認されれば追加コストは僅少(1segment
   あたりTTS 1〜数回+ASR、既存fallback含め既定3回上限)。
2. `KEY_PHRASE_EXPLANATION_EN`(Advanced英語解説)を将来実装するか。
   実装には新規Key Phrase解説テキスト生成方式の設計が必要(過去Trial
   REJECTED実績を踏まえた再設計)、本Trialのscope外。
3. 本Trialの試聴結果を踏まえ、Role style拡張(shell/KP/JA)をProduction
   採用するか(`APPROVED_FOR_PRODUCTION`はユーザーのみ判断可能)。
4. Standardのslow instruction除去+6% post-process単独方式を、6%の値も
   含め正式採用するか(duration面では既存同等という定量evidenceあり、
   聞き取りやすさの主観評価は試聴待ち)。

## 12. Production変更が一切入っていない証拠

- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er038`
  → **出力なし(空)**、逐語確認済み(2026-09-28実行)。
- Production Master Audio Store(`er006_output/master_audio_store_01/`)の
  manifest.jsonに、本Trialのstyle_instruction_id(`trial_role_style_*`等)
  ・Role名(`NUMBER_LABEL`/`PROGRAM_SECTION_INTRO`等)を含むentryが
  **0件**であることをgrepで確認(Trial専用Store
  `er038_output/tts_all_spoken_role_style_trial_01/hormuz/
  trial_master_audio_store/manifest.json`に10 entry、完全分離)。
- CURRENT_SPEC.mdは未編集(本タスクでの変更行数0)。
- `TTS_EXECUTION_MODE=STANDARD`を明示した同期実行のみ(バッチ実行なし)。
- 既存の安全装置(Human Review Lock、Audio Validation Gate、KEY-PHRASE-
  SOURCE-CONSISTENCY-GATE)は§9で述べたとおりいずれも独自判断で回避・
  無効化していない(num_two/num_three STOPPED→b1b assembly BLOCKEDのまま
  維持)。

## SSOT追記文案(編集権なし、Fable/ユーザーへの文案のみ)

**REPORT_LEDGER新行案**: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md` |
Trial | Status案: USER_DECISION_REQUIRED(試聴待ち) | 全spoken要素Role
棚卸し+Role style(EN/JA)Trial、Standard slow instruction除去比較。

**DECISION_LOG新規エントリ案**: 2026-09-28、
`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`。ユーザー指示によりFamily X
Flash-Lite既存6-roleを全spoken要素(shell narration・Key Phrase・JA含む)へ
拡張するTrialを実施。Role表・style表は
`docs/pm/design_tts_all_spoken_role_style_trial_01.md`。Standard(A2)は
全件OK・Baseline同等duration、Advanced(B1B)は共有narration2件が既存Human
Review Lockに到達しフル組立て不可(既存安全装置の正常動作、独自回避なし)。
Advanced Key Phrase英語解説の既存Production仕様・テキストartifactは
存在しないことを確認(過去Trial`KEY-PHRASE-LEVEL-SPEC-TRIAL-01`は
REJECTED、未配線)。Status: USER_DECISION_REQUIRED(試聴待ち)。Production
採用は未決、CURRENT_SPEC変更なし。

**OPEN_ITEMS候補案(新規発見のみ)**:
1. Advanced Key Phraseに英語解説トラックを追加するか(新規テキスト生成
   方式の設計が必要、過去Trial REJECTED実績あり)。
2. "Two."/"Three."等の極短context-free単語のFlash-Lite品質限界
   (style文言によらず非決定的に発生しうる、Human Review Lock到達実績
   2件目[OPEN-201に続く再現])。
3. `er006_master_audio_store_01.py`のSTORE_DIR等がパラメータ化されて
   おらず、Trial等での隔離にモンキーパッチが必要な設計上の制約
   (Production動作には影響しないが、将来同様のTrialを行う際の既知の
   注意点として記録)。

## STOP該当有無

なし(Human Review Lock到達はSTOPではなく、既存Gateの正常動作として
記録・報告した。予算はGuardrail以内、暴走的retry・想定外API消費は
観測されていない)。
