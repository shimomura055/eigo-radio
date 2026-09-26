# spec_strict_ja.md

## ユーザー決定の厳格仕様(逐語、2026-09-26)

- 閾値: Standard 約6,000位 / Advanced 約12,000位(閾値超を原則平易化候補。必ず置換ではなく、より簡単で自然な表現がある場合に平易化を強く優先)。B/C/D定義は両Levelで同一。
- A(維持): 易しい既知語から構成され、英語学習者が構造から意味を自然に推測できる形態・複合語。単に形態素分解できるだけではKEEPしない。
- B(厳格): 日本語で使われているだけでは不十分。日本人英語学習者がその英語の語形・発音を見聞きしたとき、日本語として知っている語と自然に結び付き、意味をほぼ迷わず理解できる場合だけB。Bにしない: 英語語形との対応が分かりにくい/日本語で専門領域にしか定着していない/英語文中で理解しにくい/「カタカナ語として存在する」だけ。特に leak / pause / curtain を再判定。
- C(厳格): 本当の固有名詞・公式名称・固有の引用名称だけ(人名・地名・組織名・商品/サービス名・公式名称・報道上その呼称自体がFactになっている固有の引用名称[例: Metaが実際に "human concierges" と呼んだ])。Cにしない: 一般名詞が引用符に入っているだけ/一般的な技術用語/記事中で引用されているだけ/Writerが強調のため引用符を付けただけ。septic / septic tank をCと判定してはならない(Promptに個別語名は書かず、定義で導く)。
- D(厳格): より易しい自然な語・表現へ置換すると、記事の意味の核心・事実精度・必要なニュアンスが明確に壊れる場合だけKEEP。Dにしない: 専門用語だから/元記事で使われているから/比喩として少し自然だから/Writerの表現として気に入っているから/置換すると少し雰囲気が変わるから。可能な簡単語があればSIMPLIFY優先。特に artery / sewer(s) / flush / septic を再評価。

## 対象(既存本文、新規Researchなし)
- Standard: Meta er012_output/e_family_two_level_wiring_01/meta/a2/article.md、Sewer er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/a2v5_standard_sewer.md(前回と同一)
- Advanced: Meta er012_output/e_family_two_level_wiring_01/meta/b1b/article.md、Sewer er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md(Advanced v2 Trialと同一)
