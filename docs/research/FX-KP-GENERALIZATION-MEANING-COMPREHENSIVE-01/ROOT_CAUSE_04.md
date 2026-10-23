# ROOT_CAUSE_04: 課題① 日本語意味の字義訳 — 原因究明のやり直し(委任_21、2026-10-24、API 0・Production変更0・SSOT編集なし)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_21 / 根拠=ユーザー決定(2026-10-24、委任文§0・§Z) / 前版=`ROOT_CAUSE_03.md`(B節)・`ROOT_CAUSE_02.md`
範囲: 既存データの再集計+Prompt組立関数のローカル呼出のみ(API 0)。再現script=`er112_output/kp_gm_design_07/`(`prompt_dump.py`・`ng_context_dump.py`・`hardcore_arm_table.py`・`canon_reasoning_census.py`・`cp_vs_b0.py`)。コード行は**HEAD(c7a43c8f3)基準**(作業ツリーは並行の課題②配線で`er003_key_words_gloss_alignment.py`等が編集中のため行番号がずれる。`git show HEAD:<file>`で確認可)。
前提の訂正(FABLE_VERIFICATION_02): `reach for someone's wallet`・`apply one's findings`は見出し語placeholderの問題で字義訳NGではない(本書の字義訳集計から除外し別掲)。

## 0-R. 【改訂(委任_22、2026-10-24)OPUS_REVIEW_07 OF-KP1-01の反映 + Fable裁定】 以下の§0〜§6の記述のうち、この節と矛盾する部分はこの節が優先する

原文の§0〜§6は逐語を残す(履歴)。結論の文言のみ次のとおり改訂する(根拠=`OPUS_REVIEW_07.md`論点1、Fable裁定=委任_22 §0)。

| 項目 | 旧(§0) | 改訂後 |
|---|---|---|
| 主因 | H5(gloss callの文脈限定句)が主因 | **主因=gloss callに『本文での意味を確定する段』が無い**(翻訳モードでglossを直接1本書く形。H4+H10の統合)。根拠: 意味の計算を強いたarm(G2/G3/Cp/C)は、制約句の有無と無関係に効いた。 |
| H5(文脈限定句) | 主因(確度高) | **増悪因子(未検証)**。反証: (1)Cpは制約句を含む現行messageのまま(`er112_kp_gm_trial_04_gen.py` l.115-121、`CP_BLOCK`を差し込むだけ)で hard-core 0/4・F層FAIL 0/41、(2)G3は制約句不変で0/7、G2は制約句をむしろ強化して1/7、(3)Mは制約句を残しても `greener grass` 0/2・trophy 1/2。制約句は字義訳の**必要条件ではない**。X1(M対X1)で検証する。事前の期待は下げる。 |
| 性質の表現 | 『確率的ではなく決定論的』 | **特定の型に集中する高確率の失敗。promptの揺れにも敏感**。型=『具体名詞を含み、字義どおり読んでも文法が通り、直訳した日本語では比喩の意味が運ばれない、新造または断片化した比喩』。各KP 2rep(+Production artifact)ではp=0.7とp=1.0を区別できない。Mのchurn(出力がB0から入れ替わる)も確率性を示す。 |
| 暴露の上流原因(追記) | (なし) | 選定の規則5(字面で分かる表現を除外)が再利用性の低い新造比喩(`question shaped like a trophy`、`an unseen clock`)を選ばせ、規則3が慣用句を断片化させる(`greener`)。これがリスクの母数を作る。 |
| few-shot例(追記・原因候補) | (なし) | 現行の判定参考例『key_phrase「fall into」にcurrent「～に落ちる」: 意味は表れているので一致です(「～に陥る」へ書き換えません)』(`er003_key_words_gloss_alignment.py` `build_user_message_corrected`)は、**字義寄りの訳を手本として示している**。M-baseは再整合用の指示と共に除くため新規生成では除かれるが、Production現行のB0には含まれる=原因候補として記録(新造比喩のような字義訳との因果は未検証)。 |
| Cpの機序(追記・未確認) | 『gloss後の欄は影響しない構造のため機序不明』 | effort=highの推論モデルは出力前の隠れた推論で全欄を計画する。『Cpの欄はglossの後だから影響しない』という前提は成り立たない。reasoning_tokensによる確認を試みた結果は`TRIAL_05/REASONING_TOKENS_01.md`(既存ledgerにはluna gen行のreasoning_tokensが**未記録**のため、新規実行から計測)。 |
| 設計意図のトレードオフ(追記) | (なし) | 『key_phrase単体で再利用できる訳』と新造比喩の訳は原理的に両立しない(新造比喩に再利用できる訳は存在しない)。gold(字義訳=FAIL)は『本文での意味』側のユーザー水準を示している。ただしこの原則の変更は承認事項として明示する(`DESIGN_07.md` §5 (1))。 |
| 『確率的で済ませない』への回答 | 決定論的 | 型の特定(上の『型』)で応える。決定論と断定しない。 |

## 0. 結論(先頭)

「LLMが確率的に字義訳を選ぶ」は**誤り**である。実データでは、字義訳NGは**ごく少数のKP(4個)に集中し、現行Promptでは3個がほぼ決定論的に字義訳になる**(G0/B0出力: `an unseen clock` 2/2、`greener grass` 2/2、`question shaped like a trophy` 2/2、`draw a line`のみ確率的で2/5。4KP合計 8/11=73%)。それ以外のF層KP(比喩・慣用37個)は現行Promptで字義訳0。つまり「全体の1〜3%がランダムに外れる」のではなく、**特定の型のKPがPrompt構造の下で系統的に外れる**。系統的な失敗はPrompt/構造に原因がある。

| # | 問い | 結論(1行) | 確度 | 主な証拠 |
|---|---|---|---|---|
| 1 | なぜ文脈から意味を取れず字義訳を選ぶか | gloss生成Promptが**文脈を『語義選択専用』『他文脈でも再利用できる訳』に限定**し、文脈に依存して意味が決まる比喩(新造比喩・断片化した慣用)では**文脈を使わない辞書訳(=字義訳)が指示どおりの出力になる**。この制約句は過去の全arm(G0〜G3・M・C・Cp)で不変だった | 中〜高(原因の構造は確認。因果の直接検証は次Trial X1) | §2-1、HEAD:`er003_key_words_gloss_alignment.py:309,320,603` |
| 2 | Key Phrase選定時点で意味・文脈が失われているか | **失われている**。選定の出力は`phrase`と`word_count`のみ(用法・意味メモ無し)。さらに選定Promptの「最小化」規則で慣用の手がかりが落ちる(`greener grass`は選定が`greener`1語に縮約→canonicalizationが`grass`を復元)。canonicalizationの`reasoning`は『比喩的な意味』『負担を担う』と**意味を認識している例があるのに、gloss段へ渡されない** | 高(file:lineと実artifactで確認) | §2-2 |
| 3 | 意味生成Promptへの入力は十分か | **量は十分、使い方の指示が逆**。見出し語・元の見出し・source_sentence(1文、断片化あり)に加え**記事全文が末尾に『(参考)』で付く**。一方、指示は「source_sentenceは辞書の複数語義から選ぶためだけに使う」「本文固有の文脈の追加はしない」 | 高 | §2-3 |
| 4 | 解釈と日本語化の同時実行が原因か | **必要条件の一部だが十分ではない**。解釈を先に書かせると新造比喩(`an unseen clock`)は4/4直る一方、解釈が正しくても日本語化で字義訳が出る例がある(G2 `draw a line`: core_sense=『区別をはっきりさせる』で正解、gloss=『はっきりと線を引く』)。**日本語化の段にも『字義の像が日本語読者に意味を運ぶか』の判断が要る** | 中〜高 | §2-4 |
| 5 | 過去のPrompt改善Trialが効かなかった理由 | (a)**効かなかったのは『言い回しだけを変えたarm』(G1・M)**。(b)**処理を変えたarm(G2・G3・Cp・C)は対象KPで効いていた**(字義訳 G0/B0 8/11 → G3 0/7、Cp 0/4、C 0/5)。(c)それが『効かない』と評価されたのは、評価が**全体の1〜3%という希釈された率**と**副作用(薄い△・説明文化)・検出器指標(recall/precision)**で行われたため。(d)どのarmも『文脈限定句』『単一の日本語glossを翻訳モードで書く』という前提を変えていない | 中〜高 | §2-5 |
| 6 | NGに共通する構造・条件 | 4KP共通: (i)**具体名詞を含む名詞句/動詞句で、字義読みが文法的に成立**、(ii)**字義の日本語訳(calque)が比喩の意味を運ばない**(「時計」「トロフィーの形」「青々とした芝生」「線を引く」)、(iii)**比喩の意味は同文では暗示的で、隣接文(直前/直後)に説明がある**、(iv)新造比喩2・慣用の断片/拡張2。比喩が日本語でも通じる慣用(光を当てる・舞台裏・ハンドルを握る・ひっくり返す)は字義訳でも正解になるため外れない | 高(4KP+周辺KP全数) | §3 |
| 7 | 変更が有効な工程 | 費用対効果の順に **(1)gloss生成call内(入力の使い方の指示+解釈を先に書く欄+字義の日本語が像だけを運ぶかの判定欄)** → (2)canonicalizationの意味所見をhintとして渡す(call 0、副作用に注意) → (3)選定(Prompt 2は逐語固定・ユーザー承認事項、波及大) → (4)事後検査(ユーザーが現段階不採用)。**追加callなしで済む工程は(1)** | 中(根拠は既存データ、(1)の効果はTrialで検証) | §5、`DESIGN_07.md` |

**重要な再評価**: Trial_04の**Cp(gloss callに自己監査欄を足した生成arm)**は、検出器としてはrecall 0で不採用になったが、**生成方式として見ると全arm中で最良**だった(F層41KP: FAIL 0、B0は7、Cは3。hard-core 4KPの字義訳0/4)。検出に失敗したのは『gloss確定後に自分のglossを評価した』からで、生成そのものは**欄の存在がモデルに意味の同定を促した**可能性が高い(§2-5)。これを生成方式として再評価し、費用(+0.12円/call)と薄い出力(THIN 2/61)を下げる設計が`DESIGN_07.md`の推奨案。

## 1. 工程ごとの意味の流れ(実Prompt・実artifactで確認)

| 段 | 入力 | 出力にある意味情報 | file:line(HEAD) |
|---|---|---|---|
| 選定 | 記事全文+Prompt 2(ユーザー逐語固定、sha固定) | **`phrase`,`word_count`のみ**。用法・意味・比喩/字義の別なし | `er105_kp_fulltext_selector_01.py:51-71`(Prompt)、`:74-92`(schema、`:85`) |
| canonicalization | 記事全文+候補(source_span,source_sentence) | 形の正規化+QA11本+**`reasoning`(日本語1〜2文の自由記述)**。意味欄は無いが`reasoning`に比喩・慣用の認識が現れる | `b1_p2_keywords_canonicalization_fulltext_prompt_template.txt`、`er003_key_words_canonicalization.py:123-137` |
| gloss | key_phrase・元の見出し・source_sentence・added_content_words(人称token)+記事全文(参考) | **`japanese_gloss`(1本)**。schema順は rank→current_gloss_consistent→**japanese_gloss**→qa→**reasoning**(reasoningはgloss確定後) | `er003_key_words_gloss_alignment.py:79-114`(DEVELOPER・schema)、`:549-606`(message)、`:382-`(effort=high、1call=最大3KP) |
| Adv説明(b1bのみ) | phrase・source_sentence・**gloss(参考)** | 英語1文 | `er019_family_x_kp_explanation_01.py:54-85,164-178`(effort medium) |
| 検査 | — | 意味の正否・字義/慣用の検査は**無い**(qa自己申告・括弧・数字・人称のみ) | `ROOT_CAUSE_02.md` §2 |

ローカル再構成の検証(`prompt_dump.py`): 保存済みProduction artifact(`uk_train_speaker_playback__run_nws_02/a2/key_phrases/gloss_alignment_prompt.txt`)と`build_user_message_corrected`の出力は、**数値補完句1段落(`include_numeric_rule=True`の差)を除いて一致**。したがってDEV TrialのPromptはProductionと同じ構造である。NG KPの実message(3件)=`er112_output/kp_gm_design_07/prompt_dump_gloss_ngkp.txt`。

## 2. 7点への回答と証拠

### 2-1. なぜ文脈から適切な意味を取らず字義訳を選ぶか(要求1)
**実Promptの指示(引用、HEAD)**:
- `er003_key_words_gloss_alignment.py:603`(全項目共通の見出し): 「key_phrase単体で**他の文脈でも再利用できる自然な訳**にし、**本文固有の固有名詞・文脈の追加はしないでください**。」
- `:320`(新規生成の規則、fulltext由来の全項目): 「source_sentenceは、**辞書に複数の語義がある表現で、そのうちどの語義かを選ぶためだけに使ってください**(文中の固有名詞・文脈の追加はしないでください)。」
- `:309`(人称の規則): 「source_sentenceは…**語義を選ぶためだけに使い、人称の指示対象を決めるためには使わないでください**。」
- 承認済みgloss規則(`b1_p2_keywords_l_prompt_template.txt:19`): 「直訳調…は避けてください」(抑止はこの1句だけ。字義/慣用を先に決める手順は無い)。

→ gloss段のタスクは『文脈に依存しない辞書訳を書く』と定義されている。`an unseen clock`は筆者が作った比喩で辞書義が無く、文脈を使わない訳は『目に見えない時計』になるしかない(**指示どおりの出力**)。`question shaped like a trophy`・`greener grass`(ことわざの断片)も同様。文脈で意味が決まるKPに対して文脈の使用を禁じていることが、系統的な字義訳の直接の構造原因と推定する。

**反証可能な予測**: この制約句を『この表現が本文のこの箇所で実際に表す意味を、記事固有の固有名詞・数値を除いて書く』へ替えると、hard-core 4KPの字義訳が減る(`DESIGN_07.md`のX1)。**注意**: これは未検証。過去のM arm(再整合用の指示を除いたmessage)はこの句を残しており(`er112_kp_gm_trial_04_gen.py` の`M_HEAD`)、Mで字義訳が減らなかったことはこの仮説と矛盾しない。

**傍証(C再生成)**: Trial_04のCは、flag項目だけに『日本語意味だけを読むと『{字義の像}』の意味に取れ、本文での意味『{usage_meaning_en}』を伝えていない。本文での意味を日本語で表す』(`er112_kp_gm_trial_04_c.py` の`reason_text`)を与えて再生成し、字義訳を5/6直した。**同じモデルに『本文での意味』と『字義の像』を明示すれば直せる=能力の問題ではなく、デフォルトの動かし方の問題**。モデル差も小さい(Trial_02: gpt-6.1-sol G0 10/12 ≒ luna G0 9/12、`TRIAL_RESULT_02.md` 結論2)。

### 2-2. Key Phrase選定時点で意味・文脈が失われているか(要求2)
1. **選定出力に用法・意味が無い**: `SELECTOR_JSON_SCHEMA`は`phrase`と`word_count`のみ(`er105:85`)。選定結果は`japanese_gloss: None`の項目に変換される(`:281`、コメント「Prompt 2は意味を出力しない」)。Prompt 2はユーザー逐語固定(sha固定)。
2. **選定の規則が慣用の手がかりを削る**: 規則3『最小化…不要な目的語・修飾語・文脈は除く』(`er105:58-59`)。実例=`greener grass`: 本文は`your neighbor's greener grass`だが、選定は`greener`の**1語**(`source_span='greener'`)を選び、canonicalizationが`restore_semantic_complement`で`grass`を復元して`greener grass`にした(`paycheck_personality__run_pp_01/a2/key_phrases/keywords_canonicalized.json`、reasoning『比喩的な表現としても不十分です。source_spanから「grass」を復元』)。ことわざ`the grass is greener`の想起手がかり(`neighbor's`)が見出し語から落ち、glossは『もっと青々とした芝生』になった(Production artifact実在)。また規則5は『字面どおりに意味が分かる表現を除外』する=**比喩・慣用が選ばれやすい構造**(字義訳リスクに常にさらされる)。F層は115KP中41個(36%)。
3. **canonicalizationは意味を認識しているが渡さない**: `reasoning`が比喩・慣用を述べる項目は260 unique項目中36(13.8%、`canon_reasoning_census.py`)。NG KPの実例(Production artifact): `an unseen clock`『…**比喩的な意味も保たれる**ため変更しません』(gloss=『目に見えない時計』)、`question shaped like a trophy`『…**という比喩を含む**自然な句』(gloss=『トロフィーの形をした問い』)、`Carry the Load`『…**「負担を担う」という意味**で単独でも自然な表現』(gloss=『荷物を運ぶ』)。**認識した意味・用法はglossの入力に載らない**(gloss message項目dict `:554-560`は固定キーでreasoningを含まない)。

→ 要求2への回答: **失われている(選定出力に無い/最小化で手がかりが落ちる/canonicalizationの所見が捨てられる)**。ただし意味情報は記事全文から**いつでも再取得できる**(全文はgloss callに渡っている)ため、情報の欠落は『必要条件』であって『十分原因』ではない(2-3、2-5)。

### 2-3. 意味生成Promptへの入力は十分か(要求3)
実際の入力(NG KP `an unseen clock`の実message抜粋、`prompt_dump_gloss_ngkp.txt`):
```
【対象項目】 [{"rank":1,"key_phrase":"an unseen clock","display_phrase_before_canonicalization":"an unseen clock",
  "current_japanese_gloss":null,"source_sentence":"A coffee price tag may have an unseen clock of its own, separate from the latest news about the market",
  "added_content_words":[]}]
【記事本文(参考)】 (記事全文 約2,600字)
```
- 見出し語・元の見出し・source_sentence・記事全文は**ある**。選定時の意味メモ・段落・canonicalizationの所見は**ない**。
- source_sentenceは文分割の都合で断片化することがある(`The words draw that line simply`、`Here's news about this kind of "sound no one asked for`)。比喩の説明は多くが**隣接文**にある(§3)。記事全文は末尾で『(参考)』と呼ばれ、使い方の指示は2-1の制約。
- 先頭の『1. current_japanese_glossが…一致しているか判定』『判定の参考例(based on…)』等は**既存glossの再整合用の指示**で、新規生成(current=null)では無関係。Trial_04のM armはこの部分を除き、**費用が0.061→0.038円/callに下がった**(入力2,244→1,329 token)=字義訳は減らないが原価は下がる副次知見。
- 結論: **量は十分。ただし文脈を『使うな』と指示している**。要求3の答え=不足ではなく、使い方が間違っている。

### 2-4. 解釈と日本語化が1回で行われることが原因か(要求4)
- 現行は1 call(effort high、隠れた推論あり)で、visibleな出力は`japanese_gloss`のみ(その後に`reasoning`)。**『意味の同定』が出力として現れない**。
- 解釈を先に書かせたarmの実測(hard-core、字義訳数/出力数):

  | arm | 変えたもの | draw a line | unseen clock | trophy | greener | 計 |
  |---|---|---|---|---|---|---|
  | G0/B0(現行) | — | 2/5 | 2/2 | 2/2 | 2/2 | **8/11** |
  | G2 | usage→core_sense_en→gloss(可視欄を先に) | 1/5 | 0/2 | 未実施 | 未実施 | 1/7 |
  | G3 | 日本語案2〜3→選択(認識で選ぶ) | 0/5 | 0/2 | 未実施 | 未実施 | **0/7**(`unseen clock`のrep1は字義案『目に見えない時計』を案に挙げて選ばなかった) |
  | Cp | 自己監査欄(出力はgloss後、promptにはgloss前から記載) | 0/1(THIN) | 0/1 | 0/1 | 0/1 | **0/4** |
  | C | 独立検査→flag項目のみ再生成 | (未flag) | 0/2 | 0/1(+語義誤認1) | 0/2 | 0/5 |
  | M | 再整合指示を除く(制約句は残す) | 1/2 | 2/2 | 1/2 | 0/2 | 4/8 |
  | Sol G0 / G2 | モデル | 0/3 / 0/3 | | | | draw a lineのみ |

  (`hardcore_arm_table.py`で再現。注意: これら4KPは字義訳が出たために選ばれた**事後層別**で、G0/B0の率は選択バイアスで過大。次Trialでは新規repで対照を取る。Fisher(片側)G0+B0 8/11 対 G3 0/7 p=0.004、対 Cp 0/4 p=0.026、対 G2 1/7 p=0.025 [探索的])
- **解釈が正しくても日本語化で外れる例**: Trial_03 G2 rep2 `draw a line`: usage_type=figurative、core_sense=『To make a clear distinction between things.』(正解)なのにgloss=『**はっきりと線を引く**』(字義訳)。→ 『解釈→日本語化』を分けるだけでは、日本語化段で字義の像(calque)に戻ることがある。日本語化の段で『このまま日本語に置き換えると意味が運ばれるか』を見る必要がある(G3が案を並べて選ぶ方式で0/7なのは、認識(判別)が生成より易しいため。unseen clockのG3 rep1は字義案を挙げながら選ばなかった)。
- **解釈の質を測る別の根拠**: 独立検査(V2)は`usage_meaning_en`で本文の意味を正しく言語化(例 `an unseen clock`→『The label may follow its own hidden timing process, separate from current market news.』)し、`gloss_alone_reading_en`で『A timekeeping device that cannot be seen.』と字義像を言語化してflagできた(`er112_output/kp_gm_trial_04/inspect_main.jsonl`)。**解釈も字義像の言語化もモデルには可能**。
- 結論: 要求4への答え=『同時実行』は寄与するが主因ではなく単独では十分条件でない。**解釈(本文の意味)と、字義の日本語が運ぶ像の判定、の2点を、gloss確定の前に明示させる**構造が必要。

### 2-5. 過去のPrompt改善Trialが効かなかった本質的な理由(要求5)

**各armが変えたもの/変えなかったもの**(○=変えた、×=変えない/同じ):

| arm | 内容 | 文脈限定句(2-1)を変えたか | 解釈の可視化(gloss前) | 字義像の判定 | 日本語案の比較 | 追加call | 結果(hard-core 字義訳 / 全体) |
|---|---|---|---|---|---|---|---|
| G0/B0 | 現行 | × | × | × | × | 0 | 8/11 / F層82出力中FAIL_LIT 6 |
| G1(probe-03) | 「全語反映」句の除去 | × | × | × | × | 0 | 変化なし(NG 3/14) |
| G2 | 用法先決め+core_sense_en(一般化) | **強化**(『記事固有を入れず別の場面でも通用する形に』) | ○(ただし一般化した中心義) | × | × | 0 | 1/7、薄い△3、説明文化(標準偏差) |
| G3 | 辞書定訳→慣用句→言い換えの順に2〜3案→1つ選ぶ | × | × | ○(案を並べて選ぶ) | ○ | 0 | 0/7、薄い△4(『聞いてすぐ分かる』基準でterm/定訳が説明文化) |
| Sol | モデルをSolに | × | × | × | × | 0 | 変化なし(10/12≒9/12) |
| M | 再整合指示を除く | ×(制約句は**残す**) | × | × | × | 0 | 4/8、字義訳の顔ぶれが入れ替わる(churn 62%) |
| C | 独立検査→flagのみ再生成 | (再生成時に『本文での意味』を明示) | ○(検査側) | ○(検査側) | × | **+1** | 0/5、precision 5/19=26%(FP14) |
| Cp | 自己監査欄(`usage_meaning_en`,`gloss_alone_reading_en`,`gloss_conveys`) | × | ○(欄がpromptにある。出力はgloss後) | ○(同上) | × | 0 | **0/4**(F層41KP FAIL 0)、検出器としてはflag 0/61 |

**本質的理由**:
1. **効かなかったのは『言い回しだけを変えたarm』(G1・M)に限る**。G2・G3・Cp・Cは、対象KPの字義訳を実際に減らしていた(8/11 → 0〜1/7)。
2. それが『効果なし』とされた理由は評価にある。(a)対象KPは全体の数%で、全体率(1〜3%)に希釈される。(b)G2・G3は対象KPを直した一方、対象外のKP(term・定訳のあるKP)を**説明文化・薄化**して△を出した(例: 標準偏差→『データのばらつき具合を表す値』、値札→『値札に表示された価格』、reach for someone's wallet→『人が支払いを覚悟する』)。原因は『全KPに一律に』解釈→言い換えを課した構造と、G2の『一般化した中心義』・G3の『聞いてすぐ分かる』基準にある。(c)Cpは『検出器』の指標(recall)で評価され、『生成方式』としての優位は見られなかった(§0)。
3. **全armが共通して変えなかったもの**: (i)文脈を語義選択専用とする制約句、(ii)gloss=単一の日本語phraseを『翻訳モード』で出すタスク構造、(iii)対象KPが稀で、事前に層別されず検出力が不足する評価設計(Trial_04で初めて事前層別)。
4. 同じ『語彙既定に戻る』現象は`take the wheel`(『ハンドルを握る』/『車を運転する』、goldは許容)等のgold曖昧KPでも見られ、**『本文での意味に寄せる』と『定訳を守る』の2方向のトレードオフ**を持つ。一律の言い換え強制(G2)はこのトレードオフで悪化する。**必要なのは『字義の日本語が運ぶ像で意味が伝わる場合は現行どおり、伝わらない場合だけ意味に寄せる』という条件付き構造**。

## 3. 字義訳NGの発生事例(要求6)― Trial_02〜04の全NG(△含む)を1表

判定者: Trial_02=Opus確定gold(`TRIAL_02/GOLD_LABELS_FINAL_01.md`)、Trial_03=Fable盲検(`TRIAL_03/FABLE_BLIND_RESULT_03.md`、`AUDIT_01/FABLE_VERIFICATION_01/02.md`)、Trial_04=Fable盲検(`TRIAL_04/FABLE_BLIND_RESULT_04.md`)。出力はarm/rep。model=gpt-6-luna(特記なし)。

### 3-1 字義訳NG(FAIL_LIT)と同KPの周辺

| KP(Production実形) | 見出し語の型 | 比喩 | 字義の日本語が運ぶか | 本文での説明の位置 | NG出力(arm/rep) | 同KPの非NG | Adv(同KP、gloss入力下) |
|---|---|---|---|---|---|---|---|
| `draw a line`(Prod: `draw that line`) | 動詞句(V+限定詞+具体名詞) | 慣用の拡張用法(指示語`that`+『The words draw that line simply』) | 『線を引く』は図形を描く動作で、『一線を引く』は慣用。**同形で分岐** | 同文は短く、前文『Share the journey, not the noise』・後文『It's more like saying "Choose who hears the sound."』に説明 | 『線を引く』T02 G0 r1,r3 / 『はっきりと線を引く』T03 G2 r2 / 『線を引く』T04 M r2。Production artifact『その線を引く』『その境界線を引く』(nws_02 a2/b1b) | 『一線を引く』T02 G0 r2・T03 G0×2、G3 5/5、Sol 3/3、『区別する』Cp(THIN) | E0@G0 3/3 sense OK(gloss=『線を引く』でも) |
| `an unseen clock` | 名詞句 | **新造**(辞書に無い) | 『時計』は時間管理の器具の像のみ。比喩(隠れた時間の周期)は運ばない | 同文『…of its own, separate from the latest news about the market』は暗示的。意味は次の節(『nine months to affect US retail prices』)側 | 『目に見えない時計』T03 G0 r1,r2、T04 M r2 / 『見えない時計』T04 M r1。Production artifact(coffee_prices run_jre_01 outer_retry attempt_1)あり | G2/G3 4/4、Cp、C『目に見えない時間の流れ』(Fable盲検でPASS) | E0@G0『a hidden sense of time that affects when something happens or changes』sense OK |
| `question shaped like a trophy` | 名詞句 | **新造** | 『トロフィーの形をした問い』は形の像のみ。比喩=『賞という形で投げかける問い』は運ばない | 前文『They create one prize and ask the others, "So, what would you do?"』=賞が『他の賞への問い』という説明が**直前**に | 『トロフィーの形をした質問/問い/問いかけ』B0 r1,r2、M r2、C r1(未修復)/ FAIL(語義誤認)『成果や地位を誇示するような問い』C r2。Production artifact『トロフィーの形をした問い』(prix_pascal run_nws_01 a2) | M r1『賞を通じて投げかける問い』、Cp『賞という形で投げかける問い』 | E0@prod 『A question whose outline looks like a trophy.』(**Advも字義**、gloss入力の伝染) |
| `greener grass` | 名詞句(ことわざ`the grass is greener`の断片) | 慣用の断片(選定が`greener`1語に縮約、canonicalizationが`grass`を復元。`neighbor's`が落ちた) | 『青々とした芝生』=植物の像のみ。日本語のことわざは『隣の芝生は青い』で、断片からは想起されない | 同文『putting down binoculars you use to look at your neighbor's greener grass』に比喩が直接あり、前文『stopped comparing people with others』が説明 | 『より青々とした芝生』B0 r1,r2 / Production artifact『もっと青々とした芝生』(pp_01 a2) | M『自分より恵まれて見える人の暮らし』等、C、Cp | E0@prod『something that seems better or more attractive than what you have』sense OK |

### 3-2 その他のNG・△(字義訳以外)

| KP | 出力(arm/rep) | 判定 | 構造 |
|---|---|---|---|
| `settle at` | 『～で落ち着く』T03 G0 r2 | △(市場用語『取引を終える』が落ちる。FABLE_VERIFICATION_01で△に確定) | 語義選択(term)。字義ではなく一般義への後退 |
| `Carry the Load` | 『荷物を運ぶ』G0/G2全arm(gold=許容。比喩含意があれば上位) | 許容 | canonicalizationの`reasoning`は『負担を担う』と認識しているのにglossは字義(情報が渡らない一例) |
| `take the wheel` | 『ハンドルを握る』『車を運転する』『主導権を握る』 | gold許容 | 字義・比喩が本文で重なる(『運転しない』の比喩的例え) |
| `standard deviation` | 『データのばらつき具合を表す値』T03 G2 r2・G3 r1,r2 | △(定訳でなく説明文) | G2『一般化した中心義』、G3『聞いてすぐ分かる』基準による説明文化 |
| `price tag` | 『値札に表示された価格』T03 G2 r1 | △ | 同上 |
| `reach for someone's wallet` | 『人が支払いを覚悟する』T03 G2 r2 | △(動作が消えた意訳) | G2の定義→gloss変換 |
| `brace yourself for` | 『～に備える』T03 G3 r2 | △(含意欠落) | G3の候補選択が薄い案を選ぶ |
| `on the throne` | 『トップの座にいて』T03 G3 r2 | △ | 同上 |
| `pump one's fist` | 『自分の拳を突き上げる』T04 B0 r2 | △(喜びの含意欠落) | 現行でも出る |
| `play a part` | 『影響する』T04 M r2 | △ | M(churn) |
| `supply chain` | 『商品が作られて店に届くまでの流れ』T04 Cp | △(範囲が狭い) | Cp |
| `draw a line` | 『区別する』T04 Cp | △ | Cp |
| (別掲: 見出し語placeholder、字義訳ではない) `reach for someone's wallet`『人の/誰かの財布に…』, `apply one's findings`『人の研究結果』 | — | 課題②の対象(別委任) | — |

### 3-3 共通構造(要求6への回答)
- **比喩が新造か慣用か**: 新造2(unseen clock・trophy)、慣用の断片/拡張2(greener grass・draw a line)。辞書にある完全な慣用で、日本語にも同種の比喩があるもの(shine a light on・behind the curtain・off the hook・turn on its head)は現行でも字義訳0。
- **見出し語の型**: 名詞句3・動詞句1。いずれも『具体名詞(line/clock/trophy/grass)を含み、字義読みも文法的に成立』する。
- **本文の説明位置**: 4KPとも比喩の意味は**同文の外(直前/直後)か暗示**で、source_sentenceだけでは確定しない。記事全文には説明がある。
- **Std/Advの差**: Adv(英語1文の意味説明)は、字義訳のStd glossを入力に受けても4/5が非字義(draw a line 3/3、unseen clock 1/1、greener grass 1/1。例外は`question shaped like a trophy`のAdv『outlineがトロフィーに見える質問』=glossの伝染)。**英語の意味説明タスクは日本語glossタスクより字義の像に引かれにくい**(ただしnが小さい)。
- **モデル差**: luna G0 vs Sol G0は`draw a line`で2/3対0/3(n小)。全体の合格率は同等(`TRIAL_RESULT_02.md`)。モデル強化は主因ではない。
- **同一KPのrep間ゆれ**: `draw a line`のみ確率的(G0 2/5)。他3KPは現行Promptで6/6字義(ほぼ決定論)=**確率的ではなくPrompt構造に依存した系統的失敗**。

## 4. 仮説の整理(支持/反証)

| ID | 仮説 | 判定 | 根拠 |
|---|---|---|---|
| H1 | 選定は用法を把握しているが意味生成へ渡していない | **事実として確認**(選定は意味を出力しない。canonicalizationの`reasoning`は意味を言うがgloss段へ渡されない)。『それが字義訳の十分原因』かは**未確定**(記事全文はgloss段にあるため再取得可能) | §2-2 |
| H2 | 意味生成の入力が見出し語+1文のみで比喩の説明文が範囲外 | **半分反証**: 全文は渡されている。範囲外なのは**使い方の指示**(語義選択専用) | §2-3 |
| H3 | 出力が短い日本語glossであることが字義像に引く | **部分支持**: Adv(英語文)はstd glossより字義に引かれない(4/5)。G3のように案を並べて選ぶと0/7。**日本語phrase1本を直接書く形**が最も字義に近い | §3-3、§2-4 |
| H4 | 意味同定と訳出の同時実行 | **部分支持**(§2-4)。同定を先に書かせると新造比喩は直る。だが日本語化段にも判定が要る | G2 r2 |
| H5(新) | 文脈限定句(再利用可能な訳・本文固有の文脈の追加禁止・source_sentenceは語義選択専用)が文脈依存の比喩で字義訳を誘発する | **最有力・未検証**。全armで不変の唯一の共通因子。Trial X1で直接検証 | §2-1 |
| H6 | モデル能力不足 | **ほぼ反証** | Sol≒luna、C再生成で直る |
| H7 | 再整合用Promptが字義訳を誘発(OF-06) | **反証** | M: 字義訳4/8で変化なし、費用は下がる |
| H8 | 検査の不在が原因 | **生成原因ではなく永続原因**(誤りが残る理由)。検査追加は誤検知が多い(Cのprecision 26%) | §2-5 |
| H9 | 純粋な確率的ゆれ | **反証**(3KPは現行で6/6字義。draw a lineのみ確率的) | §3-3 |
| H10 | 日本語化段で字義像を使うかの判定が無い | **支持**(G2 r2) | §2-4 |

## 5. どの工程を変更するのが有効か(要求7)

| 工程 | 変更の例 | 追加call | 効く対象 | 副作用/リスク | 評価 |
|---|---|---|---|---|---|
| **gloss生成call内(入力の使い方+出力構造)** | 制約句の置換+『本文での意味(英)→字義の日本語は意味を運ぶか→gloss』を先に書かせる | **0** | 4KPの全型(新造・断片) | 薄い/説明文化(G2・G3で観測)。条件付きにして回避 | **本命**(`DESIGN_07.md` 案A) |
| canonicalizationの所見をhintとして渡す | 既存`reasoning`または新欄を、glossの入力に参考として追加 | 0 | `Carry the Load`型(認識があるのにgloss字義) | E3: 意味を固定して渡すと判断が外れたとき悪化(ROOT_CAUSE_02 §3-2)。canon call(0.28円)の出力増、2module変更 | 次点(案D) |
| 選定 | schemaに意味メモ欄/規則3の手がかり保持 | 0 | `greener grass`の断片化 | Prompt 2逐語固定(ユーザー承認事項)、選定品質への波及が不明 | 後回し(案E、要ユーザー承認) |
| 事後検査 | 独立検査+再生成 | +1 | 検出可能なもの | precision 26%、再生成負荷(ユーザー不採用) | 採らない(案F=最終手段) |

## 6. 限界・未確認(推測で埋めない)
- 事後層別: hard-core 4KPは字義訳が出たKPとして選ばれたため、G0/B0の率(8/11)は過大。対照は新規repで取り直す(`TRIAL_DESIGN_05.md`)。
- Cpは1 rep・61出力。N層はTHIN 1。Cpの優位は探索的で、再現が必要。
- G2・G3は`question shaped like a trophy`・`greener grass`に未実施。
- Adv側の4/5は小標本(5件)。
- 制約句仮説H5は、DEVのアーム比較で未検証(X1が直接検証)。
- Production artifactの字義訳実在は`greener grass`『もっと青々とした芝生』、`question shaped like a trophy`『トロフィーの形をした問い』、`draw that line`『その線を引く』『その境界線を引く』の3KP(`an unseen clock`はouter_retry attempt_1の候補artifact)。全Productionでの率は未測定。
- 作業ツリーのProductionファイルは課題②の並行配線で編集中。本書のfile:lineはHEAD基準で、配線後に行番号が変わる。
