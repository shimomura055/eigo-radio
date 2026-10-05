# OPEN-233 COST-FEASIBILITY-CHECK-01 量産原価と+¥2達成可能性(委任_16、¥0分析)

管理ID OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01。API支出0・コード/Prompt/gold変更0・Production未変更・`APPROVED_FOR_PRODUCTION`ではない。為替160円/USD固定。「実測」=ログ値(出典付き)、「推計」=式・前提付き。評価(3択の結論)はFableが後記する。集計: `er052_output/open233_kpi_recovery_02_offline_01/agg_production_set_cost_01.{py,json,md}`・`agg_production_set_cost_01_composite.json`・`agg_rep30_cost_breakdown_01.{py,json}`。

## §1 最新Production仕様のベース原価(Standard+Advanced 1セット)

「約¥40/記事」の出典はSSOTのGrepで特定できなかった(確認)ため使わない。単一runに全工程のログが揃わない(確認)ため、部品別の実測を合成した。最新=2026-09-29のFamily X refresh E2E(hormuz/meta run_03、gpt-5.6-luna=現行Production routing)と、同日のflash-lite TTS音声wiring run。

| 部品(円/セット) | hormuz型 | meta型 | 区分 | 出典(er019_output/配下) |
|---|---|---|---|---|
| Research+Ledger(web検索込み) | 28.74 | 28.74(借用) | 実測n=1 | family_x_b3_production_wiring_01/run_01(research14.47+ledger14.27) |
| Storyline | 0.67 | - | 実測n=1 | 同run_01 |
| JA生成+JA検査(=Fact Check JA) | 6.65 | 3.16 | 実測 | family_x_refresh_e2e_01/{hormuz,meta}/run_03 |
| 英語Std+Adv(writer+deviation check) | 2.82 | 4.22 | 実測(stage名無し、入力>=5000tok=check呼出は推計分類) | 同上 |
| scaffold(meta型のみ) | - | 5.01 | 実測 | family_x_audio_production_wiring_01/meta__run_03 |
| TTS(flash-lite、Standard同期) | 20.76 | 15.58 | 実測 | 同audio wiring(hormuz__run_06_flashlite_full_kp、meta__run_03) |
| ASR+TTS周辺LLM | 4.48 | 3.39 | 実測 | 同上 |
| **合計(TTS Standard同期、ログどおり)** | **64.1** | **60.1** | | |
| 合計(TTS=Batch、TTS半額) | 53.7 | 52.3 | 推計(flash-lite単価表 Batch=Standardの1/2、`pricing_snapshot.json`) | CURRENT_SPEC: 量産はBatch標準 |

- 実測不能: Support、Key Phrase選定LLM、Pronunciation Research等はこのログ群にstage名が無く集計不能(推計で埋めない)。上記は「最低限これだけかかる」下限寄り。
- 区分別統計(run単位、n/平均/中央/最大。duplicate含む): JA生成 n=12 0.96/0.86/2.63、JA検査 n=9 2.77/2.62/4.48、英語writer+check(stage名無し) n=6 2.27/1.91/4.22、ASR n=11 14.3/4.47/105(dev run含む)、TTS Standard n=11 42.3/17.5/155(旧Pro TTS・retry多発dev runを含む。flash-lite 3 runは15.6〜20.8)。
- retry上振れ(実測): hormuz run_03はrun_02に対しJA再生成2回でJA+2.94、英語+1.82。TTS retryは音声run差(15.6〜20.8 flash-liteの幅、旧dev runは最大155)。
- 約¥40との差の説明(推測を含む): 最新はResearch/Ledger web検索(約28.7)とTTS+ASR(約20〜25)が大きい。セット=2レベル分。旧値の内訳が不明のため差の確定は不能。

## §2 品質チェック純増(外数、gpt-6-luna単価=Trial実測の価格体系)

### 2-1 セット換算の根拠
- 確認: Family Xは Advanced(P1)・Standard(P2)で各々`run_deviation_check`が走る。ログでも1セット中の英語check呼出が3回(hormuz/meta run_03、入力>=5000tok)=Advanced・Standard各1+再検査1。`production_wiring_gap_open233_01.md` §2 P1/P2・§4-2: 「両levelに同一flowを適用」、Standardは「再検査で独立にCheck」。Stage 1の入力に記事本文を含むためLedger共有でも1回にならない。Rewrite/Recheck/出口3'-Rも記事単位。
- 結論: セット換算=記事単位の費用x2(確認+設計)。ただし(1)StandardがAdvanced由来で同一claimが多い場合のStage 2再判定reuseは未設計(推測)、(2)これまでのTrial/rep30のinstanceは英語1本(例 hormuz_run03_advanced/standard別、確認)で、過去の「+¥2/記事」判定が1本基準だった可能性がある(要確認、Fable論点)。以下は1記事基準とセット基準を併記。

### 2-2 新フロー費用(円/英語1記事)
| 項目 | low | mid | high | 区分・式 |
|---|---|---|---|---|
| Stage 1 r3 medium+r5 high | 1.23 | 1.23 | 1.23 | r3 0.447(G arm実測)+r5 0.785(段階A実測)、混合fresh未測定=推計 |
| Stage 2(候補比例) | 0.83 | 1.50 | 1.69 | low=fit上限10候補(0.099+0.073x10)、mid=0.1+0.064x21.8、high=0.099+0.073x21.8(外挿)。候補21.8=G arm NORMAL実測 |
| Rewrite+Recheck | 0.17 | 0.17 | 0.35 | mid=Rewrite率20/38(0.53、実測)x0.314、high=全記事Rewrite+cycle>=2 4/38 |
| 出口3'-R全文 | 0.22 | 0.22 | 0.45 | Rewrite記事のみ。mid=計画書平均、high=全記事x0.447 |
| **新フロー計/記事** | **2.45** | **3.11** | **3.72** | 推計。計画書の3.1にはshadow V4A 0.3が入っているが、本表は除外 |

rep30の後段実測再確認(`agg_rep30_cost_breakdown_01.json`、38 run): Stage 2 0.285・Recheck 0.165・Rewrite等0.10・Stage 1 0.023、計0.573/run、Rewrite20/38、cycle>=2 4/38。新フローのStage 2が候補比例になり約5倍(0.285→1.5)が主増分。

### 2-3 置換処理の差し引き(実測、二重計上なし)
差し引くのは現行英語deviation check(V4A Stage 1+再検査)のみ。refresh E2E run_03の3 call(gpt-5.6-luna実額: hormuz 1.71、meta 2.08)を6-luna単価換算で0.76/0.91/セット(実測tokens x6-luna単価、換算は推計)。JA検査・モデル世代差・writer全文再生成(約0.14〜0.3/セット、分離不確実)は未差引=保守。

### 2-4 ベース+純増=合計(円、推計。ベース=§1の2型平均 TTS Standard同期62.1/Batch53.0)
| | 通常(mid) | 下振れ(low) | 上振れ(high) |
|---|---|---|---|
| 新フロー計/セット(記事x2) | 6.22 | 4.90 | 7.44 |
| 差し引き(現行check、6-luna換算、実測) | -0.83 | -0.91 | -0.76 |
| **品質チェック純増Y/セット** | **+5.4** | +4.0 | +6.7 |
| 純増/英語1記事 | +2.7 | +2.0 | +3.3 |
| ベースX(Standard同期ログどおり) | 62.1 | 62.1 | 62.1 |
| **合計Z/セット(Standard同期)** | **67.5** | 66.1 | 68.8 |
| 合計Z/セット(TTS=Batch量産想定) | **58.4** | 57.0 | 59.7 |

- worst run(推計): rep30後段worst 4.14+Stage 1新1.23+Stage 2増分約1.2=約6.6/記事。retry/Human Reviewで更に上振れ。
- 参考(推計、価格体系の感度): 新フローをgpt-5.6-luna単価で動かすと約2.2倍(rep30 48.18/21.79、`agg_cost_recalc_models_01.md`)、mid純増/セットは約11.9(新6.22x2.21−現行check実額1.89)。gpt-6-luna採用は別途ユーザー判断(Opus#17 §6: 世代差を本設計の手柄にしない)。
- Human Review/STAGE4: API費用の追加callは本調査では確認していない(未確認)。人手工数は円換算しない。
- 純増は総コストの約8〜9%(mid、Standard同期ベース)。

## §3 +¥2達成の技術評価

### 3-1 改善幅(円)
| 基準 | 現状純増(mid) | +2までの削減幅 | low(2.0)で |
|---|---|---|---|
| 英語1記事基準(Trial従来単位) | +2.7 | -0.7/記事 | ほぼ境界(0) |
| セット基準(ユーザー原文) | +5.4 | -3.4/セット(-1.7/記事) | -2.0/セット |

構造的下限(推計): Stage 1純増=1.23−0.42(差し引き平均/記事)=+0.82/記事=+1.64/セット。セット基準では+2の82%をStage 1だけで使い、残り0.36/セットにStage 2(最小でも10候補0.83x2=1.66)・Rewrite・出口が収まらない。1記事基準では残り1.18/記事に対しStage 2+Rewrite+出口の現状1.9(mid)→必要削減0.7。

### 3-2 削減レバー(円/記事、Safety影響、規模、検証費。推計。実効性順)
| # | レバー | 削減/記事 | Safety影響 | 実装規模 | 検証Trial費 | 備考 |
|---|---|---|---|---|---|---|
| a | Stage 2出力短縮(551tok/候補→判定+短理由) | 0〜0.6(mid0.3) | 中: 判定前の推論量が品質を左右、gold再検証要 | 小(prompt/schema+test) | 約10〜20(保存候補のStage 2 replay) | **Stage 2はユーザー承認済み構成のため承認要**。551tokのreasoning/可視内訳はcall_logに無く不明=効果は判断不能 |
| b | Stage 2 batch内重複・同一fact束ね | 0.1〜0.39(上限=委任_10) | 低(入力共有のみ、判定は候補ごと) | 小〜中 | オフライン+約5 | 既にbatch済みで上限が小さい |
| g | Advanced→Standardの同一claim判定reuse | 0.1〜0.35/記事(セット0.2〜0.7、仮定:同一claim50%) | 低〜中(本文変更claimは再判定必須) | 中 | 約5〜10 | 新案(未承認・未設計)。rep30の非BLOCKING再利用(承認済み)の別levelへの拡張 |
| d | prompt caching(Ledger+記事の共通prefix) | 0.05〜0.15 | なし | 小 | E2E内実測 | Stage 1入力は10%のみ。段階A実測のcache命中2/83=期待薄 |
| c | Stage 1 SUPPORTED逐語引用省略 | 0〜0.13(E案推定) | 中: quote整合の根拠喪失の恐れ | 小 | 約8(r3のみ18 run) | 費用対効果低 |
| h | Recheck範囲限定(変更単位+前後1) | 既に2-2に算入済 | 低(Opus#16仕様) | 中(150〜200行、未実装) | - | 追加削減なし |
| f | 決定論事前処理 | 判断不能 | 緩和に近い | - | - | 既存precheckは24 fixtureで候補1件のみ、Stage 1候補は意味判断でStage 2前の決定論削減余地は小(推測) |
| i | Human Review/STAGE4 | API費用追加なし(未確認) | - | - | - | |

Safety維持の候補a+b+c+d合計: 0.15〜1.25/記事(mid約0.7)。+g(未承認案)で最大約1.6。

### 3-3 採れない/グレー
- 採れない(Safety KPI毀損、事前固定): r5 effort引下げ(A4-0 0/3)、r5-V(能力10〜12/18)、片経路化、候補上限、Safety-critical除外、gold変更、Checker甘化、r3/r5を1callの2判定に統合(冗長性喪失、削減も入力10%の範囲で約0.06)、exit 3'-R全文の省略(Opus#16必須)。
- グレー(Fable/ユーザー判断前に採らない): SEMI/VAGUE候補をtriage 1callに回す2層化(委任_10の表でA(e=0.2)+Bは約-0.46/記事)。「候補数を減らす」に該当し得る。gold 18/18・hold-out 9/9がstrict CONCRETEである事実はあるが小標本。

## §4 開発時間と追加費用(推計。本管理IDの委任実績: 1委任15〜55分、有料Trial 33〜42 runで15〜35分を基準)
### 4-1 実作業時間(レンジ)
| 工程 | 時間 | 内容 |
|---|---|---|
| ¥0分析 | 1〜3時間 | Stage 2のreasoning/可視内訳(保存usageから)、重複候補のオフラインreplay、cache可否、Advanced/Standard同一claim率 |
| 実装 | 4〜8時間 | a/b/g/dのflag実装+単体テスト(2〜4h)+Recheck新仕様(未実装、150〜200行、2〜4h)。全てTrial専用・既定OFF |
| 限定Trial | 1.5〜3時間 | Stage 2 replay(実行0.5〜1h+集計) |
| 最終E2E | 2〜4時間 | 20 run(実行1〜1.5h+集計・判定) |
| Opus独立レビュー(条件A/C) | 1〜2時間 | 必須Gate(回数上限外) |
| **合計** | **約9.5〜20時間(1.5〜3日)** | 並行不可の逐次委任4〜7本 |

### 4-2 追加費用(残¥98.29)
| 項目 | low | mid | high | 区分 |
|---|---|---|---|---|
| 実装 | 0 | 0 | 0 | API無し |
| 限定Trial | 10 | 18 | 36 | 推計: Stage 2 replay。low=gold含むbatchのみ、high=SC18+NORMAL6の全候補(24x1.5) |
| 最終E2E 20 run | 48 | 62 | 86 | 計画書(shadow V4A 約6を含む。shadow不要なら-6) |
| 合計 | 58 | 80 | 122 | |
| 残¥98.29との差 | +40 | +18 | **-24(不足)** | |

- midで収まるが余裕は¥18で、E2E失敗時の再実行(約¥62)は賄えない。上限側では約¥24不足。先に示す必要額: 余裕を持たせるなら追加約¥25(枠¥238→¥263)。最小E2E 18 run(約¥56、43〜77)なら合計mid 74、high 113(不足約¥15)。
- ループ3(Stage 2側を触る)はユーザー承認済み構成の変更を伴うため、実装前にユーザー承認が必要(レバーa)。

## §5 3択の材料(結論はFableが評価する。ここは事実のみ)
### 5-1 「+¥2を狙ってループ3を続行する価値が十分ある」を支持する事実
- 1記事基準では現状mid+2.7、low+2.0で、削減幅0.7がSafety維持レバー(a+b+c+d mid約0.7、範囲0.15〜1.25)と同程度。
- Stage 2は候補比例で、出力短縮・重複排除はSafetyの検出(Stage 1)に触れない。
- 純増は総コストの約9%(Z約58〜68/セット)。
### 5-2 「技術的にかなり厳しい」を支持する事実
- セット基準では必要削減-3.4/セット(-1.7/記事)で、Safety維持レバーの上限(約1.25、g込み1.6)を超える。Stage 1純増だけで+¥2の82%。
- Stage 1の最安Safety構成(r5 high必須)は確定済みで、effort引下げ・r5-V・片経路化は事実として不合格。
- Stage 2最小(10候補)でもセット1.66。候補21.8は外挿でさらに上振れし得る。
- 残予算の余裕がmidで¥18、high側は不足。
### 5-3 「追加情報がないと判断不能」を支持する事実
- KPI分母(記事かセットか)が過去判定でどちらだったか未確認で、結論が反転する(1記事=五分五分、セット=かなり厳しい)。
- Stage 2の551tokがreasoning主体か可視出力主体か未確認(レバーaの効果0〜0.6)。
- Stage 1混合構成(r3 medium+r5 high)のfresh費用・∪検出が未測定。Stage 2費用の候補21.8での実測がない(fit範囲10候補)。
- 現行checkの実費はstage名なしログからの分類(3 call/セット)で、Production全記事の確定値ではない。
