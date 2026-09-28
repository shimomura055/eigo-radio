# FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02 設計書

管理ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02(ユーザー承認済みTrial、
Trialのみ)。Production code・正式Prompt・CURRENT_SPEC・routingは一切
変更しない。

## §1 目的

Trial-01(`er037`)で観測した「Hormuz記事のANパターン(A3+N2)で、JA段階の
固有名詞が9件なのにEnglish Advanced段階で19件に増える」という現象が、
(a) 実際に日本語記事に無い固有名詞を英語化工程で新規追加しているのか、
(b) 単なるカウント方式(tokenization)のアーティファクトなのかを実データで
切り分ける。あわせて、Hormuz/Meta 2記事について、日本語Writer側
AN3(A3+N2)/AN2(A2+N2) × 英語化側 T0(現行)/T1(Trial限定の抑制追記)の
2×2 Matrixを比較し、「数字・固有名詞を減らしながら記事内容・因果関係・
面白さを維持できる組み合わせ」を探す。

## §2 固有名詞9→19の実体調査(read-only、¥0)

対象: `er037_output/family_xy_concreteness_control_trial_01/hormuz`の
ANパターン(A3+N2)、JA=`task_a_ja/AN_r2.md`、EN=`task_a_advanced/AN.md`
(いずれもTrial-01の既存artifactを再利用、再生成しない)。

### 2.1 旧カウンタ(Trial-01 `extract_entities_ja`/`extract_entities_en`)の実測

- AN JA(旧): 9件 -> イラン, ガソリン, タンカー, トランプ, ドル, ニュース,
  バレル, ブレント, ホルムズ
- AN EN(旧): 19件 -> Bill, Brent, Character:, Donald, Eastern, Gulf,
  Hormuz, Iran, July, Main, Market's, Middle, Missing, Oil, Percent,
  States, Strait, Trump, United

### 2.2 Advanced化Promptの入力範囲(実装読み込み結果)

`er003_v1_n3_01_advanced_adaptation_generate.generate_advanced_adaptation
(ja_article_text, ...)` および `build_prompt(ja_article_text, must_fix=None)`
は、引数として**日本語記事本文(ja_article_text)のみ**を受け取り、
Source記事・Verified Fact Ledger・過去の英語版などは一切渡していない
(`build_prompt()`の実装、`[Japanese article]\n" + ja_article_text`で
入力終端)。したがって、英語化段階で「Ledgerから新しい固有名詞を掘り
起こす」経路自体が存在しない(Ledger自体を読んでいないため)。

### 2.3 「固有名詞をKEEPする」既存ルールの原文(逐語引用)

`ADVANCED_VOCAB_RULE_V2_BLOCK`(ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01、
ユーザー正式決定によりAPPROVED_FOR_PRODUCTION)より:

> C. It is a proper noun (a person's name, a company or product name, a
> place name).

これは「簡単な語へ言い換える簡略化(vocabulary simplification)」の
除外条件の1つであり、固有名詞であれば簡略化(易しい言い換え)をしない、
という規則。**数字・固有名詞そのものを増減させる規則ではない**(N2等の
JA側の「固有名詞を一般化する」指示とは無関係の独立した既存ルール)。

### 2.4 6項目の事実確認への回答

1. **JA側に存在しなかった固有名詞が英語化後に新規出現したのか**:
   旧カウンタの単純比較では「Donald」が新規に見えるが、これは
   「トランプ氏」に対応する人物の名(Donald Trump)のfirst nameを
   モデルが自身の一般知識で補ったもので、Ledger由来ではない
   (Advanced Promptはja_article_text以外を読んでいないため、Ledgerからの
   掘り起こしではあり得ない)。§2.6の改良カウンタでは「Donald Trump」を
   1つの名称単位として扱うため、この論点は「新規固有名詞の追加」では
   なく「同一人物の呼称の詳細化」に整理される。
2. **同じ固有名詞の繰り返し回数が増えただけか**: 一部あり
   (「Trump」は複数文で言及されるが、旧カウンタは繰り返しを1件として
   集計する[setベース]ため、これ自体は9→19の主因ではない)。
3. **カウント単位・tokenizationが異なるだけか**: **主因はこれ**。
   §2.5/2.6で実測する。
4. **英語化Promptは何を入力としているか**: §2.2の通りJA記事本文のみ。
5. **「固有名詞をKEEPする」規則の意味と挙動**: §2.3の通り、簡略化の
   除外条件であり、新規追加とは無関係。
6. **増加元を具体的な名称単位で示す**: §2.6の名称単位差分表を参照。

### 2.5 tokenization差の実例

- JA: `ホルムズ海峡`のうち、既存正規表現`_KATAKANA_ENTITY_RE`は
  カタカナ範囲`[゠-ヿ]{2,}`のみを拾うため「ホルムズ」だけが1トークンに
  なり、「海峡」(kanji)は拾われない。同様に「米国」「中東」「湾岸諸国」
  はkanjiのみで構成されるため、既存正規表現では一切検出されない
  (過小カウント)。
- EN: `_ROMAN_ENTITY_RE`は大文字始まりの連続英字を素朴に1トークンとして
  拾うため、「United States」「Strait of Hormuz」「Middle Eastern」は
  それぞれ2トークンに分割される(過大カウント)。
- EN見出し: `# The Oil Market's Main Character: The Missing 20 Percent
  Bill`のような記事タイトル(Title Case)は、既存`extract_entities_en`が
  「文頭語(各文の最初の1語)」だけを除外し、見出し全体を除外しないため、
  タイトル内の"Oil, Market's, Main, Character:, Missing, Percent, Bill"の
  7語すべてが固有名詞として誤カウントされる(旧EN 19件中7件がこれ)。

### 2.6 改良カウンタ(Trial-02限定、Production無変更)による数え直し

このTrial限定で、以下のルールに基づく改良カウンタを実装した
(`er039_family_xy_concreteness_control_trial_02.
extract_entities_ja_improved`/`extract_entities_en_improved`)。
Hormuz/Meta 2記事の観測語彙に基づく簡易辞書方式であり、汎用NER/形態素
解析器の代替ではないことを明記する。

- 複合固有名詞(United States, Strait of Hormuz, Middle Eastern->Middle
  East, Gulf states/Gulf-state/Gulf countries, Donald Trump等)は1件として
  統合する。
- Title Case見出し行(`#`で始まる行)は本文抽出の対象から除外する。
- JA側はkanji固有名詞(米国, 中東, 湾岸諸国等、観測語彙ベースの辞書)も
  検出し、英語canonical名へ正規化する(米国<->United States等)。
- 一般名詞のカタカナ語(ニュース, バレル, ドル, タンカー, ガソリン,
  AI等)は除外する(N2ルール自身の定義「人名・企業名・地名」に該当しない
  ため)。
- 月名(July等)は除外する(人名・企業名・地名ではない)。
- 所有格接尾辞(’s/'s)・em/enダッシュに密着した語は正規化してから判定
  する。

**実測結果(Hormuz AN、Trial-01既存artifactに対して適用)**:

| | 旧カウンタ | 改良カウンタ |
|---|---|---|
| JA | 9 | 7 |
| EN | 19 | **7** |

名称単位差分表(改良カウンタ、AN、Hormuz):

| 固有名詞(canonical) | JA出現 | EN出現 | ENで新規か |
|---|---|---|---|
| Donald Trump | True | True | False |
| Strait of Hormuz | True | True | False |
| Brent | True | True | False |
| Iran | True | True | False |
| United States | True | True | False |
| Middle East | True | True | False |
| Gulf states | True | True | False |

**結論: 改良カウンタで数え直すと JA=EN=7 で完全一致し、ENで新規に出現した
固有名詞は0件だった。「9→19」は実質的にすべてカウント方式
(tokenization・見出し混入)のアーティファクトであり、日本語記事に無い
固有名詞を英語化工程が実際に新規追加した事実は(Hormuz ANについては)
確認されなかった。** ただしMeta記事のANでは旧カウンタ自体が12(JA)->
11(EN)とほぼ横ばいであり、「9→19」という急増自体はHormuz記事(かつ
AN Pattern)特有の現象だった(Trial-01 §5.2表と照合、JA=9/EN=19は
Hormuz ANの数値と一致)。

限定事項: 改良カウンタは文頭語除外ロジック(既存`extract_entities_en`を
踏襲)を維持しているため、文体の違いにより固有名詞が文頭に来ると
その語だけ検出されない(例: AN3-T1で"Brent"が段落先頭に来て検出漏れに
なったケースを§9に記録)。これは意味的な固有名詞削減ではなく、指標側の
既知の限界であり、本Trialのcell間比較でも同一バイアスが両側にかかる。

## §3 Trial script構成(`er039_family_xy_concreteness_control_trial_02.py`)

`er037_family_xy_concreteness_control_trial_01`をimportして以下を再利用:
`ARTICLE_SOURCES`/`load_article_inputs`/`PATTERNS_A`/`PATTERNS_N`/
`COMBO_PATTERNS`(AN=A3+N2をAN3として無変更再利用)/
`extract_entities_ja`/`extract_entities_en`(旧カウンタ)/
`deterministic_metrics`相当のold-metrics計算/`run_essential_fact_check`
(`vfl01.run_deviation_check`のラッパー)/`run_rubric_eval`/
`budget_check`/`save_text`/`save_json`/`merge_save_json`。

新規実装:
- `JA_PATTERN_TEXT = {"AN3": t1.COMBO_PATTERNS["AN"], "AN2": PATTERNS_A["A2"]
  + "\n" + PATTERNS_N["N2"]}`
- `run_ja_chain()`: pattern_idではなく直接テキストを受け取るJA
  Original(+pattern)->R1(現行)->R2(現行)チェーン(t1と同型)。
- `run_advanced_translation_t0()`: `t1.run_advanced_translation`
  (= production `generate_advanced_adaptation`をそのまま呼ぶ、無変更)。
- `run_advanced_translation_t1()`: production `adv_gen.build_prompt()`の
  出力(無変更)に`T1_SUPPRESSION_SUFFIX`(下記)を連結した別promptで、
  production関数(`generate_advanced_adaptation`)は呼ばず、その内部と
  同じ既存primitive`vfl01.run_writer_with_technical_retry`を直接呼ぶ。
  Production関数自体・Prompt定数自体は無変更のまま、別経路で1回callする。
- 改良カウンタ・名称単位差分表・比較ページ生成(§2/§6参照)。

### T1追加文(逐語、`T1_SUPPRESSION_SUFFIX`)

```
[Trial-only additional instruction -- not part of the production prompt]
Do not add any number, time, or proper noun (a person's name, a company or
product name, or a place name) that is not already in the Japanese article
above. Where the Japanese article uses a general or vague expression
instead of a specific number, time, or name, keep that expression general
in the English version as well. Do not use this instruction as a reason to
remove facts, numbers, times, or names that ARE already stated in the
Japanese article.
```

単体test(`er039_family_xy_concreteness_control_trial_02_test_01.py`、17件)
で、T1連結後のpromptが production `build_prompt()`の出力そのままを
prefixとして含むこと、production側sha256定数(`ADVANCED_UNCHANGED_
PORTION_SHA256`等)がimport時点で無変更検証されること、を確認している。

## §4 実行Pattern(2×2 Matrix + Baseline)

- Baseline = Trial-01の既存A0(JA=`task_a_ja/A0_r2.md`、
  EN=`task_a_advanced/A0.md`)を**再生成せず再利用**。
- AN3-T0: JA=Trial-01の既存AN(A3+N2)出力を再利用。EN=Trial-01の既存AN
  Advanced出力(T0=現行production Prompt)を再利用(deviation/rubricも
  既存artifactを再利用、新規API callなし)。
- AN3-T1: JAは上と同じ既存ANを再利用。ENのみ新規生成(T1)。
- AN2-T0: JAを新規生成(A2+N2)。ENを新規生成(T0)。
- AN2-T1: JAはAN2-T0と同じ新規生成JAを再利用(英語化のみ2回、JAは
  1回だけ生成)。ENを新規生成(T1)。

## §5 費用実績

Hormuz ¥8.768、Meta ¥8.088、固有名詞調査¥0、合計約¥16.9(Guardrail
¥70に対し大幅に余裕あり)。詳細は各記事の`raw_usage_log.jsonl`/
`cost_matrix.json`。

## §6 ユーザー確認用成果物

- `user_test/concreteness_trial_02/index.html`(GitHub Pages。Baseline/
  AN3-T0/AN3-T1/AN2-T0/AN2-T1のJA/EN全文並列表示+指標小表)
- `er039_output/family_xy_concreteness_control_trial_02/{hormuz,meta}/
  comparison_{article}.md`(同内容のMarkdown)
