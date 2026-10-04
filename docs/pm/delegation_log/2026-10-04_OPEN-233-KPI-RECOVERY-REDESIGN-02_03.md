## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_03)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: 委任_02の実測(確認役=NORMAL群BLOCKING化47.3%で不採用、補助ベルト=流出15/16・誤停止0.2%・¥0、G_L=NORMAL群10.9%)を受けたFableの再設計判断(下記)に基づき、Step 7の再設計ループ1回目を実行する: 再設計D*′(Tier 0=因果floorの語彙拡張+独立データで妥当性確認、Tier 1′=S1[Stage 2第2意見、割れたらBLOCKING]、Tier 2=hint合成)の¥0評価→実装→Step 5(rep26既知case限定確認、約¥5)→**Step 6(Safety-critical群+既存29件を同じ構成で再確認、約¥20)**→KPI判定(`VALIDATED`/未達ならFableへ)。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。
- 到達上限Status: Step 6のKPI判定まで。KPI 4つ同時達成なら`VALIDATED`(Trial評価。Production採用ではない)。未達なら`IN_PROGRESS`のままFableへ報告(ユーザーへKPI緩和を提案しない)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- Fableの再設計判断(SSOTへ逐語記録。変更しない):
  1. **確認役(Tier 1 LLM、Checker指摘を提示)は不採用**: 実測でNORMAL群47.3%・body経路でも37%の正当降格を重大化し、QCD優先3に反する(Opus#11が警告したprimingが実測で確認された)。Hook/title/disclosure_gapの除外でも10%に届かない。再調整は行わない。
  2. **G_Lは不採用**: 流出閉鎖の上積みは「and」版1行のみで、NORMAL群10.9%の誤停止はQCD優先3に反する。委任_02のSonnet判断(`TIER0_G_L_ENABLED=False`)を承認。
  3. **Tier 0=因果floor(`G_H`の一般化)を主構造として採用**: 既存の機械的安全装置(数値・主体・否定・比較・時期のfloor)と同じ「Checker flag+決定論の文面確認」の構造で、因果(`changed_causality`∧因果接続語∧ヘッジなし)を6番目のfloorとして位置づける。Opus#11の「既知10行に合わせた語彙パッチ」の指摘に対しては、**接続語・ヘッジ語の語彙を流出事例から独立した標準的な言語学的目録から構築**し(例: 結果・理由・目的の接続詞/前置詞/動詞: so, because, since, as, due to, owing to, thanks to, therefore, thus, hence, consequently, as a result, that is why, which is why, led to, leads to, resulted in, caused, causing, drove, driving, prompted, triggered, sparked, forced, made, pushed, fueled, in response to, following[文頭+結果節]等)、**流出16行を見ずに語彙を確定してから**流出閉鎖率と正当降格518件・NORMAL群110件の誤停止率を測る(hold-out相当)。ヘッジ語は「推測・可能性・他者の見解の帰属」(may, might, could, possibly, likely, appears, seems, some say, analysts/officials say, reportedly, is said to, expected to)に限定し、`can`/`would`の扱いはA/B両方を¥0で測って誤停止≤2%かつ閉鎖最大の方を採る。
  4. **`issue_actor`は補助ベルトとして残す**(主体の断定。既存floor `changed_actor`の補完)。
  5. **Tier 1′=S1**(Opus#10の3修正付き: 第2意見は`run_stage2`の最終`materiality`で比較、対象claimのみのbatch、割れたらBLOCKING、API失敗はBLOCKING、floor_verify解放済みは除外、毎cycle再評価): Tier 0非該当のChecker MAJOR→Stage 2非BLOCKING全件に適用。q=0/30(委任_68)の実測により不要Rewriteを増やさず+¥0.15/記事。役割分担: Tier 0=既知クラス(因果・主体)の決定論保証、S1=偶発的な外れ(rep25型)、系統誤り(rubric起因)は既存のSafety-critical回帰(V7b再較正、0/30・10/10)で捕まえる。
  6. **Tier 2=hint合成**(委任_02実装済み)は維持。解除不可claimは必ずRewrite(Human Reviewへ倒さない)。
  7. **残り1行(rep24 cycle 2のB3「and」版「…continued on July 14, and the flashy 20% plan left the stage.」)のFable判断**: 正式基準(重大=事実関係の重大な誤解)で**問題なし**(「and」は因果を主張しない。確認役も2回ともRELEASE)。この行がSafety-critical流出に計上されるのは`text_substring`「flashy 20% plan」の部分一致によるラベル付けであり、A4-1(委任_57)と同じく`CORRECT_LABEL_OVERRIDES`で「and版=ACCEPTABLE」を登録して旧値/新値を並記する。この判断はユーザーへ報告し、否認されれば戻す。cycle 2でCheckerがこの文を再指摘したのはprior_issuesの古い本文(`so`)の引用が原因で、委任_01の是正で解消見込み(rep26で確認)。
  8. **Opus再レビューは本委任では行わない**: D*′の構造(決定論Guard+S1)はOpus#10(S1の3修正)と#11(Guard+S1を退避案として許容)で既にレビュー済みであり、実測(確認役の特異度不足)に基づく「修正して採用」。Step 6でKPI達成なら、Production採用提案前(条件C)に改めてOpusレビューを入れる。
  9. Stage 1 recall(第二段階)は本委任では着手しない(Step 6の結果で未検出があれば次ループ)。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。Checker Prompt・Schema・判定方法・Stage 2本体rubric(V7b)は変更しない。
  - 語彙の確定前に流出16行の文面を見ない(手順を記録。既に委任_01/02で見た語彙G_Hの6語は「既知」として、拡張分は目録から)。語彙確定後の調整は`can`/`would`のA/Bのみ。
  - 確認役(`STAGE2_DOWNGRADE_VERIFY`)はコードを残すが既定OFFかつ`KPI_TRIAL_SWITCHES`から外す。Solを使わない。
  - Human Reviewへ倒す新経路を作らない。Step 6の母数・nは固定(iteration 7と同じ29 instance・38 run)。再実行・n増しをしない(失敗は失敗として記録)。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: 上限¥35(Guardrail。内訳の目安: rep26[B3/A2A3/neg5/neg3×n=2]≈¥5、Step 6[38 run、rep24実測¥16.7+S1追加≈¥4]≈¥22)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥617.19、上限¥900、残¥282.81。有料実行前に費用概算を出し実測と並記。
- 即時STOP(有料run中): JA変更/例外2 instance以上/1 instance-run費用>¥7。重大見逃し・STAGE4は**止めずに完走し**、件数と原因(claim・経路・Tier発火・Rewrite失敗理由)を特定して報告(Step 6は1回限りのため)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_03.md`。**委任文は全文そのまま保存(要旨化不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。スクリプトはWrite/Editツールで作る(heredoc禁止)。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。10分のツール制限で中断した場合は`skip existing`で1回だけ再開し、中断の事実を記録(rep24と同じ扱い)。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

````
Step 6
Safety-critical群＋既存29件を再確認。
ここで最低限、
- Human Review 0件
- 重大見逃し 0件
を同じ構成で同時に確認すること。
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
(略)
Productionに存在しないTrial補助でKPI達成を演出してはいけません。
````

## 作業1: Fable再設計判断の記録(¥0)

設計書`docs/pm/design_open233_kpi_recovery_02.md` §10「再設計ループ1: D*′(Fable判断、委任_03)」に上記1〜9を逐語で記録。`docs/pm/opus_l2_review_open233_kpi_recovery_02_11.md`に「(4)実測後のFable再判断」節を追記(確認役不採用の実測根拠、Opus#11の退避案[Guard+S1]を採用した経緯、再レビューを本委任で行わない理由)。

## 作業2: Tier 0 因果floorの語彙構築と¥0評価(hold-out手順)

- 2-1 語彙構築(流出16行を見ない): `CAUSAL_CONNECTIVES_EN`(目録から。結果・理由・目的の接続詞/前置詞句/因果動詞。日本語記事は対象外[英語claimのみ])、`HEDGE_MARKERS_EN`(推測・可能性・帰属)。各語の出典(目録名/一般的な文法参照)を定数のコメントに記載。`can`/`would`はA(ヘッジに含める)/B(含めない)の2版。語彙確定のcommit(1回目)を**先に**行い、評価は確定後に実施したことをgit履歴で示す。
- 2-2 評価`replay_guards_04_causal_floor.py`: 既存MAJOR 1143件(降格534・流出16・正当降格518・NORMAL群110)に対し、A/B各版で「流出閉鎖(旧10/新16。『and』版を除いた15も併記)/正当降格誤停止(件数・率)/NORMAL群誤停止/既知G_H 6語との差分(拡張で新たに閉じた・止めた件)」。採用条件: 誤停止≤2%(正当降格)かつ閉鎖≥15/16(「and」版除き15/15)。A/Bで条件を満たす方(両方なら閉鎖が多い方、同じなら誤停止が少ない方)を採る。満たさない場合は語彙を削らず、条件を満たさない事実を記録してFableへ報告(Step 5以降へ進まない)。
- 2-3 「and」版のラベル登録: `CORRECT_LABEL_OVERRIDES`に「rep24 cycle 2 B3 and版=ACCEPTABLE(Fable判断2026-10-04、委任_03、ユーザー未確認)」を追加し、流出集計を旧値(16)/新値(15)並記。

## 作業3: 実装(runner)

- 3-1 Tier 0: `changed_causality_floor`(`FLOOR_FLAGS`に準じる6番目のfloorとして`apply_floor`または`stage2_release_guard`に統合。発火条件: `dev.changed_causality`∧claim文に`CAUSAL_CONNECTIVES_EN`のいずれか∧`HEDGE_MARKERS_EN`なし。`floor_reason="changed_causality_floor"`)。`issue_actor`は補助ベルトのまま。G_Lは無効のまま。スイッチ`CAUSAL_FLOOR`(既定OFF、`KPI_TRIAL_SWITCHES`でON)。
- 3-2 Tier 1′ S1: `apply_stage2_second_opinion`(Opus#10の3修正: 最終`materiality`比較、対象claimのみbatch、割れたらBLOCKING、API失敗/schema不一致BLOCKING、`floor_reason`がfloor由来なら異常ログ、floor_verify解放済み除外、毎cycle・Recheck由来にも適用、記録: 2回の`materiality`/basis/prompt sha/費用)。スイッチ`STAGE2_SECOND_OPINION`(既定OFF、`KPI_TRIAL_SWITCHES`でON)。既存NORMAL群2-of-2は既定OFFのまま(KPI構成OFF)。
- 3-3 `KPI_TRIAL_SWITCHES`から`STAGE2_DOWNGRADE_VERIFY`を外す(コードは残置、既定OFF)。
- 3-4 Tier 2 hint合成を、Tier 0該当・S1で割れたclaimにも適用。
- 3-5 summary集計: Tier 0発火(理由別)/S1対象・一致・割れ・失敗/費用/旧新Safety-critical集計/L6復元/prior_issues現行本文化の発火。
- テスト: 新規(因果floorの発火・非発火[ヘッジ]・語彙A/B・OFF不変/S1の対象判定・一致/割れ/失敗・最終materiality比較・除外・毎cycle/KPI構成の内容/「and」版override)。runner単体・er052回帰・全体回帰(基準11件以外新規なし)。

## 作業4: Step 5 rep26 既知case限定確認(有料≈¥5)

`er052_open233_self_recovery_flow_runner_01_rep26_known_01.py`(委任_02作成済みを`KPI_TRIAL_SWITCHES`[因果floor+S1+L6+prior_issues現行本文+NORMAL群2-of-2 OFF+P-strict-closed+Q/U-2(1)+VS_MATCH_EXT+english_only+V7b+time_only floor_verify]へ更新)。instance=`bgroup_B3`、`safety_A2A3`、`neg5_*`(B3同一文)、`neg3_hormuz_prodrunner_b1b`、n=2。
- 確認: STAGE4 0/重大見逃し0(旧新定義)/L6実flow復元(A2A3のspan不完全、B3のcycle 2再指摘がprior_issues是正で消えるか)/Tier 0・S1の発火と結果/解除不可claimのRewrite解消率・cycle数/不要Rewrite(neg3・neg5)/費用/JA 0。
- 判定: STAGE4 0かつ見逃し0なら Step 6へ。1件でもあれば原因特定し、**本委任内で是正可能(実装バグ・hint不足・照合漏れ等の技術是正)なら是正→rep26を同じinstanceだけ再実行(1回のみ、≈¥5追加)**。設計変更が必要ならStep 6へ進まずFableへ報告。

## 作業5: Step 6 Safety-critical群+既存29件の再確認(有料≈¥22)

`er052_open233_self_recovery_flow_runner_01_rep27_full_01.py`(rep24複製、`KPI_TRIAL_SWITCHES`)。iteration 7/rep24と同じ29 instance・38 run。出力`er052_output/open233_self_recovery_flow_runner_01_rep27/`。
- 集計(rep24比・iteration 7比): Human Review(STAGE4)件数・理由/重大見逃し(旧定義・新定義[自動導出]・`residual_at_pass`全件仮ラベル)/Safety-critical 6件(B3・B4-a・A2A3-0・A4-0・A5-0・neg5)の検出・経路/Tier 0発火・S1一致/割れ/不要Rewrite(既存定義+全runのRewrite件数、rep24 24件/19 run比)/過剰Major(Stage 2 BLOCKING件数、floor単独)/L6・P・Q/U-2(1)の発火と誤範囲/prior_issues現行本文化の発火/英語だけ修正(JA 0)/費用(合計・平均追加/記事[rep24比]・worst・Cap+¥3超のrunの有無)/モデル・構成の記録。
- **KPI判定**: Human Review 0∧重大見逃し0(新定義含む)∧平均追加≤+¥2∧worst追加≤+¥3 → `VALIDATED`(Trial評価)。1つでも未達→`IN_PROGRESS`のまま、原因分析(claim・経路・Tier・Rewrite失敗理由)をREPORTに書きFableへ(再ループ)。

## 作業6: SSOT

- `OPEN_ITEMS.md` `OPEN-233-KPI-RECOVERY-REDESIGN-02`行Status: 「委任_03: 再設計D*′(因果floor語彙拡張hold-out【閉鎖X/16・誤停止Y%】+S1+hint)実装、rep26【STAGE4 a・見逃しb・¥c】、Step 6 rep27【STAGE4 d・見逃しe(旧/新)・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】。確認役・G_Lは不採用(実測)。次: 【Closeout(委任_04)/再ループ】」。Step進捗欄。`docs/pm/REPORT_LEDGER.md`。REPORT §53。`docs/pm/ACTIVE_TASK.md`(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない(Closeout委任で転記)。

## 事前指定Read一覧

- runner: Grep `stage2_release_guard|g_h_guard|issue_actor_guard|TIER0_G_L_ENABLED|apply_floor|FLOOR_FLAGS|floor_reason|downgrade_verify_rewrite_hint|KPI_TRIAL_SWITCHES|STAGE2_DOWNGRADE_VERIFY|run_stage2|apply_stage2_two_of_two|floor_verify_target|CORRECT_LABEL_OVERRIDES|SAFETY_CRITICAL_CLAIM_DEFS|derive_safety_critical_from_labels` → 該当範囲(全文Read禁止)。
- `er052_output/open233_kpi_recovery_02_offline_01/replay_guards_02.py`・`replay_guards_03_gl.py`(母集団抽出・集計の再利用)、`replay_verify_01_summary.json`(集計キーのみ)。
- `docs/pm/design_open233_stage2_safety_downgrade_01.md` §8(修正版S1仕様)。`docs/pm/opus_l2_review_open233_self_recovery_10.md`(論点6の比較基準)。
- rep26スクリプト(委任_02作成)、rep24スクリプト(複製元)、`rep24_agg_01.py`。
- SSOT: Grep `KPI-RECOVERY-REDESIGN-02` → 更新位置。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_03.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_03.md_check.json

¥0評価:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\replay_guards_04_causal_floor.py

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

rep26(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep26_known_01.py --stage main --n 2 --budget-jpy 8
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep26_known_01.py --stage agg

rep27(有料、1回):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep27_full_01.py --stage main --budget-jpy 26
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep27_full_01.py --stage agg
(引数名は実装に合わせてよい。)

順序: T-0 → 作業1 → 2-1(語彙確定)→ **1回目commit/push(語彙確定の証跡)** → 2-2・2-3 → 3(テスト含む) → 2回目commit/push → 4 → [判定OKなら]5 → 6 → 3回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORT。
- 1回目commit(語彙確定): runner(語彙定数のみ)、委任ログ。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: 因果floorの接続語・ヘッジ語語彙を言語学的目録から確定(流出事例を参照せず、評価前の証跡)(委任_03)`
- 2回目commit: 設計書§10、Opus#11ファイル追記、replay、runner、テスト。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: 再設計D*′(因果floor hold-out評価【閉鎖X/16・誤停止Y%】+S1第2意見+hint合成)を検証用runnerへ実装(既定OFF、KPI構成ON)、確認役・G_Lは実測で不採用、and版ラベル登録(委任_03)`
- 3回目commit: rep26/rep27スクリプトと出力、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: Step 5 rep26【…】・Step 6 rep27 29件+Safety-critical再確認【STAGE4 d・見逃しe・平均追加+¥g】→【VALIDATED/未達】(委任_03)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(KPI 4つの実測値、VALIDATED/未達)、(2)語彙確定の証跡(commit hash)とhold-out評価表(A/B、閉鎖・誤停止)、採った版、(3)実装箇所・テスト件数、(4)rep26結果表(是正・再実行の有無)、(5)rep27結果表(rep24・iter7比、Safety-critical 6件、Tier発火、S1一致/割れ、不要Rewrite、費用、worst、モデル・構成)、`residual_at_pass`全件仮ラベル、(6)未達の場合の原因分析と再ループ案、(7)費用(概算/実測/Phase累計)、(8)SSOT更新箇所、(9)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別、(10)Fableへの論点(「and」版判断の扱い、Closeoutへ進めるか)。
