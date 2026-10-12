# PHASE_D_REPORT_02 (委任_04、2026-10-12) 結果: M1再確認PASS(6/6)、Phase D本体実行。陰性対照FAIL(R3 run1)のためTrial Status見込み = **再設計(REJECTED as-is)**

使用モデル: **gpt-6-luna**(抽出・選定・正規化・重複QAすべて)。最新世代最上位か: Productionの Family X KP選定(SUPPORT_MODEL)と同一(PM_GOVERNANCE 25節「Production比較可能性」例外、委任_02から継続)。Production code/Prompt/DB/共有Template/共有canonicalization無変更。SSOT: 暫定記録のみ(別途、DECISION_LOG/OPEN_ITEMS)。

## 1. extractor v3 の変更点(委任_03の v2 からの差分)
- Prompt `prompts/extractor_prompt_v3.txt`: 「通常は0〜2件」「枠が3件あることは3件出す理由にならない」を削除。「不透明度が高い順に最大3件、該当なしなら0件」「非透明な表現が1つでもあれば最も不透明なものを必ず rank 1」。schemaに `rank`(integer)追加。
- transparency欄は残すが除外ロジックから外し記録のみ(`self_declared_transparent` 除外を廃止)。Pythonがrank昇順に並べ替えてからcap3・検証・重複除外を適用。
- `LEVEL_DESC["adv"]` の旧表現「基本的な句動詞は既知」を、選定guidance(M4)と整合する文言へ修正。
- バグ修正: LLM候補dict生成行でコメントが `cefr_level`/`source_span` キーを飲み込んでいた(Phase C/委任_03のコードでは候補にこれら2キーが無かった)。キーが入るよう修正、testで固定。
- test: 47 -> 50件PASS(`phase_d/test_results_02.txt`)。Coffee語句のhardcode不在test(prompt/guidance/コード)維持。
- ドライ実行(API stub): 2回とも attempts 非空(V0/V1d各1 attempt)で「attempts空」は再現せず。原因は未特定のまま(委任_03時点で `STOP_ALL`(Family Z test由来)が一時存在した可能性。本件runnerはSTOP判定を本件用STOP/STOP_NOTICEのみに限定し、Family Z STOP_ALLは参考ログのみに変更)。

## 2. 凍結証跡
`phase_d/FROZEN_PLAN_02.md/json`: frozen_at = **2026-10-12T21:12:34+0900**。受入基準・variant定義・正解表(`GOLD_TABLE_02.md`)・記事は01と同一、変更点はv2->v3のみ(同書に明記)。`phase_d/cost_02.json` の最初の有料call started_at = **2026-10-12T21:12:40+0900** -> 凍結が全有料callより前。runnerは凍結shaが一致しないと起動しない。

## 3. M1: Coffee再確認(extractor v3、抽出のみ n=3 x Std/Adv、費用 JPY1.5018)
| Level | run | 抽出accepted(rank順) | pump-fist抽出 | V2 shortlist |
|---|---|---|---|---|
| Std | 1 | two numbers in the ring / pumps its fist / its own hidden clock | ○(rank2、core_span縮約) | ○ |
| Std | 2 | numbers in the ring / pumps its fist / its own hidden clock | ○(rank2) | ○ |
| Std | 3 | pumps its fist / in the ring / its own hidden clock | ○(rank1) | ○ |
| Adv | 1 | in the ring / been behind price increases / pumps its fist | ○(rank3) | ○ |
| Adv | 2 | two figures in the ring / been behind price increases / pumps its fist | ○(rank3、縮約) | ○ |
| Adv | 3 | pumps its fist / been behind price increases / in the ring | ○(rank1) | ○ |
- **MUST-1 = 抽出 6/6 かつ shortlist 6/6 でPASS**。
- 注意(原因の読み): pump-fistが rank1 になったのは 2/6 だけ(rank2 x2、rank3 x2)。MUST-1を満たした主因は「rank1構造」ではなく、**v3ではCoffeeで毎回3件(cap)出力され、pump-fistがその3件内に入った**こと。v2でAdv run1だけ落ちた原因(件数圧で2件に絞られ pump-fist が枠外)は、件数圧文言の削除で解消した。ただし rank1に入る構造とはいえず、「3件に収まる余裕」に依存する(記事に非透明表現が4件以上あれば落ちる余地は残る)。
- 副作用: 抽出件数は毎回3(cap)。Coffeeは比喩・慣用が複数ある記事なので妥当だが、下記R3(3件出て偽陽性)のように「3件埋め」が他記事でも起きる。

## 4. Phase D 結果表

### 4-1. 抽出(extractor v3、費用 JPY2.0924)
| 記事 | Level | role | n | raw件数 | accepted件数 | 主な内容 | 備考 |
|---|---|---|---|---|---|---|---|
| N1 | Std | 陰性 | 3 | 0,0,0 | 0,0,0 | 抽出なし | 字義用法の慣用句字面を非抽出(OK) |
| D6 | Adv | 陰性 | 3 | 1,1,1 | 0,0,0 | `make up`(既存DB重複) | OK |
| D5 | Std | 陰性 | 3 | 0,0,0 | 0,0,0 | なし | OK |
| R3 | Adv | 陰性 | 3 | 3,3,3 | 1,2,2 | `gets the first word`(3/3)/`lie less in`/`sleep inertia` | **偽陽性候補**。`under way`は既存DB重複、`has read the clock`はexcluded_by_existing_gate |
| D2 | Std | 正例 | 2 | 3,3 | 2,2 | `pulling my leg`/`bit her tongue`(`spill the beans`は既存重複) | 両者placeholderと同canonical(後述) |
| D3 | Adv | 正例 | 2 | 3,3 | 2,1 | run1: `taken out against the future`/`began to whisper`、run2: `holding its breath`(+ `is resting not retreating`は句読点またぎreject) | b1のみ候補は run1で2/3回収、run2で0/3 |
| D4 | Adv | 回帰 | 2 | 3,3 | 0,0 | 全件が既存DB重複(`turned down`/`add up to`/`picked up`、core_span縮約後) | 抽出追加なし |
- 陰性対照accepted平均 = **0.42/回**(基準 <=1 PASS。記事別 N1 0 / D6 0 / D5 0 / R3 1.67)。
- 主語込みスパン率(近似ヒューリスティック): Phase D accepted(縮約後)は 0件/全件。M1の抽出では raw spanが主語込みで core_span縮約が発生したものが 5件(accepted 18件中)、縮約後の最終spanは全て主語なし。
- 包含重複除外: 0件。self_declared_transparent除外: 0件(廃止)。reject理由別: crosses_punctuation_or_format 1(D3 run2)、excluded_by_existing_gate 1(R3 run1)。
- 予約枠: 未選択数は後述4-3。cap3による押し出し(overflow)は D2 のみ 1件(`change her mind`、placeholder 4件のうち3件を予約、1件overflow)。D2ではLLM候補(`pulling my leg`/`bit her tongue`)がplaceholderと同canonicalで、V2のpoolはplaceholderを先に登録するため重複はplaceholder側が残る(結果としてV2 shortlist = V1+d shortlist)。
- transparency自己申告(記録のみ): Phase D raw 30件は opaque 13 / semi 17 / transparent 0。transparent自己申告は出ず、除外に使える弁別力なし(v2と同じ)。R3の偽陽性 `gets the first word` も semi。

### 4-2. shortlist再現率(決定論、V0/V1+d/V2/V3、¥0。詳細 `analysis_02.md/json`)
| 記事 | V0 | V1+d | V2(run別) | V3 | 備考 |
|---|---|---|---|---|---|
| D2(gold6) | 2/6 | **5/6** | **5/6, 5/6** | 5/6 | overflow=`change her mind`。V0にあった gold(`kept an eye on`,`spill the beans`)は保持 |
| D3(gold6) | 2/6 | 3/6 | 4/6(5/6 partial), 3/6 | 3/6 | b1のみ3件(whisper/asleep/loan): run1が whisper+loan を回収、run2は0 |
| D4(gold8) | 4/8 | 4/8 | 4/8, 4/8 | 4/8 | V0 shortlistの句動詞はすべて残存(不変条件OK) |
| N1(gold5 字義陰性) | 1/5 | 3/5 | 3/5 x3 | 4/5 | 陰性記事でも(a)が`bit her tongue`/`opened his eyes`を予約枠へ(最終には入らず) |
| R3(`open your eyes`字義) | 0/1 | 1/1 | 1/1 x3 | 1/1 | (a)が`open your eyes`を予約枠へ(最終には入らず) |
| R1(`changes my mind`) | 0/1 | 1/1 | 1/1(noLLM) | **0/1**(overflow) | V3(b2ルール)は無関係な3件を先に予約し押し出す |
| R2(`made his mark`) | 0/1 | 1/1 | 1/1 | 1/1 | |
| D5/D6 | 追加0 | 追加0 | 追加0 | 追加0 | 予約枠0 |
- D2_shortlist(V2 exact >=5/6): **PASS(5/6、両run)**。D3_shortlist(b1のみ3件のうち>=1、**両runでPASS**必要): run1=2件回収、run2=0件 -> **FAIL(run2)**。

### 4-3. 最終選定(V0 n=1、V2 n=2。D5/D6/N1 は V2 run1,2)
| 記事 | variant | 最終5件(display_phrase) | gold | llm/placeholder由来 | 予約枠 / 未選択 | 重複QA | 正規化 |
|---|---|---|---|---|---|---|---|
| D2 | V0 | keep an eye on / divide / take away / spill the beans / bike lane | 2/6 | - | - | PASS | PASS |
| D2 | V2 r1 | bite one's tongue / pull someone's leg / lose one's temper / spill the beans / bike lane | **4/6** | 3(placeholder) | 3 / 0 | PASS | PASS |
| D2 | V2 r2 | pull someone's leg / bite one's tongue / lose one's temper / spill the beans / bike lane | **4/6** | 3 | 3 / 0 | PASS | PASS |
| D3 | V0 | shrug off / under the surface / take out / different story / renter | 2/6 | - | - | PASS | PASS |
| D3 | V2 r1 | take out against the future[LLM] / under the surface / hold one's breath[ph] / shrug off / interest rate | 3/6(選定時点) | 2 | 3 / 1 | **未到達** | **INVALID x2(run最終INVALID)**: `loan against the future`がsource_span内の連続部分でない(Rule7) |
| D3 | V2 r2 | hold one's breath[ph] / shrug off / under the surface / interest rate / retreat | 3/6 | 1 | 1 / 0 | PASS | PASS |
| D4 | V0 | new schedule / add up to / figure out / pick up / teamwork | 3/8 | - | - | PASS | PASS |
| D4 | V2 r1 | add up to / pick up / fade / weak / new schedule | 2/8 | 0 | 0 / 0 | PASS | PASS |
| D4 | V2 r2 | add up to / pick up / fade / new schedule / teamwork | 2/8 | 0 | 0 / 0 | PASS | PASS |
| N1 | V0 | freeze / break the ice / spill / come down / school pond | (字義陰性 1/5=break the ice) | - | - | PASS | PASS |
| N1 | V2 r1,r2 | freeze / break the ice / centimeter / spill / school pond | 同(1/5) | **0,0** | 2 / 2 | PASS | PASS |
| D6 | V0 | make up / installation costs / turn into / come from / coating | - | - | - | PASS | PASS |
| D6 | V2 r1,r2 | make up / caution / installation costs / stack / humidity ほか | - | **0,0** | 0 | PASS | PASS |
| D5 | V0 | walk away / community center / bus route / bus stop / next to | - | - | - | PASS | 初回INVALID->REVIEW_REQUIRED(V0でも) |
| D5 | V2 r1 | new bus route / fifteen minutes / rider / nearest / community center | - | **0** | 0 | PASS | PASS |
| D5 | V2 r2 | bus route / walk away / fifteen minutes / community center / rider | - | **0** | 0 | PASS | 初回INVALID->REVIEW_REQUIRED(V0同一原因 `a twenty-minute walk away`) |
| R3 | V2 r1 | **get the first word[LLM]** / sleep inertia / minute-perfect / slow-wave sleep / time-isolation | `open your eyes`は非選択 | **1(FAIL)** | 2 / 1 | PASS | PASS |

### 4-4. 受入基準の判定(事前凍結どおり)
| 基準 | 結果 |
|---|---|
| M1 MUST-1(抽出6/6・shortlist6/6) | **PASS** |
| 陰性対照FAIL(N1/D6/D5/R3、run単位、llm/placeholder由来最終 0件) | N1 0,0 / D6 0,0 / D5 0,0 / **R3 run1=1件(`get the first word`) -> FAIL** |
| 陰性対照 抽出accepted平均 <=1 | PASS(0.42) |
| D2_shortlist(exact >=5/6) | PASS(5/6 両run) |
| D2_final(両runで>=2件) | PASS(4件,4件。V0は2件) |
| D3_shortlist(両runでb1のみ>=1件) | **FAIL**(run1=2件、run2=0件) |
| D3_final(両runで>=2件) | PASS(3,3。ただしrun1はcanonicalization INVALIDのためrun最終gate未達) |
| D4_final(両runで>=2件 かつ CD>=V0-1) | PASS(2,2 / CD 2,2 >= V0のCD 2-1) |
| MUST-3 item単位(対象項目の正規化・重複QA) | D2対象3項目PASS、D3 `loan`系 INVALID、R3対象PASS |
| MUST-3 run単位(run最終gate全PASS) | V2 13runのうち11 PASS、INVALID 1(D3 r1)、REVIEW_REQUIRED 1(D5 r2。V0 D5でも同一原因) |

### 4-5. 陰性対照の評価(最優先)
- **FAILあり**: R3 V2 run1 の最終5件に LLM由来 `get the first word`(本文 `gets the first word`、extractorが rank1・semiで抽出し、R3では3/3回抽出された)が入った。凍結基準では1件でもFAIL。参考: 当該表現は「(他者より)先に主張する」の弱い比喩で、字義とも比喩ともつかない曖昧例。人間判断では偽陽性か許容かが割れる可能性があるが、基準は事後変更しない。
- N1/D6/D5: LLM・placeholder由来の最終採用は0件。N1では(a)が`bit her tongue`/`opened his eyes`を予約枠へ入れたが、選定LLMが字義用法として選ばなかった(Trial guidanceの条件が機能)。`break the ice`はV0の既存DB由来(字義陰性の弱点、V2で悪化ではない)。
- R3: `open your eyes`(字義)は予約枠に入るが最終に選ばれなかった(1run)。
- V1+d(extractorなし)の陰性対照: N1/D5/D6はextractor accepted=0のためV2 shortlistがV1+dと同一で、V2最終 N1/D5/D6 計6runのllm/placeholder 0件がそのままV1+dの陰性耐性の参考になる(ただしR3のV1+d最終は未実施)。

### 4-6. D4 句動詞回帰
- V0 shortlistの句動詞は全て残存(不変条件、shortlist 4/8=V0と同数)。最終5件: V2はgold 2/8(`add up to`,`pick up`)、V0は3/8(+`figure out`)。V2で`figure out`が`fade`/`weak`(単語)に置き換わった。D4はV2 shortlist=V0 shortlist(予約枠0、抽出追加0)なので差は **選定guidance(d)と選定のばらつき**由来。CD件数はV0 2、V2 2,2で基準(>=V0-1)PASS。`figure out`は非CD。B1学習者に`figure out`を落とすのが妥当かは要判断(押し出しの妥当性は下記)。

### 4-7. 押し出し(V0最終 vs V2最終)と妥当性所見(最終判断はFable/ユーザー)
| 記事 | V0から消えた | V2で新たに入った | 所見 |
|---|---|---|---|
| D2 | keep an eye on(gold)/divide/take away | bite one's tongue/pull someone's leg/lose one's temper(gold 3件) | `keep an eye on`はA2に既知の可能性が低い慣用句でgoldだが押し出された(2runとも)。差し引き gold 2->4。divide/take awayは優先度低で妥当 |
| D3 | take out/different story/renter | run1: take out against the future[LLM]/hold one's breath、run2: hold one's breath/retreat | 妥当。`take out`->LLM版の方が文脈に合う。ただしrun1は正規化INVALID |
| D4 | figure out/teamwork(r1) | fade/weak | `figure out`の押し出しは疑問(B1の基本句動詞なら妥当、文脈義なら不適)。`fade`/`weak`は単語でphrase優先から外れた |
| N1 | come down | centimeter | 中立(単語1語入替) |
| D6 | turn into/come from/coating | caution/stack/humidity | guidance(d)で透明な句動詞(turn into/come from)が下がり単語が上がる。意図した方向だが、V0と同一化の観点ではV0との差が残る |
| D5 | next to/bus stop 等 | rider/nearest/fifteen minutes | 中立 |

### 4-8. 副指標(運用コスト)
- 重複NG(Redundancy QA): 初回NG 0/13(V2)・0/6(V0)。retry使用 0/13、retry費用 JPY0。
- 正規化INVALID: V2 試行単位 3/15(20%)、run最終 INVALID 1/13・REVIEW_REQUIRED 1/13。V0 試行単位 1/7、run最終 REVIEW_REQUIRED 1/6(D5)。
- 1 job平均: V2 JPY0.894 / 103.7秒、V0 JPY0.932 / 106.5秒(差なし。V2はretry発生なし)。
- source_span整合不一致: 0件(全attempt)。

## 5. V1+d(Coffee Adv n=2、効果分離): **未実行(委任者への報告事項)**
必須分完了後(残額 >= JPY3)に `--stage v1d` を1回起動したが、私がラッパとして付けた `timeout 115` により約115秒で自プロセスを打ち切ってしまい(外部停止ではなく**自分のミス**)、selector_prompt.txtのみ生成された状態で未完了(`job_result.json`なし、cost_02.jsonに記録なし)。API呼出が一部実行されていた場合、未計上の費用が最大 約JPY1.6(2job x 0.8の見積)ある可能性がある。「有料run再起動は委任文が許可した回数のみ」に従い再起動していない。再実行する場合はFable/ユーザーの指示が必要(推定 JPY1.6〜2.5)。

## 6. 費用(JPY)
| 段 | 費用 | 累計(本件専用 / 上限50) |
|---|---|---|
| Phase C(委任_02) | 14.4411 | 14.4411 |
| 委任_03 M1(v2) | 1.2792 | 15.7203 |
| 委任_04 M1(v3) | 1.5018 | 17.2221 |
| 委任_04 抽出(18run) | 2.0924 | 19.3145 |
| 委任_04 最終選定(19job: V0 6/V2 13) | 17.2175 | 36.5320 |
| 計(`cost_02.json` cumulative 20.8117 + 過去15.7203) | | **36.5320**(残 13.4680。V1+d未計上分あり得る) |

## 7. Trial Status見込み と 根拠
**見込み: 再設計(REJECTED as-is)**。VALIDATED候補にはしない。
- 根拠(凍結基準): 陰性対照FAIL(R3 run1)、D3_shortlist FAIL(run2でb1のみ回収0)。Fableの事前指示どおり、FAIL時はREJECTED/再設計として報告。
- 効いた部分: (a)placeholder予約枠 + (c) + (d)guidanceは、D2で shortlist 2/6->5/6、最終 2/6->4/6、N1/D5/D6で偽陽性0。V1+dとV2のshortlistがD2/D3 run2で同一なので、効果の大半は(a)+(c)+(d)由来。
- b1(LLM抽出)の寄与: Phase DでのCoffee `pumps its fist`(MUST)回収に必要(a/c/d単独では回収できない。b2ルールでも回収可能とPhase Bで確認済み)、D3 run1のみb1のみ候補を回収。一方で R3の偽陽性を生んだ。**b1の費用対効果は「本文全文をLLMへ送る原則との衝突」を含めて疑問**。
- 再設計の方向(実装なし、候補): (1)(a)+(c)+(d)を主軸にし、b1は rank1の opaque のみ・または(b2)ルール候補(`pumps its fist`型)で代替できるか検討 (2)transparency自己申告は弁別力が無いため、別の判定(例: 別のLLM呼出での字義/比喩判定など)を使うかは新仕様でありユーザー判断。
- 未検証のためStatus断定に使わない: V1+d単独のCoffee効果、R3のV1+d最終、D3 run2の再現性(n=2のみ)。

## 8. Production採用時の前提(採用提案ではない。今回すべて未実装)
1. 原則文言の改訂(ユーザー判断): CURRENT_SPEC:1847「本文全文をLLMへ送らない」との衝突(b1採用の場合のみ。(a)+(c)+(d)のみなら衝突しない)。
2. model routing契約: 抽出段を新たに追加するなら `er006_model_routing_contract_01` に抽出用stage登録が必要(Trialではgpt-6-lunaを直接指定)。
3. telemetry: 抽出raw/accepted/reject理由・予約枠採用/未採用・llm/placeholder由来の最終採用数を既存telemetryへ追加する設計が必要。
4. feature flag / rollback: 予約枠と抽出段を記事単位で無効化できるflag、V0へ即時復帰できる経路。
5. Family X 12記事回帰: 全Std/Adv既存記事でV0 shortlist不変条件・最終選定差分・費用/所要時間を確認(今回は自作6記事+Coffee+R1〜R3のみ)。
6. OPEN-310決着: Rule7(its/my->someone's等)の許容表。D2で`pull someone's leg`はPASSだったが、Coffeeの`pump its fist`->`pump one's fist`、Phase C `one's own hidden clock`、D3 `loan against the future`のINVALIDは表の問題。
7. 重複NG retry上限時の挙動: 今回は重複NG 0件でretry未発生のため未検証。Production上限(2回)到達時の挙動(NGのままか、予約枠由来項目を落とすか)は未定義。

## 9. 未解決論点・Fableへの判断依頼
1. Status: 再設計でよいか。再設計する場合、(a)+(c)+(d)を主軸にb1を外す/弱めるか。
2. V1+d Coffee Adv n=2 の再実行可否(推定JPY1.6〜2.5、残13.47)。
3. R3 `gets the first word` を偽陽性とみなす基準の最終判断(凍結基準上はFAIL)。
4. D4 `figure out` 押し出しの妥当性、D2 `keep an eye on` 押し出しの妥当性。
5. WANT `mark the date`: 本Phase Dでは扱わず(Coffee固有でgold表に入れていない)。再定義はUSER_DECISION_REQUIRED。
6. `one's own hidden clock`型(辞書外比喩の過剰一般化)、`loan against the future`型(source_spanにない辞書形)のINVALIDは別論点(OPEN-310依存)。
7. 「attempts空」の原因未特定: 再現せず。仮説=Family Z STOP_ALL(test由来)の一時存在。runnerの判定対象を本件STOPのみに限定済み。
8. 本runnerの`--stage v1d`で`timeout`を付けると自プロセスを打ち切ってしまう点(運用ミス、再発防止: 有料runにtimeoutラッパを付けない)。

## 10. 成果物
`phase_d/`: FROZEN_PLAN_02.md/json、freeze_02.py、cost_02.json、m1_recheck_02/、m1_summary_02.json、extraction/、extract_summary_02.json、final/、final_summary_02_*.json、analyze_02.py、analysis_02.md/json、test_results_02.txt。`prompts/extractor_prompt_v3.txt`。
