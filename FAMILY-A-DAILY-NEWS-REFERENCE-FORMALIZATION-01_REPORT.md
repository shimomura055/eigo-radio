# FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01 報告書

管理ID: FAMILY-A-DAILY-NEWS-REFERENCE-FORMALIZATION-01(Lane A-1)。
Lane A-2(News固有層設計Trial、読み取り専用)・Lane B(B-Family A2横断
監査、`er012_*`)とは相互独立、他Laneの成果物は参照していない。本タスクが
唯一のSSOT編集・Git担当。

## 1. 対象・根拠

ユーザー決定(2026-09-08、A-UDR-5)「Hanshin系現役Production資産を通常
News(Major/Daily News)の正式referenceとしてCURRENT_SPECへ反映する」を、
`FAMILY-A-DAILY-NEWS-SPEC-DRAFT-01_REPORT.md`(§2/§3/§5)の内容に基づき
実装した。条件: 既にDECIDED/PRODUCTION_WIRED済みの内容だけを正式化/
B1-A等obsolete仕様は混ぜない/ADD03(イラン)・A02(英SNS)は題材・構造
referenceに限定/Trend Synthesis専用仕様は混ぜない/Gate 4 Dangling
Reference Check/DECISION_LOG・OPEN_ITEMS・Git反映。

## 2. CURRENT_SPEC.mdへの反映

新設「## 通常News(Major/Daily News)Reference仕様」節(「## News
Editorial Mode(Trend Synthesis)」節の直後、400行目付近)を追加。既存
DECIDED仕様の本文は重複転記せず、各既存節(CEFR-A2構造・音声仕様/B1/
Cross-level仕様/Key Phrase/Audio Assembly)への参照+「通常Newsに適用
される」ことの明記のみとした。表10行、各行にStatus(DECIDED/
VALIDATED/PRODUCTION_WIRED)と根拠管理IDを付与。News固有層(Layer3
Focus Module・Mode判定基準)は内容を書かず「未設計・設計Trial起票済み
(`FAMILY-A-DAILY-NEWS-FOCUS-LAYER-DESIGN-TRIAL-01`、Lane A-2)」とのみ
明記した。

続けて以下3小節を追加。
- **Reference記事の正式指定**: Hanshin(`ER-003-A2-B1-N3-01`)を構造・
  Writer・Fact Safety・音声のreference実装として正式指定、Health/
  Householdを同系列として併記。ADD03/A02は題材・音声構造referenceに
  限定(本文生成コードパス・完成音声は非再利用)。
- **通常News仕様に含めない(obsolete除外)**: B1-A方式・P-series専用
  script・Natural English Source方式・旧Preview分量・旧trim margin・
  ER-010設計文書の6件を、既存置換記録への参照付きで明記。
- **Trend Synthesisとの境界**: Focus Module/Counter-signal/Trend Gate/
  Evidence Strength/Trend Memory/Engagement/Reference Digestは本節へ
  含めないことを明記。

冒頭changelogへ「第15弾」エントリを追加。

## 3. Gate 4 Dangling Reference Check

追記テキストが参照した管理ID(ER-003-A2-STRUCT-02〜04、
ER-003-A2-SPEC-FREEZE-01、ER-003-A2-B1-N3-01、ER-003-B1-B2-SCOPE-FIX-01、
ER-003-SPOKEN-FIRST-03、ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02、
ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12、
ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01、
ER-003-CROSSLEVEL-AUDIO-02、ER-003-B1-NOVEL-AUDIO-01系、
ER-003-POINT-NOTIFICATION-01、
ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23)を、
`CURRENT_SPEC.md`・`DECISION_LOG.md`内でgrep確認した。全件既出
(結果は本文末尾の表を参照)。DECISION_LOG.md 5711行の
「既にHISTORICAL化済みの完成テーマ向けスクリプト」記述も現存を確認した。
Trial-only・未承認仕様(Trend Focus Module、Discovery Layer3、Reference
Digest等)は本節の規定内容として参照していない(名指しは「含めない」
文脈のみ)。

| 管理ID | CURRENT_SPEC.md出現 | DECISION_LOG.md出現 |
|---|---|---|
| ER-003-A2-STRUCT-02 | 3 | 7 |
| ER-003-A2-SPEC-FREEZE-01 | 10 | 3 |
| ER-003-A2-B1-N3-01 | 16 | 12 |
| ER-003-B1-B2-SCOPE-FIX-01 | 5 | 5 |
| ER-003-SPOKEN-FIRST-03 | 1 | 3 |
| ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02 | 2 | 2 |
| ER-010-NO9-FACTCHECK-POLICY-AND-POINT-COMPRESSION-DIAGNOSTIC-12 | 3 | 5 |
| ER-011-PREVIEW-ROLE-AND-NUMERIC-PRECISION-PRINCIPLE-PRODUCTION-WIRING-01 | 4 | 1 |
| ER-003-CROSSLEVEL-AUDIO-02 | 3 | 1 |
| ER-003-B1-NOVEL-AUDIO-01 | 8 | 3 |
| ER-003-POINT-NOTIFICATION-01 | 1 | 2 |
| ER-011-NO18-A2-TIGHT-SPEECH-AND-TRIM030-PRODUCTION-WIRING-23 | 4 | 3 |

**結果: PASS。新規仕様追加が必要な事態は発生せず、STOPなし。**

## 4. OPEN_ITEMS.md / DECISION_LOG.md反映

- `OPEN_ITEMS.md` OPEN-112行へ追記(通常News reference正式化完了・
  reference記事指定・News固有層Trial起票・A-UDR-7観測継続4項目)。
- `DECISION_LOG.md` 冒頭「最終更新」パラグラフ先頭へ本タスク用の新規
  エントリを1件追加(ユーザー決定A-UDR-5/6/7反映内容、Gate 4結果)。

## 5. 触っていないもの

`er012_*`、Lane A-2のReport、`er006_output/`、`er011_output/`、
古い未追跡群。コード・Prompt編集・API呼び出しは実施していない。

## 6. Git

`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`の3ファイルを
ファイル名指定でstage、1 commitで`origin/main`へpush。commit hash・
push結果は`docs/pm/RESULT_PACKET.md`参照。
