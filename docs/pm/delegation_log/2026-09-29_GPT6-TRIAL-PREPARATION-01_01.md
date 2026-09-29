## 管理ID

GPT6-TRIAL-PREPARATION-01(Family X Closeout 後に GPT-6 Trial を即開始できる状態にする read-only 整理、委任 _01)。**調査・整理のみ。Trial 開始禁止、Production code・Prompt・routing・SSOT 4 点・REPORT_LEDGER の変更禁止、API 呼び出し禁止(¥0)、Opus 起動禁止**。一時ファイル `docs/pm/ACTIVE_TASK_G6P.md` / `docs/pm/RESULT_PACKET_G6P.md`(commitしない)。並行: 別 Sonnet 1 件(Family X Meta E2E、`er019_output/family_x_refresh_e2e_01/meta/**`・`user_test/family_x_refresh_e2e_01/**`・`FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01_REPORT.md`・設計書を編集中)→ これらに触れない(Read は可)。本タスク出力先: `docs/pm/gpt6_trial_preparation_01.md`(新規)+delegation_log のみ。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 背景(ユーザー指示要旨)

優先順位: ① Meta E2E ② Family X Closeout / Gate 3 ③ GPT-6 Trial ④ GPT-6 Routing 判断 ⑤ Checker 根本再設計(OPEN-233、deferred)。GPT-6 Trial の基本方針: 「新旧モデルを同一入力・同一 Prompt・同一 Validator 条件で比較。特に Checker については今回の Evidence(重大 A 群・過剰品質 B 群・Hormuz B-2・changed_causality・notes_for_writer・非決定性)をそのまま比較できる状態にする」。GPT-6 で「過剰 BLOCK 率・非決定性・changed_causality・notes_for_writer・origin 判定・重大 fixture 検出率」がどう変わるかを見てから Checker 再設計に戻る。

## 整理項目(出力ファイルの章立て)

### 1. 現在の各 Role の actual model_id(Production 正式経路、Family X を主、他 Family も表に)
Grep 起点: `er006_model_routing_contract_01.py`(`PROCESS_MODEL_MAP|SUPPORT_MODEL|WRITER_MODEL|require_model`)、各 runner の `model=`・`require_model(`、`raw_usage_log.jsonl` の `model` 実測値(Hormuz run_03・Meta run_02/03・an3_t0_wiring_regression から)。Role: Writer(JA Writer O Original/R1/R2)、Researcher、Verification、Ledger / Deviation Checker(JA Fact Check・EN Advanced・Standard)、Translation(忠実英訳)、Standard simplification(A2)、Comment1〜4、Key Phrase 抽出、Key Phrase explanation(`KEY_PHRASE_ADVANCED_EXPLANATION`)、In One Line、Natural English QA、pronunciation resolver、その他 LLM Role(Family A/B/C/Z で使うもの)。表: Role/process 名/Contract 上の model_id/実測 model_id(log)/reasoning 設定/呼び出しファイル:行/Family。Contract と実測の不一致があれば明示。
### 2. routing SSOT
`er006_model_routing_contract_01.py` の構造(process → model、fail-closed、変更手順)、CURRENT_SPEC/DECISION_LOG の routing 関連決定(Grep `Model Routing|routing|gpt-5|model_id|SUPPORT_MODEL`)、GPT-6 へ切替える際に触る箇所(Contract 1 ファイルで済むか、runner にハードコードが残っていないか=Grep `"gpt-` で全一覧)。
### 3. 現行モデルの baseline cost / latency
`raw_usage_log.jsonl`・既存 REPORT(`NEWS-FAMILY-X-JA-FACT-DOUBLE-CHECK-COST-01`、`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01` §5、`FAMILY-X-REFRESH-E2E-*` §E2E)から Role 別の 1 call あたり cost 中央値・latency 中央値・token 量を集計(母集団明記、未計測は「未計測」)。集計スクリプトは scratchpad(repo に追加しない)。
### 4. 代表 fixture
- Checker 比較用: ER-009-N1 の危険 fixture 9 種(`er009_*` パス)、調査 REPORT の A 群 5 件・B 群 4 件(evidence json パス、JA/EN 逐語、gold 判定=現行 MAJOR/MINOR/origin)、Hormuz B-2、changed_causality 事例、notes_for_writer 12 件(Hormuz Ledger)、非決定性測定用の同一入力セット(Hormuz run_02/run_03 の JA・EN と Ledger)。
- 生成 Role 比較用: Family X 代表記事(Hormuz・Meta)の Ledger・storyline・JA・Advanced・Standard・Comment・KP・In One Line の入力/出力ペア(パス・sha256)。
- 各 fixture を「同一入力・同一 Prompt・同一 Validator」で新旧モデルに流すための入力ファイル一覧(存在確認のみ、コピーはしない)。
### 5. Evidence の所在
Hormuz run_01〜03(STOP evidence、案B 発動記録)、Meta run_02/run_03(Meta E2E 完了後に追記する欄を空けておく)、調査・レビュー REPORT、OPEN-233 本文、Family X 各 Trial の deviation json。
### 6. GPT-6 Trial 計画の下書き(決定しない、材料のみ)
比較軸(Quality: 重大 fixture 検出率・不要 BLOCK 率・一致率/Cost: call・費用/Delivery: latency)、Role ごとの比較順(Checker → Writer → Translation → Simplification → Comment/KP)、反復回数案(n=5)、費用概算(Role 別 1 call 中央値 × fixture 数 × n × 2 モデル)、STOP 条件・Guardrail 案、GPT-6 の model_id が Contract に未登録である場合の登録手順(変更はしない)。**新モデルの model_id 文字列は推測で書かず「未確認」とする**。

## 出力ファイル `docs/pm/gpt6_trial_preparation_01.md`

各項目に根拠(ファイル:行/log パス/REPORT 名)。未計測・未確認は明記。採用提案・Production 変更提案は書かない。ユーザー向け表記 Standard/Advanced。

## 固定ブロック

T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_GPT6-TRIAL-PREPARATION-01_01.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_GPT6-TRIAL-PREPARATION-01_01.md --json-out docs/pm/delegation_log/2026-09-29_GPT6-TRIAL-PREPARATION-01_01.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: API 支出なし。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧

- 上記 Grep 起点。`OPEN_ITEMS.md` Grep `OPEN-233`(全文)。`CURRENT_SPEC.md`/`DECISION_LOG.md` は Grep 該当箇所のみ。
- 更新位置: 出力ファイル(新規)、delegation_log。

## 実行コマンド全文

- `git pull --ff-only origin main`
- `grep -rn "\"gpt-" er0*.py | head -80`(ハードコード一覧)
- 集計: `.venv\Scripts\python.exe <scratchpad>\aggregate_usage.py`(自作、repo 外)

## Git

- add 対象(path 指定のみ): 出力ファイル、delegation_log+`_check.json`。メッセージ `GPT6-TRIAL-PREPARATION-01: GPT-6 Trial準備(Role別actual model_id・routing SSOT・baseline cost/latency・代表fixture・Evidence所在・Trial計画材料、read-only)`、trailer `Management-ID: GPT6-TRIAL-PREPARATION-01`。push。

## 報告(RESULT_PACKET_G6P + handback、目安30行)

Role 別 model_id 表の要約(Contract と実測の不一致有無)/ハードコード箇所数/baseline cost・latency の要点/fixture 数と所在/Trial 費用概算/未確認事項/commit hash・raw URL。
