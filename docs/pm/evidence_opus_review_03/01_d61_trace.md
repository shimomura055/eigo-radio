# Evidence packet 01: D61(G-03)見逃しtrace (OPEN-233-DIRECTIONAL-MISREAD-OPUS-REVIEW-03 委任_01a, 2026-10-06, 事実のみ。仮説は【推測】)
パス略記: T2=`er052_output/open233_directional_misread_trial_02/`、T1=`er052_output/open233_directional_misread_trial_01/`

## A. G-03定義 (T2/testset_02.json items[id=G-03])
- article_sentence: "After the plan was withdrawn, oil prices fell."
- article_context: **フィールド自体なし**(`row.get("article_context","")`=空→前後文はpromptに入っていない。`er052_open233_directional_trial_02.py:96`)
- fact_id=HF-009 / role=gold_reversal / origin="委任_60 重大期待の明確な方向反転(比較系)" / label="真の反転"
- expected_ledger_state=UNCHANGED / expected_article_state=DECREASED / expected_compare=REVERSED / acceptable_compare=[REVERSED,UNCLEAR]
- **expected_event_subject="水準"** / trial02_reason="prices fell=事象「水準」INCREASED(復帰)の逆。上げ幅縮小と読む余地はUNCLEARで許容"
- note: "Ledger=UNCHANGED(高水準へ復帰)に対しDECREASEDは固定ゴール外。goldは重大扱い"
- T1/testset_01.json G-03との差分: T2のみ追加={expected_event_subject, outside_event_list=False, legacy_expected_compare, legacy_acceptable_compare, trial02_reason}。article_sentence/expected_*はT1と同一。

## B. Ledger HF-009
- `er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt:58`:
  "[VERIFIED] HF-009: Yahoo Financeは、7月14日の撤回・投資案件への置換発表後、Brent先物が一時的に上げ幅を縮小したものの、ほどなく発表前に近い高い水準へ戻ったと報じた。記事掲載時点ではBrent先物は約2.6％高で、1バレル85ドルを上回っていた。"
- T2/ledger_truth_02.json facts.HF-009.events:
  - event_key=上げ幅 aliases=[上げ幅,上昇幅,gains,Brent先物の上げ幅] result_state=DECREASED(許容DECREASED/NARROWED) quote="一時的に上げ幅を縮小した"
  - event_key=水準 aliases=[水準,高い水準,価格水準,price level,Brent先物] result_state=INCREASED(許容INCREASED/UNCHANGED) quote="ほどなく発表前に近い高い水準へ戻った" note="実質は発表前と同程度でUNCHANGED許容"

## C. Ledger側抽出 (T2/run/ledger_cache.json HF-009)
| rep | subject_x / state / quote |
|---|---|
| rep1 | Brent先物の上げ幅/DECREASED/"一時的に上げ幅を縮小した" ; Brent先物の水準/INCREASED/"ほどなく発表前に近い高い水準へ戻った" ; Brent先物価格/INCREASED/"約2.6％高で" |
| rep2 | Brent先物の上げ幅/DECREASED/"Brent先物が一時的に上げ幅を縮小した" ; Brent先物の価格水準/INCREASED/"ほどなく発表前に近い高い水準へ戻った" |
| rep3 | rep2と同一 |
- T1(T1/run_same_blind/results_same_blind.jsonl G-03 repeat_events): rep1=[Brent先物の上げ幅 DECREASED, Brent先物の水準 INCREASED]; rep2=[Brent先物 DECREASED, Brent先物 INCREASED](**同一ラベル"Brent先物"が2event**); rep3=[Brent先物の上げ幅 DECREASED, Brent先物の水準 INCREASED]。
- 差分: T2のLedgerラベルは全rep「Brent先物の〜」で修飾語付き。T1 rep2のみ汎用"Brent先物"。T2 rep1に"Brent先物価格"(約2.6％高)が追加。

## D. 記事側入力と応答 (T2)
prompt本文(`er052_open233_directional_trial_02.py:28-39` article_prompt、逐語。ENUM_TXTは別定義):
> 次の記事文は、下の対象のうちどれについて『事象後の結果状態』を述べているか。1つ選べ(どれも述べていなければ selected_subject に NONE と答える)。selected_subject は対象一覧の文字列をそのまま返すこと。選んだ対象の結果状態を次の固定分類から1つ選べ: {ENUM_TXT}。判断できなければUNCLEAR。quoteは記事文からの逐語引用必須。
> [対象一覧]\n- {label}...\n\n[前後文](contextありの場合のみ)\n[記事文]\n{sentence}
- Ledgerのstate/quote/本文は記事側に渡さない(blind)。
G-03実入力・応答 (T2/run/results_merged.jsonl id=G-03):
| rep | 渡ったラベル一覧 | selected_subject | article_state | article_quote |
|---|---|---|---|---|
| 1 | Brent先物の上げ幅 / Brent先物の水準 / Brent先物価格 | NONE | NOT_MENTIONED | "After the plan was withdrawn, oil prices fell." |
| 2 | Brent先物の上げ幅 / Brent先物の価格水準 | NONE | NOT_MENTIONED | "oil prices fell." |
| 3 | Brent先物の上げ幅 / Brent先物の価格水準 | NONE | NOT_MENTIONED | "After the plan was withdrawn, oil prices fell." |
- call_log(`T2/run/call_log_shard_*of3.jsonl`)は usage/jpy/prompt_chars/errorのみでraw応答・prompt全文なし(逐語取得不可)。「NONE」でもquoteには記事文が引用されている点は事実。
- 比較ロジック: selected==NONE→compare=NOT_MENTIONED固定(`:56-57`)。NOT_MENTIONEDは見逃し扱い。
## E. HF-009由来の他項目 (T2/run/results_merged.jsonl、selected/article_state。repeat=1項目は1件のみ)
| id | 記事文(要旨) | 期待subject | 選択結果 |
|---|---|---|---|
| F-09 | "Brent crude oil futures briefly lost some of their gains." | 上げ幅 | 3/3 Brent先物の上げ幅/DECREASED 成功 |
| F-10 | "Brent crude oil futures briefly gave up some of their gains." | 上げ幅 | 3/3 成功 |
| S-06 | "...Brent crude oil futures briefly lost some of their gains."(reinstated) | 上げ幅 | 1/1 成功(SAME) |
| S-07 | "...Brent crude oil futures briefly added some of their gains." | 上げ幅 | 1/1 Brent先物の上げ幅/INCREASED=REVERSED検出 |
| G-05 | "Just after the charge plan disappeared, prices began to fall. Soon, however, they returned to a high level." | 上げ幅\|水準 | rep1,3=Brent先物(の)(価格)水準/INCREASED(SAME), rep2=NONE (2/3選択) |
| G-04 | "...the events driving oil prices—and the prices themselves—quickly returned." | 水準 | rep1=NONE, rep2,3=Brent先物の価格水準/UNCLEAR (2/3選択) |
| F-05 | "...they soon returned to a high level close to where they had been before..." | 上げ幅\|水準 | Brent先物価格/UNCHANGED (選択) |
| F-07 | "...the fee plan left the stage, but the price did not leave with it." | 水準 | Brent先物価格/UNCHANGED (選択) |
| F-01,02,03,04,06 | "oil prices stayed high..."/"did not fall across the board"/"prices themselves quickly returned"等 | 水準(F-04は上げ幅\|水準) | NONE(各1/1) |
| S-01〜05 | F-01〜07の反転版("oil prices"/"prices"主語) | 水準 | NONE(各1/1) |
| **G-03** | "After the plan was withdrawn, oil prices fell." | 水準 | **3/3 NONE** |
- 成功例(selected≠NONE)の共通点(事実): 文中に"Brent crude oil futures"+"gains"、または"returned to a high level"/"the price"で選択。失敗例の主語は"oil prices"/"prices"。ただしF-05/F-07/G-04/G-05は"prices/the price"主語で選択できた回もあり、主語語だけでは分離しない。
- 同一ラベル「Brent先物の水準/価格水準」: G-05(rep1,3)では選択・G-03(rep1〜3)では未選択。
- T1 G-03の記事側応答(subject_x指定方式、event毎に記事側判定): rep1=上げ幅 NOT_MENTIONED/水準 NOT_MENTIONED(quote "After the plan was withdrawn, oil prices fell." / "oil prices fell"); rep2=Brent先物 DECREASED(quote "oil prices fell")x2 → SAME+REVERSED; rep3=上げ幅 DECREASED(SAME)/水準 DECREASED(REVERSED)。T1 repeat_compares=[NOT_MENTIONED,REVERSED,REVERSED]。T1ではrep2/3で記事側が"oil prices fell"を「水準」ラベルに対しDECREASEDと判断できた。
- T1とT2の差(事実): T1=Ledger eventごとに「この記事文はこの事象を述べているか」を個別判定(選択肢なし)。T2=ラベル一覧から1つ選択 or NONE。T2はrep1/2/3全部NONE(T1は1/3のみ未検出)。

## F. 事実から言えること/言えないこと
(i) 仮説「ラベル抽象性が主因」を支持する事実
- G-03は全labelが「Brent先物の〜」で、記事文は"Brent"を含まず"oil prices"のみ。"Brent crude oil futures ... gains"の文(F-09/F-10/S-06/S-07)は上げ幅ラベルへ選択成功(8/8 rep)。
- 「水準」系ラベルが期待subjectの項目はF-01〜04,06,S-01〜05でNONE多数(抽象的な「水準」と"oil prices stayed high"等が対応付かなかった可能性と整合)。
(ii) 仮説に反する/弱める事実
- 同一ラベル(Brent先物の水準/価格水準)がG-05では選択された(2/3)。G-04も2/3選択。主語"prices"でも選択される。
- G-03のrep1〜3でラベル表記が違う(価格/価格水準)のに3/3 NONE。rep1には汎用寄りの"Brent先物価格"もあったがNONE。
- T1ではほぼ同一内容のラベル("Brent先物の水準"等)に対しrep2/3で"oil prices fell"をDECREASED判定できた(ラベル抽象性だけなら説明しにくい差)。
- NONE応答でもquoteは"oil prices fell."を逐語引用(文は認識)。
(iii) 代替仮説候補【推測】(いずれも未検証)
1. 【推測】選択promptの「どれも述べていなければNONE」+『事象後の結果状態を述べているか』が、"prices fell"(単独の下落)を「復帰後水準」でも「上げ幅縮小」でもないと判断させ、NONE倒しになる(T1=選択肢なし判定で検出、T2=NONE選択肢ありで消失した差と整合)。
2. 【推測】G-03文は"Brent"/"futures"/"gains"/"level"のいずれも含まず、「oil prices fell」は上げ幅・水準のどちらとも直接対応しない比較表現(下落)。Ledger側の2事象が「縮小」「復帰」でありPython側の語対応では中間。
3. 【推測】前後文(article_context)なし。F-系も同様なので、前後文がないため"After the plan was withdrawn"の事象(撤回)と結びつかない可能性。
4. 【推測】T1のrep2/3の検出は、ラベルが汎用"Brent先物"(rep2)や個別判定方式によるもので、T2のラベル詳細化・方式変更により却って未検出化した可能性(T1 rep3は"水準"ラベルでも検出済のため弱い)。
5. 【推測】testsetのexpected_event_subject="水準"はT2で追加された設定で、記事文自体は両事象のどちらとも読める。goldとしての正解subject設定の妥当性(acceptable_compareはUNCLEAR許容)。
6. 【推測】3 rep全NONEは確率的なばらつきだけではなく、このprompt×この文の決定論的傾向(同条件G-05は1/3NONE)。
- 言えないこと: 主因の特定。call_log/raw応答が無いため、モデルがなぜNONEを選んだかの理由は取得不可。

## G. Opusが確認すべきファイル一覧
- `er052_open233_directional_trial_02.py` L20-39(article_prompt/NONE)、L52-67(compare_selected NONE→NOT_MENTIONED)、L95-103(article_select・context)、L105-129(process_row)
- `er052_output/open233_directional_misread_trial_02/testset_02.json` items[id=G-03/F-*/S-*]、`ledger_truth_02.json` facts.HF-009、`run/ledger_cache.json` HF-009、`run/results_merged.jsonl` id=G-03/G-04/G-05/F-05/F-07
- `er052_output/open233_directional_misread_trial_01/run_same_blind/results_same_blind.jsonl` id=G-03(repeat_events)、`testset_01.json` G-03
- `er019_output/family_x_refresh_e2e_01/hormuz/run_03/ledger/verified_fact_ledger.txt` L58
- 未取得: `run/call_log_shard_*of3.jsonl`はraw応答なし

