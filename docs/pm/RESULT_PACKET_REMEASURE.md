# RESULT_PACKET_REMEASURE(PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01)

- 性質: read-only再測定、費用¥0(API呼び出しなし)。Git操作なし(commit/push未実施)。
- 詳細: `PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01_REPORT.md`(root新規)。
- 母集団: sonnet-worker Before357件/After33件、**100%(357/357・33/33)でtranscript取得**(復元手法により従来7.1%から大幅改善)。境界=commit`710241006b`(2026-09-12 20:37:12 +09:00)。
- 重要発見: After委任文へのE-1/D-1/G-1明記は**55%(18/33)のみ**、45%は無記載(運用ルールが未徹底)。
- E-1(同一ファイル再読率): Before中央値33.9%→After40.8%。**改善シグナルなし**。
- D-1(全文Read率): Before59.9%→After47.9%(相対▲20%)、Read1回あたり文字数▲37%。**弱い改善シグナルあり**(明記あり群でより顕著、ただしn小)。
- G-1(git出力比率): Before4.4%→After8.9%。**改善なし**(元々主因ではない)。
- 累積usage(全ターン合算、種別非統一): Before中央値430万→After532万(+24%、悪化)。**ただしtool_uses自体が中央値50→68(+36%)へ増加**しており(相関+0.93)、消費増加はタスク複雑化が主因の可能性が高い。E-1/D-1/G-1導入の失敗と断定できない。
- 交絡: 観測期間非対称(Before7日 vs After18時間)、種別構成比の違い((a)25.8%→39.4%等)、モデルは同一(交絡なし)。**現状Nでは効果の有無を確定できる検出力はない**。
- Trial前提数値: tool_uses vs usage相関+0.93(20%削減で線形近似上usage約30%減の可能性、外挿注意)。全文Read率 vs usage相関−0.047(ほぼ無相関、Read削減が消費削減に直結する保証はない)。全文Read率57%→25%ならRead文字量▲42.9%(tool_result全体の約▲22.6%相当)。
- 判定語(VALIDATED等)は付けていない。材料提示のみ、Trial設計・実装はしていない。
- 次アクション: 上記数値を踏まえ、施策1(tool_uses削減)・施策2(D-1徹底、まず委任文明記率を100%に是正)のTrial設計をFable/ユーザーが判断。
