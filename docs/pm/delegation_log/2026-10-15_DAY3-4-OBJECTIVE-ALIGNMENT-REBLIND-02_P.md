# 委任_P: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02(OAR-02)— Phase B準備: 未使用事例の選定と被験パッケージ構築(ケース選定役)

あなたは「ケース選定役」。採点はOpus、独立照合はFableが行う(役割分離)。Repo(`C:\Users\tensh\eigo-radio`)は**Read-onlyで扱う**(Repo内への書込はdelegation_log保存のみ。別案件がbranch上で作業中のためgit操作禁止)。成果物は**Repo外 `C:\Users\tensh\eigo-radio-replay\oar2\`** に作る。費用JPY0(API呼出0)。

## T-0
本委任文全文を `docs\pm\delegation_log\2026-10-15_DAY3-4-OBJECTIVE-ALIGNMENT-REBLIND-02_P.md` に保存(commitしない。委任_Qがまとめてcommit)。`check_delegation_prompt.py`→`_check.json`(FAILでも継続)。stop_scope_check rc=0確認。

## 背景(要点)
Day3〜4の盲検・再盲検では、被験Fable(`claude -p --agent sandwich-pm`)が欠陥②「失敗終了時に、ユーザーの品質要件を満たさない最終成果物を残すこと」を2/2で見逃した(事例はKey Phrase日本語gloss不整合)。原因: 受入記録(1)「当初目的」にユーザー原文でなく委任の作業目標を書き、承認済み設計どおりかの確認に置き換わった。今回は是正(ユーザー原文目的の必須引用/設計準拠≠目的適合)を反映した規則で、**未使用の別種事例**で再盲検1ラウンドを行う。

## ユーザー指定の選定条件(逐語)
- 「欠陥ケース：1〜2件/正常な陰性対照：1件」
- 「前回のKey Phrase日本語gloss不整合ケースは再利用しない。」
- 「異なる種類の成果物・品質要件を持つ、過去の未使用事例を選ぶこと。」
- 「できる限り、実際のユーザー要求と成果物が確認できる事例を利用する。」
- 「作為的に答えが明白なケースだけを選ばず、PMとして通常求められる目的適合性の判断能力を検証する。」
- 独立性: 「被験Fableには採点基準の正解・期待判定・欠陥位置を渡さない。採点者が使用する根拠資料は保存する。ケース選定時に未使用であることを確認する。」

## 事前指定Grep/参照
- 前回構成の正本: `C:\Users\tensh\eigo-radio-replay\`(`defect_case/`、`negative_control/`、`subject_settings.json`、`RUN_SESSION.ps1`、`NEUTRALIZATION_LOG_01.md`、`synthetic/_scorer_only/`)と `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/BLIND_REPLAY_RUNBOOK_01.md`・`REPLAY_FEASIBILITY_01.md`・`CRB_PHASE1_APPLIED_01.md`(中立化手順・deny設定・漏洩チェック手順)。
- 事例の探索元: `docs/pm/delegation_log/`(ユーザー原文の指示が`_USER`/各管理IDで保存されている)、`ER-*_REPORT.md`、`docs/pm/REPORT_LEDGER.md`、`OPEN_ITEMS.md`(Grep `失敗終了`/`最終成果物`/`残存`/`fallback`/`退避`/`STOP`等、全文読込禁止)、`er0XX_output/*/`の失敗終了run(ディレクトリ一覧とsummary/evidenceのみ。大量ログを読まない)。
- 使用済み(除外): gloss不整合事例(`ER-003-KP-GLOSS-ALIGN-02`/KGCPW/`run_kgcpw_z_*`/a337d8acc/c21cce27a/合成wd_*)。

## やること
### 1. 候補調査(4〜6件)
実在する過去事例から、次を満たす候補を4〜6件挙げる: (i)ユーザー原文の目的・品質要件が`delegation_log`等に残っている (ii)最終成果物(記事md/音声manifest/試聴ページ/レポート等)が確認できる (iii)欠陥候補=「処理・Fallbackは仕様どおり(test PASS・設計どおり)だが、最終成果物がユーザー原文の要件を満たさないまま残った/残り得た」状態が**自然に**再現できる(例: 速度・Voice・Prompt逐語・配置要件・件数・言語・Family固有例外などの要件不一致、失敗終了時の部分出力残存、代替品の無断採用) (iv)陰性候補=要件を満たした正常終了。gloss事例と成果物種別が異なること。各候補に「未使用確認(Grep結果)」「ユーザー原文の所在(ファイル:行)」「成果物の所在」「欠陥/陰性の性質」「答えの明白さ(低/中/高)」を付ける。
### 2. 選定
欠陥2件(可能なら成果物種別も互いに異なる)+陰性1件を選び、理由を書く。「答えが明白すぎる」候補だけを選ばない(明白さ中を1件以上含める)。事例の欠陥は**実際に存在したもの**を優先し、実在しない場合のみ最小限の合成改変(前回NEUTRALIZATION_LOGと同方式で記録)。
### 3. パッケージ構築(`C:\Users\tensh\eigo-radio-replay\oar2\<case_id>\`)
前回`defect_case/`と同じ構造: 被験が受入判定するために必要な範囲のRepo複製(規則ファイルは**委任_Oが`day3/OAR2_PHASE_A_APPLIED_01.md`に記録する改定後版**を同期。委任_Oが未完了なら、完了を待つか、同期手順をREADYにしてFableへ報告)、ユーザー原文、委任文(作業指示)、最終成果物、Sonnet役の完了報告(RESULT_PACKET相当。前回同様「技術的には仕様どおり・test PASS」と読める記述で、答えを示唆しない)、被験への起動指示(前回の`SUBJECT_TASK.md`相当: 「本委任の受入判定を行い、受入記録5項目を含む報告を出すこと」)。被験には正解・期待判定・欠陥位置・採点基準v3を入れない。前回結果(`_runs/**`、`BLIND_REPLAY_*`、`REBLIND_*`、`day3/`)と`oar2/_scorer_only/`はdenyに含める(`subject_settings.json`をoar2用にコピーして拡張)。
### 4. 採点者専用資料(`oar2/_scorer_only/`)
各ケースの`EXPECTED.md`: 正解判定(ACCEPTED/NOT ACCEPTED)、ユーザー原文の目的・品質要件の引用期待(ファイル:行)、欠陥位置と「なぜ技術準拠だけでは目的不適合か」、陰性の「不当差戻しとなる判定の例」、11-7(c)該当有無。`SELECTION_LOG.md`: 候補一覧・選定理由・未使用確認・中立化記録・パッケージsha256一覧。
### 5. 漏洩チェック
各パッケージ内をGrepし、`EXPECTED`/`正解`/`欠陥位置`/`採点`/`RUBRIC`/`v3`/前回run id等の語が0件であることを確認し、結果を`SELECTION_LOG.md`へ。
### 6. 起動準備
`RUN_SESSION.ps1`のoar2版(`RUN_OAR2.ps1`)を用意(`claude -p --agent sandwich-pm --settings <oar2 settings> --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose --max-budget-usd 4`、出力先`oar2/_runs/<id>/`)。`-CheckOnly`で起動可否のみ確認(本起動しない)。7項目事前確認(claude -p起動可否/モデル・ルーティング/課金経路/ツール権限・委任/独立性/漏洩なし/Repo・秘密情報不可)のチェックリストを`oar2/PRECHECK_01.md`に記入(実行は委任_Q)。

## 禁止
再盲検の本起動、Repo内ファイルの変更(delegation_log保存以外)、git操作、gloss事例の再利用、ユーザー原文の創作・要約置換(原文が無い候補は不採用)、正解情報の被験パッケージ混入。

## 報告様式(受入記録5項目)
(1)当初目的=上記ユーザー指定の選定条件の逐語 (2)実際の成果物(パッケージpath・sha) (3)証拠(候補表・未使用Grep結果・漏洩Grep結果・CheckOnly結果) (4)条件ごとの一致/不一致 (5)判定と理由。加えて: 選定3件の概要(Fable向け。**欠陥位置の詳細はFableにも書かない**—Fableは独立照合役のため、`_scorer_only/`のpathだけ示す)/委任_O同期の待ち状態/費用JPY0/逸脱。

(注: 本ファイルは委任文の保存。システム注記・Git attribution等は省略。)
