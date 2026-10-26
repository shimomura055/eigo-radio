# COMPARISON_02 (KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02 委任_01、2026-10-26)

数値の出典: `trial_runs_02.json`(今回6 run: 件数・call数・費用はusage log)、`own_rubric_02.json`(自ルーブリックY/B/N=前回DESIGN_01 §7を変更せず適用。judge前に確定)、`judge/judge_*.json`(gpt-6.1-sol。単語のみ今回新規、フレーズは前回judge再利用)、`gate_results_02.json`、前回`trial_runs_01.json`(P7+W3 r1・現行)。候補全文=`RESULT_02.md`。表は`make_comparison_02.py`が`trial_runs_02.json`から出力した値(A〜G)。
比較条件: 今回のP7はAPI 0(前回r1のP7返答をmessage sha256一致を確認して再利用)。フレーズ側はP7返答が同一のため、差は後段(canonicalization等のLLM再実行)の揺れだけ。各level 1回のみ(再現性の追加実行はしていない)。

## 0. 先に結論的な事実(数値は下表)
1. 5件要求に対しW5は**6/6 levelとも5件を返した**(前回W3は3件要求に12/12回とも3件)。最終は、Gateで`detour`(AI島×2)・`interferes`(猿の手Adv)が`duplicate_of_top3`で除外され4件の3 levelを除き5件(UK×2・猿の手Std)。
2. **単語は18→27件(+9)**。自Yは14→16(+2)に留まり、増分の大半は自B(基本寄り)で、自B 3→10(+7)。実際に追加された11語(UK Stdの`audience`・UK Advの`masterpiece`は脱落、差し引き+9)の内訳は Y 3(`nationwide`・`drag`・`snatch`)/B 8(`Strategy`・`technique`・`campaign`・`entertainment`・`carriage`×2・`recommendations`・`funeral`)。N は 前回と同じ`performance` 1件のみ。
3. ③④適合: 適合 14→16、境界(基本寄り)3→10、不適合(易しい語)1→1。**単語に占める『基本寄り+易しい』の割合は 4/18(22%) → 11/27(41%) に上昇**。自N(明確に易しい)の割合は 1/18(5.6%)→1/27(3.7%)で低下(絶対数は同じ`performance`1件)。
4. 前回挙がった易語: `performance`=残存(AI Adv、W5生返答の2位。自N)、`discovery`=残存(AI Std、`discoveries`として生返答5位、canonicalizationで`discovery`)、`automatically`=残存(UK Adv、生返答3位)、`Strategy`/`technique`=**W5の生返答で1位**(AI Std/Adv。前回はr2のみ、r1には無し)、`carriage`=UK Std/Advの両方で5位(前回はr2のUK Stdのみ)、`audience`=不出現(UK Std)、`responsibility`=不出現(前回もr2のみ)。③④が働いたと言えるのは`audience`の脱落程度で、**『易語を除く』という意図は部分的にしか機能していない**(下記§3)。
5. フレーズ側はP7同一入力のため品質は不変(自Y 19→20、自N 1→1)。`given written permission`(UK Std)・`pulling free`(猿の手Std)・`pulled free`/`accept no responsibility`(猿の手Adv)の4件が前回r1では出なかった形で最終に残った(前回r1ではcanonicalizationで除外されていた同系の句が、今回のLLM再実行で通過。LLMの揺れ)。
6. judge(gpt-6.1-sol)は評価した29語(前回W3 r1+今回W5の和集合)を**全て good/Y** とした(`performance`・`campaign`・`entertainment`・`recommendations`・`carriage`含む)。易語判別に使えない(自ルーブリックを主、judgeを副とする前回方針のとおり)。

## A. レベル別(件数・Y/B/N)
| level | 方式 | フレーズ | 単語 | 計 | フレーズ自Y/B/N | 単語自Y/B/N | 単語judge Y/B/N | ③④適合/境界/不適合 | 費用¥ | 秒 |
|---|---|---|---|---|---|---|---|---|---|---|
| ai_island_temple:a2 | 現行 | 5 | 0 | 5 | 4/1/0 | 0/0/0 | 0/0/0 | 0/0/0 | — | — |
| ai_island_temple:a2 | 前回P7+W3 r1 | 6 | 3 | 9 | 5/1/0 | 2/1/0 | 3/0/0 | 2/1/0 | 1.447 | 133.4 |
| ai_island_temple:a2 | 今回P7+W5 | 6 | 4 | 10 | 5/1/0 | 2/2/0 | 4/0/0 | 2/2/0 | 1.509 | 152.6 |
| ai_island_temple:b1b | 現行 | 7 | 0 | 7 | 5/1/1 | 0/0/0 | 0/0/0 | 0/0/0 | — | — |
| ai_island_temple:b1b | 前回P7+W3 r1 | 5 | 3 | 8 | 3/2/0 | 2/0/1 | 3/0/0 | 2/0/1 | 1.495 | 138.8 |
| ai_island_temple:b1b | 今回P7+W5 | 5 | 4 | 9 | 3/2/0 | 2/1/1 | 4/0/0 | 2/1/1 | 1.74 | 181.6 |
| uk_train_speaker_playback:a2 | 現行 | 6 | 0 | 6 | 3/1/2 | 0/0/0 | 0/0/0 | 0/0/0 | — | — |
| uk_train_speaker_playback:a2 | 前回P7+W3 r1 | 3 | 3 | 6 | 2/1/0 | 2/1/0 | 3/0/0 | 2/1/0 | 1.773 | 159.8 |
| uk_train_speaker_playback:a2 | 今回P7+W5 | 4 | 5 | 9 | 2/2/0 | 2/3/0 | 5/0/0 | 2/3/0 | 1.646 | 156.2 |
| uk_train_speaker_playback:b1b | 現行 | 8 | 0 | 8 | 5/1/2 | 0/0/0 | 0/0/0 | 0/0/0 | — | — |
| uk_train_speaker_playback:b1b | 前回P7+W3 r1 | 6 | 3 | 9 | 5/1/0 | 2/1/0 | 3/0/0 | 2/1/0 | 1.744 | 170.1 |
| uk_train_speaker_playback:b1b | 今回P7+W5 | 6 | 5 | 11 | 5/1/0 | 2/3/0 | 5/0/0 | 2/3/0 | 1.622 | 172.8 |
| monkeys_paw:a2 | 現行 | 4 | 1 | 5 | 2/1/1 | 0/0/1 | 0/0/0 | 1/0/0 | — | — |
| monkeys_paw:a2 | 前回P7+W3 r1 | 5 | 3 | 8 | 4/1/0 | 3/0/0 | 3/0/0 | 3/0/0 | 2.106 | 212.1 |
| monkeys_paw:a2 | 今回P7+W5 | 6 | 5 | 11 | 4/2/0 | 4/1/0 | 5/0/0 | 4/1/0 | 1.92 | 186.3 |
| monkeys_paw:b1b | 現行 | 3 | 4 | 7 | 1/2/0 | 3/0/1 | 2/0/0 | 4/0/0 | — | — |
| monkeys_paw:b1b | 前回P7+W3 r1 | 5 | 3 | 8 | 0/4/1 | 3/0/0 | 3/0/0 | 3/0/0 | 2.406 | 251.4 |
| monkeys_paw:b1b | 今回P7+W5 | 7 | 4 | 11 | 1/5/1 | 4/0/0 | 4/0/0 | 4/0/0 | 2.138 | 220.2 |

## B. 総括(6 level合計)
| 項目 | 現行 | 前回P7+W3 r1 | 今回P7+W5 |
|---|---|---|---|
| フレーズ件数 | 33 | 30 | 34 |
| 単語件数 | 5 | 18 | 27 |
| 総件数 | 38 | 48 | 61 |
| フレーズ 自Y | 20 | 19 | 20 |
| フレーズ 自B | 7 | 10 | 13 |
| フレーズ 自N | 6 | 1 | 1 |
| 単語 自Y | 3 | 14 | 16 |
| 単語 自B | 0 | 3 | 10 |
| 単語 自N | 2 | 1 | 1 |
| 単語 judge Y | 2 | 18 | 27 |
| 単語 judge N | 0 | 0 | 0 |
| 単語 ③④適合 | 5 | 14 | 16 |
| 単語 ③④境界(基本寄り) | 0 | 3 | 10 |
| 単語 ③④不適合(易しい語) | 0 | 1 | 1 |
単語Y(自)≥3件のlevel数: 現行 1 / W3 2 / W5 2
単語Y(自)≥1件のlevel数: 現行 1 / W3 6 / W5 6
自N(単語)割合 W3 1/18 W5 1/27; 易語(境界+不適合)割合 W3 4/18 W5 11/27; 自Y割合 W3 14/18 W5 16/27
全体(フレーズ+単語)自Y 現行/W3/W5: [23, 33, 36]  自N: [8, 2, 2]  総件数: [38, 48, 61]

## C. 単語側 W3 r1 vs W5(level別・順位順)
- ai_island_temple:a2: W3 r1 = [('obstacle', 'Y', '適合'), ('separately', 'Y', '適合'), ('discovery', 'B', '境界')]
    W5 = [('Strategy', 'B', '境界'), ('obstacle', 'Y', '適合'), ('separately', 'Y', '適合'), ('discovery', 'B', '境界')]
    W5返答(生) = ['strategy', 'obstacle', 'separately', 'detour', 'discoveries']  / 返答→最終: 5→4
- ai_island_temple:b1b: W3 r1 = [('performance', 'N', '不適合'), ('exploration', 'Y', '適合'), ('overlook', 'Y', '適合')]
    W5 = [('technique', 'B', '境界'), ('performance', 'N', '不適合'), ('overlook', 'Y', '適合'), ('exploration', 'Y', '適合')]
    W5返答(生) = ['technique', 'performance', 'overlook', 'exploration', 'detour']  / 返答→最終: 5→4
- uk_train_speaker_playback:a2: W3 r1 = [('exception', 'Y', '適合'), ('masterpiece', 'Y', '適合'), ('audience', 'B', '境界')]
    W5 = [('exception', 'Y', '適合'), ('campaign', 'B', '境界'), ('entertainment', 'B', '境界'), ('masterpiece', 'Y', '適合'), ('carriage', 'B', '境界')]
    W5返答(生) = ['exception', 'campaign', 'entertainment', 'masterpiece', 'carriage']  / 返答→最終: 5→5
- uk_train_speaker_playback:b1b: W3 r1 = [('Uninvited', 'Y', '適合'), ('automatically', 'B', '境界'), ('masterpiece', 'Y', '適合')]
    W5 = [('Uninvited', 'Y', '適合'), ('nationwide', 'Y', '適合'), ('automatically', 'B', '境界'), ('recommendations', 'B', '境界'), ('carriage', 'B', '境界')]
    W5返答(生) = ['uninvited', 'nationwide', 'automatically', 'recommendations', 'carriage']  / 返答→最終: 5→5
- monkeys_paw:a2: W3 r1 = [('fate', 'Y', '適合'), ('twist', 'Y', '適合'), ('scrape', 'Y', '適合')]
    W5 = [('fate', 'Y', '適合'), ('funeral', 'B', '境界'), ('scrape', 'Y', '適合'), ('twist', 'Y', '適合'), ('drag', 'Y', '適合')]
    W5返答(生) = ['fate', 'funeral', 'scraped', 'twisted', 'dragged']  / 返答→最終: 5→5
- monkeys_paw:b1b: W3 r1 = [('compensation', 'Y', '適合'), ('deserted', 'Y', '適合'), ('burial', 'Y', '適合')]
    W5 = [('compensation', 'Y', '適合'), ('snatch', 'Y', '適合'), ('deserted', 'Y', '適合'), ('burial', 'Y', '適合')]
    W5返答(生) = ['compensation', 'interferes', 'snatched', 'deserted', 'burial']  / 返答→最終: 5→4

## D. 前回易語の扱い(W5での出現)
- performance: 前回W3(r1+r2)出現=[('ai_island_temple__b1b__p7w3__r1', 'performance', 6), ('ai_island_temple__b1b__p7w3__r2', 'performance', 8)] / W5最終出現=[('ai_island_temple:b1b', 'performance', 7, 'N', '不適合')] / W5生返答内順位=[('ai_island_temple:b1b', 2)]
- audience: 前回W3(r1+r2)出現=[('uk_train_speaker_playback__a2__p7w3__r1', 'audience', 6)] / W5最終出現=[] / W5生返答内順位=[]
- responsibility: 前回W3(r1+r2)出現=[('monkeys_paw__b1b__p7w3__r2', 'responsibility', 5)] / W5最終出現=[] / W5生返答内順位=[]
- discovery: 前回W3(r1+r2)出現=[('ai_island_temple__a2__p7w3__r1', 'discovery', 9)] / W5最終出現=[('ai_island_temple:a2', 'discovery', 10, 'B', '境界')] / W5生返答内順位=[]
- strategy: 前回W3(r1+r2)出現=[('ai_island_temple__a2__p7w3__r2', 'Strategy', 6)] / W5最終出現=[('ai_island_temple:a2', 'Strategy', 7, 'B', '境界')] / W5生返答内順位=[('ai_island_temple:a2', 1)]
- technique: 前回W3(r1+r2)出現=[('ai_island_temple__b1b__p7w3__r2', 'technique', 7)] / W5最終出現=[('ai_island_temple:b1b', 'technique', 6, 'B', '境界')] / W5生返答内順位=[('ai_island_temple:b1b', 1)]
- carriage: 前回W3(r1+r2)出現=[('uk_train_speaker_playback__a2__p7w3__r2', 'carriage', 6)] / W5最終出現=[('uk_train_speaker_playback:a2', 'carriage', 9, 'B', '境界'), ('uk_train_speaker_playback:b1b', 'carriage', 11, 'B', '境界')] / W5生返答内順位=[('uk_train_speaker_playback:a2', 5), ('uk_train_speaker_playback:b1b', 5)]
- automatically: 前回W3(r1+r2)出現=[('uk_train_speaker_playback__b1b__p7w3__r1', 'automatically', 8), ('uk_train_speaker_playback__b1b__p7w3__r2', 'automatically', 8)] / W5最終出現=[('uk_train_speaker_playback:b1b', 'automatically', 9, 'B', '境界')] / W5生返答内順位=[('uk_train_speaker_playback:b1b', 3)]

## E. フレーズ側 W3 r1 vs W5(同一P7返答。差はcanonicalization等の再実行のみ)
- ai_island_temple:a2: W3 r1=['worth paying attention to', 'carry over', 'a useful card to play', 'take a detour', 'make a difference', 'one step ahead']
    W5    =['worth paying attention to', 'carry over', 'a useful card to play', 'take a detour', 'make a difference', 'one step ahead']
    差: -[] +[]
- ai_island_temple:b1b: W3 r1=['carry over', 'a useful card to play', 'call on', 'look at separately', 'take a detour']
    W5    =['carry over', 'a useful card to play', 'call on', 'look at separately', 'take a detour']
    差: -[] +[]
- uk_train_speaker_playback:a2: W3 r1=['draw a line', 'sound no one asked for', "reach for one's wallet"]
    W5    =['draw a line', 'sound no one asked for', 'given written permission', "reach for one's wallet"]
    差: -[] +['given written permission']
- uk_train_speaker_playback:b1b: W3 r1=['draw a line', 'blanket ban', 'due to be shared', "reach for one's wallet", 'written permission', 'face a fine']
    W5    =['draw a line', 'blanket ban', 'due to be shared', "reach for one's wallet", 'written permission', 'face a fine']
    差: -[] +[]
- monkeys_paw:a2: W3 r1=['back to life', 'to blame', 'take hold of', 'break the silence', 'rise into the night']
    W5    =['back to life', 'to blame', 'take hold of', 'pulling free', 'break the silence', 'rise into the night']
    差: -[] +['pulling free']
- monkeys_paw:b1b: W3 r1=['pay off the house', 'interfere with fate', 'caught in the machinery', 'wail of loss', "shake one's husband awake"]
    W5    =['accept no responsibility', 'pay off the house', 'interfere with fate', 'pulled free', 'caught in the machinery', 'wail of loss', "shake one's husband awake"]
    差: -[] +['accept no responsibility', 'pulled free']

## F. Gate除外(全件)
- ai_island_temple:a2: [call2] detour stage=duplicate_of_top3 ['前記の選定済み表現と同一または包含関係(重複)']
- ai_island_temple:b1b: [call2] detour stage=duplicate_of_top3 ['前記の選定済み表現と同一または包含関係(重複)']
- monkeys_paw:b1b: [call2] interferes stage=duplicate_of_top3 ['前記の選定済み表現と同一または包含関係(重複)']

## G. 費用・時間
今回run: 30 call ¥10.575 (平均/level ¥1.762, 5.0 call)  judge: 6 call ¥5.73
前回W3 r1 6 run: 36 call ¥10.971 (平均/level ¥1.829, 6.0 call)
elapsed 今回平均 178.3秒 / 前回r1平均 177.6秒
RQA: {'ai_island_temple:a2': 'REDUNDANCY_PASS', 'ai_island_temple:b1b': 'REDUNDANCY_PASS', 'uk_train_speaker_playback:a2': 'REDUNDANCY_PASS', 'uk_train_speaker_playback:b1b': 'REDUNDANCY_PASS', 'monkeys_paw:a2': 'REDUNDANCY_PASS', 'monkeys_paw:b1b': 'REDUNDANCY_PASS'}

## H. 読み取り(事実に基づく所見。判定はFable)
- **③④の機能**: W5はユーザー順(③上級者向け→④易語除外→⑤単語単体の学習価値[非必須])に是正されたが、5件要求下で**基本寄り語が増えた**。語の内訳を見ると、W5が1位に置いた語は`Strategy`(AI Std、B)・`technique`(AI Adv、B)・`exception`(UK Std、Y)・`uninvited`(UK Adv、Y)・`fate`(猿Std、Y)・`compensation`(猿Adv、Y)で、**6 levelのうち2 levelで基本寄り語(B)が『学習価値の最上位』に置かれた**(順位=学習価値順の仕様に対し、順位と③④適合が対応していない)。
- **数合わせ傾向**: W5は6/6 levelで要求上限5件を返した(『不足なら5件未満でよい・数合わせ禁止』の明記にもかかわらず)。増分11語中8語が自B(基本寄り)で、残る良質語はY 3語。上限まで必ず埋める挙動は前回W3(3/3を12/12回返答)と同じ。自Nは前回と同数(1)で、明確な低品質候補(N)は増えていないが、**境界(B)の基本寄り語が増える形の緩い数合わせ**が見られる(ただし数合わせの定義[前回DESIGN §7: N かつ R4易/R2不自然/R5重複]に厳密に該当するのは`performance`の1件)。
- **含有語の扱い(新しい事実)**: W5は『含有語を一律除外しない』ので、`detour`(←take a detour)・`interferes`(←interfere with fate)を返したが、**承認済みGate(`duplicate_of_top3`、Production `er119.run_vocab_selection`の`_containment`)がこれを除外した**(計3件、W5返答30語中10%)。Promptの方針とGateの機械除外が食い違い、3 levelで5件枠のうち1枠が無駄になった。Gateは変更していない(ユーザー§3『既存の承認済みGateは維持』)。
- **フレーズ側**: P7同一入力のため候補・順位は同一(AI島2 level・UK Adv は完全一致、UK Std・猿の手2 levelは通過句が1〜2件増)。『フレーズ抽出結果と単語抽出結果は別々に評価』のとおり、フレーズ側の再検証はしていない。
- **候補総数と`KP_CANDIDATE_MAX`**: 最終候補は9〜11件(前回r1は6〜9件)。Production上限8(`rv.KP_CANDIDATE_MAX`)は変更せず、Trial側は通過件数をそのまま記録(8超は6/6 level。前回r1は2 level[9件])。Production採用時にこの上限を超える設計は別判断(Human Review UIの扱い・OPEN-540系)。
- **再現性**: 各level 1回のため安定性は評価していない。前回Trial-01(2回実行)では猿の手Advの再現性が低かった(Jaccard 0.25)。今回の単語集合も前回r1との一致は、AI Std 3/4・AI Adv 3/4・UK Std 2/5・UK Adv 2/5・猿Std 3/5・猿Adv 3/4(重なり語数/今回語数)。追加実行は、改善見込みが低いと判断し行っていない(Status案STATUS_02 §3)。

## 時間・費用の影響(§G の値の解釈)
- 今回の6 runは、P7のAPI 0・W5 1 call + canonicalization/gloss/RQAで、**1 levelあたり平均¥1.76(5.0 call)**。前回r1(P7+W3)は平均¥1.83(6.0 call、P7 1 callを含む)。P7 1 callは約¥0.12(前回usage log: 1,200 in/1,267 out、gpt-6-luna)なので、P7込みに換算すると今回約¥1.88/level vs 前回¥1.83/level = **約+¥0.05/level(+3%)**。W5 call自体はW3と同程度(AI Std: W3 ¥0.067 → W5 ¥0.073)で、増分は候補増に伴うcanonicalization・gloss再整合の出力増(AI Std gloss出力 5,471→6,139 tokens)。出典: `runs/*/usage_log.jsonl`(`trial_runs_02.json`の`cost`、前回`w3_r1_cost`)。
- 所要(1 levelのelapsed): 今回平均178秒、前回r1平均178秒(同等。6 level並列起動のため参考値)。
- 本Trial実費: run ¥10.58(30 call)+ judge ¥5.73(6 call)= **¥16.3**(Guardrail ¥40内)。

## 9. 訂正(2026-10-26 Fable確認): 救済機構による交絡
**訂正対象**: §0-5および§E冒頭の『前回r1で除外されていた句が今回のLLM再実行で通過(LLMの揺れ)』、および委任_01報告の『`er125`は不在のためスキップ』。**いずれも誤り**。`er125_kp_rescue_production_01.py`はHEADに存在し、本日(commit 2910e859b、19:28)PRODUCTION_WIRED(既定ON)となった。前回r1(17:05生成)は配線前、今回(20:45生成)は配線後で、全6 runの`trial_result.json` `doc.rescue_provenance.rescue_enabled=true`。

### 9-1 `rescued: true`候補の全件(6 run全走査、`doc.candidates[].flags.rescued`)
| 句 | run | rescue_codes | auto可否(`rescued_not_auto`) | 前回r1に出ていたか |
|---|---|---|---|---|
| given written permission | uk_train_speaker_playback:a2 | REVERT_SURFACE(llm_key=`give written permission`) | **不可**(`p_aabe5020d3`) | 無(今回追加) |
| pulling free | monkeys_paw:a2 | REVERT_SURFACE(llm_key=`pull free`) | **不可**(`p_fd00a23331`) | 無(今回追加) |
| pulled free | monkeys_paw:b1b | REVERT_SURFACE(llm_key=`pull free`) | **不可**(`p_82e055c35c`) | 無(今回追加) |
| caught in the machinery | monkeys_paw:b1b | REVERT_SURFACE(llm_key=`caught in machinery`) | 可(auto対象のまま) | 有(r1にも出現=件数差に寄与せず) |
他の2 run(ai_island_temple a2/b1b)・uk b1bは`rescued: true`なし(`rescued_not_auto`=[])。

**救済フラグが付かなかった1件**: `accept no responsibility`(monkeys_paw:b1b、表示形`accepts no responsibility`)は`rescued`なし。`canonicalization_runtime_metadata.json`は attempt1 で`CANONICALIZATION_PASS`(reasons空)。r1では同じkey文字列がRule7(連続部分文字列でない辞書形)で除外されていた(WORD3 r1 `trial_result.json:976-979`)。r1→今回で通過した原因は**未確定**(救済ではない。LLM揺れの可能性は残るが、断定しない。Production差分0のため§9-4と矛盾しない)。

### 9-2 結論(a)
フレーズ側の件数差(前回r1 30 → 今回34)のうち**3句は救済機構の有無**による(P7入力は同一=前回r1の返答再利用)。残る1句(`accept no responsibility`)は救済外で原因未確定。`pulling free`/`pulled free`/`given written permission`は**ProductionではHR表示のみ(auto不可)**。

### 9-3 結論(b) 救済分離後のフレーズ側(6 level合計、自ルーブリック`own_rubric_02.json`)
| 集合 | 件数 | 自Y | 自B | 自N |
|---|---|---|---|---|
| 前回P7+W3 r1(救済機構なし) | 30 | 19 | 10 | 1 |
| 今回W5(救済込み・as-is) | 34 | 20 | 13 | 1 |
| 今回W5から`rescued: true`全4件を除外 | 30 | 20 | 9 | 1 |
| 今回W5から救済3件+救済外の`accept no responsibility`を除外(=r1と同一集合) | 30 | 19 | 10 | 1 |
除外した句の自評価: given written permission=B / pulling free=B / pulled free=B / caught in the machinery=B / accept no responsibility=Y。level別: UK a2 4→3、猿の手Std 6→5、猿の手Adv 7→5(r1と同数)で他3 levelは無変化。**救済を除くとフレーズ側はr1と同一(件数30、Y/B/N 19/10/1)**。したがって『フレーズ側でW5が優れる/劣る』は本Trialから言えない(交絡)。

### 9-4 結論(c) 単語側(W5)への救済の影響
単語候補(`origin: call2`)で`rescued: true`は**0件**。単語側の比較(§C・§D・§A単語列)は救済の影響を受けない(救済はcanonicalization段のフレーズ候補のみに作用)。

### 9-5 結論(d) Production差分0の再確認(er125含む)
`git diff --stat b15266613~1 b15266613 -- er125_kp_rescue_production_01.py er119_kp_candidates_01.py er105_kp_fulltext_selector_01.py er003_key_words_canonicalization.py` = **空(差分なし)**。委任_01 commit(b15266613)は上記4ファイルを変更していない。
