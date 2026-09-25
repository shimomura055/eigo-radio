# ADVANCED-VOCAB-RULE-TRIAL-01_REPORT.md

管理ID: NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 / Phase 2 =
ADVANCED-VOCAB-RULE-TRIAL-01(Sonnet実行、2026-09-25)

Production実装ではない。Trialのみ。Production Prompt/Validator/
Production path/SSOTへは一切実装していない。Standard側への反映もしていない
(所見のみ§7-9に記載)。

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

## §8 QCD(cost/時間/失敗)

- Cost: 合計 JPY 1.7362(Meta=0.275円、Sewer=1.4612円)、予算上限
  JPY 5以内。`er015_output/advanced_vocab_rule_trial_01/cost.json`。
- 時間: Meta 19.983秒、Sewer 118.368秒(候補語数8個・reasoning
  tokens=5,696のため長め)。
- 失敗: リトライ0回、fallback検出0回、schema parse失敗0回。両記事とも
  1回のcallで完了(実行前に定めた「1記事あたり生成1回、技術的失敗時
  のみ再試行1回」の上限内)。

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

## §10 [Fable記入]

## §11 [Fable記入]
