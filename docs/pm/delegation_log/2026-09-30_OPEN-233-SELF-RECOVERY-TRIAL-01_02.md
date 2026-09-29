管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_02: 設計書へコスト Cap 要件を組み込む修正+Opus model_id probe 結果の記録。**API 呼び出しなし・¥0・Production 非接続・実装なし**)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 前提
- docs/pm/PM_BRIEF.md 固定ヘッダ、docs/pm/PM_GOVERNANCE.md 8節。
- 対象: docs/pm/design_open233_self_recovery_flow_01.md(委任_01 成果、12 節)、OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md、docs/pm/RESULT_PACKET_C233E.md。
- 一時ファイル: docs/pm/ACTIVE_TASK_C233F.md / docs/pm/RESULT_PACKET_C233F.md(新規、commit 禁止)。既存 *_C233A〜E は削除・移動しない。

## 1. ユーザー追加指示(2026-09-30、逐語要旨。DECISION_LOG へ 1 エントリで記録)
- 量産時に増加する Production 継続コストの上限 **最大 +¥3/記事**。ただし「+¥3 まで使ってよい」ではなく「できる限り安く達成する」が大前提。同品質・同自動完結率なら +¥0.5/+¥1/+¥2/+¥3 のうち安い方式を優先。
- コストを無視した対策(Checker 多重追加・Second Judge 追加・Rewrite 複数回・self-consistency 常時・高価モデル常時)は禁止。Safety/Self-Recovery/Cost を同時最適化。
- Stage 別計測: Initial Check/Re-screening/Rewrite/Recheck/追加 Judge/self-consistency/その他追加 LLM call について、発動率・1 回コスト・1 記事平均追加コスト・worst case・P50/P95。**毎記事必ず発生する固定費**と**BLOCK 時だけ発生する条件付き費用**を分離。
- 評価基準: Safety(重大 Fact 見逃し 0)/Self-Recovery(10〜20 記事 Trial で Ledger/Deviation 起因 USER_DECISION_REQUIRED 0)/Cost(追加継続コスト ≤ ¥3/記事、その中で最小化)。
- +¥3 以下で困難と判断できる Evidence が出た場合、勝手に膨らませず早期に中間報告(なぜ困難か/¥3 以内で達成できる水準/¥3 超で何が改善するか/想定追加コスト/代替案/トレードオフ)= USER_DECISION_REQUIRED。
- 各 Mandatory Checkpoint で必須報告: best variant の追加コスト/記事/固定追加費/条件付き追加費/BLOCK 時平均 recovery 費用/P50/P95/+¥3 Cap までの余裕。品質だけ改善して Cost 確認後回しは禁止。
- 設計優先順位: ①初回 Checker 精度改善(追加 call なしで改善できるなら最優先)→ ②BLOCK 時のみ Re-screen(全記事への固定追加 call を避ける)→ ③必要時のみ Rewrite → ④それでも必要なら限定的 self-consistency/Second Judge。常時 2 回 Checker より、必要な記事だけ 2 段目へ進む設計を優先。
- Opus レビュー: 開始前に実際の model_id を確認し、利用可能なら最新 Claude Opus 5.5 を明示使用。旧 Opus 固定なら勝手に実行せず報告・更新。レビュー報告に actual model_id を runtime evidence として残す。

## 2. Fable 判定・記録事項
- Opus model_id probe(2026-09-30、Fable 実施、read-only): opus-consultant(`.claude/agents/opus-consultant.md` の `model: opus` エイリアス)の自己申告=モデル名「Opus 5 (1M context)」、exact model ID `claude-opus-5[1m]`、knowledge cutoff 2026-05。**Opus 5.5 ではない**ため本 Phase の Opus L2 レビューは未実行(ユーザーへ model_id 指定を要請中)。前 Phase の Opus L2 #1(docs/pm/opus_l2_review_open233_checker_trial_01.md)も同エイリアス経由であり Opus 5 で実行された可能性が高い(当時 model_id 未記録)。→ これを REPORT §1 と opus_l2_review_open233_checker_trial_01.md の**冒頭ヘッダに注記として追記**(本文は一字も変えない)、DECISION_LOG エントリにも記録。`.claude/agents/opus-consultant.md` は**本委任では変更しない**(ユーザーから model_id 指定後に別途)。
- 設計の第一候補は「Stage 1 は現行 call 数のまま(固定追加費 ¥0)、BLOCK 時のみ Stage 2(1 call)→ 必要時のみ局所 Rewrite+全文 Recheck」。self-consistency 常時実行・高価モデル常時利用は不採用。

## 3. 設計書への追加・修正(既存節は削除せず、追記・修正箇所を明示)
### 3-1. 新設 §13「コストモデルと +¥3/記事 Cap」
- 単価根拠(公式単価・推測禁止): gpt-5.6-luna In $0.20/Cached $0.02/Out $1.20、gpt-6-luna In $0.10/$0.01/$0.50(per 1M、GPT6-MODEL-COMPARISON-TRIAL-01_REPORT.md §Closeout C-2)、¥156.88。Checker 1 call 実測: 前 Phase n=20 データ(V0 ¥0.21〜0.30、V4-A ¥0.28〜0.38 @gpt-6-luna)、Production 現行(gpt-5.6-luna)は GPT-6 Trial の 84 call 突合(記事 4 call ¥1.96)を根拠に 1 call ≈ ¥0.49。
- 記事 1 本の現行 Checker 構成(JA/Standard/Advanced 等、何 call か)を er012 の実装から確定し、**現行ベースライン費用/記事**を算出。
- 追加コスト = 固定費(毎記事、目標 ¥0)+ 条件付き費 = Σ(Stage 発動率 × Stage 単価)。Stage 2 単価(入力: Ledger+context+対象 claim+Stage 1 出力、出力: schema 小)を token 見積りから算出、Stage 3 局所 Rewrite 単価(Writer モデル・入力 sentence±1+Ledger、出力短文)、Recheck 単価(全文 Checker 1 call)、案B(JA 差し戻し=JA Writer 再生成+Fact Check+再英訳+再 Check、既存 E2E 実測から)。
- 発動率の根拠: E2E 実測(Hormuz run_01〜03 は 3/3 で STOP、Meta run_03 は must-fix retry 1 回で通過)と前 Phase B 群/negative 候補の BLOCK 率。楽観/中央/悲観の 3 シナリオで、記事あたり平均追加コスト・P50/P95・worst case(cycle 上限 2 回到達時)を表にする。
- **+¥3 Cap 判定**: 各シナリオ・各モデル(Stage 2 を gpt-6-luna にする案/gpt-5.6-luna にする案)で Cap 内か、余裕はいくらか。worst case が ¥3 を超える場合は cycle 上限・Rewrite 範囲でどう抑えるかを明記。
- 「できる限り安く」の観点で、優先順位 ①〜④ に沿った**段階案**(案 α: Stage 1 Prompt 改善のみ[V4-A/C2 相当、追加 call 0、ただし Production Prompt 変更=将来ユーザー判断]、案 β: α+BLOCK 時のみ Stage 2、案 γ: β+局所 Rewrite、案 δ: γ+限定 self-consistency)を並べ、各案の想定追加コスト/記事と到達見込み(自動完結率)を対比。第一候補を明示。
### 3-2. §8 測定項目に Stage 別コスト計測(発動率・1 回コスト・1 記事平均・worst・P50/P95、固定費/条件付き費の分離)を追加。Trial harness が Stage ごとに usage を記録する要件を §9 に追加。
### 3-3. §9 Phase 1 Trial 計画に「Stage 1 のモデル差異(Production=gpt-5.6-luna/Trial=gpt-6-luna)をどう扱うか」の方針を明記(Fable 案: Stage 1 出力は既存 gpt-6-luna データを再利用、Stage 2 以降は gpt-6-luna で Trial、Production 採用時の Stage 1 モデルは routing 判断[ユーザー判断]として分離)。
### 3-4. §10 リスクに「コスト肥大(loop×高単価)」「Cap 超過時の USER_DECISION_REQUIRED 条件」を追加。§11 Opus 論点に「+¥3 Cap 内で自動完結率を最大化する設計の妥当性/より安い代替」を追加(合計 8 個以内)。
### 3-5. §12 に Checkpoint A で提示する項目一覧(ユーザー指定の中間報告項目+コスト 6 項目)を追加。

## 4. 記録・Git
- REPORT §2「コスト章追加(委任_02)」を追記(費用 ¥0/累計 ¥0/残 ¥400、Opus 使用 0 回、probe 結果)。
- SSOT(最小限、1 agent のみ): DECISION_LOG.md に §1 追加指示+§2 Fable 判定を 1 エントリ。OPEN_ITEMS.md OPEN-233 行に「コスト Cap +¥3/記事、Opus model_id 確認待ち」を追記。CURRENT_SPEC.md 不変。
- delegation_log: docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_02.md+check script(FAIL 既知・non-blocking)。
- commit: パス指定 git add(-A 禁止)、Management-ID trailer、ACTIVE_TASK*/RESULT_PACKET*/.env は add しない。競合時 git merge origin/main のみ(reset/amend/rebase/force push/stash/rm/git clean/削除/移動 禁止)。
- 事後確認: git diff --stat で Production ファイル(er003_*/er006_*/er012_*/er019_*)無変更、`.claude/agents/` 無変更。
- 報告(RESULT_PACKET_C233F.md と handback、簡潔に): 【現行ベースライン Checker 費用/記事(構成 call 数付き)】【段階案 α〜δ の追加コスト/記事・固定費/条件付き費・P50/P95/worst・Cap 余裕・到達見込み】【第一候補と理由】【Cap 内で困難な要素があれば明記】【Stage 別計測要件】【Opus 論点(8 個以内)】【ユーザー判断 11 該当有無】【費用 ¥0/累計 ¥0/残 ¥400】【Git(hash・raw URL)】【Status=DESIGN_READY_FOR_OPUS_L2(model_id 確認待ち)】。
