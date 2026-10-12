# Phase D 正解表(案) GOLD_TABLE_DRAFT_01(2026-10-12、委任_02。Phase Dは実行しない。Fable確認後に凍結)

注: 本書は「案」。凍結前に (1) 自作記事の本文を作成し、(2) 各ターゲットが現行DBにあるか(V0で拾えるか)を¥0のローカル判定で確認し、(3) Fableが内容を確認してからsha凍結する。Coffee固有表現は正解表に入れない(hardcode防止、Coffeeはtrial基準fixtureとして別管理)。

## 1. 記事セット(案)

自作6記事(各300-350語。D1/D2/D3はStd(A2)+Adv(B1)の2 Level、D4-D6は1 Level。API不使用で自作)+既存実記事3本(Phase B走査で(a)が実際にヒットした自然な出現例を含む)+陰性対照2本。

| ID | 種別 | 狙い | 拾うべき表現(shortlistに残るべき) | 最終選定で選ばれるべき | 選ばれるべきでない |
|---|---|---|---|---|---|
| D1 | 典型Idiom(固定形) | DB収録固定形が劣化しないこと | spill the beans / break the ice / call it a day / hit the road(案。DB収録をローカル確認して確定) | 各Levelで1-2件(Stdは高頻度でないもの優先) | 透明な高頻度句(right/wrong系の基本定型) |
| D2 | 活用・代名詞・所有格変化Idiom | (a)の回復 | bit her tongue / lost his temper / pulling my leg / kept an eye on their kids(案) | 2件以上 | 字義用法の同形(下の陰性対照) |
| D3 | 辞書外の比喩・擬人化(Coffeeとは別の主語・動詞・名詞で自作) | (b1)の回復。DB外のため(b1)のみ | 擬人化・比喩を2-3箇所(例の方向性: 無生物が人の動作をする文。Coffee表現のコピー禁止、DB未収録をローカルで確認) | 1-2件 | 構成語から意味が推測できる透明表現 |
| D4 | phrasal verb中心 | 既存挙動の維持(退行なし) | figure out / run into / turn down / put off(案) | V0と同等の件数 | - |
| D5 | 透明な複数語表現のみ(陰性対照) | 偽陽性監視。拾いすぎないこと | なし(DB一致の透明句は残ってよいが選定で非字義的として選ばれないこと): bus stop / weekly meeting / a glass of water(案、Phase B記載の例とは別) | **なし**(Idiom枠を埋めない) | 全件 |
| D6 | Idiomなし(統計・技術中心) | 悪化0 | なし | V0とほぼ同一の5件 | 抽出件数に引きずられた非Idiom枠の押し出し |
| R1 | 既存実記事(`er014_output/four_type_observation_01/voices/run3_first_person/b1_2v_new_theme_attempt3/article.md`) | (a)が拾った自然出現 | `changes my mind`(ラベル=IDIOM_USE。見出し change one's mind) | 選ばれうる(必須ではない) | - |
| R2 | 既存実記事(`er011_output/news_ledger_enrichment_ab_trial_12/a2/enriched/run1/article.md`) | (a)が拾った曖昧例 | `made his mark`(ラベル=AMBIGUOUS。野球文脈で結果を出した意味) | 判断はFable/ユーザー | - |
| R3 | 既存実記事(`er011_output/discovery_focus_part_a_standalone_trial_01/b1b/article.md`) | (a)の字義用法ノイズ | なし(`open your eyes`は字義用法=陰性) | **選ばれてはならない** | `open your eyes`(字義) |
| N1 | 陰性対照(慣用句の字面を字義どおりに使った自作文) | 字義/比喩の判別 | なし | **選ばれてはならない** | 例: broke the ice on the pond / opened the can of beans and spilled them(字義)(案) |
| N2 | 陰性対照 | 同上(所有格付き字義用法) | なし | 同上 | open your eyes(字義)、lost her keys(字義)等(案) |

## 2. 指標定義

- 再現率(shortlist単位): 「拾うべき表現」のうちshortlistに残った割合。V0/V1/V2/V3それぞれ。
- 再現率(最終選定単位): 「選ばれるべき表現」のうち最終5件に入った割合。各記事n=2以上の反復で平均。
- 不要候補増: 抽出件数(b1+a)+予約枠のうち、最終5件に選ばれなかった件数(= 増えた候補のうち不採用)。陰性対照では「抽出された件数」自体も記録する(0件が理想)。
- 品質(押し出し): V0最終5件から押し出された表現の件数と、その妥当性(判断: 透明/既知として落ちるのが妥当か、学習価値のある表現が落ちたか)。**妥当性判定はFable/ユーザーが実施**(Sonnetは材料のみ提示)。
- 副指標: 正規化INVALID率(試行単位/最終runレベル)、Redundancy QA NG率(初回/retry後)、source_span整合不一致件数、1記事あたり費用。

## 3. 合格基準(案)

- 陰性対照(D5/D6/N1/N2/R3)で「選ばれてはならない表現が最終5件に入った」件数=0、かつ非Idiom枠の押し出し0(悪化0)。
- D1/D4はV0と同等以上(退行0)。
- D2はV1以上でshortlist再現率が向上、D3はV2で向上。
- 抽出件数分布: Coffee C1では全6回が上限5件(0件許可でも枠埋め偏り)。陰性対照で抽出件数が3以上なら「枠埋め偏り」が顕在化したと判定し、(b1)抽出Prompt/Level基準の見直しをFableへ報告。

## 4. 費用見積(Phase C実費 JPY14.44を差し引き、上限JPY50 → 残JPY35.56)

実測単価(Phase C): 抽出1回 約JPY0.15 / V2(選定+正規化+重複QA) 1runあたり JPY1.0-1.5(retry時は+JPY1.0-1.5) / V0相当も同程度(約JPY1.0-1.2) / VL約JPY0.37-0.71。

| 項目 | 内訳 | 費用見込み |
|---|---|---|
| 抽出+shortlist比較のみ(全14記事・Level、抽出n=3) | 0.15 x 3 x 14 | 約JPY6.3 |
| 最終選定(6記事・Level: D2 Std、D3 Adv、D5、D6、R1、N1): V0 x1 + V2 x2、canonicalization+QAまで | (1.1 + 1.3 x 2) x 6 | 約JPY22.2 |
| 予備(retry・追加反復) | | 約JPY3-5 |
| **計** | | **約JPY31.5-33.5(残JPY35.56内、余裕約JPY2-4)** |

余裕が小さいため、Phase D開始前にFableが記事数/反復数を絞るか、上限追加(要ユーザー判断)を決める。優先度が高い順: N1/D6(悪化0確認) > D2 > D3 > R3 > D5 > R1。
