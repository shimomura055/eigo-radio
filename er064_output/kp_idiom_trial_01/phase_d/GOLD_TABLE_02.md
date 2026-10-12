# Phase D 正解表 GOLD_TABLE_02(委任_03、凍結対象。GOLD_TABLE_DRAFT_01の硬化版)

本書の内容は `FROZEN_PLAN_01.md/json` に取り込まれ、Phase D有料call開始前に凍結する。Coffee固有表現は本書に入れない(Coffee MUST-1再確認は別枠 M1 として FROZEN_PLAN の `m1` に記載)。

## 1. 記事セット(自作はAPI不使用で作成。`phase_d/inputs/`)

| ID | Level | 種別 | 狙い | 実行 |
|---|---|---|---|---|
| N1 | Std(A2) | 陰性対照: 慣用句の字面を字義どおりに使った文 | 字義/比喩の判別。偽陽性監視 | 抽出n=3、最終V0 n=1・V2 n=2 |
| D6 | Adv(B1) | 陰性対照: Idiomなし(統計・技術) | 悪化0 | 抽出n=3、最終V0 n=1・V2 n=2 |
| D5 | Std | 陰性対照: 透明な複数語表現のみ | 偽陽性監視 | 抽出n=3、最終V0 n=1・V2 n=2 |
| R3 | Adv | 既存実記事。`open your eyes`は字義用法(陰性) | (a)の字義ノイズ | 抽出n=3、shortlist確認、最終V2 n=1(予算内・任意) |
| D2 | Std | 活用・代名詞・所有格変化Idiom | (a)の回復 | 抽出n=2、最終V0 n=1・V2 n=2 |
| D3 | Adv | 辞書外の比喩・擬人化 + DB収録比喩 | (b1)の回復 | 抽出n=2、最終V0 n=1・V2 n=2 |
| D4 | Adv | phrasal verb中心(文脈依存義を含む) | 退行監視(Coffee Adv `come with`/`show up`型の押し出し) | 抽出n=2、最終V0 n=1・V2 n=2 |
| R1 | Adv | 既存実記事(`changes my mind`=IDIOM_USE) | (a)が拾う自然出現 | shortlistのみ(¥0) |
| R2 | Std | 既存実記事(`made his mark`=AMBIGUOUS) | (a)が拾う曖昧例 | shortlistのみ(¥0) |

D1(DB収録固定形)はD2のspill the beans/kept an eye on、D4の句動詞で代替確認する(費用圧縮、独立記事は作らない)。N2はN1へ統合。

## 2. variant定義(固定)

- V0 = Production現行(`run_stage1_and_shortlist`のshortlistそのまま + Production guidance)。
- V1+d = V0 shortlist + (a)placeholder照合の予約枠(c) + Trial guidance(d)。(b1抽出なし)
- V2 = (a)placeholder + (b1)LLM補助抽出(extractor v2: cap3 / transparency自己申告でtransparent除外 / core_span縮約 / 包含重複除外)+ 予約枠(c: 上限3、cap15の外側)+ Trial guidance(d)。
- V3 = shortlistのみ(b2ルール候補 + c)。最終選定は行わない(¥0)。
- 不変条件: V0 shortlist ⊆ V1/V2/V3 shortlist(testで固定済み)。

## 3. 正解表(target)

`id`: 評価ID。`exact`: 主語なし完全一致(正規化後の全文一致、基本形・代名詞変形を含む)。`partial`: 部分一致(全キーワードがspan/display内に含まれる)。評価は「主語なし完全一致」と「部分一致」を分けて記録する。
shortlist単位=shortlistのsurface_formに対して。最終選定単位=最終5件のdisplay_phrase/key_phrase(完全一致)および display_phrase+source_span(部分一致)に対して。

### D2 (Std)
| id | exact | partial | V0で拾えるか(ローカル確認済み) |
|---|---|---|---|
| d2_temper | lost his temper / lose his temper / lose one's temper | temper | 拾えない(placeholderで回復) |
| d2_leg | pulling my leg / pull my leg / pull one's leg / pull someone's leg | leg | 拾えない(placeholder) |
| d2_tongue | bit her tongue / bite her tongue / bite one's tongue | tongue | 拾えない(placeholder) |
| d2_mind | change her mind / change one's mind | mind | 拾えない(placeholder) |
| d2_eye | kept an eye on / keep an eye on | eye | 拾える(V0) |
| d2_beans | spill the beans | beans | 拾える(V0) |

### D3 (Adv)
| id | exact | partial | 由来 |
|---|---|---|---|
| d3_breath | holding its breath / hold its breath / hold one's breath | breath | placeholder |
| d3_shrug | shrugged off / shrug off | shrug | V0 |
| d3_surface | under the surface | surface | V0 |
| d3_whisper | whisper a different story | whisper | b1のみ(辞書外) |
| d3_asleep | are asleep | asleep | b1のみ(辞書外) |
| d3_loan | a loan taken out against the future / taken out against the future / loan taken out against the future | loan | b1のみ(V0の`taken out`は部分のみ) |

### D4 (Adv)
| id | exact | partial | 文脈依存義(CD) |
|---|---|---|---|
| d4_comeswith | comes with / come with | comes with + come with(いずれか) | CD |
| d4_addup | add up / add up to | add up | CD |
| d4_pickedup | picked up / pick up | picked up | CD |
| d4_showup | show up | show up | CD |
| d4_raninto | ran into / run into | ran into | CD |
| d4_figure | figure out | figure out | - |
| d4_putoff | put off | put off | - |
| d4_turneddown | turned down / turn down | turned down | - |

(partialは各idで `partial_all` の全語を含むこと。comeswithは `comes with` を含むもの)

### 陰性(選ばれてはならない表現 / FAIL判定は2種類)
- **FAIL(一次)**: 最終5件のうち `llm_noncompositional` または `placeholder_title` 由来の項目が1件でもあればFAIL(run単位)。対象: N1/D6/D5/R3。
- 二次監視(FAILではない、報告のみ): N1の字義用法同形(`bit her tongue`/`opened his eyes`/`lost her keys`/`broke the ice`/spilled beans)が最終に入った件数(由来を問わず。`broke the ice`はV0=DB既存の弱点)。R3の `open your eyes`。

| id | 記事 | exact | partial |
|---|---|---|---|
| n1_tongue | N1 | bit her tongue / bite her tongue / bite one's tongue | tongue |
| n1_eyes | N1 | opened his eyes / open his eyes / open one's eyes / open someone's eyes | eyes |
| n1_keys | N1 | lost her keys / lose one's keys | keys |
| n1_ice | N1 | broke the ice / break the ice | ice |
| n1_beans | N1 | spill the beans / spilled the beans | beans |
| r3_eyes | R3 | open your eyes / open one's eyes / open someone's eyes | eyes |

### 実記事(shortlistのみ、判定材料)
- R1: `changes my mind`(exact: changes my mind / change my mind / change one's mind、partial: mind)
- R2: `made his mark`(exact: made his mark / make his mark / make one's mark、partial: mark)

## 4. 指標・合格基準(事前確定)

### 4-1. 一次指標
1. **陰性対照FAIL**(N1/D6/D5/R3、run単位): 最終5件の `llm_noncompositional`/`placeholder_title` 由来件数 = 0 でPASS。1件でもあればその記事×runはFAIL。FAILが1件でもあれば「偽陽性あり」とし、Trial StatusはREJECTEDまたはv2再Trial候補(根拠付き)。
2. **抽出件数(陰性対照)**: 陰性対照4記事×n=3のacceptedの1回あたり平均 ≤ 1 を合格(記事ごとの平均も記録)。2.0超なら枠埋め偏り(M1の効かず)と判定。D6はV0と同一化の検査として「予約枠由来の採用0件」(一次指標1と同じ)。
3. **D2**: shortlist再現率(exact, 6件) V2 ≥ 5/6(V0は2/6。予約枠cap3のため(a)placeholder 4件のうち最大3件が回復対象で、残り1件は予約枠overflow。overflow件数・押し出した候補は別途報告)。最終選定(run単位): D2 gold(6件)のうちexactまたはpartialで最終5件に ≥ 2件。両runでPASSを合格。V0 n=1の件数も併記。
4. **D3**: shortlist: b1のみ3件(whisper/asleep/loan)のうちexact/partial問わず shortlistに ≥ 1件(run単位、両runでPASS)。最終選定(run単位): D3 goldのうち ≥ 2件が最終5件(partial可)。両runでPASS。
5. **D4(退行監視)**: V0 shortlistの句動詞が全て残る(不変条件)。最終選定(run単位): D4 gold(8件)のうち ≥ 2件が最終5件(partial可)で、かつ文脈依存義(CD、5件)の最終5件内件数が V0最終のCD件数 − 1 以上。両runでPASS。
6. **Coffee MUST-1再確認(M1)**: `pump(s) its fist`相当(partial: pump & fist)が両Level n=3 で抽出accepted 6/6 かつ V2 shortlist 6/6。満たさなければSTOP。

### 4-2. 副指標(報告のみ、合否に使わない)
- 重複NG率(Redundancy QA 初回NG/最終NG)、retry使用率・retry費用・所要時間(秒)
- 正規化INVALID率(試行単位 / run最終単位)、REVIEW_REQUIRED件数
- 主語込みスパン率(accepted候補のうち主語名詞込みと判定された割合。近似ヒューリスティック: 限定詞/所有格で始まり3語以上で後続にbe動詞または-s/-ed/-es/-ing語尾語を含む、またはcore_span縮約が発生)
- 包含重複件数(containment duplicate除外件数)、抽出reject理由別件数、self_declared_transparent除外件数
- 押し出し: V0最終5件から押し出された表現と、V2で新たに入った表現(妥当性判定はFable/ユーザー)
- 不要候補増: 抽出accepted件数、予約枠のうち最終未選択件数
- source_span整合不一致件数

### 4-3. 実行優先順位(予算上限 JPY35.56 超過見込みでSTOP。陰性対照を削って収めない)
M1 → 抽出(全記事) → 最終選定: N1/D6 > D2 > D5 > D3 > R3(V2 n=1、任意) > D4 → 任意: Coffee Adv V1+d n=2(必須分完了後、残額≥JPY3の場合のみ)。
