## 管理ID

PM-CLOSEOUT-CONSOLIDATION-126
並行タスク衝突確認: 並行してEDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07(er013_*とer013_output/のみ、Git操作なし、ACTIVE_TASK/RESULT_PACKET.md不使用)が走る。本タスクはSSOT+docs/pmのみを扱い、er013_*に触れない。Git操作は本タスクのみ。RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。`docs/pm/ACTIVE_TASK.md`は本タスクが固定ヘッダ付きで上書きしてよい。

## 性質/到達上限Status/禁止事項

- 性質: SSOT登録(¥0、API呼び出しなし)。ユーザー指示によりDiscovery S2の量産単価上振れ問題をOPEN_ITEMSへ**Priority HIGH・意図的defer**として新規登録し、DECISION_LOGに記録、commit/push。
- 禁止: CURRENT_SPECの仕様変更(ユーザー指示: 不要)/Discovery Production仕様・コードの変更/改善Trialの開始/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/API呼び出し。
- STOP条件: push失敗3回→報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> Discovery S2自体はPRODUCTION_WIREDとして正式受入です。ただし、今回runtime evidenceで確認された「Point Overlap NG → Stage 2-3全体retryにより、A2量産単価がretryなし約¥32.71 → 実測¥55.30まで上振れした問題」は、現時点では対応しませんが、事業上無視できない問題です。必ず以下としてOPEN_ITEMSへ明示登録してください。Priority: HIGH/性質: Production量産コスト最適化/問題: Point Overlap retry時にStage 2-3全体を再実行するため、retryが量産単価へ大きく影響/現時点の実測: retryなし概算: 約¥32.71 / A2、retryあり実測: ¥55.30 / A2、上振れ要因の大部分がStage 2-3 retry/今回は改善Trialを開始しない/将来、量産実績を見ながら局所retry / reuse / cheaper replan等の選択肢を検討/Discovery Production仕様自体は変更しない。CURRENT_SPECに仕様変更として入れる必要はありません。OPEN_ITEMS / 必要ならDECISION_LOGに「意図的にdefer、高優先」と記録してください。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_S2H.md` L25-45(費用実測・Open Item候補の記述、数値の出典)。
2. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-147 ` → その行の直後(最終行番号の次)に新規行`OPEN-148`を既存行と同じ表書式で追加(下記①)。Grep `^\| OPEN-135 ` → 行末尾に「OPEN-148起票(量産単価上振れ、HIGH、意図的defer)」の参照1文を追記。
- `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-125` で直近エントリ位置・索引書式を確認 → 直後に新エントリ(②)+索引1行。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID=本タスク、Status=完了、UDR-blocking=なし、UDR-deferred=OPEN-148(HIGH、意図的defer)/OPEN-134/121(d)等既存、APPROVED未配線=OPEN-83/145/146(+OPEN-120 3Vゲート自然発火待ち)、STOP条件=なし、次アクション=Family C Trial-07完了待ち、報告単位Status: Discovery S2=PRODUCTION_WIRED(正式受入済み) / Family C=Trial-07実行中)。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-126.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-126_check.json`
2. `git status --porcelain` → `git add OPEN_ITEMS.md DECISION_LOG.md docs/pm/ACTIVE_TASK.md docs/pm/RESULT_PACKET.md docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-126.md docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-126_check.json` → commit → `git push origin main`(classifierブロック時は同一コマンドを最大3回再試行)。
(回帰実行は不要: コード変更なし。)

## SSOT追記文

① OPEN-148新規行: 「| OPEN-148 | **Discovery S2量産単価のretry上振れ(Production量産コスト最適化、Priority: HIGH、Status: DEFERRED[意図的defer、ユーザー判断2026-09-14])**: FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01のruntime evidenceで、Point Overlap QA NG時にStage 2-3(Role Planning+Points+Evidence Compression+QA)全体を再実行する構造のため、A2量産単価(Standard同期)がretryなし概算約¥32.71→retryあり実測¥55.30へ上振れ。上振れ要因の大部分はStage 2-3 retry(不使用round0=¥21.20)。背景: Point単独再生成はER-008-N8-FINAL-QA-HARDENING-21でProduction自動経路から外されている(OPEN-134関連)。ユーザー判断: 事業上無視できないが現時点では対応せず、改善Trialは開始しない。将来、量産実績を見ながら局所retry/reuse/cheaper replan等の選択肢を検討。Discovery Production仕様(CURRENT_SPEC)自体は変更しない。実測出典: `er011_output/discovery_s2_production_runtime_evidence_02/cost_summary.json`、`FAMILY-A-DISCOVERY-S2-PRODUCTION-HAPPY-PATH-EVIDENCE-01_REPORT.md`。 |」(既存行の列数・区切りに合わせる。列が多い場合は既存の他行の書式に従って空欄を埋める。)
② DECISION_LOG新エントリ: 「2026-09-14: PM-CLOSEOUT-CONSOLIDATION-126。ユーザー判断: Discovery S2はPRODUCTION_WIREDとして正式受入(確定)。量産単価上振れ問題(retryなし¥32.71→retryあり¥55.30/A2、Stage 2-3全体retry起因)をOPEN-148としてPriority HIGH・意図的deferで登録。改善Trialは開始しない、CURRENT_SPEC変更なし。」

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: 上記コマンド2のとおり6ファイルのみ。er013_*・無関係既存差分はaddしない。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-126: OPEN-148起票(Discovery S2量産単価のStage 2-3 retry上振れ、HIGH・意図的defer)+Discovery S2正式受入の記録` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash(full)・push結果、2) OPEN-148の追加位置(行番号)とOPEN-135参照追記位置、3) DECISION_LOG追記位置、4) T-0結果・事前指定外Read、5) ACTIVE_TASK更新済み、6) STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(er013不可・並行側Git操作なし)
