# conditions_diff: 過去Trial群と今回(B3 Trial)の生成条件・測定条件の差分表(OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 委任_B1、2026-10-07、¥0・read-only)

注: 各セル末尾の[ ]は出典(REPORT=`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`の§番号、他は5節のパス)。「不明」=今回読んだ範囲で確認できず。解釈は書かない。
REPORT内の件数単位は「記事」「run」「fact」が混在。各行のN列で明記。

行ID: B3-V0=今回(現行B3) / B3-V1356=今回の構造変種 / E2E-従来=E2E_02の従来版 / E2E-P2=E2E_02のP2版 / STW=工程別NG監査(再評価のみ、生成なし) / MX-a=MX T0M0,T0M1,T1M0,T1M1,T2M0 / MX-b=MX T2M1(P2相当) / ENT-P1 / ENT-P2 / RB=ROLLBACK 01/02 / CHK=CHECKER-FLOOR 9/20 / R30=rep30

## 1. 生成側の比較表

| 行 | Trial/節 | B3 brief種別 | briefへ追加した情報(種類と量) | Writer本数・prompt版 | Checker | Rewrite/Recheckループ | EN生成 | テーマ | N | 生成不能・Gate STOPの扱い | 費用 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B3-V0 | B3-BRIEF-STRUCTURE §100 | 現行(無変更、対照) | 追加なし。ledgerはpolysemy_trial_02のcontrol台帳。notes折込の有無・行数は不明 [PLAN.md L8, design_01 §1] | Writer1本/brief(w1)、DEV runner `er052_open233_polysemy_nb_dev_01.py` phase1、prompt版は不明 | なし(`--no-checker`) | Writer内部のR0/R1/R2修正工程のみ。Checker Rewrite/Recheckなし。上限回数は不明 | あり(b1b、phase2) | meta/hormuz/space_weapons | 12記事(brief b1〜b4×3テーマ) | WRITER_GATE_STOP(Advanced deviation MAJOR未解決/JA_RECHECK_REQUIRED/JA_FACT_CHECK_STOP)は「記事生成不能」として評価母数から除外、件数は別集計(V0は0/12)、Gate回避なし [§100-3, design_01 5-A6] | 条件別内訳は不明。段階2 ≈¥379、段階1 ¥55.49 [§100-8] |
| B3-V1356 | 同上 | V1(主体・対象保持)/V3(V1+単一因果)/V5(V3+未提示明記)/V6(最大簡潔、逆方向対照)。V2はWriter段なし | B3指示文のBLOCKを1つ追記(Note転記ではない)。V6はbrief省略率0.07。V5は未提示明記が20項目中10命中(V0は1) [design_01 §1, §100-4] | V0と同じ | なし | V0と同じ | あり | 同上 | V1 12/V3 11/V5 8/V6 12(評価記事数) | Gate STOP: V3 1/12、V5 4/12(評価母数から除外、V5は母数減で選択バイアスの恐れ)、V1/V6 0 [§100-3, §100-7] | 同上 |
| E2E-従来 | E2E_02 §94(比較行) | TRIAL-04 Control rep1(Noteなし台帳) | 追加なし(brief長はP2の約半分) [§94-5] | 1本/run、DEV runner。prompt版は不明 | あり(41スイッチ構成) [§94-1] | あり。Checker Rewrite/Recheck(cycle 1〜3、Rewrite有3/無2) [§94-3] | あり | meta/hormuz/space_weapons/sewer/ai_control 各1 | 5(各テーマrep1) | 記載なし(不明) | 不明(TRIAL-04側) |
| E2E-P2 | E2E_02 §94 | P2台帳(全factにnotes付与)+転記規則修正版runner | 全fact一律Note「注意: <既存notes> / 注意(多義): <文言>」を台帳へ付与(空notes 0)。brief転記=notes全体を省略・分割せず該当fact直後へ。brief長は従来の約2倍。両Note到達10/10 [§93-1, §94-1, §94-5] | 1本/run、DEV runner(転記規則のみTrial専用修正)。prompt版は不明 | あり(従来と同41キー一致) [§94-1] | あり(cycle 1〜5、Rewrite有 7/10 run) [§94-3] | あり | 5テーマ | 10(各テーマ2rep) | sewer rep2 phase1 JA_FACT_CHECK_STOP/LEDGER_DEVIATION→同枠1回再実行して再実行版を採用(除外ではなく再実行) [§94-2] | ≈¥110.4(Checker ¥52.7含む) [§94-6] |
| STW | STAGEWISE-NG-AUDIT §95 | 生成なし(E2E-従来5+E2E-P2 10の再評価) | - | - | E2E各行のCheckerをそのまま使用 | 同左 | - | 5テーマ | 15本 | - | ¥0 |
| MX-a | NOTE-TRANSFER-MATRIX §97 | 固定brief(テーマごと1本固定)、T0転記なし/T1要約転記/T2逐語転記×M0/M1のうちT2M1以外の5セル | brief本文は条件間で固定、転記の有無・形式・多義語注意の有無のみ変更 [§97-1] | 各セルN=2、DEV runner(固定brief開始オプション)、prompt版は不明 | なし(ENのb1bが最終) | Writer内部R0/R1/R2のみ。Checker loopなし | あり(EN完成33/STOP3→再実行で36/36) | meta/hormuz/sewer | 各セル6記事(3テーマ×2)、全36 | STOP3枠のうち2枠は各1回再実行して完走、hormuz T0M0 rep1はdriver誤判定で失敗扱い→1回目成果物を採用 [§97-2] | 全36 ≈¥268.8、セル別内訳は不明 |
| MX-b | 同上 | 固定brief、T2(逐語転記)×M1(多義語注意あり)=P2相当 | MX-aと同じ | 同上 | なし | なし | あり | 同上 | 6記事 | 同上 | MX全体に含む |
| ENT-P1 | ALLFACT-NOTE-ENT §93 | nb variant、control台帳の全factへ「 / 注意(多義): 文言」付与 | 全factにNote末尾付与。briefは14行、選択3factすべて転記3/3 [§93-1, -2] | 1本、DEV runner、prompt版は不明 | あり(自動Checker) | あり(3cycle、Rewrite1回、RESOLVED_REWRITE_THEN_DOWNGRADE) | あり | meta | 1 | 記載なし(不明) | P1+P2+pairwise合計≈¥50.2(pairwise ¥29.0) |
| ENT-P2 | 同上 | nb variant、全factに「注意: <既存> / 注意(多義): 文言」 | briefは14行、既存notes3行のみ転記、多義注意0/3(行内後半脱落)=従来notes転記相当 [§93-2] | 同上 | あり | あり(1cycle、Rewriteなし) | あり | meta | 1 | 記載なし(不明) | 上に含む |
| RB | ROLLBACK-MINIMAL-NOTE §91/§92 | nb variant(`OPEN233_B3_VARIANT=nb`)、一般的な多義注意1文をbriefへ転記 | 最小Note1文(逐語、対象語を指さない)。brief転記6/6 [§91-1, §92-1] | 1本/rep、DEV runner `--phase phase1`、`--budget-jpy 8`、prompt版は不明 | 不明 | 不明(Writer内R0〜R2はあり) | 不明(§92は`--phase phase1`のみ記載) | meta(HC-012のみ) | §91 N=5(rep2〜6)+rep1参考。§92 開始10/完了7/停止3 | 停止3本(JA_FACT_CHECK_STOP/LEDGER_DEVIATION)は集計除外、代替rep17/18/19は集計外 [§92-2, §92-3b] | §91 rep2〜6 ¥21.14。§92 合計推定≈¥61.8(上限¥60超過) |
| CHK | CHECKER-FLOOR-PRODUCTION-E2E-01 §81 | Production初回path含むE2E(fresh)。brief種別は不明 | 不明 | 1本/run、prompt版は不明 | あり(新仕様: 数字のみfloor+再分類+S1、承認構成) | あり(Rewrite 6件/4 run、Human Review 0) | 不明 | meta_adv/meta_std/hormuz_adv/hormuz_std/B3/neg1/neg2/neg3/neg7(std/adv/negの意味は不明) | 9 run(計画20、11は停止) | failed/aborted/skipped 0 [§81-1] | ¥31.519(平均¥3.502/run) |
| R30 | KPI-RECOVERY-REDESIGN-02 §62 | 不明(Stage 1はfrozen再利用31 run/V0差替え3 run/fresh 3 call[4 run] [§63遡及注記]) | 不明 | 該当なし(Stage 1出力の凍結再利用) | Checker+Self-recovery(KPI構成、gpt-6-luna、V7b) | あり(Rewrite+Recheck、cycleは最大3以上実測、S1/L6/N1′/B′等) | 不明 | 29ケース(テーマ名は不明) | 29 instance・38 run | STAGE4/Human Review 0、Guardrail未到達 | rep30 ¥21.79、rep30a ¥3.02 |

## 2. 測定側の比較表

| 行 | rubric名・版(path) | 重大・軽微の定義(1行) | 「保留」区分 | 評価者(単独/人間/盲検) | 評価単位 | 評価対象の工程 | 台帳参照 | 重大NG件数 | 軽微NG件数(1記事当たり) | 評価者間一致の記録 |
|---|---|---|---|---|---|---|---|---|---|---|
| B3-V0 | `docs/pm/b3_trial_01/eval_rubric.md`(MATRIX継承、基準は直前監査と同一) | 重大=意味が変わり誤解(主体対象入替/方向逆転/台帳外断定/否定反転)、軽微=不正確・過剰断定・曖昧・範囲曖昧・軽い具体化。同一誤りは同一工程1件 | あり(pending、集計外。境界は軽微計上しnotes記録) | 評価者インスタンス(Sonnet実行層)による盲検(条件非開示・匿名コード・MAP開封は全員分出揃い後)、人間確認なし、複数評価者に交互配分。brief_reviewは別インスタンス [blinding.md, §100-4, §100-7] | 記事×NG項目(同一誤りはJA/EN共通ID)。★factは3分類 | s1(JA R2)・s2(EN b1b)・R0→R2退行。主指標は②EN | あり(`polysemy_trial_02/ledgers/<slug>/control/.../verified_fact_ledger.txt`、notes含む) | 0(12記事) | 9(0.75)。保留4(0.33)、退行1(0.08) | 運用差の記述あり(SUMMARY_STAGE2 ⑥)。評価者差を分離する統計は取っていない |
| B3-V1356 | 同上 | 同上 | あり | 同上 | 同上 | 同上 | あり | V1 0/V3 0/V5 0/V6 0 | V1 10(0.83)/V3 8(0.73)/V5 3(0.38)/V6 6(0.50)。保留 V1 0.17/V3 0.45/V5 0.00/V6 0.33、退行 V6 0.42 | 同上 |
| E2E-従来 | 実施時は`docs/pm/allfact_e2e_02/eval_template.md`(Fact整合7区分件数+★3分類+JA→EN意味変化+Checker項目)。重大/軽微の分類は§95で再集計 [§94-3, §95-1] | 評価時は7区分の「Fact誤り件数」(重大/軽微の分離なし)。§95再集計で重大=意味が変わり誤解/軽微=不正確・過剰断定・曖昧・軽い具体化 | §95で保留1+境界4が別記(従来分は境界2) | Sonnet実行層の単独判定・人間確認なし。盲検の記載なし(不明) [§95-1, STAGEWISE §0] | 評価時はFact誤り件数、§95で同一誤り1件のNG項目 | JA最終R2+EN最終(評価時は3系統で⑤定義混在、§95で⑤a=EN最終/⑤b=EN+JAのみ残存に統一) | あり(台帳全文、watchlist) | ⑤a 0/⑤b 0(5本) | ⑤a 19(3.8)、⑤b 21(4.2)、①JA 18(3.6) | 記録なし(不明) |
| E2E-P2 | 同上(eval_template、E_*.md、summary_*.json) | 同上 | 保留(meta r1のRewrite挿入文「That」=集計外)など | 同上(盲検の記載なし) | 同上 | 同上(JA R2も評価対象。JAのみ残存は⑤bで計上) | あり | ⑤a 1/⑤b 4(10本)。①JA 4、②EN Rewrite前 5 | ⑤a 52(5.2)、⑤b 57(5.7)、①JA 49(4.9) | 記録なし(不明)。Checker判定ぶれの記述のみ [§94-5] |
| STW | `STAGEWISE_SUMMARY.md` §0。重大/軽微は既存NG台帳のSonnet単独判定を再判定せず再集計 | 同上 | 保留1+境界4 | 既存台帳の判定をそのまま使用(再判定なし) | NG項目(同一誤り同一工程1件) | ①JA最終/②EN Rewrite前/③Rewrite後/④Checker最終cycle生件数(参考、NG実数ではない)/⑤a/⑤b | 各台帳に依存 | E2E行の合算(従来0、P2 ⑤a 1/⑤b 4) | 同上 | 記録なし |
| MX-a | `docs/pm/note_transfer_matrix_01/eval_rubric.md`(直前監査と同一基準、変更なし) | 同上 | あり(保留16件は集計外、うちminor寄り少数) | Sonnet実行層の単独判定・人間確認なし。盲検の記載なし(不明) [§97-2] | 記事×NG項目 | ①JA R2、②EN(b1bが最終)、R0→R2退行 | あり | EN 0.17/記事(T0M0のみ、1件)、JA 0 | EN: T0M0 0.67/T0M1 0.67/T1M0 0.33/T1M1 0.67/T2M0 0.67 | 記録なし(不明) |
| MX-b | 同上 | 同上 | 同上 | 同上 | 同上 | 同上 | あり | EN 0、JA 0 | JA 1.33/EN 1.67(福島県型除外でEN 1.33) | 記録なし |
| ENT-P1 | `er052_output/open233_meta_allfact_note_ent_01/eval/E_allfact_ent_01.md`(rubric版は不明) | HC-012の3値(正しい/曖昧/重大誤読)+pairwise。重大/軽微の分類は不明 | 不明 | 単一LLM評価、N=1、pairwise順序入替2回 [§93-4] | HC-012相当文1箇所+pairwise | JA R2とEN | あり(HC-012のnotes) | 誤読0(HC-012) | 分類なし(不明) | なし(単一LLM、N=1) |
| ENT-P2 | 同上 | 同上 | 不明 | 同上 | 同上 | 同上 | 同上 | 誤読0 | 分類なし(不明) | なし |
| RB | `er052_output/open233_meta_rollback_minimal_note_01/eval/E_rollback_minimal_note.md`、`..._trial02.md`(rubric版は不明) | HC-012相当文のみ3値(正しい/曖昧/誤読) | 不明 | 不明(評価者区分の記載なし) | 1文(HC-012) | R0/R1/R2(§91はR0〜R2、§92はR2中心) | あり(HC-012のnotes) | 誤読0/12(rep9を重大扱いなら1/12) | 軽微数の記録なし。R2曖昧は§91 4/5、§92 5/7 | 不明 |
| CHK | 集計=`er052_output/open233_prod_e2e_02/report_final/`(rubric正本pathは不明) | 事後ラベル(問題なし/軽微/重大/判断不能)+true_critical Y/N/UNDECIDABLE。重大の定義はgold依存(詳細不明) | UNDECIDABLE 1件 | Sonnet推測ラベル(3 worker)+Fable突合、ユーザー未確認、盲検ではない [§81-1] | claim単位(候補単位)と後段判定単位 | Checker各cycleと最終本文の見逃し判定 | あり(Ledger一致で判定) | true_critical=Y 4件、最終本文残存の重大見逃し1(meta_adv HC-012) | ラベル軽微8件(123判定中、claim単位。記事当たり値なし) | 記録なし |
| R30 | 設計書・`docs/pm/opus_l2_review_open233_*`(KPI定義)。重大見逃しは旧/新/text_pattern 3定義 | Safety-critical定義(旧/新/text_pattern)で最終本文に残存した重大 | 不明 | 自動集計+Fable照合、人間確認の記載なし | instance/claim単位(Human Review、cycle) | Checker/Rewrite後の最終本文残存+Human Review・費用KPI | あり | 重大見逃し0(旧0/新0/text_pattern0)、Human Review 0 | NG件数でなくKPI(該当なし) | 記録なし |

## 3. 機械的に読み取れる差分(事実のみ、解釈なし)

### 3-1. 今回(B3系)だけ異なる条件
1. 評価が盲検(条件非開示・匿名コード・MAP後開封・複数評価者に交互配分・brief_reviewは別インスタンス)。他Trialに盲検の記載は今回読んだ範囲で見当たらない(不明)。
2. 記事生成不能(Writer内部Gate STOP)を評価母数から除外し件数を別集計(5/60、V5 4/12)。E2E-P2(sewer r2)は再実行して採用、MXは再実行して36/36完走。
3. 操作対象がB3 briefのprompt指示文(V1/V3/V5/V6)で、台帳notesの付与・転記は操作しない(V0は現行briefのまま)。ENT/E2E-P2/MXは台帳notes・転記規則を操作。
4. brief4本×Writer1本(b1〜b4)/テーマ/条件で記事55(V0は12)。MXは各セル6、E2Eは各テーマ1〜2。
5. 判定ルール(テーマ差≥0.5件/記事かつb1〜b4多数同符号、48判定)を事前登録。他Trialに同種の事前登録の記載は未確認(不明)。
(共通点: Checkerなしかつ同一rubric基準はMXと同じ。V0単独はMXと同基準・同Checkerなし)

### 3-2. P2系(E2E-P2、ENT-P1/P2、MX-bのT2M1)だけ異なる条件
1. 台帳notesを全factへ一律付与(「注意: <既存> / 注意(多義): <文言>」、空notes 0)。E2Eではbrief長が従来の約2倍。
2. brief転記規則の最小修正(notes全体を省略・分割せず該当fact直後へ)をrunner(Trial専用)に適用(E2E-P2のみ)。
3. E2E-P2はChecker+Rewriteループありで、Checker対象外のJA R2まで評価に含め⑤bとしてJAのみ残存を計上(重大4/10本)。MX-bはCheckerなしで重大0・EN軽微1.67/記事。
(同じP2相当でもChecker有無が異なる: E2E-P2=有、MX-b=無)

### 3-3. rubric(測定)が異なるTrial
- B3/MX/STW: 基準は同一文言(STAGEWISE §0由来)。B3はMXのrubricを継承(変更は条件・★fact・ID形式・brief_review追加のみ)。
- E2E_02元評価: `eval_template.md`(Fact整合7区分件数中心、重大/軽微の分離なし、3系統で⑤定義が不統一)。STWで再集計して統一(⑤a/⑤b)。
- ENT/RB: HC-012の3値のみ、NG件数集計なし(rubric版は不明)。
- CHK: claim単位の事後ラベル(Sonnet推測+Fable突合、ユーザー未確認)、判断不能区分あり。
- R30: KPI(Human Review/重大見逃し3定義/費用)でNG件数ではない。

### 3-4. 同一基準の数値の並び(事実のみ)
| 条件 | 評価記事数 | 重大NG | 軽微NG/記事 | 工程 |
|---|---|---|---|---|
| B3-V0 | 12 | 0 | 0.75 | ②EN(Checkerなし) |
| B3全55 | 55 | 0 | V0〜V6で0.38〜0.83 | ②EN(Checkerなし) |
| MX全36 | 36 | 1(ENのみ、T0M0 rep2) | 0.78 | ②EN(Checkerなし) |
| MX T1M0 | 6 | 0 | 0.33 | ②EN |
| MX T2M1 | 6 | 0 | 1.67 | ②EN |
| E2E-従来 ⑤a | 5 | 0 | 3.8 | EN最終(Checkerあり) |
| E2E-P2 ⑤a | 10 | 1 | 5.2 | EN最終(Checkerあり) |
| E2E-従来 ②(Rewrite前) | 5 | 0 | 4.2 | ②EN(Checker前) |
| E2E-P2 ②(Rewrite前) | 10 | 5 | 5.6 | ②EN(Checker前) |

## 4. 不明セル一覧と埋めるために読むべきファイル候補

| # | 行 | 列 | 候補ファイル |
|---|---|---|---|
| 1 | 全Trial行(約11行) | Writer prompt版 | `er052_open233_polysemy_nb_dev_01.py`、各Trial `runs/manifest.json`、`DECISION_LOG.md`の各Trial追補 |
| 2 | B3-V0 | notes折込の有無・行数(control台帳notes、V0 briefへの転記) | `er052_output/open233_polysemy_trial_02/ledgers/*/control/research_ledger/verified_fact_ledger.txt`、`er052_output/open233_b3_trial_01/eval/STAGE1_BRIEF_CHECK.md`(notes 12字率列) |
| 3 | B3 | Writer内R0〜R2の修正上限 | `er052_open233_polysemy_nb_dev_01.py` |
| 4 | B3-V0/V1356 | 条件別費用 | `er052_output/open233_b3_trial_01/runs/manifest.json` |
| 5 | E2E-従来 | STOP扱い・費用 | `er052_output/open233_polysemy_trial_04/`、REPORT TRIAL-04節 |
| 6 | ENT-P1/P2 | STOP扱い | `er052_output/open233_meta_allfact_note_ent_01/cost.json`、`E_allfact_ent_01.md` |
| 7 | RB | Checker有無・EN生成有無・評価者区分・rubric版・保留 | `er052_output/open233_meta_rollback_minimal_note_01/eval/E_rollback_minimal_note*.md`、`runs/manifest.json` |
| 8 | CHK | B3 brief種別・EN有無・std/adv/negの意味・重大定義の正本・Writer prompt版 | `er052_output/open233_prod_e2e_02/report_final/`、REPORT §80 |
| 9 | R30 | B3 brief種別・EN有無・テーマ・評価者区分・保留区分 | `er052_output/open233_self_recovery_flow_runner_01_rep30/summary_kpi_01.json`、`docs/pm/rep30_stage1_provenance_01.md` |
| 10 | E2E-従来/P2、MX、ENT、RB | 盲検の有無(評価者への条件開示) | `docs/pm/delegation_log/2026-10-07_*_D1.md`、`docs/pm/note_transfer_matrix_01/eval_assignment.md` |
| 11 | E2E/MX/ENT/RB/CHK/R30 | 評価者間一致の記録(「記録なし」は今回読んだ範囲に記述なし) | 各eval SUMMARY、`E_*.md`のnotes |
| 12 | ENT/RB | 軽微NG件数・保留区分 | `E_allfact_ent_01.md`、`E_rollback_minimal_note*.md` |

不明セル数: 表中の「不明」表記は約45セル(1節約25、2節約20。「記録なし」を含めると約55)。

## 5. 出典一覧
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §62(rep30)、§63(遡及注記)、§81(CHECKER-FLOOR 9/20)、§91〜§95、§97、§100
- `er052_output/open233_b3_trial_01/eval/SUMMARY_STAGE2.md`(⑥評価者間運用差)、`.../PLAN.md`、`.../eval/STAGE1_BRIEF_CHECK.md`
- `docs/pm/b3_trial_01/{design_01.md,eval_rubric.md,blinding.md}`、`docs/pm/b3_brief_structure_hypothesis_01.md`
- `er052_output/open233_allfact_note_e2e_02/eval/SUMMARY.md`、`.../eval/stagewise/STAGEWISE_SUMMARY.md`、`docs/pm/allfact_e2e_02/eval_template.md`
- `docs/pm/note_transfer_matrix_01/eval_rubric.md`
