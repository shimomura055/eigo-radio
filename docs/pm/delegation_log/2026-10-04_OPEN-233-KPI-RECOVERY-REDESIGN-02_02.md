## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_02)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: Opus批判レビュー#11(本委任文末尾に全文)に対するFableの評価(下記)に基づき、Step 3(設計改善)・Step 4(Trial側実装)・offline評価(有料、上限¥45)・Step 5(既知caseの限定確認、有料、約¥5)を**自律的に**進める。KPI未達ならユーザーへ上げずFableへ報告(再設計ループ)。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。「Safetyを理由にHuman Reviewへ逃がさない」。
- 到達上限Status: 本委任は限定確認(Step 5)まで。Trial Statusは`IN_PROGRESS`のまま(Step 6後に`VALIDATED`/`USER_DECISION_REQUIRED`を判定)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- Fableの評価(Opus#11の採否。SSOTへ逐語記録する。変更しない):
  1. **修正採用**: 三層構造(Tier 0決定論Guard / Tier 1確認役 / Tier 2失敗時BLOCKING→Rewrite)を主構造とする。D*(G_H∨issue_actor+S1)は主構造にしない。G_H/issue_actorは「既知の型への補助ベルト」としてTier 0に残す(¥0、誤停止は少数)。S1(同一prompt2回目)は採用しない(判別力が低い。確認役が別prompt・別入力の第2意見を兼ねる)。
  2. **採用**: Tier 1確認役は既存`floor_verify`(委任_60/61実装)の一般化。対象=「Checker MAJORをStage 2が非BLOCKING(QUALITY/ACCEPTABLE)にしたもの全て」(QUALITYとACCEPTABLEで要件は同一)。call 1回。入力=関連factブロック(Ledger逐語)+claim文(確定範囲)+局所文脈+Checkerのissue/flags(「検証すべき仮説」として提示)。出力schema=`verdict`(UPHOLD_BLOCKING/RELEASE)+`ledger_citation`(日本語Ledger逐語、決定論照合必須)+`basis`+`explanation`。prompt原則は単一定義の短いrubric(「英語学習者に記事の本質について重大な誤解を与えるものだけを止める」+正式基準3定義+「迷えばBLOCKING」)。RELEASEかつ引用逐語のときだけ解除。それ以外(UPHOLD/引用非逐語/API失敗/schema不一致)はBLOCKING維持。Stage 2本体(1回目)は現行のまま(指摘を見せない。本体の較正を崩さない)。
  3. **採用**: Tier 2=解除不可にしたclaimのrewrite_hintを、Checkerのissue/explanation+Ledgerの`notes_for_writer`/`conditions`から生成(Stage 2のhintは降格時に空のため)。確認役のAPI失敗・schema不一致はBLOCKING(Rewrite)へ倒し、Human Reviewへ倒さない。Guard・確認役は毎cycleの現行本文で再評価。
  4. **採用(¥0評価)**: Tier 0 G_L(Ledgerの構造化欄`causal_strength`[OBSERVED_REPORTED/CORRELATIONAL/CAUSAL_STATED_BY_SOURCE/NOT_APPLICABLE]×`notes_for_writer`の禁止文×Checkerのflag)を¥0 replayで判別力を評価。判別力が出れば主Guard、G_B並みに広ければ不採用。
  5. **採用**: 確認役のoffline replay(有料)で採否判定。指標: (i)流出10行+neg5(6行)の閉鎖率=100%必須、(ii)NORMAL群のラベル付き正当降格のうち確認役がBLOCKINGにした率(不要Rewriteの上限)、(iii)全降格534件のBLOCKING化率。**判定基準(Fable事前設定)**: (ii)≤10%かつ(i)=100% → 採用して限定確認へ。(ii)10〜25% → Tier 0/promptの調整を1回だけ試し再replay(追加費用内)。(ii)>25%または(i)<100% → 採用せずFableへ報告(ユーザーへKPI緩和を提案しない)。
  6. **採用**: neg5(B3と同一文)のSafety-critical登録(計測の是正)と、Safety-critical集合を「正BLOCKINGラベル付きclaim(正規化同一文を含む)」から自動導出する補助集計の追加。旧値(流出10行)と新値を並記。
  7. **採用**: Q(引用符字形の同一視、一意のみ)とU-2(1)(閉じた語彙の位置語→構造要素)を実装。R(長い説明文残余を捨てる)は保留(現行Checkerで発生0、Opus#11の位置手がかり語彙の指摘あり)。
  8. **不採用(現時点)**: Sol等の強モデル(B3は同一入力で10/10正解=能力不足ではない。割れたらBLOCKING→Rewriteの方が安く決定論的)。Rewrite失敗がHuman Reviewを生むと測定で示された場合のみ再検討。
  9. **採用**: ACCEPTABLE定義の重複(R3基底とV7)はSafety対策としてrubricを直さず、確認役promptは単一定義で書く。本体rubricの統合は次回の計画的再較正に回す(記録)。
  10. **採用**: Stage 1 recallは第二段階。6-B∧6-F(決定論候補生成+Ledgerの因果禁止・相関のみ記録)をprecheck経路の候補として¥0評価する(本委任では設計書に手順を書くのみ。実装は委任_03以降)。
  11. **採用**: 計測是正: In one lineのclaimが`section_type=body`で渡っている点を記録(判定変更はしない)。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。Checker Prompt・Schema・判定方法は変更しない。Stage 2本体のprompt(V7b)も変更しない。
  - 新スイッチは既定OFF(`STAGE2_DOWNGRADE_VERIFY`等)。`KPI_TRIAL_SWITCHES`(KPI確認構成)にはONで追加。OFFで既存挙動不変をテストで固定。
  - Human Reviewへ倒す新経路を作らない。Solを使わない。
  - offline replay・限定確認の母数・nは固定(増やさない)。採否基準(上記5)を事後に変えない。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: 上限¥55(Guardrail。内訳の目安: 確認役offline replay≤¥45[降格534+流出10+neg5 6≈550件×¥0.04〜0.05×1回≈¥25、NORMAL群正当降格と流出・neg5行のみn=2追加≈¥5、調整1回の再replayは対象限定で≤¥10]、限定確認≈¥5)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥584.07、上限¥900、残¥315.93。**有料実行の前に費用概算を出し、`results`に実測と並記する。**
- Opus独立技術レビューGate: #11実施済み(条件A)。実装がFable評価の形から外れる変更が必要になったら実装せず報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_02.md`。**委任文は全文そのまま保存(末尾のOpus#11全文を含む。要旨化不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。報告用`.md`をWriteツールが拒否する場合はPythonから出力。heredocでバックスラッシュが壊れる事故(委任_01)を避けるため、スクリプトはWrite/Editツールで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

````
Step 3
Fable/Claudeでレビュー内容を咀嚼し設計改善。
Step 4
必要な技術是正をTrial側へ実装。
Step 5
B3/A2A3等の既知caseで限定確認。
(略)
Opusから問題を指摘されたら、そのままユーザーへ投げず、
- 採用
- 不採用
- 修正して採用
をFable/Claudeで判断し、Guardrail内で改善してください。
(略)
Safetyを理由にHuman Reviewへ逃がさないこと。
Human Reviewゼロ自体がKPIです。
````

## 作業1: Opus#11の保存とFable評価の記録(¥0)

`docs/pm/opus_l2_review_open233_kpi_recovery_02_11.md`: (1)依頼文(本委任文末尾の「Opusへの依頼」節を逐語)、(2)Opus#11全文(逐語)、(3)Fable評価1〜11(逐語)+PM_GOVERNANCE 11-3の8項目照合+STOP条件非該当の根拠(Opusとの重要対立なし: Fableは三層を採用、D*を補助へ降格)。設計書`docs/pm/design_open233_kpi_recovery_02.md`に§8「Opus#11後の設計改善(三層)」を追記(Tier 0/1/2の仕様、採否基準、測定計画、Stage 1 recall 6-B∧6-F手順)。

## 作業2: 実装(runner、既定OFF)

- 2-1 Tier 0: `stage2_release_guard(claim, ledger_fact, article_ctx)`→`(blocked: bool, reason)`。構成: G_L(Ledger `causal_strength`/`notes_for_writer`禁止文×Checker flag。判別力は作業3の¥0 replayで決め、閾値・語彙は定数化)、補助ベルトG_H/issue_actor(委任_01の定義のまま、`reason`に`aux:`接頭辞)。
- 2-2 Tier 1: `run_stage2_downgrade_verify(...)`=`floor_verify`の一般化(既存`run_floor_verify_call`/`_fv_validate_call`を再利用または共通化。既存floor_verifyの挙動は不変をテストで固定)。対象判定: Checker severity=MAJOR∧Stage 2最終`materiality`∈{QUALITY, ACCEPTABLE}∧Tier 0非該当∧floor_verifyで解放済みでない。prompt: Fable評価2のとおり(単一定義rubric、Checker issue/flagsを仮説として提示、Ledger逐語引用必須、迷えばBLOCKING)。prompt sha256・費用・verdict・citation・照合結果を記録。
- 2-3 Tier 2: 解除不可(Tier 0該当/確認役UPHOLD/非逐語/失敗)のclaimの`rewrite_hint`を、Checker `issue`/`explanation`+Ledger `notes_for_writer`/`conditions`から決定論で合成(`hint_source`記録)。失敗はBLOCKING→Rewrite経路(既存ラダー)。Human Reviewへの新経路なし。毎cycle再評価。
- 2-4 スイッチ`STAGE2_DOWNGRADE_VERIFY`(既定OFF、CLI `--stage2-downgrade-verify`)。`KPI_TRIAL_SWITCHES`へON追加。summary集計(`downgrade_verify_summarize`: 対象/Tier 0該当[理由別]/確認call数/RELEASE/UPHOLD/非逐語/失敗/費用)。
- 2-5 neg5のSafety-critical登録(`SAFETY_CRITICAL_CLAIM_DEFS`に`neg5_*`のB3同一文、expected BLOCKING)と、自動導出集計`derive_safety_critical_from_labels()`(正BLOCKINGラベル付きclaimの正規化同一文)。`detect_safety_critical_misdowngrades`は両方で集計し、旧値/新値を並記。
- 2-6 Q(引用符字形同一視: `“”"`/`‘’'`/「」の相互同一視、文字数不変、一意のみ採用)とU-2(1)(委任_66設計: `headline`/`title`/`heading`→`#`見出し行、`one-line summary`/`In one line`/`one line`/`summary`→`## In one line`直下1行、`opening`は対象外)を`VS_EXPLAIN_SPLIT`配下に実装(新スイッチなし。P-strict-closedの4ガードは不変。範囲は拡張のみ)。Rは実装しない。
- 2-7 In one lineの`section_type`記録の是正(判定は変えず、`section_type_observed`を記録に追加)。
- テスト: 新規(Tier 0判定・G_L・補助ベルト/確認役の対象判定・解除条件・失敗時BLOCKING・引用照合・prompt sha/Tier 2 hint合成/OFF不変/floor_verify不変/neg5登録/自動導出/Q/U-2(1)/既定OFF)。runner単体・er052回帰・全体回帰(基準11件以外新規なし)。

## 作業3: ¥0評価(Tier 0 G_L)

`er052_output/open233_kpi_recovery_02_offline_01/replay_guards_03_gl.py`: 既存MAJOR 1143件(降格534+流出10+neg5 6を含む)に対しG_L・G_H・issue_actor・組合せの「流出閉鎖(16行)/正当降格のBLOCKING化(件数・率)」を表に。G_Lの判別力が出なければ(正当降格BLOCKING化>5%かつ閉鎖の上積みなし)G_Lは不採用とし補助ベルトのみ残す(理由を記録)。

## 作業4: 確認役のoffline replay(有料、上限¥45)

`er052_output/open233_kpi_recovery_02_offline_01/replay_verify_01.py`。対象: 既存ログの「Checker MAJOR→Stage 2非BLOCKING」534件+流出10行+neg5 6行(Tier 0該当分は確認役を呼ばずTier 0でBLOCKINGとして集計)。各件、記録済みの本文・Ledger・claim・issue/flagsで確認役を1回呼ぶ。NORMAL群のラベル付き正当降格と流出・neg5行はn=2(2回目は再現性確認)。**実行前に費用概算**(件数×probe単価)を出し、¥45超なら「NORMAL群正当降格全件+流出・neg5全件+その他は層化サンプル200件」へ縮小して理由を記録。
- 指標: (i)流出10行+neg5 6行の閉鎖率(Tier 0 or UPHOLD)、(ii)NORMAL群正当降格のBLOCKING化率(UPHOLD+非逐語+失敗)、(iii)全降格のBLOCKING化率、(iv)QUALITY/ACCEPTABLE別、rubric版別、(v)引用非逐語率、(vi)費用(1件単価、記事換算+¥)、(vii)n=2の一致率。
- 採否判定はFable評価5の基準どおり。10〜25%の場合の調整1回はTier 0の語彙/確認役promptの「迷えばBLOCKING」の表現・引用要件の明確化に限り(本体rubric不変)、対象限定(NORMAL群+流出+neg5)で再replay(≤¥10)。

## 作業5: Step 5 限定確認(有料、約¥5。作業4で採用判定のときのみ)

`er052_open233_self_recovery_flow_runner_01_rep26_known_01.py`(rep25複製、`--kpi-trial-config`+`STAGE2_DOWNGRADE_VERIFY=True`)。instance=`bgroup_B3`、`safety_A2A3`、`neg5_*`(B3同一文のinstance)、`neg3_hormuz_prodrunner_b1b`、n=2。出力`er052_output/open233_self_recovery_flow_runner_01_rep26/`。
- 確認: Human Review(STAGE4)0件/重大見逃し0件(旧定義・新定義とも)/L6の実flow復元(A2A3・B3のspan不完全がcycle内で復元されるか、prior_issues現行本文化でB3型の古い引用が消えるか)/Tier 0・確認役の発火と結果(RELEASE/UPHOLD、引用逐語)/解除不可claimのRewrite解消率・cycle数(Human Reviewへ行かないか)/不要Rewrite(neg3・neg5)/費用(rep24・rep25同instance比、+¥/記事)/JA変更0。
- 即時STOP: JA変更、重大見逃し、例外。STAGE4が1件でも出たら、その原因(Rewrite失敗/照合不能/cycle上限)を特定して報告(追加runはしない)。

## 作業6: SSOT

- `OPEN_ITEMS.md` `OPEN-233-KPI-RECOVERY-REDESIGN-02`行Status: 「委任_02: Opus#11→Fable評価(三層採用)、Tier 0/1/2実装(既定OFF、KPI構成ON)、G_L ¥0評価【結果】、確認役offline replay【閉鎖X/16・NORMAL群BLOCKING化Y%・¥Z】→【採用/調整/不採用】、Step 5 rep26【STAGE4 a件・見逃しb件・¥c】。次: 委任_03=Step 6(Safety-critical群+29件再確認)」。Step進捗欄更新。`docs/pm/REPORT_LEDGER.md`。REPORT §52。`docs/pm/ACTIVE_TASK.md`(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない(Fable評価はOpus保存ファイルと設計書に記録。DECISION_LOGへの転記は委任_03のCloseout時)。

## 事前指定Read一覧

- `docs/pm/design_open233_kpi_recovery_02.md`(§2〜§7)、`docs/pm/rca_open233_b3_stage2_misdowngrade_01.md`(§4-3 tie-break、欠陥表)。
- runner: Grep `floor_verify_target|run_floor_verify_call|_fv_validate_call|floor_verify_evaluate|FLOOR_VERIFY_MODE|KPI_TRIAL_SWITCHES|apply_kpi_trial_switches|run_stage2|rewrite_hint|SAFETY_CRITICAL_CLAIM_DEFS|detect_safety_critical_misdowngrades|vs_explain_split_resolve|VS_EXPLAIN_POSITION_REJECT_RE|section_type|precheck` → 該当範囲(全文Read禁止)。
- `er003_v1_en_direct_vfl_01_generate.py` 88〜107(`causal_strength`列挙、read-only)。Ledger: `notes_for_writer`/`conditions`の形式(Grep)。
- 既存ログ: `er052_output/open233_kpi_recovery_02_offline_01/replay_guards_02.py`(語彙・母集団の抽出ロジック再利用)、`replay_d_type_01.py`。
- 委任_61の単体確認スクリプト`er052_open233_floor_verify_unit_check_02.py`(確認役promptの参考)。
- SSOT: Grep `KPI-RECOVERY-REDESIGN-02` → 更新位置。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_02.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_02.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

¥0評価:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\replay_guards_03_gl.py

確認役offline replay(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\replay_verify_01.py --stage probe
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\replay_verify_01.py --stage main --budget-jpy 45
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\replay_verify_01.py --stage agg

限定確認(有料、採用判定時のみ):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep26_known_01.py --stage main --n 2 --budget-jpy 8
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep26_known_01.py --stage agg
(引数名は実装に合わせてよい。)

順序: T-0 → 作業1 → 2(テスト含む) → 3 → 1回目commit/push → 4 → [採用なら]5 → 6 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORT。
- 1回目commit: Opus#11保存、設計書、runner、テスト、G_L replay、委任ログ。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: Opus批判レビュー#11を保存しFable評価(三層構造を採用、D*は補助、S1・Sol不採用)、Tier 0決定論Guard/Tier 1確認役(floor_verify一般化)/Tier 2 hint合成・neg5登録・Safety-critical自動導出・Q/U-2(1)を検証用runnerへ実装(既定OFF)、G_L ¥0評価(委任_02)`
- 2回目commit: 確認役replayスクリプト・出力、rep26スクリプト・出力、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: 確認役offline replay【閉鎖X/16・NORMAL群BLOCKING化Y%・¥Z】→【採用/調整/不採用】、Step 5既知case限定確認rep26【STAGE4 a件・見逃しb件・¥c】(委任_02)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(KPI 4つの現状値、採否判定、Step 6へ進める状態か)、(2)実装箇所(行番号)とテスト件数、(3)G_L ¥0評価表、(4)確認役replay結果表(指標(i)〜(vii))と採否判定・調整の有無、(5)rep26結果表(run別: STAGE4/見逃し旧新/L6復元/Tier発火/Rewrite解消率/費用/JA)、(6)費用(概算と実測、Phase累計)、(7)SSOT更新箇所、(8)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別、(9)Fableへの論点(再設計が必要な点、Step 6の構成提案)。

---

## 参考(逐語): Opusへの依頼(レビュー#11)

[Fableがopus-consultantへ送った依頼。論点1〜12: 1.RCAの妥当性 2.D*が穴を本当に閉じるか(パターンパッチではないか) 3.Evidence要件による構造的是正(F5型一般化、Ledger側逐語引用、Major→Minor/No issue分離) 4.ACCEPTABLE定義重複 5.不要Rewriteの見積り 6.Human Reviewへ逃げていないか 7.より単純な方法・既存資産再利用 8.説明文混入5件のQ/R/U-2(1) 9.Stage 1 recall第二段階 10.Sol限定利用の要否 11.cost・非決定性・retry loop 12.neg5未登録の是正。packet: `docs/pm/opus_packet_open233_kpi_recovery_02_01.md`、RCA: `docs/pm/rca_open233_b3_stage2_misdowngrade_01.md`、設計書: `docs/pm/design_open233_kpi_recovery_02.md`。]

## 参考(逐語): Opus独立レビュー#11 全文

## Opus独立レビュー#11(条件A): OPEN-233-KPI-RECOVERY-REDESIGN-02 後段Safetyの再設計

先に結論: 後段の再設計は**必要**です。ただし推奨案D\*を主構造にすることには反対します。D\*の(A)決定論Guardは、既知10行に合わせて作り、同じデータで評価した語彙パッチです。(B)S1(同じpromptで2回目を呼ぶ)は、偶発的な誤り(1回だけの外れ)にしか効かず、rubric起因の系統的な誤り(毎回同じように外れる誤り)には効きません。その根拠はV5のB3が2回中2回降格したこと、neg5が6回降格されていることです。D\*を採っても、ユーザーが禁止候補とした「AI判定だけで重大→問題なし」は、Guardの語彙外では形を変えて残ります。代わりに、**決定論Guard+「確認役」call+失敗時はBLOCKING**の三層を提案します(下記「推奨構造」)。確認役は既存floor_verifyの一般化で、Checkerの指摘を仮説として受け取り、Ledgerの逐語引用を返す別promptのcallです。この確認役は、有料のoffline replay(約¥30〜90)で不要Rewriteの増え方を測ってから選ぶべきです。

### 論点1〜12

**1. RCAの妥当性**
(a)〜(g)は概ね正しいです。次の3点が抜けているか、重みが軽すぎます。
- (補1) **迷ったときの扱いが「解除」側に固定されている**。R3冒頭のtie-breakは「迷えばQUALITY」で、QUALITYはRewriteされず通過します。つまり不確実なときは解除へ倒れる設計です。ユーザーの言う「confidenceやEvidenceが足りないときはMajor維持」と真逆で、RCAは§4-3で触れたのに欠陥表に入れていません。
- (補2) **Stage 2が二つの役を兼ねている**。Checkerの過剰Majorを下げる役(精度)と、Safetyの最後の防波堤の役です。「解除」と「維持」の誤りのコスト差がどこにも書かれていません。
- (補3) **計測の欠陥**。流出は手作業の`SAFETY_CRITICAL_CLAIM_DEFS`に載ったclaimしか数えないため、未登録の流出は見えません(neg5がその実例)。
- 小さい点: In one lineのclaimが`section_type=body`としてStage 2に渡っています。学習者にとって要約行は誤解の影響が最も大きい場所なので、RCAが「判定には無関係」としたのは楽観的です。
- RCAが「乱数は引き金、権限構造が原因」と結論づけた点は支持します。

**2. D\*は本当に穴を閉じるか**: 閉じません。
- **9/10閉鎖は設計に使った10行での成績です**。別の検証用データでは確認していません。
  - 接続語(CONN)は6語だけです。since / due to / thanks to / driving / prompted / that is why、「after X, Y fell」のような時系列で因果を匂わせる型が漏れます。
  - ヘッジ語(HEDGE)に`can`/`would`が入っているため、「so the plan would leave」のような文は除外されます。
  - `issue_actor`の語彙は旧Checkerの1例から作ったものです。
  - 正当な降格25件から6件への絞り込みは、ほぼヘッジ語除外だけで実現しています。
- **閉じない1行(rep24 cycle 2の「and」版)が弱点の実例です**。Rewriteで接続語が消えると、Checkerが因果を指摘し続けていてもGuardは外れます。Rewriteは結果としてGuardを回避する方向に働きます。
- **(B)S1**: q=0/30は「2回目もほぼ必ず同じ判定」という意味です。追加Rewriteが少ない(安い)ことの根拠であると同時に、**判別力も低い**ことの根拠です。S1が拾えるのはrep25のような外れ(p≈1/11)だけです。V5 2/2やneg5×6のような、inputごとにpが高い系統誤りはp²でもほとんど減りません(E[p²]がE[p]²を大きく上回る)。
- 未知の型(条件の断定、確実性の強化、範囲の一般化[D3のBrent→原油全般]、数値なしの比較、主体の断定)には「同じpromptで2回」しか残りません。これは構造的な是正ではありません。

**3. Evidence要件(F5型の一般化)**: D\*より筋が良いです。ただし二つ修正が要ります。
- (i) **逐語引用は反証の証明になりません**。runnerの`_fv_validate_call`(2577〜2585行)は、引用が関連factブロックに逐語であることしか検査していません。B3なら、LLMはHF-009の「懸念が継続していた」を逐語で引いたまま解除できてしまいます。逐語照合で決定論的に保証できるのは「Ledgerと向き合った根拠が監査できる形で残る」ことと「捏造した引用を弾く」ことまでで、争点を反証したことではありません。したがってEvidence要件を唯一の防波堤にはせず、Tier 0(決定論)と組み合わせる必要があります。
- (ii) **配置の仕方**。Opus#8/#10のpriming懸念は「Stage 2本体の較正(正当な降格68件)が崩れる」ことでした。1回目のStage 2は今のまま指摘を見せずに判定させ、**降格しようとした場合だけ**、指摘を見せる別promptの確認役が同意したら解除する形にすれば、本体の較正は崩れません。primingの影響は降格候補の確認だけに閉じ込められます。
  - 同じpromptの2回目ではなく、別promptと別入力による2つの意見になるので、誤りの相関が下がり、系統誤り(V5型)にも効く見込みがあります。
  - 確認役では、迷ったときの扱いを「迷えばBLOCKING」にします。
  - Sonnetが「日本語Ledger×英語記事で逐語照合は不成立」としたのは、claim側を照合する場合の話です。引用をLedger側の逐語にすれば成立し、委任_61で実証済みです。
- (iii) **Major→MinorとMajor→No issueで要件を分ける案は、現行の意味づけでは無意味です**。QUALITYもACCEPTABLEも「Rewriteなしで通過」なので、どちらも同じ「解除」です。要件は同一にすべきです。分ける意味が出るのは、QUALITYに別の帰結(例: 軽いRewrite)を持たせる場合だけで、それは不要Rewriteを増やす方向です。
- (iv) **不要Rewriteの見積り方**(¥0では見積もれません)。既存のChecker MAJOR 1143件(降格534件+流出10行+neg5)に対し、確認役を固定入力でoffline実行します。短い入力(関連fact+claim+指摘)で約¥0.03〜0.05/件、全件×2〜3回反復で約¥30〜90です(Phase残¥315の範囲内)。指標は二つです。
  - NORMAL群のラベル付き正当降格のうち確認役がBLOCKINGにした率(不要Rewriteの上限)
  - 流出10行とneg5を閉じた率

**4. ACCEPTABLEの定義が2つある問題**
- 統合はすべきです。ただし**Safety対策としてrubricを直すのは避けてください**(9層目のパッチになり(f)を繰り返します)。
- 解除の要件を構造側で同一にすれば、QUALITYとACCEPTABLEの境界はSafetyに効かなくなります。
- 統合は次回の計画的な再較正のときに、V7のACCEPTABLE行を削ってR3側へ寄せる形で行い、優先度は低くてよいです。確認役のpromptは最初から単一定義の短いrubricで書けば、この問題を持ち込みません。

**5. 不要Rewriteの見積り**
- D\*のGuard部分は¥0 replayで確定しています(7/524、ただし同じデータでの評価)。
- S1部分は既存のq=0/30が根拠ですが、上限は約10%と広いです。
- 確認役は3(iv)のoffline replayが必須で、推測で埋めてはいけません。
- 解除不可になったclaimについては「Rewrite 1回の費用」と「Rewriteが失敗する率」も同時に測るべきです(6へ)。

**6. Human Reviewへ逃げていないか**: 現状は未測定で、ここが最大のリスクです。
- 固定BLOCKING → Rewrite → Recheckで再びMAJOR → cycle上限 → Stage 4(Human Review)という経路があります。
- 是正の必須事項:
  - (a) Guardや確認役で解除不可にしたclaimのrewrite_hintは、Checkerのissue/explanationと、Ledgerの`notes_for_writer`/`conditions`から作る。Stage 2のhintは降格時には空です。
  - (b) 限定確認(B3・neg5・neg3・A2A3)で、Rewriteの解消率とcycle数を測る。
  - (c) 確認役のAPI失敗やschema不一致はBLOCKING(Rewrite)へ倒し、Human Reviewへは倒さない。

**7. より単純な方法・既存資産の再利用**
- **floor_verify(runner 2272〜2610行)をほぼそのまま「降格の確認」へ一般化するのが最も単純です**。対象条件(`floor_verify_target`)を「Checker MAJORをStage 2が非BLOCKINGにしたもの」へ広げ、callは1回にします(Stage 2本体の1回と合わせて2つの意見)。仮説としての指摘提示、逐語引用、失敗時BLOCKINGの仕組みは既に実装と単体確認が済んでいます。新しい処理フローを作るよりこちらが良いです。
- **Ledgerの構造化欄は未活用です**。`causal_strength`は列挙値(OBSERVED_REPORTED/CORRELATIONAL/CAUSAL_STATED_BY_SOURCE/NOT_APPLICABLE、`er003_v1_en_direct_vfl_01_generate.py` 96〜99行)で、`notes_for_writer`の禁止文(「撤回の原因として記述しない」等)と組み合わせると、言語に依存しない決定論Guard(仮称G_L)の候補になります。ユーザーが挙げた「LedgerとChecker根拠を利用した決定論Guard」に最も近い形です。
  - ただしB3の関連fact HF-007はCAUSAL_STATED(Ledgerが別の原因を明記)で、禁止文はHF-001/HF-011にあります。そのため判別力は未知で、G_Bに近づく(広すぎる)おそれがあります。¥0 replayで要検証です。

**8. 説明文混入型5件の解法(Q/R/U-2(1))**
- Q(引用符の字形を同一視、一意のときだけ採用)とU-2(1)は誤範囲を生みにくく、妥当です。
- Rには修正が要ります。「wrong-range(無関係な文を書き換える)は構造上起きない」は正しいですが、「under-scope(範囲が狭すぎる)はRecheckが後ろ盾」は弱いです。Recheck/Stage 1のrecallは既に低いと測られています(DET 2/10〜4/10)。
  - 説明文の残りに、閉じた語彙で解決できない位置・参照の手がかり(also/again/elsewhere/both/throughout/later/conclusion/paragraph、記事の固有名詞、引用符)が1つでもあれば、捨てずに棄却(現状維持で未確定)にすべきです。D2の「also」のように、断片を含む要素へ解決できる場合だけ通します。
- 5件はすべて旧Checkerの出力で、現行(rep24〜25)では出ていません。**今回の主目的には不要で、優先度は低い**です。QとU-2(1)だけ先行し、Rは保留でよいと考えます。

**9. Stage 1 recall(§6)**
- 6-B(決定論で候補を生成)は良いです。
- 6-C(新しい判定promptの補助call)より先に、**6-B∧6-F(Ledgerの因果禁止・相関のみの記録)を、既存のprecheck経路(`detected_by=="precheck"`は無条件floor)へ候補として入れる案**を¥0で評価すべきです。新しいpromptも判定基準も作らずに済みます。
- 偽陽性の量はfixture 29本の0.45文/記事を上限として測れます。6-Cは、その精度が足りない場合の次の手です。順位は後段の是正より後で妥当です。

**10. 強モデル(Sol)は必要か**: 現時点で不要です。
- 根拠: B3は同じ入力の再試行で10/10正解しており、モデルの能力不足ではありません。原因は構造と外れです。
- Stage 2本体と確認役が割れた場合は、「割れたらBLOCKING→Rewrite」(約¥0.5〜0.8)の方がSol裁定(平均約¥2.8、1 callで+¥3のCapを超えうる)より安く、決定論的で安全です。
- Solを検討する意味が出るのは「Rewriteの失敗がHuman Reviewを生む」と測定で示された場合だけです。その場合も、1記事1 call、出力上限の固定、事前の費用見積りで¥3を超えるならRewrite側へ倒す、という条件付きにすべきです。

**11. cost・非決定性・retry loop**
- 確認役の費用はS1と同程度かそれ以下です(入力が短いため、約¥0.05〜0.15/run)。
- 非決定性はLLMが1つ増えますが、外れたときは安全側へ倒れます。
- retry loopの前提: 解除不可にしたclaimは既存のcycle上限の内側で扱い、新しいループを作らない。Guardの判定は毎cycleの現行本文で再評価する(回避されたら確認役が受ける)。
- 既存2-of-2(NORMAL群、既定OFF)とは逆方向で、衝突しません。

**12. neg5未登録の是正**
- 計測の是正として妥当です。新しい仕様ではありません。
- より構造的には、Safety-criticalの集合を手作業のリストではなく**「正BLOCKINGのラベルが付いたclaim(正規化した同一文を含む)」から自動で導く**べきです。
- 過去分の再集計では流出数が増えます(10→16相当)。旧値と新値を並べてユーザーに明示する必要があります。

### 必要/不要
- 必要: 後段の解除構造の是正、neg5計測の是正、解除不可にしたclaimのRewrite成功率の測定。
- 主構造としては不要: D\*のS1部分、Sol、rubricパッチによる是正、QUALITY/ACCEPTABLEで要件を分けること、規則R(当面)。

### 推奨構造(代替案)
- **Tier 0(決定論、¥0)**: G_L(Ledgerの構造化欄×Checkerのflag)を¥0 replayで評価します。判別力が出ればそれを主にします。`G_H`/`issue_actor`は「既知の型への補助ベルト」と明記したうえで残してよいです(費用¥0、誤って止めるのは少数)。
- **Tier 1(確認役)**: Tier 0に当たらない、Checker MAJORのStage 2による降格すべてについて、floor_verifyを一般化した確認役(指摘を仮説として提示、関連factの逐語引用必須、迷えばBLOCKING)が同意した場合だけ解除します。QUALITYとACCEPTABLEで要件は同一です。
- **Tier 2(失敗時)**: 不同意、引用が非逐語、API失敗のいずれも、BLOCKING→Rewriteへ倒します。hintはChecker issueとLedger notesから作ります。Human ReviewにもSolにも倒しません。
- **採否の判定材料**: 確認役のoffline replay(約¥30〜90)で、流出10行+neg5を閉じた率と、NORMAL群の正当降格をBLOCKINGにした率を測ります。正当降格のBLOCKING率が許容を超える場合に限り、D\*(Guard+S1)を「確率的保護」と明記したうえでの退避案にします。

### リスク
- 確認役のprimingで不要Rewriteが増える(未測定、replayで定量化が必要)。
- 逐語引用は反証の証明ではないので、Tier 1単独ではゼロ保証になりません。
- 固定BLOCKINGにしたclaimのRewriteが失敗してHuman Reviewへ流れる(未測定)。
- G_Lは判別力が未知で、G_B並みに広くなる可能性があります。

### 追加で読んだファイルと概算文字数
- packet・RCA・設計書(指定分、約4.6万字)
- `er052_open233_self_recovery_flow_runner_01.py` 2270〜2400行、2550〜2610行(約8千字)
- `er052_output/open233_kpi_recovery_02_offline_01/replay_guards_02.py` 1〜40行(約2千字)
- `docs/pm/opus_l2_review_open233_self_recovery_10.md`のGrep(約2千字)
- `er003_v1_en_direct_vfl_01_generate.py` 88〜107行(約1千字)
- 追加分の合計: 約1.3万字

### 十分に答えられなかった論点
- 論点5と10の定量部分: 確認役の不要Rewrite率とRewrite失敗率は、データがないため推測にとどまります。
- 論点7のG_Lの判別力: ¥0 replayをまだ行っていません。
- 論点8の位置手がかり語彙: 5件の残り文字列を全文では照合していません。
- いずれもProduction採用の可否ではありません(採用はユーザーのみが決めます)。
