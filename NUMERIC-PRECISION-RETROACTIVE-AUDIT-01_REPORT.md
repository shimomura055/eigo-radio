# NUMERIC-PRECISION-RETROACTIVE-AUDIT-01 実行報告

**種別: 読み取り専用の点検。編集・API呼び出し(TTS/LLM/ASR)・Git操作は一切実施していない。**

## 1. 点検母集団(8完成episode、機械抽出+目視確認)

DECISION_LOG.md/OPEN_ITEMS.md/ARTIFACT_REGISTRY.mdを「APPROVED」「完成」「Assembly」等で
照合し、以下を母集団として確定した(`er011_output/open112_trend_theme2_b_final_audio_rerun_04/`
は指示どおり除外)。各episodeの`article.md`・`parts.json`・`*_support_texts.json`・
`key_phrases/keywords_canonicalized.json`全文を対象に`[0-9]+\.[0-9]+`を機械抽出し目視確認した。

| # | 出力ディレクトリ | 生成日時(mtime) | 精密ブロック(2026-09-07 09:22)前後 | 状態 |
|---|---|---|---|---|
| 1 | `er003_output/n3_01/hanshin/{a2,b1b}` | 2026-08-17 | 前(土台配線2026-09-04より前、原則自体が未存在) | 完成(clippingなし)/NOT_REVIEWED |
| 2 | `er003_output/n3_01/health/{a2,b1b}` | 2026-08-17 | 前(同上) | 完成/NOT_REVIEWED |
| 3 | `er003_output/n3_01/household/{a2,b1b}` | 2026-08-17 | 前(同上) | 完成/NOT_REVIEWED |
| 4 | `er011_output/open112_trend_theme2_b_final_audio_rerun_02/a2` | 2026-09-06 20:40 | 前(土台のみ有効) | USER_FINAL_AUDIO_REVIEW_REQUIRED |
| 5 | `er011_output/.../rerun_02/b1b`・`rerun_03/b1b`(article同一) | 2026-09-05生成 | 前 | USER_FINAL_AUDIO_REVIEW_REQUIRED(既知、OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01で報告済み) |
| 6 | `er012_output/editorial_b_voices_trial_09_audio/b1b` | 2026-09-07 20:34 | 後 | ユーザーPASS(構造4項目APPROVED_FOR_PRODUCTION、Production経路自体は未配線) |

## 2. ヒット一覧(重要度順)

| 値 | 出力 / segment | 文脈 | 精密ブロック前後 | 元データ | 重要度 |
|---|---|---|---|---|---|
| 25.2% | Theme2 B1 `point_one`(rerun_02/03) | 男性29歳以下「ひとり旅」25.2% | 前 | F-202一次資料が小数第1位 | 高(既報告、OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01) |
| 44.7% | Theme2 B1 `point_two`(rerun_02/03) | 女性29歳以下「有名な観光地」44.7% | 前 | 同上 | 高(既報告) |
| **24.1%** | **Theme2 A2 `part1`(rerun_02、新規発見)** | 「1カ月休暇なら1週間程度」が最多、24.1%が選択 | 前 | F-205一次資料(2〜3泊23.2%/2週間11.1%/行かない18.0%との4択比較) | **高相当**(本文内では23.2%等の他選択肢の値自体は言及されておらず、24%へ丸めても「最多」の順位・意味は変わらない。ただし一次資料は僅差の4択比較のため「閾値前後」除外規定に触れる可能性はゼロではなく、最終判定はユーザー判断が必要) |
| 1.8(nights) | Theme2 A2/B1 `part1`/`part2` | 「平均泊数1.8泊、中央値2泊」 | 前 | 別調査(Jalan系) | 低(前回報告で判断済み、丸め困難・僅少値のため対象外と整理済み) |
| 8.1(years) | n3_01 Health A2/B1 `part1`相当 | 追跡研究の中央値追跡期間「8.1年」 | 前(原則自体が未存在、2026-08-17生成) | 研究論文の追跡期間 | 低(比較・閾値ではなく研究デザインの固有値、%型の目安丸め対象と性質が異なる) |
| なし | Hanshin(a2/b1b)、Household(a2/b1b) | — | — | — | 該当なし |
| なし | B-Family Voices Trial-09(b1b) | — | — | — | 該当なし(統計数値を扱わない記事のため) |

## 3. 修正要否の概算(参考値、修正は未実施)

- **24.1%(新規)**: 影響segmentは`part1`(Main Story)1件のみ。既存事例(OPEN-121実測¥3.64/segment)から類推し概算**数円〜十数円**。ただし選択肢A(決定的文字列置換)/選択肢B(Editor再実行で言い回し非決定的に変化しうる)の論点は25.2%/44.7%と同一構造で発生する。
- n3_01 3テーマ(Aug 17生成)は原則自体が存在しない時期の生成物であり、遡及的に「配線後との差分」を問う対象ではない(そもそも仕様が無かった)。修正要否はユーザー判断(新規原則を過去完成音声へ遡及適用するか)。

## 4. 既知failure mode照合

- `OPEN-112-THEME2-B1-NUMERIC-PRECISION-WIRING-AUDIT-01`(25.2%/44.7%、登録済み)。
- `OPEN-112-THEME2-AUDIO-REVIEW-FIX-02-PREVIEW-NUMERIC_REPORT.md`(c)(CEFRレベル間の数字粒度差、OPEN_ITEMS.md OPEN-112行に副次論点として記載、未登録の別Open Item)。
- **24.1%は上記いずれにも未記載の新規発見**(DECISION_LOG.md/OPEN_ITEMS.mdへ「24.1」の言及なしを確認済み)。

## USER_DECISION_REQUIRED候補

1. Theme2 A2「24.1%」への対応要否(選択肢A/B、25.2%/44.7%と合わせて一括対応するか)。
2. n3_01 3テーマ(Aug 17生成、原則自体が存在しない時期)へ新原則を遡及適用するか。
3. レベル間数字粒度差(OPEN-112-THEME2-AUDIO-REVIEW-FIX-02-PREVIEW-NUMERIC (c))の新規Open Item登録要否。
