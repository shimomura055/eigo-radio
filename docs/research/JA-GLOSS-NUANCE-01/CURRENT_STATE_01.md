# JA-GLOSS-NUANCE-01 現状調査 (CURRENT_STATE_01)

管理ID=JA-GLOSS-NUANCE-01 / OPEN-630 / 委任_01 / 2026-10-31 / 調査のみ(Production変更0)。
ユーザー原文=docs/pm/delegation_log/2026-10-31_LEARNING-ITEM-QUALITY-TRIO-01_USER.md:28-60(§2)。方針=:38-43(文脈に最適な1語/不必要に列挙しない/2訳語は重要ニュアンスが伝わらない・誤解を生む場合のみ/2訳語の実在を先に調査)、:54(個別辞書ルール禁止・一般的改善)、:56(VALIDATEDでも正式採用判断を待つ)、:58(未承認のPrompt・品質GateをProductionへ配線しない)。
凡例: 【事実】=ファイル・記録で確認 / 【推定】=記録から言えるが直接の証拠はない / 【判定】=本agentの評価(単独ラベラー、限界は§7)。

## 1. verdict の現状

### 1-1. 本文の文脈(公開Advanced、原文逐語)
記事全体が「出しっぱなしの物」を裁判にかけるたとえで書かれている(題: The Trial of "Leaving Things Out" Is Now in Session。prosecutor・the court・defense lawyer・charge・interrogation・dismissが出る)。verdictの文と直前:

> But don't rush to announce, "Science proves that if you leave it out, you won't forget!" The supplement example is the participant's own explanation; the study did not test whether keeping it in sight works. ...
> **So the verdict is not, "Clutter is completely innocent!" First, ask, "What job is that thing doing there?" Don't dismiss it without question just because it's out. Before bringing out the storage box, hear it out.**

出典=er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01/b1b/key_phrases/kp_candidates/round_1/work/gloss_alignment_prompt.txt(【記事本文(参考)】、source_sentence_id=S36)。

### 1-2. 公開ページで verdict 周辺に出る日本語(4種類が不一致)【事実】
出典=origin/main user_test/family_x_untidiness_family_resource_01/enduser/data/article.json(levels.adv)

| 表示場所 | 日本語 |
|---|---|
| 学習項目「本文中の意味」(今回の対象) | **結論** |
| 学習項目「解説」(英語表現の説明) | 「裁判で、被告人が有罪か無罪かなどについて出される判断を指します。reach a verdict(**評決**に達する)…裁判以外でも…最終的な評価や結論を表すことがあります。…sentence(刑罰)とは区別されます。」 |
| 学習項目「日本語訳」(この文の訳) | 「したがって、**判定**は「散らかりはまったく無罪だ」というものではありません。」 |
| 本文の日本語訳(approved_ja_manuscript、std/adv共通の段落) | 「だから**判決**は、「散らかり、全面無罪!」ではない。」 |

解説(英語表現の説明)が「評決」を使い、gloss(本文中の意味)が「結論」である。解説生成は英語表現のみを入力とし、gloss・本文を受け取らない(er003_kp_general_explanation_01.py:9,166,353)ため、両者は独立に決まり、整合を取る仕組みが無い【事実】。

## 2. 生成経路の追跡(file:line)

1. 学習項目の選定(Prompt 2)は日本語glossを出力しない。全文選定由来itemはjapanese_gloss未生成で、後段で新規生成する: er105_kp_fulltext_selector_01.py:289,299(japanese_gloss=None)、er003_key_words_gloss_alignment.py:340-343(is_fulltext_gloss_missing)、:350-358(select_generation_targets)【事実】。
2. gloss新規生成=X2p'(newgen_meaning_v1、2026-10-24ユーザー正式採用APPROVED_FOR_PRODUCTION、CURRENT_SPEC.md:2892)。Prompt組立=er003_key_words_gloss_alignment.py:710-751(build_user_message_newgen_meaning)、文面=:139(HEAD)・:144(RULE)・:148(SCOPE)・:152-156(MEANING、japanese_gloss規則は:156)・:159(OUTRULES)。承認済みgloss規則(平易・硬い漢語回避・括弧禁止など)を実行時に抽出して添付(:421-443、元=er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt)【事実】。
3. 入力=対象item(rank・key_phrase・source_sentence・added_content_words)の一覧 + **記事本文の全文**(「【記事本文(参考)】」以降。上記1-1の全段落が入っている)。文単位ではない。実測: input 3,331 tokens(untidiness b1b)【事実】(gloss_alignment_prompt.txt、gloss_alignment_runtime_metadata.json attempts_detail[0].usage)。
4. モデル=gpt-6-luna(er006_model_routing_contract_01.py:50 SUPPORT_MODEL、呼出=er003_v1_n3_01_scaffold_generate.py:535-541)、reasoning_effort=high(er003_key_words_gloss_alignment.py:470)、1回の呼出で12item一括、費用¥0.6128、attempt 1でALIGN_PASS(gloss_alignment_runtime_metadata.json)【事実】。
5. 出力欄: meaning_in_text_en → naive_ja → naive_ja_conveys(yes/partly/no)→ japanese_gloss(:152-156)。**verdictの実出力**(item_log["9"]): meaning_in_text_en="The conclusion or judgment reached after considering an issue." / naive_ja="評決" / naive_ja_conveys="partly" / japanese_gloss="結論" / reasoning="裁判の比喩を使いながら、最終的な判断を述べています。" / verdict=VALID・attempt 1【事実】(gloss_alignment_runtime_metadata.json item_log.9)。
6. 検査: validate_item_corrected(:784-845)は、gloss非空・qa PASS・括弧/算用数字/…/音声化禁止記号・人称語・(新規生成では)新3欄の非空とenumだけを見る。**意味のニュアンス(近義語との区別)を検査する箇所は無い**。gloss==naive_jaも記録のみ(:780、合否に使わない)【事実】。
7. 後続: (a)canonicalization/merge: qa_*がすべてPASS(vocab_confirmed.json items[3].qa)、(b)人称・所有格の修復(er105_kp_fulltext_selector_01.py:1323-1343 person_role_repair): verdictはstatus=NO_POSSESSIVEで対象外、(c)N5一般化(er138_kp_n5_generalization_01.py:889-897 span_gloss)は句の一般化用でPROD_GLOSSを引き継ぐだけ。1語のverdictは一般化対象でなく、glossを書き換えない、(d)選定フォーム/Human Review: 候補表にglossを表示するがニュアンス判定の基準は無い(CURRENT_SPEC.md:2230は自然さ・平易さの基準)。**どの後続工程もglossを置換していない**【事実】(kp_candidates.json candidates[6].japanese_gloss=結論 → vocab_confirmed.json items[3].japanese_gloss=結論 → confirm_03/confirm_untidiness_family_resource__b1b.json extra_explanation=["verdict","結論"] → 公開article.json)。

## 3. 「結論」が選ばれた根本原因

### 3-1. 棄却した仮説(証拠付き)

| 仮説 | 結果 | 根拠 |
|---|---|---|
| 入力文脈不足(本文を渡していない) | **棄却** | 記事本文の全文が渡されている(§2-3)。modelのreasoningも「裁判の比喩」に言及している(§2-5) |
| 後処理による置換 | **棄却** | gloss生成の初回出力が既に「結論」でVALID(§2-5)。以降の工程で値は不変(§2-7) |
| モデル能力不足 | **棄却** | 同じgpt-6-lunaが、Promptの規則を変えるだけで判決/判決/評決を3/3で出した(TRIAL_01.md §2) |
| 偶然(1回だけの揺らぎ) | **棄却** | 現行Promptの再生3回でも 結論/最終的な判断/結論(裁判語0/3)。公開値と保存出力も「結論」(TRIAL_01.md §2) |

### 3-2. 原因(Promptの規則の構造)【事実+推定を区別】
verdictの出力を再生した実験(TRIAL_01.md)と、規則の原文から、次の要因が連鎖して「見出し訳(定訳)の評決」を避け、より一般的な「結論」へ落ちている。

- **原因R1: 『定訳をそのまま使わせない』規則(anchoring対策)**【事実:規則の存在・由来/実験で効果を確認】。japanese_gloss規則(:156)は、yesのとき「naive_jaをそのまま写さず、自然で平易な訳を選ぶ」、partly/noのとき「naive_jaの字義の像を使わず、meaning_in_text_enの意味全体を…平易な短い言い換えで表す」と書く。この規則は、Trial_06のOpusレビューで「naive_jaに引きずられる(アンカリング)」対策として追加された(docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/DESIGN_07.md:116、OPUS_REVIEW_07.md:54 OF-KP1-05)。**1語のkey_phraseでは、naive_jaは英和辞典の見出し訳そのもの**(verdict→評決)なので、この規則は「定訳を避けよ」という意味になる。verdictの現行Prompt再生では、yesと判定した回(3回中2回)も「そのまま写さず」により評決を避けて「結論」へ行った(A r1・r3: naive_ja=評決, conveys=yes → gloss=結論)。
- **原因R2: 比喩の『像』を剥がす規則**【事実:規則/実験で効果を確認】。meaning_in_text_enは「比喩ならその比喩が指す一般的な意味(what it stands for)」を書く(:153)。verdictはこの記事では裁判の比喩の中の語で、modelは裁判の語を「最終的な判断」という一般義へ言い換えた(meaning_in_text_en="The conclusion or judgment reached…")。partly判定の回は、さらに『字義の像を使わず』(:156)により「評決」(裁判の像)が除外される(A r2: conveys=partly, gloss=最終的な判断)。
- **原因R3: 言い換え語が一般語なので、それがgloss候補になり、近義語との区別を確かめない**【推定:meaning_in_text_enの語がglossへ流れたと読めるが、モデル内部の推論は見えない】。meaning_in_text_enの言い換えの中心語conclusionが日本語の「結論」に対応し、近義語との区別(verdictは裁判・評決の含み、conclusionは推論の帰結)を確かめる手順がPromptに無い(:156に近義語との比較指示は無く、validate(:784-845)にも無い)。
- 補助要因【推定】: 承認済みgloss規則の「平易・硬い漢語を避ける」(CURRENT_SPEC.md:2001)が「評決」を避ける方向に働いた可能性は否定できないが、実験でB3(同じ規則を維持したまま上記R1・R2を調整)が評決/判決を出したため、主因ではない。
- 実験による切り分け(TRIAL_01.md §2。各案3回): 案B=partly分岐だけ緩め+近義語対比の文を追加 → 「結論」3/3(yes分岐のR1が残るため変化なし)。案B2=yes分岐のR1も緩め+『一般語と同じ日本語にしない』確認を追加 → 「最終判断/最終的な判断」3/3(結論から離れたが、比喩の像を剥がすR2が残り裁判語にならない)。案B3=1語は見出し訳を使う(R1)+比喩の像を保つ(R2)+一般語確認 → 判決/判決/評決(3/3)。**R1(1語は見出し訳を使う)とR2(比喩の像を保つ)の両方を直した案だけが裁判語に到達した**。ただし1要因ずつ外す追加Trialは行っておらず、B2→B3の差はR2と「1語は見出し訳を使う」明文化の複合効果であり、要因の分離は不完全。

### 3-3. 結論
「結論」になった根本原因は、**X2p'(gloss新規生成)のPrompt規則が、(a)1語のkey_phraseでも英和辞典の定訳を直接使わせず、(b)比喩の語を一般義へ言い換えさせ、(c)言い換え語と近義語の区別を確かめない**ことにある。モデル・入力文脈・後処理は原因ではない。個別の語(verdict)の不具合ではなく、**1語のkey_phraseを一般語へ平板化する構造的な傾向**であり、§5で他の語にも同型の事例があることを示す。

## 4. 現在の文脈での最適な訳語【判定】

- **評決**(推奨)。理由: (1)verdictの英和辞典の見出し訳(定訳)で、この記事の裁判の比喩(検察官・開廷中・尋問)と対応が崩れない。(2)英語解説が「評決に達する」「有罪/無罪の評決」「sentence(刑罰)とは区別」と書いており、「評決」を使えば本文中の意味と解説が一致する(現状は結論/評決で不一致)。(3)「判決」は日本語では刑罰を含む判決全体を指しやすく、解説が区別するsentenceとの境が曖昧になる。(4)「結論」はconclusionと同じ訳になり、ユーザーが指摘したニュアンスの区別が日本語で消える。
- 許容: 判決(本文の日本語訳の語と一致するが、sentenceとの区別が弱い)。不可寄り: 判定(軽い)、最終判断(一般義、像が消える)、結論(conclusionと区別できない)。
- 「評決が必ず正しい」とは決め打ちしていない。文脈で比較した結果である(本文が裁判の比喩で一貫していること、解説との整合、近義語との区別)。裁判の比喩を使わない文脈の verdict(例: the verdict on the film)なら「評価」「判断」が適する場合があり、1語の置換ルールでは決められないため、一般的な方式の改善(DESIGN_01.md)を提案する。

## 5. 類似事例の調査

### 5-1. 母集団と方法
- **公開済みX/Y/Z記事**: origin/main の user_test/*/enduser/data/article.json 10記事(X5・Y2・Z3、Std/Adv各)、学習項目84件(Adv42+Std42)。抽出=tools/extract_published_glosses_01.py、data/published_glosses_01.json。
- **gloss生成の全記録**: er019/er026/er121の473ファイルから、gloss新規生成(newgen_meaning_v1)の記録1,045件(重複除去後449件=1語157・2語以上292)。Trial/evidence runを含む(公開物だけではない)。抽出=tools/collect_newgen_records_01.py、集計=tools/survey_population_01.py、data/survey_stats_01.txt。
- 判定=本agent(単独)。基準=「本文の文脈で、近義語から区別される最も限定的な訳語になっているか」。

### 5-2. 構造的な傾向(定量)【事実】(data/survey_stats_01.txt)

| 項目 | 1語(157) | 2語以上(292) |
|---|---|---|
| naive_ja_conveys yes/partly/no | 84 / 54 / 19 | 57 / 76 / 159 |
| gloss==naive_ja(見出し訳をそのまま採用) | 26件(17%) | 3件(1%) |
| yesなのにnaive_jaと異なる | **58/84(69%)** | 54/57 |
| 平均gloss文字数 | 4.71 | 8.30 |

1語のkey_phraseは、naive_jaが定訳でyes(同じ意味が通じる)と自己判定した84件のうち58件(69%)で、naive_jaと異なる別の語へ置換されている。置換の多くは無害(波長=wavelength、配偶者を亡くした=widowedなど、naive_jaの方が不自然な場合)だが、次のパターンが含まれる。

### 5-3. ニュアンス不足(平板化)の疑い事例【判定】

- **パターンH(上位語・一般語への平板化)**: verdict→結論(対象)、culprit→原因(naive=犯人。公開moon Adv、"The coat is the culprit"で責められる側のニュアンスが消える)、charge→非難(裁判のたとえの文脈。naive=料金。罪状/容疑の意味。選定候補段階で未公開)、investigation→調査(探偵のたとえの文脈。捜査の含み。未公開)、account→話、technique→やり方。
- **パターンD(定訳のある語を定義文へ置換)**: radius→「中心から外側までの長さ」(半径)、exception→「一般の決まりに当てはまらない場合」(例外)、shepherd→「羊の世話をする人」(羊飼い)、insulation→「熱を逃がしにくくするもの」(断熱)、campaign→「呼びかけ運動」、errand→「用事を済ませる外出」、porous→「小さな穴やすき間が多い」(公開moon Adv)。承認済みの「説明文・定義文にしない」(:156末尾)に反する形で、いずれもnaive_ja=定訳のyes/partlyの1語で発生している(R1の副作用と読める)。
- **公開済み記事のAdvanced 1語18件の内訳**: 明確な不足=1件(verdict)、中程度の疑い=4件(culprit原因・complications複雑な要素・frustrateいら立たせる[探偵のたとえで悩ませる]・puzzling理解しにくい[不可解な])、文体(定義風)=1件(porous)、問題なし=12件。Standard側にも同じ原因のverdict→結論がある(A2のvocab)。母集団(449)では、1語157件中パターンH 6件・D 8件を確認(約9%)。
- 注意: ラベルは本agent単独の判定で、境界の語は主観を含む。件数は目安であり、「Production全体の不良率」ではない。

### 5-4. 1訳語で足りるケースと、2訳語が必要なケース

- **2訳語が必要な実例は見つからなかった【事実+判定】**: gloss記録449件(2語以上292含む)のうち、複数訳語(「A、B」「A・B」「または」)や括弧併記を含むgloss=0件(data/survey_stats_01.txt)。公開84件でも0件。本文で語義が複数ありうる語(medium=霊媒師/媒体、adopted=養子になった/採用された、current=水の流れ/現在、execution=処刑/実行、charge=罪状/料金、seize、stain)を確認したが、**本文の文脈が1つの語義を決める**ため、いずれも1訳語で足りる(誤解を生む例は無い)。
- 1訳語で足りるケースの共通点: 本文の文脈が語義を一つに絞る。見出し訳が日本語でも同じ分野・含みを持つ(検察官・処刑・霊媒師)。
- 2訳語が理論上必要になる条件(今回のデータには実例なし): (i)本文の語義が日本語の1語に対応せず、近い2語が別々の側面を持ち、片方だけだと重要な意味が落ちる場合、(ii)1語の訳が誤読を生む場合。今回はいずれも該当せず、**2訳語を許容する規則を足す必要性は実証されていない**。許容規則を入れても複数訳語の多発は観測されなかった(TRIAL_01.md C4: B系160 item中0件)。

## 6. 現状まとめ(報告用の事実)

- 結論になった根本原因=Prompt規則(R1定訳回避・R2比喩の像剥がし・R3近義語区別の欠如)。モデル・入力文脈・後処理は原因ではない。
- 同型の事例は存在する(1語のkey_phraseで一般語化/定義文化)。ただし多くの語は問題ない。
- 1訳語で足りる。2訳語が必要な実例は未発見。

## 7. 限界

単独ラベラー(本agent)。母集団にTrial/evidence runを含む。公開10記事・Advanced中心。モデル内部の推論は見えないため、R3と補助要因は推定。母集団統計はnewgen_meaning_v1経路のみ(旧方式の公開記事は対象外)。別件: 公開Advanced Comment 4のJA訳誤り(KP-N5-PHRASE-COVERAGE-AUDIT-01 AUDIT_01.md:143-144 J4)は本調査の対象外(Fable判断)。
