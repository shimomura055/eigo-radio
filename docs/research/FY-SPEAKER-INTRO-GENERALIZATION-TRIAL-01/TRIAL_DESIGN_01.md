# FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01 設計(Trial。到達Status上限=VALIDATED。2026-10-29 FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01 委任_04A)

原文=`docs/pm/delegation_log/2026-10-29_FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01_USER_02.md` §2。DEV/Trial専用経路。Production Prompt・関数は直接編集していない。

## 1. 現状(Y人物紹介の生成箇所・仕様)
- 生成: `er121_family_y_text_core_01.py:1665 generate_intros`(3本を1 call、route `FAMILY_Y_PERSONA_INTRO`=gpt-6.1-sol/high、`:48`)。Prompt=`er121_prompts/persona_intro_01.txt`(sha固定、`load_article_prompt('intro')`)。入力の人物ブロック=`:1650 person_block`(Theme Package sheetsの`role_ja`・`daily_life_ja`・`identity_cue_ja`・本人の語り[読取専用])。
- 決定論検査: `:1615 check_intro`(一人称禁止・主張先取り語・本人語りとの10字連続一致・役割伝達[role_ja+who_jaの2字連続]・字数`INTRO_RANGE=(32,62)`:1482)。生成後`run_leadintro_gate`(Tension項目セットLeakage判定、FAMILY_Y_LEAK_JUDGE=gpt-6-luna)。
- 英語版は日本語紹介文を含む記事全体の英訳(`stage_translate` er121_family_y_runner_01.py:405。Adv=忠実英訳、StdはAdvから)。**紹介文のEnglishはJA紹介文の翻訳**。
- 承認済み仕様: Voice説明文(CURRENT_SPEC.md:3200-3207)は別件。人物紹介自体の方式は委任_28(`generate_intros`移植元)・YL-C01(5パート契約、紹介行+本人の語り)。人物紹介の一般化方針は未決(本Trialが初)。
- 原因(run_02): Theme Package `sheets.voice_1.role_ja`=「婿養子になって、妻の家の苗字になった**父親**」が人物ブロックに入り、現行JA紹介文も「…名乗る**父親**」と属性を主名詞にした。英訳が「The first speaker is a father.」を独立した第1文にし、「息子の結婚を語る父親」と誤読された。事実としては3人の息子の父だが、本テーマ(妻の姓を選んだ経験)では立場を表さない。

## 2. Trial設計
- Prompt差分(Trial専用コピー。`er121_family_y_intro_trial_01.py`が`persona_intro_01.txt`の`【書き方】`直後へ1項目を足す。ファイル自体は不変):
  - 原則bullet(ユーザー候補原則を逐語趣旨で): テーマに直接関係する立場・経験を優先 / 親・職業・年齢等の属性は立場理解に重要なときだけ / 役割名の機械的転記禁止 / 属性を削るだけで終わらせない / 根拠のない設定を足さない。
  - variant A=原則のみ / B=原則+人物ブロックに`contact_point_ja`(話題との関わり)行を追加 / C=B+「欄にない時期・きっかけを足さない」 / D=C+「結婚して・結婚を機に等の時期表現を使わない」(Cが守られなかったため強化)。
- 生成: gpt-6.1-sol/high(Production同一route・最新上位)。A/B各2sample、C 2sample、D 1sample(費用管理のため)。
- 検査: Production `check_intro` を各案に適用。最終推奨案にはProduction `run_leadintro_gate` も適用。
- 英語化preview: 同モデルで紹介行だけをAdv(忠実)/Std(A2)の文体で英語化(既存V2/V3の英訳行を文体見本に渡す)。記事へは未適用。
- 評価観点: 立場の明確さ / 誤解の解消 / Persona・発言・主張との整合 / 創作なし(事実性) / 他Voice紹介の自然さ / 本文(Voice発言・Lead・Closing)非変更。

## 3. 範囲外(厳守)
本文のVoice発言・Lead・Closingは変更しない。Productionの`persona_intro_01.txt`・`check_intro`・閾値は不変更。run_02の正式データ(text/KP/音声/pages)へ一切書かない。
