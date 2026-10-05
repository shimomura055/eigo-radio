# DELEGATION_STANDARD_TEMPLATE(委任文標準テンプレート)

管理ID: PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01(D-2、
2026-09-13ユーザー正式採用[施策1]、`docs/pm/PM_GOVERNANCE.md` 11節D-2参照)。

Fableは全委任文(Sonnet/Opusへの委任)を本テンプレートの見出し構成に従って
作成する。各見出し文字列は固定(`docs/pm/tools/check_delegation_prompt.py`
が本文字列でセクション検出を行うため、文言を変更しない)。

---

## 管理ID

(例: `PM-XXXX-01`。並行タスクとの衝突がないか確認した結果も1行で記す。)

## 性質/到達上限Status/禁止事項

(Trial/Production/検証等の性質、到達しうる最終Status[VALIDATED/
APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED/USER_DECISION_REQUIRED等]、
禁止事項[対象外ファイル不可・費用上限[Cap]・破壊的操作禁止等]を明記する。
費用上限[Cap]の記載はT-3の定型文(Guardrail文言)に従う。「上限¥X、
超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが
無いもの)は使用しない。**Opus独立技術レビューGate(`docs/pm/PM_GOVERNANCE.md`
11-3節、2026-10-02)の該当判定[条件A/B/C/D/非該当]を1行で記す。**)

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

`docs/pm/templates/DELEGATION_READ_EFFICIENCY_BLOCK.md`の本文をそのまま
貼る(E-1/D-1/G-1/F-1/T-0/T-2は常時、T-1は施策1 Trial対象タスクのみ、
T-3は費用上限[Cap]を伴う委任のみ)。T-0は委任文標準の検証手順(受領した
委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し
`check_delegation_prompt.py`で検証)であり、本文言は
`DELEGATION_READ_EFFICIENCY_BLOCK.md`側が正本。T-2(2026-09-25、
`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`)はTTS Standard同期
明示の再確認であり、本文言も`DELEGATION_READ_EFFICIENCY_BLOCK.md`側が
正本。T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`)は費用上限
[Cap]=暴走防止Guardrail(自動STOP閾値ではない)の明示であり、本文言も
`DELEGATION_READ_EFFICIENCY_BLOCK.md`側が正本。

## ユーザー指示(原文)

(該当する場合、ユーザーの承認・指示原文をそのまま引用する。)

## KPI provenance欄(KPI・Gate判定を扱う委任のみ必須、PM_GOVERNANCE 24節)

(KPI・合否数値ごとの測定経路を6区分[fresh/frozen/reuse/manual_substitution/
synthetic/production_formal_path]から明記し、混在時は件数内訳を書く。E2E自己確認
[「fresh Production初回pathを含むE2E値か」Yes/No]の欄も置く。該当しない委任は「該当なし」。)

## Opus台帳更新(Opus指摘が関係する委任のみ必須、PM_GOVERNANCE 11-5)

(`docs/pm/OPUS_FINDINGS_LEDGER.md`の関連指摘IDと、本委任での状態遷移
[RAISED→FABLE_DECIDED→IMPLEMENTED/TRIALED→EVIDENCED→CLOSEOUT_CONFIRMED]を書く。
該当しない委任は「該当なし」。)

## 事前指定Read一覧

(「ファイル:行範囲」または「Grepで位置特定→該当範囲Read」の形式で列挙する。
プレースホルダ[TBD/同上/前回と同じ等]禁止。)

## 事前指定Grep一覧+追記位置・更新位置の手順

(Grepパターンと対象パス、検出後の追記位置・更新手順を明記する。)

## 実行コマンド全文

(コマンドは引数の実値[絶対パス・具体的なフラグ値]を含めて全文で書く。
「同上」「前回と同じ」「<引数>」等のプレースホルダは禁止。実行コマンドは
`.venv\Scripts\python.exe`(またはvenv有効化後のpython)を使用する。PATH上の
素の`python`はMicrosoft Store版等の別環境を拾い回帰が誤検知する
(CONSOLIDATION-118で実証)。`run_project_regression.py --pattern`のglobは
必ず`_test`を含める(例`er003*_test_*.py`)。テスト以外のスクリプトが
import実行される事故防止(CONSOLIDATION-124)。)

## SSOT追記文

(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC等への追記文案をそのまま使用できる
形で記す。)

## Git(明示add対象・コミットメッセージ・trailer)

(明示`git add`対象ファイルの一覧、コミットメッセージ文案、末尾trailerを記す。
`-A`/`stash`/`amend`は既定で禁止。)
(SSOT編集権の有無: 本Agentが`CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/PM_GOVERNANCE.md`の
編集権を持つか明記する。持たない場合、SSOT追記文案はRESULT_PACKETへ
記載するのみとし、SSOTファイル自体は編集・addしない。8-Y節[SSOT編集の
直列化ルール]参照。)

## 報告(RESULT_PACKET項目)

(RESULT_PACKETへ記載すべき項目を列挙する。)

---

## Fable自己チェック(送信前)

- [ ] Read一覧に行範囲/Grepパターンあり
- [ ] 追記位置手順あり
- [ ] コマンドに引数実値あり
- [ ] 禁止事項・費用上限あり
- [ ] 並行タスク衝突回避あり
- [ ] Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定[A/B/C/D/非該当]あり
