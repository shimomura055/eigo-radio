## 管理ID

OPEN-233-CHECKER-REDESIGN-TRIAL-01(Phase A=Trial 計画確定のみ、委任 _01)。一時ファイル `docs/pm/ACTIVE_TASK_C233A.md` / `docs/pm/RESULT_PACKET_C233A.md`(commitしない)。並行 Agent なし(`git pull --ff-only origin main`、HEAD `8be7d639` 以降)。**SSOT 編集は DECISION_LOG 1 エントリ+OPEN_ITEMS(OPEN-233 へポインタ追記)のみ**。削除・移動・`rm`・`git clean`・`git stash`・rebase/reset/amend/force push 禁止。未追跡ファイルは他タスク由来として触らない。push 競合時は `git merge origin/main` のみ。**APIキー本文を表示・log・commit・報告に書かない**。**Production code・共通 Checker Prompt・severity・routing・Production schema の変更禁止。Production への配線禁止。Trial 実行(有料 fixture 実行)禁止**(Phase A は計画のみ。Trial 用 variant の実装は Production 非接続の `er051_*` として作成可、mock テストのみ)。Opus 起動禁止。費用 ¥0(API 呼び出しなし)。

## ユーザー決定(2026-09-29、逐語厳守)

1. QUALITY は Production 通過可(Trial 前提として承認、Production 採用決定ではない): BLOCKING=従来どおり fail-closed/QUALITY=通過+log/ACCEPTABLE=通過。
2. deterministic 昇格 Trial: `changed_actor`/`changed_number`/`changed_negation`/`changed_comparison` の flag=true は LLM severity が MINOR でも BLOCKING へ昇格させる案を検証。
3. 過剰 BLOCK 側: 単純な causality 緩和ではなく、factual_constraint / writer_guidance、qualifier、basis、Ledger 観測との整合 等の **schema 変更候補を含めて Trial**。Production schema は変更しない。**Family X 限定の Trial variant**。
4. Hormuz B-2 は **暫定 gold=QUALITY**(Trial 評価用ラベル、最終仕様ではない)。
5. 不要 BLOCK 率: baseline 75% → **Trial 目標 25% 以下**。
6. Prompt / schema variant は Family X 限定。他 Family へ波及させない。Production 共通 Prompt/schema を変更しない。
7. Trial 対象モデルは **`gpt-6-luna` のみ**(`gpt-5.6-luna` 再比較不要、Sol/Astra 対象外)。
8. QUALITY ログ運用・Human Review 連携設計は Trial 後へ defer。
9. 最優先評価: Safety=重大 fixture BLOCKING 維持率 100%/Productivity=不要 BLOCK 率 25% 以下/Stability=同一 input の揺れ低減/QCD=cost・latency・retry・STOP 率。受入目的=「過剰品質によって Production 生産性を失わない」。
10. Phase A で確定: fixture 固定/gold 確定/Family X 限定 variant/post-hoc v2/schema variant/Prompt variant/Trial 構成/反復回数/正式費用見積/Guardrail/受入条件/STOP 条件。Phase A 終了後、**Trial 実行前に正式報告して STOP**。

## 入力(全文 Read 可)

`docs/pm/design_checker_redesign_v02_01.md`(v0.2 §1〜§14)、`OPEN-233-CHECKER-REDESIGN-V02-01_REPORT.md`、`GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md` §Phase B/§Closeout(正式単価: gpt-6-luna Input $0.10/Cached $0.01/Output $0.50 per 1M、reasoning は output に含む、為替 ¥156.88)、`er050_output/gpt6_checker_comparison_trial_01/cost_recalc_01.json`・`summary_*.json`(fixture 別 token 実測)、`er050_gpt6_checker_comparison_trial_01.py`(harness、fixture 定義 json)、`er003_v1_en_direct_vfl_01_generate.py`: Grep `DEVIATION_PROMPT_TEMPLATE|DEVIATION_JSON_SCHEMA|_apply_deviation_post_hoc_validation|FACT_LEDGER_JSON_SCHEMA|notes_for_writer|def run_deviation_check`、`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md` §3(A/B 群 evidence パス)、`docs/pm/review_ledger_deviation_redesign_01_part_b.md`(notes_for_writer 12 件分類)。

## Phase A 成果物: `docs/pm/design_open233_checker_redesign_trial_01.md`(新規、章立て固定)

### 1. fixture 固定(表: id/群/入力パス/sha256/現行判定/gold/gold 根拠)
- 重大群(Safety、BLOCKING 維持 100% 対象): ER-009-N1 9 種+A 群 5 件(A-1 は「category 未検出」例として別掲し、維持率の分母に含めるか否かを明記して提案)+`er009_changed_actor`(n=5 反復対象)。
- 境界・過剰品質群(Productivity、不要 BLOCK 率の分母): B-1(4 事例)、B-2(gold=QUALITY 暫定)、B-3、B-4(3 項目)、Meta run_03 Standard translation MAJOR。**不要 BLOCK 率の定義**を確定(分母=gold が QUALITY/ACCEPTABLE の fixture 数、分子=BLOCKING 判定数。baseline 75% の算出根拠[B 群 4 件中 3 件 MAJOR]と一致する定義にする)。
- 非決定性群(Stability): Hormuz run_03 の advanced/standard/ja_original/ja_r2+Ledger(GPT-6 Trial と同一入力、n=5)。
- 追加 fixture は作らない(負例不足は「制約」として明記)。sha256 を実測。

### 2. gold 確定(表)
既存 A/B 区分を gold の出発点とし、B-2=QUALITY(ユーザー暫定)、changed_actor=BLOCKING、B-1=ACCEPTABLE 候補、B-3=?、B-4=?、Meta Standard=?(fact_id 010/012)を **Fable/ユーザー確認が必要なものは「暫定+要確認」印**で列挙(Claude が独自に確定しない)。gold ラベルは BLOCKING/QUALITY/ACCEPTABLE の 3 値で付け、現行 MAJOR/MINOR との対応も併記。

### 3. Family X 限定 variant(Production 非接続、`er051_open233_checker_trial_variant_01.py` 新規)
- **post-hoc v2**: 既存 `_apply_deviation_post_hoc_validation` のロジックをコピーし(import して wrap でも可、vfl01 は無変更)、昇格ルール(actor/number/negation/comparison flag=true → `severity_final=BLOCKING`)、`severity_final`/`action`/`basis`/`rule_id` の付与、QUALITY/ACCEPTABLE の判定ルール(v0.2 §6〜§7 に基づく: numeric/actor/time/negation 矛盾なし+Ledger 観測と整合+factual_constraint に反していない → QUALITY、教材化の合理的範囲 → ACCEPTABLE。定型 hedge 単独を免罪符にしない)を実装。mock テスト(既存 run json 67 件への適用で誤昇格 0・A 群 BLOCKING 維持・JA 段 origin=None の誤降格なし)。
- **schema variant**(Trial 出力 schema、Production schema は不変): deviation に `qualifier_present`(限定語/留保文の有無と該当文)、`ledger_field_basis`(判定根拠が fact 本体か notes_for_writer か)、`observation_consistent`(記事の最終理解が Ledger 観測と矛盾しないか)、`matched_notes_id` を追加。Ledger 入力側: notes_for_writer を `factual_constraint` / `writer_guidance` に **Trial 内で機械分類または手動分類**(Hormuz 12 件は Part B の分類を使用、Meta Ledger は本 Phase A で分類し表に)し、Checker には factual_constraint のみを notes として渡す variant と、現行どおり全量渡す variant を用意。
- **Prompt variant**(Family X 限定、`DEVIATION_PROMPT_TEMPLATE` を import して差分ブロックを追加する形。共通 Prompt は不変): 上記 schema フィールドの出力指示、「claim 単体ではなく前後 1〜2 文の留保・限定を考慮して observation_consistent を判定」、「notes_for_writer の writer_guidance は判定根拠にしない」。差分ブロックの逐語と sha256 を記録。
- variant 一覧(構成 ID): V0=現行 Prompt+現行 post-hoc(baseline、GPT-6 Trial 結果を再利用し **再実行しない**)/V1=現行 Prompt+post-hoc v2(昇格のみ)/V2=Prompt variant+schema variant+post-hoc v2(notes 全量)/V3=V2+notes を factual_constraint のみ。各 variant の「変えた要素」表。

### 4. Trial 構成・反復回数
モデル `gpt-6-luna` のみ、reasoning="high"(現行と同一)。Step 1 重大群(V1/V2/V3 × 1 回、changed_actor は n=5)→ Safety 100% 未達の variant は以降を実行しない/Step 2 境界群(V1/V2/V3 × 1 回)→ 不要 BLOCK 率/Step 3 非決定性群(最良 variant のみ n=5、V0 の GPT-6 実測と比較)。call 数を表に。

### 5. 正式費用見積(gpt-6-luna 正式単価 × GPT-6 Trial の fixture 別実測 token、為替 ¥156.88)
variant 別・Step 別・合計(USD/JPY)。Prompt variant は入力 token 増分を見積(差分ブロックの token 数を tiktoken 等で概算し根拠記載)。Guardrail 案(合計上限、Step 別上限、想定の 2 倍で STOP)。

### 6. 受入条件(確定案)
Safety: 重大群 BLOCKING 維持率 100%(V0 で MISS していた changed_actor は V1 以降で 5/5 BLOCKING を要求)/Productivity: 不要 BLOCK 率 ≤25%/Stability: 非決定性群の一致率が V0(GPT-6 実測)以上/QCD: 記事換算 cost・latency 中央値・retry・STOP 率を V0 と比較し、cost は V0 の 1.5 倍以内(案、根拠記載)。**受入目的「過剰品質によって Production 生産性を失わない」を明記**。

### 7. STOP 条件
予算・API error 継続・schema 非互換・harness 不具合・fixture 破損・Production への影響/Safety 100% 未達(当該 variant の打ち切り、Trial 全体は続行)/gold の再判断が必要な判定割れ(USER_DECISION_REQUIRED 候補として列挙、Claude は gold を書き換えない)。

### 8. 既存仕様との競合・Dangling Reference 確認(variant が Production を一切 import 経由で変更しないことをテストで証明)、リスク、★ユーザー判断(gold 要確認 fixture、cost 上限、V3 の notes 分類の妥当性)。

## SSOT(最小)
- DECISION_LOG: 新エントリ(ユーザー判断 1〜10 逐語要旨、Phase A 成果物ポインタ、Status)。
- OPEN_ITEMS: OPEN-233 に Trial 管理ID ポインタ+「Phase A 完了・実行前 STOP」を追記。
- REPORT `OPEN-233-CHECKER-REDESIGN-TRIAL-01_REPORT.md`(新規、Phase A 要約)。REPORT_LEDGER は文案のみ。

## 固定ブロック
T-0: 本委任文を `docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-TRIAL-01_01.md` へ逐語保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-TRIAL-01_01.md --json-out docs/pm/delegation_log/2026-09-29_OPEN-233-CHECKER-REDESIGN-TRIAL-01_01.md_check.json` を実行し結果 1 行記録。T-2: TTS なし。T-3: API 支出なし。E-1/D-1/G-1/F-1 標準。

## 事前指定Read一覧 / 事前指定Grep一覧
上記「入力」。更新位置: 設計書(新規)、`er051_*`(新規、Production 非接続)+テスト、REPORT(新規)、DECISION_LOG、OPEN_ITEMS、delegation_log。

## 実行コマンド全文
- `git pull --ff-only origin main`
- `.venv\Scripts\python.exe -m unittest er051_open233_checker_trial_variant_01_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er003*_test_*.py"`(Production 無変更の確認、pre-existing 4 件は根拠付き)
- 費用見積: `.venv\Scripts\python.exe <scratchpad>\estimate_open233_trial_cost.py`(自作、repo 外)

## Git
- commit 2 つ: (1) 設計書+`er051_*`+テスト+REPORT+delegation_log `OPEN-233-CHECKER-REDESIGN-TRIAL-01: Phase A(fixture固定・gold暫定・Family X限定variant V1〜V3[post-hoc v2/schema/Prompt]・Trial構成・正式費用見積・Guardrail・受入条件・STOP条件、Production非接続、Trial未実行)`;(2) SSOT 2 点 `OPEN-233-CHECKER-REDESIGN-TRIAL-01: SSOT反映(ユーザー判断1〜10、Phase A完了・実行前STOP)`。trailer `Management-ID: OPEN-233-CHECKER-REDESIGN-TRIAL-01`、path 指定 add、push。

## 報告(RESULT_PACKET_C233A + handback、目安50行)
【fixture 固定】(群別件数・不要 BLOCK 率の定義)【gold 確定】(暫定+要確認の一覧)【variant V1〜V3】(変えた要素、差分ブロック sha256、mock テスト結果)【Trial 構成・反復・call 数】【正式費用見積】(variant 別・Step 別・合計 USD/JPY、Guardrail 案)【受入条件】【STOP 条件】【既存仕様競合・Dangling Reference 確認】【★ユーザー判断】/commit hash 2 件・raw URL/Status=`READY_FOR_TRIAL_EXECUTION` または `USER_DECISION_REQUIRED`(いずれも実行前 STOP)。
