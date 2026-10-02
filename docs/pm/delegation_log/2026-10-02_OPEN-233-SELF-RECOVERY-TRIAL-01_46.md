## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_46)。並行タスク: 委任_42(受け渡し修正の実装と限定Trial)が実行中で、`er052_open233_self_recovery_flow_runner_01.py`、同テスト、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/design_open233_self_recovery_flow_01.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET.md`、`er052_output/open233_self_recovery_flow_runner_01_rep22/` を編集・生成している。本委任はこれらを一切編集しない(読むのは可。ただしrunnerは編集途中の可能性があるので、行番号は自分でGrepして確認すること)。

## 性質/到達上限Status/禁止事項

- 性質: read-onlyの事実確認(既存記録の照合と集計)。対策設計の前提を固めるための確認であり、実装・Trialではない。
- 到達上限Status: なし(Status変更なし。OPEN-233は現状のまま)。
- 禁止事項:
  - コード・Prompt・SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)・設計書・`ACTIVE_TASK.md`・`RESULT_PACKET.md`の編集禁止。
  - LLM/TTS/ASR/Web Searchの呼び出し禁止(費用¥0)。
  - `git add`/`commit`/`push`/`stash`/`amend`禁止(作成ファイルは未追跡のまま残す)。
  - Production正式pathのファイルは読むだけ。
  - 報告用の`.md`ファイルは作らない。報告は最終メッセージ本文で返す。
- 費用上限: ¥0(API呼び出しなしのためT-3は対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(read-onlyの事実確認で、構造変更の設計・実装を含まない)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足(本委任での実値): 保存先は `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46.md`。**受領した委任文を全文・見出しを省略せずそのまま保存すること(要約保存は不可)。** 結果は`RESULT_PACKET.md`ではなく最終メッセージに1行で書く(`RESULT_PACKET.md`は委任_42が使用中)。

## ユーザー指示(原文)

今回のフェーズのユーザー指示全文は、`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_43.md` と `_44.md` に引用済み(必要なら該当箇所だけGrepして読む)。本委任に関係する部分の原文:

- 「今回、可能なものは**調査だけでなく対策＋限定確認まで**進めてください。」
- 「Production正式pathは変更禁止です。Trial/検証用の範囲で進めてください。」
- 「日本語は、エンターテイメント性のある英語記事を作るための手段。LedgerとのDeviationが英語側にあるなら、英語を直せばよい。」
- 「単に「日英整合を保ちたい」という理由だけなら、日本語まで遡って修正する必要はありません。」

## 背景(前の委任で分かっていること。再調査は不要)

- 委任_44(周回別の新規指摘の分析、成果物は`er052_output/open233_cycle_new_issue_analysis_01/`の`analyze_01.py`/`results_01.json`/`cases_detail_01.csv`): 2周目以降の新規BLOCKING 85行のうち、見逃し型がP2a 18行+P2b 16行。`meta_run03_standard`の英語記事にある文「Also, some calls needed user information to continue.」(fact `MUSE-HC-010`)は元記事に最初からあるが、固定したStage 1出力(`er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`)には含まれない。Recheckで指摘されたのは8回中4回。rep21 sample2はこの文が残ったまま「解消」で終わった。**この文が本当にLedgerからの逸脱かどうかは未確認。**
- 委任_43(日本語側の実害調査): 日本語本文はユーザーへ届かない。届くのは日本語タイトル行だけ(`er019_family_x_audio_production_runner_01.py` 133〜147行付近の`derive_japanese_title`、読み上げとプレイヤー表示)。Ledger逸脱が日本語タイトルへ入った例があるかは未確認。
- 委任_45(特定不能35件の分類、成果物は`er052_output/open233_handoff_log_aggregation_01/unverified35_classification_01.csv`): Checkerが**英語記事の見出し**を違反箇所として指摘した例が複数ある(neg1_meta_b3prod_a2の見出し「We Thought It Was AI—But There Was a Person Inside Meta’s Muse」、bgroup_B4の見出し「I Thought It Was an AI Call—But There Was a Person Inside? …」、hormuz_run03_standardの見出し「The Fee Plan Leaves, But High Oil Prices Stay」など)。

## 確認してほしいこと

### 問A: 「Also, some calls needed user information to continue.」は本当にLedgerからの逸脱か

A-1. `MUSE-HC-010`のLedger記載(fact本文、限定語・条件、出典の記載があればそれも)を逐語で示す。関連しそうな隣接fact(同じ内容に触れるもの)があれば、それも逐語で示す。Ledgerの所在はGrep(`MUSE-HC-010`)で特定する。
A-2. 記事側の該当文と、その前後各2文を逐語で示す(固定fixtureが参照するcycle1の英語記事本文)。対応する日本語記事の文も逐語で示す。
A-3. この文を指摘したRecheck 4回それぞれについて、`claim_in_article`、`issue`、`severity`、boolフラグ(`changed_scope`等、trueのものだけ)、Stage 2の判定(LLM判定と最終判定、floorや降格の適用有無)を逐語で一覧にする。指摘しなかった4回は、その周回のRecheck出力にMUSE-HC-010の指摘が1件もないのか、別の文で出ているのかを示す。
A-4. 判定。次の3区分のいずれかに分類し、根拠を書く。
  - 「逸脱である」: Checker Promptの逸脱定義(`er003_v1_en_direct_vfl_01_generate.py`の`DEVIATION_PROMPT_TEMPLATE`、Grep `DEVIATION_PROMPT_TEMPLATE`で位置特定)に照らして、Ledgerの記載と記事文の間に事実・範囲・数量・確度の差が具体的に指摘できる。
  - 「逸脱ではない」: Ledgerの記載の範囲内に収まっており、差を具体的に指摘できない。
  - 「判断が分かれる」: 読み方によってどちらとも言える。分かれ目になっている語句を具体的に示す。
  あわせて、逸脱である場合に重大度がBLOCKING相当かどうかを、Stage 2の判定基準(`er052_open233_self_recovery_stage2_production_01.py`のStage 2 Prompt、Grep `BLOCKING`で位置特定)とrunnerの決定論的floorの条件に照らして示す。設計書`docs/pm/design_open233_self_recovery_flow_01.md`に`meta_run03_standard`の正解ラベル(期待される指摘)の記載があれば、そこにMUSE-HC-010が含まれるかも確認する(Grep `MUSE-HC-010` と `正解ラベル`)。
  **これはあなたの判定であり、Checkerの多数決で決めないこと。Ledgerの文言と記事の文言を突き合わせて決める。**
A-5. `meta_run03_standard`の全実行(iter・repの全sample)について、(1)最終記事にこの文(またはその書き換え後の文)が残っているか、(2)その実行でMUSE-HC-010が一度でもBLOCKINGで指摘されたか、(3)最終結果(解消/降格/Stage 4など)を表にする。「文が元のまま残り、一度も指摘されず、解消で終わった」実行の数を数える。

### 問B: 見逃し型34行全体について、同じ形の「指摘されないまま解消」がどれだけあるか(上限の見積もり)

B-1. 委任_44の`cases_detail_01.csv`のP2a・P2b(34行)を、記事×fact×該当文で重複排除し、種類数を出す。
B-2. 各種類について、同じ記事(同じ固定fixture)を使った他の実行のうち、「その文が最終記事に元のまま残り、その実行中に一度もBLOCKINGで指摘されず、最終結果が解消(人間確認なし)で終わった」実行の数を数える。文の一致は文字列の完全一致(空白の正規化のみ可)で判定し、類似度は使わない。一致を確認できない場合は「確認不能」として別に数える。
B-3. 結果は「見逃しがあった場合に誤って合格になった可能性がある実行の上限」として報告する。各種類が本当に逸脱かどうかの個別判定は、件数が多ければ上位5種類(該当実行数が多い順)だけでよい。上位5種類については問A-4と同じ3区分で判定する。

### 問C: 英語の見出しが違反とされた場合、ユーザーへ届く日本語タイトルに同じ誤りが残るか

C-1. `derive_japanese_title`が日本語タイトルを何から作るかを、コードの該当行を示して説明する(日本語記事の1行目をそのまま使うのか、英語見出しから作るのか、別の入力か)。Trial runner(`er052_open233_self_recovery_flow_runner_01.py`)の自己修復フローの出力のうち、この関数の入力になるものはどれか(現状はProduction未接続なので「接続した場合に何が入力になるか」でよい)。
C-2. 既存記録の全BLOCKING指摘のうち、英語記事の見出し(`# `で始まる行)の全部または一部を違反箇所に含むものを数え、記事別・fact別に一覧にする(委任_41の`er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv`と各instance JSONを使う。見出し文字列との完全一致・部分一致で判定)。
C-3. C-2の各記事について、対応する日本語記事の見出し(1行目)を逐語で示し、英語見出しで指摘されたのと同じ内容(同じ事実の言い過ぎ・誤り)が日本語見出しにも入っているかを、種類ごとに「入っている/入っていない/判断が分かれる」で判定する。
C-4. 英語の見出しだけを直した場合に、日本語タイトルに誤りが残る経路が成立するかを結論として書く。成立する場合、考えられる対策の候補を挙げる(例: 英語見出しを書き換えた場合に限り日本語タイトルを英語見出しから作り直す、英語見出しを書き換えた記事は日本語タイトルを人間確認に回す、など。実装はしない。追加のLLM呼び出しの要否と、Production正式pathへの変更が必要かどうかを各候補に付ける)。

## 事前指定Read一覧

- `er052_output/open233_cycle_new_issue_analysis_01/analyze_01.py`: 全文(分類ロジックと入力の所在を知るため。構造把握目的)。
- `er052_output/open233_cycle_new_issue_analysis_01/cases_detail_01.csv`: Pythonで読み、P2a・P2b行とMUSE-HC-010行だけ抽出(全文Readしない)。
- `er052_output/open233_cycle_new_issue_analysis_01/results_01.json`: Pythonで必要キーだけ抽出。
- `er052_output/open233_self_recovery_flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`: Pythonで`deviations`の`related_fact_id`一覧と記事本文の所在だけ抽出。
- `er052_output/open233_handoff_log_aggregation_01/claims_detail_01.csv` と `unverified35_classification_01.csv`: Pythonで必要行だけ抽出。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `DEVIATION_PROMPT_TEMPLATE` で位置特定 → テンプレート本体の範囲(おおよそ502〜601行)をRead。
- `er052_open233_self_recovery_stage2_production_01.py`: Grep `BLOCKING` で位置特定 → Stage 2 Prompt本体(おおよそ40〜79行)をRead。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `floor` と `disclosure_gap` で位置特定 → floorと降格の条件の該当範囲だけRead(委任_42が編集中のため行番号は自分で確認)。
- `er019_family_x_audio_production_runner_01.py`: Grep `derive_japanese_title` で位置特定 → 関数本体と呼び出し箇所の該当範囲をRead。
- `docs/pm/design_open233_self_recovery_flow_01.md`: Grep `MUSE-HC-010` と `正解ラベル` → 該当範囲だけRead(全文Read禁止)。
- 各instance JSON(`er052_output/open233_self_recovery_flow_runner_01_*` 配下および委任_44の`analyze_01.py`が入力にしているディレクトリ): スクリプトで該当フィールドだけ抽出(全文Readしない)。

一覧外のReadが必要になった場合は、理由を最終メッセージに1行で記録する。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep `MUSE-HC-010`(対象: リポジトリ内の`*.json`/`*.md`、`er052_output/`は件数が多いので`output_mode: files_with_matches`で絞ってから) → Ledgerの所在を特定。
- Grep `derive_japanese_title`(対象: `*.py`) → 定義と呼び出し箇所。
- Grep `正解ラベル`(対象: `docs/pm/design_open233_self_recovery_flow_01.md`)。
- 追記・更新: なし(本委任はSSOT・設計書を編集しない)。

## 実行コマンド全文

集計スクリプトは新規ディレクトリに作る(標準ライブラリのみ、既存モジュールをimportしない、LLM呼び出しなし)。

```
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_missed_detection_truth_check_01\check_01.py
```

出力は同ディレクトリの `C:\Users\tensh\eigo-radio\er052_output\open233_missed_detection_truth_check_01\results_01.json` と `cases_01.csv`。

T-0:

```
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_46.md_check.json
```

## SSOT追記文

なし(本委任はSSOTを編集しない。SSOTへの記録は後続の委任でFableが指示する)。

## Git(明示add対象・コミットメッセージ・trailer)

- `git add`/`commit`/`push`は行わない。作成ファイル(委任ログ2点、`er052_output/open233_missed_detection_truth_check_01/`配下)は未追跡のまま残す。
- SSOT編集権: なし。

## 報告(RESULT_PACKET項目)

`RESULT_PACKET.md`には書かず、最終メッセージ本文で次を返す。

1. 結論(10行以内): 問A-4の判定(3区分のどれか)、問Bの上限の数、問C-4の結論。
2. 問A: A-1〜A-5(Ledger文言・記事文・Recheck出力は逐語)。
3. 問B: 種類数、種類ごとの該当実行数、上位5種類の判定。
4. 問C: C-1〜C-4(コード行の引用、日本語見出しは逐語)。
5. 検算(行数の合計が元データと一致するか)、限界・未確認点(確認できたことと推測を分けて書く)。
6. 読んだファイルと行範囲、一覧外の追加Read、T-0の結果(PASS/FAIL・reasons)、作成ファイルの絶対パス。

確認できなかったことは「未確認」と書き、推測で埋めないこと。
