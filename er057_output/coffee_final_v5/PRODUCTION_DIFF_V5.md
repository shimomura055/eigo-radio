# PRODUCTION_DIFF_V5 (v4 -> v5 provenance差分、Std/Adv確定)

## std: 変更role 5件 / 不変 25件 / 尺 v4 317.683s -> v5 316.603s(peak 0.9572 -> 0.9505)
- preview: v4 9e54868b1342 -> v5 b9739f509f5e (P2 -> R2)
- comment_1: v4 8b2248d7a82d -> v5 1381b2418be6 (P2 -> R2)
- comment_2: v4 d94da2084ffb -> v5 9a588e46c189 (P2 -> R2)
- comment_3: v4 b9496509481b -> v5 4500cb0fb87d (P2 -> R2)
- comment_4: v4 237d2c7f584b -> v5 d108c5872efd (P2 -> R2、文章も新Prompt(Trial-03最小修正)で再生成)
- 不変25 role(sha256一致): Full Story Part1〜3(P8+6%減速、v4音声)、In One Line、Intro/固定shell、topic_intro、japanese_title、KP英語5・日本語意味5 等。`provenance_diff_v5_std.json` 参照。
- Std Comment 4 文章: v4「コーヒー豆の値段が下がっても、店の値札がすぐに変わるとは限りません。値段が変わる時期には、豆以外の費用も関わります。続いて、記事の要点を英語で聞いていきましょう。」(81字) -> v5「コーヒー豆の相場が動いても、店の値札にすぐ表れるとは限りません。カフェの値段には、豆以外の費用も関わっています。最後に、英語で記事の要点を振り返ります。」(76字、3文、「最後に」、gpt-6-luna、Production Prompt定数、attempt1)。

## adv(委任_02で確定): 変更role 5件 / 不変 24件 / 尺 v4 317.07s -> v5 315.71s(peak 0.9800 -> 0.9800)
- kp1_explanation_en: v4 1f5728335b06 -> v5 da1d5b752d65 (P0 -> P3)
- kp2_explanation_en: v4 00840679c3b9 -> v5 f86f7a907c5f
- kp3_explanation_en: v4 613e88f0e604 -> v5 69e6cd9a7a2d
- kp4_explanation_en: v4 ecc706afc931 -> v5 99695c64900e
- kp5_explanation_en: v4 fc58921d490c -> v5 9e37b57805ab
- 不変24 role: Full Story Part1〜3(P8、v4音声)、In One Line(v4)、固定shell等、KP英語・日本語意味。`provenance_diff_v5_adv.json` 参照。英語解説の文章(text)はv4のまま。
- 所見: headroom safety valve発動(原因 Key Phrase 5のP3新clip、peak_before 1.0522→scalar 0.9314で全体0.98へ。v4はscalar 0.9953)。全体が約-0.6dB下がる(clipping 0)。

## 変更していないもの(確認)
Production共通定数 `FAMILY_X_ROLE_STYLE_EN`/`FAMILY_X_ROLE_STYLE_JA`/`KEY_PHRASE_EXPLANATION_EN`、`FAMILY_X_B1_COMMENT_*`、`FAMILY_X_A2_COMMENT_1〜3`、共有module(er003/er006/er011/er033)、Master Store、v4成果物(`er057_output/coffee_final_v4/`、`user_test/coffee_final_v4/`)、Production原稿(`er019_output/coffee_prices/run_l3_01`)。変更: `FAMILY_X_A2_COMMENT_4_ROLE`(ユーザー承認A)、`er019_family_x_style_profile_01.py`(profile拡張)、runner(R2/P3解決・記録、`--only-segments`)。
