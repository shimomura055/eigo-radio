# content label sheet(L3評価のみ・Sonnet判断・人手確認前): B3_twostage_gate
凡例: l1/l2と同じ。

| theme | fact_id | note(逐語) | 字数 | 既知誤読との一致 | 型 | 台帳外混入 | 警告 | 根拠 |
|---|---|---|---|---|---|---|---|---|
| meta | MUSE-HC-003 | 注意(逆転): MetaがMuseの製品設計として、専用クラウドコンピューターへの保存とSentinelによる許可管理を説明。Museの実運用で専用クラウドPCへの保存とSentinelの管理が行われた、ではない。 | 107 | -(対象外) | 変質止まり | 無 | - | 設計説明段階↔実運用稼働の段階反転だが主題結論を変えるほどではない(L2 B2と同判断) |
| space_weapons | F-001 | 注意(逆転): 米国が軌道上兵器を敵対的な相手の行動から統合軍を防護する用途で配備している。敵対者を攻撃する軌道上兵器を配備しているのではない。 | 72 | 不一致 | 真の逆転型(妥当) | 無 | - | 防護用途↔攻撃用途の取違えで妥当だが既知誤読(初めて認めた発言→初めて配備)とは別(B2nと同判断) |

## stage1.5判定(対象factのみ。cid別likelihood)と対象の見落とし(FN)

- meta MUSE-HC-012: stage1通過(run1,run2)=[True, True] / stage1.5=A=low,B=low / FN: stage1_5_low
- meta MUSE-HC-014: stage1通過(run1,run2)=[False, True] / stage1.5=A=low / FN: stage1_5_low
- hormuz HF-009: stage1通過(run1,run2)=[True, True] / stage1.5=A=low,B=low / FN: stage1_5_low
- hormuz HF-007: stage1通過(run1,run2)=[True, True] / stage1.5=A=medium,B=medium / FN: stage1_5_medium
- space_weapons F-009: stage1通過(run1,run2)=[True, True] / stage1.5=A=low,B=low / FN: stage1_5_low
- space_weapons F-001: stage1通過(run1,run2)=[False, True] / stage1.5=A=high / 付与
- space_weapons F-002: stage1通過(run1,run2)=[True, True] / stage1.5=A=medium,B=low / FN: stage1_5_medium
- space_weapons F-007: stage1通過(run1,run2)=[True, True] / stage1.5=A=low,B=low / FN: stage1_5_low
- sewer F-011: stage1通過(run1,run2)=[True, True] / stage1.5=A=medium,B=medium / FN: stage1_5_medium
- sewer F-010: stage1通過(run1,run2)=[False, True] / stage1.5=A=medium / FN: stage1_5_medium
- sewer F-016: stage1通過(run1,run2)=[True, False] / stage1.5=A=medium / FN: stage1_5_medium
- ai_control EVID-006: stage1通過(run1,run2)=[True, True] / stage1.5=A=medium,B=low / FN: stage1_5_medium
- ai_control EVID-004: stage1通過(run1,run2)=[False, False] / stage1.5=- / FN: stage1_not_reversible_in_any_run
- ai_control CONTROL-001: stage1通過(run1,run2)=[False, False] / stage1.5=- / FN: stage1_not_reversible_in_any_run
- (holdout参考) A02 POL-01: stage1通過=[False, True] / stage1.5=A=low / stage1_5_low
- (holdout参考) A02 POL-06: stage1通過=[True, True] / stage1.5=A=medium,B=low / stage1_5_medium