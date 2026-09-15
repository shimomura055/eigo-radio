# B-Family Voices 2V 三人称化 調査結果(USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-VOICES)

## 結論

**一人称"I"での記述は既存正式仕様(APPROVED_FOR_PRODUCTION)であり、現2V記事
(`voices/run2_clean/b1_2v_new_theme_attempt3/article.md`)の三人称化は
**Production不整合(Writer Promptのバグ)** である。新仕様ではない。

## 根拠1: CURRENT_SPEC.md — ユーザー正式決定の記録

`CURRENT_SPEC.md`(354行目付近、`PM-CLOSEOUT-CONSOLIDATION-05`エントリ)に
以下の記載がある(原文引用):

> 2026-09-08(PM-CLOSEOUT-CONSOLIDATION-05、ユーザーが2026-09-08にB-Family
> [Voices]のTrial-09完成episodeを試聴し、`APPROVED_FOR_PRODUCTION`と正式
> 決定した4項目[(1) Voice A=Algieba/Voice B=Erinome/Narrator見出し=Aoede
> 固定、(2) Tension slot「Where the Difference Comes From」の正式構造への
> 追加、(3) Key Phrase位置=Preview直後(現状維持)、**(4) Voice A/Bの一人称
> "I"記述**]を記録した。

「Voice A/B」という命名は2V(2声Voice構成、`voice_a`/`voice_b`)方式そのもの
(3VはRegistry上`voice_1`/`voice_2`/`voice_3`または`voice_a`/`voice_b`/
`voice_c`)であり、この決定はまさに現在の2V記事タイプに直接該当する。

続く`PM-CLOSEOUT-CONSOLIDATION-11`(2026-09-08、B-Family Production Path
Phase 1)には次の注記がある:

> スコープ注記: B-Family(Voices)の音声Production経路(既存承認済み記事→
> Voice A/B/Narrator固定・Tension slot・Key Phrase位置・Comment 1〜4確定版
> Contract・A-Family同規約の安全機構→Assembly)のみで、記事生成(Writer)・
> Key Phrase選定は範囲外、**一人称"I"の機械保証はPhase 2保留**。

これは「一人称"I"記述」という仕様自体が撤回・保留されたのではなく、Phase 1の
配線スコープが「既存承認済み記事を音声化するAssembly経路のみ」であり、Writer
プロンプトへ一人称を**機械的に強制するValidator**の実装がPhase 2待ちだった、
という意味である(仕様=`APPROVED_FOR_PRODUCTION`のまま、機械的保証だけが
未実装)。

## 根拠2: Writer Prompt本体の実装差分(3V vs 2V)

`er012_b_family_voices_writer_generic_01.py`の3V用テンプレート
(`COMMON_INTRO_AND_STRUCTURE_BLOCK_TEMPLATE`、255〜262行目、修正前)には
明示的な人称指示ブロックが存在する:

> 【人称(重要、4V版から継続、ユーザーが承認済みの原則)】
> 3人のVoiceセクション(Voice 1〜3)の本文はすべて、その人物自身が"I"で語る
> 一人称で書いてください。三人称("The applicant feels...", "She
> worries...", "He must choose...")ではなく、"I look at...", "I know...",
> "I cannot..."のように、その人物自身の声として書いてください。(…)

加えて禁止事項まとめ(347〜348行目)にも同旨のリマインダーがある。

一方、2V用テンプレート(`COMMON_INTRO_AND_STRUCTURE_BLOCK_TEMPLATE_2V`、
修正前)には、この【人称】ブロックが**丸ごと欠落**していた。存在したのは
【Narrator(語り手)がVoiceの人物を外側から要約・分析しないこと】という、
語り手の三人称的要約を禁じる指示のみで、「Voice本人は一人称"I"で書く」と
いう明示的な指示そのものが無かった。禁止事項まとめにも同種のブロックが
無かった。

コメント(2V template冒頭、修正前498〜501行目)には「2V Trial-07で確立した
構造原則をテーマ非依存の共通テンプレートとして正式に切り出したもの…人称
指示…はTrial-07から内容を変更していない」とあり、Trial-07由来の欠落が
そのままテンプレート化された経緯がうかがえる(Trial-07自体は承認済み記事が
たまたま一人称で書かれていたため[根拠3参照]、Promptの欠落が表面化しな
かったと推測される)。

## 根拠3: 承認済み実例記事(2V/3V とも一人称)

- **2V(PRODUCTION_WIRED)**: `er012_output/editorial_b_voices_trial_07/
  b1b_run02_attempt2/article.md`(Voice A/B、Tension slot構造、`er012_b_
  family_production_runner_01.py`のA2 Production記事`_04`と同じ2026-09-09
  承認系列)。実例:
  > Every morning, **I** look for an empty desk. (…) **I** cannot leave
  > papers in a drawer, and **I** sometimes worry about (…)
  > Some mornings, **I** choose a quiet corner because **I** need to
  > think. (…)
  完全に一人称"I"で書かれている。

- **3V(APPROVED_FOR_PRODUCTION、`ARTICLE_PATH_3V`)**:
  `er012_output/editorial_b_voices_3v_person_voice_trial_02/
  b1b_run01_attempt2/article.md`。実例:
  > **I** speak to a camera while software scores my tone, face, and
  > gestures. (…) **I** start with résumés and an AI tool that sorts
  > them (…)
  こちらも一人称"I"。

対して現在問題の記事(`run2_clean/b1_2v_new_theme_attempt3/article.md`)は:
> On the morning train, **she** opens a news app's "For you" page. (…)
> **She** follows topics and sources (…) **She** still worries that (…)
完全な三人称("she"多数、"the reader"に相当する代名詞)。

## 判定

一人称"I"での記述は、(a) ユーザーが2026-09-08に`APPROVED_FOR_PRODUCTION`と
明示決定した仕様項目そのもの、(b) 3Vテンプレートで実際にPrompt化されている
既存原則、(c) 2V/3Vいずれの承認済み実例記事も実際に満たしている実装パターン
である。現2V記事の三人称化は、2V用Focus Moduleテンプレートにこの指示ブロック
が欠落していたことに起因する**Production不整合(Writer Promptのバグ)**であり、
新しい仕様判断を必要としない。
