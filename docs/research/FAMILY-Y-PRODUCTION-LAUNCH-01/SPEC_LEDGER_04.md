# SPEC_LEDGER_04: Family Y 仕様差分台帳(ユーザー追加承認USER_03 ①②反映版)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_05 / 2026-10-25(JST)。SPEC_LEDGER_03(66行)を、ユーザー追加承認(原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_03.md`。以降「USER_03 §x」)で更新した版(**66行**、行数は不変)。機械可読版=`spec_ledger_04.json`(全行)。
他の行はSPEC_LEDGER_03から**変更なし**(本書は変更行だけを書く。全行の表は`SPEC_LEDGER_03.md`+本書の差分で読む)。位置づけ・Status語彙・スコープ基準・廃止条件(Y PRODUCTION_WIRED時にCURRENT_SPECの配線Status表へ一本化)はSPEC_LEDGER_02/03 §0〜§1のとおり。

## 1. 件数サマリ

| 区分 | 件数 |
|---|---|
| 台帳行 合計 | **66** |
| Y_OWN | 12 |
| APPLY | 38 |
| EXCLUDE | 7 |
| APPLY_AFTER_DEP | 4 |
| NO_PREADOPT | 4 |
| PENDING | 1 |

(03→04の変化: EXCLUDE_OPEN 1→0、APPLY 37→38。YL-E02がEXCLUDE_OPEN→APPLY。)

## 2. 03からの変更(差分)

| ID | 変更前 → 変更後 | 根拠 |
|---|---|---|
| YL-C05 | 案Bの固定Closing: Gate=既存再判定(判定<=3・書換えなし・残存FAILは`FIXED_CLOSING_RESIDUAL_FAIL`でSTOP) → **加えて、3回すべてFAILかつFAIL項目の和集合が`leak_evidence_memorable`のみ・本文byte一致・書換えなしの場合に限り、個別Human承認で`PASS_BY_HUMAN_APPROVAL`**(Gate判定は改変せず保持、別ファイルの承認記録)。他項目FAIL・他slug・本文変更・再生成/局所書換え後は従来どおりSTOP。APPROVED_FOR_PRODUCTION(当該記事のみ)。実装済み・offline test PASS・Production runtime evidence未取得 | `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_03.md` §1(「選択肢Ⅱを正式承認する。」「承認済み案Bの本文と完全一致する場合のみ適用する。」「対象Gate項目は `leak_evidence_memorable` のみ。」「他のGate項目のFAILは救済しない。」「既存のHuman個別承認機構を可能な限り再利用し、新たな汎用例外機構を不要に増やさない。」) |
| YL-E02 | Prompt/Gate整合: EXCLUDE_OPEN(変更しない) → **APPLY(`leak_discovery_syntax`の判定定義へ補足一文のみ追加。Family YのClosing判定のみ・Prompt 02不変)**。`leak_tension_reverts_to_research`の合格条件変更は含まれない(据え置き・OPEN継続)。実装済み・較正済み(GATE_CALIBRATION_02) | `docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_03.md` §2(「選択肢(a)を正式承認する。」「Prompt 02の本文・意味・hashは変更しない。」「対象はFamily YのClosing判定。」「必要最小限の判定定義変更にとどめる。」「他FamilyのGateを無断変更しない。」) |

## 3. 実装との整合メモ

- 補足文言は上記承認原文の一文そのまま。委任文にあった後半「ただし…引き続きFAIL」は、較正で案Bのdiscovery FAIL 3/3を招くため実装していない(GATE_CALIBRATION_02 §0-2。**Fableへ判断候補として開示**)。
- YL-B08(Chunk TTS)のうちOT-44(a)(共通er020のY chunk ID解決)は本委任で実装済み。runnerの`chunk_tts`表記更新(OT-44(b))は委任_03所有。
