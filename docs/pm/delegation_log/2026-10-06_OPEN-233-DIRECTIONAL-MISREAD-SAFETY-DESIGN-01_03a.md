## 管理ID

OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01(委任_03a: Opus Part 2レビューの必須修正3点+F4指摘を設計docへ反映し、Opus Part 1/Part 2レビューを逐語保存する)。並列委任_03bがSSOT(OPEN_ITEMS/DECISION_LOG/REPORT/OPUS_FINDINGS_LEDGER/ACTIVE_TASK)を編集中のため、**それらのファイルと`docs/pm/RESULT_PACKET.md`には触れない**。**git操作・コード変更なし。** 書込先: `docs/pm/design_open233_directional_misread_safety_01.md`、`docs/pm/opus_l2_review_open233_directional_misread_safety_01.md`(新規)、`docs/pm/RESULT_PACKET_03A.md`、`docs/pm/delegation_log/`。

**作業方式(必須)**: Edit/Writeは1回30〜40行以内に分割、Bash heredoc不使用、説明最小。T-0の委任文はWriteで新規作成後、残りをEditで追記して逐語保存(Writeは上書きのため分割時はEdit追記)。時間目安20分。

## 性質/到達上限Status/禁止事項

- 性質: 設計doc修正(¥0)。到達上限: DESIGN_READY_FOR_REVIEW(Opus条件Aレビュー済み)。最終StatusはFableがUSER_DECISION_REQUIRED判定済み(設計判断・有料Trialがユーザー承認事項)。
- 禁止: 残11 run/Production変更/全機械floor復活/一律厳格化/gold・KPI変更/Human Review振替/有料API/コード変更/数字floor穴修正/新原則の「決定」記載。
- Opus Gate: 条件A必須レビュー実施済み(Part 1+Part 2)。本委任は反映のみ。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一ファイル再読禁止。D-1: Grep→範囲Read。G-1: git出力不使用。F-1: 退避不要。T-1: 事前指定一覧に従う(一覧外は理由記録)。T-0(2026-09-13常時有効): 委任文を`docs/pm/delegation_log/2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_03a.md`へ逐語保存し`check_delegation_prompt.py`実行、結果1行をRESULT_PACKET_03Aへ(FAILでも継続)。T-2/T-2追記(7-5): TTSなし。T-3: ¥0のため対象外。

## ユーザー指示(原文、要点)

> Opusレビュー必須(設計後・実装前): 同一モデルの相関誤りを本当に減らせるか/方向反転以外の同型systematic misread/過剰Safetyへ逆戻りしないか/既存Checker信号を捨てている他の箇所。到達Statusは DESIGN_READY_FOR_REVIEW / USER_DECISION_REQUIRED まで。

## Opus Part 2レビュー(逐語、保存対象)

(逐語本文は`docs/pm/opus_l2_review_open233_directional_misread_safety_01.md`のPart 2節に保存。委任文内の同一テキストと同一。)

## 作業内容

1. `docs/pm/opus_l2_review_open233_directional_misread_safety_01.md`(新規): ヘッダ+Part 1要約+Part 2逐語。
2. 設計doc修正(既存文は削除せず「Opus Part 2反映」として追記・訂正): §4 L177/§7改訂のT-E母集団訂正、§8改訂の抽出失敗扱い訂正と案E'整理(旧案D撤回候補)、§3旧「代替E」を「代替V」へ改名(§8旧記述も)、§1表S1 L4055をL4160-4203へ訂正、§12判断事項をOpus 1〜7へ差替え(到達Status=DESIGN_READY_FOR_REVIEW、最終=USER_DECISION_REQUIRED)、§13に(新1)(新2)(新3)とRewrite hint追記、§9にF3追加対象(1)〜(6)・STOP条件・費用約¥15以内【推測】追記、§14新設。
3. `docs/pm/RESULT_PACKET_03A.md`: 変更箇所一覧、T-0結果、Dangling確認(Grep `代替E|案E`)、一覧外Read理由。

## 事前指定Read/Grep一覧

1. 設計doc: Grep `^## |^### |代替E|案E|L4055|123|抽出失敗|BLOCKING→Rewrite` →該当範囲Read。
2. 他ファイルのReadは不要。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_03a.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01_03a.md_check.json`
2. 改名漏れ確認: Grep `代替E` 設計doc(0件であること)。

## SSOT追記文

なし(委任_03bが担当)。

## Git

git操作なし。

## 報告

`docs/pm/RESULT_PACKET_03A.md`。最終報告は8行以内。
