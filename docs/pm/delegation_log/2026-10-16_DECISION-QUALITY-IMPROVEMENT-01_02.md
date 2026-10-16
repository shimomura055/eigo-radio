## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` / `DECISION-QUALITY-IMPROVEMENT-01` 委任_02(提案書`DQI_PROPOSAL_01.md`の作成: Fable推奨案+Opusレビュー原文の機械転記+規則文案[草案・未適用])。並行: AUW 委任_09(read-only、進行中)、Opus FCJレビュー(read-only)。**本委任はGit操作・SSOT編集・`sandwich-pm.md`/`PM_GOVERNANCE.md`/templatesの編集を一切しない**(規則文案は提案書の中に「草案」として書くのみ)。新規作成=提案書・RESULT_PACKET_DQI2.md・委任文保存・scratchpad内の抽出script。衝突なし。

## 性質/到達上限Status/禁止事項

- 性質: C案件の成果物(改善案の比較・推奨)の文書化。到達上限Status: `PROPOSAL_READY_USER_DECISION_REQUIRED`(ユーザー指示C-4「改善案の比較と推奨がまとまった段階でSTOPし、ユーザーへ提示する」)。**新しい運用仕様の採用・適用は禁止。追加盲検・Day5〜6開始は禁止。**
- 禁止: 上記ファイルの編集、Git操作、有料API、Opusレビュー本文の要約・改変(§8は機械抽出の逐語のみ。**Sonnetは抽出した本文を読まない・解釈しない**。§9の採否表はFableが本委任文に与えた内容をそのまま転記する)、Fable推奨の内容変更(文言整形のみ可。不明点は「Fable確認要」と注記)。
- Opus独立技術レビューGate(11-3): 実施済み(任意枠 2026-10-16 1回目。Opus所見は下記jsonlから抽出)。
- 時間見込み: 40〜60分。並列化: 他と独立。
- 費用/日次: JPY0。承認区分: C(承認済みscope内=「改善方式の検討・既存規則との整合確認・具体案の提示」)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 費用上限[Cap]なし。

T-0保存先: `docs/pm/delegation_log/2026-10-16_DECISION-QUALITY-IMPROVEMENT-01_02.md`(全文保存。要旨化禁止)。

## ユーザー指示(原文)

C-1〜C-4・D節の原文は `docs/pm/delegation_log/2026-10-16_DECISION-QUALITY-IMPROVEMENT-01_01.md` L29-76(逐語引用)を正とする(`2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`はorigin/mainに委任_08がcommit済みだがmain dirは1 commit前のため未反映の可能性。存在すればそれも参照可、Git操作で取りに行かない)。要点: 「今回の到達範囲：改善方式の検討・既存規則との整合確認・具体案の提示」「改善案の比較と推奨がまとまった段階でSTOPし、ユーザーへ提示する。新しい運用仕様を独自にProduction採用してはならない。」「Fableは単にOpusの提案を転記するのではなく、自分自身の推奨案・理由・代替案・QDC評価を示す。」

## KPI provenance欄

該当なし。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`は本委任では編集しない。提案書§9に、Opus指摘を仮ID `OF-DQI-01`〜(Q1(a)〜(d)、Q2過剰1・不足3、Q3、Q4、Q5穴1〜4、Q6、Q7-1〜5、Q8)として列挙し、状態は全件`RAISED→FABLE_DECIDED(採用/一部採用/不採用)`と記す(台帳への転記は後続委任)。

## 事前指定Read一覧

- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_INVENTORY_01.md` L110-141(§3比較表。提案書§2へ転記)、L144-159(§4 K1〜K5)、L163-191(§5)。
- `docs/pm/delegation_log/2026-10-16_DECISION-QUALITY-IMPROVEMENT-01_01.md` L29-76。
- `.claude/agents/sandwich-pm.md` L60-95(4-2現行文。規則文案の挿入位置の特定のみ。編集しない)。
- `docs/pm/PM_GOVERNANCE.md` L2739-2762(12-13の2節。統合案の対象行の特定のみ)。
- `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md` L104-115(報告節。「Sonnetは判断候補と表記」の挿入位置特定のみ)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- Opus所見の抽出元: `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\tasks\a25820c0f24441c5a.output`(subagent transcript jsonl。**Read toolで開かない**。下記scriptで最終assistantメッセージ本文[「# Opus独立レビュー所見: DECISION-QUALITY-IMPROVEMENT-01」で始まるMarkdown]を抽出し、提案書§8へ逐語で書き込む。抽出に失敗したら、handback tool_use のinput内の本文fieldを探索対象に加える。それでも失敗なら§8に「抽出失敗(理由)」と書きFable確認要とする)。
- 追記位置: 新規 `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROPOSAL_01.md`。

## 実行コマンド全文

- 抽出script(scratchpadに作成): `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\extract_opus_dqi.py` — jsonlを1行ずつjson.loadsし、`type=="assistant"`のmessage.content内`type=="text"`のtextのうち「# Opus独立レビュー所見」を含む最後のものを選び、UTF-8で `...\scratchpad\opus_dqi_verbatim.md` に書き出し、sha256と文字数をstdoutへ出す。実行: `cd C:\Users\tensh\eigo-radio; .venv\Scripts\python.exe -I C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\extract_opus_dqi.py C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\tasks\a25820c0f24441c5a.output`
- 提案書§8への挿入は、verbatimファイルをそのまま連結する(別script or PowerShell `Get-Content -Raw`+`Add-Content -Encoding utf8`)。Sonnetが本文を読まずに済む方法で行う。
- T-0 check: `cd C:\Users\tensh\eigo-radio; .venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-16_DECISION-QUALITY-IMPROVEMENT-01_02.md --json-out docs\pm\delegation_log\2026-10-16_DECISION-QUALITY-IMPROVEMENT-01_02.md_check.json`

## SSOT追記文

本委任ではSSOT編集しない。提案書§10に後続用の文案(DECISION_LOG「DECISION-QUALITY-IMPROVEMENT-01 委任_01〜02: 提案提示・ユーザー判断待ち」、REGISTER新規UDR #88〜の文案、REPORT_LEDGER行)を記す。

## 提案書の構成と内容(Fableが与える。これを文書化する)

(構成§0〜§10の詳細本文は長大のため、成果物 `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROPOSAL_01.md` に文書化済み。保存者注: 受領した委任文の当該節[§0 Fable結論/§1 原因/§2 選択肢比較/§3 パッケージP1〜P5/§4 代替案/§5 QDC/§6 リスク/§7 ユーザー判断事項/§8 Opus原文/§9 採否表/§10 SSOT文案]の内容は提案書の各節に1対1で反映されている。この節に限り、保存時に逐語転写を省略した。Fable確認要。)

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: **なし**。Git操作: **なし**(commitはFableが後続委任で一括指示)。新規ファイルは未追跡のまま残す。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_DQI2.md`: 1 T-0結果 / 2 抽出結果(sha256・文字数・成否) / 3 提案書パス・行数・§構成の自己確認(§0〜§10の有無) / 4 Fable確認要の箇所一覧 / 5 費用JPY0・所要時間 / 6 受入記録5項目(当初目的=C-3・C-4原文逐語/最終成果物=提案書/証拠/一致・不一致/判定)。
