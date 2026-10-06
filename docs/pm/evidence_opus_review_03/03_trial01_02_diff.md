# Evidence packet 03: TRIAL-01 / TRIAL-02 差分整理(OPEN-233 委任_01c、事実のみ。【推測】は明記)

## A. Prompt/schema 逐語(出典: er052_open233_directional_trial_01.py L65-101、trial_02.py L20-40)
ENUM(共通)= AVAILABLE, STOPPED, PAUSED, INCREASED, DECREASED, UNCHANGED, STARTED, ENDED, EXPANDED, NARROWED, NOT_MENTIONED, UNCLEAR

### A-1 Ledger側 prompt(01/02共通。02は t1.ledger_prompt をそのまま import。差分なし)
```
次のfact blockは、ある対象の状態変化・方向性(開始/停止/増減/拡大縮小/撤回復元等)を記述しているか判定せよ。している場合、各事象について対象X(短い名詞句)と『事象後の結果状態』を次の固定分類から1つ選べ: {ENUM}。複数事象があれば各事象を列挙。quoteは原文からの逐語引用必須。

[fact block]
{fact_text}
```
Ledger schema(共通): {has_direction:bool, events:[{subject_x:str, result_state:ENUM, quote:str}]}(strict)

### A-2 記事側 prompt: TRIAL-01(1 subject_xごとに1 call)
```
次の文は対象X『{subject_x}』について『事象後の結果状態』を述べているか。述べていれば次の固定分類から1つ選べ: {ENUM}。述べていなければNOT_MENTIONED、判断できなければUNCLEAR。quoteは文からの逐語引用必須。

[前後文]            (contextがある場合のみ)
{context}

[記事文]
{sentence}
```
schema 01: {result_state:ENUM, quote:str}

### A-3 記事側 prompt: TRIAL-02(1 rowにつき1 call、ラベル一覧から選択)
```
次の記事文は、下の対象のうちどれについて『事象後の結果状態』を述べているか。1つ選べ(どれも述べていなければ selected_subject に NONE と答える)。selected_subject は対象一覧の文字列をそのまま返すこと。選んだ対象の結果状態を次の固定分類から1つ選べ: {ENUM}。判断できなければUNCLEAR。quoteは記事文からの逐語引用必須。

[対象一覧]
- {label1}
- {label2} ...

[前後文]            (contextがある場合のみ)
{context}

[記事文]
{sentence}
```
schema 02: {selected_subject:str, result_state:ENUM, quote:str}(strict、selected_subjectはenumでなくstring)

### A-4 差分(箇条書き、事実)
- Ledger側prompt/schema/model(gpt-6-luna、effort=high)は同一。ただしTRIAL-02はLedgerを再実行(ledger_cache.json)しており、同一promptでもsubject_x文言がサンプルごとに異なる(例 HF-009 rep1「Brent先物の水準」+「Brent先物価格」の3事象、rep2/3「Brent先物の価格水準」の2事象)。
- 記事側: 01=subject_x 1つを名指しで「述べているか」を問う(事象ごとにcall)。02=全labelを並べ「どれについてか」を選ばせ、NONEを許す。
- 02の記事側にはLedger本文・state・quoteは渡さない(01も同様)。渡すのはsubject_xラベルのみ。
- 02は選択subject以外のeventを比較に使わない(総当たり比較廃止)。01は全event比較後worst。
- 02は「NONE」が追加された出力経路。01は事象ごとにNOT_MENTIONED。
- 02にはsubject_xの選択根拠(quote)をLedger側へ照合する処理はない(article quoteは記事文からの引用のみ)。
- 01のcontext/sentence受け渡し・前後文形式は同一。

## B. 規則の差分
| 項目 | TRIAL-01 | TRIAL-02 |
|---|---|---|
| 記事側への対象指定 | Ledger側各subject_xを1つずつ(eventごと1 call) | 全subject_xラベル一覧から1つ選択(row/repごと1 call) |
| 比較対象 | 全event | 選択subjectのeventのみ |
| 項目の集約 | worst(SEVERITY順 SAME<SAME_FAMILY<NOT_MENTIONED<LEDGER_NO_DIRECTION<UNCLEAR<REVERSED) | 同一subject内複数eventは SAME/SAME_FAMILYがあればそれ、なければworst(compare_selected) |
| NONE | なし(NOT_MENTIONED) | NOT_MENTIONED(Ledger側stateなし、compare=NOT_MENTIONED) |
| ラベル外(selected not in labels) | 該当なし | UNCLEAR |
| quote欠落 | compare()でUNCLEAR(共通) | 同(共通compare()) |
| Ledger events空/has_direction=false | LEDGER_NO_DIRECTION | 同(labels空なら記事側callせず) |
| 方向対 REVERSED | AVAILABLE-STOPPED/PAUSED, INCREASED-DECREASED, STARTED-ENDED, EXPANDED-NARROWED | 同(import共通) |
| SAME_FAMILY | PAUSED-STOPPED のみ | 同 |
| UNCLEAR条件 | どちらかがUNCLEAR、ledger=NOT_MENTIONED、quote欠落、非対応の相違(例 STOPPED-ENDED、UNCHANGED vs 他) | 同 |
| article NOT_MENTIONED | NOT_MENTIONED | 同 |

## C. 結果差分(出典: trial_summary_02.md 前回比表、regression_vs_trial01.md、results_same_blind.jsonl / results_merged.jsonl のPython突合。以下id比較はrep0基準、repeat別は明記)
| 項目 | TRIAL-01 | TRIAL-02 |
|---|---|---|
| HC-012(G-01) k/n | 3/3 | 3/3 |
| A5-0(G-02) k/n | 3/3 | 3/3 |
| D61(G-03) k/n | 2/3 | 0/3 |
| gold計 | 8/9 | 6/9 |
| 正常文誤重大(REVERSED誤爆) | 3件 (F-09, F-10, F-19) rate 0.0698 | 0件 |
| UNCLEAR全体 | 14 | 6 |
| 人工反転検出(S-01..S-14, リスト内外含む) | 5/14 | 4/14 |
| low/mid/high 追加円/run | 0.369/0.429/0.76 | 0.34/0.423/0.885 |
| low/mid/high 不要Rewrite/run | 0.232/0.521/2.133 | 0.0/0.0/0.0 |
| 実費 | 01: 63項目x3構成(実費10.35円) | 02: 63項目 2.08円/104 call |
| 合格基準6(新しい重大見逃しなし) | - | 未達: new_misses=[S-06] |

### C-2 項目id別(01 rep0 -> 02 rep0。repeat=3のgoldはrepeat列挙)
- 01検出(REVERSED)->02見逃し: S-06(人工反転、outside_event_list=True。01 REVERSED、02 SAME)、G-03/D61(repeat: 01=NOT,REV,REV -> 02=NOT,NOT,NOT。02は3/3でselected=NONE)。
- 01見逃し->02検出(REVERSED): なし。
- 01誤爆(REVERSED on faithful)->02解消: F-09, F-10, F-19(02は全てSAME/SAME_FAMILY)。
- 01検出かつ02も検出: G-01, G-02(3/3)、S-07, S-10, S-12, S-13。
- 両方未検出の人工反転: S-01,S-02,S-03,S-04,S-05,S-08,S-09,S-11(LEDGER_NO_DIRECTION),S-14(01 S-01/02/04はUNCLEAR、02はNOT_MENTIONED=selected NONE)。
- その他rep0変化: UNCLEAR->NOT_MENTIONED: F-01,F-02,F-04,G-04,S-01,S-02,S-04。UNCLEAR->SAME: F-12,F-20。NOT_MENTIONED->SAME: F-14,F-21,G-05。NOT_MENTIONED->UNCLEAR: N-02(新規UNCLEAR)。合計rep0変化17項目+G-03のrepeat変化。
- G-05(曖昧gold): 01 repeat=NOT,REVERSED,NOT(1回REVERSED) -> 02=SAME,NOT,SAME(REVERSEDなし)。
- 02のUNCLEAR残: F-05, F-07, F-11, F-13(いずれも faithful の期待SAME、01もUNCLEAR)、G-06、N-02、G-04のrep2/3。
- 項目数: 01と02は同一63項目(ID一致)。

## D. ユーザー指定6観点別(id、01/02結果、修正案で変わりうる箇所は事実ベース)
| 観点 | 該当id | 01 -> 02 結果 | 事実メモ(評価はOpus) |
|---|---|---|---|
| 同義表現 | F-05/G-05(returned to high level vs 水準), F-11/F-12/F-13(drop/replaced vs 償還料STOPPED/ENDED), S-14(drop vs 価格) | F-05 UNCL->UNCL, F-12 UNCL->SAME, F-11/13 UNCL->UNCL, S-14 NOT->NOT | F-11はSTOPPED(Ledger)対ENDED(article)でUNCLEAR(compareの非対応ペア)。Ledger側label自体が rep間で変動(償還料: STOPPED/ENDED) |
| 主語省略 | G-03/D61 "oil prices fell", S-14 "The drop was...", N-02 "The problem was..." | G-03 NOT/REV/REV -> NONE x3, S-14 NOT->NOT, N-02 NOT->UNCL | D61: labelsに「Brent先物の水準」「価格水準」「価格」が含まれていてもNONE(02は3/3)。ラベルは名詞句のみでLedger quote/stateを持たない |
| 比較表現 | S-03 "did not fall across the board", F-05 "might start to fall ... returned" | S-03 NOT->NOT(NONE), F-05 UNCL->UNCL | 該当2〜3項目のみ。比較・否定を含む文のテスト数は少ない |
| 方向表現(increase/decrease) | F-09/F-10(lost some of their gains), S-06(reinstated ... lost some of their gains), S-07, G-03, G-05, S-14 | F-09/10 REVERSED->SAME, S-06 REVERSED->SAME, S-07 REVERSED->REVERSED, G-03 2/3->0/3 | S-06とF-09は文差分が「withdrawn」→「reinstated」のみ(ledger fact同一HF-009)。02はどちらも選択=上げ幅(DECREASED vs DECREASED=SAME) |
| 一つのFactに複数事象 | HF-009(上げ幅DECREASED+水準INCREASED、rep1は価格INCREASED追加の3事象), MUSE-HC-012(テストSTARTED+機能PAUSED/STOPPED), HF-007 rep2(STARTEDの置換先事象を追加) | 01は全event比較でF-09/10/19誤爆。02は選択1事象のみ比較で誤爆解消。S-06は選択事象違いで見逃し | 02はrow内で1事象しか比較しない(2事象を述べる文: F-05/G-05でも1つ) |
| 記事側の言い換え | S-01..S-05(HF-009、置換語=事象リスト外)、S-08/S-09(HF-007) | S-01/02/04 UNCL->NOT, S-03/05 NOT->NOT, S-08/09 NOT->NOT | outside_event_list項目(S-01..S-06等)は別集計。02で人工反転4/14検出(リスト外の検出は02でS-06喪失) |

### D-2 「修正案(実体名付与+意味上の部分一致)」で変わりうる箇所(事実のみ)
- 前提事実: 現行02は記事側にラベル文字列(例「Brent先物の水準」)のみ渡し、文字列完全一致(selected in labels)で選択を受理する。意味上の部分一致の受理はまだない。実体名(例 Brent/Metaテスト)を付与するかの実装も未実施。
- 影響しうるid(【推測】、実行未検証): G-03 D61(NONEx3、ラベルに「水準」「価格」が存在)、S-06(選択が事象違い)、S-01/S-02/S-04(NONEだがLedger側に「水準」INCREASEDが存在)、F-05/F-07(selected=Brent先物価格で UNCLEAR)。
- 逆に誤爆増加の恐れが検証可能な箇所(【推測】): F-09/F-10/F-19(現在SAME)、N-02(selected=機能 -> UNCLEAR)。

## E. 全体構造: Ledger側抽出 -> 記事側blind選択 -> 機械比較
| 段 | 渡す | 渡さない | 失われうる情報/偏り(事実・観察) |
|---|---|---|---|
| Ledger側抽出 | fact blockのみ(記事文なし) | 記事文、記事側結果 | 同一promptでも抽出結果が揺れる: HF-009のeventsはrep1=3件、rep2/3=2件、subject_x名もrep間で変動。HF-007のstateもrep間でSTOPPED/ENDED。Ledger側にhas_direction=falseの項目(F-16/17/18, ND-01..03, S-11)は記事側未実行 -> LEDGER_NO_DIRECTION |
| 記事側blind選択 | subject_xラベル一覧+記事文+前後文 | Ledger本文/state/quote、Ledger側の他情報 | ラベルは短い名詞句のみで同義・曖昧(価格/水準/上げ幅)。D61では3/3NONE。選択は1つのみ。NONEの根拠(選択理由)は出力されない |
| 選択 | selected_subjectは文字列自由(schema enumではない) | - | ラベル外文字列はUNCLEAR。完全一致のみ受理。事前にラベル順(出現順固定)でbias可能性(未検証) |
| 機械比較 | 選択subjectのevent、両側quote | 他subjectのevent | 同一subject内の複数eventはSAME優先 -> SAMEが偶然選ばれる経路あり(S-06 SAME)。NONE=NOT_MENTIONED=通過(設計doc §8の「未言及=通過」と整合) |

### E-2 設計doc(docs/pm/design_open233_directional_misread_safety_01.md §8 Opus Part 2反映 L316-329、§14 L486)との整合
- 整合: Ledger側=factごと事前抽出・記事文脈なし(L319)。枠の値=enum固定(L320)。記事側=blind(L323)。Python比較・未言及=通過(L325)。事象リスト化(L321)。
- 不整合/未実装(事実): §8「どの事象かを引用付きで選ばせる」(L324)に対し、02の記事側出力のselected_subjectは文字列、quoteは記事文からの引用でLedger側quoteとの照合なし。§8「2モデル一致、割れたfactはQUALITY」(L321)は02に実装なし(Ledgerは1 model、3 rep)。「1回retry」「解消判定=再抽出+Python再比較」(L316, L326)はTrial範囲外。
- 設計docの「記事側: 対象Xだけ渡し」と02は一致するが、設計docは全事象を見せるか選ばせるかを明示していない(L323では「どの事象かを選ばせる」)。

## F. Opusが確認すべきファイル一覧
- er052_open233_directional_trial_01.py L1-60(ENUM/compare/PAIRS)、L65-101(schema/prompt)、L231-273(process_row)
- er052_open233_directional_trial_02.py L20-75(schema/prompt/compare_selected)、L100-125(process_row)
- er052_output/open233_directional_misread_trial_02/trial_summary_02.md、regression_vs_trial01.md、ledger_truth_02.md、testset_02.json、run/results_merged.jsonl、run/ledger_cache.json
- er052_output/open233_directional_misread_trial_01/trial_summary_01.md、run_same_blind/results_same_blind.jsonl
- docs/pm/design_open233_directional_misread_safety_01.md §8 L316-329、§14 L486-
- 注: regression_vs_trial01.md/trial_summary_02.mdは日本語がcp932と思われる文字化けあり(UTF-8表示でない箇所)。本packetの数値はjson/jsonlをPythonで再突合した値。
