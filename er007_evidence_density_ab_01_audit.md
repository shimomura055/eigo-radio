# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part A-5: Evidence Density Audit

No.4〜6のspoken script(Full Story Part1/2・Point One/Two本文)に含まれるEvidence表現を
カテゴリ別に抽出し、`KEEP` / `COMPRESS` / `REMOVE_FROM_SPOKEN` に分類した。

凡例: `KEEP`=そのまま維持、`COMPRESS`=情報は残すが密度を下げる、`REMOVE_FROM_SPOKEN`=spoken layerから削除(Ledgerからは削除しない)。

## No.4 スーパーマーケット棚替え

| カテゴリ | 該当表現 | 判定 | 理由 |
|---|---|---|---|
| research year | "A 2025 trade article"の2025年、"In a 2021 study"の2021年、"A 2023 field study"の2023年、"A 2022 study"の2022年 | `REMOVE_FROM_SPOKEN` | 聞き取りに意味を持たない出版年。Ledgerには残す |
| researcher/institution name | "Vogel and colleagues" | `REMOVE_FROM_SPOKEN` | 物語上、名前を覚える必要がない。副次効果としてASR誤認識リスク(実際にASR fragileな固有名詞と確認済み)も下がる |
| journal name | "*PLoS Medicine*" | `REMOVE_FROM_SPOKEN` | 出典の格を示すだけで、聞き取り理解には不要 |
| sample size | "six discount supermarkets"、"150 women"、"205 supermarkets shoppers" | `COMPRESS` | 「3店舗 vs 3店舗」という比較設計自体はStory上重要(因果解釈の妥当性を支える)なので構造は残し、正確な店舗数・調査対象者数は削減 |
| meaningful statistic | "6,170 portions per store each week"、"9,820 portions"、"1,359 fewer portions" | `KEEP`(ただし"standard deviations"は削除) | 具体的なポーション数は驚き・スケール感がありStoryの核心。統計単位(標準偏差)は一般聴衆に意味を持たないため削除 |
| location | "UK"/"England"、"Greece" | `COMPRESS` | 地域性はやや残すが、精度(具体的な都市名等)までは追わない |
| methodology | "field study"、"transaction data"の分析手法詳細 | `COMPRESS` | 「データを使って判断した」という骨子は残し、手法名の詳細は削る |
| other attribution | "An industry article also lists..." | `KEEP`(単数形に修正) | 単一の出典であることを正確に保つ |

## No.5 カフェのラップトップ問題

| カテゴリ | 該当表現 | 判定 | 理由 |
|---|---|---|---|
| research year | "A 2021 qualitative study" | `REMOVE_FROM_SPOKEN` | 出版年は物語に不要 |
| researcher name | "L. Mimoun and A. Gruen" | `REMOVE_FROM_SPOKEN` | 実際にASR fragileな固有名詞(前タスクのCascade分析で確認済み)。物語上も名前は不要 |
| journal name | "*Journal of Service Research*" | `REMOVE_FROM_SPOKEN` | 同上 |
| sample size / methodology | "38 third places"、"52 observation visits"、"27 customers"、"12 service providers"、"55 media sources" | `REMOVE_FROM_SPOKEN`(構造は`COMPRESS`) | 個々の数字は聞き取り負荷が高いだけで理解に寄与しない。「観察とインタビューを組み合わせた」という手法の骨子はCOMPRESSで残す |
| classification framework名(Archetypal/Status Quo/Compromise/PTP) | 4類型の名称・定義 | `KEEP` | これは記事全体の説明ロジックの中心であり、削除するとStoryが成立しない |
| exact date | "on April 28, 2026" | `REMOVE_FROM_SPOKEN` | 正確な公開日は不要 |
| meaningful statistic | "more than 70 percent of seats"、"a 25 percent drop in sales" | `KEEP` | 驚き・スケール感のある具体的数字で、Storyの核心(なぜThe Barnが方針転換したか)を支える |
| location | "Berlin"、"Neukölln" | `COMPRESS` | 「ベルリンのカフェ」は残すが、地区名(Neukölln)は削る |
| researcher/founder name | "Ralf Rüller" | `REMOVE_FROM_SPOKEN` | 発言内容(「良いコーヒー体験を提供したい」)自体はKeepするが、フルネームは不要かつ非英語名でASR/TTSリスクがある |
| attribution | "Coffee Intelligence"の出典 | `COMPRESS` | 「業界レポートによると」という帰属自体は保持(事実の確度を示すため)、社名の反復は減らす |

## No.6 配送追跡ページの心理

| カテゴリ | 該当表現 | 判定 | 理由 |
|---|---|---|---|
| research year | "A 2025 longitudinal study"、"a 2021 *Scientific Reports* experiment" | `REMOVE_FROM_SPOKEN` | 出版年は不要 |
| researcher name | "Howell and Sweeny" | `REMOVE_FROM_SPOKEN` | 実際に"Sweeny"/"Sweeney"のASR不一致でTTS再生成が繰り返されていた固有名詞(直近2タスクで検証済み)。削除により物語理解を損なわず、副次的にASR waste削減効果もある |
| journal name | "*Emotion*"、"*Scientific Reports*" | `REMOVE_FROM_SPOKEN` | 不要 |
| example groups(選挙・司法試験・採用) | "2020 United States presidential election"、"California bar exam"、"academic job" | `KEEP`(年・州名も維持) | Ledgerのscope定義そのもの。当初「調査期間・地域」として圧縮候補にしたが、Ledger Deviation Checkで「対象範囲を広げている」との指摘を受け、年(2020)・州名(California)を復元した。**圧縮しすぎるとscope超過になる実例** |
| sample size / age range | "28 healthy people aged 19 to 29" | `REMOVE_FROM_SPOKEN` | 聞き取り負荷が高いだけで理解に寄与しない |
| statistical notation | "b = 0.90, P < 2 × 10⁻¹⁶" | `REMOVE_FROM_SPOKEN` | 一般聴衆に理解不能な統計記法。定性的な強さの表現("strong")へ置き換え、過大評価にならないよう注意(p<10⁻¹⁶という非常に強い統計的有意性を"strong"と表現するのは控えめな評価であり誇張ではない)。**この文はNo.6コストRCA(前々タスク)で実際にTTS再生成waste最大の原因だった箇所そのもの** |
| meaningful statistic | なし(既存の"more worried, searched more often"は定性的パターンで数字を伴わない) | — | — |
| uncertainty hedges | "This is a possible mechanism, not proven causation"等 | `KEEP` | 原則5(不確実性の維持)により厳守 |

## 全体件数サマリー(Part A-5要求)

| カテゴリ | KEEP | COMPRESS | REMOVE_FROM_SPOKEN | 合計 |
|---|---|---|---|---|
| research year | 0 | 0 | 8 | 8 |
| sample size | 0 | 2 | 4 | 6 |
| study duration | 0 | 1 | 1 | 2 |
| number of studies | 0 | 0 | 2 | 2 |
| researcher/institution name | 0 | 0 | 6 | 6 |
| location | 0 | 3 | 1 | 4 |
| methodology | 0 | 2 | 1 | 3 |
| legal/date detail | 0 | 0 | 1 | 1 |
| meaningful statistic | 4 | 0 | 0 | 4 |
| other attribution | 2 | 1 | 0 | 3 |
| **合計** | **6** | **9** | **24** | **39** |
