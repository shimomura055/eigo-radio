## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_54)。並行タスクなし(委任_51〜53は終了)。

## 性質/到達上限Status/禁止事項

- 性質: (1)全体回帰の失敗件数が基準11件→12件に増えた原因の特定(read-only調査。修正はしない)、(2)委任_51〜53の結果とFable判断のSSOT反映、(3)委任_52の成果物のcommit、(4)委任_51〜53の報告の保存。
- 到達上限Status: `USER_DECISION_REQUIRED`(OPEN-233。ユーザー判断3点を提示してSTOP)。
- 禁止事項: コード・Prompt・テストの編集禁止(回帰の原因が本変更に起因しても修正せず報告)。LLM/API呼び出し禁止(¥0)。Production正式pathの変更禁止。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`の編集禁止。`git add -A`/`stash`/`amend`/`rebase`禁止。既存のM表示の差分(`er006_output`等、rep19のbudget state)に触れない。
- 費用上限: ¥0(T-3対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(調査と記録のみ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_54.md`。**委任文は全文そのまま保存(要旨化・参照形式は不可。委任_52・53は圧縮保存してFAILになった)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文、2026-10-03。全文は`DECISION_LOG.md`の2026-10-03エントリに逐語あり)

- 「この段階で、- 何が解決したか - 何がまだ残るか - USER_DECISION_REQUIREDが残るか - 次Trialへ進める状態か を報告してSTOPしてください。」
- 「**5記事×2レベルの次Trialは開始しないでください。**」
- 「真のMajor見逃しだけが、その後の対策対象です。」
- 「`PRODUCTION_WIRED`と判断するのは、既存Gateどおり…まで完了してからです。『Trialでは直っていたがProductionへ入れ忘れた』状態を禁止します。」

## 作業1: 全体回帰の失敗件数の差(11→12)の原因特定(修正はしない)

委任_42・49の基準は「既存の失敗11件: er003_test_bad、p2j 4件、er015 loader、er025、er040、er043、er011 3件」。委任_53(commit `74d805b9`時点)では「失敗6+エラー6=12件、er003/er011/er012/er015/er025/er040/er043」で1件増えた(委任_53は原因未確認)。
1-1. 現在の作業ツリーで全体回帰を1回実行し、失敗・エラーのテスト名を全件、ファイル名つきで列挙する。
1-2. 委任_49のcommit `78d56a5d`時点の失敗一覧と比較する。方法: `git worktree add <%TEMP%配下のパス> 78d56a5d` で別ディレクトリに基準を展開し(stashは使わない)、そこで**増えた1件のテストファイルだけ**を同じ`.venv`のpythonで実行して、基準でも失敗するかを確認する。終わったら`git worktree remove`で片づける。
1-3. 増えた1件が、(a)基準でも失敗する(委任_49の「11件」の数え方の差)、(b)委任_51〜53のcommit(`b7068028`・`f7e46b38`・`74d805b9`)で新たに失敗するようになった、(c)環境・時刻・外部依存による揺れ、のどれかを特定する。(b)の場合は、どのcommitのどの変更が原因かを`git log -p --stat`の範囲で示す(修正はしない)。er012のテストが新たに失敗している場合は、委任_53がer012を編集していないことを`git show --stat f7e46b38 74d805b9`で確認して書く。

## 作業2: 委任_51〜53の報告の保存

`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f9ae115b-0305-437d-ac2d-b452b22a5e2a\subagents\` の `agent-ab461ba7a9687e60a.jsonl`(委任_51)、`agent-a785a39f4bc460edf.jsonl`(委任_52)、`agent-a047a3cb72ff271ae.jsonl`(委任_53)から、SubagentHandbackに渡した最終報告本文をスクリプトで抽出し(委任_48・49と同じ方法。全文Readしない)、`docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_51_result.md`、`_52_result.md`、`_53_result.md`として保存する(冒頭に抽出元と改変なしの旨)。抽出できないものは作らず報告する。

## 作業3: SSOT反映(Fable判断を含む)

### 3-1. `DECISION_LOG.md` 末尾へ追記(そのまま使用。【】は実測値で埋める)

OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-03、委任_51〜54、ユーザー決定2026-10-03の反映結果とFable判断。`USER_DECISION_REQUIRED`で停止)

1. 線引きの補正と再分類(委任_51、`docs/pm/open233_materiality_criteria_2026-10-03.md`、`docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`): 見逃し候補23種類(すべて旧判定BLOCKING)を新しい線引きで再分類。過剰品質17/23、真の重大見逃し1/23(K19「Just after the charge plan disappeared, prices began to fall.」HF-009、境界)、軽微8/23、問題なし9/23、新判定が重大で見逃し0が5/23。入れ子3種類を除く20種類では、過剰品質17/20、真の重大見逃し1/20、軽微8/20、問題なし9/20。過剰品質17のうち8種類は、LLM判定がACCEPTABLE/QUALITYで決定論floorだけがBLOCKINGにしたもの(floorは変更しない)。
2. K19の原因切り分け(委任_51): 1周目で完全に見逃し(固定Stage 1出力に無い)。再検査で文が残った約12回中1回のみ指摘。Rewrite起因ではない(日本語原文が起点)。Checkerと判定役の基準の食い違いは証拠なし(Stage 2が見た唯一の回はBLOCKINGで一致)。Production現行のChecker出力はK19をMAJORで指摘できていた。MINORで拾っていたかは記録が無く確認不能。
3. 線引き案への指摘(委任_51、7点)のうちFableが重要と判断したもの: 「迷えば実害で決める」は既存の「迷えばBLOCKING」(fail-closed)と逆向きで、判定役へ適用すればSafety原則の変更に当たる。Fableは判定役を変更していない(線引きは評価・ラベル用の文書化に留めた)。判定役と線引きの不整合は4箇所(V4原則の一律BLOCKING、disclosure_gap降格の否定形限定、production rubricの「動機の帰属=QUALITY」、「迷えばBLOCKING」)。
4. 句読点差対策のProduction反映準備(委任_52、`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md`): Family XのProduction正式経路にはCheckerの引用を記事内で探す処理が無く、反映先が無い。位置特定を行うProduction処理は`er010_ledger_local_rewrite_09.py`の`locate_target_sentence`(完全一致→単語重なり0.25)で、Discovery Focus・N3・B-family voicesが呼ぶ。Production記録では句読点差のみの不一致は0件(標本小、sentence_fallback 67件は原因未判定)。Fable判断: ユーザー意向は「Self-Recovery FlowをProductionへ接続する際の必須項目」として追跡する(`OPEN_ITEMS.md`に`OPEN-233-A1-PROD`を新設、Status=`APPROVED_FOR_PRODUCTION`[ユーザー意向、2026-10-03]・approved-but-unwired)。接続時はL0〜L3の単語境界・L5・label_onlyを一体で取り込み、初回・Rewrite周回・Recheck・retry/fallback/regenerationが同じ照合を通ること、含めずに接続した場合は`PRODUCTION_WIRED`としないことを条件にする。接続前にOpus独立レビュー条件Cに該当。er010の`locate_target_sentence`への同等処理は別の仕様変更であり、ユーザー判断事項として提示する(今回は実装しない)。
5. 日本語本文を直さないことの実害(委任_52): 実害あり1系統(Production再生成がer012_e L361・365・403〜404/er019 entertainment runner L358〜397で古い日本語R2から英語を再翻訳し、直した誤りが戻りうる。ただし再生成後は必ず`run_deviation_check`を通る。最小対策=既存で足り、接続仕様に「再生成後も必ずSelf-Recovery Flowを通す」を明記)。整合だけ2、影響なし5。日本語タイトルは英語記事を入力にせず、変更なし前提(ユーザー決定)。`JA_MODE=english_only`はユーザー方針3点を満たす。Production採用時は「忠実英訳」(CURRENT_SPEC L1272〜1278)・「案B」(L1242〜1257)と衝突する可能性が高く、その時点でユーザー判断が必要。
6. 説明文混入12件(委任_53): 主因は出力形式10・Prompt2・後段処理0(推定)。Trial専用`CHECKER_SPANS_MODE=violation_spans`(既定legacy)を実装(テスト406→418件PASS、er052回帰462件PASS)。Stage 1のみの限定確認(6記事×2腕×n=3、¥14.99): 特定不能は対照0/24・処置0/24(説明文混入はStage 1では再現せず。12件中8件はRecheck出力)、配列要素は35/35確定、費用ほぼ同じ(¥0.412/¥0.421)、Human Review増0。一方、BLOCKING fact検出は対照12/18→処置8/18、false PASSは対照1/15→処置4/15と悪化方向(n=3、対照どうしの一致率0.67で揺れ大)。**Fable判断: `VALIDATED`にしない。既定OFFのまま。ユーザー確認項目「検出漏れが増えないか」「false PASSが増えないか」を満たしたと言えないため、現時点では採用しない。** 実装は設計書§3の形と同じだが機構が異なる(claim dictにlistを持たせる設計に対し、claim文字列を鍵にしたモジュール内の対応表`_VS_SPANS_REGISTRY`で配列を引く)。有効化する場合はclaim dictへ配列を載せる形へ直すこと(同一文字列の衝突・隠れた状態を避けるため)。
7. 予算: 委任_53 ¥14.9926。Phase累計¥530.0107、上限¥900、残¥369.9893。
8. 回帰: 【作業1の結果】。
9. 全体の状態: 次Trial(5記事×2レベル)は未開始・開始禁止。`USER_DECISION_REQUIRED`としてSTOP(判断事項は`OPEN_ITEMS.md`と`ACTIVE_TASK.md`に記載)。

### 3-2. `OPEN_ITEMS.md`

- OPEN-233行のStatusセルを「`USER_DECISION_REQUIRED`(2026-10-03、委任_54): 再分類完了(過剰品質17/23、真の重大見逃し1/23[K19、境界])。句読点差対策はProduction反映先なし→`OPEN-233-A1-PROD`で接続時必須項目として追跡。日本語本文は直さない方針で整理済み(実害1系統は既存Checkerで検知)。説明文混入の出力形式変更は限定確認で検出・false PASSが悪化方向のため不採用(既定OFF)。ユーザー判断3点(K19の重大度/判定役を新しい線引きへ合わせるか/出力形式の再確認の要否)待ち。次Trial開始禁止。`VALIDATED`ではない。Production未接続。」に更新し、直前のStatusは「旧Status参考(委任_51)」として残す。
- 次Actionセルへ追記: 「(委任_54)ユーザー判断3点の後: 判断1でK19が重大なら1周目の検出力の対策を設計(Opus条件A)。判断2で判定役を合わせるなら、Meta-1/Meta-2のSafety-critical登録解除・V4原則文の修正・disclosure_gap降格の肯定形拡張を、Safety対照セットで再較正(過去水準¥5〜10)。その後、英語だけ修正(`JA_MODE=english_only`)と照合の追補(`VS_MATCH_EXT`)を有効にした限定flow確認→29件横断→ユーザー確認→次Trial(5記事×2レベル)。」
- 新規行`OPEN-233-A1-PROD`を追加: 案文は`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md`のA-5節の完全版を使う(Grep `A-5`で位置特定)。Status語彙は既存に合わせ、「`APPROVED_FOR_PRODUCTION`(ユーザー意向2026-10-03、Gate 3未着手、`PRODUCTION_WIRED`未達、approved-but-unwired)」とする。

### 3-3. `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考へ追記

「2026-10-03 委任_51〜54: ユーザー決定反映(線引き補正・再分類・日本語本文は直さない・句読点差対策はA1-PRODで追跡・出力形式変更は不採用)。`USER_DECISION_REQUIRED`。」

### 3-4. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §38

「§38 2026-10-03ユーザー決定の反映(委任_51〜54)」として、3-1の1〜9を、各成果物のパスと委任_53の集計表(対照/処置の7項目)つきで記載する。

### 3-5. `docs/pm/design_open233_countermeasures_after_handoff_01.md` 末尾(付録の前)に「12-2. 2026-10-03ユーザー決定後の採否(委任_51〜54)」を追記

対策A1(L5)=ユーザー正式採用意向→`OPEN-233-A1-PROD`で追跡/A2-a・単語境界=Trialで実装済み(既定OFF)/B=不採用(限定確認の結果、機構の差の記録、有効化時の条件)/C=K19の扱い待ち/D=`english_only`はユーザー方針を満たす(補正つき、Production採用時の衝突点)。

### 3-6. `docs/pm/ACTIVE_TASK.md`

固定ヘッダのStatusを`USER_DECISION_REQUIRED`にし、判断3点(判断1: K19「Just after the charge plan disappeared, prices began to fall.」を重大とするか軽微とするか/判断2: 判定役[Stage 2のV4原則文・disclosure_gap降格の範囲・Meta-1/Meta-2のSafety-critical登録]を新しい線引きへ合わせる再較正を次Trial前に行うか/判断3: 出力形式変更の再確認[Recheck文脈]を行うか、見送るか)を記載する(addしない)。

## 事前指定Read一覧

- `docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md`: Grep `A-5` → 案文の範囲。
- `OPEN_ITEMS.md`: Grep `OPEN-233` → 該当行だけ。新規行の挿入位置は、OPEN-233行の直後。
- `DECISION_LOG.md`・`docs/pm/REPORT_LEDGER.md`・`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`・設計書: 末尾/該当行の追記位置だけ(全文Read禁止)。
- `run_project_regression.py`: 引数の確認だけ(Grep `argparse`/`--pattern`)。
- `docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_49_result.md`: Grep `失敗` → 基準11件の記述。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のとおり。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_54.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_54.md_check.json

全体回帰(1回):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

基準の展開(例。パスは%TEMP%配下の実パスにする):
git worktree add C:\Users\tensh\AppData\Local\Temp\o233_base_78d56a5d 78d56a5d
(増えた1件のテストファイルだけを `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest <テストモジュール名>` でそのディレクトリ内から実行)
git worktree remove C:\Users\tensh\AppData\Local\Temp\o233_base_78d56a5d

回帰後に`git status --porcelain`で意図しない変更(`budget_state_c233an_42_rep22.json`等)が出ていたら`git checkout -- <file>`で戻し、commitに含めない。

## SSOT追記文

作業3のとおり。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾、`OPEN_ITEMS.md` OPEN-233行と新規行、`docs/pm/REPORT_LEDGER.md` OPEN-233行)。
- 明示add対象(1ファイルずつ): `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/design_open233_countermeasures_after_handoff_01.md`、`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md`、`docs/pm/delegation_log/2026-10-03_OPEN-233-SELF-RECOVERY-TRIAL-01_52.md`、同`_check.json`、`_51_result.md`、`_52_result.md`、`_53_result.md`、`_54.md`、`_54.md_check.json`。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- commit前に`git status --porcelain`で確認。コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 2026-10-03ユーザー決定の反映結果を統合(再分類・A1のProduction追跡項目OPEN-233-A1-PROD新設・日本語本文は直さない整理・出力形式変更は不採用)、回帰差分の原因を記録、USER_DECISION_REQUIREDでSTOP(委任_54)`。`git push origin main`まで。競合・エラーは自動解決せず報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内、(2)作業1の結果(失敗一覧、増えた1件の特定、(a)/(b)/(c)のどれか、根拠)、(3)作業2の保存結果、(4)作業3の更新内容(OPEN-233-A1-PROD行の最終文言を逐語)、(5)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別。
