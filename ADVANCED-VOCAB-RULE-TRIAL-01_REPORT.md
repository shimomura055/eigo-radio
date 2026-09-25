# ADVANCED-VOCAB-RULE-TRIAL-01_REPORT.md

管理ID: NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 / Phase 2 =
ADVANCED-VOCAB-RULE-TRIAL-01(Sonnet実行、2026-09-25、**fix01反映**)

Production実装ではない。Trialのみ。Production Prompt/Validator/
Production path/SSOTへは一切実装していない。Standard側への反映もしていない
(所見のみ§7-9に記載)。

## fix01(Fable差し戻し1回目)概要

v1はFableから以下2点の指摘を受け差し戻された(詳細根拠は
`docs/pm/ACTIVE_TASK_AVT.md`差し戻し指示に記録)。

1. 順位算出が表層形のみで、ユーザー前処理条件(活用形は可能な範囲でlemma
   へ正規化し重複カウントしない)に違反。municipalities/collects/
   inspectionsが疑似候補になっていた。
2. Meta記事のFact変更見逃し: `Meta called these workers "human
   concierges."` は事実(Metaが実際に使った呼称)であり語彙置換の対象外
   だったが、v1では誤ってSIMPLIFYされた。

v2で両方を修正し、`er015_advanced_vocab_rule_trial_01_v2.py`により
Meta/Sewer各1回(計2 call)を再実行した。v1成果物はそのまま
`er015_output/advanced_vocab_rule_trial_01/`に残し、v2成果物は
`er015_output/advanced_vocab_rule_trial_01/v2/`に保存した。本REPORTは
v1の記録を保持したまま、各節末尾に「### v2(fix01)」を追記する形で更新する。

## §1 目的

ユーザー定義のAdvanced難語仕様候補(一般英語頻出順位 約12,000位超を原則
平易化候補とし、A[既知の易しい語から推測可能な形態]/B[日本語に定着した
外来語]/C[固有名詞]/D[意味・自然さを損なう不可欠語]は例外として残せる)を、
Meta/Sewer Advanced記事2本でTrialとして1回だけ検証した。目的は仕様候補の
実際の挙動を実測することであり、Production採用判断ではない。

## §2 仕様候補(ユーザー定義、日本語原文)

`er015_output/advanced_vocab_rule_trial_01/spec_candidate_ja.md` に保存
(ユーザー委任文から逐語転記)。要点は本REPORT冒頭の§1に要約した通り。
英訳版はPromptとして
`er015_output/advanced_vocab_rule_trial_01/prompt_advanced_vocab_rule_v1_meta.txt`
/ `prompt_advanced_vocab_rule_v1_sewer.txt` に全文保存。

## §3 方法

1. コード側(`er015_advanced_vocab_rule_trial_01.py`)で、各記事の本文から
   content word(機能語・数字・記号除外、固有名詞除外は既存
   `v3mod.capitalized_positions`ヒューリスティック再利用)を抽出し、
   **表層形(surface form、記事中の実際の活用形そのまま)** ごとに
   wordfreq 3.1.1 (`top_n_list('en', 20000)`) の順位を直接算出した
   (lemma化はしない。理由: 既存`simple_lemma()`には単数"sewer"が
   末尾-erを比較級とみなして"sew"という別lemmaに誤正規化されるバグが
   あり[ADVANCED-VOCAB-DIFFICULTY-AUDIT-01 audit.md確認事項7(a)で既知]、
   これを継承すると"sewer"(12,324位)が正しく閾値超語として検出できない
   ため、新規ロジックとして表層形ベースの順位付けに変更した)。
2. rank>12,000またはtop20,000位圏外の語を「閾値超候補」、10,000〜12,000
   位を「BORDERLINE参考語」としてコード側で確定し、順位を文字列として
   Promptへ明記した(モデルには順位を推測させない)。
3. 記事ごとに1 call(model=gpt-5.6-luna, effort=high, json_schema strict)
   でPromptへ候補語リスト・BORDERLINE参考語リスト・記事本文・仕様候補の
   英訳・記事別の構造契約(Meta: `# `題名+`### `×2+`## In one line`、
   Sewer: 見出しなしの平文段落)を渡し、語ごとの判定(KEEP各理由/
   SIMPLIFY/BORDERLINE)とAfter本文を1回のJSON出力で得た。
4. コード側で構造契約維持・語数文数差・After新出難語(regression)・
   band参考値(既存lemmaベースbmod.measure_bands再利用、参考値のみ)を
   機械算出し、Before/After全文のunified diffをSonnetが目視で全件確認した。

### §3 v2(fix01): 順位算出をlemma対応へ修正

v1は表層形(surface form)のみで順位を算出しており、ユーザー前処理条件
(活用形は可能な範囲でlemmaへ正規化し、同一lemmaを重複カウントしない)に
違反していた。v2では
`rank = min(rank(surface form), rank(best lemma candidate))` に変更した。
lemma候補は `-s/-es/-ies/-ed/-ing/-ly` の単純規則のみで生成し、v1コメントで
問題視した既存`simple_lemma()`の `-er/-est` 比較級除去規則は使わない
(この規則が単数"sewer"を末尾-erの比較級とみなして別語"sew"へ誤lemma化する
バグの原因だった)。安全条件として、(i) lemma候補がwordfreq top20000
リストに存在しない場合は採用せず、(ii) 生成された候補語が元語より4文字
以上短い場合(len(candidate) < len(original) - 3)は元語とは別語である
可能性が高いとして除外する
(`er015_advanced_vocab_rule_trial_01_v2.py` `lemma_candidates_v2()`)。
Decision Logには surface rank / 採用lemma / lemma rank / 採用rank を
併記した。

Fact不変チェック(修正D)として、Before/After間で引用符内文字列・数値・
大文字化語(固有名詞候補)が完全一致するかをコード側で機械検証し
(`{article}_fact_tokens_check.json`)、Sonnet目視diff確認と併記した。

## §4 Meta Before/After/Decision Log

Before: `er015_output/advanced_vocab_rule_trial_01/meta_before.md`
After: `er015_output/advanced_vocab_rule_trial_01/meta_after.md`

### Meta Decision Log

| Word | Frequency Rank | 判定 | 理由 | Before | After |
|---|---|---|---|---|---|
| concierges | > 20,000 (zipf=1.70, extremely rare) | SIMPLIFY | Although the word names a specific service role, the simpler natural term "human operators" preserves the meaning in this phone-call context. It is therefore simplified. | Meta called these workers "human concierges." | Meta called these workers "human operators." |
| onstage | 15,670 | KEEP -- predictable morphology/compound | The meaning of "onstage" can be easily guessed from the familiar words "on" and "stage." It is a transparent compound, so it can be kept under exception A. | Who is speaking onstage? And who is behind the curtain? | Who is speaking onstage? And who is behind the curtain? |

notes_on_ambiguous_cases: (空、Metaは無し)

BORDERLINE参考語(10,000〜12,000位、判定対象外): understandable (10,629位)
— 候補にならず提示のみで、正しくLLMへ判定を求めなかった(閾値ライン機能の
確認、§7-1参照)。

Meta diff: Before/Afterの差分は1文のみ
(`Meta called these workers "human concierges."` →
`Meta called these workers "human operators."`)、他は一字も変わっていない
(unified diff全文は`meta_diff.md`)。word_count diff=0、sentence_count
diff=0、構造契約(見出し4行・段落数11)完全一致。

### §4 v2(fix01): Meta結果

Before/After: `er015_output/advanced_vocab_rule_trial_01/v2/meta_before.md`
/ `meta_after.md`。候補語はv1と変化なし(concierges/onstageの2語、
lemma化の影響を受けない語のため、`meta_candidates_diff.md`参照)。

Prompt v2のFact不変明確化(引用符内の語・組織が実際に使った呼称は事実であり
語彙置換の対象にしない旨を一般則として追加)を反映した結果、判定が変わった。

| Word | 採用Rank | 判定(v1→v2) | v2理由 |
|---|---|---|---|
| concierges | > 20,000 (extremely rare) | SIMPLIFY → **KEEP -- proper noun** | "Human concierges" is a designation that Meta actually used for these workers, so it is a quoted designation and must be kept exactly as reported. |
| onstage | 15,670 | KEEP -- predictable morphology/compound(変化なし) | 同左 |

v2 After本文はBeforeと完全一致(word_count diff=0、sentence_count diff=0、
構造契約完全一致)。`meta_fact_tokens_check.json`でも引用符内文字列
(`"human concierges."`等)・数値・大文字化語がBefore/Afterで完全一致
(`overall_fact_tokens_match: true`)を機械確認した。v1のFact変更見逃しは
解消された。全文Decision Log: `v2/meta_decision_log.md`。

## §5 Sewer Before/After/Decision Log

Before: `er015_output/advanced_vocab_rule_trial_01/sewer_before.md`
After: `er015_output/advanced_vocab_rule_trial_01/sewer_after.md`

### Sewer Decision Log

| Word | Frequency Rank | 判定 | 理由 | Before | After |
|---|---|---|---|---|---|
| septic | > 20,000 (zipf=3.21) | KEEP -- indispensable / natural replacement unavailable | "Septic tank" names a specific kind of household wastewater-treatment tank. Simpler alternatives such as "water-treatment tank" are broader or unnatural in these sentences. | (4文、`sewer_decision_log.md`参照) | (同上) |
| sewers | > 20,000 (zipf=3.22) | SIMPLIFY | In this context, "sewers" can be replaced naturally with simpler expressions referring to underground pipe systems. | (3文) | "underground pipe systems" / "these pipe systems" / "these systems" |
| artery | 12,006 | KEEP -- indispensable / natural replacement unavailable | The image of an artery is central to the article's metaphor of a system carrying water through the town. Replacing it with "pipe" or "line" would weaken that intended comparison. | (2文) | (変更なし、artery維持) |
| municipalities | 12,279 | SIMPLIFY | "Local governments" is a simpler, natural expression that preserves the meaning of "municipalities." | (2文) | "local governments" |
| sewer | 12,324 | SIMPLIFY | The infrastructure meaning of "sewer" is not reliably guessable from its parts in these sentences. | (2文) | "underground pipe systems" / "a network of underground pipes" |
| inspections | 12,446 | KEEP -- predictable morphology/compound | "Inspections" is readily understood from the common verb "inspect" and the predictable noun and plural forms. | Installation, inspections, and cleaning are still necessary. | (変更なし) |
| collects | 13,117 | KEEP -- predictable morphology/compound | This is the predictable third-person singular form of the common verb "collect." | It collects water from homes in underground pipes... | (変更なし) |
| wastewater | 18,216 | KEEP -- predictable morphology/compound | "Wastewater" is a transparent compound of the easy words "waste" and "water." | (タイトル+1文) | (変更なし) |

全項目のBefore/After文全文は`sewer_decision_log.md`に保存(表が横長のため
本REPORTでは代表文のみ抜粋)。

notes_on_ambiguous_cases: "'Septic' was a close call because it is a
technical term, but no simpler replacement is equally specific and
natural. 'Artery' was retained because replacing it would weaken the
article's central metaphor."

Sewer diff: unified diffで5文のみ変更(段落3・5・7・15・17)、いずれも
宣言されたSIMPLIFY語(municipalities→local governments、
sewer/sewers→underground pipe system(s)/pipes/these systems)の置換のみで、
それ以外の語・事実・順序・トーンは一字も変わっていない(`sewer_diff.md`)。
word_count diff=+11(単語1語→複数語のフレーズ置換のため増加)、
sentence_count diff=0、構造契約(見出しゼロ・段落数8)完全一致。

### §5 v2(fix01): Sewer結果

Before/After: `er015_output/advanced_vocab_rule_trial_01/v2/sewer_before.md`
/ `sewer_after.md`。lemma化により候補語数が8語→5語へ減少した
(`v2/sewer_candidates_diff.md`全文参照)。

| Word | v1候補? | v1 Rank(surface) | v2候補/BORDERLINE? | v2 採用Rank(min surface/lemma) | 変化 |
|---|---|---|---|---|---|
| municipalities | 候補(12,279) | 表層形12,279位 | **BORDERLINE参考語**(11,073) | lemma "municipality" 採用 | 候補から除外(前処理条件違反の是正) |
| collects | 候補(13,117) | 表層形13,117位 | 対象外(圏外) | lemma "collect" 3,802位 | 候補から除外(疑似候補だった) |
| inspections | 候補(12,446) | 表層形12,446位 | 対象外(圏外) | lemma "inspection" 5,694位 | 候補から除外(疑似候補だった) |
| sewers | 候補(zipf、表外) | 表外(rank無し) | 候補(継続) | lemma "sewer" 12,324位 | 変化なし(候補のまま、根拠がzipf推定→lemma実測順位に変わった) |
| septic / sewer / artery / wastewater | 候補(継続) | (各自順位) | 候補(継続) | 表層形=lemma(活用なし) | 変化なし |

v2 Decision(全5候補): SIMPLIFY 3語(septic/sewer/sewers)、KEEP 2語
(artery/wastewater)。

| Word | v1判定 | v2判定 | 備考 |
|---|---|---|---|
| septic | KEEP -- indispensable(v1) | **SIMPLIFY**(v2、→"treatment") | D境界のLLM判断が割れた(下記参照) |
| sewer | SIMPLIFY(v1)→"underground pipe systems"等 | SIMPLIFY(v2)→"underground pipe network" | 表現は変わったが判定は同じSIMPLIFY |
| sewers | SIMPLIFY(v1) | SIMPLIFY(v2) | 同上 |
| artery | KEEP -- indispensable(v1、比喩保持) | KEEP -- indispensable(v2、比喩保持) | **v1と同一結果**(§9のUSER_DECISION_REQUIRED論点は解消していない) |
| wastewater | KEEP -- predictable morphology(v1) | KEEP -- predictable morphology(v2) | 変化なし |
| municipalities/collects/inspections | v1でKEEP -- predictable/SIMPLIFYの判定対象だった | v2では候補外(判定不要) | lemma化修正の直接効果 |

v2でセプティック("septic")がv1のKEEPからSIMPLIFYへ変わり、"combined
septic tank" → "combined treatment tank" のように引用符内の語も含めて
置換された。この置換はSewer記事内で「ニュース報道で使われる可能性のある
用語の例」として引用符を使っている箇所であり(Metaの事例のような「実際に
特定の組織が使った呼称」の引用ではない)、septic自体がwordfreq
top20000圏外で日本語未定着・易しい語からの推測も困難なため、ルール上は
SIMPLIFY対象として妥当な判断である。ただし`sewer_fact_tokens_check.json`
は機械的に`quoted_strings_match: false`(引用符内文字列が変化)を検出した
(下記§6・§7-8参照、Sonnet目視で誤検知と判断)。

全文Decision Log: `v2/sewer_decision_log.md`(surface/lemma/rank列付き)。

## §6 AI判断が必要だった箇所

- **A(形態から推測可能)**: onstage/wastewater/inspections/collectsの4語
  すべてがA理由でKEEPされた。いずれも「易しい既知語からの規則的な派生・
  複合」であり、仕様の想定通りの判断(onstage=on+stage、
  wastewater=waste+water、inspections=inspect+ion+s、
  collects=collect+s)。
- **B(日本語定着語)**: 今回の10候補中、B理由でKEEPされた語はゼロ
  (piano/curtain/privacy等の既存B型語彙はいずれも12,000位以下のため
  候補にすら上がらなかった)。B判断そのものは今回未検証。
- **C(固有名詞)**: 今回の10候補中、C理由でKEEPされた語もゼロ(閾値超の
  固有名詞が両記事に存在しなかった)。C判断も今回未検証。
- **D(不可欠語)**: septic・arteryの2語がD理由でKEEPされた。septicは
  「"septic tank"という専門語で自然な代替が無い」という妥当な理由。
  一方artery は「記事中心比喩を守るため」という理由でKEEPされており、
  これはユーザーが期待として明記していた「artery型(12,000超・推測困難・
  日本語未定着)は原則平易化候補」という想定と**異なる結果**になった
  (§7-4・§9のUSER_DECISION_REQUIRED参照)。
- **平易化した語のニュアンス変化**: "sewer"/"sewers"を"underground pipe
  system(s)"等へ一律置換した結果、記事の中心語であった単語が本文から
  完全に消え、代わりに複数の言い換え表現("underground pipe systems" /
  "a network of underground pipes" / "these pipe systems" / "these
  systems")が反復して使われる形になった。文法・意味は正しいが、やや
  冗長で単調な繰り返しになっている(§7-7参照)。

### §6 v2(fix01): Fact変更見逃しの記録と再発防止チェック

- **v1のFact変更見逃し(concierges)**: v1のLLMは"human concierges"(Metaが
  労働者に実際に使った呼称、Reuters原文の事実)を通常の難語候補として扱い
  "human operators"へSIMPLIFYした。これはPromptのFact不変指示
  ("do not remove any fact")が一般的すぎて「引用符内・実際に使われた
  呼称は事実」という具体的適用範囲を明示していなかったことが原因と判断
  した。v2ではRULE_BLOCK_ENに一般則として1文追加し(新しい例外カテゴリ
  ではなく既存C[固有名詞]の適用範囲の明確化として)、`spec_candidate_ja.md`
  にも「Fableが明確化した点」として追記した(ユーザー仕様原文は不変)。
  v2の実行結果、concierges語は"KEEP -- proper noun"として正しく保持
  された(§4 v2参照)。
- **コード側Fact不変チェックの追加(修正D)**: Sonnet目視のみに頼らず、
  Before/After間で引用符内文字列・数値・大文字化語(固有名詞候補)が
  完全一致するかを機械的に検証する`fact_tokens_check`を追加した。
  Meta記事は`overall_fact_tokens_match: true`(完全一致)。Sewer記事は
  `quoted_strings_match: false`(1件、"combined septic tank" →
  "combined treatment tank")を検出したが、Sonnet目視の結果これは
  Metaの事例のような「実際の呼称の引用」ではなく「用語例を示すための
  引用符」であり、septicがルール上正当にSIMPLIFY対象だったための変化と
  判断した(誤検知)。この結果は、機械チェックが「引用符内変化」を
  もれなく検出できる一方、「その引用が事実の引用か、単なる強調の引用符か」
  の判別にはSonnet目視が引き続き必要であることを示している。

## §7 受入観点9項目のSonnet所見

1. **12,000ラインが機能したか**: 機能した。閾値超語(concierges/onstage、
   septic/sewers/artery/municipalities/sewer/inspections/collects/
   wastewater)が過不足なく候補として抽出され、閾値未満語(understandable
   10,629位)は候補に含まれず判定対象にもならなかった(コード側の
   フィルタが正しく作動)。
2. **onstage/understandable/wastewater型を不必要に簡易化していないか**:
   していない。onstage/wastewaterはA理由で正しくKEEP。understandableは
   閾値未満のためそもそもLLMへ判定を求めなかった(過剰動作なし)。
3. **piano/curtain型を難語扱いしていないか**: していない。piano(4,258位)
   ・curtain(8,776位)はいずれも12,000位を大きく下回るため今回候補にすら
   上がらず、閾値ラインが誤って難語扱いすることはなかった(確認済み、
   直接のB判定テストにはなっていない点は§6参照)。
4. **artery型を平易化候補にできたか**: 部分的成功。コード側の閾値
   メカニズムはartery(12,006位)を正しく候補として抽出できた(仕組みは
   機能した)。しかしLLMはD理由(中心比喩の保持)でKEEPを選択し、
   ユーザーが明記していた「artery型は原則平易化候補」という期待とは
   異なる結果になった。これは仕様候補の想定と実際のLLM判断が食い違った
   最も重要な発見であり、**USER_DECISION_REQUIRED**として報告する
   (「比喩保持」はD[意味精度・自然さ]の正当な適用範囲か、それとも
   artery型は比喩であっても平易化すべきという原則を明文化すべきか、
   ユーザー判断が必要)。
5. **例外判断の一貫性**: 一貫していた。Aは規則的形態変化・複合語のみに
   限定され、Dは「自然な代替が無い」「比喩を損なう」という具体的根拠を
   伴っていた。「定型表現だから」という理由単独での例外は一度も
   使われなかった(仕様の禁止事項を遵守)。
6. **例外過多で形骸化していないか**: 今回のサンプル(全10候補、
   SIMPLIFY 4/KEEP 6)では明確な過多の兆候はないが、n=10と小規模であり、
   B・C理由の使用例がゼロだったため「例外の全カテゴリが機能している
   かどうか」は統計的に確認できていない(カバレッジの限界)。
7. **過剰平易化でAdvancedらしさを壊していないか**: 軽度のリスクを観測。
   sewer/sewersの一律置換により、記事本文から"sewer"という単語自体が
   消え、"underground pipe systems"等の複数語フレーズが5文にわたって
   反復使用される結果になった。文法的には正しく意味も保たれているが、
   単語としての簡潔さ・自然な変化に富んだ語彙という点でAdvancedらしさが
   やや後退した可能性がある(致命的ではないが、Fable/ユーザーの確認材料)。
8. **Fact/Storytelling/意味不変か**: 不変。Sonnetがunified diffを両記事
   とも全行目視確認し、変更は宣言されたSIMPLIFY語の置換のみで、事実・
   順序・トーン・構造(見出し・段落数)に一切の変更がないことを確認した。
   word_count diff: Meta=0/Sewer=+11(単語→フレーズ置換による自然増)、
   sentence_count diff: 両記事とも0。
9. **Standardへ同じ例外原則を適用した場合の副作用所見(所見のみ、実装
   判断ではない)**: Standard側は現状Advancedよりはるかに厳しい頻度
   カットオフ(最頻出2,000〜6,000語程度)を使っている。A/B型の例外
   (規則的形態変化・定着した外来語)はStandardへ適用しても妥当に機能
   すると考えられるが、D型の「比喩保持のため残す」という例外は、A2
   読者にとって必要な語彙頻度遵守をStandardレベルで大きく損なうリスクが
   ある(artery型の語をStandardで残すのは通常望ましくないはず)。D例外は
   Advancedより厳格に運用するか、Standardでは実質的に無効化すべき、
   という所見のみ記録する(実装はしていない)。

### §7 v2(fix01)再評価

1. **12,000ラインが機能したか**: v2で更に改善確認。lemma化修正により
   municipalities(表層12,279位)がlemma "municipality"(11,073位)で
   BORDERLINE参考語へ正しく降格し、collects/inspectionsは候補からも
   BORDERLINE参考語からも完全に除外された(lemma順位がborderline帯
   10,000未満)。v1で発生していた「表層形の疑似候補」3語が解消された
   (`v2/sewer_candidates_diff.md`)。sewer/artery/septic/wastewaterは
   引き続き正しく候補として抽出された。
2. **onstage/understandable/wastewater型を不必要に簡易化していないか**:
   v1と同様、していない。onstage/wastewaterはA理由で正しくKEEP。
3. **piano/curtain型を難語扱いしていないか**: v1と同様、していない
   (今回未検証のまま、B判定の直接テストにはなっていない)。
4. **artery型を平易化候補にできたか**: **v1と同一結果、未解決**。v2でも
   artery(12,006位)はD理由(比喩保持)でKEEPされ、ユーザーが明記していた
   「artery型は原則平易化候補」という期待と食い違ったままである。fix01の
   2つの修正(lemma順位・Fact不変)はいずれもartery判定には無関係の論点で
   あり、修正後も再現したことで、これは実装のバグではなく仕様候補
   そのものの解釈論点(比喩保持をD例外に含めてよいか)であることが
   より明確になった。**USER_DECISION_REQUIRED継続**(§9)。
5. **例外判断の一貫性**: 一貫していた。v2でも「定型表現だから」という
   理由単独での例外は使われなかった。
6. **例外過多で形骸化していないか**: v2ではSewer候補が8→5語に減った分
   サンプルはさらに小さくなった(Meta+Sewer合計7候補、SIMPLIFY4/KEEP3)。
   B・C(固有名詞)理由の使用はゼロのまま(concierges語はC[固有名詞]の
   拡張適用[引用された呼称]でKEEPされたが、通常の固有名詞ケースではない)。
   カバレッジの限界は引き続き残る。
7. **過剰平易化でAdvancedらしさを壊していないか**: v1と同様の軽度リスクに
   加え、v2ではseptic→treatmentへの新規SIMPLIFYが発生し、"septic tank"
   という具体的な専門語が本文から消えた。文法・意味は保たれているが、
   D境界の判定がLLM実行ごとに揺れうること(v1:septic KEEP、v2:septic
   SIMPLIFY)を示す実例であり、D例外の再現性には限界があることが分かった
   (§6参照)。
8. **Fact/Storytelling/意味不変か**: v2で強化確認。concierges(Meta)は
   `fact_tokens_check`で完全一致、Sewerの引用符変化は目視でルール上正当な
   SIMPLIFYと判断した。両記事ともunified diff全行をSonnetが目視確認し、
   宣言されたSIMPLIFY語の置換以外に変更がないことを確認した。
   word_count diff: Meta=0/Sewer=+9(v1は+11、候補減少に伴い縮小)。
   sentence_count diff: 両記事とも0。
9. **Standardへの副作用所見**: v1の所見(D例外はStandardでは実質無効化
   すべき)は変わらない。加えて、v2で判明したD境界判定の揺れ
   (septicの例)は、D例外をStandardへ適用する場合はより厳格な運用基準
   (例: 複数回生成しての多数決、または禁止)が必要という追加所見となる
   (実装はしていない)。

## §8 QCD(cost/時間/失敗)

- Cost: 合計 JPY 1.7362(Meta=0.275円、Sewer=1.4612円)、予算上限
  JPY 5以内。`er015_output/advanced_vocab_rule_trial_01/cost.json`。
- 時間: Meta 19.983秒、Sewer 118.368秒(候補語数8個・reasoning
  tokens=5,696のため長め)。
- 失敗: リトライ0回、fallback検出0回、schema parse失敗0回。両記事とも
  1回のcallで完了(実行前に定めた「1記事あたり生成1回、技術的失敗時
  のみ再試行1回」の上限内)。

### §8 v2(fix01)cost累計

- v2 Cost: 合計 JPY 1.9875(Meta=0.2437円、Sewer=1.7438円)。
  `er015_output/advanced_vocab_rule_trial_01/v2/cost.json`。
- **累計(v1+v2)**: JPY 3.7237(予算上限JPY 5以内、`within_budget: true`)。
- v2時間: Meta 14.728秒、Sewer 137.366秒(v1のSewerと同程度、候補5語で
  reasoning tokens多め)。
- v2失敗: リトライ0回、fallback検出0回、schema parse失敗0回。両記事とも
  1回のcallで完了。

## §9 Sonnet仮分類

**USER_DECISION_REQUIRED**

根拠:
- 仕組み自体(閾値抽出・A/D判断・構造保持・Fact不変)は概ね期待通りに
  機能し、REJECTEDと判定する技術的欠陥は見つからなかった。
- しかし、ユーザーが仕様候補の核心的な期待として明記していた
  「artery型(12,000超・推測困難・日本語未定着)は原則平易化候補」が、
  実際のLLM判断ではD理由(比喩保持)でKEEPされ、想定と食い違う結果に
  なった。これは仕様候補そのものの解釈(比喩保持をD例外に含めてよいか)
  に関わる論点であり、Sonnet単独では「VALIDATED」と判断できない。
- B/C例外(日本語定着語・固有名詞)が今回のサンプルでは一度も出現せず
  未検証のため、仕様候補全体をVALIDATEDと断定する根拠も不足している。
- ユーザー判断が必要な論点: (1) artery型の「比喩保持によるKEEP」は
  許容するか、それとも仕様の期待通り平易化を強制すべきか、(2)
  sewer/sewers一律置換による語彙反復(§7-7)は許容範囲か、(3) B/C例外の
  追加検証(他記事でのTrial)が必要か。

### §9 v2(fix01)再判定

**USER_DECISION_REQUIRED(継続)**

根拠:
- fix01で指摘された2つの技術的欠陥(表層形順位による前処理条件違反、
  Fact変更見逃し)はいずれもv2で修正され、実測evidenceで解消を確認した
  (§3-§6)。municipalities/collects/inspectionsの疑似候補化は解消、
  concierges(Meta)は"human concierges"というMetaの実際の呼称として
  正しくKEEPされた。
- しかし、v1の差し戻し理由には含まれていなかったが、fix01実行後も
  **artery型のD理由(比喩保持)によるKEEP**というユーザー期待との食い違い
  (v1 §9で最初に報告)はv2でも完全に同一の結果で再現した。これは
  lemma化・Fact不変チェックのどちらの修正とも無関係な、仕様候補
  そのものの解釈論点であり、Sonnet単独では判断できない。
- 加えてv2で新たに判明した所見として、D境界の判定(septic)がLLM実行
  ごとに割れうること(v1:KEEP、v2:SIMPLIFY)を確認した。これは技術的
  欠陥ではなく「意味・自然さを損なう不可欠語」の判定が本質的に主観的
  境界を含むことを示す実例であり、D例外の運用基準(単発生成で確定
  させてよいか)についてもユーザー確認材料として追記する。
- ユーザー判断が必要な論点(v1から継続): (1) artery型の「比喩保持による
  KEEP」は許容するか、それとも仕様の期待通り平易化を強制すべきか、(2)
  sewer/sewers一律置換による語彙反復は許容範囲か、(3) B/C例外の追加検証
  (他記事でのTrial)が必要か。
- 追加論点(v2で判明): (4) D例外(意味・自然さを損なう不可欠語)の判定が
  実行ごとに割れる場合(septic型)、Production化する際にどう安定させるか
  (複数回生成・多数決・D例外の対象を限定するなど)。

## §10 [Fable記入]

## §11 [Fable記入]
