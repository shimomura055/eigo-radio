## 管理ID

OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01(委任_02b: SSOT反映・Opus台帳・ACTIVE_TASK更新・commit/push。¥0。委任_02aでOpusレビュー保存とdoc §10は完了済み)。並行タスクなし。本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

**作業方式(必須)**: 追記はすべて`Edit`ツールで行い、Bashのheredoc/echoでファイルを書かない。1回のEditは1箇所・目安30行以内に小分けし、長文を1回で出力しない。説明・思考は最小限。文案は`docs/pm/RESULT_PACKET_FLOOR.md`の15節と`docs/pm/opus_l2_review_open233_floor_selectivity_01.md`・設計doc §10から転記・短縮して使う(新規の長文分析を書かない)。T-0の委任文保存は本委任文を逐語で(Writeツールで2〜3分割して)保存する。

## 性質/到達上限Status/禁止事項

- 性質: 記録・SSOT反映のみ。本管理IDの最終Status(Fable確定): **USER_DECISION_REQUIRED**。
- 禁止: コード変更/Prompt変更/Production変更/有料API/gold変更/設計案採否の「決定」記述/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET.md`・`RESULT_PACKET_FLOOR.md`のadd/`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`の編集。
- 費用: ¥0。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 条件A該当・レビュー実施済み(本委任はその記録)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2(2026-09-25): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし。
T-2追記: TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文)

> 現在Status / 到達可能Status: 今回到達してよいのは USER_DECISION_REQUIRED または DESIGN_READY_FOR_REVIEW まで。Production変更は禁止。STOP条件: 正当6件を守りながら半分以下へ減らす見込みが立たない／新しいSafety原則の追加が必要／gold定義変更が必要／有料Trialが必要／Production仕様変更が必要。勝手に実装・Trialへ進まないこと。

## KPI provenance欄

該当なし(記録のみ。数値はRESULT_PACKET_FLOOR・設計docから転記)。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`へ新規6行(最大番号+1〜+6、既存書式、1行ずつEdit): (1)根本原因はStage 1 `changed_*`フラグ生成側(absence/contra混同、HOOK_CLAUSE相当なし)=RAISED/(2)案1/5は正規表現当て込み・hold-outでgold見逃し=FABLE_DECIDED(不採用方向、ユーザー判断待ち)/(3)案4はS1再サンプルで正当2件を失いうる=FABLE_DECIDED(非推奨)/(4)推奨代替=RECLASSIFY-02区分のfloor発火条件流用/cite-to-fire(`apply_floor_cited`反実仮想記録再利用)/Stage 1 prompt補正=RAISED(ユーザー判断待ち)/(5)順序=RECLASSIFY-02評価→¥0段階0(0a〜0d)→設計確定→承認→段階1=RAISED/(6)集計scriptの(iii)分岐欠落・No.21/23不一致=RAISED(doc §10で訂正済み)。各行の出典=`docs/pm/opus_l2_review_open233_floor_selectivity_01.md`。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FLOOR.md`: Grep `^## 15|SSOT追記文案|^## 16` →15・16節のみ。
2. `docs/pm/opus_l2_review_open233_floor_selectivity_01.md`: 全文(68行)。
3. `docs/pm/design_open233_floor_selectivity_01.md`: Grep `^## §10` →§10のみ。
4. `docs/pm/ACTIVE_TASK.md`: 全文。
5. `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `^\| OF-` →最終3行。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01` →その行の直後に本管理IDの新規行(1行、POST_USER_VALIDATION区分、Status=USER_DECISION_REQUIRED)を追加。内容: 「機械Safety(floor)誤爆35件の¥0分析+設計案0〜5比較(2026-10-06、委任_01〜02b)。35件内訳: 比較14/時期8/主体6/否定5/数字4/因果1/他1(正当6=数字3主体2時期1、不要24、判断不能5、RCA推測ラベル)。不要24の原因: Stage 1フラグ不整合17/重大性判定欠如6/Tier0語彙1((iii)は集計script構造上0)。案別in-sample強制重大: 案1 14/案2 8/案3 0/案4 4/案5 14(現行35)。hold-out(rep30)で案1はneg3 gold(時期)を見逃し。Opus条件Aレビュー: 根本原因=Stage 1 `changed_*`フラグ生成側(absence/contra混同)、案1/5は過適合、案4非推奨、推奨代替=①RECLASSIFY-02区分のfloor発火条件流用②cite-to-fire(`apply_floor_cited`反実仮想記録再利用)③Stage 1 prompt補正、順序=RECLASSIFY-02評価→¥0段階0→設計確定→承認→段階1。いずれも承認済み線引きOPEN-233-A1-PROD(時期のみverify・他は決定論維持、APPROVED_FOR_PRODUCTION・未配線)の変更=ユーザー承認要→STOP条件『Production仕様変更が必要』該当。ユーザー判断U1設計方向/U2線引き変更可否/U3 ¥0段階0実施可否/U4正当6・判断不能5のラベル確認。Dangling Referenceなし。¥0、Production未変更。設計doc `docs/pm/design_open233_floor_selectivity_01.md`、Opus `docs/pm/opus_l2_review_open233_floor_selectivity_01.md`、REPORT §79。」
- `docs/pm/REPORT_LEDGER.md`: 末尾最新行の直後に1行追加(2026-10-06 | OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01 委任_01〜02b | 要約、REPORT §79)。
- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `§78-2` →§78-2の末尾に「## §79 OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01: 機械Safety(floor)誤爆35件の分析と設計案比較(委任_01〜02b、¥0)」を4回のEditに分けて追加: (a)前提・provenance・35件内訳表、(b)誤爆主因と案別比較表、(c)Opusレビュー要旨、(d)Fable判断全文とU1〜U4。
- `DECISION_LOG.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-02` →最新エントリの直後に本管理IDの新エントリを3回のEditで追加: (a)見出し+ユーザー指示要点、(b)分析結果+Opusレビュー要旨、(c)Fable判断全文+U1〜U4(U1 設計方向: Opus代替①/②/③/Sonnet案2+5/floor撤廃別設計、U2 線引きA1-PROD変更可否、U3 ¥0段階0(0a〜0d)実施可否、U4 正当6件・判断不能5件のラベル確認)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(1回のWrite、25行以内)。
- `docs/pm/RESULT_PACKET.md`: 冒頭に委任_02bの結果を追記(1回のEdit)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file ...02b.md --json-out ...02b.md_check.json`
2. 上記Edit(小分け)。
3. `git status --porcelain`→明示add→commit→push。

## Git

明示add対象のみ: 設計doc、opus_l2_review、`er052_output/open233_floor_selectivity_offline_01/floor_fire_analysis_01.py`(+`.json`/`.md`)、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、REPORT、delegation_log `_01b`/`_01c`/`_02a`/`_02b`(+`_check.json`)。`ACTIVE_TASK.md`・`RESULT_PACKET.md`・`RESULT_PACKET_FLOOR.md`はaddしない。コミットメッセージは「OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01: floor誤爆35件分析...REPORT §79(委任_01〜02b、¥0)」。push前に`git status --porcelain`で混入確認。

## 報告(RESULT_PACKET項目)

1. T-0結果。2. 追記したファイルと箇所。3. commit hash・push結果・raw URL。4. 一覧外Read理由。最終報告は10行以内。
