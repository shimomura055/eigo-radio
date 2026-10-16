# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01 委任_01(read-only調査・提案書作成。略称RLCO)。本日=2026-10-16(JST)。

## 性質/到達上限Status/禁止事項
- 性質: **read-only・JPY0**。実測ログ・コード・Promptの静的分析と提案書作成のみ。
- 到達上限Status: `ANALYSIS_COMPLETE_PROPOSAL_READY`(採用判断はユーザー。実装・Trialへ進まない)。
- 費用上限: JPY0(有料API呼出禁止。Web検索・LLM呼出を伴うscript実行禁止。test実行も不要)。
- 禁止: Productionコード・Promptの変更/新規Research・Ledger実行/有料Trial/モデル変更/品質Gate緩和/改善案の独断採用/Family A・B・Cの調査/無関係Open Item棚卸し。**単純なFact数削減・検証省略・低性能モデル置換を第一案にしない**。不要に見える処理も品質保証上の役割を確認せず削除候補にしない。推定値は根拠・前提付き、算出不能なものは「算出不可」と書き架空の数字で埋めない。削減効果の二重計上禁止。
- **並行タスク衝突回避(重要)**: 現在、別のsonnet-workerが同じrepoで「FXPW 委任_06(Coffee音声工程実走・commit/push)」を実行中。したがって本委任では (1) **gitの書込み操作(add/commit/push/merge/checkout/stash)を一切行わない**(読取 `git log/show/status --porcelain` は可)。成果物は新規ファイルとして作成し、最後に「commit対象ファイル一覧」をRESULT_PACKETに書いてFableへ渡す(後続委任でcommitする)。(2) `docs/pm/ACTIVE_TASK.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・`docs/pm/REPORT_LEDGER.md`・`docs/pm/USER_DECISION_REGISTER_01.md`は**編集しない**(SSOT編集権なし。追記文案はRESULT_PACKETに記載のみ)。(3) `er019_output/family_x_audio_production_wiring_01/`配下と`user_test/`配下には触れない(読まない・書かない)。(4) `er019_output/coffee_prices/run_fxpw_01/`配下は**読取のみ**。(5) 一時ファイルはscratchpad(`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\rlco\`)を使う。
- Opus独立技術レビューGate(11-3): 非該当(設計・実装なし。提案採用時に条件A/Cの要否をFableが判断)。
- 時間見込み: ログ集計30分/コード・Prompt読解60分/過去対策・承認仕様照合30分/提案書60分 ≒ 3時間。並列化: 単独。
- STOP条件(ユーザー§8): 有料Trialが必要/品質仕様変更が必要/Production改修が必要/実測証拠不足で推測結論になる/新しいユーザー採用判断が必要/調査範囲拡大が必要 → 該当箇所を「STOP理由」として記録し、分析できる範囲で提案書を完成させて報告(作業全体を止める必要はないが、推測で埋めない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし=該当なし)
T-3: 本委任は費用上限JPY0(API呼出禁止)のため、Cap Guardrail定型は該当なし。
T-0補足(厳守): (a)本委任文は**全文**を `docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_委任_01.md` へ保存(要約・見出しのみ不可)。(b)下記「ユーザー指示(原文)」節を**一字一句そのまま** `docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_USER.md` へ保存し、文字数とsha256をRESULT_PACKETへ記録(約2,600〜3,000字の範囲外なら保存漏れを疑う)。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
# Claude Code／Fableへの指示
## Family X Research・Verified Fact Ledger コスト構造調査・削減案検討

**管理ID：FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01**

**現在Status：INVESTIGATION_REQUIRED**

**今回の到達点：ANALYSIS_COMPLETE／PROPOSAL_READY**

**Production実装・追加Trial：禁止**

### 1. 目的

Family X Coffee正式E2Eで、ResearchおよびVerified Fact Ledgerの費用が大きい原因を特定し、品質を維持しながら量産原価を削減する方策を提案する。

今回の実測：

| 工程 | 実測費用 |
|---|---:|
| Research | ¥19.85 |
| Verified Fact Ledger | ¥25.14 |
| **合計** | **¥44.99** |
| Text工程全体 | ¥72.64 |

Research＋LedgerでText工程の約62%。

Family Xの量産原価目標は**Standard＋Advancedで70円／記事セット**。

特に、Verified Fact LedgerがResearchより高額になっている理由を重点調査する。

### 2. 調査対象

対象run：

`er019_output/coffee_prices/run_fxpw_01`

正式Production経路のResearch・Verified Fact Ledgerを調査する。

以下を実測ログ・コード・Promptと突合する。

**A. API費用の構造**
- 実際に使用したmodel_id
- API呼出回数
- 入力・出力トークン数
- モデル別費用
- Web検索の回数・単価
- キャッシュ利用状況
- retry／fallback／再生成による追加費用

**B. 処理内容の妥当性**
- ResearchとLedgerで重複している調査・検証処理
- 同じ情報への繰り返しWeb検索
- 不必要に長いPrompt・入力コンテキスト
- Fact候補数と検証対象数の関係
- 必要以上のLLM判定・外部検索
- ResearchからLedgerへの情報引き渡しの効率
- 品質に寄与していない可能性のある工程

**C. 品質上の必要性**
- 各処理が防いでいるFact誤り
- 情報源・出典確認の必要性
- 曖昧な表現・意味反転・時系列誤読を防ぐ機能
- WriterのFact Lockに必要な情報の保持
- 承認済みのResearch・Fact Ledger仕様との整合

不要と見える処理でも、品質保証上の役割を確認せず削除候補としないこと。

### 3. 改善案の検討

以下を候補として比較する。ただし、これらの方法を採用することは決定していない。

- Research結果・出典情報の再利用による二重検索削減
- Ledger検証の対象・検索回数の合理化
- Prompt・コンテキストの効率化
- 重複LLM判定の削減
- キャッシュや既存情報の安全な活用
- 必要な品質を維持できる範囲でのモデル配置見直し
- ResearchとLedgerの責務分担の最適化

既存の承認済み仕様や過去のコスト削減対策を確認し、同じ仕組みを重複して新設しないこと。

**単純なFact数削減、検証省略、低性能モデルへの置換を安易な第一案としない。**

### 4. 提案書の必須内容

改善案ごとに以下を整理する。

| 項目 | 内容 |
|---|---|
| 原因 | 何が費用を押し上げているか |
| 証拠 | 実測ログ・コード・API usage |
| 対策 | 具体的に何を変更するか |
| 削減額 | Research／Ledgerそれぞれの円単位の試算 |
| 削減率 | 現行実測比 |
| 品質リスク | Fact正確性・出典品質・Writerへの影響 |
| 実装負荷 | 小／中／大 |
| 検証方法 | 採用前に必要なTrial・Regression |
| 推奨順位 | 品質・費用・開発負荷を総合評価 |

推定値には根拠と前提を明記すること。

算出できないものを架空の数字で埋めない。

また、改善案を個別に実施した場合と、組み合わせた場合の費用を比較する。削減効果の二重計上は禁止。

### 5. QCD上の方針

**品質 ＞ 納期 ＞ コスト**

量産コスト削減は重要だが、次を犠牲にしない。

- Factの正確性
- 検証可能な出典
- Fact Lock
- Writerへ渡す必要情報
- 記事の自然さ・面白さ
- Family X正式仕様との整合

70円目標の達成可能性も分析するが、達成のために品質を下げる案は推奨しない。

### 6. 作業範囲・禁止事項

**実施してよいこと**
- 既存ログ・コード・Promptのread-only調査
- 過去runとの比較
- 費用内訳の再計算
- 無課金の静的分析
- 対策案・削減試算・リスク評価
- Fableによる独立レビュー

**禁止事項**
- Productionコード・Promptの変更
- 新規Research・Ledger実行
- 有料APIによる追加Trial
- モデル変更
- 既存品質Gateの緩和
- 改善案の独断採用
- Family A／B／Cの調査・開発
- 無関係なOpen Itemの棚卸し

今回の調査費用は原則JPY0。

### 7. Coffee E2Eとの関係

Coffeeの音声化は既にユーザー承認済みであり、別の正式タスクとして進行中。

**今回のコスト調査を理由に、Coffee音声化を止めたり、実装を変更したりしない。**

Coffeeの音声工程完了後に得られる実測費用は、最終的な量産原価分析へ追加してよい。

ただし、今回の原因調査は既存のResearch・Ledger実測記録だけで進められるため、音声工程の終了待ちを必須にしない。

### 8. STOP条件

以下の場合はSTOPして報告する。

- 有料Trialが必要
- 品質仕様を変更する必要がある
- Production改修が必要
- 実測証拠が不足し、推測で結論を出すことになる
- 新しいユーザー採用判断が必要
- 調査範囲の拡大が必要

分析の途中で改善案が有望と判明しても、実装へ進まない。

### 9. 最終報告

非エンジニアPM向けに、次の順で報告する。

1. **Research ¥19.85、Ledger ¥25.14の具体的な費用発生原因**
2. モデル・API・検索・トークン別の費用表
3. 無駄・重複・過剰処理の有無
4. 品質上削れない処理
5. 推奨改善案（最大3案程度に絞る）
6. 案ごとの削減額・削減率・品質リスク
7. 組合せ後の量産原価見込み
8. 70円／記事セット目標への影響
9. 次に検証する場合の必要費用・受入条件
10. 本当にユーザー判断が必要な事項のみ

**最終報告後はSTOP。実装・Trialには進まない。**

Fableは、原因分析と削減試算を実測証拠と照合し、品質リスクや削減効果の過大評価がないか独立確認すること。

(ユーザー原文ここまで)

## KPI provenance欄(24節)
- 費用内訳・token数・呼出回数・web_search回数: `reuse`(run_fxpw_01の既存ログ `cost.json`/`raw_usage_log.jsonl`/各stage成果物。再計測なし)。
- 単価: `er005_output/cost_baseline_01/pricing_snapshot.json`等の正式価格記録から(frozen)。記録にない単価は「未確認」。
- 過去run比較: `reuse`(run_l3_01等の既存cost.json)。
- 削減試算: `manual_substitution`(実測token×単価の机上計算)と明記。E2E自己確認: No(分析のみ)。

## Opus台帳更新(11-5)
該当なし。

## 事前指定Read一覧
1. `er019_output/coffee_prices/run_fxpw_01/cost.json` 全文、同dir `raw_usage_log.jsonl` 全行(stage tag `research`/`ledger`の行をmodel/呼出/token/web_search/cache欄で集計。行数が多ければ scratchpad の集計scriptで `python -I` 実行)。
2. `er019_output/coffee_prices/run_fxpw_01/research_ledger/` 配下: Glob `**/*.json`・`**/*.md` → entry_point/research出力/ledger出力/各Factの検証記録(候補数・検証対象数・出典数・web_search回数・LLM判定回数)。`run_fxpw_01_stage_research*.log`/`*_stage_ledger*.log`(Glob `er019_output/coffee_prices/run_fxpw_01_stage_*.log`)。
3. Research/Ledgerのコード: `er019_family_x_entertainment_production_runner_01.py` を Grep `def .*research|def .*ledger|web_search|model=|MODEL|max_output_tokens|reasoning|cache|retry` → 該当範囲Read。呼び出し先モジュール(import先。Grep `^from er0|^import er0`)のうちResearch・Verified Fact Ledgerを実装するもの(名称に `research`/`fact_ledger`/`verified` を含むもの、例 `er0XX_*fact_ledger*`) を Grep `def |prompt|PROMPT|web_search|model` → 該当範囲Read。Prompt本文は文字数・構成(system/user、few-shot有無、記事候補の埋込量)を記録。
4. 承認済み仕様: `CURRENT_SPEC.md` を Grep `Verified Fact Ledger|Fact Ledger|Research Ledger|Fact Lock|web_search|Research仕様` → 該当節のみRead(全文読込禁止)。`DECISION_LOG.md` を Grep `Fact Ledger|Research` で直近決定のみ(全文禁止)。`OPEN_ITEMS.md` を Grep `Ledger|Research|OPEN-395|cost|原価|70円` → 既存のコスト対策・関連Open Item(重複新設防止、PM_GOVERNANCE 21節 A/B/C分類)。
5. 過去run比較: `er019_output/coffee_prices/run_l3_01/cost.json`(research 21.96/ledger 24.88とされる)、Glob `er019_output/*/run_*/cost.json` から直近Family X run 3〜5件のresearch/ledger費用(同テーマ・別テーマの分布)。
6. 単価: `er005_output/cost_baseline_01/pricing_snapshot.json` 全文(モデル別input/output/cached単価、web_search単価、USD_JPY)。
7. `docs/pm/PM_GOVERNANCE.md` Grep `15-8|15-9|^## 21|21-` → 該当範囲(1生成セット総原価・70円・Existing Spec/Prior Trial Check Gate)。
8. `docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/COFFEE_E2E_PLAN_01.md` Grep `15-9|Research|Ledger|OPEN-395` → 既記載の原価見込み・偶発リスク。

## 事前指定Grep一覧+追記位置・更新位置の手順
- 成果物(新規作成): `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/ANALYSIS_REPORT_01.md`(ユーザー§9の10項目順+§4表+付録: 集計表・証拠path・集計script名)。集計scriptは同dir `tools/` ではなく `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/aggregate_usage_01.py`(read-only、API呼出なし)として保存可。
- SSOT追記文案(編集せず文案のみ): DECISION_LOG(調査着手・提案書所在)、OPEN_ITEMS(新規Open Item候補: 提案の管理ID、Status=PROPOSAL_READY_USER_DECISION)、REPORT_LEDGER行、ACTIVE_TASK追記行。RESULT_PACKETに記載。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_委任_01.md --json-out docs/pm/delegation_log/2026-10-16_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01_委任_01.md_check.json`
- 集計: `.venv\Scripts\python.exe -I docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/aggregate_usage_01.py --usage-log er019_output/coffee_prices/run_fxpw_01/raw_usage_log.jsonl --cost-json er019_output/coffee_prices/run_fxpw_01/cost.json --pricing er005_output/cost_baseline_01/pricing_snapshot.json --out docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01/usage_breakdown_01.json`(scriptは自作。ネットワーク・API呼出を含めない。集計結果の合計が cost.json の research 19.85/ledger 25.14 と一致することを検算し、差があれば差額と原因[丸め・未集計行・web_search課金の扱い]を報告)。
- 有料コマンド・runner実行は一切しない。

## SSOT追記文
(編集権なし。文案のみRESULT_PACKETへ。)

## Git(明示add対象・コミットメッセージ・trailer)
- **本委任ではgit書込みを行わない**(並行委任_06がcommit中)。RESULT_PACKETに「commit対象ファイル一覧」(delegation_log 2件+_check.json、ANALYSIS_REPORT_01.md、aggregate_usage_01.py、usage_breakdown_01.json)とcommit message案「FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01 委任_01: Research/Verified Fact Ledger費用構造のread-only分析+削減案提案書(JPY0、実装・Trialなし)」を記載。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_RLCO1.md`(要約20行程度、詳細はANALYSIS_REPORT_01.md):
1. T-0結果2行(委任文保存/check結果、ユーザー原文保存path・文字数・sha256)。
2. Status・STOP理由の有無。
3. Research 19.85 / Ledger 25.14 の内訳(model別・呼出回数・input/output/cached token・web_search回数と単価・retry分)と検算結果(cost.jsonとの差)。
4. Ledger>Researchの直接原因(1〜3点、証拠path付き)。
5. 無駄・重複・過剰処理の有無(各々「品質上の役割」を併記。役割不明は「要確認」とし削除候補にしない)。
6. 品質上削れない処理の一覧。
7. 推奨改善案(最大3案、§4表の全項目)+個別/組合せ削減額(二重計上なし)+Existing Spec/Prior Trial Check(A/B/C)。
8. 組合せ後のtext工程・1記事セット原価見込み(音声は「未実測」のまま。委任_06完了後の値は入れない)と70円目標への影響(達成可能性は条件付きで)。
9. 次に検証する場合の必要費用(出典付き)・受入条件案。
10. 判断候補(A既判断/B承認範囲内/C独立/D真に新しい、の別)。改善案の採用はユーザー判断事項として列挙するが、提案書の段階で「採用してよいか」以外の細かい質問を作らない。
11. 4行(①既存仕様整合[file:line] ②Production到達経路の未承認機能既定値=変更なし ③最終成果物path ④撤去・残置=なし)。
12. `判定整合: 重大NG=[…|なし] / 主因= / 是正対象= / STOP理由= / 提示=…`。
13. commit対象ファイル一覧・SSOT追記文案。
14. 一覧外Readの理由(あれば1行ずつ)。

## Fable自己チェック(送信前)
- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり(新規ファイル・SSOTは文案のみ)
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(JPY0)
- [x] 並行タスク衝突回避あり(git書込み禁止・ACTIVE_TASK/SSOT不編集・音声dir不可触)
- [x] Opus Gate判定あり(非該当)
- [x] 時間見込みあり(約3時間、単独)
- [x] 新規委任(再委任ではない)
