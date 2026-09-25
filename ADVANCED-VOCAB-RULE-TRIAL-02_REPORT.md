# ADVANCED-VOCAB-RULE-TRIAL-02_REPORT.md

管理ID: ADVANCED-VOCAB-RULE-TRIAL-02(Sonnet実行、2026-09-26)

Production実装ではない。Trialのみ。Production Prompt/Validator/
Production path/SSOTへは一切実装していない。Standard側への反映もしていない
(所見のみ§7に記載)。ADVANCED-VOCAB-RULE-TRIAL-01(v1/fix01=v2)の
スクリプト・出力は一切変更していない。新規出力は
`er015_output/advanced_vocab_rule_trial_02/`のみ。

## §1 目的

ADVANCED-VOCAB-RULE-TRIAL-01(v1/v2)で残ったUSER_DECISION_REQUIRED論点
(artery型がD[比喩保持]でKEEPされ、ユーザーが仕様候補で明記していた
「artery型[12,000超・推測困難・日本語未定着]は原則平易化候補」という
期待と食い違った)を受け、ユーザーが定義した仕様候補v2(Topic Core Word
例外の新設 + Metaphor単独理由でのKEEP禁止 + 優先順位「テーマの根幹語 >
比喩表現 > その他」)をTrialとして実測検証した。Production採用判断では
ない。

## §2 仕様候補v2(原文 + Prompt差分 v2→v3逐語)

日本語原文(ユーザー委任文から逐語転記):
`er015_output/advanced_vocab_rule_trial_02/spec_candidate_v2_ja.md`。

Prompt(英訳)の差分は、trial_01/v2の`RULE_BLOCK_EN_V2`(A/B/C/D例外 + C[固有
名詞]への引用符内呼称の明確化)をベースに、以下を追加した(v3、
`er015_output/advanced_vocab_rule_trial_02/prompt_advanced_vocab_rule_v3_
{meta,sewer}.txt`に記事ごと全文保存)。

- **E. Topic Core Word**(新設): 「12,000位超でも、その語が記事テーマの
  根幹であり、失うと『何についての記事か』が弱くなるならKEEP可。単に
  『よく出る語』では不可。判断基準3点(Topicそのものを指す/記事理解の
  中心/将来Topic Word価値)を明記し、Eを使う場合は`topic_core_
  justification`にこの記事固有の具体的理由を書くことを必須化(曖昧・
  一般的な理由は不可と明記)」。
- **Metaphor restriction**(新設): 「AI Writerが作った比喩・
  Storytelling装置のための語は、『比喩を守りたいから』『物語としてきれい
  だから』という理由だけではKEEPしない。12,000超で他のA/B/C/D/E例外が
  比喩とは独立の理由で該当しない限り、原則平易化対象。Dを使う場合は
  比喩維持が理由でないことをreasoningで明示させる」。
- **優先順位**(新設): 「同じ語に複数の考慮が当てはまりうる場合、個別語の
  決め打ちではなく意味上の役割で判断する。Topic Core Word(E) > 比喩
  (Metaphor) > その他」。
- **判定ラベル更新**: `KEEP -- topic core word`を追加、`KEEP -- proper
  noun`を`KEEP -- proper noun / quoted designation`へ改称(意味は
  trial_01/v2のC明確化と同一)。
- **schema拡張**(decisions各項目): `is_metaphor: boolean`、
  `exception_used: "A"|"B"|"C"|"D"|"E"|"none"`、
  `topic_core_justification: string`(E以外は空文字)を追加。
- **TASK_TAIL更新**: 「事実・トーン・Storytelling・結末ロジックを変えない」
  という既存の保護指示から「中心比喩(central metaphor)」を除外し、代わりに
  「比喩のためだけの語はA/B/C/D/Eが比喩と独立に該当しない限り通常の平易化
  候補である」と明記(Dを比喩保持の隠れ蓑にする経路を塞いだ)。

実装上の注記: ラベル文字列は既存schema enumとの一貫性のため
`KEEP -- X`(ハイフン2つ)表記のままとした(ユーザー原文の`KEEP — X`
[emダッシュ]と同義、表記のみ既存enumスタイルに合わせた表記上の選択。
個別語指示ではない)。`exception_used`の"E"という記号自体はSonnetが
実装上付与した内部ラベル(Prompt本文ではTopic Core Wordという名称で
説明)。

## §3 方法

候補語抽出・順位算出(rank = min(surface, lemma)、-er除去なし)・
fact_tokens_check・構造/語数/文数チェックはtrial_01/v2の実装
(`er015_advanced_vocab_rule_trial_01_v2.py`の`lemma_candidates_v2`/
`rank_of_word_v2`/`build_candidates_v2`/`fact_tokens_check`)をそのまま
importして再利用し、新規実装は行っていない(新スクリプト
`er015_advanced_vocab_rule_trial_02.py`)。候補語数はtrial_01/v2と完全
一致(Meta=2語、Sewer=5語、BORDERLINE参考語各1語)、同一記事・同一頻度
データのため予定通り。Prompt(RULE_BLOCK_EN_V3・TASK_TAIL_V3)とJSON
schema(`is_metaphor`/`exception_used`/`topic_core_justification`追加、
decision enumにTopic Core Word追加)のみ新規実装した。記事ごと1 call
(model=gpt-5.6-luna、effort=high、json_schema strict)、計2 call。

## §4 Meta結果

Before/After: `er015_output/advanced_vocab_rule_trial_02/meta_before.md`
/ `meta_after.md`(完全一致、diff 0行)。

| Word | surface rank | 判定 | exception_used | is_metaphor | topic_core_justification | reasoning |
|---|---|---|---|---|---|---|
| concierges | >20,000(zipf=1.70) | KEEP -- proper noun / quoted designation | C | False | (該当なし) | "Human concierges" is a designation that Meta reportedly used for these workers, so it must be preserved as a quoted fact under exception C. |
| onstage | 15,670 | KEEP -- predictable morphology/compound | A | **True** | (該当なし) | Although "onstage" is used as part of the article's performance metaphor, its meaning is easily guessed from "on"+"stage." Exception A applies independently of the storytelling effect. |

trial_01/v2と判定結果は同一(concierges/onstageともKEEP、本文一字も
不変)。新フィールドにより、onstageが実は記事の演劇比喩の一部
(`is_metaphor=True`)でありながら、それでもA(形態から推測可能)という
比喩とは独立の理由でKEEPされたことが今回初めて明示された。
`meta_fact_tokens_check.json`: `overall_fact_tokens_match: true`
(引用符内文字列・固有名詞語とも完全一致)。全文Decision Log:
`meta_decision_log.md`。

## §5 Sewer結果

Before/After: `er015_output/advanced_vocab_rule_trial_02/sewer_before.md`
/ `sewer_after.md`。

| Word | 採用rank | 判定 | exception_used | is_metaphor | topic_core_justification(要約) |
|---|---|---|---|---|---|
| septic | >20,000(zipf=3.21) | KEEP -- topic core word | E | False | 記事は町全体の下水systemに代わる"combined septic tank"の是非がテーマそのもの。"septic"はその中心技術を指す語。 |
| artery | 12,006 | **SIMPLIFY** | none | **True** | (該当なし。比喩のみで、比喩と独立の他例外も非該当のため平易化) |
| sewer | 12,324 | KEEP -- topic core word | E | False | 記事の中心対比(町全体のsewer system vs 各家庭のseptic tank)を成立させる語。 |
| sewers | 12,324(lemma) | KEEP -- topic core word | E | False | 記事全体で繰り返し対比され、結末の問いかけにも使われる中心語。 |
| wastewater | 18,216 | KEEP -- topic core word | E | False | 題名("Household Wastewater")に明示され、本文の説明対象そのもの。 |

決定: SIMPLIFY 1語(artery)、KEEP -- topic core word 4語(septic/sewer/
sewers/wastewater)。diffはartery→pipeの2文のみ(タイトル・他文は一字も
不変)、`sewer_diff.md`参照。word_count diff=0、sentence_count diff=0、
構造契約(見出しゼロ・段落数8)完全一致。`sewer_fact_tokens_check.json`:
`overall_fact_tokens_match: true`。全文Decision Log(topic_core_
justification全文含む): `sewer_decision_log.md`。

## §6 旧v2(trial_01/v2) vs 今回(trial_02)比較表

### Meta

| Word | Rank | 旧判定(v2) | 新判定(v3) | 新しい判断理由 |
|---|---|---|---|---|
| concierges | >20,000 | KEEP -- proper noun | KEEP -- proper noun / quoted designation | ラベル名称のみ変更(意味は同一、C適用) |
| onstage | 15,670 | KEEP -- predictable morphology/compound | KEEP -- predictable morphology/compound(変化なし) | is_metaphor=Trueが新たに明示されたが、Aが比喩と独立に適用されると確認 |

### Sewer

| Word | Rank | 旧判定(v2) | 新判定(v3) | 新しい判断理由 |
|---|---|---|---|---|
| artery | 12,006 | KEEP -- indispensable / natural replacement unavailable(比喩保持理由) | **SIMPLIFY** | is_metaphor=True; 比喩のためだけのKEEPは禁止のため、"main pipe"へ平易化。**trial_01のUSER_DECISION_REQUIRED論点が解消**。 |
| septic | >20,000 | SIMPLIFY(→"treatment") | **KEEP -- topic core word** | 記事の中心技術・比較対象そのものであるため、E(Topic Core Word)でKEEP。v1では逆にKEEP(D)だった経緯もあり、3バージョンで判定が揺れた語(§7-4参照)。 |
| sewer | 12,324 | SIMPLIFY(→"underground pipe network") | **KEEP -- topic core word** | 記事の中心対比を成立させる語としてE適用。本文から"sewer"という語自体が消える問題(trial_01 §7-7指摘)が解消。 |
| sewers | 12,324 | SIMPLIFY(→"underground pipe networks") | **KEEP -- topic core word** | 同上。冗長な言い換えの反復(trial_01 §7-7指摘)も解消。 |
| wastewater | 18,216 | KEEP -- predictable morphology/compound(A) | KEEP -- topic core word(E) | ラベルの根拠がAからEへ変化(本文は不変)。題名に明示された語であることが理由。 |

全文(reasoning全文・before/after文含む): `sewer_v1v2_vs_trial02_
compare.md` / `meta_v1v2_vs_trial02_compare.md`。

## §7 評価(9項目)

1. **Topic Core Word例外が期待どおり機能したか(sewer)**: 機能した。
   septic/sewer/sewers/wastewaterの4語はいずれも「記事の中心対比・題名の
   主題」を具体的に引用したjustificationでKEEPされ、単なる高頻度出現を
   理由にした語はゼロだった。
2. **Metaphor KEEP禁止が機能したか(artery)**: 機能した。arteryは
   `is_metaphor=True`かつ`exception_used=none`でSIMPLIFYされ、trial_01
   (v1・v2とも)で発生していた「比喩保持のためのD濫用」が解消された。
   これがtrial_01のUSER_DECISION_REQUIRED最重要論点の解消結果である。
3. **wastewater=A維持か**: **維持していない**。trial_01/v2ではA
   (形態から推測可能)だったが、今回はE(Topic Core Word)に変わった
   (本文は完全不変)。題名"Household Wastewater"に明示されているため
   Eの適用自体は妥当だが、AもEも両方成立しうる語でLLMがEを優先した形
   であり、「ラベルの根拠が実行ごとに変わりうる」という点は観察事項
   として記録する。
4. **septicの判断観察**: v1(KEEP-D)→v2(SIMPLIFY)→v3(KEEP-E)と、3回とも
   異なる判定になった。v1→v2の変化はD境界判断の揺れ(trial_01 §9で
   既報)。v2→v3の変化はルール自体の変更(Topic Core Word新設)によるもの
   であり、今回は具体的なjustification(記事の中心技術)を伴っており、
   前2回の「専門語だから」的な理由よりも根拠が明確になった。
5. **Meta既存挙動(concierges=KEEP呼称、onstage=KEEP A)維持か**: 維持
   された。両語とも判定・本文とも trial_01/v2と完全一致。
6. **Topic Core Wordが「重要そうだからKEEP」の万能逃げ道になっていないか
   (justificationの具体性を引用して評価)**: 4件とも一般論ではなく
   記事固有の具体的引用を伴っていた(例: septic「The article is
   specifically about municipalities considering combined septic tanks
   as an alternative to aging sewer systems」、wastewater「The title
   explicitly presents the story as being about household wastewater」)。
   一方、Sewer記事の候補5語中4語がTopic Core Wordに該当した比率の高さ
   (80%)は、この記事が下水インフラそのものをテーマにした専門色の強い
   記事であることを踏まえても、単一記事(n=5)のみでは「万能逃げ道化」の
   リスクを完全には否定できない。artery(比喩のみ)が正しくEの対象外と
   判定された点は、少なくともEと「比喩だけの中心語らしさ」を区別できて
   いることを示す一事例である。他記事での追加検証が望ましい(§9)。
7. **比喩をDへ逃がしていないか**: 逃がしていない。onstage
   (is_metaphor=True)はAで独立に正当化され、artery(is_metaphor=True)は
   Dを使わずSIMPLIFYされた。今回の2記事7候補中、Dが使われた語は
   ゼロ件だった(D自体が今回未使用のため「D濫用」は原理的に発生しな
   かった点も付記)。
8. **12,000ルール形骸化の有無**: 閾値抽出自体は正しく機能(候補語数は
   trial_01/v2と完全一致)。E追加によりKEEP率が7語中5語(71%)とv2
   (7語中3語、43%)より上昇したが、各KEEPには具体的根拠があり、
   「機械的に全部残す」形骸化は観測されなかった。
9. **Advancedらしさの不必要な低下**: 低下なし、むしろ改善。trial_01/v2で
   問題視されていた「sewer/sewersを冗長な言い換えで反復置換し単調になる」
   現象(§7-7)が、Topic Core Word例外により解消された(本文の
   sewer/sewers/wastewaterはそのまま残り、変更はartery→pipeの2文のみ)。

**Fact/Storytelling/意味の副作用**: Meta/Sewerとも
`overall_fact_tokens_match: true`(引用符内文字列・数値・固有名詞語すべて
完全一致)。Sonnetがunified diff全行を目視確認し、変更はarteryの2文の
みで、他は一字も変わっていないことを確認した。word_count diff:
両記事とも0。sentence_count diff: 両記事とも0。構造契約(見出し・段落数)
完全一致。

**Standardへの副作用所見(所見のみ、実装判断ではない)**: Topic Core
Word例外は、記事テーマの根幹語彙をStandardでも保持したい場合に有用な
可能性があるが、Standardは現状Advancedよりはるかに厳しい頻度カットオフ
を使っており、E例外を無条件で持ち込むとStandard読者向けの語彙制約を
大きく損なうリスクがある(所見のみ、実装はしていない)。

## §8 QCD(cost/時間/失敗)

- Cost: 合計 JPY 1.4772(Meta=0.3181円、Sewer=1.1591円)、予算上限
  JPY 5円以内(trial_02単体予算、trial_01とは独立)。
  `er015_output/advanced_vocab_rule_trial_02/cost.json`。参考: 前回
  trial_01/v2実績 JPY 1.9875円。
- 時間: Meta 16.299秒、Sewer 57.308秒(trial_01/v2のSewer 137.366秒より
  短縮、reasoning tokens=4,072 vs 前回7,416)。
- 失敗: リトライ0回、fallback検出0回(response_model_actual=
  gpt-5.6-luna一致)、schema parse失敗0回。両記事とも1回のcallで完了
  (実行前に定めた「1記事あたり生成1回、技術的失敗時のみ再試行1回」の
  上限内)。

## §9 Sonnet仮分類

**VALIDATED**(このTrialの検証目的の範囲内。Production採用判断ではない)

根拠:
- trial_01(v1・v2)で唯一残っていたUSER_DECISION_REQUIRED論点
  (arteryが比喩保持のD理由で誤ってKEEPされ、ユーザー期待「artery型は
  原則平易化候補」と食い違っていた)が、今回の実測で解消をevidence
  確認した(§7-2)。
- Topic Core Word例外(新設)は、単なる高頻度語ではなく記事固有の
  具体的な根拠(題名・中心対比の引用)を伴ってのみKEEP判定に使われ、
  「重要そうだからKEEP」という曖昧な万能逃げ道にはなっていなかった
  (§7-6)。
- Metaphor単独理由でのD濫用を防ぐ制約も機能し、比喩語(onstage/artery)
  はいずれもMetaphorとは独立の理由(A適用 or 例外非該当→SIMPLIFY)で
  正しく処理された(§7-7)。
- Fact不変・構造契約・語数文数・技術的失敗ゼロ・予算内、いずれも実測
  確認済み(§7末尾・§8)。
- ただし、次の2点は「VALIDATEDだが引き続き観察が必要な所見」として
  残る(STOP条件[新例外カテゴリ追加が必要/Topic Core Word定義拡張が
  必要/Standard同時反映が必要/個別語対応が必要]には該当しないため
  STOPはしない):
  (a) Sewer記事1本ではTopic Core Word比率が80%(5語中4語)とやや高く、
      他記事での追加サンプルがあれば比率の妥当性をより確認できる
      (§7-6)。
  (b) septicの判定が3バージョン(v1/v2/v3)で3回とも変わっており、
      D境界・Topic Core境界いずれも実行間で揺れうるという既知の限界が
      継続している(§7-4)。

## §10 [Fable記入]

## §11 [Fable記入]
