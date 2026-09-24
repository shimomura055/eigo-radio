# comparison_sets.md (機械集計、観察のみ、評価はFable/ユーザー)

分類model: gpt-5.6-luna / 対象件数: 74

## 型タグ比率(集合別、%)

| 集合 | n | Everyday | Personal | Reversal | Talkability | BigChange | HardSocial | Tech | Product | Entertainment | domestic | international | unclear |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Reference(R) | 20 | 10.0 | 20.0 | 10.0 | 30.0 | 0.0 | 30.0 | 35.0 | 40.0 | 15.0 | 12 | 8 | 0 |
| ChatGPT API-only(A) | 20 | 25.0 | 20.0 | 20.0 | 30.0 | 0.0 | 25.0 | 35.0 | 30.0 | 15.0 | 14 | 5 | 1 |
| Luna API(B) | 17 | 29.4 | 11.8 | 0.0 | 17.6 | 0.0 | 5.9 | 23.5 | 70.6 | 11.8 | 14 | 0 | 3 |
| Trial-03(T3) | 17 | 23.5 | 58.8 | 0.0 | 17.6 | 0.0 | 29.4 | 29.4 | 17.6 | 17.6 | 13 | 0 | 4 |

## PR/広告混入率(Trial-03のみ、Source Gate結果に基づく機械算出)
Trial-03 PR/広告除外率: 0.185 (source_gate_round1+2, exclude=5/total=27)
R/A/Bはこの分類callにSource品質項目を含めておらず、機械算出のPR混入率は無い(N/A、必要ならFable判断で別途目視確認)。

## Referenceとの話題重複候補(機械ヒューリスティック、Jaccard>=0.3の単語一致のみ、目視推奨)
件数: 0