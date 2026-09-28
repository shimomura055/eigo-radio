# design_family_x_no_heading_segmentation_trial_01.md

管理ID: FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01
作成: Sonnet(text-onlyTrial)。Production code・正式Prompt・CURRENT_SPEC・
routing・Comment仕様は一切変更しない(読み取りのみ)。

## 0. ユーザー指示(原文要旨、委任文より逐語転記)

「Trial仕様: 本文途中の見出しを廃止/日本語完成記事を基本そのまま英訳/
英訳時に過度な再構成・再編集をしない/本文を自然な段落境界でPart1/Part2/
Part3に分割/なるべく均等に分けるが、分割のために本文を書き換えない/
構成: Comment1・body1・Comment2・body2・Comment3・body3・Comment4・In One
Line/In One Lineは短い自然な一文/Commentで変化をつけるため、本文見出しは
不要。重要: このTrialはOPEN-228の古い『最初の###見出し前に導入部2段落
以上』前提を将来的に不要化できるかを見る意味もある。したがってOPEN-228を
先に単独修正しない。対象: 既存Family X記事(Hormuz/Meta)で最小構成。
入力: AN3-T0で生成された日本語完成記事。新しい記事生成・Source取得は
不要。ユーザー仮説(見出し作成→本文編集→構造複雑化→In One Lineの過剰
圧縮)は仮説であり『見出しが原因』と決めつけて実装しない。評価項目:
日本語原文への忠実性/Fact保持/因果保持/新規Fact 0/順序保持/意味の追加・
削除/読みやすさ/聞きやすさ/Entertainment性/3分割の自然さ/長さバランス/
Commentとの接続自然さ/In One Lineの簡潔さ・要旨正確性/見出しをなくした
結果、内容が単調になりすぎないか。STOP条件: 忠実英訳だけでは英語として
不自然/3分割で意味が壊れる/Comment位置が不自然/見出し廃止で著しく聞き
にくい/In One Line簡潔化で重要Factが落ちる/既存正式仕様と大きく衝突/
Family共有Prompt変更が必要/新しいProduct判断が必要。」

## 1. Existing Spec Check(Grep先を明記)

### 1-1. CURRENT_SPEC.md「Family X(Entertainment News)音声構造」節(L1143-1236)

- Status: 2026-09-26ユーザー確定、`APPROVED_FOR_PRODUCTION`。3分割・
  Comment配置・音声Assembly仕様(2026-09-27 Stage 1〜3dで`PRODUCTION_WIRED`)。
- 音声構造(SE-1 CLOSED、L1190-1198): `Comment1 → 本文1 → Comment2 →
  本文2 → Comment3 → 本文3 → Comment4 → In One Line`。**本Trialの構成と
  完全一致**(Comment1・body1・Comment2・body2・Comment3・body3・Comment4・
  In One Line)。
- 本文1/2/3の区切り定義(L1199-1205、`DECIDED`): 本文1=Title+1つ目の
  見出し直前まで/本文2=1つ目の見出し+2つ目の見出し直前まで/本文3=2つ目の
  見出し+In One Line直前まで。50%/25%/25%は理想目安でVaildator/Gate化
  しない。**本Trialはこの「見出しに基づく区切り」を「段落境界に基づく
  決定論的均等分割」へ置き換えるため、この既存定義とは異なる新規方式**
  (下記§10で「復旧か新規か」を判定)。
- Section Segmentation(見出し境界)Contract(L1206-1218、`PRODUCTION_WIRED`、
  commit`9cec45f1`/`e7311d37`): 見出しが新しい論点を先取りしないための
  Contract。本Trialは見出し自体を廃止するため、このContractは適用対象外
  になる(Contract自体を変更・否定するものではない。見出しがある既存
  Productionには引き続き適用される)。
- 見出し独立sub-segment化(L1160-1173、Stage 3c、`PRODUCTION_WIRED`):
  本文2/3の見出しをHEADING_READOUT sub-segmentとして分離した設計変更
  (repetition QA/ASR誤検知対策)。本Trialが「見出し廃止」を検証する
  ことは、この既存音声機構(見出しsub-segment)が将来的に不要になり
  得るかを問う意味を持つ(ユーザー指示に明記の通り)。**本Trialは
  text-onlyであり、この音声機構自体には一切触れない**。

### 1-2. `er003_v1_n3_01_advanced_adaptation_generate.py`のPrompt定数(Grep結果、L74-357)

翻訳以外に要求している編集要素を逐語で列挙:
- `ADVANCED_ARM3_BLOCK`(L110-117、NATURAL ENGLISH水準): "You may reorder,
  merge, or reshape paragraphs, and adjust the wording of metaphors where
  English needs it." → **段落の再配置・統合・再構成を明示的に許可**
  (本Trialが除外する編集要素)。
- `ADVANCED_CONTRACT_SUFFIX_LINES`(L210-218): "then exactly two \"### \"
  subsections, each 30–60 words, with headings that describe their
  content in your own words... then a final section headed exactly
  \"## In one line\" containing one sentence." → **見出し2つの新規生成・
  In One Line生成を指示**(本Trialが除外する編集要素)。
- `ADVANCED_SECTION_BOUNDARY_CONTRACT`(L271-294): 見出し境界の内容配置
  ルール(見出し廃止Trialでは適用外)。
- `ADVANCED_VOCAB_RULE_V2_BLOCK`(L144-187、`APPROVED_FOR_PRODUCTION`、
  sha256固定): 語彙難易度ルール(12,000語順位を目安とした簡略化判断)。
  翻訳の「訳語選択」ルールであり構成編集ではないため、**本Trialでは
  そのまま逐語流用**(importのみ、コピペしない。sha256一致は
  `_assert_vocab_rule_v2_sha256()`のimport時fail-closed検証で既に
  保証されている)。
- `ADVANCED_COMMON_BLOCK_PREFIX`/`ADVANCED_GENERAL_PRESERVE_BULLETS`/
  `ADVANCED_COMMON_BLOCK_SUFFIX`(L80-107): 「Do not rewrite the article
  from scratch. Preserve angle/structure/order/ending. Keep every fact.」
  という一般原則自体は本Trialの意図と整合するが、ARM3_BLOCKと不可分に
  設計されたセットであり、かつ「reorder」を明示禁止していないため、
  本Trialでは流用せず、**Trial限定の新規最小Prompt**(§3)を別途作成する
  (VOCAB_RULE_V2_BLOCKのみ既存ブロックを流用)。

### 1-3. `er003_v1_n3_01_scaffold_generate.py::split_article_text()`(Grep結果、L107-162)

Family A(既存)の分割関数。###見出しちょうど2つ+『## In one line』の
構造契約必須(満たさなければRuntimeError)。Main Story(導入部)の段落を
語数バランス最良の境界1点で前半/後半に機械分割するロジック(L138-155、
`running`変数で累積語数diffを最小化する境界を探索)が存在する。**この
「累積語数diff最小化で境界を選ぶ」アルゴリズムを、本Trialの3分割
(境界2点探索)へ一般化して流用する**(関数自体はimportしない、
考え方のみ参考にTrial script内に新規実装、Production関数は無編集)。
このチェックの「Main Story段落数2以上必須」がOPEN-228のクラッシュ原因
(`er019_family_x_audio_plan_01.split_family_x_article_text()`でも同型の
2見出しちょうど2つ必須チェックが存在、見出しがあることが前提)。本Trial
は見出し自体を廃止するため、この2関数(scaffold_generate/audio_plan)の
`split_*`はいずれも呼び出さない(本Trial専用の新規分割関数を使う)。

### 1-4. Family A/Y等との共有Prompt有無

Grep `import .*advanced_adaptation|from er003_v1_n3_01_advanced` →
`er012_e_family_entertainment_two_level_runner_01.py`のみがimport
(Family X専用の生成関数)。Family A/Y/Z等からのimportなし。
`ADVANCED_VOCAB_RULE_V2_BLOCK`はFamily X Advanced固有(Family Aは別の
`er003_v1_n3_01_standard_a2_generate.py`系のvocab v5を使用、別モジュール)。
本Trialは`er003_v1_n3_01_advanced_adaptation_generate.py`をimportのみ
行い(sha256定数・VOCAB_RULE_V2_BLOCKの参照)、一切編集しない。

### 1-5. 過去の「見出し廃止」「翻訳のみ」Trialの有無

Grep `DECISION_LOG.md`/`OPEN_ITEMS.md` `見出し|heading|翻訳のみ|faithful`
→ 見出し関連はSection Segmentation Contract(既存PRODUCTION_WIRED仕様、
見出しを前提とした内容配置ルール)のみがヒット、「見出し廃止」「翻訳のみ」
Trialへの言及は0件。**本Trialは新規**(既存仕様の復旧ではない)。

### 1-6. 既存Family X音声構造(Comment位置・言語)

`er019_family_x_audio_production_runner_01.py` Grep結果: 音声順序は
topic_intro→preview→Comment1→full_story_part1→Comment2→
[full_story_part2_heading→]full_story_part2→Comment3→
[full_story_part3_heading→]full_story_part3→Comment4→in_one_line→outro
(B1B/A2共通のスロット順序、L1016-1057・L1222-1258)。

`er019_family_x_audio_plan_01.py` Grep結果: Comment1/2/Preview roleは
Family A既存role(`b1s.COMMENT_1_ROLE`等)をそのまま流用、Comment3/4のみ
Family X専用role(`FAMILY_X_B1_COMMENT_3/4_ROLE`、L152-200)。B1B
(Advanced/Charon)は英語、A2(Standard/単一Voice)は日本語(L232-297の
`run_family_x_b1_scaffold`/`run_family_x_a2_scaffold`)。Comment3/4は
`parts['part1']`/`part2']`/`part3']`(見出しベースの現行split結果)を
contextとして生成される。

**本Trialでの扱い**: 新しいComment LLM呼び出しは行わない(委任文の
「既存Comment1〜4は同run または直近Production runのCommentをreuse」に
従う)。B1B(英語Advanced)のComment1〜4を、直近のFamily X B1B scaffold
run(Hormuz: `er019_output/family_x_audio_production_wiring_01/
family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/b1b/
b1_support_texts.json`[2026-09-28 09:04、AN3-T0後の最新]、Meta:
`er019_output/family_x_b3_diversity_trial_01/meta/scaffold_text/b1b/
b1_support_texts.json`[2026-09-26 19:52、Meta b1bで最新])からそのまま
reuseする。**既知の制約**: これらのComment1〜4は、AN3-T0 run自体では
scaffold stageを実行していない(REPORT §10「本タスクでは--stage
standard/allは一度も実行していない」)ため、AN3-T0のJA/Advanced本文とは
別runの本文(同じ記事テーマの別ドラフト)から生成されたComment。内容の
大筋(Hormuz=20%手数料案の顛末とホルムズ海峡情勢/Meta=Museの人間代行
発覚)はAN3-T0と一致するが、字句レベルでは完全一致しない。この制約を
比較ページ・REPORTに明記し、「Comment位置が不自然」というSTOP判定は
文脈のズレではなく構成上の位置・接続自体で判断する。

## 2. 入力・Baseline確定(重要な発見: Hormuz on-disk article.mdは別run)

- JA最終R2: `ja_writer/revision2.md`(Hormuz/Meta とも disk上のテキストが
  `FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01_REPORT.md`の転記と
  バイト一致[diff確認済み]。信頼できるSource of truthとしてdiskから読む)。
- Baseline English(見出しあり、現行Advanced):
  - Meta: `meta/b1b/article.md`(diskの内容がREPORTの`LEDGER_COMPLIANT`
    転記と一致[カーリークォート表記のみ差異、内容同一をdiff確認済み]。
    diskから読む)。
  - **Hormuz: diskの`hormuz/b1b/article.md`は、AN3-T0 REPORT作成後に
    別タスクが再実行した際の生成物であり、REPORT転記文(`LEDGER_COMPLIANT`
    2回目)とは異なるテキスト(diffで非一致を確認、タイトルが"20 Percent"
    vs "20%"等)。本Trialでは委任文の明示指示通り、REPORTの`## 記事本文
    全文`セクション(L196-216)からHormuz Advanced最終テキストを
    プログラム的に抽出して使う(正規表現でコードフェンス内を抽出、
    ハードコード転記による人為的ズレを避ける)。**disk側article.mdは
    本Trialでは一切使用・変更しない**。**この発見(disk article.mdが
    複数run分の生成物で上書きされ続けている)自体は本Trialのscope外の
    観察であり、修正はREPORT側で報告のみに留める**。
- Verified Fact Ledger(Deviation Check用): `{article}/research_ledger/
  verified_fact_ledger.txt`(既存、disk読み取りのみ)。
- Baseline Deviation Check結果(既存artifactをreuse、**追加API呼び出し
  不要**): `meta/b1b/audit/deviation_checks/advanced_attempt1.json`
  (`LEDGER_COMPLIANT`)、`hormuz/b1b/audit/deviation_checks/
  advanced_attempt2.json`(`LEDGER_COMPLIANT`、`all_prior_issues_
  resolved=true`、REPORT転記テキストと同一生成の判定結果)。

## 3. Trial限定Prompt(逐語、新規)

### 3-1. 忠実英訳Prompt(Trial限定、Production Prompt定数は無変更)

developer message:
```
You are a translator who turns a finished Japanese feature article into
natural English for listeners who are learning English. Your task is
translation, not editorial rewriting.
```

user message = 下記`TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION` +
`ADVANCED_VOCAB_RULE_V2_BLOCK`(`er003_v1_n3_01_advanced_adaptation_
generate.ADVANCED_VOCAB_RULE_V2_BLOCK`をimportして逐語使用、sha256は
import時に既存モジュールがfail-closedで検証済み) + `[Japanese
article]\n{ja_article_text}`。

`TRIAL_FAITHFUL_TRANSLATION_INSTRUCTION`(新規、Trial限定):
```
Translate the Japanese article below into English, paragraph by
paragraph, staying as close to the original as natural English allows.

Do not add new ideas, claims, background, general observations,
examples, or facts that are not in the Japanese article. Do not remove
any fact, claim, or causal link that is in the Japanese article. Keep
the same order of information and the same paragraph structure: the
English article must have exactly the same number of paragraphs as the
Japanese article, in the same order, each English paragraph translating
the corresponding Japanese paragraph. Do not merge, split, or reorder
paragraphs.

Do not add section headings, subheadings, or any Markdown heading markup
("#", "##", "###") inside the body. Do not add a concluding one-line
summary; that is handled separately by another step.

Output format: first output a title line starting with "# " followed by
an English title that translates the Japanese title, then a blank line,
then the body paragraphs (one blank line between paragraphs, same count
and order as the Japanese article). Output nothing else (no commentary
about the translation itself).

Use short, simple, natural English that a learner could understand by
listening once.
```

（VOCAB_RULE_V2_BLOCKの逐語本文は`er003_v1_n3_01_advanced_adaptation_
generate.py`L144-187を参照。本設計書では重複転記しない。）

### 3-2. In One Line Prompt(Trial限定、新規)

developer message: 上記と同一。

user message:
```
Below is a finished English news feature article (already translated
from Japanese, no section headings). Write ONE short, natural sentence
that captures the core of the story -- its central point or twist.

Do not add any new fact, conclusion, or lesson that is not already
stated in the article below. Do not summarize with a generic moral
unless the article itself states it. Output only the sentence itself,
nothing else (no quotation marks, no label like "In one line:").

[Article]
{trial_full_body_text}
```

### 3-3. 決定論的3分割アルゴリズム(LLM不使用、Trial script内実装)

1. Trial英訳body(title行を除く)を空行("\n\n")で段落へ分割する
   (`paragraphs = [p for p in body.split("\n\n") if p.strip()]`)。
2. 各段落の英単語数を`re.findall(r"[A-Za-z']+", p)`でカウント。
3. 2つの境界インデックス`(i, j)`(`0 < i < j < len(paragraphs)`、
   `j - i >= 1`)を全探索し、3区間の語数`(c1, c2, c3)`と目標値
   `target = total/3`との二乗誤差`(c1-target)^2+(c2-target)^2+
   (c3-target)^2`が最小になる`(i, j)`を選ぶ(同値の場合は`i`昇順→`j`昇順で
   最小のものを選び、決定論性を保証)。
4. `part1 = "\n\n".join(paragraphs[:i])`、`part2 = "\n\n".join(
   paragraphs[i:j])`、`part3 = "\n\n".join(paragraphs[j:])`。本文の
   書き換えは一切行わない(結合のみ)。
5. 段落数が3未満(3区間を作れない)の場合はSTOP条件「3分割で意味が壊れる」
   に該当するとみなし、Trial側でエラー記録して報告する(強制的な文分割は
   行わない)。

### 3-4. 評価(決定論指標+Deviation Check+Rubric)

- Deviation Check: `er003_v1_en_direct_vfl_01_generate.run_deviation_
  check(client, ledger_text, article_text, hook_aware=False,
  include_related_fact_id=True, source_article_text=ja_text)`
  (Production Advanced Deviation Checkと同一呼び出しパターン、
  `er012_e_family_entertainment_two_level_runner_01.py`L309-310に準拠)。
  Baseline側は既存artifactをreuse(§2)、Trial側のみ新規に1回実行
  (must-fix retryは行わない。MAJORが出た場合はSTOP条件「忠実英訳だけ
  では英語として不自然」寄りの事象として報告し、Trial側で本文を書き換え
  ない)。
- 決定論指標: 段落数(JA/Trial EN一致確認)、3区間の語数・文字数、
  JA→EN段落対応(段落数が一致する場合のみ1:1対応とみなす)、新規固有
  名詞・数字の有無(`er039_family_xy_concreteness_control_trial_02.
  extract_entities_ja_improved`/`extract_entities_en_improved`を
  importして使用、Baseline比較ではなくJA原文とTrial ENの比較で「JAに
  無い固有名詞がTrial ENに新規出現していないか」を確認)、In One Lineの
  語数・文数。
- Rubric(LLM 1 call/記事、Baseline/Trial両方を1回のcallで評価): ユーザー
  評価項目14点(§0)をJSON Schemaで1〜5点+根拠を出力させる。項目14
  (見出し廃止で単調になりすぎないか)はBaselineには見出しがあるため
  適用外(`null`)とし、Trialのみ採点させる。Model: `routing.
  require_model_or_override("B1_WRITER", "gpt-5.6-luna")`(Approved
  Model一致、override不使用)。

## 4. STOP条件の再掲(委任文原文)

忠実英訳だけでは英語として不自然/3分割で意味が壊れる/Comment位置が
不自然/見出し廃止で著しく聞きにくい/In One Line簡潔化で重要Factが
落ちる/既存正式仕様と大きく衝突/Family共有Prompt変更が必要/新しい
Product判断が必要。→ いずれかに該当した場合、追加改善(Prompt再調整・
再生成)は行わずSTOP報告する。

## 5. 出力構成

- `er045_output/family_x_no_heading_segmentation_trial_01/{hormuz,meta}/`:
  `trial_translation.json`(title/body/paragraphs/usage/cost)、
  `trial_split.json`(part1/2/3・語数・境界インデックス)、
  `trial_in_one_line.json`、`deviation_check_trial.json`、
  `deviation_check_baseline_reused.json`(§2の既存artifactをコピー、
  出典パスを記録)、`metrics.json`(決定論指標)、`rubric.json`。
- `user_test/no_heading_trial_01/index.html`: 記事ごとにJA原文/Baseline
  EN(見出しあり)/Trial EN(3分割・Comment挿入位置明示)/In One Line
  Before-After/段落単位diff/指標・rubric表。

## 6. Production無変更の確認方法

`git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v
er045`が空であることをコミット前に確認する(§実行コマンド全文参照)。

## 7. 修正1回目(2026-09-28、委任_02)で追加した3ステージ

初回(§3-4)はTrialのDeviation CheckでMAJORが出てもmust-fix retryを
行わない設計だった。これはBaselineが持つmust-fix retry機構
(`er012_e_family_entertainment_two_level_runner_01.py`)と比較条件が
異なっていたため、修正1回目で以下の3ステージを`--stage`引数として追加
した(v1の`run_trial()`本体は無変更、v1成果物`trial_translation.json`
等も一切上書きしない。新規artifactは`{out_dir}/v2/`配下へ追加保存)。

### 7-1. `--stage must-fix-retry`(Metaのみ)

- 入力: v1の`trial_result.json`内`trial_deviation.parsed.deviations`
  からseverity=="MAJOR"のみ抽出(MINORはmust-fix対象外、Production同様)。
- must-fixブロック生成: `er003_v1_n3_01_advanced_adaptation_generate.
  build_must_fix_block(must_fix)`をそのままimportして呼び出す(Trial側で
  文言を再定義しない)。Trial翻訳Prompt(`TRIAL_FAITHFUL_TRANSLATION_
  INSTRUCTION` + `ADVANCED_VOCAB_RULE_V2_BLOCK` + JA本文)の末尾へ、この
  ブロックをそのまま追加するだけ(見出し生成等の新規指示は追加しない)。
- 1回だけ再生成 → `vfl01.run_deviation_check(..., prior_issues=must_fix)`
  で再検証(Production`er012`と同一呼び出しパターン、`prior_issues`
  経由で`all_prior_issues_resolved`を取得)。`LEDGER_COMPLIANT`に
  ならなくてもそれ以上retryしない(Production同様、1回→STOP)。
- Hormuzは既にCOMPLIANTのため、このステージ自体を呼び出さない
  (MAJORが無い場合はSKIPPED_NO_MAJORを記録して安全側に倒す実装だが、
  実運用ではHormuzに対して本ステージを実行していない)。

### 7-2. `--stage in-one-line-v2`(両記事)

- 新規Prompt`TRIAL_IN_ONE_LINE_V2_INSTRUCTION_TEMPLATE`(Trial限定):
  ユーザー仕様(1文のみ/一回聞いて理解できる/論点を詰め込まない/新規
  Fact・結論・教訓の追加禁止)を明示し、「参考ガイド(Trial限定、厳密
  ルールではない): 主節1つ+従属節最大1つ、およそ12〜18語」を追記。
  見出しMarkup生成の指示は含まない(テストで確認)。
- 入力本文: `{out_dir}/v2/trial_translation_v2.json`が存在すれば
  それ(Meta、must-fix retry後)、無ければv1の`trial_translation`
  (Hormuz)。

### 7-3. `--stage rubric-v2`(両記事)

- v1と同じ`run_rubric()`(14項目、Comment文脈込み)を、Meta本文はv2
  (must-fix retry後、存在すれば)、Hormuz本文はv1(不変)を使って
  再実行。In One Line欄はv2のテキストを使う。目的はIn One Line
  v2反映後の`in_one_line_conciseness_accuracy`等の更新であり、
  本文自体の再評価(Hormuz)は同じ1 callの副産物として得られる値。

### 7-4. ページ(`--build-page`)への統合

`_attach_v2(result, result_dir)`が`{result_dir}/v2/*.json`の存在有無を
見て`result['v2']`へ添付する(API呼び出しなし)。`_render_v2_section()`が
存在する場合のみ「修正1回目」セクションを記事ごとに追記する(v1
セクションは無変更のまま残り、v1/v2併載)。

結果・費用実測・テスト結果は
`FAMILY-X-TRANSLATION-SEGMENTATION-NO-HEADING-TRIAL-01_REPORT.md`§13に
記載。
