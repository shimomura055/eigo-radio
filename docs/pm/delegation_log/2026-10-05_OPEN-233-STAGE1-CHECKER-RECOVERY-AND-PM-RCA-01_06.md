# 委任_06 委任文(全文保存、2026-10-05)

## 管理ID

`OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01`(委任_06、ループ1「実装」段)。**並行タスクあり**: 委任_05(Opus#16保存・設計書§6・DECISION_LOG・Opus台帳・OPEN_ITEMS・REPORT・REPORT_LEDGER・offline集計スクリプトを編集、commit)。本委任は**コード(Trial側)とテスト、新規スクリプト、新規設計メモのみ**を編集し、上記SSOT・文書・`ACTIVE_TASK.md`/`RESULT_PACKET.md`に触れない。報告はhandback本文。gitは自分のファイルのみ明示add(index.lockは10秒待ち最大3回再試行)。

## 性質/禁止事項

- 性質: ¥0(有料API実行なし)。Opus#16を受けたFable確定構成をTrial runnerへ実装し、¥0で検証(単体テスト・fixtureでの決定論dry-run・偽LLM fixture)。段階A(有料)のスクリプトは作成のみ(未実行)。
- **実装する確定構成(Fable評価、変更しない)**:
  1. **文ID分割(決定論)**: 本文をhook/1行要約/段落/文に分割し単位IDを付与(既存`split_family_x_article_text_v2`・runnerの文分割ユーティリティ`vs_sentence_segments_l6`等を再利用)。**関係単位ID**: 文頭に因果・照応語(既存`CAUSAL_SENTENCE_INITIAL_RE` runner L3147付近を再利用し、`So`/`This is why`/`That is why`/`As a result`/`Therefore`等を追加)がある文は直前文と組にした単位IDも生成。正規化(空白・引用符・大小)後に同一文が複数IDにあれば「同文グループ」を記録。
  2. **3'-R(記事→Ledger方向)**: 全単位IDに判定を返すprompt(新規module `er052_open233_stage1_coverage_checker_01.py`)。出力schema: 単位IDごとに`verdict∈{CANDIDATE, SUPPORTED}`、SUPPORTEDには`support_fact_ids`+Ledger逐語引用必須、CANDIDATEには`issue`・`flags`(既存10フラグ)・`related_fact_id`・`claim_in_article`。**重大度(MAJOR/MINOR)はStage 1で決めない**(「迷えば候補」。候補は全てStage 2へ)。欠落IDは機械検査→再実行1回→なお欠落なら当該単位をCANDIDATE(sub_reason=`coverage_gap`)としてStage 2へ。
  3. **5-lite(Ledger→記事方向)**: 同じ単位IDを使う1 call。各Ledger factについて「対応する単位IDを全て列挙し、各々一致/逸脱(逸脱なら上記CANDIDATE形式)」を返す。fact未対応は許容(新規主張は3'-Rが担う)。
  4. **∪**: 2経路のCANDIDATEを単位ID(+同文グループ)で重複排除して合流→Stage 2へ。経路別の出力は監査ログに保持(経路別検出率・相関を集計できる形)。
  5. **決定論検査(OK判定の検査、候補生成ではない)**: SUPPORTED単位について (i)単位内の数値が引用fact内に無い (ii)単位に因果語があるのに引用factに因果記述(`causal_strength`等)が無い (iii)否定の極性不一致(既存否定語リスト) (iv)同文グループ内で判定不一致 → CANDIDATE(sub_reason付き)へ戻す。引用の実在検査(Ledger本文に逐語一致)も必須。主体名照合は対象外。
  6. **F3配線**: Stage 1非検出(候補0)でもprecheck・決定論floor・兄弟列挙を実行(runner L8203付近の早期returnの前に配線。スイッチ`F3_PRECHECK_ALWAYS`)。
  7. **H1是正(fail-closed)**: Stage 1 API失敗(`_stage1_api_failure`)はPASSへ抜けない: 再実行1回→なお失敗なら許可リスト`api_failure`でSTOP(後段の既存許可リスト関数へ)。連続失敗のcircuit breakerとの整合を確認。
  8. スイッチ: `STAGE1_MODE∈{legacy_v4a, coverage_union}`(既定legacy=rep30挙動不変)、`F3_PRECHECK_ALWAYS`、`STAGE1_FAIL_CLOSED`、`STAGE1_ROUTES∈{both, r3_only, r5_only}`(段階Aで経路別測定用)。モデルは`gpt-6-luna`(runner `MODEL`)。Trial計測用。
- **禁止**: Production正式path(`er003*`/`er009*`/`er010*`/`er012*`/`er019*`)変更禁止(importして読むのは可)。Checker V0/V4A promptの既存定数は変更しない(新promptは新module)。Stage 2(V7b・S1・floor)・後段は変更しない(F3配線・H1是正はrunnerのフロー制御のみ)。Safety-critical定義・gold・fixture変更禁止。有料API禁止(dry-runは偽LLM/記録出力)。`git add -A`/`stash`/`amend`禁止。既存M差分・untrackedに触れない。1回の書き込み2,500文字以下(コードは関数単位で分割Edit)。
- T-0: 委任ログ`docs/pm/delegation_log/2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_06.md`に全文保存(分割)、check実行・結果をhandbackに1行。
- 固定ブロックE-1/D-1/G-1/F-1/T-2/T-3は従来どおり。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。

## ユーザー指示(原文、該当部分)

````
2. Checker改善の基本原則
重大な問題に対してCheckerを甘くすることは禁止。…重大な問題は確実に拾う。重大でないものへの過剰検出はできるだけ減らす。
Safety KPIを良く見せるために、Safety-criticalの定義・gold・母数を都合よく変更してはならない。
4. 根本設計も検討対象 …QCD・単純性・既存資産再利用・非決定性・Production運用性を比較して、最も合理的な構造を設計すること。
7. Trialの評価方法 今回はfresh Stage 1を含むE2E評価を必須とする。
````

## 作業

1. T-0。
2. 設計メモ`docs/pm/design_open233_stage1_coverage_impl_01.md`(新規、実装仕様: 単位ID付与規則、関係単位規則、schema、prompt方針[網羅・候補寄り・逐語引用必須]、決定論検査規則、∪規則、F3/H1のフロー変更箇所[行番号]、スイッチ、監査ログ項目[経路別候補・欠落ID・再実行・検査で戻した件数・費用])。prompt本文はmodule内に定数として置き、sha256を記録。
3. 実装(上記1〜8)。既存runnerの変更は最小(Stage 1呼出分岐・F3・H1)。
4. ¥0検証: (a)単体テスト(分割・関係単位・同文グループ・schema検査・欠落ID検査・決定論検査(i)〜(iv)・∪重複排除・H1 fail-closed・F3配線・legacy不変)。(b)fixture dry-run(スクリプト`er052_open233_stage1_coverage_dryrun_01.py`): 全Trial fixture(SC 6 instance+B2_hormuz+hormuz_run01/02+neg1〜5+NORMAL群+er009合成9種)で分割を実行し、正式gold 6 claim(`SAFETY_CRITICAL_CLAIM_DEFS`)の文が単位IDに対応するか、neg5で「continued on July 14.」+「So the flashy 20% plan…」の関係単位が生成されるか、単位数/記事、同文グループ数を集計(json/md)。(c)偽LLM fixtureで、欠落ID→再実行→coverage_gap、API失敗→fail-closed、SUPPORTEDの引用不実在→CANDIDATE、を確認。(d)回帰: runner単体・er052回帰・全体回帰(基準11件以外新規なし)。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"` 0件。
5. 段階Aスクリプト作成(未実行)`er052_open233_stage1_stageA_01.py`: `STAGE1_MODE=coverage_union`、経路別(r3_only/r5_only)と∪を同じinstanceで取得(両経路の出力を1 runで保存し集計で分離可能なら1回の実行で可)。対象: SC 6 instance+B2_hormuz(監視)+負例/NORMAL 6をn=3、er009合成9種をhold-out n=1。集計: 正式SC 6件の経路別/∪検出(run単位)、見逃し相関表、NORMAL候補数/記事、欠落ID率、再実行回数、決定論検査で戻した件数、費用/call・合計。採用基準(事前固定): SC 6件∪3/3、hold-out新規見逃し0、欠落ID残存≤5%。`--budget-jpy`既定65。費用概算を出力。
6. commit/push(明示add: 新module、runner、テスト、dry-runスクリプト・出力、段階Aスクリプト、設計メモ、委任ログ+check.json)。メッセージ: `OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01: Stage 1再設計をTrial実装(文ID網羅3'-R+fact逆照合5-liteの2経路∪・関係単位・決定論検査・F3配線・H1 fail-closed、既定legacy不変)、fixture dry-run【gold 6対応 x/6・neg5関係単位 有/無】、段階Aスクリプト(未実行)(委任_06、¥0)`

## 事前指定Read一覧

runner: Grep `def run_stage1|stage1_fresh_with_enumeration|_stage1_api_failure|ACCEPTABLE_STAGE1|precheck|CAUSAL_SENTENCE_INITIAL_RE|vs_sentence_segments_l6|stage4_allowlist_decision|api_failure|KPI_TRIAL_SWITCHES|MODEL` → 範囲(全文Read禁止、構造変更箇所のみ広めに)。`er051_open233_checker_trial_variant_01.py`(V4A schema・10フラグ名の参照のみ)。`er003_v1_en_direct_vfl_01_generate.py`(判定方針の該当箇所、変更しない)、`causal_strength`。`split_family_x_article_text_v2`(Grepで所在特定)。fixture読込経路(`build_target_instances` L7661〜)。`docs/pm/design_open233_stage1_redesign_01.md`(案3'-R/5-liteの記述)。

## 事前指定Grep一覧+追記位置・更新位置の手順

新規ファイル作成+runnerの該当箇所のみEdit。SSOT編集なし。

## SSOT追記文

なし(SSOT編集禁止。委任_05が担当)。

## 実行コマンド全文

T-0 check: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_06.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01_06.md_check.json
テスト: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_stage1_coverage_checker_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py
dry-run: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_stage1_coverage_dryrun_01.py
Git: `git status --porcelain`→明示add→commit→`git push origin main`→`git log --oneline -1`。

## 報告(handback、短く)

(1)結論8行以内(実装範囲、dry-run結果: gold 6対応・neg5関係単位・単位数/記事、テスト件数、legacy不変確認)、(2)フロー変更箇所(行番号)とスイッチ、(3)段階A費用概算、(4)T-0・commit・push・raw URL(新module/runner/dry-run md)、一覧外Read、確認/推測、(5)Fableへの論点(段階Aへ進めるか、設計で判断が必要になった点)。

## 固定ブロック

E-1/D-1/G-1/F-1/T-2/T-3は従来どおり(本ログでは参照のみ)。
