## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_47)。並行タスク: 委任_48(対策設計書の作成と、委任_43〜46の成果物のcommit)が同時に動く。委任_48は`docs/pm/design_open233_countermeasures_after_handoff_01.md`の新規作成と`git add`/`commit`/`push`を行う。本委任はgit操作をせず、下記の新規ディレクトリと委任ログ以外のファイルを作らない・編集しないことで衝突を避ける。

## 性質/到達上限Status/禁止事項

- 性質: read-onlyの照合(限定Trial rep22の記録を、プロジェクトの正解ラベルと突き合わせる)。Fableが委任_42のTrialを REJECTED / VALIDATED / USER_DECISION_REQUIRED に分類するための材料。
- 到達上限Status: なし(Status変更なし。分類はFableが行う)。
- 禁止事項:
  - コード・Prompt・SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・設計書・REPORT・`ACTIVE_TASK.md`・`RESULT_PACKET.md`の編集禁止。
  - LLM/TTS/ASR/Web Searchの呼び出し禁止(費用¥0)。Trialの再実行禁止。
  - `git add`/`commit`/`push`/`stash`/`amend`禁止。作成ファイルは未追跡のまま残す。
  - 報告用の`.md`ファイルは作らない。報告は最終メッセージ本文で返す。
- 費用上限: ¥0(API呼び出しなしのためT-3は対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(read-onlyの照合で、構造変更の設計・実装を含まない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足(本委任での実値): 保存先は `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_47.md`。受領した委任文を全文・見出しを省略せずそのまま保存すること(要約保存は不可)。結果は`RESULT_PACKET.md`ではなく最終メッセージに1行で書く。

## ユーザー指示(原文)

今回のフェーズのユーザー指示全文は`DECISION_LOG.md`末尾付近(委任_42が逐語で追記済み、Grep `委任_42`で位置特定)にある。本委任に関係する部分の原文:

- 「Trial終了時には、REJECTED / VALIDATED / USER_DECISION_REQUIRED のいずれかへ分類してください。VALIDATEDでもProduction採用ではありません。」
- 「単に1回TrialがFAILした、1つ新しい変種が出た、という理由だけでは戻さず、Guardrail内で原因特定→対策→限定再確認まで進めてください。」
- 「Production正式pathは変更禁止です。Trial/検証用の範囲で進めてください。」

限定Trialの成功条件5項目の原文も同じ箇所にある。照合の際は、その原文を逐語で引用してから当てはめること。

## 背景(分かっていること)

- 委任_42(commit `850cfe3f`)が受け渡し修正を実装し、限定Trial rep22を実行した。出力は`er052_output/open233_self_recovery_flow_runner_01_rep22/`(`analysis_rep22.json`、`summary_rep22.json`、各instance JSON、是正前T3の`instances_safety_a_run1_before_carry_forward_fix`)。
- 委任_42の報告: T1(固定Stage 1、`meta_run03_standard`、n=4)は s1・s3・s4 が`RESOLVED_REWRITE_THEN_DOWNGRADE`、s2が`STAGE4_ESCALATION`/`cycle_limit_exhausted`。T2(n=2)は1周のみの再現。T3は是正後`RESOLVED_REWRITE`。「false PASS 0」と報告しているが、これは「検出済みのBLOCKINGが未解消のまま合格した例が0」という意味で、**正解ラベルとの照合ではない**。
- 委任_46(成果物`er052_output/open233_missed_detection_truth_check_01/`)で判明: `meta_run03_standard`の文「Also, some calls needed user information to continue.」(fact `MUSE-HC-010`)は、設計書`docs/pm/design_open233_self_recovery_flow_01.md`の正解ラベルでSafety-critical(BLOCKING維持、"Meta-1"、runnerの`SAFETY_CRITICAL_CLAIM_DEFS`にも登録)。固定Stage 1出力には含まれない。旧方式の固定入力7実行(iter8 s1/s2、rep19 s1、rep20 s1/s2、rep21 s1/s2)では、「文が元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終了」は1実行(rep21 s2)。委任_46の作業中(rep22生成途中)の観察では、rep22のs1・s3・s4は文が残り未指摘、s2は指摘あり、だった(未確定の途中観察)。

## 確認してほしいこと

### 問1: rep22の各実行は、正解ラベルに照らして「誤って合格」になっていないか

T1 s1〜s4、T2 s1〜s2、T3(是正後)の各実行について、次を表にする。
1-1. 最終状態(`final_state`、Stage 4理由)。
1-2. 最終EN記事に「Also, some calls needed user information to continue.」が元のまま残っているか(完全一致、空白正規化のみ)。変わっている場合は最終記事の該当文を逐語で示す。T3は別記事なので、その記事のSafety-critical定義(`SAFETY_CRITICAL_CLAIM_DEFS`の該当エントリ)で同じ確認をする。
1-3. その実行中に`MUSE-HC-010`が一度でもBLOCKINGで指摘されたか(周回番号つき)。
1-4. runnerまたはrep22スクリプトが`SAFETY_CRITICAL_CLAIM_DEFS`を使った評価(Safety-criticalな文が残ったまま合格していないかの判定)を実行しているか。実行している場合はその記録値、実行していない場合は「未評価」と書き、評価に使う関数名と所在だけ示す(Grep `SAFETY_CRITICAL_CLAIM_DEFS`)。
1-5. 結論として、「Safety-criticalな文が元のまま残り・一度もBLOCKINGで指摘されず・人間確認なしで終了」した実行の数を、新方式(rep22 T1の4実行)と旧方式(固定入力7実行、委任_46の`cases_01.csv`/`results_01.json`の値を再利用)で並べる。**途中観察を鵜呑みにせず、確定した記録から数え直すこと。**

### 問2: T1の`RESOLVED_REWRITE_THEN_DOWNGRADE` 3件(s1・s3・s4)の最終周回は妥当か

各実行の最終周回のRecheck指摘を全件、次の列で一覧にする(逐語): `related_fact_id`、`claim_in_article`、`issue`、Checkerの`severity`、trueのboolフラグ、Stage 2のLLM判定、最終判定、floor理由、降格の種類と理由(disclosure_gap降格など、適用された規則の関数名)。
- LLM判定がBLOCKINGだったのに規則でQUALITYへ降格したものがあれば、明示する。
- 同じ文・同じfactが、s2(Stage 4になった実行)や旧方式の実行でBLOCKINGになっているか(重大度の揺れ)を対応付ける。
- 設計書の正解ラベル(Grep `正解ラベル`、`Meta-`、`MUSE-HC-012`、`MUSE-HC-011`)に、その文がBLOCKINGとして拾うべき対象として載っているかを確認する。

### 問3: 成功条件5項目への当てはめ

`DECISION_LOG.md`にある成功条件5項目の原文を逐語で引用し、各項目について、委任_42の報告値(`analysis_rep22.json`)と、問1・問2の結果を当てはめて「満たす/満たさない/条件の読み方による」を示す。読み方による場合は、どの読み方ならどちらになるかを書く。**判定はFableが行うので、当てはめの材料と両方の読み方を示すこと。結論を一方に寄せない。**

### 問4: 新方式の副作用の有無(記録から分かる範囲)

4-1. T1の4実行と、旧方式の固定入力7実行について、周回数・call数・費用・成立した水準(①③④)を並べる(委任_42の`analysis_rep22.json`と、旧方式は委任_41の`claims_detail_01.csv`または各instance JSONから)。
4-2. T2で水準③が主体置換ガードで棄却された2件について、棄却の根拠になった語、その語が書き換え前の同じ段落に既に存在していたか、範囲(確定範囲)の内か外か、を逐語で示す。ガードの関数名と所在も示す。
4-3. `carry_forward_resolution`(委任_42が追加)が発動した1件(T3)について、先行claimと後続claimの`issue`を逐語で並べ、先行claimのRewriteが後続claimの`issue`も解消する内容だったか(後続の`issue`はRewriteの指示文に渡されたか)を、記録とコードから示す。

## 事前指定Read一覧

- `er052_output/open233_self_recovery_flow_runner_01_rep22/analysis_rep22.json` と `summary_rep22.json`: Pythonで必要キーだけ抽出。
- `er052_output/open233_self_recovery_flow_runner_01_rep22/` 配下の各instance JSON: スクリプトで該当フィールドだけ抽出(全文Readしない)。
- `er052_output/open233_missed_detection_truth_check_01/check_01.py`: 全文(照合ロジックを再利用するため。構造把握目的)。同`results_01.json`/`cases_01.csv`はPythonで必要行だけ抽出。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `SAFETY_CRITICAL_CLAIM_DEFS`、`carry_forward_resolution`、`collect_replaced_units`、主体置換ガード(Grep `actor` と `new_actor`/`subject`等で位置特定)→ 該当範囲だけRead。
- `er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py`: Grep `agg` と `SAFETY` → 集計部分だけRead。
- `DECISION_LOG.md`: Grep `委任_42` で位置特定 → 成功条件5項目の原文がある範囲だけRead(全文Read禁止)。
- `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `正解ラベル`、`Meta-1`、`6-18` → 該当範囲だけRead(全文Read禁止)。

一覧外のReadが必要になった場合は、理由を最終メッセージに1行で記録する。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `SAFETY_CRITICAL_CLAIM_DEFS`(対象: `er052_open233_self_recovery_flow_runner_01*.py`)。
- Grep `carry_forward`(対象: 同上)。
- Grep `委任_42`(対象: `DECISION_LOG.md`、`output_mode: content`、行番号つき)。
- Grep `正解ラベル`と`Meta-1`(対象: `docs/pm/design_open233_self_recovery_flow_01.md`)。
- 追記・更新: なし(本委任はSSOT・設計書を編集しない)。

## 実行コマンド全文

集計スクリプトは新規ディレクトリに作る(標準ライブラリのみ、既存モジュールをimportしない、LLM呼び出しなし)。

C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_rep22_truth_label_check_01\check_rep22_01.py

出力は `C:\Users\tensh\eigo-radio\er052_output\open233_rep22_truth_label_check_01\results_01.json` と `C:\Users\tensh\eigo-radio\er052_output\open233_rep22_truth_label_check_01\cases_01.csv`。

T-0:

C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_47.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_47.md_check.json

## SSOT追記文

なし(本委任はSSOTを編集しない)。

## Git(明示add対象・コミットメッセージ・trailer)

- `git add`/`commit`/`push`は行わない。作成ファイルは未追跡のまま残す。
- SSOT編集権: なし。

## 報告(RESULT_PACKET項目)

`RESULT_PACKET.md`には書かず、最終メッセージ本文で次を返す。

1. 結論(10行以内): 問1-5の数(新方式・旧方式)、問2で「LLM判定BLOCKING→規則で降格」が何件あったか、問3の5項目の当てはめの要約。
2. 問1の表、問2の一覧(逐語)、問3の当てはめ(原文引用つき)、問4。
3. 検算、限界・未確認点(確認できたことと推測を分ける)。
4. 読んだファイルと行範囲、一覧外の追加Read、T-0の結果、作成ファイルの絶対パス。

確認できなかったことは「未確認」と書き、推測で埋めないこと。委任_42の報告と食い違う事実があれば、食い違いをそのまま示すこと。
