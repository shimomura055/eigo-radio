# DELEGATION_READ_EFFICIENCY_BLOCK(Fable→Sonnet/Opus委任文への固定貼付ブロック)

管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-TRIAL-DESIGN-01(施策2)。
Fableは以下をSonnet/Opusへの**全委任文**にそのまま貼る(明記率100%が目的、
既存ルールPM_GOVERNANCE 11節[E-1/D-1/G-1]の遵守手段であり新ルールではない)。

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
(施策1 Trial対象タスクのみ追加)T-1: 本委任文に列挙した「事前指定
Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由を
RESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-
WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久
運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を
`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/
check_delegation_prompt.py --file <path> --json-out <path>_check.json`
を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する
(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、
既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルール
ではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り
`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外
条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`
等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは
別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md
7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]
再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの
有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認
上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし
報告、の4点を必須とする。
---

## 使用上の注意
- ラベル(E-1/D-1/G-1/F-1/T-1/T-2)は明記率計測(`remeasure_reminder_tag_01.py`
  相当のGrep検出)のため、文言を変えずそのまま貼ること。
- 品質・Gate要件(受入条件照合、Dangling Reference確認、明示`git add`、
  回帰全件1回の実行等)を省略する指示ではない。本ブロックは読込・出力の
  最小化のみを対象とする。
- 施策1 Trial対象外の通常委任ではT-1行を省略してよい(E-1/D-1/G-1/F-1/T-0/T-2の
  6行は常時貼付、T-1のみTrial対象タスク限定)。
