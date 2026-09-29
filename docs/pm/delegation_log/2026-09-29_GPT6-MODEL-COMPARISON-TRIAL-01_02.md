## 管理ID

GPT6-MODEL-COMPARISON-TRIAL-01(Phase B=`gpt-6-sol` 互換性 probe 1 call+`gpt-5.6-luna` vs `gpt-6-luna` の Checker 比較 Trial[段階実行]、委任 _02)。一時ファイル `docs/pm/ACTIVE_TASK_G6B.md` / `docs/pm/RESULT_PACKET_G6B.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`、HEAD `2ef442f8` 以降)。**SSOT 編集は DECISION_LOG のユーザー決定記録 1 エントリのみ**(下記 §SSOT)。他の SSOT・CURRENT_SPEC・REPORT_LEDGER は文案のみ。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキーは環境変数のみ、key 本文を表示・log・commit・報告に書かない**。**Production code・Prompt・Checker・Model Routing Contract・routing の変更禁止**(Trial harness は Contract 非経由の model 直接指定)。Opus 起動禁止。

## ユーザー決定(2026-09-29、逐語厳守)

- 主対象 **`gpt-6-luna`** vs 現行 baseline **`gpt-5.6-luna`** のみを比較。「変えるのは model のみ。Prompt / Developer message / input / JSON schema / Validator / post-processing / reasoning 設定 / fixture / 評価方法は完全固定」。
- **`gpt-6-astra` は Trial 対象外**(追加 probe 不要・fixture 実行不要・副対象に含めない。既実施の 1-call probe は Evidence として残す)。
- **`gpt-6-sol` は 1-call 互換性 probe のみ**(現行 Checker と同一条件: Responses API 正常応答/`reasoning="high"` 受理/`text.format.type="json_schema"`+`strict:true`/現行 Checker schema どおりの JSON/timeout・error なし)。**比較対象に自動追加しない**。位置づけ=Luna で品質不足だった場合の第二候補。
- **費用上限 ¥300(Phase B 全体、Guardrail 必須)**。段階実行: Step 1 重大 fixture 群を新旧 1 回ずつ → **GPT-6 Luna に重大見逃しがあれば STOP**/Step 2 境界・過剰品質 fixture 1 回ずつ/Step 3 非決定性評価 同一 fixture n=5 反復。「総費用が ¥300 に達する前に必ず停止」「不要な追加 fixture・追加モデル・追加反復は行わない」。
- 受入条件: Safety=重大 fixture BLOCKING 維持率 100%・新たな重大見逃し 0 件(満たさなければ不採用)/Over-blocking=不要 BLOCK 率が現行比改善、Hormuz B 群・Meta 境界例で過剰品質が減るか/Stability=n=5 一致率、現行より非決定性改善/QCD=call 単価・latency・token・retry/error 率。
- Gold label: 既存 A/B 分類を暫定 gold。「新旧で判定が大きく割れた/どちらが正しいか明確でない/Product 判断が必要」な fixture のみ USER_DECISION_REQUIRED として列挙。**Claude が独自に gold を書き換えない**。
- Sol の大量 Trial・Production routing 変更へ自動で進まない。Trial 終了 Status は `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED` のいずれか(Fable が最終分類。`VALIDATED` は Production 採用を意味しない)。
- OPEN-233 / OPEN-234 のコード変更は行わない。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_02.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_02.md --json-out docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_02.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: 上限 ¥300(段階別: Step 1 想定 ≈ ¥16〜20、Step 2 ≈ ¥16〜20、Step 3 ≈ ¥150〜180、各段は想定額の 2 倍超で STOP。GPT-6 単価は未確認のため、**実費は API usage の token 数と、判明している単価(現行)での参考換算を併記**し、GPT-6 分は token 数を一次記録とする。累計の参考換算が ¥300 に到達する前に停止)。

## 手順

### 0. 事前(¥0)
`git pull --ff-only`、`git stash list`、設計書 `docs/pm/design_gpt6_model_comparison_trial_01.md` §3〜§7 を Read(fixture 一覧・sha256・比較条件・指標定義)。fixture の sha256 を再検証(不一致なら STOP)。

### 1. `gpt-6-sol` 互換性 probe(1 call、上限 ¥2)
Phase A の probe スクリプト(scratchpad)と同一条件で 1 call。結果(SUCCESS/エラー本文[key なし]、schema 準拠、reasoning 受理、latency、token)を REPORT §Sol probe に記録。**比較対象に追加しない**。

### 2. Trial harness 実装(¥0、repo 内 `er050_gpt6_checker_comparison_trial_01.py`+`_test_01.py`)
- `vfl01.run_deviation_check()` の内部呼び出しと同一の client・Prompt・Developer message・schema・post-hoc validation を使い、**model 引数だけ差し替える**(vfl01 を import して利用、vfl01 本体は不変。model 指定が関数引数で不可能なら、同一 Prompt/schema 定数を import して同一形式の Responses API 呼び出しを harness 側で構成し、sha256 一致をテストで証明)。Contract 非経由。
- 入力: fixture 定義 json(設計書 §3 を機械可読化: id/群/Ledger パス/記事テキストパス/source_article_text の有無[JA 側は無し・EN 側は有り、現行運用と同一]/gold[A/B 区分・現行判定])。出力: `er050_output/gpt6_checker_comparison_trial_01/<step>/<fixture_id>/<model>/run_<k>.json`(prompt sha256・model・reasoning・usage・latency・raw/parsed・post-hoc 後の severity/category/origin)。集計 `summary_step<N>.json`。
- Guardrail: 累計 token/参考換算を各 call 後に更新し、Step 上限・累計 ¥300(参考換算)到達で停止。error 率 20% 超で停止。
- mock テスト: model 以外の固定性(Prompt/Developer/schema sha256 が Phase A 記録と一致)、Guardrail 停止、出力 schema、post-hoc 適用、fixture 数が設計書と一致(追加なし)。

### 3. Step 1 重大 fixture 群(ER-009-N1 9 種+A 群 5 件、新旧各 1 回)
両モデルで実行 → BLOCKING(MAJOR)維持率・見逃し(gold=重大なのに MAJOR にならない)を集計。**`gpt-6-luna` に重大見逃し 1 件でもあれば STOP**(Step 2 へ進まず報告)。A-1(時制 drift、現行も見逃した例)は「現行同様見逃し」と「新モデルで検出」を区別して記録(見逃しは STOP 条件に含めるが、現行も見逃している既知例は別掲し Fable 判断へ)。

### 4. Step 2 境界・過剰品質群(B 群 4 件+Meta Standard translation MAJOR 1 件、新旧各 1 回)
不要 BLOCK 率(gold=B 群で MAJOR となる率)、category・origin の一致性、Hormuz B-1/B-2・Meta 境界例の判定差を fixture ごとに表。判定が大きく割れた fixture は「USER_DECISION_REQUIRED 候補」として列挙(gold は書き換えない)。

### 5. Step 3 非決定性(同一 fixture n=5、新旧両モデル)
対象: 設計書 §3 非決定性群(Hormuz run_02/run_03 の JA・Advanced・Standard+Ledger、Advanced/Standard 判定割れケース)。各 fixture × モデルで 5 回実行し、完全一致率・多数決一致率・severity/category/origin のブレを集計。現行モデルも同時測定(相対比較)。費用が累計上限に近づく場合は fixture 数を減らさず**反復回数を報告の上で停止**(勝手に fixture を追加・削除しない)。

### 6. 集計・REPORT
`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` に §Phase B: Sol probe/実行条件(sha256 固定の証明)/Step 1〜3 の表/新旧比較サマリ(Safety・Over-blocking・Stability・QCD)/Cost(token 一次記録+参考換算、記事換算 4 call)/Latency(中央値・最大)/retry・error 率/リスク・未解決/USER_DECISION_REQUIRED 候補 fixture/**Trial 終了 Status の候補(REJECTED / VALIDATED / USER_DECISION_REQUIRED)と根拠**(最終分類は Fable)。設計書 §9 Phase B 追記。RESULT_PACKET へ SSOT 文案(Trial 結果・OPEN-233 への追記案、Routing 判断はユーザー)。

## SSOT(本タスクで編集するのは DECISION_LOG 1 エントリのみ)
「2026-09-29 ユーザー判断: GPT-6 Checker Trial 主対象 `gpt-6-luna` vs `gpt-5.6-luna`/`gpt-6-astra` は対象外(高コスト、Luna/Sol で不足時の上位候補)/`gpt-6-sol` は互換性 probe のみ(第二候補)/Phase B 費用上限 ¥300、段階実行 Step 1〜3/受入条件(Safety 100%・見逃し 0、Over-blocking 改善、Stability 改善、QCD)/gold は既存 A/B 暫定、割れた fixture のみ USER_DECISION_REQUIRED/Trial 終了 Status は REJECTED・VALIDATED・USER_DECISION_REQUIRED、VALIDATED は Production 採用を意味しない/順序: Luna Trial → Routing 判断 → 必要なら Sol → OPEN-233 → OPEN-234」。

## 事前指定Read一覧 / 事前指定Grep一覧
- 設計書 §3〜§8、`er003_v1_en_direct_vfl_01_generate.py`: Grep `def run_deviation_check|DEVIATION_PROMPT_TEMPLATE|DEVIATION_DEVELOPER|DEVIATION_JSON_SCHEMA|_apply_deviation_post_hoc_validation|client\.responses|reasoning|text_format`、Phase A REPORT(probe 手順)、`er009_ledger_deviation_recalibration_02_test.py`(fixture 9 種の入力形式)。
- 更新位置: `er050_*`(新規)、`er050_output/**`、REPORT、設計書、DECISION_LOG、delegation_log。

## 実行コマンド全文
- `git pull --ff-only origin main`
- Sol probe: `.venv\Scripts\python.exe <scratchpad>\gpt6_probe.py --model gpt-6-sol`
- テスト: `.venv\Scripts\python.exe -m unittest er050_gpt6_checker_comparison_trial_01_test_01 -v`
- Step 実行: `.venv\Scripts\python.exe er050_gpt6_checker_comparison_trial_01.py --step 1 --models gpt-5.6-luna,gpt-6-luna --budget-jpy 300`(同様に `--step 2`、`--step 3 --repeat 5`。`--step all` は実装しない)

## Git
- commit: (1) harness+テスト+delegation_log(Step 実行前)、(2) Step 1 結果、(3) Step 2 結果、(4) Step 3 結果+REPORT+設計書、(5) DECISION_LOG。メッセージ例 `GPT6-MODEL-COMPARISON-TRIAL-01 (Phase B Step 1): 重大fixture群 gpt-5.6-luna vs gpt-6-luna 各1回(BLOCKING維持率・見逃し集計)`、trailer `Management-ID: GPT6-MODEL-COMPARISON-TRIAL-01`。path 指定 add、push。

## 報告(RESULT_PACKET_G6B + handback、目安50行)
【gpt-6-sol 互換性 probe 結果】【Trial 実行条件】(sha256 固定の証明)【重大 fixture 結果】(表、見逃し有無、STOP 有無)【境界 / 過剰品質 fixture 結果】【非決定性結果】【新旧モデル比較】【Cost / Latency】(token 一次記録+参考換算、累計、Guardrail 遵守)【リスク / 未解決問題】【Trial 終了 Status 候補と根拠】【USER_DECISION_REQUIRED 候補 fixture】/commit hash・raw URL。
