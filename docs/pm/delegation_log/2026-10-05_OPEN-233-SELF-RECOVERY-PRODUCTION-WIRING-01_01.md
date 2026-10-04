# 委任文(全文保存、T-0): OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01 委任_01(2026-10-05)

## 管理ID

`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(委任_01)。前管理ID `OPEN-233-KPI-RECOVERY-REDESIGN-02`(Trial、Status USER_DECISION_REQUIRED→本ユーザー決定で解消)、親 `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: **¥0・SSOT記録のみ(コード変更なし)**。ユーザー正式決定(下記原文)を逐語でSSOTへ記録し、TrialのCloseout(Trial=`VALIDATED`、対象仕様=`APPROVED_FOR_PRODUCTION`)、Cost KPI更新(+¥3単発Cap撤回→monitor/report)、Opus/Fable改善ループ3回Capの運用ルールを`PM_GOVERNANCE.md`へ反映する。Production配線(Gap棚卸し・設計・実装・runtime evidence)は次の委任_02以降で行う。
- 到達上限Status: 対象仕様は`APPROVED_FOR_PRODUCTION`(ユーザー決定済み)。**`PRODUCTION_WIRED`にはしない**(Gate 3=完了条件1〜12すべて達成後のみ)。新管理IDのStatusは`IN_PROGRESS`(Phase: Closeout記録完了→Gap棚卸しへ)。
- Fable補足(逐語記録): 「rep30の実測値はユーザー記載のとおり(29ケース・38 run・Human Review 0・重大見逃し0・平均¥0.573/run・rep24比+¥0.13/run・不要Rewrite 3/14で悪化なし)。worst追加は+¥3.135(safety_A4 s1、1/38 run)であり、ユーザー決定により単発Capは撤回、¥3超は報告・記録対象として本決定記録に残す。」
- 禁止事項: コード変更禁止(Production・Trial両方)。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。ユーザー決定文の要約・改変禁止(逐語)。既に`APPROVED_FOR_PRODUCTION`の個別項目(`OPEN-233-A1-PROD`束)の表記は維持しつつ、本決定で束に合流させる。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01.md`。**委任文は全文そのまま保存(要旨化不可。委任_13の委任ログは要約版で保存されT-0違反だったため、本委任では必ず全文)。** 費用上限: ¥0。

## ユーザー指示(原文、全文。DECISION_LOGへ逐語記録すること)

````
Claude Codeへの指示
管理ID：OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01
目的
OPEN-233品質改善Trialをクローズし、最終rep30で採用された構成を量産Production正式経路へ配線する。
ユーザーは正式に、
今回Trialで織り込まれ、最終rep30構成で有効となっている仕様のうち、量産Productionに未実装のものはすべて正式採用する

と決定した。
したがって対象仕様のStatusは、
APPROVED_FOR_PRODUCTION
とする。
ただし、Gate 3をすべて満たすまではPRODUCTION_WIREDとしてはならない。
Trial Closeout
最終Trial結果：
- 29検証ケース
- 38 run
- Human Review：0
- 重大Fact見逃し：0
- Self-Recovery平均費用：¥0.573/run
- rep24比平均追加：+¥0.13/run
- 不要Rewrite：悪化なし
Trial結果は VALIDATED。
そのうえで今回、ユーザーが正式Production採用を決定したため、対象仕様を APPROVED_FOR_PRODUCTION へ進める。
追加N増しTrialは不要。
今後はProduction量産中に新しい問題が発生した場合に別途改善する。
Cost KPI更新
従来の単発 +¥3/記事Capは撤回する。
今後のCost管理は、
- 平均追加費用を主要KPIとして継続監視
- 1記事/runで¥3を超えた場合は必ず報告・記録
- ¥3超だけを理由に自動STOP・KPI FAILとはしない
とする。
既存の平均費用KPIは変更しない。
F1「品質regen条件を緩めて費用削減」は、最終rep30では不採用なのでProductionへ入れないこと。
Production採用対象
最終rep30の実際の有効構成を正本として、ProductionとのGapを先に棚卸しすること。
少なくとも以下を含む。
- 重大度判定Materiality V7b
- 英語本文だけを修正する方針
- violation spanの引継ぎ
- terminal punctuation差を許容した位置特定
- Checker説明文混入からの決定論的範囲復元
- 不完全spanから完結文への復元
- time系のみAI再確認を許すSafety floor
- 因果等の決定論Safety floor
- Checker重大判定を後段AI1回だけで安易に解除させないSafety構造
- Recheck未解決claimを次cycleへ戻す処理
- 構造要素を空にせず上位Rewriteへ進める処理
- 主体変更Safety guard
- 構造要素のbefore/afterをRecheckへ渡す処理
- Human Review出口の許可リスト化
- 同一箇所のRewrite level引継ぎ
- 元の悪い文章へ戻るRewriteの防止
- span特定失敗時の段階的fallback
- Rewrite上限後の判定専用cycle
- 非構造要素の最終手段処理
- 本文不変の重大判定を後段の揺らぎで解除しない固定
- 同一箇所で修正後も重大なら、同じ箇所のRewrite範囲を一段広げる
- 本文不変・同一箇所で2回非重大が一致済みなら、その判定を再利用
- 同じFactの別箇所を初回判定時に把握する仕組み
- rep30でONだったその他Self-Recovery構成
逆に、Trial中に試したが最終rep30でOFF/REJECTされた候補をProductionへ混ぜないこと。
特に、
- F1品質regen条件変更
- 不採用となった確認役案
- N3′
- G_L
- NORMAL群2-of-2 Trial補助
等を誤って入れないこと。
最終rep30構成とProduction実装の1対1対応表を先に作ること。
Production Wiring必須範囲
Trial runnerだけを移植して完了としてはならない。
確認対象：
- Production正式初回Checker経路
- Rewrite経路
- Recheck
- retry
- fallback
- regeneration
- cycle上限到達時
- span取得失敗時
- API failure時
- Standard / Advanced等、Productionで対象となる全経路
Trial専用er052_*をProductionから暗黙参照する構造は禁止。
Production正式実装として整理すること。
Dangling Reference Check
今回の仕様名・原則・Safety ruleをProduction Prompt/codeへ追加する際、
- CURRENT_SPECに正式仕様があるか
- ユーザー承認済みか
- 初回Production経路にも存在するか
- retry/fallbackだけに孤立していないか
- Trial専用定義へ依存していないか
を全件確認すること。
不足があれば配線前にSSOTを整える。
Runtime evidence
静的コード変更やunit testだけではPRODUCTION_WIREDとしない。
最低限、Production正式pathで実際に発火させ、
- actual model_id
- routing
- Checker
- Stage 2/materiality
- Rewrite
- Recheck
- 必要なSafety guard
- 最終PASS/STOP
- 実費
を確認する。
すべての稀な分岐を実LLMで再現する必要はないが、主要Production flowはruntime evidence必須。稀なSafety分岐はunit/integration fixtureで補完してよい。
受入条件
Production正式pathで以下を確認する。
- Trial最終rep30の採用仕様とProduction挙動が一致
- Human Reviewを安易な出口にしていない
- 重大違反を後段1回の揺らぎで解除しない
- retry/fallback/regenerationでも仕様不整合なし
- 日本語本文を不要に変更しない
- 不要Rewriteが大幅増加しない
- Regression PASS
- integration test PASS
- runtime evidenceあり
- ProductionコードがTrial専用runnerへ依存していない
- ¥3超runがあれば報告
- 平均費用を記録
Opus / Fable改善ループの正式運用ルール
今回有効だった以下を今後の通常ルールとして記録する。
Opusレビュー
→ Fable評価
→ 実装
→ Fable再確認
→ Trial
ループ上限
最大3回までは自律的に実施してよい。
4回目以降が必要な場合は、その都度STOPし、
- 3回までの結果
- 現在残っている問題
- 次回Trialで何を変えるのか
- なぜ改善が期待できるのか
- 費用
をユーザーへ報告する。
ユーザーから明示的に4回目実施の指示を受けた場合でも、5回目以降も同じルールを継続する。
つまり、4回目以降は毎回ユーザーGateを通す。
ユーザーが別途ルール変更を明示した場合のみ例外とする。
このルールをPM_GOVERNANCE等の適切な正式運用SSOTへ反映すること。
SSOT / Closeout
以下を必ず更新する。
- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- OPEN-233 Trial Report
- 必要なPM_GOVERNANCE
- Production wiring report
記録すること：
- Trial=VALIDATED
- ユーザー正式採用=APPROVED_FOR_PRODUCTION
- Gate 3完了後のみ=PRODUCTION_WIRED
- +¥3単発Cap撤回
- ¥3超はmonitor/report
- B′同一箇所昇段承認
- 非BLOCKING判定再利用承認
- Trial改善ループ3回Cap
- 追加N増しなし
- Productionで問題発生時は個別改善
- F1不採用
STOP条件
以下の場合はSTOPして報告。
- Trial最終構成とProduction正式経路に構造的な競合がある
- APPROVED仕様をProduction初回pathへ安全に入れられない
- retry/fallbackとの仕様矛盾
- 新しいProduct判断が必要
- Production runtimeで重大見逃し/Human Reviewが発生
- 平均費用が大きく悪化
- 既存Production品質を明確に悪化させる
- Opus/Fable改善ループが4回目へ入る必要がある
通常の実装バグ・テスト修正・SSOT整合はユーザー判断にせず自律的に解決すること。
完了条件
コードに入れただけでは完了ではない。
以下すべて完了時のみ PRODUCTION_WIRED：
1. Production正式初回path配線
2. retry/fallback/regeneration整合
3. Trial専用依存なし
4. Production runtime evidence
5. Regression / integration PASS
6. actual routing/model確認
7. CURRENT_SPEC更新
8. DECISION_LOG更新
9. OPEN_ITEMS更新/close
10. Git commit/push
11. ユーザー承認内容とProduction挙動一致
12. Dangling Referenceなし
1つでも欠ければ APPROVED_FOR_PRODUCTION のままとする。
````

## 作業

1. **DECISION_LOG.md**(末尾、既存の書式に従う): (a)ユーザー決定`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(2026-10-05)を上記原文のまま逐語記録、(b)Fable補足(上記)、(c)**前管理ID`OPEN-233-KPI-RECOVERY-REDESIGN-02`の委任_02〜_13のFable評価・判断を転記**(設計書§12〜§18-C、各委任ログ、`OPEN_ITEMS.md`該当行の経過、`REPORT`§42〜§62から、各委任の「Fable判断」「採用/不採用」「Opus#11〜#14の指摘と対応」を日付・委任番号付きで時系列に。要約ではなく判断文は逐語で。長くなる場合はDECISION_LOG本体に見出しと判断文、Evidenceパスを置く)、(d)Trial Closeout分類: Opus#11〜#14指摘・Trial候補をREJECTED(確認役案・G_L・N3′・因果floor目録拡張・A1・F1・C・E1・E2・F2・NORMAL群2-of-2[Trial補助、配線しない])/VALIDATED(rep30有効構成)/USER_DECISION(本決定で解消: Cap・B′・再利用)に分類して記録。
2. **CURRENT_SPEC.md** OPEN-233節: 「Trial結果: rep30 VALIDATED(数値)」「ユーザー正式採用2026-10-05: 対象仕様一覧(ユーザー列挙22項目+rep30でONだったその他構成=`KPI_TRIAL_SWITCHES`のON項目を列挙: HANDOFF_MODE=violation_span, VS_MATCH_EXT, VS_EXPLAIN_SPLIT+Q/U-2(1), JA_MODE=english_only, V7b, FLOOR_VERIFY_MODE=time_only, VS_SENTENCE_RESTORE(L6, focus_absentは本文全体判定), CAUSAL_FLOOR known6+issue_actor, STAGE2_SECOND_OPINION(S1), RECHECK_MERGE_UNRESOLVED(N1′), STRUCTURAL_ELEMENT_REWRITE, STRUCTURAL_PAIRS_TO_RECHECK, ACTOR_GUARD_MODE=ag1_strict+related_fact欠落時Ledger全体fallback+同義語表, 件数一致index別集約, prior_issues現行本文, STAGE4_ALLOWLIST, LADDER_LOCATION_CARRY(B′), REWRITE_REVERT_GUARD(A2), SPAN_FALLBACK_CHAIN(D+H-1 carry list), JUDGE_ONLY_CYCLE_AFTER_CAP(G), LAST_RESORT_DELETE(T), MATERIALITY_BLOCKING_PIN, STAGE2_VERDICT_REUSE_NONBLOCKING, STAGE2_SIBLING_LOCATIONS_CYCLE1、degenerate是正)=`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`は完了条件1〜12達成後のみ」「配線しないもの(REJECTED/OFF): F1・確認役・N3′・G_L・NORMAL群2-of-2・STAGE2_DOWNGRADE_VERIFY・TIER0_G_L・RECHECK_BEFORE_AFTER_PAIRS・CAUSAL_FLOOR_VOCAB=inventory」「Cost KPI: 平均追加費用を主要KPIとして継続監視、¥3超runは必ず報告・記録、¥3超のみで自動STOP/FAILとしない、単発+¥3 Capは撤回(2026-10-05)」「残る正当なHuman Review経路(H-3: ①上限後に位置特定不能なBLOCKING ②最終手段後の新規BLOCKING ③構造要素のladder枯渇 ④API失敗)」。`OPEN-233-A1-PROD`束との関係(合流)を明記。
3. **OPEN_ITEMS.md**: 前管理ID行Status→「VALIDATED(rep30)・ユーザー決定2026-10-05でUSER_DECISION解消、Production配線は`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`へ」。`OPEN-233-A1-PROD`行に本決定で追加された項目を合流。新行`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`(Status IN_PROGRESS、完了条件1〜12のチェック欄、次: 委任_02 Gap棚卸し1対1対応表)。OPEN-233本体行Statusを更新。
4. **PM_GOVERNANCE.md**: 11節(ループ上限)に「Opus/Fable改善ループ正式運用ルール(2026-10-05ユーザー決定、`OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01`)」小節を追加: Opusレビュー→Fable評価→実装→Fable再確認→Trial、自律実施は最大3回、4回目以降は毎回ユーザーGate(報告項目: 3回までの結果/残問題/次回変更点/改善期待理由/費用)、ユーザーが4回目を指示しても5回目以降も同ルール、例外はユーザー明示のみ。既存の「Sonnet委任上限」「Opus診断上限」との関係(別カウント)を1行で明記。CLAUDE.mdは編集しない(Fableがユーザーへ報告し、必要なら別途)。
5. **OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md** §63「Trial Closeout(VALIDATED)」: 最終数値、Human Review推移(iter7 7→rep24 2→rep27 3→rep28 3→rep29 3→rep30 0)、Safety-critical 6件の結果、費用(Phase累計¥720.20、rep別)、使用モデル(`gpt-6-luna`のみ、Sol未使用)、Opus#8〜#14の指摘と対応、未解決事項(残穴候補: `blocking_structural_after_ladder`の未検証経路[T無効・T使用済み・cap後T不可・T削除失敗]→配線時に是正)、未処理USER_DECISION(なし: 本決定で解消)、APPROVEDだが未配線(全対象)、未報告Trial(なし)、Dangling Reference(配線時に全件確認)。
6. `docs/pm/REPORT_LEDGER.md`1行。`docs/pm/ACTIVE_TASK.md`を新管理IDの固定ヘッダで書き直し(addしない)。委任_13の委任ログ`2026-10-05_OPEN-233-KPI-RECOVERY-REDESIGN-02_13.md`は要約版のまま残し、末尾に「T-0違反(要約保存)。Fable運用メモ」の注記だけ追記(全文は復元不能のため)。
7. commit/push(明示add: `DECISION_LOG.md`、`CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`docs/pm/PM_GOVERNANCE.md`、REPORT、`REPORT_LEDGER.md`、委任ログ_13注記、委任ログ_01+check.json)。メッセージ: `OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01: Trial Closeout(rep30 VALIDATED)・ユーザー正式採用(APPROVED_FOR_PRODUCTION、PRODUCTION_WIREDはGate 3後)・+¥3単発Cap撤回・改善ループ3回Cap運用ルールをSSOTへ記録(委任_01、¥0)`

## 事前指定Grep一覧+追記位置・更新位置の手順

- `DECISION_LOG.md`: 末尾(Grep `OPEN-233-KPI-RECOVERY-REDESIGN-02`で前回ユーザー指示エントリの書式を参照)。全文Read禁止。
- `CURRENT_SPEC.md`: Grep `OPEN-233` → 該当節のみ範囲Read・更新。全文Read禁止。
- `OPEN_ITEMS.md`: Grep `OPEN-233`(本体行・`OPEN-233-A1-PROD`・`KPI-RECOVERY-REDESIGN-02`行)。全文Read禁止。
- `docs/pm/PM_GOVERNANCE.md`: Grep `11` 節見出し(`ループ上限|Opus独立技術レビュー|11-3`)→該当節末尾に小節追加。
- 設計書`docs/pm/design_open233_kpi_recovery_02.md` §12〜§18-C(Fable評価の転記元)、委任ログ`docs/pm/delegation_log/2026-10-0{4,5}_OPEN-233-KPI-RECOVERY-REDESIGN-02_{02..13}.md`(Fable判断ブロックのみGrep `Fable判断|Fable評価|Fable照合`)。
- REPORT §42〜§62の見出しのみ(Grep `^## §`)。

## 実行コマンド全文

T-0: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-SELF-RECOVERY-PRODUCTION-WIRING-01_01.md_check.json
Git: `git status --porcelain`で対象確認→明示`git add <files>`→commit→`git push origin main`→`git log --oneline -1`。

## 報告(RESULT_PACKET項目)

(1)結論10行以内、(2)SSOT別の更新箇所(行範囲)とStatus表記、(3)DECISION_LOG転記の網羅(委任_02〜_13各1行で何を転記したか)、(4)REJECTED/VALIDATED/USER_DECISION分類表、(5)PM_GOVERNANCE小節の全文、(6)T-0・commit・push・raw URL(DECISION_LOG/CURRENT_SPEC/OPEN_ITEMS/PM_GOVERNANCE/REPORT)、一覧外Read、確認/推測の区別、(7)Fableへの論点(委任_02 Gap棚卸しへ進めるか、SSOT上の不整合があれば)。
