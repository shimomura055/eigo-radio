## 管理ID

`ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01` 再確認調査(委任_07、ユーザー緊急指示2026-10-15)。**Read-only調査限定**(新規Trial・TTS/ASR API実行・仕様変更・Production実装・SSOT編集すべて禁止。新たな問題が判明しても修正せず報告)。目的: ChatGPTが「③Secondary ASRの誤PASS対策・PASS_WITH_WARNING/試聴連動」「④数値・否定などの安全判定の是正」を未解決として再提示したが、ユーザーは既に判断・是正済みと指摘。10/12以降の決定・実装・報告を事実確認し、既決事項を再びUSER_DECISION_REQUIREDにしないための根拠表を作る。並行: Day3 委任_J(Repo外パッケージ・`day3/BLIND_REPLAY_RUN_LOG_01.md`のみ)。本委任のRepo内書込は`docs/research/ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01/REDETERMINATION_CHECK_01.md`(新規、dir新規可)と`docs/pm/delegation_log/`・`docs/pm/RESULT_PACKET_ASRX7.md`のみ。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/到達上限Status/禁止事項

- 性質: Read-only事実調査。到達上限: `INVESTIGATION_COMPLETE`。費用JPY0。
- 禁止: 上記。推測をPASS扱いしない(根拠のない項目は「未確認」と書く)。分類は4区分(`PRODUCTION_WIRED`=承認・実装・必要テスト・runtime evidence・SSOT・Git反映を確認済み/`APPROVED_FOR_PRODUCTION`=正式承認済みだが配線未完了/`VALIDATED`=Trial有効性確認済みだが正式採用未決定/`USER_DECISION_REQUIRED`=本当に新たな判断が必要)で、**ユーザー決定済みの事項をUSER_DECISION_REQUIREDに分類しない**。部分実装は完了部分と未完部分を分ける。git操作はadd対象のみ(git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f禁止)。
- 時間見込み: 約1.5h。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read(全文Readは`UNIFIED_FLOW_SPEC_V04.md`・`RECONCILIATION_FINAL_REPORT_01.md`の該当節のみ許可)。G-1: git出力最小化。F-1: transcript退避不要。
T-0(2026-09-13): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、check_delegation_prompt.pyを実行する。結果をRESULT_PACKETへ1行記録(FAILでも継続)。保存先: `docs/pm/delegation_log/2026-10-15_ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01_07.md`。
T-2: TTSなし。T-3: 費用0。

## ユーザー指示(原文・逐語)

# Claude Code／Fableへの緊急調査指示
## ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01：既決事項・是正済み事項の再確認

### 目的

10月12日の統一ASR/TTS設計について、ChatGPTが以下2項目を未解決事項としてユーザーに再提示した。

**③ Secondary ASRの誤PASS対策・PASS_WITH_WARNING／試聴連動**

**④ 数値・否定などの安全判定の是正**

しかしユーザーは、**これらは既に判断・是正したはず**と指摘している。

同じ議論・検証・意思決定を繰り返さないため、10月12日以降の決定・実装・報告を含めて事実確認すること。

### 調査範囲

- `ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01`
- `UNIFIED_FLOW_SPEC_V04.md`
- `RECONCILIATION_FINAL_REPORT_01.md`
- 10月12日以降の関連タスク・委任報告
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Decision Register
- Git履歴・Production Validator・ASR Routing実装
- Opusレビューと是正Closeout

**10月12日の古い報告だけで判断しないこと。最新のユーザー決定と実装状況を優先して確認する。**

### 調査① Secondary誤PASS対策

以下を確認する。

1. Secondary PASSの自動採用条件は最終的に何と決まったか。
2. `PASS_WITH_WARNING`と試聴連動は採用・実装済みか。
3. 固有名詞、語尾脱落、同形異音などの危険ケースはどう扱う仕様か。
4. 既存Validator、QA、Human Reviewのどこに反映されたか。
5. 実際のProduction正式経路で発火した証拠はあるか。

### 調査② 数値・否定の安全判定

以下を確認する。

1. 日本語の漢数字・算用数字の値一致／不一致は是正済みか。
2. 英語の `%`／`percent` 等の表記差・値変更は是正済みか。
3. 英語・日本語の否定表現保護は何が正式仕様か。
4. Primary／Secondaryそれぞれの判定で適用されるか。
5. 初回・retry・fallback・再生成の全経路に配線されているか。
6. テスト結果・runtime evidenceは存在するか。

### 必須の確認

各項目を以下のいずれかに分類する。

- **PRODUCTION_WIRED：** 承認・実装・必要テスト・runtime evidence・SSOT・Git反映を確認済み
- **APPROVED_FOR_PRODUCTION：** 正式承認済みだがProduction配線未完了
- **VALIDATED：** Trialで有効性確認済みだが正式採用未決定
- **USER_DECISION_REQUIRED：** 本当に新たなユーザー判断が必要

部分的に実装済みの場合は、完了部分と未完部分を明確に区別する。

**既にユーザーが決定した事項を、再びUSER_DECISION_REQUIREDにしてはならない。**

### 報告形式

非エンジニア向けに、次の表を最初に示すこと。

| 項目 | 最終ユーザー決定 | 実装状況 | 残課題 |
|---|---|---|---|
| ③ Secondary誤PASS対策 | | | |
| ③ 警告・試聴連動 | | | |
| ④ 数値の安全判定 | | | |
| ④ 否定の安全判定 | | | |

続いて、根拠となる決定日・管理ID・commit・ファイル・行番号を提示する。

最後に、**10月12日の統一フローをProduction採用するために、本当に残っている未決事項だけ**を抽出する。

### STOP条件

今回はread-only調査限定。

- 新規Trial禁止
- TTS／ASR API実行禁止
- 仕様変更・Production実装禁止
- 過去の承認事項について再承認を要求しない
- 新たな問題が判明しても勝手に修正せず報告

調査終了時にSTOPし、結果をユーザーへ報告すること。

**最重要：既決事項の見落としによって、ユーザーに同じ判断を繰り返し求める事態を再発させないこと。**

(ユーザー指示原文ここまで)

## 事前指定Read一覧・手順・成果物・Git・報告項目(要点保存。全文は委任文受領記録)

事前指定Read: UNIFIED_FLOW_SPEC_V04.md / RECONCILIATION_FINAL_REPORT_01.md / ACTIVE_TASK_..._D.md / 10/12-10/14関連delegation_log群 / DECISION_LOG / OPEN_ITEMS / USER_DECISION_REGISTER_01 / CURRENT_SPEC / 実装(PASS_WITH_WARNING等のpy) / runtime evidence / OPUS_FINDINGS_LEDGER / git log --since=2026-10-12。
成果物: docs/research/ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01/REDETERMINATION_CHECK_01.md (§0冒頭4行表 §1調査①5問 §2調査②6問+配線表 §3 4区分 §4真に残る未決のみ §5ChatGPT再提示理由推定 §6確認不能・矛盾)。
Git: 明示addのみ(成果物・本ファイル・_check.json)。コミットメッセージ「ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_07: 既決事項再確認(③Secondary誤PASS対策・警告/試聴連動、④数値・否定安全判定)のRead-only調査報告(4区分分類・根拠・真に残る未決事項)。SSOT/Production無変更、JPY0」、push origin/main。
報告: docs/pm/RESULT_PACKET_ASRX7.md に(1)T-0(2)冒頭4行表(3)要旨(4)4区分(5)真に残る未決(6)SSOT矛盾(7)commit/push/raw URL(8)確認不能事項。Fableが(2)(4)(5)を照合。
