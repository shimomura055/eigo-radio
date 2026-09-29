管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01(委任_04: Opus L2 所見の逐語保存+Phase 1 前の設計是正+Phase 1 計画改訂。**API 呼び出しなし・¥0・Production 非接続・実装なし**)
日付: 2026-09-30。作業ディレクトリ C:\Users\tensh\eigo-radio。

## 0. 前提
- docs/pm/PM_BRIEF.md 固定ヘッダ、docs/pm/PM_GOVERNANCE.md 8節(削除・移動・rm・stash・git add -A・履歴書換 禁止)。
- 対象: docs/pm/design_open233_self_recovery_flow_01.md、OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md、DECISION_LOG.md/OPEN_ITEMS.md(最小限)。参照: er012_e_family_entertainment_two_level_runner_01.py L389-432/L502-523/L654-666、er019_family_x_ja_writer_o_r1_r2_01.py L276-344、er003_v1_en_direct_vfl_01_generate.py L647-688(prior_issues)、er051_open233_checker_trial_variant_01.py L48-131/L188-201、er051_output/open233_checker_trial_01/trial_03_stability_n20/(hormuz V4A 非検出 3 attempt)、docs/pm/negative_claim_candidates_open233_01.md。
- 一時ファイル: docs/pm/ACTIVE_TASK_C233H.md / docs/pm/RESULT_PACKET_C233H.md(新規、commit 禁止)。既存 *_C233A〜G は削除・移動しない。

## 1. 作業 A: Opus 所見の逐語保存
- docs/pm/opus_l2_review_open233_self_recovery_01.md を新規作成し、Opus L2 レビュー #1 全文を一字も変えず保存。冒頭ヘッダのみ付与: 管理ID/日付 2026-09-30/種別 L2 批判的設計レビュー #1/read-only/**runtime evidence: ユーザー指定 `claude-opus-5-5` は Claude Code 2.1.272 未対応で 400(要 2.1.280+、request id req_011CfYW9VqvuUcvEUyfZu1Bs、model sent: claude-opus-5-5)→ 起動時オーバーライドで `claude-opus-5[1m]`(Opus 5、cutoff 2026-05)にて実行。`.claude/agents/opus-consultant.md` の指定は claude-opus-5-5 のまま維持(クライアント更新後に有効)**。

## 2. Fable 判定(Opus 所見に対する採否。設計書 §15「Opus L2 #1 への対応」として記録)
採用(Phase 1 前に設計へ反映):
- A1 Recheck に `prior_issues` を必ず渡し、継続条件=「LEDGER_COMPLIANT かつ all_prior_issues_resolved==True」(現行 Production gate を維持。外す選択は Safety 緩和に当たるため採らない)。
- A2 pre-check 由来の検出は `detected_by="precheck"` を持たせ floor 扱い(Stage 2 LLM で降格不可、Stage 2 をスキップして Stage 3 へ)。ただし FP 率実測(¥0)で高ければ「Stage 2 強制送付(棄却可)」へ弱める分岐を設計に併記し、実測で選ぶ。
- A3 pre-check FP 率の ¥0 測定を Phase 1 の最初に置く(既存 LEDGER_COMPLIANT 記事 28 件へ regex 適用)。
- A4 origin=ja_source の claim に EN 局所 Rewrite を適用しない(JA/EN 乖離を誰も検査しないため。Safety 保守側)。Rewrite 機構は cycle index ではなく origin で選ぶ。JA 側 paired local rewrite(JA 該当 1 文±1+対応 EN 文を同一 hint で局所編集、JA Fact Check 1 call+EN Deviation Check 1 call)を Phase 1 の第一級実装項目へ繰り上げ(設計章を新設: 入力・guard[文体/記号 Gate/段落数 Gate]・Recheck・上限・実装リスク)。案B(JA 全文)は「paired local rewrite が guard 抵触で失敗した場合のフォールバック、記事あたり 1 回」に位置づけ直す。
- A5 cycle 2 の発火条件に「cycle 1 と異なる claim/fact_id」を追加。同一 claim 再 BLOCKING は即 Stage 4。
- A6 §13-6 を式へ書き換え(Stage 2 call 数=claim 数を変数化、案B 実測 ¥4.02 に含まれる再実行分と recheck の二重計上を精査)。JA-origin 比率を 40%→実測 80%(n=5)へ改め根拠明記。BLOCK 率は V4-A 実測後に置換する旨を明記。単一数値(¥2.88/¥3.96)での Cap 判定はしない。
- A7 Stage 4 条件表をコード上の例外型と 1 対 1 対応(JARecheckRequiredError 上限、JAFactCheckStopError[original/r2/symbol]、段落数 retry 枯渇、assert_budget_ok、Stage 1 API/schema 失敗=fail-closed で Stage 2 強制送付または Escalation、all_prior_issues_resolved=False)。
- A8 Stage 2 入力から Stage 1 の explanation/severity/10 flags を**外す**(渡すのは対象 claim・Ledger 全文・source context・段落±1 のみ)。10 flags は Stage 2 外側の floor 判定にのみ使用。ヘッジ語 regex で段落±1 外にヘッジがあれば ±2 へ拡張(決定論的)。
- A9 Stage 2 を instance 単位 1 call に batch 化する案を主案、per-claim を比較対照として Phase 1 で同一入力比較。
- A10 rubric ACCEPTABLE 定義を「Ledger に無い**新規の**固有名詞・数値・時期・主体・因果を一切加えず」へ明文修正。`changed_certainty` は floor に**含める**(B4-d=BLOCKING ラベルと整合、fail-closed 側)。
- A11 rewrite_hint schema に `rewrite_kind: delete | replace_with_ledger_value | narrow_scope` を追加。delete 型は決定論削除を第一候補、局所 Rewrite にも Ledger 全文を渡す。Rewrite 後の機械検証(delete=文字列消滅、replace=Ledger 値の出現)を追加。guard 抵触時は「置換破棄→同一 cycle 内 1 回再試行→既存全文 must-fix retry へフォールバック→Stage 4」。
- A12 prompt caching(Ledger を固定 prefix 化)の受理可否・削減率を Phase 1 で実測する項目に追加。
- A13 §8 測定項目に「Escalation 0 件の内訳(真の解消/QUALITY 通過/all_prior_issues_resolved 未確認/誤 PASS 候補[同一 claim が Recheck で無言消滅])」「Rewrite 解消のうち all_prior_issues_resolved==True で裏付けられた件数」「QUALITY 通過件数・claim 内容」を必須化。Trial 報告テンプレートにも必須項目化。
- A14 Phase 1 実測項目に追加: (1) V4-A の BLOCK 率増分(negative 候補の出典 7 記事を V4-A で再実行、7〜14 call)、(2) er009_changed_actor の V0/V4-A 各 n=15 追加(30 call)、(3) hormuz n=20 で V4-A が見逃した 3 attempt の Stage 1 出力(deviations=[])に対し pre-check/Stage 2 が独立に拾えるか、(4) Stage 2 実単価(per-claim vs batch)、(5) caching 実測、(6) 局所 Rewrite の型別成功率。Stage 1 variant(V4-A vs V0+pre-check)の最終確定は (1)(2) の実測後とし、V0+pre-check を比較対照として Phase 1 に含める(実測前に V0 へ戻さない)。
- A15 Phase 1 ではモデル非依存の構造的結論(prior_issues 併用、pre-check FP、JA/EN 乖離ルール、call 数・batch・caching)を優先して確定させる方針を §9 に明記。Stage 2 評価は V4-A 由来レコードに限定(V2/V3 混在を排除)。
- A16 Production 化後の継続監視案(shadow sampling 5〜10%、QUALITY 週次サンプル、決定論指標)を Phase 2 設計項目として §11-8 の答えに記載(採用判断はユーザー)。
不採用/保留(理由付きで記録):
- cycle 上限を 1 に下げる案(不採用: 実観測パターンに cycle 2 が必要)。Stage 2 入力の Ledger 部分化(不採用: B3 型見逃し)。Stage 2/3 統合(不採用)。
- KPI 再定義(記事単位 0 件→事象単位推定、見逃しゼロ→測定 fixture 0+shadow sampling)、Cap 定義(LLM 費のみか総費か)、QUALITY 通過の Safety 緩和該当性: ユーザー判断事項として Checkpoint A で提示済み(Fable が決めない)。設計書には「現行 KPI 文言のまま進め、事象単位推定と 0 件内訳は追加報告項目として併記」と記す。

## 3. 作業 B: 設計書改訂
上記 A1〜A16 を該当節へ反映(既存節は削除せず改訂・追記、変更箇所に「[委任_04 改訂]」印)。新設: §15(Opus 対応表: 指摘→採否→反映節)、§5-4(paired local rewrite 設計)、§9-1 改訂(Phase 1 実測項目の順序: ①pre-check FP 率 ¥0 → ②hormuz 見逃し 3 attempt 補完実験 → ③V4-A BLOCK 率+changed_actor n=15 → ④Stage 2 単価/batch/caching → ⑤Stage 3 型別 Rewrite → ⑥統合 dry-run、各項目の call 数・費用見積[gpt-6-luna 公式単価×既存実測 token]・Guardrail、合計見積と Phase 予算 ¥400 内の配分)。
Phase 1 実行前チェックリスト(A1〜A13 が設計に反映済みか)を §9-0 として置く。

## 4. 記録・Git
- REPORT §4「Opus L2 #1 と設計是正(委任_04)」追記(runtime evidence、採否要約、費用 ¥0/累計 ¥0/残 ¥400、Opus 使用 1 回)。
- SSOT(最小限、1 agent のみ): DECISION_LOG.md に Fable 判定(§2 採用/不採用/ユーザー判断送り)を 1 エントリ。OPEN_ITEMS.md OPEN-233 行に「Opus L2 #1 完了(claude-opus-5[1m]、5.5 未対応)、Checkpoint A 報告済み、Phase 1 準備中」を追記。CURRENT_SPEC.md 不変。
- delegation_log: docs/pm/delegation_log/2026-09-30_OPEN-233-SELF-RECOVERY-TRIAL-01_04.md+check script(FAIL 既知・non-blocking)。
- commit: パス指定 git add(-A 禁止)、Management-ID trailer、ACTIVE_TASK*/RESULT_PACKET*/.env は add しない。競合時 git merge origin/main のみ。
- 事後確認: git diff --stat で Production ファイル(er003_*/er006_*/er012_*/er019_*)無変更、`.claude/agents/` 無変更。
- 報告(RESULT_PACKET_C233H.md と handback、簡潔に): 【保存先】【A1〜A16 の反映箇所一覧】【paired local rewrite 設計要点と実装リスク】【Phase 1 実測項目の順序・call 数・費用見積・Guardrail】【再計算後のコスト式と暫定値(誤差幅付き)】【USER_DECISION_REQUIRED 該当有無(ユーザー指定 7 条件)】【費用 ¥0/累計 ¥0/残 ¥400】【Git(hash・raw URL)】【Status=PHASE1_READY】。

(Opus L2 レビュー #1 全文は本委任文中でSonnetに提示されたが、逐語保存先は
docs/pm/opus_l2_review_open233_self_recovery_01.md であり、本delegation_log
への二重複製はしない。)

## 5. 実行結果メモ(委任_04実施記録、Sonnet追記)
- 作業A: `docs/pm/opus_l2_review_open233_self_recovery_01.md`を新規作成し、Opus L2レビュー#1全文を一字も変えず保存(冒頭ヘッダのみ付与)。
- 作業B(Fable判定): 採用16件(A1〜A16)・不採用3件(cycle上限1化/Stage2入力Ledger部分化/Stage2-3統合)・ユーザー判断送り3件(KPI判定方法再定義/Cap定義解釈/QUALITY通過のSafety緩和該当性)。
- 作業C(設計書改訂): §3-0/§3-1/§3-3/§3-5/§4-2/§4-3/§4-4/§4-5/§5-1/§5-2/§5-3/§6-1/§8-1/§9-1/§11-8/§12/§12-1/§13-6/§14-3を改訂、新設§5-4(paired local rewrite)/§9-0(チェックリスト)/§15(Opus対応表)。
- 作業D(記録): REPORT §4追記、DECISION_LOG.mdに1エントリ追加、OPEN_ITEMS.md OPEN-233行へ追記。
- 実行コマンド全文: 本委任はAPI呼び出し・シェルコマンド実行を伴わない設計書編集作業のみ(Read/Edit/Writeとgit操作のみ使用、Production/Trial実行コマンドは実行していない)。
