# PROMPT_TRIAL_01 — ニュアンス解説Prompt品質Trial (NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01b、2026-10-29)

Status: Offline Trial(DEV/Trial専用。Production・Prompt・公開物・既存出力は未変更、読み取りのみ)。採用可否の判断はFable。VALIDATED/APPROVED_FOR_PRODUCTIONの付与なし。
正本原文: `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md` §2-A/B(最大1件・Key Phrase/Word(最大5件)と学習上の焦点が重複したらNG・候補なし可・過去Trial Promptの無検証採用禁止・Part 4等は導入しない)。

## 0. 結論(要約)

- 8記事レベル(X『AI島』Std/Adv、X『Paycheck Personality』Std/Adv、Z『告げ口心臓』Std/Adv、Y『宅配の再配達』Std/Adv)で、改良Prompt v1・v2を各1回生成(retryなし)+重複検査2段を実施。合計費用 **¥3.1921**(上限¥10)。モデル=gpt-6-luna(本番ライン既定。`er006_model_routing_contract_01.py:50` SUPPORT_MODEL、`er003_v1_n3_01_scaffold_generate.py:61` `_a2_support_model()`。評価用途の「最新原則」(Charter 25節)とは別枠で、Productionに載るモデルでの品質確認が目的)。
- **v1**: 8/8で候補を生成(0件ゼロ)。重複検査は全件PASS(構造0/8 fail・LLM 0/8 fail・引用逐語8/8)。ただし学習価値はworker所見で 高3/中4/低1(`don't have to vs mustn't`=A2既習の基礎対比)。モデル自己評価は high 7/8 で識別力がない。人工の平易文(control)でも `stood vs stood up` を強制選定=「0件」が実質出ない。
- **v2**(学習価値4条件・基礎文法対比除外・Part 1/2との役割分担・入れ替えテスト): 実8中 候補5・0件3。候補5のうち1件(`was linked to`)は段1構造検査(`link`⊂`weak link`)でfail→破棄(段2 LLMはpass=段1と段2が不一致の境界事例)。HR提示可 4件。controlは0件(0件が出せることを確認)。一方、**過度な抑制と不整合**が出た(AI島Stdで `at least`=too_basic→0件、同AdvではPASS候補。告げ口心臓も Std=`You should have seen`採用/Adv=grammar_structureで除外)。
- 重複検査 段2(LLM)の感度確認(人工候補3件): 同義の言い換え(`pass on`↔carry over)・同じ比喩の別表現(`chill someone to the bone`↔make one's blood turn cold)を2/2でfail、非重複1/1でpass。**段1(構造)は人工の重複2件とも検出できず**、LLM判定が実質の主検査。
- 実生成物でKey Phrase/Wordと実質重複と判定された採用候補は0件(v1/v2とも)。生成時に自ら `kp_word_overlap` で外した候補が3件(v1 y_std「can't be helped」、v2 paycheck_std「Coming first and being the cause」、v2 y_std「I guess it can't be helped」)あり、生成時の差別化指示は機能した。
- 単価実測: v1 ¥0.328/記事セット(Std+Adv、生成+重複判定)、v2 ¥0.382/記事セット。ユーザー原文§6の概算(+0.10〜0.14円)の約3倍。主因=推論token(1回平均 v1 757/v2 931)。70円目標の約0.5%。

## 1. 素材の確認と弱点3点(Trial-01〜04のPart 3)

読んだもの: `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/` の PROMPT_04.md:217-330(Part 3/4 Prompt=03d固定ブロック。`PROMPT_04.md:307`「0〜1個選ぶ。適切なテーマがなければ0個」)、OUTPUT_01_RAW.md、OUTPUT_04_*_USER.md の Part 3、FABLE_EVAL_01.md:6,8、FABLE_EVAL_02.md:7,10、EVAL_04.md:73。

1. **基礎語・品詞差などニュアンスではない題材を選びがち**: Trial-01 の worthy of / worth は品詞差の説明で「B1目標のAdvanced学習者に対する価値が低い」(FABLE_EVAL_01.md:6)。上位候補(shabby、Nothing showy、foolish↔wisest)を見送り、「0個でもよい」より「1つ選ぶ」方向に寄った(同:6)。
2. **選定が生成ごとに揺れ、物語解釈に寄る**: 同一Prompt・同一本文でもPart 3の選定対象が生成ごとに変わり、「物語解釈に寄る揺れがある」(FABLE_EVAL_02.md:10)。foolish↔wisest も「説明は物語解釈寄りで語法の深掘りは薄い」(同:7)。
3. **Key Phrase/Wordとの重複回避が設計に無い**: Trial-04のPart 3はPart 1/2との重複回避を指示するだけで(`PROMPT_04.md` Part 3ブロック、EVAL_04.md:73)、Key Phrase・Word(HR確定)を入力せず、焦点での重複判定もない。今回の必須条件(承認原文§2-B)に対し、重複検査工程が未整備。

(Trial-04 出力例: `take that number on its own`(ig_nobel r1)や `only half her attention`(open_window r1)は KP/Word 級の句の語義説明に近く、今回の「KP/Wordと焦点が別」条件に照らすと境界。)

## 2. 改良Prompt v1 / v2 と重複検査Prompt

方針(v1): 日本語解説、英語表現+本文逐語引用+和訳、焦点を1行(`focus`)で明示、KP/Word(5件)を入力して生成時に差別化を指示、「選ばないもの」を列挙、手順は内部思考のみ(1回生成・2段階生成にしない=Fable評価の推奨に整合)、候補なし可、解説長さ=120〜260字(Part 1の1項目相当: AI島 carry over の公開解説は約200字)。

v2 は v1 の分析(§5)を受けた1回限りの改良: 学習価値4条件(文脈性/日本語話者の落とし穴/レベル適合/非重複)、A2既習の基礎文法対比の除外、Part 1(KP)・Part 2(文法)との役割分担の明記、入れ替えテスト、`criteria_check` 出力、`mid`は候補にしない。

### 2-1. Prompt v1 全文(sha256=0c872c4832feb511f125194476c216315be88fc6a4987f3eaf6c83849f0433e0)

```text
あなたは英語学習コンテンツの編集者です。下の英語ポッドキャスト台本を読んだ学習者向けに、「ニュアンス解説」を日本語で最大1件だけ作ってください。学習価値のある候補がなければ0件にしてください。

# 記事・レベル
- 記事: {title}
- レベル: {level_note}

# 本文(引用では段落番号を付けない)
{body}

# 選定済みのKey Phrase・Word(別コーナーで解説済み。{n_kp}件)
{kp_block}

# ニュアンス解説とは
英語表現の微妙な意味の違い、語感、文脈による意味や印象の違いなど、日本語話者が辞書の訳語だけでは気づきにくい差を扱う解説です。扱える焦点の例:
(a) 近い表現との使い分け(強さ・丁寧さ・硬さ・肯定的/否定的な含み)
(b) 同じ語・構文でも文脈で意味や印象が変わる点
(c) 語の選択・助動詞・副詞などで変わる、話し手の態度や確信度の違い
(d) 日本語の訳語に引きずられると誤解しやすい点

# 最重要条件: 上のKey Phrase・Wordと重複しないこと
- 解説の「中心的な学習対象・論点(焦点)」が、上のKey Phrase・Wordのどれとも実質的に同じであってはならない。
- 表現の文字列が違っても、実質的に同じ内容を教えるなら重複とみなす(例: あるKey Phraseの類義語との違いを説明する、同じ語の別の用法を説明する)。
- 解説文の中にKey Phrase・Wordが一言登場するだけなら問題ない。ただし主役にしない。
- 本文のKey Phrase・Wordを含む文から選ぶ場合も、焦点が明確に別の語・論点であることを確かめる。

# 選ばないもの(該当する候補しかなければ0件にする)
- 品詞・語形・基礎語の文法的な違いの説明(例: 形容詞と名詞の違いだけ)
- 物語や記事内容の感想・解釈・テーマ論
- 辞書を引けば足りる語義の説明、よくある組み合わせの紹介(Key Phraseコーナーの役割)
- 文の構造・語順の解説(別の「文法・文構造」コーナーの役割)
- 本文に根拠がない一般論、学習者のレベルに見合わない細かすぎる差
- 無理に1件にするための選定。迷うなら0件にする。

# 手順(内部で考え、出力は最後のJSONのみ)
1. 本文から上の焦点に当てはまる候補を最大4つ挙げ、それぞれの焦点を1行で書く。
2. 各候補の焦点をKey Phrase・Word全件と照合し、重複するものを外す。
3. 残った候補から、このレベルの学習者が実際に誤解や使い分けで迷いやすく、学習価値が最も高い1件を選ぶ。価値が明確でなければ選ばず0件にする。

# 出力(JSONのみ。前置き・コードフェンスなし。日本語は読みやすく)
{{
  "rejected_candidates": [{{"expression": "外した候補の英語表現", "focus": "焦点を日本語1行", "reason": "kp_word_overlap または low_value または not_nuance または too_basic または other", "note": "理由を一言"}}],
  "candidate": null または {{
    "expression": "解説の中心的な学習対象の英語表現。比較なら 'A vs B'",
    "focus": "学習上の焦点を日本語1行(40字程度まで)",
    "quote_en": "本文から一字一句そのまま引用した英文(1〜2文。改変・要約・つなぎ合わせ禁止)",
    "quote_ja": "quote_enの日本語訳",
    "explanation_ja": "日本語の解説。120〜260字。比較する表現・場面を最低1つ具体的に示し、何がどう違うか(語感・印象・使い分け)を書く。Key Phrase・Wordの解説の繰り返しにしない",
    "differs_from_kp_word_ja": "Key Phrase・Wordのどれとも焦点が異なる理由を1文",
    "learning_value_self_rating": "high または mid または low(lowなら候補にせず0件にする)",
    "learning_value_reason_ja": "なぜこのレベルの学習者に価値があるかを1文"
  }},
  "no_candidate_reason_ja": "candidateがnullのときだけ理由を1〜2文。候補ありならnull"
}}

# 制約
- quote_enは本文に実在する文字列のみ。本文にない表現・事実・登場人物の言動を作らない。
- 解説の事実(語義・用法)は一般に認められた英語の用法に基づき、断定しすぎない。
- 理解度チェック・クイズ・感想は書かない。
```

### 2-2. Prompt v2 全文(sha256=9d0e0a06da02082b4ede4e0f2e09ae8609979c3641bf6a3acc49c1d1ea66da35)

```text
あなたは英語学習コンテンツの編集者です。下の英語ポッドキャスト台本を読んだ学習者向けに、「ニュアンス解説」を日本語で最大1件だけ作ってください。学習価値のある候補がなければ0件にしてください(0件は正常な結果です)。

# 記事・レベル
- 記事: {title}
- レベル: {level_note}

# 本文(引用では段落番号を付けない)
{body}

# 選定済みのKey Phrase・Word(別コーナーで解説済み。{n_kp}件)
{kp_block}

# ニュアンス解説とは
英語表現の微妙な意味の違い、語感、文脈による意味や印象の違いなど、日本語話者が辞書の訳語だけでは気づきにくい差を扱う解説です。扱える焦点の例:
(a) 近い表現との使い分け(強さ・丁寧さ・硬さ・肯定的/否定的な含み)
(b) 同じ語・構文でも文脈で意味や印象が変わる点
(c) 語の選択・助動詞・副詞などで変わる、話し手の態度や確信度の違い
(d) 日本語の訳語に引きずられると誤解しやすい点

# 他のコーナーとの役割分担
- Key Phrase・Wordのコーナー: 上の選定済み表現の意味・よく使う組み合わせ・近い表現との違いを扱う。ニュアンス解説は、これらの表現の語義補足や類義語比較をしてはならない。
- 文法・文構造のコーナー: 文型・時制・仮定法・語順などの「仕組み」を扱う。ニュアンス解説は、文の仕組みの説明ではなく、語や表現の選択による含み・印象の差を扱う。

# 最重要条件: 上のKey Phrase・Wordと重複しないこと
- 解説の「中心的な学習対象・論点(焦点)」が、上のKey Phrase・Wordのどれとも実質的に同じであってはならない。
- 表現の文字列が違っても、実質的に同じ内容を教えるなら重複とみなす(例: あるKey Phraseの類義語との違いを説明する、同じ語の別の用法を説明する)。
- 解説文の中にKey Phrase・Wordが一言登場するだけなら問題ない。ただし主役にしない。
- 入れ替えテスト: その解説をKey Phrase・Wordのコーナーに入れても違和感がないなら、重複とみなして外す。

# 学習価値の4条件(すべて明確に満たす候補だけを選ぶ。1つでも弱ければ0件)
1. 文脈性: 本文のこの場面で、その表現が選ばれていることによる含み・印象を具体的に説明できる。
2. 日本語話者の落とし穴: 日本語の訳語や既知の知識のままだと、取り違え・不自然な使い分けが実際に起こりやすい。
3. レベル適合: このレベルの学習者にとって未習か混同しやすい差である。A2までに学ぶ基礎文法の対比(例: must と have to、現在完了と過去形、冠詞の有無)や、辞書・入門書で十分な基礎語の説明は不可。
4. 非重複: 上の役割分担と重複条件に反しない。

# 選ばないもの(該当する候補しかなければ0件にする)
- 品詞・語形・基礎語の文法的な違いの説明
- 物語や記事内容の感想・解釈・テーマ論(登場人物の心理の読み取りが中心になるもの)
- 辞書を引けば足りる語義の説明、よくある組み合わせの紹介
- 文の構造・語順・時制の仕組みの解説
- 本文に根拠がない一般論、学習者のレベルに見合わない細かすぎる差
- 無理に1件にするための選定。迷うなら0件にする。

# 手順(内部で考え、出力は最後のJSONのみ)
1. 本文から上の焦点に当てはまる候補を最大4つ挙げ、それぞれの焦点を1行で書く。
2. 各候補を、Key Phrase・Word全件との照合と入れ替えテストで確かめ、重複するものを外す。
3. 残った候補を学習価値の4条件で確かめる。4条件をすべて明確に満たす候補が1件以上あれば最も価値の高い1件を選ぶ。なければ0件にする。

# 出力(JSONのみ。前置き・コードフェンスなし。日本語は読みやすく)
{{
  "rejected_candidates": [{{"expression": "外した候補の英語表現", "focus": "焦点を日本語1行", "reason": "kp_word_overlap または low_value または not_nuance または too_basic または grammar_structure または other", "note": "理由を一言"}}],
  "candidate": null または {{
    "expression": "解説の中心的な学習対象の英語表現。比較なら 'A vs B'",
    "focus": "学習上の焦点を日本語1行(40字程度まで)",
    "quote_en": "本文から一字一句そのまま引用した英文(1〜2文。改変・要約・つなぎ合わせ禁止)",
    "quote_ja": "quote_enの日本語訳",
    "explanation_ja": "日本語の解説。120〜260字。比較する表現・場面を最低1つ具体的に示し、何がどう違うか(語感・印象・使い分け)を書く。Key Phrase・Wordの解説の繰り返しにしない",
    "differs_from_kp_word_ja": "Key Phrase・Wordのどれとも焦点が異なる理由を1文",
    "criteria_check": {{"context_specific": "本文の場面での含みを1文", "jp_pitfall": "日本語話者が取り違えやすい点を1文", "level_fit": "このレベルで価値がある理由を1文(基礎文法の対比でないことを含む)"}},
    "learning_value_self_rating": "high または mid(4条件がすべて明確ならhigh。1つでも弱いならmidとし、midの場合は候補にせず0件にする)",
    "learning_value_reason_ja": "なぜこのレベルの学習者に価値があるかを1文"
  }},
  "no_candidate_reason_ja": "candidateがnullのときだけ理由を1〜2文。候補ありならnull"
}}

# 制約
- quote_enは本文に実在する文字列のみ。本文にない表現・事実・登場人物の言動を作らない。
- 解説の事実(語義・用法)は一般に認められた英語の用法に基づき、断定しすぎない。
- 理解度チェック・クイズ・感想は書かない。
```

### 2-3. 重複検査

- 段1(構造・決定論): 候補`expression`(`A vs B`は各側に分割)とKP/Wordの`key_phrase`・本文中の形の内容語(軽動詞・冠詞等を除き簡易語幹化)を比較し、一方が他方の部分集合なら一致=fail(`structural_check`、`tools/nuance_trial_01.py`)。
- 段2(LLM・理由付き): 下のPromptでKP/Word全件についてsame_focusを判定(承認原文§2-Bの規則をそのままPromptに記載)。モデル=gpt-6-luna(生成と同一モデル=自己判定のバイアスの可能性あり)。
- 追加(決定論): 引用`quote_en`が本文に逐語で実在するか。
- 最終判定: 段1 fail または 段2 fail または 引用不一致 のいずれかでfail(Q優先の保守側)。

判定Prompt(sha256=bb3d84ee351adf5dfbb1c1c1fe4198d477088eba081b5f24cf3fc13ec85e4c4f):

```text
あなたは英語学習コンテンツの重複検査員です。下の「ニュアンス解説の候補」が、「選定済みKey Phrase・Word」のいずれかと学習上の焦点で重複していないかを判定してください。

# 判定基準(ユーザー承認済みの規則)
- 単語の文字列一致ではなく、解説の学習上の焦点で判定する。
- 候補の解説文中にKey Phrase・Wordが登場すること自体は問題ない。
- ただし、候補の中心的な学習対象・論点が、Key Phrase・Wordのいずれかと同じ場合は不可(fail)。
- 表現が異なっていても、実質的に同じ内容(同じ語義・用法・使い分け)を教える場合は重複(fail)。
- 表現が含まれていても、解説の焦点が明確に別であれば許容(pass)。

# ニュアンス解説の候補
- 表現: {expression}
- 焦点: {focus}
- 本文引用: {quote_en}
- 解説: {explanation_ja}

# 選定済みKey Phrase・Word({n_kp}件)
{kp_block}

# 出力(JSONのみ。前置き・コードフェンスなし)
{{
  "per_item": [{{"item": "Key Phrase/Wordの表現", "same_focus": true または false, "note": "同じ/別と判断した理由を一言"}}],
  "verdict": "pass または fail",
  "reason": "最終判断の理由を日本語1〜2文(failなら、どのKey Phrase・Wordと何が同じ焦点か)"
}}
per_itemは上のKey Phrase・Word全件を同じ順で列挙すること。1件でもsame_focusがtrueならverdictはfail。
```

## 3. 対象記事と入力(KP/Word)

| 対象 | 本文 | KP/Word(各レベル最大5件) | 状態 |
|---|---|---|---|
| ai_island_temple Standard (X) | 2446字 | carry over / take a detour / card to play / worth paying attention to / obstacle | confirmed: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2/audit/confirmed_selection.json |
| ai_island_temple Advanced (X) | 2629字 | carry over / call on / take a detour / card to play / obstacle | confirmed: er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/b1b/audit/confirmed_selection.json |
| paycheck_personality Standard (X) | 2425字 | conscientiousness / weak link / come first / none other than / pay raise | confirmed: user_test/paycheck_personality_e2e_02/index.html (公開済みKey Phrase行。HR form導入前の公開確定KP。confirmed_selection.json無し) |
| paycheck_personality Advanced (X) | 2490字 | conscientiousness / come first / weakly linked to higher income / in the spotlight / hold on | confirmed: user_test/paycheck_personality_e2e_02/index.html (公開済みKey Phrase行。HR form導入前の公開確定KP。confirmed_selection.json無し) |
| the_tell_tale_heart Standard (Z) | 2274字 | make one's blood turn cold / raise one's voice / groan / rush at someone / go on talking | confirmed: er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_voice_fenrir_01/a2/audit/confirmed_selection.json |
| the_tell_tale_heart Advanced (Z) | 2240字 | sharpen someone's senses / mock / hideous / blood went cold / never stir | confirmed: er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_voice_fenrir_01/b1b/audit/confirmed_selection.json |
| redelivery_fee Standard (Y) | 3413字 | end up getting it / can't be helped / make an effort / in person / encourage | confirmed: er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01_s23f/a2/audit/confirmed_selection.json |
| redelivery_fee Advanced (Y) | 3656字 | doesn't sit right with someone / take the trouble to / end up receiving / beforehand / repeatedly | confirmed: er121_output/family_y_production_01/redelivery_fee/run_gpg5_y_01_s23f/b1b/audit/confirmed_selection.json |

注: Paycheckの公開KPは、HR form導入前に公開された確定KP(公開済みページのKey Phrase行)で、`confirmed_selection.json`は存在しない。Yは公開前(ユーザー最終試聴待ち)の既存完成run(KPはHR確定済み)。本文はAI島=公開済み(Local Rewrite適用後)、告げ口心臓=公開済みページの`Full Story`行を連結、Y=`parts.json`の`y_segment_order`連結。

## 4. 結果表

### 4-1. v1(gpt-6-luna、各1回、retryなし)

| 記事 | レベル | 候補表現 | 焦点 | 重複判定(段1構造/段2LLM/引用逐語) | 理由 | モデル自己評価 / worker所見 | 費用(円) |
|---|---|---|---|---|---|---|---|
| ai_island_temple | Standard | at least | 「少なくとも」ではなく、主張の範囲を限定する使い方 | **PASS** (pass/pass/OK) | 候補は at least が主張の適用範囲を限定する用法を解説しており、選定済みの表現が扱う語義・用法とは重複しません。 | high / 高: 「少なくとも」を下限と取る日本語訳の落とし穴。文脈(一般化を避ける)が明確。 | 0.122 |
| ai_island_temple | Advanced | At least for this AI | 主張の範囲を限定し、一般化を避ける言い方 | **PASS** (pass/pass/OK) | 候補は「少なくとも」によって主張の適用範囲を限定し、一般化を避ける用法を解説しています。選定済みのKey Phrase・Wordはいずれも別の語義・用法が焦点です。 | high / 高: 同上。For this AI だけでも足りるが At least を足す含みの差まで述べる。 | 0.157 |
| paycheck_personality | Standard | may have affected | mayが、原因を断定せず可能性にとどめる語感 | **PASS** (pass/pass/OK) | 候補の中心はmayが可能性を示し、原因を断定しない用法です。選定済みの各表現とは学習上の焦点が異なります。 | high / 中: may の可能性/断定の差。B1既習の基礎寄りだが本文の因果慎重論と結びつく。 | 0.146 |
| paycheck_personality | Advanced | don’t have to vs mustn’t | 「必要がない」と「してはいけない」の意味の違い | **PASS** (pass/pass/OK) | 候補は「必要がない」と「してはいけない」の意味の違いを解説しています。選定済みのKey Phrase・Wordはいずれも別の語義や用法が焦点です。 | high / 低: don't have to vs mustn't はA2既習の基礎対比。Advanced学習者には価値が薄い(Trial-01のFable評価=基礎語の品詞比較不可と同型)。 | 0.200 |
| the_tell_tale_heart | Standard | You should have seen ... | 過去の場面を強調して語る表現で、助言ではない | **PASS** (pass/pass/OK) | 候補の焦点は“You should have seen ...”を助言ではなく、過去の場面を強調して語る表現として説明することです。選定済みのKey Phrase・Wordはいず… | high / 高: You should have seen ... を『見るべきだった』と誤読しやすい。誇張表現として語感が明確。 | 0.147 |
| the_tell_tale_heart | Advanced | perhaps | 神経質さを控えめに認め、正気だと強く主張する対照 | **PASS** (pass/pass/OK) | 候補はperhapsによる控えめな認め方と、後半の強い断言との対照が焦点です。選定済みのKey Phrase・Wordはいずれも異なる語義・用法を扱っています。 | mid / 中: perhaps の控えめな認めと perfectly sane の断言の対照。語は基礎的だが対照の読みが本文固有で物語解釈寄り。 | 0.209 |
| redelivery_fee | Standard | doesn’t feel right to me | 断定を避け、自分の感覚として不公平さを伝える | **PASS** (pass/pass/OK) | 候補は、客観的な断定を避けて自分には不公平に感じると伝える表現の解説です。選定済みのKey Phrase・Wordはいずれも異なる意味や用法を扱っており、学習上の焦点は重複してい… | high / 中: feel right to me の主観化。語義説明に近くKP型イディオムの補足に寄る(Adv側KPは sit right)。 | 0.183 |
| redelivery_fee | Advanced | I’d be happy if ... | 希望を直接要求せず、控えめに伝える言い方 | **PASS** (pass/pass/OK) | 候補の焦点は、希望を直接要求せずに控えめに伝える言い方です。選定済みのKey Phrase・Wordはいずれも異なる意味・用法を扱っているため、重複しません。 | high / 中: I'd be happy if ... の控えめな要望。仮定法の仕組み(文法コーナー領域)に隣接。 | 0.150 |
| synthetic_control | Standard | stood vs stood up | stoodは立った状態、stood upは立ち上がる動作を表す | **PASS** (pass/pass/OK) | 候補の焦点は stood と stood up の意味の違いです。選定済みのKey Phrase・Wordはいずれも別の意味・用法を扱っているため、学習上の焦点は重複しません。 | mid / 低: 人工の平易文で stood vs stood up を強制選定=0件が出せない証拠。 | 0.134 |

### 4-2. v2(同一対象への再生成は各1回のみ)

| 記事 | レベル | 候補表現 | 焦点 | 重複判定(段1構造/段2LLM/引用逐語) | 理由 | モデル自己評価 / worker所見 | 費用(円) |
|---|---|---|---|---|---|---|---|
| ai_island_temple | Standard | (0件) | - | - | 候補はありますが、基本的な表現の説明にとどまるか、この文章固有の比喩に限られます。4条件を明確に満たす解説対象はありません。 | - / 誤り(見逃し): 0件。ただし同記事Advでは at least を選定。at least は v1 で高価値だったため too_basic 判定は過剰抑制(Std/Adv不整合)。 | 0.120 |
| ai_island_temple | Advanced | at least for this AI | at leastが一般化を避け、結論の適用範囲を絞る働き | **PASS** (pass/pass/OK) | 候補の焦点は at least が結論の適用範囲を限定する働きであり、選定済み項目の意味・用法とは重複しません。 | high / 高: v1と同表現。4条件の根拠(criteria_check)が具体的。 | 0.173 |
| paycheck_personality | Standard | was linked to | 研究結果で関連を示し、原因までは断定しない表現 | **FAIL** (fail/pass/OK) | 段1 was linked to~weak link / 候補は関連があっても因果までは示さない点を説明しています。「weak link」は関連の弱さを表すため、学習上の焦点は異なります。 | high / 中〜高: be linked to=関連≠因果の語感。ただしKP『weak link』と語・論点が近接し、段1構造検査がfail→破棄(境界事例)。 | 0.274 |
| paycheck_personality | Advanced | (0件) | - | - | 候補表現はありますが、基礎的な語法の説明か、記事内容の理解にとどまります。4条件を明確に満たすニュアンス解説はありません。 | - / 妥当(0件): v1の低価値候補を回避。残る候補(may have affected 等)は基礎的/記事理解寄りという判断は妥当。 | 0.136 |
| the_tell_tale_heart | Standard | You should have seen my patience | 「見ておくべきだった」ではなく、すごさを誇張して伝える言い方 | **PASS** (pass/pass/OK) | 候補は You should have seen ... が、実際に見ていたら分かったはずだという誇張を込めて聞き手に場面を想像させる用法を解説しています。選定済みの各表現の語義… | high / 高: v1と同表現。should have の『義務』誤読の落とし穴を明記。 | 0.250 |
| the_tell_tale_heart | Advanced | (0件) | - | - | 候補になりそうな表現はありますが、語義が基礎的な範囲にとどまるか、文法・構文の説明が中心になります。指定された条件をすべて満たすものはありません。 | - / 妥当(やや惜しい): 0件。v1候補(perhaps)は中程度だったので、0件は許容範囲。Std側は You should have seen を選んだのにAdvでは grammar_structure として外す不整合あり。 | 0.135 |
| redelivery_fee | Standard | Am I wrong to feel this way? | 意見をやわらげ、相手に妥当性を尋ねる語感 | **PASS** (pass/pass/OK) | 候補は、自分の感じ方が妥当かを尋ねることで意見をやわらげる語感が中心です。選定済みの5件はいずれも異なる語義・用法を扱っています。 | high / 中: Am I wrong to feel this way? の意見をやわらげる含み。会話上の含みで文法ではないが価値は中程度。 | 0.222 |
| redelivery_fee | Advanced | I guess it can’t be helped | 仕方ないという諦めを示しつつ、賛成とは限らない語感 | **PASS** (pass/pass/OK) | 候補は「仕方ない」としぶしぶ認めつつ、必ずしも賛成ではないという語感を説明しています。選定済みの表現はいずれも別の語義・用法が焦点です。 | high / 中〜高: I guess it can't be helped の『諦め≠賛成』。ただしこの句は同記事StdのKP。Adv内ではKP/Wordと非重複だが『KP級の定型句』である点に注意。 | 0.219 |
| synthetic_control | Standard | (0件) | - | - | 本文の表現には文脈に沿った読み取りが必要なものもありますが、辞書的な意味や基本的な語の理解を超える学習価値の高いニュアンスは見当たりません。 | - / 妥当(0件): 人工の平易文で0件を返せた=『0件を選べる』ことの確認。 | 0.091 |

モデル自己評価とworker所見は別: worker所見(Sonnet)は、引用・日本語の正確性(誤りなし)に加え、「日本語話者が取り違えやすいか」「そのレベルの学習者に基礎すぎないか」「KP/Wordコーナーの内容と入れ替えて違和感がないか」で判断した主観評価であり、Production基準ではない(HRまたはFableの評価に置き換わる)。

### 4-3. 重複検査 段2の感度確認(人工候補。実生成物ではない)

| probe | 対象 | 段1構造 | 段2LLM | 理由(段2) |
|---|---|---|---|---|
| probe_overlap_synonym | ai_island_std / 候補 `pass on` | pass | fail | 候補は「carry over」との違いを述べながら、期間をまたいで内容が残る用法も説明しています。この点が選定済みの「carry over」の焦点と重なります。 |
| probe_overlap_same_idiom_other_form | tth_std / 候補 `chill someone to the bone` | pass | fail | 候補は、make one's blood turn cold と同じく、寒さの比喩によって強い恐怖やぞっとする感覚を表す点を解説しており、学習上の焦点が重複しています。 |
| probe_non_overlap | ai_island_std / 候補 `at least` | pass | pass | 候補の焦点は、at least を使って主張の範囲をこのAIに限定することです。選定済みの表現・単語はいずれも異なる意味や用法が学習対象です。 |

## 5. 分析

### 5-1. 0件が妥当なケース
- 平易文・基礎語中心でKP/Word以外に文脈固有の含みが無い場合: 人工control(「A Quiet Morning」)でv2=0件(v1は `stood vs stood up` を強制選定)。実記事ではv2 Paycheck Adv(基礎的な法助動詞/記事理解寄りの候補しか無い)が妥当な0件。
- KP級の定型句や、KP/Wordと語・論点が近い表現しか残らない場合(v2 paycheck_std の `was linked to`↔`weak link` は、0件扱いで破棄)。
- 0件率の目安: v2 実8中 0件3+重複破棄1=HR提示可4(50%)。仕様上0件は正常(承認原文§2-A-6)。

### 5-2. 重複しがちなパターン
1. **KP級の定型句を候補にする**: v2 y_redelivery_adv の `I guess it can't be helped` は同記事StdのKey Phrase。同レベル内ではKP/Wordと非重複だが、HRがKPに選び得る粒度の句。Yのような口語意見記事で起きやすい(v1/v2のy_std生成時には `can't be helped` を自ら `kp_word_overlap` で除外)。
2. **同一語彙の別側面**: v2 paycheck_std `was linked to` vs KP `weak link`(段1が検出、段2は別焦点と判断)。語は同じ`link`で、論点(関連≠因果 / 関連の弱さ)が隣接する境界事例。
3. **類義語比較・同じ比喩の別表現**: 段1では検出不能(人工probe 2/2が段1 pass、段2 fail)。実生成物には出なかった(生成時の差別化指示が効いた)。
4. 文法コーナー(Part 2)との境界: `I'd be happy if`(仮定法)・`You should have seen`(modal perfect)・`must have`は文法解説と隣接。v2でも同一表現がStdでは採用、Advでは `grammar_structure` として除外と判断が割れた(告げ口心臓)。

### 5-3. Part 1「類義語との違い」観点との役割分担
- 公開済みPart 1(Vocabulary & Expressions)の解説は、意味・よく使う組み合わせ・近い表現との違いを含む(例: AI島 `card to play` ↔ `a card up one's sleeve`、公開ページ`family_x_ai_island_form_01/index.html`のstudy section)。ニュアンス解説がKP/Word本体の類義語比較をすると、Part 1と実質重複する。
- v2は「KP/Word本体の語義補足・類義語比較の禁止」と入れ替えテストを明記。生成物にはKP本体の類義語比較は出なかった(v1でも0)。役割分担は「ニュアンス解説=KP/Word以外の語・表現の語感/含み/文脈差」で運用可能と判断。
- Part 2(文法)の確定内容(`confirmed_selection.json` の`grammar`)はこのTrialでは入力していない(AI島a2・告げ口心臓a2は0件、Y b1b は1件)。Production配線時は、確定済み文法項目も入力に渡して重複回避させる案(設計側=01aで検討)。

### 5-4. 弱点
1. **自己評価が識別しない**: v1 high 7/8(`don't have to vs mustn't` も high)。v2は4条件の`criteria_check`で根拠が具体化し、`mid`以下は0件にしたことで基礎対比は消えたが、同一モデルの自己申告に過ぎない。ゲートに使えるのは重複検査(段2)であり、学習価値はHR/Fable評価が必要。
2. **v2の過剰抑制・Std/Adv不整合**(N=1): AI島Stdで `at least` を too_basic として0件。同記事Advでは同表現を採用。レベル別の基準(Standardでの `too_basic` の線引き)が曖昧。同一標本の再生成を1回に制限したため、揺れの大きさ(再現率)は未測定。
3. **段1の限界と段1/段2の不一致**: 段1は人工重複を検出できず、実生成物では偽陽性(境界)1件。段1 failを自動破棄とするとQ優先(安全側)だが、有用候補を失い得る。
4. **単価**: 推論tokenにより想定の約3倍(それでも70円目標の約0.5%)。judge callは候補ありの時のみ。
5. **同一モデルでの生成と判定**: 段2の自己判定バイアスの可能性。probeでは感度を確認したが、微妙な境界事例の網羅は未確認。

### 5-5. 次の一手の候補(Fable向け。実行・採用判断はFable)
- A: v2をベースに、レベル別基準(Standardでは `at least` のような頻出機能語の含みを許す/Advancedは基礎文法の対比のみ除外)を1文足して、Production設計(01a)へ渡す。追加Trialは、Production runtime(実HRフロー)で複数記事を見てから行う案。改善見込み=Std/Adv不整合の低減(中)。
- B: 段1は「failなら破棄」ではなく「flag→段2へヒント付きで再確認」とし、最終判定はQ優先(いずれかfailで破棄)を維持するか、構造hitのみの偽陽性を許容するかは設計判断(承認原文§2-B「HR提示前に原則として品質確認」の範囲内でB=承認範囲内)。
- C: Part 2の確定文法項目を入力に加える(隣接領域の回避)。

## 6. 候補本文(全文)と重複検査結果

### 6-1. v1

#### v1 / ai_island_temple Standard (ai_island_std)
- 表現: **at least**
- 焦点: 「少なくとも」ではなく、主張の範囲を限定する使い方
- 本文引用: For this AI, at least, remembering that way helped it build towers.
- 和訳: 少なくともこのAIについては、その方法を覚えていたことが塔を建てる助けになりました。
- 解説(155字): ここでの at least は、数の下限を示す「少なくとも」ではなく、「このAIについて言える範囲では」と主張を限定する表現です。たとえば at least three towers なら「少なくとも3つの塔」で数の話になります。ここでは、結果をすべてのAIに一般化せず、このAIに限った説明だと示しています。
- KP/Wordと焦点が異なる理由(生成時): 既出表現の語義ではなく、at least が主張の適用範囲を狭める働きに焦点を当てています。
- 価値の理由(生成時): at least をいつも数の「少なくとも」と捉える誤解を避け、説明の限定にも気づけるようになります。 / 自己評価=high
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補は at least が主張の適用範囲を限定する用法を解説しており、選定済みの表現が扱う語義・用法とは重複しません。
  - carry over: same_focus=False (「持ち越す」と、主張の範囲を限定する用法は焦点が異なる。)
  - take a detour: same_focus=False (「寄り道をする」と、主張の範囲を限定する用法は焦点が異なる。)
  - card to play: same_focus=False (「使える手」と、主張の範囲を限定する用法は焦点が異なる。)
  - worth paying attention to: same_focus=False (「注目する価値がある」と、主張の範囲を限定する用法は焦点が異なる。)
  - obstacle: same_focus=False (「障害物」と、主張の範囲を限定する用法は焦点が異なる。)
- 検討して外した候補: なし

#### v1 / ai_island_temple Advanced (ai_island_adv)
- 表現: **At least for this AI**
- 焦点: 主張の範囲を限定し、一般化を避ける言い方
- 本文引用: At least for this AI, remembering that technique helped it build towers.
- 和訳: 少なくともこのAIについては、そのテクニックを覚えていたことが、塔を建てる助けになりました。
- 解説(164字): 「at least」はここでは「少なくとも」で、主張の適用範囲をこのAIに限定し、ほかのAIにも同じ効果があるとは言っていません。「For this AI, ...」だけでも対象は示せますが、「At least」を加えると、確認できた範囲に慎重にとどめる響きが出ます。一例だけで結果を述べるときなど、一般化を避けるのに使えます。
- KP/Wordと焦点が異なる理由(生成時): 持ち越しや依頼などの語義ではなく、主張の確かさと適用範囲を限定する表現が焦点です。
- 価値の理由(生成時): 実験結果や自分の経験を英語で述べる際、証拠の範囲を超えて一般化しない言い方を学べます。 / 自己評価=high
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補は「少なくとも」によって主張の適用範囲を限定し、一般化を避ける用法を解説しています。選定済みのKey Phrase・Wordはいずれも別の語義・用法が焦点です。
  - carry over: same_focus=False (次に持ち越す意味を扱っており、主張の適用範囲を限定する焦点とは別です。)
  - call on: same_focus=False (頼むという意味を扱っており、一般化を避ける表現とは別です。)
  - take a detour: same_focus=False (遠回りをする意味を扱っており、主張の範囲を限定する焦点とは別です。)
  - card to play: same_focus=False (打てる手という意味を扱っており、候補の学習焦点とは別です。)
  - obstacle: same_focus=False (障害物という意味を扱っており、候補の学習焦点とは別です。)
- 検討して外した候補: wave a flag (low_value: この文脈では慣用的な比喩の意味を知ることが中心になり、使い分けの学習価値は限定的。)

#### v1 / paycheck_personality Standard (paycheck_std)
- 表現: **may have affected**
- 焦点: mayが、原因を断定せず可能性にとどめる語感
- 本文引用: Something else may have affected both.
- 和訳: 何か別のものが、その両方に影響した可能性もあります。
- 解説(178字): ここでの may は「〜したかもしれない」と可能性を示し、別の要因が実際に影響したと断定していません。時間を追ったデータで関連が見つかっても、原因までは確定できないという慎重な姿勢を表します。たとえば “Something else did affect both.” なら、別の要因が両方に影響したと事実として述べるため、確信の度合いが大きく異なります。
- KP/Wordと焦点が異なる理由(生成時): 既出項目の意味ではなく、助動詞 may が示す確信度と断定の避け方を扱っています。
- 価値の理由(生成時): 研究やニュースの説明で、可能性と確定した事実を読み分ける助けになります。 / 自己評価=high
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補の中心はmayが可能性を示し、原因を断定しない用法です。選定済みの各表現とは学習上の焦点が異なります。
  - conscientiousness: same_focus=False (性格特性ではなく、mayによる可能性の示し方が焦点。)
  - weak link: same_focus=False (関連の強さではなく、原因を断定しない表現が焦点。)
  - come first: same_focus=False (出来事の先後ではなく、mayが示す可能性が焦点。)
  - none other than: same_focus=False (人物の特定ではなく、原因を断定しない語感が焦点。)
  - pay raise: same_focus=False (昇給ではなく、mayによる可能性の示し方が焦点。)
- 検討して外した候補: the arrow does not point only one way (not_nuance: 主に研究結果の内容を説明する比喩で、表現の使い分けとしての学習価値は低い)

#### v1 / paycheck_personality Advanced (paycheck_adv)
- 表現: **don’t have to vs mustn’t**
- 焦点: 「必要がない」と「してはいけない」の意味の違い
- 本文引用: So when you look back on your income or the way you work, you don’t have to end the story with “That’s just my personality.”
- 和訳: だから、自分の収入や働き方を振り返るとき、「それが自分の性格だから」と結論づける必要はありません。
- 解説(185字): この文の “don’t have to” は「〜する必要はない」で、選択肢を示す表現です。「そうしてはいけない」と禁止する意味ではありません。禁止なら “mustn’t” が近く、たとえば “You mustn’t end the story that way.” は「そのように話を締めてはいけない」と強く制止します。ここでは結論を押しつけず、別の見方を促しています。
- KP/Wordと焦点が異なる理由(生成時): 選定済み表現の意味や語感ではなく、必要がないことと禁止の違いを扱っています。
- 価値の理由(生成時): “don’t have to” を禁止と取り違えやすく、日常的にもよく使う区別だからです。 / 自己評価=high
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補は「必要がない」と「してはいけない」の意味の違いを解説しています。選定済みのKey Phrase・Wordはいずれも別の語義や用法が焦点です。
  - conscientiousness: same_focus=False (仕事での慎重さや責任感を表す語で、必要・禁止の区別とは別の焦点です。)
  - come first: same_focus=False (何かが他より先に起こることを表し、必要・禁止の区別とは別の焦点です。)
  - weakly linked to higher income: same_focus=False (収入との弱い関連を表し、必要・禁止の区別とは別の焦点です。)
  - in the spotlight: same_focus=False (注目を集めている状態を表し、必要・禁止の区別とは別の焦点です。)
  - hold on: same_focus=False (短時間待つことを表し、必要・禁止の区別とは別の焦点です。)
- 検討して外した候補: なし

#### v1 / the_tell_tale_heart Standard (tth_std)
- 表現: **You should have seen ...**
- 焦点: 過去の場面を強調して語る表現で、助言ではない
- 本文引用: You should have seen my patience—he never even moved!
- 和訳: 私の忍耐強さを見てほしかったものだ。彼は少しも動かなかった！
- 解説(188字): ここでの“You should have seen ...”は「見るべきだった」という助言や義務ではなく、「見ていたら驚いたでしょう」「どれほどすごかったか想像して」という強調です。たとえば“You should have seen the crowd!”なら、群衆を見るよう勧めているのではなく、その多さを印象的に伝えます。この語り手は、自分の忍耐を誇る調子で使っています。
- KP/Wordと焦点が異なる理由(生成時): 選定済み表現の意味を言い換えるのではなく、should have seenが助言ではなく過去の様子を強調する用法を扱っています。
- 価値の理由(生成時): shouldを「〜すべき」とだけ覚えると誤解しやすく、会話でよく使われる強調表現として役立ちます。 / 自己評価=high
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補の焦点は“You should have seen ...”を助言ではなく、過去の場面を強調して語る表現として説明することです。選定済みのKey Phrase・Wordはいずれも別の語義・用法を扱っています。
  - make one's blood turn cold: same_focus=False (ぞっとさせる表現が焦点であり、過去の場面を強調する表現とは異なる。)
  - raise one's voice: same_focus=False (声を大きくする用法が焦点であり、候補の表現とは異なる。)
  - groan: same_focus=False (うめくという動作が焦点であり、候補の表現とは異なる。)
  - rush at someone: same_focus=False (人に向かって突進する動作が焦点であり、候補の表現とは異なる。)
  - go on talking: same_focus=False (話し続ける用法が焦点であり、候補の表現とは異なる。)
- 検討して外した候補: not him (too_basic: 否定と対比の基本的な読み取りにとどまるため。)

#### v1 / the_tell_tale_heart Advanced (tth_adv)
- 表現: **perhaps**
- 焦点: 神経質さを控えめに認め、正気だと強く主張する対照
- 本文引用: Nervous, perhaps, but perfectly sane.
- 和訳: 神経質なのかもしれない。だが、完全に正気だ。
- 解説(156字): perhaps はここでは、神経質であることを控えめに認める響きがあります。一方、後半の perfectly sane は強い断言です。たとえば “I’m nervous” なら本人がはっきり認める言い方ですが、perhaps を添えることで、語り手は不安定さを少し認めながら「狂ってはいない」と主張しています。
- KP/Wordと焦点が異なる理由(生成時): 既出項目は感覚や恐怖などの語義を扱いますが、ここでは perhaps が示す控えめな態度と、後半の断言との対照を扱います。
- 価値の理由(生成時): perhaps が単なる確率表現にとどまらず、話し手の認め方を和らげることを文脈から学べます。 / 自己評価=mid
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補はperhapsによる控えめな認め方と、後半の強い断言との対照が焦点です。選定済みのKey Phrase・Wordはいずれも異なる語義・用法を扱っています。
  - sharpen someone's senses: same_focus=False (感覚を研ぎ澄ます用法が焦点で、別の内容です。)
  - mock: same_focus=False (ばかにする意味が焦点で、別の内容です。)
  - hideous: same_focus=False (ひどく気味の悪いという意味が焦点で、別の内容です。)
  - blood went cold: same_focus=False (恐怖で血の気が引く表現が焦点で、別の内容です。)
  - never stir: same_focus=False (少しも身じろぎしない意味が焦点で、別の内容です。)
- 検討して外した候補: What if a neighbour heard? (low_value: 仮定の形による懸念の表現としては基本的で、選定候補より学習価値が低い。)

#### v1 / redelivery_fee Standard (y_redelivery_std)
- 表現: **doesn’t feel right to me**
- 焦点: 断定を避け、自分の感覚として不公平さを伝える
- 本文引用: Having to pay for a redelivery just doesn’t feel right to me.
- 和訳: 再配達にお金を払わなければならないのは、どうも納得できない気がします。
- 解説(141字): feel right to me は、正しいかどうかを客観的に断定するより、「自分にはしっくりこない」という感覚を伝えます。この人は再配達料を「間違った制度だ」と言い切るのではなく、自分には不公平に感じると述べています。just はここでは、その感覚を率直に表す響きを添えています。
- KP/Wordと焦点が異なる理由(生成時): 選定済みのKey Phrase・Wordは別の語句や意味が焦点で、ここでは意見を個人的な感覚として表す言い方を扱っています。
- 価値の理由(生成時): 「間違いだ」と強く断定する表現との違いを知ると、意見の強さを調整しやすくなります。 / 自己評価=high
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補は、客観的な断定を避けて自分には不公平に感じると伝える表現の解説です。選定済みのKey Phrase・Wordはいずれも異なる意味や用法を扱っており、学習上の焦点は重複していません。
  - end up getting it: same_focus=False (結局受け取ることを表す表現で、感覚や不公平さの伝え方とは焦点が異なる)
  - can't be helped: same_focus=False (仕方がないという意味で、自分の感覚として不公平さを伝える焦点とは異なる)
  - make an effort: same_focus=False (努力することを表す表現で、候補の焦点とは異なる)
  - in person: same_focus=False (直接行うことを表す語句で、候補の焦点とは異なる)
  - encourage（本文中の形: encourages）: same_focus=False (促すことを表す語で、候補の焦点とは異なる)
- 検討して外した候補: can't be helped (kp_word_overlap: 選定済みのKey Phraseと実質的に同じです。); simply say (too_basic: この文脈での差は小さく、単語の意味を知れば十分です。)

#### v1 / redelivery_fee Advanced (y_redelivery_adv)
- 表現: **I’d be happy if ...**
- 焦点: 希望を直接要求せず、控えめに伝える言い方
- 本文引用: I’d be happy if the first redelivery were free, and people who are repeatedly away had to pay.
- 和訳: 最初の再配達は無料で、何度も不在にする人には支払ってもらえるなら、私はありがたいです。
- 解説(166字): ここでの “I’d be happy if ...” は、文字どおり「そうなら幸せ」というより、「そうしてもらえたらありがたい」という控えめな希望です。“I want the first redelivery to be free.” と言うと、希望をより直接的に述べる印象になります。提案や要望をやわらかく伝えたいときに使えます。
- KP/Wordと焦点が異なる理由(生成時): 選定済み表現の「わざわざする」「結局〜になる」などの意味ではなく、希望の伝え方の強さが焦点です。
- 価値の理由(生成時): 日本語の「うれしい」に直訳すると見落としやすい、要望をやわらげる働きを実例で学べます。 / 自己評価=high
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補の焦点は、希望を直接要求せずに控えめに伝える言い方です。選定済みのKey Phrase・Wordはいずれも異なる意味・用法を扱っているため、重複しません。
  - doesn't sit right with someone: same_focus=False (しっくりこないという感覚を表す表現で、控えめな希望の伝え方とは焦点が異なる)
  - take the trouble to: same_focus=False (わざわざ何かをすることを表し、希望を控えめに伝える用法とは異なる)
  - end up receiving: same_focus=False (結局受け取るという結果を表し、希望の伝え方とは焦点が異なる)
  - beforehand: same_focus=False (前もってという時間を表す語で、控えめな希望の表現とは異なる)
  - repeatedly: same_focus=False (何度もという頻度を表す語で、控えめな希望の表現とは異なる)
- 検討して外した候補: I guess it can't be helped (low_value: 文脈に沿った語感はあるが、今回選ぶ表現より使い分けの学習価値が低い)

#### v1 / control(人工平易文。診断用)

#### v1 / synthetic_control Standard (control_trivial)
- 表現: **stood vs stood up**
- 焦点: stoodは立った状態、stood upは立ち上がる動作を表す
- 本文引用: The bus was full, so she stood.
- 和訳: バスは満員だったので、彼女は立っていた。
- 解説(148字): この文の stood は、満員のバスの中で「立った状態でいた」という意味です。stood up なら、座った状態などから「立ち上がった」という動作に焦点が移ります。たとえば、バスで席を譲るために立ち上がった場面なら stood up が自然ですが、この文では乗車中に立っていたことを表しています。
- KP/Wordと焦点が異なる理由(生成時): 解説の中心は stood と stood up の動作・状態の違いで、選定済み表現の意味とは異なります。
- 価値の理由(生成時): stoodとstood upを混同しやすく、状態と動作の違いを知ると場面を正確に表せます。 / 自己評価=mid
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補の焦点は stood と stood up の意味の違いです。選定済みのKey Phrase・Wordはいずれも別の意味・用法を扱っているため、学習上の焦点は重複しません。
  - wake up: same_focus=False (目を覚ます意味・用法が焦点ではありません)
  - by the window: same_focus=False (窓のそばを表す位置が焦点ではありません)
  - take the bus: same_focus=False (バスに乗ることではなく、立っていた状態と立ち上がる動作の違いが焦点です)
  - meet: same_focus=False (人に会う意味・用法が焦点ではありません)
  - homework: same_focus=False (宿題を表す語義が焦点ではありません)
- 検討して外した候補: some tea (low_value: この文では量が不明という基本的な意味にとどまる); made toast (low_value: よくある組み合わせの紹介が中心になる)

### 6-2. v2

#### v2 / ai_island_temple Standard (ai_island_std)
- 候補: 0件。理由: 候補はありますが、基本的な表現の説明にとどまるか、この文章固有の比喩に限られます。4条件を明確に満たす解説対象はありません。
- 検討して外した候補: at least (too_basic: 基本的な限定表現で、辞書や入門教材で十分に扱われる。); Even so vs Still (too_basic: 基本的な接続表現の対比にとどまる。); too soon to wave a flag (low_value: この文脈での比喩は分かるが、一般的な使い分けとして学ぶ価値は限定的。); by themselves (low_value: 文脈上の論理は重要だが、表現自体のニュアンス解説としては学習価値が弱い。)

#### v2 / ai_island_temple Advanced (ai_island_adv)
- 表現: **at least for this AI**
- 焦点: at leastが一般化を避け、結論の適用範囲を絞る働き
- 本文引用: At least for this AI, remembering that technique helped it build towers.
- 和訳: 少なくともこのAIについては、そのテクニックを覚えていたことが塔を作る助けになった。
- 解説(166字): ここでの at least は、単に「最低限」を示すのではなく、結論を「このAIについて言える範囲」に限定しています。たとえば「この方法はAIに役立つ」と一般化するのではなく、実験で確かめられた一例にとどめる慎重な言い方です。「少なくとも」と訳せても、何の範囲を限定しているのかを見落とすと、結論を広く受け取りすぎることがあります。
- KP/Wordと焦点が異なる理由(生成時): 選定済み表現の語義や使い分けではなく、at leastが結論の適用範囲を限定する働きを扱っています。
- 価値の理由(生成時): 実験結果を述べる文章で、結論を過度に一般化しないための限定表現を読み取る力につながります。 / 自己評価=high
- criteria_check: {"context_specific": "記憶の効果を述べた直後に置かれ、このAIの結果だけから一般論を導かない含みがあります。", "jp_pitfall": "「少なくとも」という訳だけで最低条件の意味に取ると、結論の範囲を限定する働きを見落としやすいです。", "level_fit": "基本文法の対比ではなく、既知の表現が議論の確実さや範囲をどう調整するかを学べます。"}
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補の焦点は at least が結論の適用範囲を限定する働きであり、選定済み項目の意味・用法とは重複しません。
  - carry over: same_focus=False (次に持ち越す用法が焦点であり、結論の適用範囲を限定する働きとは別。)
  - call on: same_focus=False (頼むという用法が焦点であり、適用範囲の限定とは別。)
  - take a detour: same_focus=False (遠回りをするという意味が焦点であり、適用範囲の限定とは別。)
  - card to play: same_focus=False (打てる手という意味が焦点であり、適用範囲の限定とは別。)
  - obstacle: same_focus=False (障害物という語義が焦点であり、適用範囲の限定とは別。)
- 検討して外した候補: pretty tough (too_basic: prettyの程度を表す用法の説明にとどまる。); even so (too_basic: 基本的な接続表現の説明になりやすい。); one step ahead (low_value: 文脈に即した語義説明が中心になる。)

#### v2 / paycheck_personality Standard (paycheck_std)
- 表現: **was linked to**
- 焦点: 研究結果で関連を示し、原因までは断定しない表現
- 本文引用: Their study found that, within the same person, higher income was linked to greater conscientiousness later on.
- 和訳: その研究では、同じ人の中で、収入が高くなった後に、より高い誠実性が見られることに関連があると分かりました。
- 解説(184字): 研究結果の「be linked to」は、二つの事柄に関連が見られたことを述べますが、それだけで「一方がもう一方を起こした」とは言いません。本文も続けて、収入が性格を変えたとは証明できないと注意しています。原因まで述べる caused とは意味の強さが異なります。日本語の「結びついている」も原因を連想させることがあるため、ここでは「関連があった」と読むのが安全です。
- KP/Wordと焦点が異なる理由(生成時): 選定済みの「weak link」が関連の強さを扱うのに対し、ここでは関連を原因と取り違えないための表現の含みを扱います。
- 価値の理由(生成時): 「関連がある」と「原因である」を区別する力は、研究やニュースの英文を正確に読むうえで役立ちます。 / 自己評価=high
- criteria_check: {"context_specific": "この研究結果では収入と性格の関連を述べ、因果関係は証明できないという注意につながっています。", "jp_pitfall": "「関連している」や「結びついている」を、原因と結果が確定した意味に受け取りやすい点に注意できます。", "level_fit": "基礎文法の対比ではなく、研究結果を読む際に重要な表現の慎重さをA2〜B1でも学べます。"}
- 重複検査: 段1構造=fail [{"candidate_part": "was linked to", "kp": "weak link", "shared": ["link"]}] / 段2LLM=pass / 引用逐語=OK → **最終 FAIL**
  - 段2理由: 候補は関連があっても因果までは示さない点を説明しています。「weak link」は関連の弱さを表すため、学習上の焦点は異なります。
  - conscientiousness: same_focus=False (性格特性の意味が焦点で、関連と因果の区別とは異なる)
  - weak link: same_focus=False (関連の弱さが焦点で、因果関係を断定しない用法とは異なる)
  - come first: same_focus=False (出来事の順序が焦点で、関連の表現とは異なる)
  - none other than: same_focus=False (人物を強調する表現が焦点で、関連の表現とは異なる)
  - pay raise: same_focus=False (昇給の意味が焦点で、関連の表現とは異なる)
- 検討して外した候補: “Coming first” and “being the cause” are two different things. (kp_word_overlap: 「come first」の意味を扱う内容と実質的に重なるため。); The arrow does not point only one way. (low_value: この場面の比喩としては理解しやすく、独立した使い分けの学習価値は弱いため。); It was a different contest altogether. (low_value: 文脈上の言い換えとしては分かりやすく、語の選択による差を深く学ぶ価値は弱いため。)

#### v2 / paycheck_personality Advanced (paycheck_adv)
- 候補: 0件。理由: 候補表現はありますが、基礎的な語法の説明か、記事内容の理解にとどまります。4条件を明確に満たすニュアンス解説はありません。
- 検討して外した候補: may have affected both (too_basic: 助動詞mayの基本的な確信度の説明にとどまる。); a single snapshot / a series of photos (low_value: 本文の研究方法を理解する助けにはなるが、語感の差としての学習価値は限定的。); none other than you (low_value: 文脈上の強調は分かりやすく、辞書的な説明を超える差が乏しい。); the arrow doesn’t point just one way (not_nuance: 中心は研究結果の内容理解であり、表現選択の微妙な含みではない。)

#### v2 / the_tell_tale_heart Standard (tth_std)
- 表現: **You should have seen my patience**
- 焦点: 「見ておくべきだった」ではなく、すごさを誇張して伝える言い方
- 本文引用: You should have seen my patience—he never even moved!
- 和訳: 私の辛抱強さときたら、見ていたら驚いたはずだよ—彼は少しも動かなかったんだから！
- 解説(190字): ここでの You should have seen ... は、過去の義務や後悔を述べるというより、「実際に見ていたら、そのすごさが分かったのに」という誇張を込めた言い方です。単に I was very patient と言うより、聞き手にその場面を想像させ、自分の辛抱強さを印象的に語ります。should have をいつも「〜すべきだった」と訳すと、この語感を取り逃がします。
- KP/Wordと焦点が異なる理由(生成時): 選定済みの表現の語義や使い分けではなく、聞き手に向けた誇張表現の語感を扱っています。
- 価値の理由(生成時): should have の訳を一つに固定せず、話し手が聞き手に場面を想像させる働きまで理解できます。 / 自己評価=high
- criteria_check: {"context_specific": "七晩も老人の様子をうかがったことを、話し手が「見ていたら驚いただろう」と誇張して語る場面です。", "jp_pitfall": "should have を「〜すべきだった」という義務・後悔だけで捉え、ここでの誇張や聞き手への呼びかけを見落としがちです。", "level_fit": "基礎文法の対比ではなく、会話で使われる表現の含みを学べるため、A2〜B1の学習者にも有用です。"}
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補は You should have seen ... が、実際に見ていたら分かったはずだという誇張を込めて聞き手に場面を想像させる用法を解説しています。選定済みの各表現の語義・用法とは重複しません。
  - make one's blood turn cold: same_focus=False (人をぞっとさせる表現で、誇張を込めて辛抱強さを語る用法とは別です。)
  - raise one's voice: same_focus=False (声を大きくする表現で、候補の語用上の焦点とは異なります。)
  - groan: same_focus=False (うめく動作を表す語で、候補の語用上の焦点とは異なります。)
  - rush at someone: same_focus=False (人に向かって突進する動作で、候補の語用上の焦点とは異なります。)
  - go on talking: same_focus=False (話し続ける用法で、候補の語用上の焦点とは異なります。)
- 検討して外した候補: in the country (low_value: 文脈から田舎を指すと分かり、辞書で確認できる語義の違いにとどまる。); what if a neighbour heard? (too_basic: what if の基本的な用法の説明になりやすい。); Could you bear that? (low_value: この場面の効果は分かりやすく、語義の説明を超える差を示しにくい。)

#### v2 / the_tell_tale_heart Advanced (tth_adv)
- 候補: 0件。理由: 候補になりそうな表現はありますが、語義が基礎的な範囲にとどまるか、文法・構文の説明が中心になります。指定された条件をすべて満たすものはありません。
- 検討して外した候補: in the country (too_basic: countryのこの意味は辞書や基礎的な語彙解説で確認できる。); You should have seen my patience! (grammar_structure: 焦点がshould haveの構文的な解釈に寄る。); Could you have borne it? (grammar_structure: could haveの構文説明と切り分けにくい。)

#### v2 / redelivery_fee Standard (y_redelivery_std)
- 表現: **Am I wrong to feel this way?**
- 焦点: 意見をやわらげ、相手に妥当性を尋ねる語感
- 本文引用: Am I wrong to feel this way?
- 和訳: こんなふうに感じる私は間違っているのでしょうか？
- 解説(172字): ここでは、直前の「配達員は大変だと分かるが、料金を払うのは受け入れられない」という意見を撤回するのではなく、自分の感じ方が無理のないものか相手に確かめています。たとえば “I’m wrong, aren’t I?” なら「私は間違っているよね」と、間違いを前提にする響きがあります。一方、この質問は答えを開いたままにし、意見を少しやわらげます。
- KP/Wordと焦点が異なる理由(生成時): 選定済み表現の意味や使い分けではなく、意見の妥当性を尋ねる質問が会話で与える印象を扱っています。
- 価値の理由(生成時): 意見を控えめに伝える英語の言い方と、日本語の直訳から生じやすい印象のずれを学べます。 / 自己評価=high
- criteria_check: {"context_specific": "料金への反対を述べたあと、自分の感じ方が妥当かを尋ねる形で意見をやわらげています。", "jp_pitfall": "直訳だけだと、相手に「間違いかどうか」の判定を求める強い質問と受け取りやすいですが、ここでは理解や確認を求める響きがあります。", "level_fit": "疑問文の文法ではなく、意見を述べる際の会話上の含みを学べるため、A2〜B1の学習者にも有用です。"}
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補は、自分の感じ方が妥当かを尋ねることで意見をやわらげる語感が中心です。選定済みの5件はいずれも異なる語義・用法を扱っています。
  - end up getting it: same_focus=False (結局受け取るという結果を表す表現で、意見の妥当性を尋ねる語感とは別の焦点です。)
  - can't be helped: same_focus=False (避けられないことを表す表現で、意見をやわらげて相手に尋ねる用法とは別の焦点です。)
  - make an effort: same_focus=False (努力することを表す表現で、候補の焦点とは別です。)
  - in person: same_focus=False (直接会う・行うことを表す表現で、候補の焦点とは別です。)
  - encourage(本文中の形: encourages): same_focus=False (促すことを表す語で、候補の焦点とは別です。)
- 検討して外した候補: I guess it can’t be helped (kp_word_overlap: 中心となる「can’t be helped」が選定済みKey Phraseと重なるため。)

#### v2 / redelivery_fee Advanced (y_redelivery_adv)
- 表現: **I guess it can’t be helped**
- 焦点: 仕方ないという諦めを示しつつ、賛成とは限らない語感
- 本文引用: The delivery workers must have a hard time because there aren’t enough of them, and I guess it can’t be helped. But I can’t accept having to pay for that.
- 和訳: 配達員は人手不足で大変でしょうし、仕方ないのだろうと思います。でも、そのために料金を払わなければならないのは受け入れられません。
- 解説(177字): ここでの “I guess it can’t be helped” は、人手不足を「仕方ない」としぶしぶ認める響きです。問題をよいことだと評価したり、何でも受け入れたりしているわけではありません。続く “But I can’t accept …” と対比され、配達員の苦労には理解を示しながら、再配達料を受け取る側に負担させることには反対だと伝わります。
- KP/Wordと焦点が異なる理由(生成時): 選定済み表現の意味や類義語ではなく、不可避だと認める言い方と、そのことへの賛成との違いが焦点です。
- 価値の理由(生成時): 訳語だけでは見落としやすい「諦めて認めること」と「賛成すること」の違いを、発言の流れに沿って学べます。 / 自己評価=high
- criteria_check: {"context_specific": "話者は人手不足を避けがたいと認めますが、その費用負担には同意していません。", "jp_pitfall": "「仕方ない」を全面的な同意や、話題を終わらせる表現として受け取りやすい点に注意が必要です。", "level_fit": "句全体の諦めの含みと文脈での働きは、基礎文法の対比ではなくB1〜B2で学ぶ価値があります。"}
- 重複検査: 段1構造=pass / 段2LLM=pass / 引用逐語=OK → **最終 PASS**
  - 段2理由: 候補は「仕方ない」としぶしぶ認めつつ、必ずしも賛成ではないという語感を説明しています。選定済みの表現はいずれも別の語義・用法が焦点です。
  - doesn't sit right with someone: same_focus=False (しっくりこない感覚ではなく、仕方ないと認めつつ賛成とは限らない語感が焦点。)
  - take the trouble to: same_focus=False (わざわざ何かをすることではなく、諦めを含む受け止め方が焦点。)
  - end up receiving: same_focus=False (最終的に受け取ることではなく、仕方ないという認識と賛否の違いが焦点。)
  - beforehand: same_focus=False (時間的に前もって行うことではなく、諦めを含む語感が焦点。)
  - repeatedly: same_focus=False (何度も繰り返すことではなく、仕方ないという受け止め方が焦点。)
- 検討して外した候補: on top of (too_basic: 「〜に加えて」という基本的な意味の説明にとどまる。); must have a hard time (grammar_structure: 主な焦点が助動詞による推量の仕組みになる。); Am I wrong to feel this way? (low_value: この場面では話者の気持ちの解釈が中心になり、語句の選択による差を十分に扱いにくい。)

#### v2 / synthetic_control Standard (control_trivial)
- 候補: 0件。理由: 本文の表現には文脈に沿った読み取りが必要なものもありますが、辞書的な意味や基本的な語の理解を超える学習価値の高いニュアンスは見当たりません。
- 検討して外した候補: stood (too_basic: 文脈から分かる基本的な動詞の意味の区別です。); full (too_basic: 基本語の語義説明にとどまります。)


## 7. 費用(円@160。呼出ごとの記録=`usage_log_01.jsonl`)

| tag | 入力tok | 出力tok | 推論tok | 秒 | 円 |
|---|---|---|---|---|---|
| v1_ai_island_std_gen | 1990 | 632 | 314 | 7.0 | 0.0824 |
| v1_tth_std_gen | 2014 | 922 | 516 | 10.9 | 0.1060 |
| v1_paycheck_std_gen | 1937 | 980 | 573 | 11.0 | 0.1094 |
| v1_ai_island_std_judge | 651 | 360 | 25 | 4.2 | 0.0392 |
| v1_y_redelivery_adv_gen | 2254 | 948 | 516 | 11.6 | 0.1119 |
| v1_ai_island_adv_gen | 2018 | 1059 | 621 | 12.5 | 0.1170 |
| v1_tth_std_judge | 703 | 378 | 37 | 4.2 | 0.0415 |
| v1_y_redelivery_adv_judge | 655 | 340 | 26 | 3.9 | 0.0377 |
| v1_paycheck_std_judge | 656 | 325 | 59 | 4.6 | 0.0365 |
| v1_ai_island_adv_judge | 675 | 369 | 27 | 4.3 | 0.0403 |
| v1_y_redelivery_std_gen | 2206 | 1373 | 905 | 17.2 | 0.1451 |
| v1_paycheck_adv_gen | 1951 | 1630 | 1282 | 19.0 | 0.1616 |
| v1_tth_adv_gen | 2008 | 1735 | 1327 | 20.1 | 0.1709 |
| v1_y_redelivery_std_judge | 637 | 347 | 31 | 4.1 | 0.0380 |
| v1_paycheck_adv_judge | 673 | 341 | 34 | 3.7 | 0.0380 |
| v1_tth_adv_judge | 670 | 339 | 31 | 3.7 | 0.0378 |
| v1_control_trivial_gen | 1519 | 938 | 516 | 9.8 | 0.0993 |
| v1_control_trivial_judge | 645 | 309 | 48 | 3.9 | 0.0350 |
| v2_control_trivial_gen | 2002 | 732 | 516 | 9.8 | 0.0906 |
| v2_paycheck_adv_gen | 2434 | 1215 | 819 | 11.0 | 0.1361 |
| v2_ai_island_std_gen | 2473 | 1007 | 625 | 12.1 | 0.1201 |
| v2_ai_island_adv_gen | 2501 | 1207 | 516 | 12.4 | 0.1366 |
| v2_tth_std_gen | 2497 | 2091 | 1334 | 14.9 | 0.2072 |
| v2_tth_adv_gen | 2491 | 1191 | 882 | 15.0 | 0.1351 |
| v2_ai_island_adv_judge | 689 | 318 | 29 | 3.5 | 0.0365 |
| v2_y_redelivery_std_gen | 2689 | 1754 | 1171 | 16.7 | 0.1833 |
| v2_y_redelivery_adv_gen | 2737 | 1667 | 902 | 16.8 | 0.1772 |
| v2_tth_std_judge | 723 | 388 | 28 | 4.2 | 0.0426 |
| v2_y_redelivery_adv_judge | 700 | 388 | 32 | 3.9 | 0.0422 |
| v2_y_redelivery_std_judge | 668 | 355 | 34 | 4.1 | 0.0391 |
| v2_paycheck_std_gen | 2420 | 1956 | 1197 | 20.8 | 0.1952 |
| v2_paycheck_std_judge | 678 | 844 | 576 | 10.0 | 0.0784 |
| probe_probe_overlap_synonym_judge | 652 | 538 | 282 | 5.7 | 0.0535 |
| probe_probe_overlap_same_idiom_other_form_judge | 687 | 352 | 51 | 4.8 | 0.0392 |
| probe_probe_non_overlap_judge | 602 | 274 | 29 | 2.8 | 0.0316 |

合計 ¥3.1921 / 上限 ¥10。内訳: v1実8 ¥1.3133、v1 control ¥0.1343、v2実8 ¥1.5296、v2 control ¥0.0906、judge probe ¥0.1243。呼出数35、全call `status=completed`、`model_actual=gpt-6-luna`、retryなし、エラー0。

## 8. 成果物・再現
- 本書、`prompt_trial_01.json`(スキーマ: `WIRING_DESIGN_01.md` §3 `nuance_candidate_v1` に準拠。追加フィールドは`trial_extra`のみ=`rejected_candidates`/`worker_value_assessment`/`model_self_rating`/`criteria_check`/`quote_verbatim`/`rejected_candidate_audit`)、`results_v1.json`/`results_v1_control.json`/`results_v2.json`/`judge_probe_01.json`(生出力・usage全文)、`raw/`(各callの原文)、`usage_log_01.jsonl`、`stop_check_01b*.json`。
- script: `tools/nuance_trial_01.py`(対象読込・Prompt v1・重複検査・費用ガード)、`tools/nuance_prompt_v2.py`、`tools/build_report_01.py`、`tools/assemble_md_01.py`。
- 実行: `py -3 nuance_trial_01.py dry-run`(API 0)、`NUANCE_TRIAL_PAID=1 py -3 nuance_trial_01.py gen v1|v2 [target...]`。Production・Prompt・既存出力は未変更。
