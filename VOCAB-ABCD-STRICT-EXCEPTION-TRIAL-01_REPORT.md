# VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01_REPORT.md

管理ID: VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01(Sonnet実行、2026-09-26)

Production実装ではない。Trialのみ(最大VALIDATED)。Production Prompt
(`er003_v1_n3_01_standard_a2_generate.py` Standard v5、
`er003_v1_n3_01_advanced_adaptation_generate.py` Advanced v2)は一切変更
していない。既存Standard/Advanced本文artifactの上書きもしていない。新例外
カテゴリの追加もしていない(既存A/B/C/Dの定義文言をユーザー確定の厳格版へ
差し替えたのみ)。新スクリプト`er015_vocab_abcd_strict_exception_trial_01.py`、
新出力dir`er015_output/vocab_abcd_strict_exception_trial_01/`のみを使用した。

## §1 目的

STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01(閾値6,000版)で、Sewer記事の一般
名詞`septic`(「combined septic tank」という引用符付きフレーズの一部に
過ぎない)が誤って C(固有名詞)としてKEEPされる事例が生じた。本Trialは
ユーザーが逐語で確定した厳格なA/B/C/D定義(下記§2)へPrompt文言を差し替え、
Standard(6,000位)/Advanced(12,000位)の両方・同一記事(前回と同一素材、
新規Researchなし)へ再適用した場合の判定を検証し、あわせて前回誤判定の
構造的原因を分析する。

## §2 厳格仕様(原文+Prompt差分)

ユーザー原文は`er015_output/vocab_abcd_strict_exception_trial_01/
spec_strict_ja.md`に逐語保存。英訳版Prompt本体との差分(前回v2との比較、
閾値12,000に揃えて逐語diff)は`prompt_diff_v2_vs_strict.md`。結論:

- 一般原則・Aの定義は実質変更なし。
- Bに「カタカナ語が存在するだけでは不十分」「英語語形との対応が分かり
  にくい/専門領域限定/文中で理解しにくい場合はBにしない」という否定条件と
  leak/pause/curtainの再判定指示を追加。
- Cから、v2が追加した「引用符内の語は事実として保護する」という一般化
  条件を削除し、「本当の固有名詞・公式名称・固有の引用名称だけ」に限定。
  「一般名詞が引用符に入っているだけ」「一般的な技術用語」「記事中で
  引用されているだけ」「Writerが強調のためのみ引用符」を明示的な否定条件
  とした(個別語名`septic`はPromptに書かず、定義文のみで導けるかを検証)。
- Dに「専門用語だから/元記事で使われているから/比喩として少し自然だから/
  Writerが気に入っているから/雰囲気が変わるから」は理由にしないという
  否定条件と、artery/sewer(s)/flush/septicの再評価指示を追加。

## §3 方法

- `er015_advanced_vocab_rule_trial_01_v2.py`の`lemma_candidates_v2`/
  `rank_of_word_v2`(rank = min(surface, best lemma)、-s/-es/-ies/-ed/
  -ing/-lyのみ、-er/-est除去なし)・`fact_tokens_check`をStandard/Advanced
  共通でそのまま流用(思想差ゼロを維持)。
- JSON schemaに`decision`(enum: KEEP-A/KEEP-B/KEEP-C/KEEP-D/SIMPLIFY/
  BORDERLINE)・`replacement_if_simplify`・`meaning_or_fact_change`
  (none/minor/major)を追加。
- 4 call(Standard Meta/Sewer、Advanced Meta/Sewer)。model=gpt-5.6-luna、
  effort=high、previous_response_idなし、web_searchなし、retried=false
  (全call初回成功)。
- 対象は前回と同一のBefore本文(§対象は前回§4と同一パス)。

## §4 Standard結果

### Meta(候補10語、BORDERLINE参考1語)
判定内訳: KEEP-C 2(concierges, Reuters)/KEEP-B 2(leak, curtain)/
KEEP-A 4(performer, understandable, backstage, onstage)/SIMPLIFY 2
(pause->temporarily turn off, paused->temporarily turned off)。
語数308→312(+4)、文数31→31(差0)。**見出し1本が変化**
(`### Privacy concerns led Meta to pause the feature` ->
`### ...to temporarily turn off the feature`)。これは契約上「見出しに
SIMPLIFY対象語があれば見出しも変えてよい」という明示ルールに正しく従った
結果であり違反ではない(旧STRUCTURE_BLOCKの記事別注記「見出しに候補語は
無い」はAdvanced閾値12,000を前提にした記述で、Standard閾値6,000では
`pause`[rank 7,166]が候補になるため事実と齟齬があった。動作自体は契約の
明示的例外に従っており問題ではないが、注記文言の齟齬は今後の注意点として
記録する)。`fact_tokens_check.overall_fact_tokens_match=true`(完全一致)。

### Sewer(候補8語、BORDERLINE参考4語)
判定内訳: KEEP-A 2(faraway, wastewater)/SIMPLIFY 6(**septic->treatment**,
invisible->hidden, flush->use the toilet, artery->main pipe,
sewer->underground pipe system, sewers->underground pipe systems)。
**KEEP-D・KEEP-C・KEEP-Bは0件**。語数337→346(+9)、文数34→34(差0)、
見出しなし契約維持。`fact_tokens_check.overall_fact_tokens_match=false`
(引用符内フレーズ`"combined septic tank,"`->`"combined treatment tank,"`
のみが変化。septicが正しくSIMPLIFYされた副作用であり、数字・固有名詞は
完全一致。Fact違反ではなく想定通りの挙動)。

## §5 Advanced結果

### Meta(候補2語)
判定内訳: KEEP-C 1(concierges="human concierges"、Metaが実際に使った
呼称として正しく維持)/KEEP-A 1(onstage)。語数差0、文数差0、見出し・
段落完全一致、fact_tokens_check完全一致。

### Sewer(候補5語)
判定内訳: KEEP-A 1(wastewater)/SIMPLIFY 4(**septic->household wastewater
treatment**, artery->main pipe, sewer->wastewater collection system,
sewers->wastewater collection systems)。**KEEP-D・KEEP-B・KEEP-Cは0件**。
語数337→352(+15)、文数差0、見出しなし契約維持。fact_tokens_check不一致
(引用符フレーズがseptic簡易化により変化、Standardと同様に想定内)。

**品質上の注意点(1件)**: `septic`はBefore本文中に4箇所出現するが、After
では3箇所のみ`household wastewater treatment`系へ置換され、
paragraph8(「Of course, having a **septic tank** does not mean...」)の
1箇所だけ`septic`のまま残った(Standard版では4箇所すべて`treatment`へ
一貫して置換されており、この不整合はAdvanced Sewerのみで発生)。Fact自体
(数字・固有名詞)は壊れていないが、同一語の置換一貫性という観点では
モデル側の実行漏れであり、Production採用時には「宣言したSIMPLIFY語は
記事全体で一貫して置換されているか」の機械チェックを追加する価値がある
所見として記録する。

## §6 Level間対照

`cross_level_comparison.md`参照。Standard/Advanced両方で候補になった語
(concierges, onstage, artery, septic, sewer, sewers, wastewater)は
**すべて同一判定**だった(閾値差により片方のみ候補になる語[leak, pause,
curtain, flush, invisible等]を除く)。B/C/D定義文言はレベル間で完全同一
であるため、これは「閾値以外の差は出ていない」ことの直接的な確認結果で
ある。

## §7 評価

- **septic->C解消**: 4記事すべてでseptic候補は`KEEP-C`にならず、Standard/
  Advanced双方でSIMPLIFYと正しく判定された(Promptにseptic個別語名は
  書いていない、定義文のみでの是正を確認)。
- **B過剰救済の減少**: Standard Metaで`pause`/`paused`がKEEP-B->SIMPLIFYへ
  転換(理由: ポーズは「pose」と混同しやすく、この文脈で意味が一義的に
  伝わらないため厳格Bの要件を満たさないとモデル自身が判断)。`leak`
  (リーク)・`curtain`(カーテン)は厳格審査後も日常的で一義的な対応がある
  としてKEEP-Bを維持(理由もB定義の否定条件に触れて明示的に反証している)。
- **D過剰救済の減少**: 4記事合計で**KEEP-Dは0件**(前回はartery/sewer/
  sewers/flushが軒並みKEEP-Dだった)。Advanced Sewerの`artery`も、前回
  KEEP-D(比喩保持)からSIMPLIFYへ転換し、モデル自身が「metaphor alone
  does not qualify for D」と明言した(ユーザーが問題視していた
  「比喩を理由にしたD」の根拠が消えたことを裏付ける)。
- **StandardがA2相当へ平易化されたか**: Sewerで6/8語がSIMPLIFYされ
  (前回0/8)、Metaも2/10語がSIMPLIFY(前回0/10)。厳格運用により候補語の
  大半が実際に平易化される結果となった。
- **Advancedで不必要な平易化がないか**: Advanced Metaは候補2語ともKEEP
  (Fact由来のconcierges、構造から推測可能なonstage)で、平易化ゼロ。
  Advanced Sewerは4/5語がSIMPLIFYされたが、いずれも厳格D基準(意味・
  事実精度・必要なニュアンスの明確な毀損)を満たさないとモデルが判断した
  結果であり、Fact/構造チェックはいずれも(引用符内の想定内変化を除き)
  完全一致。
- **不自然置換**: 目視確認の範囲で明確な不自然置換は見つからなかったが、
  `underground pipe system(s)`(Standard)・`wastewater collection
  system(s)`(Advanced)は元の`sewer(s)`より長く、同じ語が繰り返し使われる
  ため文体がやや冗長になった(意味は保持されている、Fable評価事項として
  記録)。
- **難語->難語**: `new_rare_words_gt_threshold_in_after`は4記事すべて空
  配列(`[]`)。難語を別の難語へ置換したケースはコード側の再検査でも
  検出されなかった。
- **Fact drift**: `numbers_match`/`proper_noun_words_match`は4記事すべて
  true。`quoted_strings_match`はStandard/Advanced Sewerのみfalse(septic
  simplify副作用、内容としては想定内で問題ない)。
- **Storytelling毀損**: 中心比喩("A sewer/wastewater collection system is
  like an invisible main artery/pipe beneath the town")・結びの論理
  ("The future of sewers/underground pipe systems may arrive...")は
  いずれも保持されていた(diff確認済み)。

## §8 前回C誤判定の原因分析

`c_misjudgment_analysis.md`に詳細($0、API呼び出しなし)。要旨: v2の
C定義に、Meta記事の"human concierges"を守るため追加された一文
"Words that appear inside quotation marks in the article, ... are facts
of the article. Do not simplify such a word ... treat it under exception
C ..."が、「記事中で引用符に入っている語」という条件を、後半の「特定の
人物・組織が実際に使った呼称」という条件から独立した単独十分条件として
読める構造になっていた。この結果、Sewer記事でWriterが読者への導入表現
として使っただけの一般名詞句"combined septic tank"にまでC保護が誤って
適用された。本Trialの厳格C定義はこの一般化条件を削除し、「一般名詞が
引用符に入っているだけ」を明示的な否定条件としたことで是正を確認した。

## §9 QCD

- Quality: 4記事とも構造契約(見出し[1件の明示的許容例外を除く]・段落数・
  文数)完全維持、fact_tokens_checkは数字・固有名詞について完全一致
  (引用符フレーズのみseptic簡易化の想定内副作用で不一致)。新出難語0件。
  唯一の品質欠陥はAdvanced Sewerの`septic`置換が本文中1箇所だけ未反映
  だった点(§5参照)。
- Cost: 実測 JPY 5.8593円(standard_meta 1.6148 + standard_sewer 2.2706 +
  advanced_meta 0.2771 + advanced_sewer 1.6968)、上限JPY 10円以内。
  web_search不使用。retried=false(全call初回成功)。
- Delegation: Sonnet実行1回のみ(初回)、上限内。

## §10 Sonnet仮分類(最大VALIDATED)

**VALIDATED(仮)**。前回誤判定(septic->C)は、Promptに個別語名を書かず
定義文言の是正のみで、Standard/Advanced双方・両記事で解消された。B/D側の
過剰救済(pause/leak/curtain、artery/sewer/flush)も、厳格定義下でモデル
自身が具体的な否定条件を挙げて再判定し、期待どおりKEEP-D 0件・
BORDERLINE 0件という結果になった。Level間対照でも閾値差以外の判定差は
観測されなかった。

留保点(仮分類に留める理由):
1. Advanced Sewerで`septic`の置換が本文中1箇所だけ未反映という一貫性欠陥
   が観測された(§5)。Fact自体は壊れていないが、Production採用を検討する
   場合は宣言済みSIMPLIFY語の全文一貫性チェックが必要。
2. `underground pipe system(s)`/`wastewater collection system(s)`という
   置換語がやや長く、繰り返し使われることで文体が冗長になる傾向が観測
   された(意味は保持)。
3. 本Trialは前回と同じ2記事(Meta/Sewer)のみの検証であり、他記事・他
   ジャンルでの汎化性は未確認。
4. 旧STRUCTURE_BLOCKの記事別注記(「見出しに候補語は無い」)がStandard
   閾値では事実と齟齬していた点は、動作自体に問題はなかったが、将来
   Prompt整理時の注意点として記録する。

## §11 Fable評価

[Fable記入]

## §12 分類

[Fable記入]
