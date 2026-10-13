# collapse_rate_03 (FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-LISTEN-COMPARE-01 委任_03, 2026-10-13)

Trial(VALIDATED上限)・採用判断なし・API呼出なし(既存ログの読取集計のみ、JPY0)。モデル: 集計対象の生成はすべて gemini-3.8-flash-lite-tts / voice Aoede(新規生成なし)。結論は書かない(Fableが判断)。

## 0. 範囲と定義
- 集計対象: generation_log_*.jsonl 全128 call。主集計=TRIAL-03(R1-3)58 + TRIAL-04(R4-6)26 + TRIAL-05(L02)8 = **92 call**。TRIAL-02(36 call)は参考(別集計)。委任文の「約116」は費用累計JPY118.02近傍の呼称で、log上の件数は92(+36)。
- 生成破綻(固定定義): (a) raw WPM<120 / (b) 同Prompt・同Levelの他takeの中央値に対し音声長1.3倍以上(他take>=2必須、1take Promptは判定不能) / (c) ASR TRUE_CONTENT_MISMATCHかつ原稿との差分ブロック(挿入/欠落/置換)が3語以上(1〜2語の置換・挿入は除外)。
- raw WPM = 原稿語数/生成直後(減速前)音声長。Std減速後の聞こえのWPMは wpm_heard。差分は tts_input 正規化語列と ASR text の difflib。
- 速度語あり = styleに slow/slower/slowly/measured/deliberate/relaxed/unhurried/rushing/pace/tempo/words per minute/steady/noticeably のいずれか(広義)。減速語あり = slow系/measured/deliberate/relaxed/unhurried/rushing(狭義)。prompts_r*.jsonに decel_word フィールドは無いため、style文字列から機械判定。

## 1. 生成破綻call一覧 (主集計+参考 全128中 2件)

| trial | round | job | Prompt | Lv | take | WPM聞こえ | raw WPM | raw長s | 他take中央値比 | out_tokens | tts JPY | 長無音(800ms+) | ASR | a | b | c |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TRIAL-03 | R1 | J11_adv_part1_t1 | J11 | adv | 1 | 161.5 | 161.5 | 48.67 | None | 1220 | 1.1838 | 0 | TRUE_CONTENT_MISMATCH | False | False | True |
| TRIAL-05 | L02 | N01_std_part1_t3 | N01 | std | 3 | 79.1 | 83.8 | 83.73 | 1.92 | 2094 | 2.0217 | 5 | TRUE_CONTENT_MISMATCH | True | True | True |

- J11_adv_part1_t1(TRIAL-03 R1): 原稿外の1文を挿入(25語: 'some people are happier about the drop in price than others and the price at the grocery store might change with the news')。音声長48.67sは他take比較不能(J11は1take)。style='Warm and clear, with a smile. Calm pace, short pauses.'。同styleのStd(J11_std)は正常(NORMALIZED_MATCH)。
- N01_std_part1_t3(TRIAL-05 L02): **ASR全文が原稿を2回連続で読み上げた形**(asr_words=240 vs 原稿117語、先頭から末尾まで同文2周)。音声83.73s≒他take(43.2/44.0s)のほぼ2倍。聞こえのペース自体は 240語/88.74s≒162WPM で通常範囲。79.1WPMは『1周分の語数÷2周分の時間』による見かけの値。長無音5本(950/950/1060/1060/980ms)は2周の文末(delay.→International、continue.→The/US、too.→a)に分布。
- 非破綻callの最低raw WPM=155.7(N02 std t2)、他take比の最大=1.09。破綻2件は他の全callと明確に分離(境界例なし)。

## 2. 発生率 (破綻/call、Wilson95%区間)

| 区分 | 主集計(TRIAL-03/04/05) | TRIAL-02(参考) | 全体(128) |
|---|---|---|---|
| 全体 | 2/92 (2.2%) [0.6-7.6%] | 0/36 (0.0%) [0-9.6%] | 2/128 (1.6%) [0.4-5.5%] |
| Std | 1/46 (2.2%) [0.4-11.3%] | 0/18 (0.0%) [0-17.6%] | 1/64 (1.6%) [0.3-8.3%] |
| Adv | 1/46 (2.2%) [0.4-11.3%] | 0/18 (0.0%) [0-17.6%] | 1/64 (1.6%) [0.3-8.3%] |
| 速度語あり(広義) | 2/86 (2.3%) [0.6-8.1%] | 0/18 (0.0%) [0-17.6%] | 2/104 (1.9%) [0.5-6.7%] |
| 速度語なし | 0/6 (0.0%) [0-39.0%] | 0/18 (0.0%) [0-17.6%] | 0/24 (0.0%) [0-13.8%] |
| 減速語あり(狭義) | 1/72 (1.4%) [0.2-7.5%] | 0/6 (0.0%) [0-39.0%] | 1/78 (1.3%) [0.2-6.9%] |
| 減速語なし | 1/20 (5.0%) [0.9-23.6%] | 0/30 (0.0%) [0-11.4%] | 1/50 (2.0%) [0.4-10.5%] |
| Take1 | 1/74 (1.4%) [0.2-7.3%] | 0/12 (0.0%) [0-24.3%] | 1/86 (1.2%) [0.2-6.3%] |
| Take2 | 0/10 (0.0%) [0-27.8%] | 0/12 (0.0%) [0-24.3%] | 0/22 (0.0%) [0.0-14.9%] |
| Take3 | 1/8 (12.5%) [2.2-47.1%] | 0/12 (0.0%) [0-24.3%] | 1/20 (5.0%) [0.9-23.6%] |

注: 主集計の速度語なし(6call)は少数。Take別はTake1が大多数(主集計 74/10/8)でTake3は少数。

### Prompt別(N01/N02: 各Lv3take)
- N01|std: 1/3 (33.3%) [6.1-79.2%]
- N01|adv: 0/3 (0.0%) [0-56.2%]
- N02|std: 0/3 (0.0%) [0-56.2%]
- N02|adv: 0/3 (0.0%) [0-56.2%]
- 3take以上ある全 Prompt×Lv(20組)のうち、音声長が2倍近くになったのはN01 Stdのみ(他は最大比1.09)。

## 3. N01 Std / Adv の3take比較

| Prompt | Lv | take | WPM聞こえ | raw WPM | 聞こえ長s | raw長s | out_tokens | tts JPY | 文末平均/最大ms | 長無音800ms+ | ASR | 異音med+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N01 | std | 1 | 153.5 | 162.7 | 45.73 | 43.16 | 1079 | 1.0473 | 494/800 | 0 | NORMALIZED_MATCH | 0 |
| N01 | std | 2 | 150.6 | 159.6 | 46.61 | 43.99 | 1103 | 1.0703 | 573/810 | 1 | NORMALIZED_MATCH | 0 |
| N01 | std | 3 | 79.1 | 83.8 | 88.74 | 83.73 | 2094 | 2.0217 | 569/980 | 5 | TRUE_CONTENT_MISMATCH | 1 |
| N01 | adv | 1 | 167.1 | 167.1 | 47.03 | 47.03 | 1177 | 1.1425 | 627/830 | 1 | NORMALIZED_MATCH | 0 |
| N01 | adv | 2 | 174.7 | 174.7 | 45.0 | 45.0 | 1125 | 1.0926 | 539/660 | 0 | NORMALIZED_MATCH | 0 |
| N01 | adv | 3 | 159.4 | 159.4 | 49.32 | 49.32 | 1233 | 1.1962 | 607/730 | 0 | NORMALIZED_MATCH | 0 |
| N02 | std | 1 | 161.3 | 170.9 | 43.53 | 41.08 | 1027 | 0.9974 | 514/800 | 1 | NORMALIZED_MATCH | 0 |
| N02 | std | 2 | 146.9 | 155.7 | 47.78 | 45.09 | 1134 | 1.1001 | 621/870 | 3 | NORMALIZED_MATCH | 0 |
| N02 | std | 3 | 160.2 | 169.7 | 43.83 | 41.36 | 1034 | 1.0041 | 494/790 | 0 | NORMALIZED_MATCH | 0 |
| N02 | adv | 1 | 170.9 | 170.9 | 46.0 | 46.0 | 1150 | 1.1166 | 600/850 | 1 | NORMALIZED_MATCH | 0 |
| N02 | adv | 2 | 179.3 | 179.3 | 43.84 | 43.84 | 1096 | 1.0647 | 476/740 | 0 | NORMALIZED_MATCH | 0 |
| N02 | adv | 3 | 172.1 | 172.1 | 45.68 | 45.68 | 1142 | 1.1089 | 447/670 | 0 | NORMALIZED_MATCH | 0 |

- N01 Stdの3takeは style_sha256・tts_input_sha256・manuscript_sha256・input_tokens(143)が完全一致(同一Prompt・同一入力)。N01/N02の12 callはいずれも文末last3語一致=True。N01 Std t3のduration_anomalyはFalse(max_reasonable=179.5s未満)。
- 事実: duration_anomaly判定は83.7sを異常としない。検知できたのはASR(TRUE_CONTENT_MISMATCH)と測定(語数/長さ)。

## 4. call費用とtoken

- 全128 callで output_tokens / raw_duration_s = 25.0〜25.03 token/s(中央値25.0)。音声1秒=約25 token一定。
- tts_cost_jpy と output_tokens は線形(R2=0.999974、0.961 JPY/1000token、最大残差0.0020 JPY)。
- N01 Std t3: 2094 token / 83.76s / JPY2.0217。同Promptのt1/t2は1079/1103 token(JPY1.047/1.070)。費用は出力音声長(=2周読み)に比例しており、課金異常ではない。非破綻callの中央値は1066.5 token / JPY1.036。

## 5. 判断材料(事実のみ。結論はFable)

仕様(Prompt)起因を支持する事実:
- N01 Stdの3take中1件(33%)で発生。N01は速度語1語を含む(speed_word_count=1)Prompt。
- 破綻2件とも広義の速度語を含むPromptの出力(J11 'Calm pace'=広義のみ、N01 'a pace a little slower'=狭義の減速語)。速度語なしPrompt(主集計6call+参考18call)では0件。ただし区間が広い(主集計0/6: 0-39%)。

確率的TTS失敗を支持する事実:
- N01 Stdのt1/t2は同一入力(style/tts_input/manuscript sha完全一致)で正常(43.2s/44.0s)。入力が同じでも結果が割れた。
- 破綻の型が2件で異なる(J11 Adv=原稿外文の挿入、N01 Std=原稿全文の2周読み)。共通する系統的な型は無い。
- 他の速度語・減速語ありPrompt(主集計86call、J02/J10/J13/K01/L01/M05/N02等)では、同種の破綻は0件。N02(別文面・速度語'slightly slower'を含む)のStd/Adv計6takeと、N01 Advの3takeは正常。
- 全体の発生率は主集計 2.2%(2/92)・全体1.6%(2/128)。一方、同じ型の破綻が同Promptで再発した例は無い(再発確認データ無し)。
- 同Std 2周読みで見かけ79WPMになったが、聞こえのペース自体は約162WPM(Prompt指示の減速効果は2周でも通常範囲)。

判別不能な点: N01 Stdはt4以降が未生成で、同Promptでの再発率は3takeでは測れない(1/3、Wilson95%=6-79%)。J11 AdvもPromptあたり1takeのみで再発確認不可。

## 6. 追加確認に必要な最小call数と見積(実行しない)

単価: Std実績 JPY約1.07/call(TTS)+ ASR概算約0.22 = 約JPY1.29。Round5実績平均 JPY1.28/call(cost_02.json per_call 1.273)。

| 案 | call | 見積(中央) | 目的 |
|---|---|---|---|
| A: N01 Std Take4〜6 | 3 | 約JPY3.9 | 同一入力での再発有無(1/6超なら入力依存の疑い。ただし3callで発生率の判別力は低い) |
| B: N01 Std Take4〜9 | 6 | 約JPY7.7 | 同上、やや判別力向上(2周読みが0/6なら発生率<約40%上限) |
| C: N01 Std Take4〜6 + J11 Adv Take2〜3 | 5 | 約JPY6.4 | 型の異なる2件の各再発確認 |
| D: 速度語なし Prompt(例H0/K03等)のStd x 6take | 6 | 約JPY7.7 | 速度語の有無で発生率に差があるかの比較(ただし発生率2%前後では6〜12callでは差が出にくい) |

注: 発生率約2%の事象を『起因特定』するには数百callが必要で現実的でない。『N01 Stdで再発するか』の確認なら案A(3call)が最小。価格定数は既存Trial定数流用(新規出典確認なし)。

## evidence
- 集計script: 一時script(scratchpad、repo外)。元データ: er057_output/coffee_tts_style_h_speed_0{2,3,4,5_listen}/**/generation_log_*.jsonl・measurements_*.json・prompts_*.json、er057_output/coffee_v5_pause_01/tts_input_texts.json。
- 全call表: collapse_rate_03.json の calls[]。
