# STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01_REPORT.md

管理ID: STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01(Sonnet実行、2026-09-26)

Production実装ではない。Trialのみ。Production Prompt(`er003_v1_n3_01_
standard_a2_generate.py` Standard v5、`er003_v1_n3_01_advanced_adaptation_
generate.py` Advanced v2)は一切変更していない。既存Standard本文artifact
の上書きもしていない。新スクリプト`er015_standard_vocab_abcd_alignment_
trial_01.py`、新出力dir`er015_output/standard_vocab_abcd_alignment_
trial_01/`のみを使用した。

## §1 目的

ユーザー方針「AdvancedとStandardで語彙ルールの思想に差をつけない。差は
頻度ラインのみ(Advanced 12,000 / Standard 6,000)」を検証するため、
Production採用済みAdvanced v2(ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01、
2026-09-26 `APPROVED_FOR_PRODUCTION`)と**一字一句同一の語彙ルール文言
(A易しい語からの推測可能形態/B日本語定着外来語/C固有名詞・引用符内呼称/
D不可欠語、閾値以外の一般原則)を、閾値のみ6,000へ差し替えて**、既存
Production E2E版Standard v5本文(Before、Meta/Sewer各1本)へ適用した場合に
何が起きるかをTrialとして検証する。目的は仕様候補の実際の挙動の実測で
あり、Production採用判断ではない。

## §2 方法

1. `er015_advanced_vocab_rule_trial_01_v2.py`(fix01のv2、Production
   Advanced v2 Promptの出典元)の`lemma_candidates_v2`/`rank_of_word_v2`
   (rank = min(rank(surface), rank(best lemma candidate))、-s/-es/-ies/
   -ed/-ing/-lyの単純規則のみ、-er/-est比較級除去は使わない)、
   `fact_tokens_check`(引用符/数字/大文字語のBefore-After一致確認)を
   そのまま流用した。
2. Prompt本体`RULE_BLOCK_EN_V2`(Production `ADVANCED_VOCAB_RULE_V2_BLOCK`
   と同内容)に対し、`"12,000" -> "6,000"`の数字2箇所のみを置換した
   (置換件数をコードでassert)。TASK_TAILのBORDERLINE参考範囲コメントも
   `"10,000-12,000" -> "5,000-6,000"`の数字1箇所のみ置換。DEVELOPER_
   MESSAGEのみ、テスト対象がCEFR B1(Advanced)ではなくCEFR A2(Standard)
   であるという文脈上の呼称を`CEFR B1 ("Advanced")` -> `CEFR A2
   ("Standard")`に改めた(語彙ルール本体の文言ではない、開示済みの唯一の
   例外)。逐語diffは`er015_output/standard_vocab_abcd_alignment_trial_01/
   prompt_diff_advanced_v2_vs_standard.md`に保存。
3. 6,000位超(top20000圏外含む)を候補語、5,000〜6,000位をBORDERLINE参考
   語としてコード側で確定し、順位を文字列としてPromptへ明記した(モデルに
   順位を推測させない)。
4. 入力はStandard v5本文(Before、Production E2E版):
   - Meta: `er012_output/e_family_two_level_wiring_01/meta/a2/article.md`
   - Sewer: `er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/
     a2v5_standard_sewer.md`
5. 記事ごとに1 call(計2 call、model=gpt-5.6-luna、effort=high、
   json_schema strict、previous_response_idなし、web_searchなし)。
   技術的失敗のみ1回まで再試行(実際には両記事とも初回成功、retried=
   false)。
6. 分析: 6,000超候補一覧・ABCD判定・平易化/KEEP対象・不自然置換の有無・
   難語→難語置換の有無(After新出語のrank再算出)・fact_tokens_check・
   構造/語数/文数チェック。

## §3 Meta結果

候補10語、BORDERLINE参考1語(convenient, 5,588位)。**全10語がKEEP、
SIMPLIFYはゼロ**。判定内訳: KEEP--established Japanese loanword 4語
(leak, pause, paused, curtain)/KEEP--predictable morphology/compound 4語
(performer, understandable, backstage, onstage)/KEEP--proper noun 2語
(concierges[引用符内の実際の呼称"human concierges"として維持]、Reuters
[固有名詞])。

Before/After: 語数308→308(差0)、文数31→31(差0)、見出し・段落数完全一致、
`meta_diff.md`のunified diffは空(1文字も変わっていない)。
`fact_tokens_check.overall_fact_tokens_match = true`(引用符・数字・
大文字語すべて一致)。

## §4 Sewer結果

候補8語、BORDERLINE参考4語(distant 5,212/installation 5,508/convenient
5,588/divide 5,876)。**全8語がKEEP、SIMPLIFYはゼロ**。判定内訳:
KEEP--predictable morphology/compound 3語(faraway, invisible,
wastewater)/KEEP--proper noun 1語(septic、後述§9で要検討)/
KEEP--indispensable / natural replacement unavailable 4語(flush, artery,
sewer, sewers)。

Before/After: 語数337→337(差0)、文数34→34(差0)、見出しなし契約維持
(`no_heading_contract_kept=true`)、段落数一致、`sewer_diff.md`の
unified diffは空。`fact_tokens_check.overall_fact_tokens_match = true`。

## §5 難語→難語置換チェック

SIMPLIFYが0件のため、置換自体が発生していない。したがって「難語を別の
難語へ置換した」ケースは論理的に存在しない。`new_rare_words_gt6000_
in_after`はMeta/Sewerとも空配列(`[]`)で、コード側の再検査でも一致した。
band参考値(A/B/C/D lemma bucket)もBefore/After完全一致。

## §6 Standard v5(Before)との差

**候補ゼロにはならなかった**(Meta 10語・Sewer 8語)。これはStandard v5
Production Promptが「6,000位超を必ず置換ではなく自然さ優先で平易化」と
いう緩い基準であるため、Writer(v5 Production生成)が既にA〜D相当の判断を
暗黙に行い、6,000超の語(leak, pause, curtain, performer, understandable,
backstage, onstage, artery, sewer, wastewater等)を「文脈上必要」として
残していたためである。本Trialでは、これら残存語を明示的なABCD例外構造で
**改めて評価し直した結果、全語がやはりKEEPと判定され、1語も追加で平易化
されなかった**。すなわち「候補はゼロではなかったが、SIMPLIFY結果はゼロ
だった」。これはv5の暗黙の仕組み(自然さ優先・必ず置換ではない)が、
Advanced v2の明示的ABCD構造と同じ結論に実質的に収束していることを示す
実測結果であり、「候補ゼロならゼロと明記」という事前予測に近い(候補は
非ゼロだが決定はゼロ)。

## §7 思想差チェック表(Production Standard v5 vs Production Advanced v2、所見のみ)

対象: `er003_v1_n3_01_standard_a2_generate.py` STANDARD_A2_PROMPT_V5の
語彙6行 vs `er003_v1_n3_01_advanced_adaptation_generate.py`
ADVANCED_VOCAB_RULE_V2_BLOCK。**Production変更はしない、所見のみ。**

| # | Standard v5(該当行) | Advanced v2(該当箇所) | 思想差の所見 |
|---|---|---|---|
| 1 | "Prefer words within roughly the 6,000 most common English words." | "Words that rank below roughly the top 12,000... are, in principle, candidates for simplification. This is NOT a mechanical ban list." | 一般原則は同じ(閾値超=平易化候補、機械的禁止リストではない)。差は数値のみ、思想差なし。 |
| 2 | "If a word is clearly outside that range, replace it when a simpler natural alternative exists." / "Do not force a replacement if it makes the sentence less natural or changes the meaning." | "simplification should be strongly preferred only when a simpler, natural expression exists...; it must not be forced when it would [harm meaning/naturalness]" | 実質同一の原則。思想差なし。 |
| 3 | "Proper names are excluded from this rule." | C: "proper noun..." に加え、**引用符内の語・実際に使われた呼称/名称(例: "human concierges")もCの適用範囲として明示**("Words that appear inside quotation marks... are facts of the article. Do not simplify such a word...") | **思想差あり**。v5は固有名詞の除外のみを述べ、「引用符内の実際の呼称」への明示的言及がない。v5生成記事にも同種のFact("human concierges")が存在するため、v5側にもこの明文化を将来検討する余地がある(本Trialでは変更しない)。 |
| 4 | "Essential technical terms may remain when a simpler equivalent would lose important meaning." | D: "Replacing it with an easier word would clearly hurt meaning precision or naturalness -- indispensable. Do not keep a word only because \"it is a technical term\" -- if a simple, natural, meaning-preserving substitute exists, simplify it." | 実質同じ条件(意味を損なう場合のみ残す)だが、Advancedは「技術語だからというだけでは残さない」という**逆方向の明示的警告文**を追加で持つ。v5にはこの警告文がない(軽微な明文化差、実害は本Trialでは未観測)。 |
| 5 | "Do not add an explanation for a hard word; make the sentence around it simple instead." | 該当なし(Advanced側にこの特定の指示は存在しない。一般則として「新しい説明・事実を追加しない」はADVANCED_COMMON_BLOCK_PREFIXに別途あるが、語彙ルールブロック内には「難語への説明追加を禁止」という専用文がない) | **思想差あり**。v5固有の追加指示。タスク指示で事前に想定されていた差分そのもの。 |
| 6 | 該当なし(idiomに関する言及なし) | "Do NOT use \"it is part of a fixed expression / idiom\" as its own exception category." | **思想差あり**。Advanced固有の追加指示(定型表現内でも通常通り判定する)。v5にはこの明文化がない。 |
| 7 | A(易しい語からの推測可能形態)/B(日本語定着外来語)の**個別カテゴリ名・具体例(onstage/wastewater/understandable、piano/curtain/privacy)の明文化なし** | A/B/C/Dの4カテゴリを名前付きで明文化し、各々に具体例を持つ | **思想差あり(タスク事前想定通り)**。v5は「Proper names」「Essential technical terms」の2条件のみで、A/Bに相当する「推測可能形態」「日本語定着外来語」という独立カテゴリの明文化がない(実務上はWriterが自然に同種の判断をしている可能性があるが、Prompt文言としては存在しない)。 |

## §8 QCD

- Quality: Meta/Sewer両記事とも構造契約(見出し・段落数)完全維持、
  fact_tokens_check完全一致、SIMPLIFY 0件・不自然な置換0件・難語→難語
  置換0件。判定理由(reasoning)はすべてABCD例外に明示的に対応しており、
  恣意的な判定は観測されなかった。唯一の要検討点はSewerの"septic"が
  「引用符内の実際の呼称」ではなく一般的な技術用語であるにもかかわらず
  KEEP--proper nounとして分類された点(§9参照)。
- Cost: 実測 JPY 2.541円(Meta 1.2988円 + Sewer 1.2422円)、上限JPY 5円
  以内。web_search不使用。retried=false(両記事とも初回成功)。
- Delegation: Sonnet実行1回のみ(初回)、上限内。

## §9 Sonnet仮分類(最大VALIDATED)

**VALIDATED(仮)**。閾値以外は完全に同一の語彙ルール文言をStandard
(6,000位ライン)へ適用した結果、Meta/Sewer両記事で構造・事実・語数文数を
完全維持したまま、既存Standard v5 Before本文に対する追加のSIMPLIFYは
1件も発生しなかった(候補語10+8語すべてがKEEP、難語→難語置換も0件)。
これは「AdvancedとStandardで語彙ルールの思想に差をつけない」というユーザー
方針が、少なくともこの2記事のBefore本文に対しては安全に(regressionなく)
適用できることを示す一次証拠である。

留保点(仮分類に留める理由):
1. Sewerの"septic"がKEEP--proper nounと分類された判定理由は、正確には
   「引用符内の実際の呼称」の趣旨(Metaが労働者を"human concierges"と
   "実際に呼んだ"という報道上の事実)とは性質が異なり、一般的な技術用語
   "combined septic tank"が記事中で引用符付きで言及されているに過ぎない
   (誰かが独自にそう呼んだという固有の呼称ではない)。モデルの判定理由が
   ルールの意図をやや拡大解釈した可能性があり、要目視確認。
2. 本Trialは「Before本文が既にStandard v5の思想で生成済み」という条件下
   での検証であり、新規生成本文(v5でまだフィルタされていない一次生成
   結果)に本ルールを直接組み込んだ場合の挙動は未検証(§6参照、Production
   組み込み方式[改稿pass vs 直接生成]の判断も本Trial範囲外)。
3. 記事2本(Meta/Sewer各1本)のみのTrialであり、他ジャンル・他記事での
   汎化性は未確認。

## §10 [Fable記入]

## §11 [Fable記入]
