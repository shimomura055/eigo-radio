# OPEN_ITEMS — 未確定事項・技術的負債

**管理ID: ER-PM-001**
**最終更新: 2026-08-09**

検討中・候補・未確定仕様・技術的負債を記録する。確定済み仕様は書かない
(→[CURRENT_SPEC.md](CURRENT_SPEC.md))。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-01 | CEFR-A2の正式仕様(語彙・文長・語数等、全20項目)が一切存在しない | `TBD` | 仕様未決 | Blocking(A2制作開始前に必須) | ユーザーがA2仕様を新規決定する。既存B1/B2の値をそのままコピーしない |
| OPEN-02 | A2の生成元(Natural English Sourceから独立生成 vs B1/B2からの派生簡略化)が、ユーザー依頼文言と公式decision recordで矛盾 | `UNDER_REVIEW` | 仕様矛盾 | Blocking(A2制作開始前に必須) | ユーザーが方針を決定。[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md) 4節参照 |
| OPEN-03 | CEFR-B2の音声化(Preview/Key Phrase/Full Story/Podcast組み立て)が一度も実施されていない | `TBD` | 未着手 | Non-blocking(B1公開には影響しない) | 着手するかどうか・いつ着手するかをユーザーが判断 |
| OPEN-04 | `used_form`/`key_phrase`の100%重複 | `DECIDED`(整理しない方針は確定済み) | 技術的負債 | Non-blocking | 実際に分ける必要が生じるまで対応しない(意図的放置) |
| OPEN-05 | 短文TTS hallucinationの根本原因(モデル側の挙動)が未解明 | `UNDER_REVIEW` | 技術的負債 | Non-blocking(strict検証+fallbackで運用上は吸収済み) | 発生時にstrict検証+fallbackで対応を継続。原因調査は優先度低 |
| OPEN-06 | ASR homophone ambiguityを機械的に判別する手段が未実装(同音異義語リスト等) | `TBD` | 技術的負債 | Non-blocking(human reviewフローで運用上は吸収済み) | 次に同種の事象が実際に発生してから検討(先回り実装はしない) |
| OPEN-07 | 正式なLUFS masteringが未導入(現状はscalar RMS基準の簡易調整のみ) | `TBD` | 技術的負債 | Non-blocking | 音質改善の必要が生じた際に検討 |
| OPEN-08 | ADD03初回Full Story生成(1回目3試行不合格分)の詳細ログが失われている(`stage_a_generate_body_audio`のバグ、2回目実行分からは修正済み) | `HISTORICAL`(バグ自体は修正済み) | 記録欠落 | Non-blocking | 再発防止は完了。過去分の復元は行わない |
| OPEN-09 | Dynamics3不使用の決定について、比較検討の詳細記録(なぜscalar RMSを選んだかの根拠レポート)が見当たらない | `TBD` | 記録欠落 | Non-blocking | 発見時に追記。現時点では推測で埋めない |
| OPEN-10 | A01(CEFR-B1)の「エピソード全体の最終承認」が未取得(`publication_status: NOT_APPROVED`のまま) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking(A02・ADD03の作業には影響しない) | ユーザーがA01最終版(r2)を通しで試聴し、公開可否を判断 |
| OPEN-11 | A02・ADD03も`user_quality_status: PASS`だが`publication_status`は`NOT_APPROVED`のまま(品質OKと公開承認は別判断) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking | ユーザーが公開判断を行うタイミングで確定 |
| OPEN-12 | `ER-003-B1_HANDOFF.md`が旧運用のまま(仕様・経緯を大量に含む29KB超のファイル)で、新ルール(直近作業再開専用)に未準拠 | `TBD` | 運用移行未完了 | Non-blocking | 次回以降の更新時に新フォーマットへ段階的に移行(今回は大規模書き換えを行わない) |

## 参照元

[CURRENT_SPEC.md](CURRENT_SPEC.md)、[DECISION_LOG.md](DECISION_LOG.md)、
[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)
