# DELEGATION_READ_EFFICIENCY_BLOCK(Fable→Sonnet/Opus委任文への固定貼付ブロック)

管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-TRIAL-DESIGN-01(施策2)。
Fableは以下をSonnet/Opusへの**全委任文**にそのまま貼る(明記率100%が目的、
既存ルールPM_GOVERNANCE 11節[E-1/D-1/G-1]の遵守手段であり新ルールではない)。

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: transcript退避は完了後Fable側で実施する。Sonnet/Opusは対応不要。
(施策1 Trial対象タスクのみ追加)T-1: 本委任文に列挙した「事前指定
Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由を
RESULT_PACKETに1行で記録すること。
---

## 使用上の注意
- ラベル(E-1/D-1/G-1/F-1/T-1)は明記率計測(`remeasure_reminder_tag_01.py`
  相当のGrep検出)のため、文言を変えずそのまま貼ること。
- 品質・Gate要件(受入条件照合、Dangling Reference確認、明示`git add`、
  回帰全件1回の実行等)を省略する指示ではない。本ブロックは読込・出力の
  最小化のみを対象とする。
- 施策1 Trial対象外の通常委任ではT-1行を省略してよい(E-1/D-1/G-1/F-1の
  4行は常時貼付)。
