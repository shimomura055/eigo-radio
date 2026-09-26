# structure_ratio.md — 構成比率分析(NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01)

対象: small_bag(A2/B1B)、meta(A2/B1B、Fact fidelity修正後)。
**hormuz(ホルムズ海峡)は対象外**(Advanced段でLedger Deviation MAJORのため
Standard/Advanced本文が存在しない。詳細は本ディレクトリの
`NEWS-FAMILY-X-B3-DIVERSITY-TRIAL-01_REPORT.md` §Hormuz参照)。

生データ: `structure_ratio_raw.json`(本ディレクトリ、プログラムで算出。
手動集計ではない)。

## wpm/cps推定根拠(既存実測、evidence-based)

- **A2レベル英語(Full Story/Point/In One Line)**: `er014_output/
  user_test_news_light_01/tiny_bags/a2/audit/tts_generation_results.json`の
  実測`duration_seconds`(ASR-verified、実際にTTS生成・検証済みの音声)と
  該当テキストの英単語数から算出。full_story_part1=119.5wpm、
  full_story_part2=125.7wpm、point_one=110.4wpm、point_two=119.4wpm、
  in_one_line=118.0wpm(平均118.6 → **119wpmを採用**)。
- **A2レベル日本語Comment/Preview**: 同ファイルの実測durationと日本語
  文字数(空白除く)から算出。comment_1=6.39、comment_2=4.93、
  comment_3=5.84、comment_4=5.33、preview=5.38、japanese_title=4.82
  chars/sec(平均5.45 → **5.4 chars/secを採用**)。
  (参考: `CURRENT_SPEC.md`記載のA2英語ナレーション速度の目安は約135wpm
  だが、これはhard constraintではない目安値であり、実測値[119wpm]の方が
  本分析の目的[想定音声秒数の推定]には適切と判断した)。
- **B1(Advanced)レベル英語(Comment/Preview/Full Story/Point/In One Line、
  全segmentが英語)**: `tts_generation_results.json`にはB1Bの
  `duration_seconds`フィールドが記録されていなかったため、`er014_output/
  user_test_news_light_01/tiny_bags/b1b/narration/*.wav`の実ファイルを
  Python標準`wave`モジュールで直接読み取り、フレーム数/サンプルレートから
  秒数を算出した(新規ライブラリ導入なし)。comment_1=144.2、
  comment_2=137.2、comment_3=153.0、comment_4=154.5、preview=154.2、
  full_story_part1=140.8、full_story_part2=140.8、point_one=139.7、
  point_two=143.0、in_one_line=138.5wpm(平均144.6 → **145wpmを採用**)。
  B1レベルはA2より速いテンポで測定された(全segment英語のため、
  日本語Comment切替のポーズが挟まらない分、体感テンポが速くなっている
  可能性がある。因果は未検証、observationのみ)。

## 表(推定音声秒数・全体比率)

### small_bag — A2(Standard)

| segment | 種別 | units | 推定秒数 | 全体比 |
|---|---|---|---|---|
| Preview | 文字数(JA) | 85 | 15.7s | 6.4% |
| C1 | 文字数(JA) | 42 | 7.8s | 3.2% |
| 本文1 | 語数(EN) | 61 | 30.8s | 12.5% |
| C2 | 文字数(JA) | 66 | 12.2s | 5.0% |
| 本文2 | 語数(EN) | 55 | 27.7s | 11.2% |
| C3 | 文字数(JA) | 134 | 24.8s | 10.1% |
| Point1 | 語数(EN) | 80 | 40.3s | 16.4% |
| Point2 | 語数(EN) | 128 | 64.5s | 26.2% |
| C4 | 文字数(JA) | 89 | 16.5s | 6.7% |
| In One Line | 語数(EN) | 12 | 6.1s | 2.5% |
| **合計** | | | **246.4s** | 100% |

### small_bag — B1B(Advanced)

| segment | 種別 | units | 推定秒数 | 全体比 |
|---|---|---|---|---|
| Preview | 語数(EN) | 42 | 17.4s | 8.3% |
| C1 | 語数(EN) | 15 | 6.2s | 2.9% |
| 本文1 | 語数(EN) | 67 | 27.7s | 13.2% |
| C2 | 語数(EN) | 24 | 9.9s | 4.7% |
| 本文2 | 語数(EN) | 61 | 25.2s | 12.0% |
| C3 | 語数(EN) | 33 | 13.7s | 6.5% |
| Point1 | 語数(EN) | 85 | 35.2s | 16.7% |
| Point2 | 語数(EN) | 134 | 55.4s | 26.4% |
| C4 | 語数(EN) | 35 | 14.5s | 6.9% |
| In One Line | 語数(EN) | 12 | 5.0s | 2.4% |
| **合計** | | | **210.2s** | 100% |

### meta(Fact fidelity修正後) — A2(Standard)

| segment | 種別 | units | 推定秒数 | 全体比 |
|---|---|---|---|---|
| Preview | 文字数(JA) | 90 | 16.7s | 6.0% |
| C1 | 文字数(JA) | 37 | 6.9s | 2.5% |
| 本文1 | 語数(EN) | 88 | 44.4s | 16.1% |
| C2 | 文字数(JA) | 71 | 13.1s | 4.7% |
| 本文2 | 語数(EN) | 102 | 51.4s | 18.6% |
| C3 | 文字数(JA) | 119 | 22.0s | 8.0% |
| Point1 | 語数(EN) | 128 | 64.5s | 23.3% |
| Point2 | 語数(EN) | 60 | 30.3s | 11.0% |
| C4 | 文字数(JA) | 97 | 18.0s | 6.5% |
| In One Line | 語数(EN) | 18 | 9.1s | 3.3% |
| **合計** | | | **276.3s** | 100% |

### meta(Fact fidelity修正後) — B1B(Advanced)

| segment | 種別 | units | 推定秒数 | 全体比 |
|---|---|---|---|---|
| Preview | 語数(EN) | 49 | 20.3s | 9.0% |
| C1 | 語数(EN) | 14 | 5.8s | 2.6% |
| 本文1 | 語数(EN) | 96 | 39.7s | 17.5% |
| C2 | 語数(EN) | 24 | 9.9s | 4.4% |
| 本文2 | 語数(EN) | 100 | 41.4s | 18.3% |
| C3 | 語数(EN) | 36 | 14.9s | 6.6% |
| Point1 | 語数(EN) | 119 | 49.2s | 21.7% |
| Point2 | 語数(EN) | 61 | 25.2s | 11.1% |
| C4 | 語数(EN) | 30 | 12.4s | 5.5% |
| In One Line | 語数(EN) | 18 | 7.4s | 3.3% |
| **合計** | | | **226.3s** | 100% |

## 観察(強制なし、自由生成の結果)

- 4本すべてで **Point2が全体の21〜26%と最大の比率**を占めた(4本中4本)。
  Point構造は「30〜60語目安、25〜70語許容」(`CURRENT_SPEC.md`診断的目安)
  よりも語数の多いPointが複数見られた(small_bag Point2=128語[A2]/134語
  [B1B]、meta Point1=128語[A2])。目安を超えているが、hard capではないため
  Gate違反ではない。
- Comment(C1〜C4)は各記事でA2/B1Bとも合計で全体の17〜24%程度に収まり、
  4本の間で比率が大きく崩れる兆候は見られなかった。
- 本文1+本文2の合計比率はA2で23.7%(small_bag)〜34.7%(meta)、B1Bで
  25.2%(small_bag)〜35.8%(meta)と、記事間で最大約10ポイントの差があった
  (meta記事は本文が相対的に長い)。
