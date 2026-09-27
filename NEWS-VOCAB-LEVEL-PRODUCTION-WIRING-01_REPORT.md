# NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01_REPORT.md (Stage 2)

管理ID: `NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`(Stage 2)
実行者: Sonnet(サンドイッチ委任、初回)
日付: 2026-09-27
性質: ユーザー正式採用済み仕様(Standard/A2は生成の最初から6,000語レベルを
中心に、文章・構文自体も簡易化する。事後の一語ずつ機械的置換ではない)の
Production配線+runtime evidence。Phase 0事前調査は
`docs/pm/recon_vocab_level_production_wiring_01.md`(Sonnet、2026-09-26、
read-only)。

## §0 要約

`er003_v1_n3_01_standard_a2_generate.py`のStandard A2 v5語彙段落(旧
「Prefer words within roughly the 6,000...」〜「...stage, backstage, lead
role, curtain).」の7行)を、`STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01`
(VALIDATED)Prompt Bの生成一体型原則+firmな6,000語Band+3除外条件のみ
(固有名詞/推測容易な派生・複合語/日本語定着語、カテゴリ記述のみ・個別
英単語例なし)の6行へ置換した。Advanced側`ADVANCED_VOCAB_RULE_V2_BLOCK`
(A〜D方式、12,000閾値)は無変更のまま維持を確認。Meta記事の正式path
再生成で構造Gate PASS・deviation COMPLIANT・語数±10%以内・Fact tokens
一致を確認。Hormuz(技術語彙が多い難ケース)では、Advanced段の残存難語
(Reuters/Brent/Strait/Hormuz等の固有名詞を除く"crude"/"blockade"/
"tanker"/"shipments"/"withdrawal"等)がStandard側でも同数残存する
という観察知見(§3.4)を得た。Fact/Story/構造は壊れておらず受入条件は
満たすが、「firm」な6,000語Bandの実効性については限定的な証跡であり、
Fable/ユーザーの追加判断材料として報告する。**PRODUCTION_WIRED判定は
Fable/ユーザー**。

## §1 差分(Prompt diff全文)

`er003_v1_n3_01_standard_a2_generate.py`から新規named定数
`STANDARD_A2_NEW_VOCAB_BLOCK`を切り出し、`STANDARD_A2_PROMPT_V5`の
旧語彙段落と置換した(構文簡易化行[平均文長9-11語・1文1アイデア等]・
Fact/Story保持行・構造保持行は無変更のまま維持)。

### 旧語彙段落(7行、削除)

```text
Prefer words within roughly the 6,000 most common English words.
If a word is clearly outside that range, replace it when a simpler natural alternative exists.
Do not force a replacement if it makes the sentence less natural or changes the meaning.
Proper names are excluded from this rule.
Essential technical terms may remain when a simpler equivalent would lose important meaning.
Do not add an explanation for a hard word; make the sentence around it simple instead.
Keep the metaphor words when they are simple enough for A2 learners (for example, stage, backstage, lead role, curtain).
```

### 新語彙段落(`STANDARD_A2_NEW_VOCAB_BLOCK`、6行、追加)

```text
As a basic principle, write naturally using words within roughly the top 6,000 most common English words. Do not generate a hard word first and then swap out only that one word afterward; instead, from the first draft, build the whole sentence around simpler words so its meaning is expressed naturally from the start.
Do not change the meaning: keep the same action, cause and effect, actor, object, quantity, time, and facts.
Do not escape one hard word by repeatedly adding long, unnatural explanatory phrases; that makes the writing heavy. Keep it light and direct, the way the rest of the article already reads.
Keep the storytelling: this is not a summary. Do not cut an interesting detail or part of the storyline, and do not mechanically remove a metaphor. Simplify only the wording, not the story.
A word outside the top 6,000 words may still stay if any of the following applies: (1) it is a proper noun -- a person's name, a company or product name, a place name, or an official title; (2) its meaning can easily be guessed from an easier word, or word parts, that it is built from; (3) it is a word that has become well established in Japanese and whose meaning is easily connected to its English pronunciation.
Judge this naturally as you write; do not sort every word into a fixed label, and do not list candidate words or output a per-word classification. Writing one naturally good CEFR A2 article matters more than labeling exceptions.
```

出典・根拠: `STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01`
(`er015_standard_a2_6000_generation_first_trial_01.py`
`_NEW_VOCAB_BLOCK_GEN_FIRST`、VALIDATED)を土台に、Fable/ユーザー承認の
3点を修正: (i) Trial Bの単一混在例外文(固有名詞/主題必須語/意味精度
必須語を1文に混在、「Do not sort each word into fixed exception
categories」という自己矛盾を含む)を、ユーザー確定の3条件(固有名詞/
推測容易な派生・複合語/日本語定着語)の明示列挙へ置換、(ii) Trial Bの
記事固有個別語例(`"flush"→"use"`)を削除(一般Prompt本体には一切の
個別英単語例を含めない)、(iii) 最終行を「per-word classification/label
を出力しない」という趣旨を保ちつつ矛盾を解消する形に調整。10,000/14,000
語Band・A/B/C/D事後置換方式は不採用のため一切含まない。

sha256: `STANDARD_A2_PROMPT_SHA256`
= `cbe73fc46f2c3c57c087c521df132ed734b8967a6ef09338c187349d35fecc33`
(旧値: `ff860ab60a0d1d4ffa4e93a30e53af37fe87afa8c4e01a99bf54e06897a42353`)。
この新値は本タスクの語彙段落置換+
`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`の境界維持1文
追加の**両方**を合算した値(同一セッション内で同一Prompt文字列へ両方の
変更を適用したため、Prompt定数は1つ)。境界維持1文自体の詳細は
`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01_REPORT.md`
§1.2を参照。

### Advanced側は無変更(確認のみ)

`er003_v1_n3_01_advanced_adaptation_generate.py`の
`ADVANCED_VOCAB_RULE_V2_BLOCK`(A〜D方式、12,000閾値)・
`ADVANCED_VOCAB_RULE_V2_SHA256`
(`d536f4b8a7780771232a95d35611606262d8041371ad8d0a1a4563b7948fb581`)は
**無変更**。6k生成制約はAdvancedにかけていない(既存
`ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01`のpost-processが引き続き適用
されることを、Hormuz/Meta双方の実runで確認、§3参照)。

## §2 Tests

- `er003_v1_n3_01_standard_a2_generate_test_01.py`: 27件PASS。新規
  `NewVocabBlockTests`(8件): 「As a basic principle」の存在(firm/原則
  wording)、3除外条件の文言存在、生成一体型/意味不変/Storytelling維持の
  文言存在、A/B/C/Dラベル・KEEP-A等マーカー不在、10,000/12,000/14,000
  不在、個別英単語例(wastewater/surprisingly/piano/curtain/onstage/
  understandable/privacy/flush/"stage, backstage")不在、Trial名
  (Generation-First/GEN_FIRST/Trial)・Topic Core/is_metaphor/BORDERLINE/
  exception_used不在、構文簡易化行(Rebuild the sentences/Aim for an
  average sentence length/Use mostly one main idea)存在、境界維持文の
  位置(構造保持行の直後)。
- `er003_v1_n3_01_advanced_adaptation_generate_test_01.py`:
  `test_standard_a2_module_self_consistent_sha256`で、Standardモジュール
  自身のsha256 assertが引き続きPASSすること(Advanced側の変更が
  Standardへ意図せず波及していないことの生存確認)を更新済みコメント
  付きで維持。
- 呼び出し元regression: `er012_e_family_entertainment_two_level_runner_
  test_01.py`(9件)全PASS(mock、`generate_standard_a2`呼び出しの
  Prompt生成部分をそのまま経由)。
- 全体regression: 1314件中errors=1
  (`er015_standard_a2_6000_generation_first_trial_01_test_01`の
  ImportError、Trial側の意図通りのfail-closed発火。詳細は
  `NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01_REPORT.md`
  §2参照、本タスクの所有ファイルではないため修正しない)。他1313件PASS。

## §3 Runtime evidence(全文・表・cost)

正式runner: `er019_family_x_entertainment_production_runner_01.py`。

### 3.1 Meta Standard 6k(正式path)

`run_01`で入力=`b1b/article.md`(ユーザー確認済みAdvanced、無変更)を
用い`--stage standard`(既存b1b/a2ともreuse判定が働くため実質
`--regenerate-stage standard`相当)を実行。旧Standardは
`a2/article_superseded_pre_6k.md`として保存済み。

- cost: ¥0.8243(1回で`STRUCTURE_PASS`、retry不要)
- deviation: `LEDGER_COMPLIANT`(must-fix不要)
- 語数: 旧399語→新386語(-3.3%、±10%以内)
- `checks_failed`: `[]`(numbers_missing/added、proper_nouns欠落なし)
- wordfreq残存語(top20000、閾値6,000、
  `er015_vocab_abcd_strict_exception_trial_01.build_candidates`を
  read-only分析専用に流用): 旧新とも同一4語
  (`concierge`[rank None、"human concierge"機能名としてFact扱い]、
  `reservations`[rank 7733]、`Meta`[rank 10578、固有名詞]、
  `Muse`[rank 13199、固有名詞])。Meta記事はもともと語彙的に平易な内容
  だったため、6k化による大きな差は観測されなかった(Advanced側の語彙
  ルールv2が既に平易化していたため、Standard側の変化余地が小さかった
  ことが一因と考えられる)。
- Advanced v2ブロック維持確認: `ADVANCED_VOCAB_RULE_V2_SHA256`は
  Meta run全体を通じて変更前と同値のまま(§1参照、Advanced自体は
  この正式pathで再生成していない=入力として無変更のまま使用)。

### 3.2 Hormuz(難ケース、正式path)

`hormuz/run_02`で`--stage all`(writer段はreuse、advanced/standardを
新規生成)。

- Advanced: `STRUCTURE_PASS`(retry不要)、deviation
  `LEDGER_COMPLIANT`(must-fix不要)、語数338語(280-420契約内)。
  English deviation checkのmust-fix retry/issue persistence/origin判定
  は**発火なし**。
- Standard: `STRUCTURE_PASS`(retry不要)、deviation`LEDGER_COMPLIANT`
  (must-fix不要)、語数351語(Advanced比+3.8%、±10%以内)、
  `checks_failed`: `[]`。

**wordfreq残存語(閾値6,000)Before/After(Advanced→Standard)**:

| 語 | rank | 固有名詞候補 | Advanced残存 | Standard残存 |
|---|---|---|---|---|
| flashy | None | No | ○ | ○ |
| withdrawal | 6645 | No | ○ | ○ |
| crude | 7115 | No | ○ | ○ |
| disliked | 8412 | No | ○ | ○ |
| Reuters | 8719 | No | ○ | ○ |
| curtain | 8776 | No | ○ | ○ |
| shipments | 10277 | No | ○ | ○ |
| blockade | 13469 | No | ○ | ○ |
| tanker | 16365 | No | ○ | ○ |
| Strait | 13066 | Yes | ○ | ○ |
| Hormuz | None | Yes | ○ | ○ |
| Brent | 11348 | Yes | ○ | ○ |

**観察知見(STOP事由ではないが報告)**: 12語のうち3語(Strait/Hormuz/
Brent)は固有名詞で除外条件(1)に正しく該当する。残り9語
(flashy/withdrawal/crude/disliked/Reuters/curtain/shipments/blockade/
tanker)は3除外条件のいずれにも明示的には該当しない一般語彙だが、
Advanced→Standardで**1語も置換されず同数のまま残存**した。deviation
Check・構造Gate・語数契約はいずれも満たしており、Fact/Story/自然さは
壊れていない。ただしこれは、新語彙段落が「Judge this naturally as you
write」という自然判断へ委ねる設計(Trial Bの結論=モデルの語感に依存、
候補語リスト方式は不採用)であることの直接的な帰結であり、「firm」な
6,000語Bandを機械的な閾値としては実現していないことを示す実測データで
ある。ユーザーの確定方針(「意味精度上必要な語は必要に応じ保持する」)と
矛盾はしないが、Bandの実効性の強さについては、この1記事のみでは
一般化できない(Meta記事では大きな差が出なかった§3.1、Hormuz記事では
残存語が変化しなかった、というサンプル2件の観察に留まる)。

### 3.3 6k受入(delegation §5基準)照合

- Fact/因果/主体・対象/数量/時間: Meta/Hormuzとも`checks_failed=[]`+
  deviation`LEDGER_COMPLIANT`で差分なしを確認。
- Storytelling維持: Meta/Hormuzとも比喩("curtain rose"/"center stage"等)
  ・段落構成を目視確認、要約化なし。
- 語数±10%以内: Meta -3.3%、Hormuz +3.8%。いずれも範囲内。
- 主題核語の過剰置換なし: Reuters/Brent/Strait/Hormuz/Meta/Muse等の
  固有名詞・主題核語はいずれも保持を確認。

### 3.4 STOP該当有無

Meta/Hormuzのいずれの正式pathでもSTOP(deviation再生成後もMAJOR/
JA_RECHECK_REQUIRED)は発生していない。Meta run_01で発生した1件の
JARecheckRequiredError(§3.5詳細は
`NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01_REPORT.md`
参照)は、誤って`--stage all`を指定しAdvanced段を意図せず再実行対象に
含めてしまったことによるものであり、既存(本タスク無関係)のJA由来
Ledger逸脱に対する安全装置が正しく発火した結果である。Standard 6k自体の
問題ではない。

## §4 Gate 3 checklist

| # | 項目 | 証跡 | Sonnet観察 |
|---|---|---|---|
| 1 | 語彙段落置換 | `STANDARD_A2_NEW_VOCAB_BLOCK`(named定数) | firm wording+3条件のみ、個別語例なし |
| 2 | sha256更新 | `STANDARD_A2_PROMPT_SHA256`(新値、import時fail-closed) | PASS |
| 3 | Advanced無変更確認 | `ADVANCED_VOCAB_RULE_V2_SHA256`不変 | PASS |
| 4 | Meta正式path | `run_01/a2/article.md`(6k)+`article_superseded_pre_6k.md`(旧保存) | 構造/deviation/語数/checks全PASS |
| 5 | Hormuz正式path | `hormuz/run_02/b1b,a2/article.md` | 構造/deviation/語数全PASS、STOP非該当 |
| 6 | wordfreq分析 | Meta/Hormuz Before/After残存語表(§3.1/§3.2) | Meta差分小、Hormuz差分なし(観察知見) |
| 7 | tests | Standard27件+Advanced28件+呼び出し元regression、全PASS | §2参照 |
| 8 | 全体regression | 1314件中errors=1(Trial fail-closed、意図通り) | §2参照 |
| 9 | cost | 小計¥4.65(Meta官式standard再生成分。small_bag/Meta evidence/Hormuz advanced+standardはSection側REPORTと合算計上、二重計上ではなく作業実体を共有) | Guardrail¥60内 |
| 10 | Git commit・push | 本Report作成後に実施 | — |
| 11 | ユーザー承認仕様との一致 | 3除外条件・個別語例なし・10k/14k/ABCD不使用を確認(§1/§2) | Sonnet仮判定 |

**Status(Sonnet仮)**: 1〜9充足。10は本Report後に実施。§3.2の観察知見
(9/12残存語がBefore/After不変)はSTOP事由ではないが、「firm」なBandの
実効性についてFable/ユーザーへの追加判断材料として明記する。
**PRODUCTION_WIREDの正式判定はFable/ユーザーが行う**。

## §5 SSOT記載案(Fableレビュー用、Sonnetは編集していない)

- `CURRENT_SPEC.md`: Standard A2 v5語彙段落の記述(L829付近)を、
  「6,000語Band(firm、3除外条件: 固有名詞/推測容易な派生・複合語/
  日本語定着語)、生成一体型(事後の一語置換ではない)」へ更新。
  `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01`の正式採用経緯
  (VALIDATED仮判定→ユーザーAPPROVED_FOR_PRODUCTION)をDECISION_LOGへ
  合わせて記録。
- `DECISION_LOG.md`: 新規エントリ`NEWS-VOCAB-LEVEL-PRODUCTION-
  WIRING-01`(Stage 2、2026-09-27、sha256、runtime evidence要約、§3.2の
  観察知見を含む)。
- `OPEN_ITEMS.md`: 「firm」な6,000語Bandの実効性(§3.2、Hormuzで9/12語
  不変)について、追加記事でのサンプル拡大や、必要であれば軽量な
  monitoring(機械的な強制ではなく観察のみ)の要否をFable/ユーザー判断
  待ちのOPEN ITEMとして新規登録することを提案する(実装は行っていない、
  提案のみ)。

## §6 Sonnet仮判定

Fact/Story/構造/語数の受入条件は**充足**。「firm」な6,000語Bandの実効性
については、サンプル数2記事(Meta/Hormuz)の観察に基づく限定的な証跡
であり、Hormuzで9/12の非固有名詞残存語が置換されなかった点は
Fable/ユーザーへ判断材料として提示する(STOP事由とはしていない、
delegation記載の受入条件[Fact/Storytelling/語数/主題核語]はいずれも
満たしている)。**正式`PRODUCTION_WIRED`判定はFable/ユーザーが行う**。

## §7 参照

- `docs/pm/recon_vocab_level_production_wiring_01.md`(Phase 0事前調査)
- `er015_standard_a2_6000_generation_first_trial_01.py`
  (`_NEW_VOCAB_BLOCK_GEN_FIRST`、VALIDATED)
- `STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01_REPORT.md`
- `NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01_REPORT.md`
- `er003_v1_n3_01_standard_a2_generate.py`
  (`STANDARD_A2_NEW_VOCAB_BLOCK`, `STANDARD_A2_PROMPT_V5`)
- `er019_output/family_x_b3_production_wiring_01/run_01/a2/`
  (`article.md`, `article_superseded_pre_6k.md`)
- `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/`
- `docs/pm/RESULT_PACKET_S2.md`
