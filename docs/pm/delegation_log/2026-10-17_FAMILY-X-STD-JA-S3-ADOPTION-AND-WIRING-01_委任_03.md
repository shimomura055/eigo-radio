# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_03(Phase B: S3をFamily X Standard日本語Preview/Comment1〜4の正式Styleとして**Production配線**+test+正式経路runtime evidence+SSOT+commit/push)。本日=2026-10-17(JST)。前委任=委任_02(commit `3b254fdf1`)。ユーザー正式承認=2026-10-17「S3をFamily X全体のStandard日本語解説の正式Styleとして採用」(Status `APPROVED_FOR_PRODUCTION`、原文は下記T-0で保存)。

## 性質/到達上限Status/禁止事項
- 性質: Production実装(Style profileの既定値変更)+Regression+正式Production経路での実走証拠(有料: Std TTS一部+ASR)。
- 到達上限Status: `S3_WIRED_EVIDENCE_RECORDED_PENDING_FABLE`(PRODUCTION_WIRED判定はFable。Sonnetは宣言しない)。
- 費用上限(T-3): 上限JPY40(Guardrail)。見積は実行前に算出し、JPY100超見込みなら実行せず報告(7-7)。期待: Std側の新規TTSはSUPPORT_JA 5 clip(約JPY1.6+ASR0.5)。Full Story/KP/IOL等は**Master Audio Storeのsha一致で再利用され新規生成0**となる想定(T-2追記の差分再生成確認で実証。想定外の全再生成が判明したらAPI実行前にSTOP)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。本日使用済み約JPY44。
- 禁止: S3文面の調整・別Style/記事本文・Advanced・Key Phrase仕様・Full Story・IOL・効果音の変更/既存の音量仕様の統一・変更(Preview無加工・Comment目標RMSはそのまま)/R2版成果物(`coffee_prices__run_fxpw_01`配下・`user_test/coffee_fxpw_e2e_01/`)の上書き/Master Audio StoreのR2 key音声の削除・上書き/**新しいfallback仕様の設計・採用**(必要と判明したらSTOP)/Family A互換ファイル(`er006_audio_cost_pilot_02_shared_narration.py`・`er006_master_audio_store_01.py`)の変更(guard `FamilyAUnchangedTest`維持)/Family Z・Y・A・B・C/RLCT関連/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd(特に `coffee_prices__run_fxpw_01/a2/audit/key_phrase_source_gate.json`)。
- STOP条件(ユーザー§9): 新しい未承認仕様の採用が必要/重大な品質不一致/正式経路でS3を適用できない/必須HR・品質Gate到達/費用Gate超過/既存成果物への意図しない破壊的変更(検知したら即停止・報告)/承認内容とruntime動作の不一致。
- 並行タスク: なし(commitは本委任のみ)。
- Opus Gate(11-3): Fable判定=条件A非該当(既存Style profile機構の既定値変更で新構造なし)、条件Cはユーザー採用判断済みのため非該当。ただし**注意点③で「S3適用失敗時に未承認Styleへ無警告で切り替わる経路」の是正にロジック変更が必要な場合は、実装前にSTOPしてFableへ報告**(Fableが任意Opusレビュー/ユーザー判断を判定)。既存パターン(非ブロッキングM3 warning、例 `KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2`)と同型の「警告追加のみ」は既存承認範囲内として実装可。
- 時間見込み: 実装・test 60分/runtime evidence 30分/Assembly・ページ 30分/SSOT・commit 30分 ≒ 2.5時間。単独。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。
T-0補足(厳守): (a)本委任文は**全文**(全節・全見出し・path省略なし)を `docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_委任_03.md` へ保存(直近2委任で要約保存→FAILが再発。要約禁止)。(b)下記「ユーザー指示(原文)」節を**一字一句そのまま** `docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_PHASE-B_USER.md` へ保存し文字数・sha256を記録。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
# Claude Code／Fableへの正式指示
## Family X Standard日本語解説 S3 — Production Wiring

**管理ID：FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01（Phase B）**

### 1. ユーザー正式承認

ユーザーは、S3「親しみのあるニュースナレーター」を**Family X全体のStandard日本語解説の正式Styleとして採用することを承認した**。

- 対象：Standard Preview／Comment1〜4
- 旧正式Style：R2
- 新正式Style：S3
- Trial：`VALIDATED`
- 現在Status：`APPROVED_FOR_PRODUCTION`
- 今回の到達目標：`PRODUCTION_WIRED`

**追加のStyle選定・採用判断は不要。Production反映を進めること。**

### 2. 採用するStyle

`coffee_ja_style_trial_04`のS3を逐語で使用する。

共通指示込みのStyle全文（199字、SHA `060c08fd…`）を、既存Trial成果の正式記録と照合すること。

名称から推測して再構成したり、独自に調整したりしない。

基準資料：

`er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md`

Coffee Phase Aの実走証拠・差し替え成果も参照する。

### 3. Production配線

Family Xの既定Style profileを更新し、Standard日本語Preview／Comment1〜4の正式StyleをR2からS3へ変更する。

最低限、以下の全経路を確認する。

- Production正式初回生成経路
- retry
- fallback
- regeneration
- Local Rewrite等の関連経路
- 既定profileの自動適用
- Style解決失敗時の動作

**特別なCLI指定をしなくても、正式Production経路でS3が使用されること。**

DEV／Trial専用scriptへの実装だけで完了扱いにしない。

### 4. Phase Aで判明した注意点

OPEN-405に記録された次の3点を確認する。

**① 既存成果物への副作用**

正式Gate関数により、R2版のJSONパス表記が一時的に書き換わった。

Phase Bでは、既存成果物やMaster Audio Storeを意図せず改変しないことを確認する。

必要な修正は今回のS3配線に直接関係する範囲に限定する。

**② Previewの音量処理**

正式CoffeeではPreviewは無加工、Commentは既存RMS目標を使用している。

S3配線によって、Previewの音量処理が意図せず変わらないこと。

既存の音量仕様を勝手に統一・変更しない。

**③ 未承認Styleへの無警告fallback**

Style適用失敗時、未承認Styleが無警告で使われる既存経路があるとの報告。

今回の正式採用により、その経路がS3の適用保証を破らないか確認する。

未承認Styleへの無警告切替を、S3が正常適用されたものとしてPASS扱いしないこと。

必要な修正が既存の承認済み仕様の範囲で安全に行える場合は対応する。

**新しいfallbackの仕様選択が必要な場合は、ユーザー判断事項としてSTOPすること。**

### 5. Production runtime evidence

正式Production経路でS3が実際に発火したことを確認する。

証拠として以下を残す。

- Production entrypoint
- 適用されたStyle ID／version
- 実際に送信されたStyle全文のSHA
- actual model_id／Voice
- Preview／Comment1〜4の対象セクション
- TTS実行結果
- AUW／ASR等の品質結果
- 既定profileからS3が選択された証拠

必要な有料TTS実行については既存費用Gateを適用する。

Phase Aの試聴版が良好だったことだけで、正式Production配線のruntime証拠の代用としない。

### 6. テスト・整合性確認

必要なRegression／Validator／integration testを実行する。

特に次を確認する。

- Family X Standardの対象5セクションにS3が適用される
- Advanced側に影響しない
- Key Phrase仕様が変わらない
- Full Story／In One Line／効果音等が変わらない
- retry／fallback／regenerationでも承認仕様が維持される
- 既存R2成果物が変更されない
- Master Audio Storeに不正な上書きがない
- Dangling Referenceが存在しない

テスト未実施の経路を「動作確認済み」と報告しない。

### 7. SSOT・Decision管理

正式採用と実装状況を以下へ反映する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS（#105・OPEN-405等、関係項目）
- 必要なStyle profile記録
- runtime evidence
- テスト結果
- Git commit／push／merge

承認済みS3とProduction実装のStyle全文が一致していることを確認する。

### 8. 費用・作業範囲

**既存費用ルールを遵守すること。**

- 実行前に費用見積と当日累計を確認
- ¥100を超える新規実行は、既存承認範囲を確認
- 日次¥1,000のsoft budgetを維持
- 不要な音声再生成を避ける
- commitを伴う作業は同時に1件のみ

今回の対象外：

- 記事本文の修正
- S3の追加調整・別Style探索
- Advanced／Key Phraseの仕様変更
- Family Z／Yへの展開
- Family A／B／Cの開発
- Research／LedgerのコストTrial
- Detective演出の変更
- 無関係なOpen Itemの改修

### 9. STOP条件

次の場合のみSTOPして報告する。

- 新しい未承認仕様の採用が必要
- 重大な品質不一致
- 正式Production経路でS3を適用できない
- 必須Human Review／品質Gateに到達
- 費用Gateを超過する
- 既存成果物への意図しない破壊的変更
- 承認内容とruntime動作が一致しない

非Blocking事項を理由に、不必要な追加Trialや仕様開発を開始しないこと。

### 10. 最終報告・Closeout

Fableは実装報告を独立レビューし、以下を照合する。

1. Production正式初回経路でS3が適用されたか
2. retry／fallback／regenerationとの整合
3. actual model_id・Style SHA等のruntime evidence
4. 必要なテストのPASS
5. R2版成果物・Master Audio Storeの保全
6. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSの更新
7. commit／push／mergeの確認
8. 承認されたS3と実際のProduction挙動の一致
9. 未解決のBlocking事項・承認済み未配線事項の有無

**すべて満たした場合のみ `PRODUCTION_WIRED` と判定する。**

未確認項目がある場合は、実装済みであっても`APPROVED_FOR_PRODUCTION`のまま追跡する。

最終報告は、技術詳細の羅列ではなく、**「正式反映できたか・証拠は何か・残課題は何か」**を最初に簡潔に示すこと。

今回の承認事項をProductionへ確実に反映し、未配線のまま放置しないこと。

(ユーザー原文ここまで)

## KPI provenance欄(24節)
- 正式経路runtime evidence(profile選択・Style sha・model・AUW/ASR・費用): `production_formal_path`(fresh)。Store再利用segment: `reuse`(sha一致)。S3 Style: `frozen`(sha `060c08fd…`)。E2E自己確認: Yes(正式audio runner、既定profile、CLI個別指定なし)。

## Opus台帳更新
該当なし(新規Opusレビューなし)。

## 事前指定Read一覧
1. `er019_family_x_style_profile_01.py` 全文(構造: `PROFILE_FX_20261016`、`DEFAULT_NEW_RUN_PROFILE`、roles定数、`_verify_constants()`、resume時の旧profile警告)。FXPW 委任_02Aの実装パターン(`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/WIRING_DESIGN_01.md` §J)を Grep `fx_20261016|DEFAULT_NEW_RUN_PROFILE|旧profile` で該当範囲のみ参照。
2. `er019_family_x_audio_production_runner_01.py`: Grep `SUPPORT_JA|support_ja|generate_a2_japanese_with_reading_safety|minimal|MINIMAL|fallback|STD_FALLBACK|style_profile_gate|M3|M4|_m3_|_m4_|record_human_approval|keywords_path|verify_episode_audio_validation_gate|local_rewrite|regenerat|resume` → SUPPORT_JA生成経路・retry・fallback(minimal instruction)・regeneration/resume・M3/M4判定・Gate関数(`keywords_path`書換箇所)の該当範囲Read。
3. Master Audio Storeのkey: `er006_master_audio_store_01.py` Grep `def .*key|style_instruction_id|version|sha` と runner側のSUPPORT_JA Store呼出(Grep `master_store|store.get|store.put|reuse`)→ **SUPPORT_JAのStore keyにStyle sha/versionが含まれ、R2音声がS3として再利用されない**ことを確認(含まれなければSTOP: Store key設計はFXPWでK2のみ対応した可能性。R2音声の誤再利用はユーザー指示違反)。
4. `er020_tts_retry_local_rewrite_01.py`: Grep `style|SUPPORT_JA|role` → Local Rewrite経路がStyleをprofileから解決しているか。
5. 既存test: `er019_family_x_fx_20261016_wiring_01_test_01.py`、`er019_family_x_style_profile_01_test_01.py`、`er019_family_x_new_structure_wiring_01_test_01.py`(Grep `625826c1|SUPPORT_JA|fx_20261016` → 期待値更新箇所)。
6. S3正本: `er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md` L53-63(S3全文・sha `060c08fde003cf7c2d15c654da96d3f857b8e7a9bd79eac31814ceaf7c923f33`、199字)。Phase A証拠: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3_support_01/style_evidence.json`・`gain_report.json`。
7. R2版正式run: `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/audit/style_profile.json`・`audit/e2e_segment_style_table.json`(SUPPORT_JA 5行)・`audit/gain_report*.json`(Preview無加工/Comment RMS)。
8. `CURRENT_SPEC.md`: Grep `SUPPORT_JA|R2|fx_20261016|Standard Preview|日本語Preview` → Family X承認仕様の記載箇所(更新位置)。全文読込禁止。
9. `OPEN_ITEMS.md`: Grep `OPEN-405|OPEN-404|OPEN-399|OPEN-401` → 更新位置。`docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#105|#103`。

## 事前指定Grep一覧+追記位置・更新位置の手順
A. 実装(Production、最小変更):
  - `er019_family_x_style_profile_01.py`: 新profile `PROFILE_FX_20261017="fx_20261017"` を追加(roles: FULL_STORY/PREVIEW/KP_EXPLANATION_EN/KP_EN/KP_JA_MEANINGは`fx_20261016`と同一sha、**SUPPORT_JA=S3全文(199字、sha `060c08fd…`)**)。`DEFAULT_NEW_RUN_PROFILE`を`fx_20261017`へ。`fx_20261016`は既存runのresume用に保持(旧profileでresume時の`[WARN][STYLE-PROFILE]`は既存どおり)。`_verify_constants()`にS3 sha/字数を追加。S3定数名は`SUPPORT_JA_STYLE_S3_20261017`等、文字列は`PROMPTS_01.md`から逐語コピー(改行・句読点を変えない。assertで sha一致)。
  - SUPPORT_JAのMaster Store key(Read 3の結果): Style sha/versionがkeyに含まれていれば変更不要。含まれていなければ**実装せずSTOP報告**。
  - 注意点③: SUPPORT_JAでStyle適用失敗→minimal instruction fallbackが発火する経路を特定し、(i)発火時にM3/M4で警告(非ブロッキング)が出るか、(ii)`style_profile_gate.json`/segment tableで`instruction_path`等の記録により「S3非適用」が判別できるか、を確認。無警告なら、既存K2パターン(`KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2`)と同型の**警告追加+記録のみ**を実装(fallback挙動自体は変えない)。fallback挙動の変更が必要と判断したら実装せずSTOP。
  - 注意点①: `verify_episode_audio_validation_gate`が`key_phrase_source_gate.json`の`keywords_path`を絶対パスへ書き換える副作用を確認。**S3配線と直接関係しないため今回は修正しない**(Phase Aで復元済み)。ただし本委任の実走で既存R2 run配下を一切書き換えないよう、新runは別run dirで実行(下記B)。実走前後でR2 run配下の全ファイルsha(またはmtime)一覧を取り不変を検証(`audit/r2_run_integrity_before/after.json`)。Master Store `manifest.json`のR2 key entryが不変であることも検証。
  - 注意点②: 音量処理コードは変更しない。新runの`gain_report`でPreview無加工・Comment目標RMS方式がR2 runと同一方式であることを記録(値は新音声から再計算されるため数値差は許容、方式一致を確認)。
  - test更新: 期待sha更新(SUPPORT_JA→`060c08fd…`、profile_id→`fx_20261017`)、`fx_20261016`のresume互換test維持、Adv/KP/FS/IOL不変のassert、`FamilyAUnchangedTest`維持。新規test: 既定profileがCLI指定なしで`fx_20261017`を選ぶ/旧profile runのresumeで警告/③の警告(実装した場合)。
B. 正式経路runtime evidence(有料、小額):
  - 新audio run dir(例 `--run run_fxpw_01_s3prod`、text成果はCoffee `er019_output/coffee_prices/run_fxpw_01`を入力。runnerが`--run`で別出力dirを作れるか確認し、不可なら text runをコピーした新dir `er019_output/coffee_prices/run_fxpw_01_s3prod` を作る。**R2 audio run dirには書かない**)。
  - `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01_s3prod --level a2 --stage plan`(CLIでStyle/backend指定なし)→ `audit/style_profile.json` の `profile_id==fx_20261017`、`style_profile_source==default_new_run_fx_20261017`、SUPPORT_JA sha `060c08fd…` を確認(不一致=STOP)。
  - `--stage scaffold --level a2 --budget-jpy 40`(KP選定はStoreに無いため再実行される可能性あり≈JPY2.4。KP結果がR2 runと異なっても仕様上問題ないが記録)→ `--stage tts --level a2 --budget-jpy 40`(SUPPORT_JA 5 clipのみ新規生成、Full Story/KP/IOL/固定shellはStore sha一致で再利用=新規0を`reuse_telemetry`で確認。**再利用が効かず全再生成になる見込みならAPI前にSTOP**)→ `--stage assemble --level a2` → `--stage player --level a2`。Advanced(b1b)は実行しない(S3非対象。ページではR2 run のAdvへリンク)。
  - evidence: `audit/e2e_segment_style_table`相当(SUPPORT_JA 5行: style_instruction_id/version/sha=S3/instruction_path=primary/AUW判定)、`tts_generation_results.json`、`cost.json`、`reuse_telemetry`、AUW/ASR結果、`style_profile_gate.json`。
  - ページ: `user_test/coffee_fxpw_e2e_01_s3prod/index.html`(「Coffee Standard 正式版(S3配線後の正式Production経路で生成)」と明記、Std通し+各section、Advはリンク)。R2版ページ・Phase Aページは不変。Pages実再生確認(HTTP 200・console error 0)は commit後。
C. Regression: `.venv\Scripts\python.exe run_project_regression.py --pattern "er019_family_x_*_test_*.py"`、`--pattern "er081_*_test_*.py"`、`--pattern "er020_*_test_*.py"`、`--pattern "er006_*_test_*.py"`(FamilyA guard)。既知FAIL(OPEN-400等)と新規FAILを区別。Dangling Reference: Grep `625826c1|R2_SUPPORT|SUPPORT_JA_STYLE_R2`(命名に合わせる)で、S3切替後にR2定数を参照する箇所がresume互換以外に残っていないこと。
D. SSOT(編集権あり):
  - `CURRENT_SPEC.md`: Family X承認仕様のSUPPORT_JA(R2)記載箇所(Read 8)の直後に「2026-10-17更新: Standard日本語Preview/Comment1〜4の正式Style=S3(sha `060c08fd…`、199字、共通指示込み。ユーザー正式採用2026-10-17、原文=…_PHASE-B_USER.md)。既定profile `fx_20261017`。R2は`fx_20261016`のresume互換のみ。Status=<Fable判定待ち: S3_WIRED_EVIDENCE_RECORDED_PENDING_FABLE>」(旧記載は削除せず注記)。
  - `DECISION_LOG.md`: 末尾に委任_03記録(承認原文sha、実装差分、test結果、runtime evidence要約、費用、Status)。
  - `OPEN_ITEMS.md`: OPEN-405を「Phase B実装済み・Fable判定待ち」+論点①②③の確認結果へ更新。③で警告追加した場合はその旨。①の副作用は改修せず継続(必要なら新OPEN-406として独立登録、区分C)。
  - `docs/pm/USER_DECISION_REGISTER_01.md`: #105=判断済み(承認2026-10-17)。
  - `docs/pm/REPORT_LEDGER.md` 行追加。`docs/pm/ACTIVE_TASK.md` ヘッダ更新(addなし)。

## 実行コマンド全文
- 事前: `git status --porcelain | head -40`、`git log --oneline -1`(HEAD=`3b254fdf1`)、`.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 --run-dir er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod`(rc=3なら中止)。
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_委任_03.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_委任_03.md_check.json`
- 実装後test: 上記C。
- 実走: 上記B(PowerShellは `$env:TTS_EXECUTION_MODE="STANDARD"` を先に設定)。実行前に `COST_ESTIMATE_01.md` を新run dirへ(Store再利用前提の内訳)。
- secret scan: `.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(hits=0)
- git: 明示add → commit → push → Pages確認 → evidence追加commit(直列)。

## SSOT追記文
上記D(実値で埋める)。

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: あり(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`PM_GOVERNANCE.md`は編集しない)。
- 明示add: `er019_family_x_style_profile_01.py`、変更したrunner/test(変更したもののみ)、新run dirの記録(json/md/jsonl、wav除外)、`user_test/coffee_fxpw_e2e_01_s3prod/`(index.html+mp3)、`docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_{PHASE-B_USER.md,委任_03.md,委任_03.md_check.json}`、SSOT 3件、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`。R2 run配下・`key_phrase_source_gate.json`・Master Store manifest(変更があれば原因を報告しaddしない)・`RESULT_PACKET_*`・`ACTIVE_TASK.md`はaddしない。
- commit message: 「FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_03: Phase B S3 Production配線(既定profile fx_20261017=SUPPORT_JA S3 sha 060c08fd、他role不変、fx_20261016はresume互換)+test更新+正式経路runtime evidence(Coffee Std a2、Store再利用、S3発火)+SSOT(Fable PRODUCTION_WIRED判定待ち)」
- push: `work/post-merge-01`でcommit → `C:\Users\tensh\eigo-radio-crbn`で `git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main` → 主dirで `git merge --ff-only origin/main`。conflictは停止して報告。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_S3W3.md`(25行程度): T-0 2行/実装差分(file:line、S3定数sha assert結果、DEFAULT切替、③の確認結果と実装有無、Store key確認結果)/test結果(PASS/FAIL、新規test、既知FAIL区別、Dangling Grep結果)/runtime evidence(entrypoint・profile選択証拠・SUPPORT_JA 5行のStyle ID/version/sha/instruction_path/model_id/voice/AUW・ASR、Store再利用件数と新規生成件数、gain方式一致、style_profile_gate)/R2 run・Master Store保全検証結果/費用(見積・実測・本日累計)/公開URL・Pages確認/SSOT位置/commit hash・push・raw URL/4行(①既存仕様整合 ②Production到達経路の未承認機能既定値 ③最終成果物・目的適合 ④撤去・残置[R2定数の扱い])/`判定整合:`行/判断候補(なし想定。③でfallback仕様選択が必要ならD区分で提示)/使用モデル(25節)。

## Fable自己チェック(送信前)
- [x] Read一覧に行範囲/Grepパターンあり [x] 追記位置手順あり [x] コマンドに引数実値あり [x] 禁止事項・費用上限(JPY40、7-7判定)あり [x] 並行衝突回避(commit単独)あり [x] Opus Gate判定(A/C非該当、③ロジック変更時STOP)あり [x] 時間見込みあり [x] 継続委任(前委任QDC: Phase A公開完了・JPY2.1・次=Phase B配線)
