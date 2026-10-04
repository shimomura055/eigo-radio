## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_02)。親 `OPEN-233-SELF-RECOVERY-TRIAL-01`、前管理ID `OPEN-233-KPI-RECOVERY-REDESIGN-02`。**並行タスクあり**: 委任_01(SSOT記録: `DECISION_LOG.md`/`CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`PM_GOVERNANCE.md`/REPORT/`REPORT_LEDGER.md`/`ACTIVE_TASK.md`/`RESULT_PACKET.md`を編集中)。衝突回避のため、本委任は**それらのファイルを一切編集せず、git commit/pushも行わない**(次委任でFableがまとめてaddさせる)。報告は委任完了時のhandback本文で行い、`RESULT_PACKET.md`には書かない。

## 性質/到達上限Status/禁止事項

- 性質: **¥0・調査と文書作成のみ(コード変更なし)**。ユーザー正式決定(2026-10-05、全文は委任_01でDECISION_LOGに記録中。要旨: Trial=VALIDATED、rep30有効構成をすべて`APPROVED_FOR_PRODUCTION`、Gate 3[完了条件1〜12]達成後のみ`PRODUCTION_WIRED`、Trial専用`er052_*`をProductionから暗黙参照する構造は禁止、OFF/REJECTED候補を混ぜない)に基づき、**「最終rep30の実際の有効構成」と「量産Production実装」の1対1対応表(Gap棚卸し)**を作る。ユーザー指示: 「最終rep30構成とProduction実装の1対1対応表を先に作ること。」
- 到達上限Status: 文書のみ。Status変更なし。
- 禁止事項: コード変更禁止(Production・Trial両方)。上記SSOT・一時ファイルの編集禁止。commit/push禁止。`git add -A`/`stash`/`amend`禁止。Trial専用の候補でrep30でOFF/REJECTEDのもの(F1品質regen条件変更・確認役`STAGE2_DOWNGRADE_VERIFY`・N3′`RECHECK_BEFORE_AFTER_PAIRS`・G_L`TIER0_G_L_ENABLED`・NORMAL群2-of-2`STAGE2_NORMAL_TWO_OF_TWO`・`CAUSAL_FLOOR_VOCAB=inventory`・A1・C・E1・E2・F2)は対応表の「配線しない」欄に明記し、配線対象に含めない。
- 費用上限: ¥0。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、check_delegation_prompt.pyを実行する。結果をhandback本文に記録。
T-2: 本委任はTTSを伴わない。
T-3: 費用上限はGuardrail。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_02.md`。

## ユーザー指示(原文、該当部分)

Production採用対象: 最終rep30の実際の有効構成を正本として、ProductionとのGapを先に棚卸しすること。少なくとも以下を含む。
重大度判定Materiality V7b / 英語本文だけを修正する方針 / violation spanの引継ぎ / terminal punctuation差を許容した位置特定 / Checker説明文混入からの決定論的範囲復元 / 不完全spanから完結文への復元 / time系のみAI再確認を許すSafety floor / 因果等の決定論Safety floor / Checker重大判定を後段AI1回だけで安易に解除させないSafety構造 / Recheck未解決claimを次cycleへ戻す処理 / 構造要素を空にせず上位Rewriteへ進める処理 / 主体変更Safety guard / 構造要素のbefore/afterをRecheckへ渡す処理 / Human Review出口の許可リスト化 / 同一箇所のRewrite level引継ぎ / 元の悪い文章へ戻るRewriteの防止 / span特定失敗時の段階的fallback / Rewrite上限後の判定専用cycle / 非構造要素の最終手段処理 / 本文不変の重大判定を後段の揺らぎで解除しない固定 / 同一箇所で修正後も重大なら、同じ箇所のRewrite範囲を一段広げる / 本文不変・同一箇所で2回非重大が一致済みなら、その判定を再利用 / 同じFactの別箇所を初回判定時に把握する仕組み / rep30でONだったその他Self-Recovery構成。
逆に、Trial中に試したが最終rep30でOFF/REJECTされた候補をProductionへ混ぜないこと。
最終rep30構成とProduction実装の1対1対応表を先に作ること。
Production Wiring必須範囲: Trial runnerだけを移植して完了としてはならない。確認対象: Production正式初回Checker経路 / Rewrite経路 / Recheck / retry / fallback / regeneration / cycle上限到達時 / span取得失敗時 / API failure時 / Standard / Advanced等、Productionで対象となる全経路。Trial専用er052_*をProductionから暗黙参照する構造は禁止。Production正式実装として整理すること。
Dangling Reference Check: 今回の仕様名・原則・Safety ruleをProduction Prompt/codeへ追加する際、CURRENT_SPECに正式仕様があるか / ユーザー承認済みか / 初回Production経路にも存在するか / retry/fallbackだけに孤立していないか / Trial専用定義へ依存していないか を全件確認すること。不足があれば配線前にSSOTを整える。

## 作業: `docs/pm/production_wiring_gap_open233_01.md`(新規)

§1 rep30有効構成の正本: `er052_open233_self_recovery_flow_runner_01.py`の`KPI_TRIAL_SWITCHES`/`apply_kpi_trial_switches`と、rep30スクリプト`er052_open233_self_recovery_flow_runner_01_rep30_full_01.py`が実際に渡した設定、rep30出力`summary_kpi_01.json`/`summary_rep30_new_01.json`の構成記録から、rep30で実際に有効だった全スイッチ・定数・モードを列挙(名前、値、runner内の実装関数名と行番号、設計書§、Opusレビュー#、ユーザー承認の有無とDECISION_LOG上の根拠)。ユーザー列挙22項目との対応を1列で示す。OFF/REJECTED候補は別表「配線しない」に列挙。
§2 Production実装の現状(read-only): 初回Checker経路(er003 build_prior_issues_instruction ~L678・件数一致式L827・causal_strength等)、Rewrite経路(er010 locate_target_sentence等)、Recheck/再検査(er012)、retry/fallback/regeneration(er009*/er019*)、Standard/Advanced分岐、cycle上限・span取得失敗・API failure時の現行挙動、既存Stage2/materiality(er052_open233_self_recovery_stage2_production_01.pyの位置づけ)、OPEN-233-A1-PROD束の現状。各経路で挿入位置/現行のHuman Review倒れを行番号付きで。
§3 1対1対応表: 行=§1各項目、列=Production現状、Gap種別(A純移植/B構造適合/C新設/D同等実装あり)、影響経路、Trial専用依存、Dangling Reference Check 5項目、runtime evidence主要flowかfixture補完稀分岐か。
§4 配線方針案(実装しない): module化案vs分散案、各経路挿入点と許可リスト4理由への集約、構造的競合候補(競合/非競合/要設計)、blocking_structural_after_ladder残穴、runtime evidence計画案(新規記事テーマはユーザー選択)、Regression/integration test、工数リスク、推奨配線順序。
§5 Fableへの論点: STOP条件候補、Opus論点(条件A/C)、ユーザー判断点。

## 報告(handback本文)

(1)結論10行以内、(2)§1〜§4要点、(3)STOP条件・Opus論点・ユーザー判断候補、(4)T-0結果、作成ファイルパス、一覧外Read、確認/推測の区別。

(注: 本ファイルは委任文の保存用に、長大な固定ブロック定型文の一部を要約して記録している。)
