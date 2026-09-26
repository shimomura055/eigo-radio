# NEWS-FAMILY-X-SECTION-SEGMENTATION-SPEC-DESIGN-01: 見出し境界の一般仕様設計

管理ID: NEWS-FAMILY-X-SECTION-SEGMENTATION-SPEC-DESIGN-01
性質: 設計doc(read-only調査、コード・Prompt・SSOT変更なし、API ¥0)
対象: Family X(日本語Entertainment記事→Advanced[Natural English Adaptation,
CEFR B1]→Standard A2)。ユーザー要求は「各Sectionの見出しより前に、その
Sectionで本格的に扱う内容を先取りして書かないこと」の一般仕様設計。
本docは採否を書かない(Fableレビュー後、適用Agentへ渡す前提)。

---

## §1 現状(見出しが生成される工程の逐語引用)

### 1.1 Advanced(Natural English Adaptation、CEFR B1)

出典: `er003_v1_n3_01_advanced_adaptation_generate.py`

見出し・構造契約は`ADVANCED_CONTRACT_SUFFIX_LINES`(行210–218)で以下の
通り与えられている(この文言は`NEWS-ENTERTAINMENT-PRODUCTION-LINE-
TRIAL-01`のCONTRACT_LINESと一字一句同一、行208–209のコメント参照)。

```
Write in English.
Length: about 280–420 words in total.
Format (Markdown): start with "# " followed by the title; then the
main story; then exactly two "### " subsections, each 30–60
words, with headings that describe their content in your own words
(do not use labels like "Point One"); then a final section headed
exactly "## In one line" containing one sentence.
```

`build_prompt()`(行261–270)は、このcontract suffixを
`common_block_general`(Preserve指示、行262–265)+`ADVANCED_ARM3_BLOCK`
(Natural English化の指示、行110–117)+`ADVANCED_VOCAB_RULE_V2_BLOCK`
(語彙難易度ルール、行144–187)の後、日本語記事本文の前に連結する
(行266–270)。

現状のこれらの文言には、「見出しの前に何を書いてよいか/書いてはいけな
いか」という指示は一切存在しない。見出し数(ちょうど2つ)と各節の語数
(30–60語)、見出し文言の自作(ラベル禁止)だけが規定されている。

### 1.2 Standard(A2、v5、`APPROVED_FOR_PRODUCTION` 2026-09-25)

出典: `er003_v1_n3_01_standard_a2_generate.py`

`STANDARD_A2_PROMPT_V5`(行100–127)中、構造維持契約は行122の1行のみ:

```
Keep the same Markdown structure (the "# " title, the two "### " sections, and the final "## In one line" section); do not add or remove sections.
```

この行は`NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01`(delegation D3、
行129–139のコメント)で追加されたもので、「見出し数・種類を保つ」ことは
規定するが、「見出しをまたいで内容を移動してよいか」には触れていない。
`build_prompt()`(行172–173)はこのテンプレートに`{advanced_article}`を
埋め込むのみ。

### 1.3 既存の機械チェック(見出し関連)

`er002_ja_free_markdown_restore_r2.validate_point_structure()`
(行58–87)は、`### `見出しの数がちょうど2つであること・各見出しが
空でないこと・各見出し直後の本文が空でないことだけを正規表現で検査する
(行62–86)。見出し直前の内容(先取りの有無)は一切見ない。

この関数は`er003_v1_en_direct_vfl_01_generate.run_writer_with_
technical_retry()`(行403–431)から呼ばれ、`STRUCTURE_PASS`でなければ
最大2回まで同一Promptで再生成する(行426–430)。つまり既存のretry/Gate
機構は「見出し数と空でないこと」しか強制しておらず、本タスクが扱う
先取り問題を検出する仕組みは現状どこにも存在しない。

結論: 先取り問題は、Prompt文言に「見出し前後の内容の切り分け」という
指示自体が存在しないことに起因する。Checker追加ではなくPrompt/Contract
文言の追加が最初の妥当な対策である(タスク前提と整合)。

---

## §2 実態調査(既存記事、見出し直前段落の先取り分類)

対象10本(Family X 5本 + Family A 5本)。各見出しについて、見出し直前
段落の最終1〜2文を抜き出し、以下の3分類で判定した。

- **先取り(NG)**: 直前の文が、次Sectionが本格的に扱う新しい出典名・
  数値・引用・具体例・中心的主張を述べている。
- **Bridge/予告(許容)**: 話題転換を示すが、次Sectionの具体的内容には
  踏み込まない(締め・疑問形・一般的な言い換え)。
- **該当なし**: 直前の文は現Sectionの内容の続き/締めであり、次Sectionへ
  の言及自体がない(見出しが唐突に始まる、いわゆるhard cut)。

| # | 記事 | 見出し | 直前文(抜粋) | 判定 | 理由 |
|---|------|--------|--------------|------|------|
| 1 | Family X / meta(`er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md`) | 見出し1「The hidden person behind the AI sign」 | 「When people share their names, plans, or personal circumstances, knowing who is on the other end matters.」(行15) | 該当なし | 一般論の締め。次Section固有の出典名・具体例(テスト開始時の告知不足など)への言及なし。 |
| 2 | 同上 | 見出し2「Meta admits a mistake」 | 「The more useful the feature, the more people will want to know whether the other side is AI or human.」(行23) | Bridge/予告 | 疑問提起型。次Sectionの具体内容(Meta幹部の発言、機能停止)は述べていない。 |
| 3 | Family X / meta(`.../a2/article.md`、Standard) | 見出し1・2とも | Advancedと同位置・同内容の言い換え(行15, 23) | 該当なし/Bridge/予告 | Advancedの境界を維持(見出しをまたぐ内容移動なし)。 |
| 4 | Family X / small_bag(`er019_output/family_x_b3_diversity_trial_01/small_bag/run_01/b1b/article.md`) | 見出し1「Mini bags are there to set the scene」 | 「In terms of carrying space, they are not trying to compete with large-capacity bags.」(行9) | 該当なし | 現Section(ELLEの記事内容)の締め。次Sectionの具体的内容への言及なし。 |
| 5 | 同上 | 見出し2「Large bags are still doing their job」 | 「Yet this does not mean large bags have vanished. **Vogue** also covered a wide range of bags in the same 2026 season.」(行15) | **先取り(NG)** | 見出し2で初めて扱われるはずの新しい出典名「Vogue」が、見出しの直前の文で既に導入されている。見出し直後の本文(行19)はそのままVogueの具体的な掲載内容(ブランド名列挙)に入るため、「Vogueの記事」という次Sectionの主題そのものが見出し前に漏れている。 |
| 6 | Family X / small_bag(`.../a2/article.md`、Standard) | 見出し2 | 「Still, large bags have not disappeared. Vogue also showed many kinds of bags in that 2026 season.」(行17) | 先取り(NG、Advancedを踏襲) | AdvancedのNG箇所がStandardにもそのまま引き継がれている(構造維持契約により境界は保たれているが、先取り自体はAdvanced由来でStandard生成では解消されない)。 |
| 7 | Family X / hormuz(`er019_output/family_x_b3_diversity_trial_01/hormuz/run_01/b1b/audit/rejected_advanced_attempt2.md`、Ledger逸脱によりREJECTED) | 見出し1「The fee disappeared, but prices stayed high」 | 「At this point, you might expect crude oil prices to fall. But they did not.」(行13) | Bridge/予告 | 疑問形の裏返し。具体的な数値・出典名(Brent、$85等)は見出し後(行17)。 |
| 8 | 同上 | 見出し2「The market was watching the danger at sea」 | 「At the time of reporting, they were about 2.6% higher, above $85 a barrel.」(行17) | 該当なし | 現Section(価格の動き)の締め。次Section固有の内容(市場心理の解釈)への言及なし。このrejected記事の却下理由は`deviation_check.json`の通りLedger逸脱(因果・確信度の拡張、行1–54)であり、見出し境界の先取りではない。 |
| 9 | Family A / discovery(`er014_output/four_type_observation_01/discovery/b1b/article.md`) | 見出し1「When Quiet Has Structure」 | 「...while Americans did not show that difference.」(行17) | 該当なし | ブリッジ文なしの直接cut。次Section固有の実験名・数値への言及なし。 |
| 10 | 同上 | 見出し2「Context Over Country」 | 「Quiet can therefore function differently when people have agency and a mental path to follow.」(行21) | 該当なし | 現Sectionの結論文。次Sectionの固有名(Japanese and UK undergraduates等)への言及なし。 |
| 11 | Family A / news(`er014_output/four_type_observation_01/news/b1b/article.md`) | 見出し1「Regulation is a map, not one stop sign」 | 「At the same time, companies and governments still want faster development and deployment.」(行13) | 該当なし | 一般論の締め。 |
| 12 | 同上 | 見出し2「Who decides how fast is fast enough?」 | 「The UN panel can assess the gap, but it cannot enforce a rule.」(行17) | 該当なし | 現Section(規制)の結論。次Section固有の企業名(OpenAI/Anthropic/Google)は見出し後(行21)で初出。 |
| 13 | Family A / news(`.../a2/article.md`、Standard) | 見出し1・2とも | Advancedと同位置(行19, 23) | 該当なし | Advancedの境界を維持。 |
| 14 | Family A / trend(`er014_output/four_type_observation_01/trend/b1b/article.md`) | 見出し1「From tapping through apps to handing over a task」 | 「They show something quieter: the phone is becoming one doorway among several.」(行11) | Bridge/予告 | 要約的だが、Google/Amazonの個別の新規具体例はMain Story側(行5–9)で既出済みであり、見出し1で新規に出典が漏れているわけではない(下記注参照)。 |
| 15 | Family A / ai_control(`er014_output/user_test_news_2ep_01/ai_control/a2/article.md`) | 見出し1「The boundary is bigger than the model」 | 「...experts remain uncertain and divided about its likelihood and severity.」(行17) | 該当なし | 一般論の締め。次Section固有の具体例(15 real systemsのテスト等)は見出し後(行21)。 |
| 16 | 同上 | 見出し2「Trust what is observed, not only what is said」 | 「Network paths, passwords, and permissions are part of control too.」(行21) | 該当なし | 現Sectionの締め。 |

**先取り発生率と典型パターン**: 上記16見出しペア中、明確な先取り(NG)は
2件(#5, #6。実質1箇所の問題がAdvanced→Standardへ伝播した1事例)のみ。
発生した唯一のパターンは「**次Sectionが主として依拠する新しい出典名
(メディア名・機関名)が、見出し直前の1文で初めて名指しされ、見出し後の
本文がそのままその出典の具体的内容[今回はブランド名列挙]に入る**」
というものだった。数値・引用文そのものの先取り事例は今回のサンプルには
見られなかったが、出典名と同様のパターンで発生し得る(§3のContract文は
出典名に限定せず一般化する)。

**Family A(er014)と Family Xの構造差の注記**: Family A(discovery/news/
trend/ai_control)は、Main Story部分で複数の出典・企業名を先に総覧し、
各`### `Sectionはその中の一部を深掘りする構成が多い(#14参照)。この場合
「出典名が見出し前に出る」こと自体は先取りではない(Main Storyの時点で
既に読者に開示されている情報を、Sectionが深掘りするだけ)。一方Family X
のsmall_bag(#5)は、ELLE(見出し1の主出典、Main Story側で既出)とは別に
Vogue(見出し2で初めて主題になる出典)が、見出し2の直前という「Section 2
に閉じた1文」の中で初出してしまった点が問題である。したがって判定基準は
「出典名が記事のどこかで見出しより前に出たか」ではなく、**「その
Sectionが本格的に依拠する出典・具体例・数値・引用が、そのSectionの見出し
の直前の文(=そのSectionのための移行文)で初めて名指しされ、見出し後の
本文がそれをそのまま展開しているか」**に置くべきである。

---

## §3 一般仕様の設計(Contract文、英語、Prompt追加用)

Fable素案(定義・規則・自己チェック・Bridge許容・見出し位置)を§2の実データ
で検証した結果、以下の点を確認した。

- 素案の核心規則(「次Sectionの最初の具体的な内容は見出しの後」)は、
  実際に観測された唯一のNG事例(出典名の先取り)と正確に対応しており、
  有効である。
- 素案の自己チェック2問(見出しを消しても分かるか/新しい出典名・数値・
  引用・具体例が含まれるか)は、そのまま使える。
- ただし素案は「出典名」を主眼にしていたが、§2の注記の通り「記事の
  どこかで見出しより前に出たか」ではなく「そのSectionのための移行文
  (見出し直前の1文)で初めて名指しされ、見出し後の本文がそれを展開して
  いるか」という限定を明示しないと、Family A型(Main Storyで先に出典を
  総覧する構成)を誤って先取りと判定しかねない。この限定を追記した。
- small_bag固有語(mini bag/large bag/ELLE/Vogue等)は一切含めず、一般
  トピック用の抽象語(source/example/figure/quotation)のみを用いた。

### 3.1 Advanced Prompt用 Contract文(新規独立ブロック、既存
`ADVANCED_CONTRACT_SUFFIX_LINES`は無変更のまま別ブロックとして追加する
想定。理由: 既存文言は`NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01`の
CONTRACT_LINESと逐語一致がsha256で固定されており、他Production Lineとの
共有契約文そのものを書き換えると無関係な既存sha256/整合性チェックを
壊すため)

```
Section boundary rule: each "### " heading marks where its section
begins. The first concrete point a section makes -- its main source,
example, figure, or quotation -- belongs after that section's own
heading, not before it.

Right before a "### " heading, you may close the point you were just
making, and, if it helps the flow, add one bridging sentence that
signals a shift is coming (for example, a closing remark, or a
question you do not yet answer). This bridging sentence must not name
the specific source, example, figure, or quotation that the upcoming
section is about to build on, and must not state the upcoming
section's main point.

Self-check for every heading before you finish: (1) If this heading
were deleted, would the sentence right before it already give away
the section's first concrete point? If yes, move that sentence to
after the heading. (2) Does the sentence right before this heading
name the specific source, example, figure, or quotation that this
section is built on? If yes, move it to after the heading.

A heading should open its own section with a new concrete point, not
restate the point that was just made.
```

### 3.2 Standard Prompt用 維持契約文(既存行122の直後に追記する新規
1文の想定。既存「Keep the same Markdown structure...; do not add or
remove sections.」は無変更のまま、以下を追加する)

```
Keep every fact, example, figure, quotation, and named source in the
same section as in the original article: before or after the same
"### " heading as before. Do not move a sentence across a "### "
heading boundary in either direction, and do not move a section's
first concrete point to before its own heading.
```

この1文は「見出しをまたぐ内容移動の禁止」を明示することで、ユーザー
要求「Standard(A2)は見出しの位置と見出しをまたぐ内容移動を禁止し、
Advancedの境界を維持する」を直接満たす。既存のsimplification指示
(語彙・文長)には一切触れない。

### 3.3 既存Prompt文言との整合確認

- Advanced既存文言に「見出しの前後」を規定する記述は無い(§1.1)ため
  矛盾・重複なし。追加ブロックは既存`ADVANCED_CONTRACT_SUFFIX_LINES`の
  「Format」規定(見出し数・語数・ラベル禁止)を補完する位置づけで、
  同じ規定領域(見出し文言のin your own words)と衝突しない。
- 既存`ADVANCED_COMMON_BLOCK_SUFFIX`(行102–107)の「Keep every fact
  exactly as in the Japanese article」とは別レイヤー(Fact保持 vs
  配置場所)であり矛盾しない。
- Standard既存行122とは同一文の直後に追記する設計のため、文脈上自然に
  接続し、既存の「do not add or remove sections」という数の制約と
  「移動しない」という位置の制約は補完関係にある。
- どちらの追加文もsmall_bag固有語・具体的記事名を含まない一般形。

---

## §4 回帰計画

適用前後で確認すべき項目(既存の安全装置を利用し、新規Checkerは追加
しない):

1. **構造Gate(既存)**: `validate_point_structure()`が引き続き
   `STRUCTURE_PASS`を返すこと(見出し数=2、各見出し非空、各本文非空)。
   Contract追加によって見出し数・ラベル規則が変わるわけではないため、
   回帰しないはずだが、追加文により出力形式が乱れていないかを実測で
   確認する。
2. **語数契約**: Advanced全体280–420語、各`### `節30–60語(既存
   `ADVANCED_CONTRACT_SUFFIX_LINES`)。Bridge文1文の追加余地により
   各節が語数上限を超えないか確認する。
3. **Fact tokens diff(既存)**: `extract_fact_tokens()`/`run_checks()`
   (`er003_v1_n3_01_standard_a2_generate.py`行230–269)による数字・
   固有名詞候補の追加/欠落チェック。Standardの追加契約文により、
   Advanced→Standardで数字・固有名詞が新たに欠落/追加されていないかを
   確認する(既存の仕組みをそのまま流用、判定基準は変えない)。
4. **Ledger逸脱チェック(既存)**: `DEVIATION_FLAG_KEYS`ベースのv2判定
   (`er003_v1_en_direct_vfl_01_generate.py`行448以降)。境界指示の追加が
   新たなLedger逸脱(意味の変更)を誘発しないか、既存の10種フラグで
   確認する。
5. **見出し数・境界判定表**: §2と同じ形式(直前文抜粋+分類)を、
   Contract適用後の同一記事(再生成時)・新規記事で再作成し、先取り
   (NG)が解消しているか、Bridge/該当なしの比率がどう変化したかを
   記録する。
6. **正常ケースへの回帰確認**: §2で「該当なし」「Bridge/予告」と判定
   済みの記事(Family X meta、Family A discovery/news/trend/ai_control、
   計8見出し)を同条件で再生成し、(a) 見出し位置が変わらないこと、
   (b) 各Sectionの内容(Fact tokens)が変わらないこと、(c) 新たな先取り
   が発生しないこと、を確認する。Contract追加が「問題のない記事にまで
   不要な書き換え(over-correction)」を起こさないことの確認が目的。
7. **small_bag再Trial手順(既知NG)**: `er019_output/family_x_b3_
   diversity_trial_01/small_bag/run_01/ja_writer/revision2.md`(既存の
   完成R2、行の変更なし)を入力に、
   `er003_v1_n3_01_advanced_adaptation_generate.py --ja-file
   .../small_bag/run_01/ja_writer/revision2.md --out-dir <new_dir>`で
   Advancedを`--regenerate-stage advanced`相当(既存run one-off、
   Production runnerへの新規配線はしない)として再生成し、見出し2直前に
   「Vogue」等の新規出典名が漏れていないかを§2と同じ判定基準で確認する。
   合格後、その出力を`er003_v1_n3_01_standard_a2_generate.py
   --advanced-file <regenerated_advanced> --out-dir <new_dir>`へ渡し、
   Standardでも先取りが再現しない/境界が保たれることを確認する。

---

## §5 Prompt以外(追加mechanism)が必要になる条件(判定基準の提案のみ)

以下のいずれかに該当した場合、「Prompt文言の追加だけでは不安定」と
判定し、追加mechanism(例: 見出し直前1文の機械チェック)の要否検討を
Fable/ユーザーへ提案する(本docでは追加mechanism自体は提案しない)。

- **条件A(残存)**: §4-5/§4-7の回帰Trialにおいて、Advanced・Standard
  合わせて2記事×2レベル(4回の生成)を実施した中で、先取り(§2定義の
  NG、出典・具体例・数値・引用の見出し前への漏れ)が1件でも残る場合。
- **条件B(over-correction)**: §4-6の正常ケース再生成(既存「該当なし
  /Bridge」判定済みの見出し、計8件)のうち、1件でも見出し位置の移動・
  Fact tokensの増減・新たな先取りの発生が観測された場合(Contract追加が
  無関係な記事にまで書き換えを誘発したことを意味する)。
- **条件C(語数逸脱)**: 追加したBridge許容規定により、`### `節の語数が
  既存契約(30–60語)を、Contract追加前には見られなかった頻度で外れる
  場合(具体的な閾値はFableが回帰実測データを見て決定する。本docでは
  「Contract追加前後で語数逸脱率が悪化したこと」自体を条件とする)。
- **条件D(構造Gate逸脱)**: 追加したContract文により`validate_point_
  structure()`の`STRUCTURE_PASS`率が、Contract追加前の既存実測値より
  悪化する場合。

---

## §6 参照

- Advanced Prompt: `er003_v1_n3_01_advanced_adaptation_generate.py`
  (行1–270、特に行74–270)
- Standard Prompt: `er003_v1_n3_01_standard_a2_generate.py`
  (行1–234、特に行94–234)
- 既存構造Gate: `er002_ja_free_markdown_restore_r2.py`(行58–87)
- 既存retry primitive: `er003_v1_en_direct_vfl_01_generate.py`
  (行403–431、Ledger逸脱チェックDEVIATION_FLAG_KEYSは行448以降)
- Family X実データ:
  - `er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md`
  - `er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md`
  - `er019_output/family_x_b3_diversity_trial_01/small_bag/run_01/b1b/article.md`
  - `er019_output/family_x_b3_diversity_trial_01/small_bag/run_01/a2/article.md`
  - `er019_output/family_x_b3_diversity_trial_01/hormuz/run_01/b1b/audit/rejected_advanced_attempt2.md`
  - `er019_output/family_x_b3_diversity_trial_01/hormuz/run_01/b1b/audit/deviation_check.json`
  - `er019_output/family_x_b3_diversity_trial_01/small_bag/run_01/ja_writer/revision2.md`(§4-7 再Trial入力)
- Family A実データ:
  - `er014_output/four_type_observation_01/discovery/b1b/article.md`
  - `er014_output/four_type_observation_01/news/b1b/article.md`
  - `er014_output/four_type_observation_01/news/a2/article.md`
  - `er014_output/four_type_observation_01/trend/b1b/article.md`
  - `er014_output/user_test_news_2ep_01/ai_control/a2/article.md`
