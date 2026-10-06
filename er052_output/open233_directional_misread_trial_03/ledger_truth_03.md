# TRIAL-03 ledger_truth_03(事前登録・凍結)

ledger_truth_02を複製し各eventにphaseを追加。gold定義・result_state・quoteは不変。

| fact | event | result_state | phase |
|---|---|---|---|
| HF-009 | 上げ幅 | DECREASED | INTERIM |
| HF-009 | 水準 | INCREASED | FINAL |
| MUSE-HC-012 | 電話テスト | STARTED | SINGLE(Ledger本文は開始の事実を述べるのみで時間段階を持たない) |
| MUSE-HC-012 | 機能 | PAUSED | FINAL(ロールバック=結末) |
| 他全fact | 全event | 従来どおり | SINGLE |

全quoteがLedger本文へ部分一致することをスクリプトでassert済み。

## 採点規則(追加分)
- phase一致率=抽出phaseとLedger event phaseの一致数/event数。Ledger側SINGLEは任意phaseと一致扱い。
- 既存の採点規則・gold定義は不変。phase一致率は診断指標で、合格基準8項目には含めない。
