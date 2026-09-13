## 管理ID
PM-CLOSEOUT-CONSOLIDATION-120

## 範囲
性質: SSOT反映+Git+read-only再棚卸し。¥0、API呼び出しなし。Productionコード(er0*)無編集。並行タスクなし。到達Status: 記録のみ(Gate判定語はFable確定済みの文言をそのまま転記)。禁止: `git add -A`/`stash`/`amend`/`rebase`、Trial系以外の未追跡差分の混入、SSOT既存行の削除。`git index.lock`があれば10秒待ち最大3回。

## 固定ブロック
---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 本委任文を`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-120.md`へ保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-120.md" --json-out "C:\Users\tensh\eigo-radio\docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-120_check.json"`を実行し結果をRESULT_PACKETへ1行記録(FAILでも継続)。
---

## ユーザー指示(原文)
> Closeout前に未処理USER_DECISION_REQUIRED、APPROVED_FOR_PRODUCTION未配線項目、未報告Trialがないかを再棚卸ししてください。

## 事前指定Read一覧
- `docs/pm/RESULT_PACKET_S2F.md`(全文、1回)
- `docs/pm/tool_uses_trial_log.md`(全文、1回、参照のみ)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. `OPEN_ITEMS.md`: Grep `-n` `^\| OPEN-135 \|`(範囲=次の`^\| OPEN-`行の直前)。範囲最終行末尾(閉じ`|`直前)へ追記(巨大行はPythonで安全に末尾追記可)。
2. `DECISION_LOG.md`: Grep `-n` `^## PM-CLOSEOUT-CONSOLIDATION-119|^## 参照元`(本文追記位置=`## 参照元`直前)。索引行は`CONSOLIDATION-119`索引行の直後に同形式で1行。該当行のみRead(前後3行)。
3. `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: 末尾10行のみ(`Get-Content -Tail 10`)。
4. 再棚卸し(read-only、編集しない): (a) `OPEN_ITEMS.md`をGrep `-n -o` `^\| OPEN-1[0-9][0-9] \|` で全OPEN IDを列挙し、各行の末尾400字を`-o`で取得して最新Statusを分類[今ユーザー判断が必要/既決・defer・低優先/WIRED・CLOSED]。(b) 同様に `APPROVED_FOR_PRODUCTION` を含み最新追記に `PRODUCTION_WIRED` を含まない行を列挙。(c) 未報告Trial: `Glob *_REPORT.md`のうち更新日が2026-09-13のファイル名を列挙し、各管理IDが`DECISION_LOG.md`にGrep一致するか(`-c`)を確認、一致0件のものを「未記録候補」として列挙。

## SSOT追記文(そのまま使用、日付2026-09-13)
### OPEN_ITEMS.md OPEN-135 末尾追記
「**追記(2026-09-13、FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01、Fable Gate 1判定=`VALIDATED`[Trial]、Production採用の承認ではない)**: ユーザー確定判断(S2を軸に完全版Trial、既存Production QAとの同等性確認、retry単位第一候補=通常Stage 1固定でStage 2-3のみ再実行・Main Story不適格時のみStage 1再生成、上限目安¥60〜90)に基づき実施。Trial専用パイプライン`er011_discovery_focus_s2_full_trial_01.py`(Stage 1新規Main Story生成+Stage 1 QA→Stage 2 Role Planning[Main Story本文入力、角度hintなし]→Stage 3 Point生成→Evidence Compression→結合→Overlap/Value QA retry[Stage 2-3単位]→記事全体Fact Checker/Ledger+Local Rewrite+差分QA→Directional Precheck)、Production関数は無編集でimport再利用、モック分岐テスト22件PASS。実行: A2/B1各1本、実費¥84.62(上限¥90)、両記事OK/Fact PASS/LEDGER_COMPLIANT。実発火: Stage 1 QA全て、Evidence Compression(両方applied)、A2で記事全体Ledger MAJOR 1件(locus=main_story)をLocal Rewrite cycle 1+差分QA PASSで解決(Stage 1再生成の一歩手前)。未発火(モック証明のみ): Overlap/Value retry、Stage 1再生成、Stage 2-3 exhaustion fallback、main_story locus escalation。角度多様性: Point Oneは異なる、Point Twoは同系統(習慣・行動差の軸、部分収束。案2の完全収束より軽度、前回S2の完全非収束より後退。Main Story自体が同じEvidenceに触れたことに起因する可能性、hint注入ではない)。競合なし(`run_one_pattern`不使用)、Dangling Referenceなし。残る問題: (1)retry分岐の実データ検証未達(意図的に問題を含むLedgerでの追加Trial要、費用要)、(2)`STAGE1_MAX_REGENERATIONS=1`は新規Trialしきい値でProduction値ではない、(3)Local Rewrite発火時はMain Story「完全固定」が成立しない(安全装置優先で許容)、(4)Fact Checker FAILのlocus分類は簡略ルール(未検証)。Discovery枠累計¥165.03/¥300。比較artifact: `er011_output/discovery_focus_s2_full_trial_01/index.html`(commit 0e4e914)。根拠: `FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01_REPORT.md`。次段階(Production設計着手可否、retry単位・しきい値の確定、retry分岐の実データ検証Trialの要否)はユーザー判断。」
### DECISION_LOG.md 新規エントリ(`## 参照元`直前)
「## PM-CLOSEOUT-CONSOLIDATION-120(2026-09-13)
FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01: ユーザー確定判断「S2を軸に、完全版Trialまで進めてください。(中略)最低限、以下を含めてください。Local Rewrite/Point Overlap・Point Value retry/Directional Precheck/Evidence Compressionを含むStage 3/retry・fallback・regenerationの整合/Main Story固定時のStage 2-3再実行/Main Story自体に重大問題がある場合のみStage 1からやり直す分岐/A2・B1間・複数記事間の角度収束確認/既存News・Trend・Discoveryとの競合確認。(中略)今回到達してよいStatusは最大VALIDATEDです。」に基づき実施。結果は上記OPEN-135追記のとおり。Gate 1: `VALIDATED`(Trial)。Production配線・CURRENT_SPEC正式化・APPROVED変更なし。実費¥84.62。commit 0e4e914。
再棚卸し結果は本エントリ末尾に表で記録(Fableが最終報告で確定)。」
索引行: CONSOLIDATION-119索引行と同形式で1行。
### docs/pm/MODEL_ROUTING_TRIAL_LOG.md 追記
「2026-09-13 FAMILY-A-DISCOVERY-FOCUS-S2-FULL-QA-PARITY-TRIAL-01: gpt-5.6-luna、¥84.62(A2/B1 Stage 1〜3+QA+Local Rewrite 1回)。」

## 実行コマンド全文
- `.venv\Scripts\python.exe docs/pm/tools/collect_subagent_transcripts.py --help`→表示引数で退避: taskId `a337646d619e598be a5ef5f43ca4b9df13`(tasks dir=`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks`、subagents dir=`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents`)
- `git status --porcelain`

## Git
明示`git add`: `OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-120*`、`docs/pm/transcripts/`追加分。コミットメッセージ`PM-CLOSEOUT-CONSOLIDATION-120: Discovery S2完全版Trial(VALIDATED、¥84.62)のSSOT反映+Closeout再棚卸し`、末尾に
```
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4
```
`git push origin main`まで(拒否時はエラー原文を報告し回避しない)。

## 報告
`docs/pm/RESULT_PACKET.md`へ20行以内: commit hash(full)/push結果、SSOT追記位置、T-0検証結果、退避結果、再棚卸し表(UDR候補/既決defer/APPROVED未配線/未記録候補REPORT)、一覧外操作の有無。最終メッセージ6行以内。
