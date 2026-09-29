## 管理ID

GPT6-MODEL-COMPARISON-TRIAL-01(Phase A=Trial 計画確定のみ、委任 _01)。一時ファイル `docs/pm/ACTIVE_TASK_G6A.md` / `docs/pm/RESULT_PACKET_G6A.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`、HEAD `6993a764` 以降)。**SSOT 4 点(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)+REPORT_LEDGER は本タスクが編集権を持つ(直列化、記録内容は下記 §SSOT に限定)**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキーは環境変数のみ、key 本文を表示・log・commit・報告に書かない**。Production code・Prompt・Checker・routing Contract の変更禁止。**Phase B(大量実行)を開始しない**。Opus 起動禁止。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー許可済み(2026-09-29)「GPT-6 Trial 開始 OK、まず Phase A として Trial 計画確定のみ。勝手に大量実行しない」。到達上限 Status: `USER_DECISION_REQUIRED` または `READY_FOR_TRIAL_EXECUTION`(いずれでも Phase B はユーザー確認後)。
- **推測禁止(逐語)**: 「対象モデルの正式 model_id / endpoint / API 互換性 / input・output 単価 / reasoning・temperature 等の利用可能設定は、推測は禁止。公式情報または実 runtime で確認」。確認できない項目は「未確認」と明記し、ユーザー判断へ回す。
- 費用: **上限 ¥5**(model 一覧取得 `GET /v1/models` は無料、endpoint 互換性確認のための最小 probe(短い入力 1〜2 call、reasoning 設定の受理確認)のみ許可。fixture 実行は禁止)。probe の実行前に「対象・想定 call 数・想定費用」を記録、実費を `raw_usage_log` 相当に記録。
- ユーザー向け表記 Standard/Advanced。

## 固定ブロック

E-1/D-1/G-1/F-1 標準。T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_01.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_01.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: 上限 ¥5(probe のみ)。

## Phase A で確定すること(出力: `docs/pm/design_gpt6_model_comparison_trial_01.md` 新規)

### 1. 対象モデル(推測禁止)
- 現行 baseline: `gpt-5.6-luna`(`er006_model_routing_contract_01.py`、`docs/pm/gpt6_trial_preparation_01.md` §1 参照)。reasoning 設定の実測値(準備資料/`raw_usage_log.jsonl` から)。
- GPT-6 候補: `GET https://api.openai.com/v1/models`(環境変数の key で認証、出力に key を含めない)で **実在する model_id を列挙**し、`gpt-6` 系を抽出。候補が複数ある場合は全列挙し、選定はユーザー判断へ。存在しない場合は「API 上で確認できず」と記録し STOP(推測で書かない)。
- endpoint / API 互換性: 現行コードが使う endpoint(Responses API か Chat Completions か、`vfl01.run_deviation_check()` と共通 client の呼び出し形式を Grep で特定)に対し、候補 model で **最小 probe 1〜2 call**(短い固定文、JSON schema strict 指定・reasoning パラメータの受理可否)を実行し、成功/エラー本文(key を含まない)を記録。
- 単価: 公式価格ページを `curl` で取得できれば URL・取得日時・該当行を逐語記録。取得できない場合は「未確認(ユーザー提示待ち)」。**推測値・過去モデルの流用禁止**。
- 利用可能設定: probe の応答から reasoning effort / temperature / structured output の受理状況を記録。

### 2. 比較対象 Role
第 1 優先 = Ledger / Deviation Checker(`vfl01.run_deviation_check()`、JA Fact Check・EN Advanced・Standard で共通)。第 2 段以降(Writer/Researcher/Translation/Standard simplification/Comment/KP explanation)は候補として列挙のみ(本 Trial 管理ID の Phase B 範囲外、別 Phase として計画)。

### 3. Checker fixture の固定(存在確認・sha256・gold 判定を表に。コピー・実行はしない)
- 重大事故群: ER-009-N1 危険 fixture 9 種(`er009_ledger_deviation_recalibration_02_test.py`)、調査 REPORT A 群 5 件(A-1 時制 drift[検出漏れ例]、A-2 価格方向反転、A-3 actor 具体化、A-4 scope 取り違え、A-5 rollback 反転)。category 被覆表(actor/scope/number/negation/causality/time/comparison/fact/certainty/unsupported_new_claim)を作り、不足 category は「fixture 不足」と明記(新規作成はしない)。
- 過剰品質 / 境界群: B 群 4 件(B-1 生活ブリッジ文[4 事例]、B-2 Hormuz causality、B-3 接続詞 so、B-4 一般化 3 件)、changed_causality 事例、notes_for_writer 関連(Hormuz Ledger 12 件)、Meta run_03 Standard translation MAJOR(`er019_output/family_x_refresh_e2e_01/meta/run_03/a2/audit/deviation_checks/standard_attempt1.json`)。
- 非決定性群: 同一 input 反復用(Hormuz run_02/run_03 の JA・Advanced・Standard 各テキスト+Ledger)、Hormuz run_01〜03、「Advanced/Standard で判定が割れた同一 JA ケース」(Hormuz run_03: `b1b` COMPLIANT vs `a2` ja_source MAJOR)。
- 各 fixture: パス/sha256/入力(Ledger・記事・source_article_text の有無)/現行判定(severity・category・origin)/gold ラベル(現行判定をそのまま gold にせず「調査 REPORT の A/B 区分+ユーザー確認待ち」と明記)。

### 4. 比較条件
「同一 Prompt(`DEVIATION_PROMPT_TEMPLATE` sha256 固定)/同一 input/同一 Validator(`_apply_deviation_post_hoc_validation`)/同一 post-processing/同一 JSON schema」。変えるのは model_id のみ(reasoning 設定は候補 model が同名パラメータを受理する場合は同値、受理しない場合は「差分」として明記しユーザー判断)。実行 harness の設計(既存 `run_deviation_check()` を model 引数だけ差し替えて呼ぶ薄いスクリプト案、出力先 `er050_output/gpt6_model_comparison_trial_01/`、run 単位の audit json、反復 n 回のシード扱い)を記述(実装は Phase B)。

### 5. 評価指標(定義と算出式を明記)
Quality: 重大 fixture の BLOCKING(MAJOR)維持率/false negative/false positive/不要 BLOCK 率(B 群で MAJOR となる率)/origin 判定一致性/changed_causality 判定/notes_for_writer 依存(notes を Ledger テキストから除いた入力との差分=**除外は Trial 入力の加工であり Production 変更ではない**ことを明記、実施可否はユーザー判断)/同一 input 反復時の一致率(n 回中の多数決一致率と完全一致率)。Cost: 1 call 単価・fixture 全体・記事換算(4 call/記事)・現行差。Delivery: latency・retry 率・STOP 率・timeout/error 率。

### 6. 受入条件案(根拠付き、ユーザー未確定)
重大 fixture BLOCKING 維持率 100%(根拠: ER-009-N1 が 9/9 を維持要件としている)/新たな重大見逃し 0 件/不要 BLOCK 率 現行比改善(現行値=B 群 4/4 MAJOR、origin 付き 15 件中 (iii)+(iv)=10 件)/非決定性 現行より改善(現行は未実測のため、Trial で現行 n 回も同時に測り比較)/Cost 同等以下または品質改善に見合う/latency Production 許容範囲(現行中央値 33 秒、上限案の根拠を記述)。閾値を置く場合は根拠、置けない場合は「現行同時測定で相対比較」とする。

### 7. 想定費用 / Guardrail 案
fixture 数 × n(案: n=5)× 2 モデル × 単価(GPT-6 単価が未確認なら現行単価での下限のみ提示し「GPT-6 分は未確定」と明記)。Guardrail 案(段階発火: 重大群 → 境界群 → 非決定性群、各段の上限、累計上限、STOP 条件=error 率・予算・schema 非互換)。

### 8. リスク
API 非互換(structured output・reasoning パラメータ)、単価未確定、gold ラベルの再現性(調査は 1 回限りの目視分類)、fixture 数の少なさ(15 件)、現行モデルの再実行が過去判定と一致しない可能性(非決定性)、Contract への新 model 登録が必要になる箇所(Phase B で `require_model` fail-closed に触れる必要があるか=Trial harness は Contract を経由せず直接 model 指定で回避可能か)。

## SSOT(本タスクで反映、最小限)
- DECISION_LOG: 新エントリ「2026-09-29 ユーザー判断: OPEN-234 は GPT-6 Trial 後に対応(deferred / non-blocking、コード変更なし)/`GPT6-MODEL-COMPARISON-TRIAL-01` 開始許可(まず Phase A、Phase B はユーザー確認後)/順序: GPT-6 Checker Trial → Routing 判断 → GPT-6 採用方針確定 → OPEN-233 再評価 → 必要なら Checker 根本再設計」。
- OPEN_ITEMS: OPEN-234 に「GPT-6 Trial 後に対応(ユーザー決定 2026-09-29)」追記。OPEN-233 に Trial 管理ID のポインタ。
- CURRENT_SPEC: 変更なし(Trial 中のため)。REPORT_LEDGER: `GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` を Phase A として登録(REPORT 本体は Phase A の要約=設計書へのポインタと model 確認結果のみ作成)。
- 「Family X: PRODUCTION_WIRED/Hormuz: deferred/OPEN-233: deferred/OPEN-234: deferred(GPT-6 後)/GPT6-MODEL-COMPARISON-TRIAL-01: 開始許可・Phase A」が SSOT と矛盾しないことを Grep で確認し結果を記録。

## 事前指定Read一覧 / 事前指定Grep一覧
- `docs/pm/gpt6_trial_preparation_01.md`(全文)、`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md` §3〜§5、`er003_v1_en_direct_vfl_01_generate.py`: Grep `def run_deviation_check|client\.|responses|chat\.completions|reasoning|text_format|json_schema|_apply_deviation_post_hoc_validation`、`er006_model_routing_contract_01.py`(全文、短い)、`OPEN_ITEMS.md` Grep `OPEN-233|OPEN-234`、`DECISION_LOG.md` 先頭ヘッダーチェーン。
- 更新位置: 設計書(新規)、REPORT(新規)、SSOT 2 点+REPORT_LEDGER、delegation_log。

## 実行コマンド全文
- `git pull --ff-only origin main`
- model 一覧: `curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`(PowerShell では `$env:OPENAI_API_KEY`。**出力に key が混入しないよう `id` のみ抽出して記録**)
- probe: `.venv\Scripts\python.exe <scratchpad>\gpt6_probe.py`(自作、repo 外、model_id を引数、短い固定入力、usage を記録)
- 価格: `curl -s <公式価格ページ URL>`(取得できた場合のみ)

## Git
- add 対象(path 指定のみ): 設計書、REPORT、SSOT 2 点+REPORT_LEDGER、delegation_log+`_check.json`。commit 2 つ(設計書・REPORT・delegation_log/SSOT)。メッセージ `GPT6-MODEL-COMPARISON-TRIAL-01: Phase A(対象model実確認・Checker fixture固定・比較条件・受入条件案・費用/Guardrail案、Phase B未実行)`/`GPT6-MODEL-COMPARISON-TRIAL-01: SSOT反映(OPEN-234 GPT-6後対応、Trial開始許可・Phase A、順序)`、trailer `Management-ID: GPT6-MODEL-COMPARISON-TRIAL-01`。push。

## 報告(RESULT_PACKET_G6A + handback、目安40行)
【GPT-6 正式 model_id / 料金確認】(実在 id 一覧・probe 結果・単価の取得可否)/【Fixture 構成】(群別件数・category 被覆・不足)/【比較条件】/【受入条件案】(根拠)/【想定費用 / Guardrail 案】/【リスク】/【未解決・未確認】/SSOT 更新箇所/Phase A 終了 Status(`USER_DECISION_REQUIRED` or `READY_FOR_TRIAL_EXECUTION`、いずれも Phase B 未実行)/commit hash・raw URL/probe 実費。
