# NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01_REPORT.md

管理ID: `NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01`
日付: 2026-09-25
実行: Sonnet(サンドイッチ委任、初回)
Production変更: なし(Trial出力のみ。Production Prompt/routing/retry/fallback/Audio配線は無変更)。
到達Status: `VALIDATED`(§13でUSER_DECISION_REQUIRED、Production採用は別判断)。

## 結果サマリ(重要)

「最頻出約2,000語を優先する」という**Prompt指示単体の実効性は低い**ことを実測で確認した。
下水道Standard v2の圏外(異なり語)数は36語で、Advanced Baseline(改変前、36語)とほぼ同じ、
v1(33語)よりむしろ多い。つまりv2でmunicipalities/artery/combined septic tank等の難語が
残っていたのは主観的印象だけでなく、機械測定でも裏付けられた。

その後、Prompt指示を「頻度目標の提示」から「判断基準の明示+self-check手順」に変更した
v3候補を1本生成したところ、圏外(異なり語)数は36→28語(-8語、-22%)、圏外(延べ語)数は
58→50語(概算、§6参照)へ減少した。v2の目玉問題だった**municipalities**はv3で完全に消え
(towns へ置換)、facilities/installation/inspections/convenience等の硬い語も平易な語へ
置換された。一方でartery/septic/combined/wastewater/underground等、原則A(専門語・代替
困難)に該当すると判断できる語は引き続き残った。Story構造(8段落)・中心比喩(main artery/
washing machineの直喩)・Ending(surprisingly familiar place)は機械+目視確認で保持を
確認。Fact drift機械diffでは数値差分なし、固有名詞diffは文頭大文字の検出ノイズのみで実質
差分なし。費用は¥0.4036(上限¥100)で完了、STOP該当なし。

---

## §1 使用した頻度/語彙基準

### 探索手順
1. Repo内探索(`Glob **/*{ngsl,NGSL,oxford,gsl,wordlist,word_list,frequency,cefr}*`、
   `Grep "ngsl|oxford 3000|wordfreq|cefr" -i`): ヒットしたのは既存Report/Prompt内の
   「CEFR」という語句への言及のみで、実体を持つ頻度リストファイルはRepo内に存在しなかった。
2. `.venv`既存依存確認: `pip show wordfreq` / `pip show nltk` / `pip show spacy` はいずれも
   未導入(`Package(s) not found`)。
3. 無料公開の頻度リストを新規取得: `pip install wordfreq`(PyPI, **Apache-2.0**,
   ローカル計算・無料、有料APIではない)を実行し `wordfreq==3.1.1` を導入(2026-09-25)。

### 採用基準
- `wordfreq.top_n_list("en", 2000)` で取得した英語頻度上位2,000語形を採用。
- 圏内/圏外判定は**lemma化した集合同士の比較**で実施。上位2,000語形を
  `simple_lemma()`(標準ライブラリのみ、複数形/三単現/過去形/-ing/比較級・最上級の
  規則活用のみ対応)でlemma化し重複除去 → **1,686 lemma**の基準集合
  (`frequency_lemma_set.json`)。記事側のcontent wordも同じ関数でlemma化してこの集合との
  一致を判定する。silent-e(damage+ed→damaged)の復元を`simple_lemma_candidates()`で追加
  対応済み(§1限界参照)。

### 件数・出典・保存先
- `er015_output/news_standard_a2_vocab_effectiveness_trial_01/frequency_top2000.json`
  (上位2,000語形本体、ライセンス表記同梱)
- `er015_output/news_standard_a2_vocab_effectiveness_trial_01/frequency_lemma_set.json`
  (lemma化後1,686語)
- `vocab_reference.md`(探索手順・採用基準・限界の全文)

### 限界(既知)
- 不規則活用(bring→brought、child→children等)は非対応。該当語は圏外判定になりうる。
- `wordfreq`は複数コーパス統合値であり、CEFR A2公式語彙リスト(Cambridge English
  Profile等)そのものではない。「高頻度語」と「A2として適切」は同義ではない。
- silent-e復元は対応したが(toilet/hardly/tap/repairs等、日常語でも一般コーパス頻度
  順位が2,000位より低い語は依然「圏外」と判定される)。本Trialの圏外語一覧には、真に
  難しい専門語だけでなく、頻度リスト自体の限界による**過剰検出(false positive)**が
  一定数含まれる(§2で個別に注記)。

---

## §2 v2の圏外語一覧と分類(固有名詞/専門語/一般語、必要/不要仮分類)

機械測定: content word抽出→機能語(冠詞/前置詞/代名詞/助動詞/接続詞/be動詞等の固定
リスト、`FUNCTION_WORDS`)を除外→lemma化→頻度圏内/圏外を判定。**固有名詞は本記事に
実質0件**(`_fact_tokens`の機械diffが検出する「大文字語」は文頭語の検出ノイズであり、
真の固有名詞・人名・地名は下水道記事に存在しない)。以下はAdvanced/v1/v2の圏外語の
**和集合(40語、表層形単位)**にSonnetが1語ずつ分類根拠を付けたもの(参考、最終分類は
Fable/ユーザー)。

| 語 | 分類 | 原則 | 根拠(1語ずつ) |
|---|---|---|---|
| combined | 専門語 | A(必要) | 「合併処理浄化槽」の公式名称の一部。置換すると制度名としての意味を失う |
| septic | 専門語 | A(必要) | 同上、"septic tank"は規制上の名称の一部 |
| underground | 一般語 | A(必要・freq限界) | 単一の平易な代替語がない基本描写語。頻度順位のみの過剰検出の疑い |
| toilet / toilets | 一般語 | A(必要・freq限界) | 日常基本語、代替語なし。頻度順位のみの過剰検出の疑い |
| sewers / sewer | 専門語 | A(必要) | 記事の主題そのものを指す語、代替不可 |
| tank / tanks | 一般語(専門語の構成要素) | A(必要) | "septic tank"の構成要素、代替不可 |
| **municipalities** | 一般語(行政用語) | **B(不要・置換可能)** | ユーザー例示どおり"towns"/"local governments"で置換可能。v3で実際にtownsへ置換され消えた |
| kitchen / kitchens | 一般語 | A(必要・freq限界) | 日常基本語 |
| bath / baths | 一般語 | A(必要・freq限界) | 日常基本語 |
| artery | 専門語/比喩語 | A(必要、要検討) | 中心比喩("hidden main artery")の核。ユーザー例示のpipe network/main line/lifeline等へ置換可能だが、比喩の鮮やかさとのトレードオフあり。最終判断はFable/ユーザー |
| pipes | 一般語 | A(必要) | 日常基本語 |
| distant | 一般語 | B(不要・置換可能) | v3で"faraway"へ置換済み(ただし"faraway"も圏外。§6の限界参照) |
| repairs | 一般語 | A(必要・freq限界) | 日常基本語、頻度順位のみの過剰検出の疑い |
| washing | 一般語(比喩語の構成要素) | A(必要) | "washing machine"比喩の構成要素、代替不可 |
| replacing | 一般語 | A(必要・freq限界) | 基本動詞"replace"の活用形 |
| rid("get rid of") | 慣用句 | B(不要・置換可能) | イディオム。v3で"removing"へ言い換え済み |
| connects / connected | 一般語 | A(必要・freq限界) | 基本動詞、頻度順位のみの過剰検出の疑い |
| wastewater | 専門語(複合語) | A(必要、要検討) | タイトルにも使われる主題語。"used water"等への置換余地はあるが精度が落ちる可能性 |
| invisible | 一般語 | **B(不要・置換可能)** | v1/v2/v3で"hidden"へ置換済み(成功例、ただし"hidden"自体も本頻度基準では圏外のまま。§1限界参照) |
| beneath | 一般語 | **B(不要・置換可能)** | v1/v2/v3で"under"へ置換済み(成功例、"under"は圏内) |
| collects | 一般語 | A(必要・freq限界) | v3では"gathers"へ言い換えたが、これも圏外のまま(単なる語の交換、真の簡略化ではない) |
| hardly | 一般語 | A(必要・freq限界) | 日常副詞、頻度順位のみの過剰検出の疑い |
| tap | 一般語 | A(必要) | 日常基本語、代替語なし |
| flush | 一般語 | A(必要) | 話題特有だが平易、代替語なし |
| facilities | 一般語(硬い書き言葉) | **B(不要・置換可能)** | v3で"places"へ置換済み(成功例) |
| divide | 一般語 | A(必要・freq限界) | v3では"split"へ言い換えたが、これも圏外のまま(語の交換) |
| installation | 一般語(硬い書き言葉) | **B(不要・置換可能)** | v3で"putting in"へ置換済み(成功例) |
| inspections | 一般語(硬い書き言葉) | **B(不要・置換可能)** | v3で"checks"へ置換済み(成功例) |
| hidden | 一般語 | A(必要・freq限界) | invisibleからの置換先。学習者にはinvisibleより平易だが本頻度基準では圏外のまま |
| convenience / convenient | 一般語(抽象語) | **B(不要・置換可能)** | v3で"keep life easy"へ言い換え済み(成功例) |
| arrive | 一般語 | A(必要・freq限界) | Ending文"may arrive in"の一部、基本動詞 |
| surprisingly | 一般語 | A(必要) | Endingの核("surprisingly familiar place")、置換するとEndingの効果が弱まる懸念 |
| familiar | 一般語 | A(必要) | 同上、Endingの核 |

**集計**: 40語中、原則B(置換可能・不要)と判定したのは **municipalities, distant,
rid, invisible, beneath, facilities, installation, inspections, convenience/convenient
の9語族**。残り約31語族は原則A(専門語・代替困難・freq限界含む)。Sonnetの仮分類であり、
最終判断はFable/ユーザー。

---

## §3 「2,000語優先」指示の実効性評価(Advanced/v1/v2の数値比較)

| 記事 | content word(延べ) | content word(異なり) | 圏内(延べ)割合 | 圏外(異なり)数 | 圏外(異なり)割合 |
|---|---|---|---|---|---|
| Advanced(改変禁止Baseline) | 178 | 122 | 0.6629 | 36 | 0.2951 |
| Standard v1 | 184 | 119 | 0.6957 | 33 | 0.2773 |
| Standard v2 | 176 | 117 | 0.6705 | 36 | 0.3077 |

**実効性評価**: v2はAdvanced比で圏外(異なり語)数を **0語しか減らせていない**
(Advanced 36 → v2 36)。v1(v2より前のStandard Prompt、数値目標なし)のほうが
圏外語が少ない(33語)。圏外(延べ語)数もAdvanced 60 → v1 56 → v2 58 で、v2はv1より
悪化している。**「roughly the 2,000 most common words」という数値目標の提示のみでは、
語彙選択の実効性はほぼ無い**ことが本測定で確認された。v2は平均語/文の短縮
(13.62→9.51語/文)には明確に効いたが、語彙そのものの平易化には効いていない。

---

## §4 v3 Prompt全文 + v2差分

developer(v2と一字も変えていない、逐語):
```
You are an editor who rewrites English feature articles for learners of English at CEFR A2 level, while keeping the article just as enjoyable as the original.
```

user templateのうち、置換した2行(v2、削除):
```
Prefer common, high-frequency English words (roughly the 2,000 most common words).
Keep harder words only when they are necessary to understand the topic (for example, a technical term or a name). Do not add an explanation for a hard word; make the sentences around it simple instead.
```

置換後5行(v3、追加、逐語):
```
Use common, everyday words whenever a simpler word can express the same meaning.
Do not keep a difficult word just because it appears in the original article.
Keep a word above A2 level only if replacing it would lose an important fact or meaning (for example, a name, or a technical term with no simple equivalent).
Do not add an explanation for a hard word; make the sentence around it simple instead.
Before you finish, check every difficult word in your draft and replace each non-essential one with simpler English.
```

それ以外の本文(v2の残り全文、段落・改行含む)は一字も変更していない
(機械assert確認済み、`prompt_standard_v3.txt`/`prompt_diff_v2_v3.md`参照)。

変更意図: v2の「約2,000語」という数値目標はモデルに具体的な判定手段を与えないため
実効性が弱かった(§3)。v3では「簡単な語で同じ意味を表せるなら簡単な語を使う」という
判断基準そのものを明示し、"Do not keep a difficult word just because it appears in
the original article."でAdvanced由来の語をそのまま残す慣性を明示的に禁止、最後に
難語を見直すself-check手順を追加した。追加は3行(2行→5行)でPromptの過剰な長文化は
避けた。

---

## §5 v3記事全文

```
“Merger”? Not Towns, but Household Wastewater

When a news report says “combined septic tank,” you may wonder about towns joining. But the things joining are not towns. They are toilet water, kitchen water, and bath water.

Some towns are thinking about replacing old sewer systems with combined septic tanks. This does not mean removing every sewer. In some places, it means considering a change. The town-wide system could become one that treats wastewater near each home.

A sewer is like a hidden main artery under a town. It gathers water from homes through underground pipes. Then it carries the water to a faraway treatment plant. We hardly think about it most of the time. We turn on the tap and flush the toilet. Then the underground system does the rest.

But the pipes grow old. Then the situation changes. The pipes are underground, so damaged places are hard to find. Repairs are not easy either. The system stretches a long way and is connected. So repairs can become large jobs too.

That is where combined septic tanks come in. They are small places that clean water near homes. Each one treats toilet water, kitchen water, and bath water. The water does not travel to a faraway plant. It gets cleaned near the home where it comes out.

It is like putting a small washing machine in each home. The other choice is one huge washing machine for the whole town. The idea is to split one big system into several smaller ones.

Of course, a septic tank does not mean no other work is needed. It still needs putting in, checks, and cleaning. For people using sewers, the hidden part of daily life will also change.

Still, here is the interesting point. To keep life easy, we do not always need a bigger system. Instead of making an old underground main artery keep working, we can move water treatment closer to home. The future of sewers may arrive in a surprisingly familiar place—right near us.
```

model: `gpt-5.6-luna`(response.model実値も`gpt-5.6-luna`、fallback無し)、effort: `high`、
1 call、previous_response_id無し、Web Search無し。

---

## §6 v2 vs v3語彙比較

| 記事 | content word(延べ) | content word(異なり) | 圏内(延べ)割合 | 圏外(異なり)数 | 圏外(異なり)割合 |
|---|---|---|---|---|---|
| Standard v2 | 176 | 117 | 0.6705 | 36 | 0.3077 |
| Standard v3 | 179 | 113 | 0.7095 | 28 | 0.2478 |

- 圏外(異なり語)数: v2 36語 → v3 28語(**-8語、-22%**)
- 消えた語(v2圏外→v3圏内または未使用、13語): baths, collects, connects, convenient,
  distant, divide, facilities, inspections, installation, kitchens, **municipalities**,
  rid, toilets
- 残った語(v2/v3とも圏外、23語): artery, bath, combined, connected, familiar, flush,
  hardly, hidden, kitchen, pipes, repairs, replacing, septic, sewer, sewers,
  surprisingly, tank, tanks, tap, toilet, underground, washing, wastewater
- 新たに出た語(v3のみ圏外、5語): arrive(v2では圏外0回、v3で新規使用箇所が発生した
  わけではなく元記事の"arrive"がv2側の抽出で異なりカウントされていなかっただけ、
  実質は既存語), **faraway**(← distant置換、圏外のまま)、**gathers**(← collects
  言い換え、圏外のまま)、**split**(← divide言い換え、圏外のまま)、**stretches**
  (新規表現"The system stretches a long way"、圏外)

**評価**: 消えた13語のうち、municipalities/rid/distant/facilities/installation/
inspections/convenient(/convenience)の7語族は§2で原則B(不要・置換可能)と判定した
語と一致し、実際にPrompt変更の意図どおり平易化された。一方、新たに出た5語のうち
faraway/gathers/splitの3語は、**「難語→別の難語への交換」であり真の簡略化ではない**
(distant→faraway、collects→gathers、divide→splitはいずれも本頻度基準では圏外のまま)。
これは頻度リスト自体の限界(§1)とv3 Promptの限界の両方を示す: Promptは「圏外語を
言い換えよ」と指示できても、言い換え先が必ず頻度上位2,000語に入る保証はない。

---

## §7 Level指標

| 記事 | words | sentences | avg words/sent | avg syll/word | long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |
|---|---|---|---|---|---|---|---|
| Advanced | 354 | 26 | 13.62 | 1.483 | 0.077 | 3.11 | 7.22 |
| Standard v1 | 364 | 27 | 13.48 | 1.451 | 0.074 | 2.75 | 6.78 |
| Standard v2 | 333 | 35 | 9.51 | 1.465 | 0.0 | 1.5 | 5.41 |
| Standard v3 | 331 | 34 | 9.74 | 1.429 | 0.0 | 1.21 | 5.07 |

v3の平均語/文はv2よりわずかに長い(9.51→9.74語、+0.23語)が、9〜11語/文の目標レンジ内。
subordinator密度・FK grade(heuristic)はv2よりさらに下がっており(1.5→1.21、5.41→5.07)、
文法的な複雑さはv2と同水準以上に簡易。機械判定は参考値であり最終判断には用いない。

---

## §8 Story・比喩・Ending保持

- 段落数: Advanced/v1/v2/v3すべて8段落で一致。
- Reveal(合併浄化槽への切り替え説明段落): v3にも同一段落位置で存在
  (「That is where combined septic tanks come in. They are small places that clean
  water near homes...」)。自動structure_map.mdの文字列一致チェックは
  "small water-treatment"という旧文言を探していたため×判定になったが(v3は"small
  places that clean water"へ簡略化されたため不一致)、目視確認でReveal自体は保持を
  確認(構造的には○、自動チェックの言い回し固定が原因の偽陰性)。
- 中心比喩: "A sewer is like a hidden main artery under a town."(直喩"like"のまま)、
  "It is like putting a small washing machine in each home."(直喩"like"のまま)、
  いずれも事実文化せず直喩のまま保持を確認(structure_map.md機械判定でも○)。
- Ending: "The future of sewers may arrive in a surprisingly familiar place—right
  near us."がv3でも同一文で保持(機械判定○)。

---

## §9 Fact drift・意味崩れ

機械fact diff(`_fact_tokens`、Advanced→v3): numbers差分なし。proper_nouns差分は
文頭大文字語の検出ノイズのみ(Because/Installation/Most/Since/Turn が消え、
Each/So/Then/To/We が新規検出。いずれも文分割位置の変化による誤検出で、真の固有名詞は
本記事に0件)。quoted_phrases一致("combined septic tank,")。negation_counts(not: 6/6で
同数)。scope_word_counts差分: all 1→0、only 1→0、no 0→1、every 0→1。

意味崩れチェック(事実列挙):
- Advanced "getting rid of all sewers" → v3 "removing every sewer"(all→every、
  普遍量化子として意味は同義、崩れなし)。
- Advanced "does not mean that nothing more is needed" → v3 "does not mean no other
  work is needed"(nothing more→no other work、言い換えだが「他に何も無いわけでは
  ない」という意味は保持)。
- Advanced "invisible main artery" → v2/v3 "hidden main artery"(invisible→hidden、
  「見えない」という核の意味は保持。ただし"invisible"は「絶対に見えない」、"hidden"
  は「隠れている(見ようとすれば見える)」に近く、厳密には語感が微妙に変化している
  可能性がある。事実列挙のみ、崩れの評価はFable/ユーザー判断)。
- v2→v3で"distant"→"faraway"、"collects"→"gathers"、"divide"→"split"はいずれも
  意味的にほぼ同義の言い換えで、意味崩れは確認されなかった。

---

## §10 model・cost・latency・tokens

| 項目 | 値 |
|---|---|
| response.model(実値) | gpt-5.6-luna(要求どおり、fallback無し) |
| effort | high |
| input_tokens | 875 |
| output_tokens | 1,956(reasoning_tokens 1,552を含む) |
| cached_input_tokens | 0 |
| elapsed_seconds | 15.131 |
| retried | False |
| cost_usd | 0.002522 |
| cost_jpy | 0.4036 |
| 予算上限 | ¥100(範囲内) |

詳細: `er015_output/news_standard_a2_vocab_effectiveness_trial_01/a2v3_standard_sewer.meta.json`
/ `cost.json`。

---

## §11 Fable参考評価
`[Fable記入]`

## §12 分類
`[Fable記入]`

## §13 USER_DECISION_REQUIRED
`[Fable記入]`

## §14 未解決事項

- artery/wastewater/septic/combined/underground等、原則A(専門語・代替困難)と
  Sonnetが仮分類した語について、ユーザー例示(artery→pipe network/main line/
  lifeline等)のように実際に置換すべきかは未決定(§2)。
- 「invisible→hidden」のように学習者には平易化されて見えるが、頻度リスト上は
  依然圏外のまま、という頻度リスト自体の限界(§1、§6)にどう対応するか
  (CEFR A2公式語彙リストへの切り替え等)は未検討・未決定。
- v3で発生した「難語→別の難語への交換」(distant→faraway、collects→gathers、
  divide→split)への対応方針(Promptにさらに指示を追加するか、許容するか)は未決定。
- Meta AI Call記事へのv3 Prompt適用は本Trialの対象外(下水道のみ)。
- 本Trialはユーザー指示どおりProduction変更・SSOT変更を行っていない。v3 Promptを
  正式採用するかはユーザー判断待ち。
