## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_50)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: SSOTと一時ファイルの記録更新のみ(Fableが`USER_DECISION_REQUIRED`としてSTOPする判断をしたことの記録)。実装・Trial・測定はしない。
- 到達上限Status: `USER_DECISION_REQUIRED`(OPEN-233)。`VALIDATED`ではない。Production採用ではない。
- 禁止事項: コード・Prompt・テストの編集禁止。LLM/TTS/ASR呼び出し禁止(¥0)。Production正式pathの変更禁止。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`の編集禁止。`git add -A`/`stash`/`amend`禁止。既存の未commit差分(M表示ファイル、他の未追跡ファイル)に触れない・addしない。下記の追記文を言い換えない(【】の指示部分を除き、そのまま使う)。
- 費用上限: ¥0(API呼び出しなしのためT-3は対象外)。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 非該当(ドキュメント更新のみ)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

T-0の補足: 保存先は `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_50.md`。受領した委任文を全文そのまま保存すること(圧縮・参照形式への置き換えは不可。委任_49では一部を圧縮保存してしまったので、今回は全文)。

## ユーザー指示(原文)

- 「以下の場合のみUSER_DECISION_REQUIREDとしてSTOPしてください。- 新しいProduct原則の採用が必要 - Safety原則の変更が必要 - Production正式仕様の変更判断が必要 - ¥600予算上限超過が必要 - Claude案とOpusレビューが重要点で対立し、Fableで解消できない - 複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要」
- 「Trial終了時には、REJECTED / VALIDATED / USER_DECISION_REQUIRED のいずれかへ分類してください。VALIDATEDでもProduction採用ではありません。」

## 事前指定Read一覧

- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダ部分(冒頭〜Status行)だけ。
- `OPEN_ITEMS.md`: Grep `OPEN-233` で該当行だけ。
- `DECISION_LOG.md`: 末尾の追記位置だけ(全文Read禁止)。
- `docs/pm/REPORT_LEDGER.md`: Grep `OPEN-233` で該当行だけ。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `^## 36`または`§36`で末尾の追記位置だけ。
- `er052_output/open233_detector_direct_compare_01/results_01.json`: 下の追記文の数値(検出器×本文の集計、費用)が記録と一致するかを、Pythonで必要キーだけ抽出して確認する。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダのStatusを`USER_DECISION_REQUIRED`にし、下の「判断事項」3点を記載する(一時ファイル、addしない)。
- `OPEN_ITEMS.md`: OPEN-233行のStatusセルを下の文言に更新し、直前のStatus文言は行内に「旧Status参考(委任_49)」として残す。次Actionセルへ下の文言を追記する。
- `DECISION_LOG.md`: 末尾に下のエントリを追記する(既存エントリは編集しない)。
- `docs/pm/REPORT_LEDGER.md`: OPEN-233行の備考へ1文追記する。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: 末尾に§37を追記する(下のDECISION_LOGエントリと同じ内容)。
- 追記文の数値が`results_01.json`と食い違う場合は、追記せずに食い違いを報告する。

## 実行コマンド全文

C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_50.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_50.md_check.json

テスト・回帰の実行は不要(コードを変更しないため)。

## SSOT追記文

### DECISION_LOG.md 末尾へ追記

OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-02、委任_50、Fable判断: `USER_DECISION_REQUIRED`としてSTOP。ユーザーの新しい決定ではない)

1. 分類: 今回フェーズ(受け渡し修正+限定Trial rep22+対策)は **`USER_DECISION_REQUIRED`**。`VALIDATED`ではない。Production採用ではない。
2. STOPの根拠(ユーザー指示のSTOP条件のうち3つに該当):
   - 「Safety原則の変更が必要」: `meta_run03_standard`の文「Also, some calls needed user information to continue.」(MUSE-HC-010)は、設計書の正解ラベル(Fableのラベル判定、設計書§4-21・委任_29)では必ず重大として拾う対象。一方、Production Checker Prompt(er003 533〜534行)は近い型を「MINORとして記録」と定めている。検出器の直接比較(委任_49、固定本文、該当文が残る本文P1〜P5)では、現行Recheckが該当文を重大で指摘 3/8・指摘なし 5/8、現行Stage 1相当が重大 2/10・指摘なし 8/10、factごとに確認させる候補Promptが重大 4/10・軽微 4/10・指摘なし 2/10。該当文を安定して拾うには、軽微の指摘を判定役へ渡す変更が必要で、これは「何を重大として扱うか」の原則の変更に当たる。
   - 「複数の合理的な設計案に明確なQCDトレードオフがあり、ユーザー判断が必要」: 該当文を重大として扱い続ける案は、合格直前の追加検査(実測単価¥0.72/回)と軽微の指摘の取り込みが必要で、費用・書き換え・人間確認が増える。軽微(品質改善)として扱う案は、追加の検査が不要になる代わりに、条件つきの内容を断定で書いた文が記事に残る。
   - 「¥600予算上限超過が必要」: Phase累計¥515.0181、残り¥84.9819。検査の実測単価は見積もり(¥0.32〜0.36)より高い(¥0.51〜0.72)。重大として扱い続ける案は、追加検査の限定確認と29件横断(追加検査つき)で残額を超える見込み。
3. 判断事項(ユーザーへ提示):
   - 判断1: 「条件つきの懸念を、起きたこととして書いた文」(該当文)を、必ず止める重大な逸脱として扱うか、品質改善(軽微)として扱うか。
   - 判断2: 「They enjoyed AI’s convenience, but a human was on the other end. They did not realize it.」(MUSE-HC-012、開示がなかったことから利用者の認識を推論した否定形の文)を、既存の降格ルール(Trial限定の判定候補、設計書1228〜1246行)どおり軽微として記事に残してよいか。
   - 判断3: 判断1で「重大として扱う」を選ぶ場合の予算上限の引き上げ。
4. 委任_49までの到達点: 受け渡し修正(委任_42)は維持。評価・記録の追加、照合の追補(`VS_MATCH_EXT`)、英語だけ修正(`JA_MODE=english_only`、補正つき)は実装済み・既定OFF・flowでは未確認。Opus独立レビュー#6の指摘どおり、合格の判定が1回の検査結果に依存する構造は未対策。
5. ユーザー判断が出るまで、実装・Trial・測定を進めない。

### OPEN_ITEMS.md OPEN-233行

Statusセル: 「`USER_DECISION_REQUIRED`(2026-10-02、委任_50): 受け渡し修正は維持。限定Trial rep22は成功条件『誤って危険な記事をPASSしない』未達(正解ラベルで重大な文が未指摘のまま合格 3/4)。検出器の直接比較で、現行の検査は該当文を多くの回で指摘せず(現行Recheck 重大3/8)、factごとに確認させる候補でも重大4/10・軽微4/10。ユーザー判断3点(該当文の型を重大として扱うか/降格ルール対象文を軽微で残すか/予算)待ち。`VALIDATED`ではない。Production未接続・Production採用ではない。」
次Actionセルへ追記: 「(委任_50)ユーザー判断待ち。判断後: 重大として扱う場合=合格直前の検査と軽微の取り込みを設計(Opusレビュー要)→限定確認→29件横断。軽微として扱う場合=正解ラベルを改め、英語だけ修正と照合の追補を有効にして限定flow確認→29件横断(1回)。」

### docs/pm/REPORT_LEDGER.md OPEN-233行の備考へ追記

「2026-10-02 委任_50: `USER_DECISION_REQUIRED`(該当文の重大度の扱い・降格ルール対象文・予算)。」

### OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md §37

「§37 `USER_DECISION_REQUIRED`としてSTOP(委任_50)」として、上のDECISION_LOGエントリの1〜5を記載する。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: あり(`DECISION_LOG.md`末尾追記、`OPEN_ITEMS.md` OPEN-233行、`docs/pm/REPORT_LEDGER.md` OPEN-233行、のみ)。
- 明示add対象(1ファイルずつ): `DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_50.md`、`docs/pm/delegation_log/2026-10-02_OPEN-233-SELF-RECOVERY-TRIAL-01_50.md_check.json`。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- commit前に`git status --porcelain`でステージ内容が上記だけであることを確認する。
- コミットメッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: USER_DECISION_REQUIREDとしてSTOP(該当文の重大度の扱い・降格ルール対象文・予算の3点)。実装・Trialなし(委任_50)`
- trailerは直近commitの慣例に従う。`git push origin main`まで行う。競合・エラーが出たら自動解決せず報告する。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)更新したファイルと更新内容の要約、(2)追記文の数値と`results_01.json`の照合結果(一致/不一致)、(3)T-0の結果、(4)commit hash・push結果、(5)変更ファイルのraw.githubusercontent.com URL、(6)指示どおりにできなかった点。
