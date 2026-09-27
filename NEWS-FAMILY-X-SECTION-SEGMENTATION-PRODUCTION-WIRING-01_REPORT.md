# NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01_REPORT.md

管理ID: `NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`
実行者: Sonnet(サンドイッチ委任、初回)
日付: 2026-09-27
性質: ユーザー正式採用済み仕様(一般仕様→Writerへ適用→small_bag再Trial→
回帰なしならProduction実装、進行許可済み)のProduction配線+runtime evidence。

## §0 要約

`docs/pm/design_family_x_section_segmentation_spec_01.md` §3.1/§3.2の
Contract文を、Advanced(独立ブロック)・Standard(既存構造保持行の直後に
1文追加)へ逐語で追加した。small_bag再Trial(既知NG、Vogue先取り)は
run_02で解消(先取り→Bridge/予告)。Meta正常ケース回帰・Hormuz難ケースとも
先取りの新規発生なし、over-correctionの兆候なし、構造Gate/deviation Check
とも全てPASS/COMPLIANT。設計doc §5の不安定判定条件A〜Dはいずれも
非該当(§5参照)。総cost 約¥12.0(2管理ID合算、詳細は
`docs/pm/RESULT_PACKET_S2.md`)。**PRODUCTION_WIRED判定はFable/ユーザー**。

## §1 差分(Prompt diff全文)

### 1.1 Advanced(`er003_v1_n3_01_advanced_adaptation_generate.py`)

既存`ADVANCED_CONTRACT_SUFFIX_LINES`/`ADVANCED_COMMON_BLOCK_*`/
`ADVANCED_ARM3_BLOCK`/`ADVANCED_VOCAB_RULE_V2_BLOCK`は**無変更**
(`ADVANCED_UNCHANGED_PORTION_SHA256`=`05ce1a296b7239fcbd141e5bc9909aa1
1e8136c1e845e39d149f0c75e5203e00`、`ADVANCED_VOCAB_RULE_V2_SHA256`=
`d536f4b8a7780771232a95d35611606262d8041371ad8d0a1a4563b7948fb581`とも
importテストで再確認済み、いずれも変更前と同値)。

新規追加: `ADVANCED_SECTION_BOUNDARY_CONTRACT`(design doc §3.1と一字一句
同一)を独立ブロックとして`build_prompt()`内、`ADVANCED_CONTRACT_SUFFIX`
の直後・`[Japanese article]`の直前へ挿入。

```text
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

sha256: `bba08c021ae41ebd748313f329b2a7eba78b1a59d7f85042ec649a7d591b8421`
(import時fail-closed assert `_assert_section_boundary_contract_sha256()`、
design docに書き起こしたテキストと逐語照合済み)。

diff全文(`git diff`): 追加80行のみ、既存行の削除・書き換えは0行
(`build_prompt()`の連結式へ1ブロック挿入する2行の変更のみ)。

### 1.2 Standard(`er003_v1_n3_01_standard_a2_generate.py`)

既存の構造保持行(`Keep the same Markdown structure (...); do not add or
remove sections.`、NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01由来)は
**無変更のまま維持**し、その直後に新規1文を追加した(design doc §3.2と
一字一句同一)。

```text
Keep every fact, example, figure, quotation, and named source in the
same section as in the original article: before or after the same
"### " heading as before. Do not move a sentence across a "### "
heading boundary in either direction, and do not move a section's
first concrete point to before its own heading.
```

named定数`STANDARD_A2_SECTION_PRESERVE_SENTENCE`として単独定義し、
`STANDARD_A2_PROMPT_V5`組み立て時に構造保持行の直後へ連結。

**この変更は`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01`(Stage 2、同一
セッション内で並行実装)による語彙段落置換と同じPromptファイル内で行った
ため、`STANDARD_A2_PROMPT_SHA256`は両変更を合算した1つの新値
(`cbe73fc46f2c3c57c087c521df132ed734b8967a6ef09338c187349d35fecc33`、
旧値`ff860ab60a0d1d4ffa4e93a30e53af37fe87afa8c4e01a99bf54e06897a42353`)
になっている。語彙段落自体の差分詳細は`NEWS-VOCAB-LEVEL-PRODUCTION-
WIRING-01_REPORT.md`§1を参照。本Report(Section側)の対象差分は上記
1文の追加のみ。**

## §2 Tests

- `er003_v1_n3_01_advanced_adaptation_generate_test_01.py`: 28件PASS。
  新規`SectionBoundaryContractTests`(6件): Prompt内存在確認・核心規則の
  文言存在・記事固有語(Vogue/ELLE/mini bag/large bag/Hormuz/Meta/Muse/
  small_bag)不在確認・既存`ADVANCED_CONTRACT_SUFFIX_LINES`不変確認・
  sha256 assert正常系/異常系。既存`test_build_prompt_contains_all_blocks_
  in_order`を新ブロック込みの順序検証へ更新。
- `er003_v1_n3_01_standard_a2_generate_test_01.py`: 27件PASS(Vocab側と
  合算、Section固有分は`test_section_preserve_sentence_present_and_
  follows_structure_line`)。`test_prompt_equals_trial_file_plus_
  structure_line_plus_vocab_and_boundary_update`でTrial file+3変更
  (構造保持行挿入/語彙段落置換/Section境界文追加)の再構成一致をsha256込みで
  検証。
- 呼び出し元regression: `er012_e_family_entertainment_two_level_runner_
  test_01.py`(9件)・`er019_family_x_b3_production_wiring_01_test_01.py`
  (24件)・`er019_family_x_entertainment_production_runner_01_test_01.py`
  (2件) 全PASS(mock、実API呼び出しなし)。
- 全体regression: `python -m unittest discover -s . -p "*_test_01.py"`
  Ran 1314 tests、**errors=1**。唯一の1件は
  `er015_standard_a2_6000_generation_first_trial_01_test_01`の
  ImportError(`er015_standard_a2_6000_generation_first_trial_01.py`が
  import時に「Production `STANDARD_A2_PROMPT_V5`の旧語彙段落テキストが
  想定と異なる」とfail-closedでRuntimeErrorを送出)。**これは意図通りの
  安全装置の発火**(このTrialは旧v5の語彙段落に対する`str.replace()`
  前提で構築されており、今回のVocab Stage 2置換によりTrialの前提テキストが
  Productionから消えたため、サイレントに誤ったPromptを使わないよう
  正しくSTOPしている)。Trialファイル自体は本タスクの所有ファイルではなく、
  既にVALIDATED判定が確定・Production側へ組み込み済みのため、このTrialを
  今後再実行する予定はない(修正不要、既存動作)。他の1313件は全PASS。

## §3 Runtime evidence(全文・表・cost)

正式runner: `er019_family_x_entertainment_production_runner_01.py`
(cost logger稼働、`model_id_actual`記録)。

### 3.1 small_bag再Trial(既知NG→解消)

`er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/`を新規
作成。`research_ledger/verified_fact_ledger.txt`・
`storyline_b3/selected_brief.md`・`ja_writer/revision2.md`はrun_01と
sha256完全一致のコピー(再生成なし)。`--stage all`で advanced→standard
を新Contract付きで生成(¥2.90、advanced/standardとも1回で
`STRUCTURE_PASS`、deviation`LEDGER_COMPLIANT`、`checks_failed=[]`)。

**境界判定表(Advanced、design doc §2形式)**

| # | Run | 見出し | 直前文(抜粋) | 判定 |
|---|-----|--------|--------------|------|
| 1 | Before(run_01) | 見出し1 | 「In terms of carrying space, they are not trying to compete with large-capacity bags.」 | 該当なし |
| 2 | Before(run_01) | 見出し2 | 「Yet this does not mean large bags have vanished. **Vogue** also covered a wide range of bags in the same 2026 season.」 | **先取り(NG)** — Vogueが見出し2の直前で初出、見出し後はVogue記事の具体的展開 |
| 3 | After(run_02) | 見出し1「ELLE's small-bag examples」 | 「...In 2026, the two sizes seem to have different jobs. One carries what we need. The other helps create the look.」 | 該当なし(ELLEの初出は見出し後) |
| 4 | After(run_02) | 見出し2「Vogue's wider list of bags」 | 「The season's picture becomes clearer when we look at what appeared beside them.」 | Bridge/予告(Vogue名・具体内容とも見出し後まで出さない) |

Standard(a2)側も同型のBefore(先取りNG、Vogue)→After(Bridge/予告)を確認
(`a2/article.md`、行17/行11参照)。語数: Advanced 362→311語(280–420契約内)、
Standard 339→302語。

### 3.2 正常ケース回帰(Meta、Family X限定)

`run_01/b1b/article.md`(ユーザー確認済み本文)は**上書きせず**、
`run_01/audit/section_contract_regression/article.md`へ新Contract付き
Advancedを再生成(evidence専用、¥1.72=generate¥0.64+deviation check
¥1.08)。`git status`で`run_01/b1b/article.md`が無変更であることを確認済み。

| # | 対象 | 見出し | 直前文(抜粋、Before→After) | 判定 |
|---|------|--------|------------------------------|------|
| 1 | Before | 見出し1 | 「...knowing who is on the other end matters.」 | 該当なし |
| 2 | Before | 見出し2 | 「...whether the other side is AI or human.」 | Bridge/予告 |
| 3 | After | 見出し1「The hidden people behind some calls」 | 「But then a problem appeared.」 | Bridge/予告 |
| 4 | After | 見出し2「What Meta admitted afterward」 | 「...had users been clearly told who was making the call?」 | Bridge/予告 |

新規の先取り(NG)発生なし、既存出典名(Meta/Muse)の見出し前漏れなし。
structure_status=`STRUCTURE_PASS`(retry不要)、deviation=
`LEDGER_COMPLIANT`。over-correctionの兆候(不要な境界移動・Fact増減)なし。

### 3.3 Hormuz(難ケース、正式path)

`hormuz/run_02/`(JA R2 COMPLIANT既存)で`--stage all`実行(writer段は
既存revision2.mdを再利用、advanced/standardのみ新規生成、¥2.74)。
must-fix retry・JA_RECHECK_REQUIREDとも**発火なし**(STOP条件非該当)。

| 見出し | 直前文(抜粋) | 判定 |
|--------|--------------|------|
| 見出し1「The 20% plan changes overnight」 | 「The number stayed at center stage for about a day. Then the story took a sharp turn.」 | Bridge/予告 |
| 見出し2「The chart refuses to stay down」 | 「...Reuters linked that rise to concern about a US sea blockade of Iran...」(Section 1の7/13時点数値の続き、Section 2固有の7/14数値ではない) | 該当なし |

advanced/standardとも`STRUCTURE_PASS`(retry不要)、deviation両段とも
`LEDGER_COMPLIANT`(1回で通過、must-fix未使用)。語数: Advanced 338語
(280–420契約内)、Standard 351語(+3.8%)。

### 3.4 語数逸脱(節ごと、既存Gate対象外の観察)

各`### `節の語数(正規表現ベース概算、記号除く)は、small_bag run_02
(79/130語)・Meta evidence regen(123/114語)・Hormuz run_02(102/51語)の
いずれも既存contract「各30–60語」を上回った。ただし**この傾向はContract
追加前から存在する既存の特性**であることを確認した(small_bag run_01
[Before]: 77/127語、Meta run_01[既存Production記事]: 112/57語)。
`validate_point_structure()`は見出し数・非空のみを検証し語数は検証対象
外(design doc §1.3)であるため、既存の構造Gateはこの逸脱を検知しない。
設計doc §5条件Cの判定基準(「Contract追加前後で語数逸脱率が悪化したこと」)
に照らすと、**悪化は観測されなかった**(条件C非該当、§5参照)。

### 3.5 STOP該当有無

いずれの正式runでもSTOP(JA_RECHECK_REQUIRED/deviation再生成後も
MAJOR)は発生していない。ただし本タスク中、Meta run_01に対し誤って
`--regenerate-stage standard`を`--stage all`と組み合わせて実行した結果、
既存(本タスク無関係)のJA由来Ledger逸脱(`MUSE-HC-*`関連、Meta従業員の
scope記述)により`JARecheckRequiredError`が発火し処理が中断した
(`run_01/b1b/audit/deviation_checks/advanced_attempt1.json`として証跡が
残存)。**この例外発火はコマンド指定の誤り(`--stage standard`のみを
指定すべきところ`--stage all`を指定したため、意図せずAdvanced段も
再実行対象になった)によるものであり、既存のJA_RECHECK_REQUIRED安全装置
自体が正しく機能したことの確認にしかならない**。`run_01/b1b/article.md`
は保存処理前に例外送出されたため無変更のまま(`git status`で確認済み)。
以降は`--stage standard`のみを指定して正しくStandard 6k再生成を実施した
(§3は`NEWS-VOCAB-LEVEL-PRODUCTION-WIRING-01_REPORT.md`側で詳述)。

## §4 Gate 3 checklist

| # | 項目 | 証跡 | Sonnet観察 |
|---|---|---|---|
| 1 | Advanced独立ブロック追加 | `er003_v1_n3_01_advanced_adaptation_generate.py`(`ADVANCED_SECTION_BOUNDARY_CONTRACT`、既存ブロック無変更) | sha256 fail-closed assert実装・PASS |
| 2 | Standard追加1文 | `er003_v1_n3_01_standard_a2_generate.py`(`STANDARD_A2_SECTION_PRESERVE_SENTENCE`) | 既存構造保持行の直後に追加、既存行は無変更 |
| 3 | small_bag再Trial(既知NG) | `small_bag/run_02/`(b1b/a2) | 先取り(NG)→Bridge/予告で解消(§3.1) |
| 4 | 正常ケース回帰(Meta) | `run_01/audit/section_contract_regression/` | over-correctionなし、b1b/article.md無変更 |
| 5 | 難ケース(Hormuz) | `hormuz/run_02/`(b1b/a2) | STOP非該当、先取りなし |
| 6 | 構造Gate | 3件ともSTRUCTURE_PASS(retry不要) | 悪化なし |
| 7 | deviation Check | 3件ともLEDGER_COMPLIANT(1回で通過) | 悪化なし |
| 8 | tests | 55件(Advanced28+Standard27)+呼び出し元regression35件、全PASS | §2参照 |
| 9 | 全体regression | 1314件中errors=1(Trial fail-closed、意図通り) | §2参照 |
| 10 | cost | 小計¥7.36(small_bag2.90+Meta evidence1.72+Hormuz2.74、Meta Standard再生成分はVocab側計上) | Guardrail¥60内 |
| 11 | Git commit・push | 本Report作成後に実施 | — |
| 12 | ユーザー承認仕様との一致 | design doc §3.1/§3.2と逐語一致(sha256照合) | Sonnet仮判定 |

**Status(Sonnet仮)**: 1〜10充足。11は本Report後に実施。**PRODUCTION_WIRED
の正式判定はFable/ユーザーが行う**(Sonnetは自称しない)。

## §5 設計doc §5 不安定判定条件A〜Dの照合結果

- **条件A(残存、先取りが1件でも残る場合)**: **非該当**。small_bag
  (Advanced+Standard)・Meta(Advanced、evidence dir)・Hormuz
  (Advanced+Standard)の計5生成すべてで先取り(NG)は0件。
- **条件B(over-correction、正常ケース8件中1件でも見出し位置移動・Fact
  増減・新規先取りが観測された場合)**: **非該当**。Meta(Family X限定、
  Fable承認済み補正(ii))の2見出しで、見出し位置・Fact tokens・deviation
  status(LEDGER_COMPLIANT)とも回帰前後で変化なし、新規先取りも0件。
  (Family A discovery/news/trend/ai_controlはFable承認済み補正(ii)により
  対象外、Meta以外の再生成は行っていない。)
- **条件C(語数逸脱、Contract追加前後で悪化した場合)**: **非該当**。§3.4の
  通り、節ごとの語数超過は既存(Contract追加前)から存在する特性であり、
  悪化は観測されなかった。
- **条件D(構造Gate逸脱、STRUCTURE_PASS率がContract追加前より悪化する
  場合)**: **非該当**。5生成すべてでSTRUCTURE_PASS(retry不要、1回で通過)。

**結論: 条件A〜Dいずれも非該当。Prompt文言追加のみで安定していることを
確認した(追加mechanismの必要性は現時点で観測されていない)。**

## §6 SSOT記載案(Fableレビュー用、Sonnetは編集していない)

- `CURRENT_SPEC.md`: Family X Advanced/Standard Prompt仕様の項へ、
  「見出し境界Contract(Section boundary rule)」追加をStatus
  `APPROVED_FOR_PRODUCTION`(ユーザー進行許可済み)+`PRODUCTION_WIRED`
  (Fable Gate 3判定待ち)として追記。
- `DECISION_LOG.md`: 新規エントリ
  `NEWS-FAMILY-X-SECTION-SEGMENTATION-PRODUCTION-WIRING-01`
  (2026-09-27、design doc §3.1/§3.2の採用、sha256、runtime evidence要約)。
- `OPEN_ITEMS.md`: 既存の見出し先取り関連の未決事項があれば解消として
  クローズ(該当項目がなければ新規登録不要)。§3.4の語数逸脱(既存
  contract「30-60語」が実際には遵守されていない)は、本タスク由来の新規
  問題ではないため、別途OPEN_ITEMS化の要否をFable判断とする(本タスクの
  受入条件には含まれない)。

## §7 Sonnet仮判定

受入条件(design doc §4回帰計画、delegation文の受入基準)は**充足**と
見受けられる: 先取り0件・Bridge/流れ維持・見出し数2・構造Gate PASS・
Fact tokens一致・deviation COMPLIANT・語数契約内・over-correctionなし・
STOP非該当。**正式`PRODUCTION_WIRED`判定はFable/ユーザーが行う**。

## §8 参照

- `docs/pm/design_family_x_section_segmentation_spec_01.md`(§3.1/§3.2/§5)
- `er003_v1_n3_01_advanced_adaptation_generate.py`
  (`ADVANCED_SECTION_BOUNDARY_CONTRACT`, `build_prompt()`)
- `er003_v1_n3_01_standard_a2_generate.py`
  (`STANDARD_A2_SECTION_PRESERVE_SENTENCE`)
- `er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/`
- `er019_output/family_x_b3_production_wiring_01/run_01/audit/section_contract_regression/`
- `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/`
- `docs/pm/RESULT_PACKET_S2.md`
