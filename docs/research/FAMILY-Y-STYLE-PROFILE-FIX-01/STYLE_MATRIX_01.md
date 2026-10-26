# STYLE_MATRIX_01 — Family Y 部位別 正Style一覧(Std/Adv)

管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01 / read-only(API 0)。機械可読版=`style_matrix_01.json`(同内容)。
照合元: (a)共通仕様=`er019_family_x_style_profile_01.py:187-189,276-283`(`DEFAULT_NEW_RUN_PROFILE=fx_20261017`の定義)・`CURRENT_SPEC.md:1268`(S3正式採用)・`CURRENT_SPEC.md:1699-1706`(Family別Status表) (b)Y固有承認=`docs/pm/delegation_log/*FAMILY-Y*USER*.md`(Style/PD06/個性/Persona/主観のGrep) (c)Y設計=`docs/research/FAMILY-Y-VOICES-DESIGN-01/DESIGN_PROPOSAL_02.md:109,242`・`FAMILY-Y-PRODUCTION-LAUNCH-01/DESIGN_01.md:84`。
判定の語: **承認済み共通**=共通仕様の承認(ユーザー正式承認)でYにも適用(28-1運用7) / **Y固有承認**=Y専用にユーザーが承認したStyle(該当0件) / **記録なし**=承認も除外も記録なし。

## 1. 結論
1. 正profile=**`fx_20261017`**(PD06/S3/E1/K2/P8-KP/P7の6 role)。Y固有に承認されたStyle・除外は**0件**(Grep: Y関連USER原文のStyle言及は一般規定のみ。`PD06`をYについて名指しした承認文は無いが、設計A19/T10[Voice別Styleを設けない]・DEV Trial[`er110:40`]・台帳YL-A01=APPLYが一致して継承)。
2. Y固有承認は**Voice割当(Puck/Zephyr/Schedar)・Comment 2削除(Adv)・Chunk・Closing Gate**で、いずれもStyle文字列の承認ではない(`CURRENT_SPEC.md:3082-3105`)。よってY固有Styleによる例外は存在せず、優先すべきY固有Style仕様も無い。
3. Voice 1〜3本文は現行コードでもDEV Trialでも**他の本文segmentと同一のrole(`FULL_STORY`)**で解決される(`er121_family_y_audio_01.py:590-605`のAdv本文loop[`style_prefix_override=_role_style("FULL_STORY")`]、同`:703-726`のStd側[`_role_style_slower("FULL_STORY")`])。人物別Style prefixは設計にもコードにも存在しない(A19「Voice別Styleは設けない」)。人物の個性は**Persona/一人称の原稿**と**Voice名の割当**が担う(`DESIGN_01.md`4-5「Voiceの個性保持[一人称・口調・迷い]」)。
4. 確定できない1点=Voice 1〜3本文へのPD06適用が個性(平板化=S9)を損なわないか。承認記録は「適用する」(A19/T10)で一致するが、**S9の試聴評価結果は記録なし**(`TRIAL_01/PHASE3_PLAN_01.md:31`が評価項目として宣言、`AUDIO_QA_01.md:86`は「ユーザー試聴の対象」とするのみ。結果を記す文書0件)。→ 7節「判断候補V」。

## 2. 定義(原文確認)
| 項目 | 内容(`er019_family_x_style_profile_01.py`) | 適用role(`ROLE_LEVELS` :208-) |
|---|---|---|
| PD06 (`FULL_STORY`) | 「Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, like a favorite morning radio host, while keeping the news clear and credible.」(:108-111、177字)。Stdは逐語(減速指示を連結せず)+生成後6%減速(`std_append_slower_instruction=False`) | Std/Adv |
| 基底(default, 現行Y) | 本文=「calm, steady news narration with natural emphasis at key points and turns; not dramatic.」(+Stdは「Speak at a slightly slower, relaxed pace…」連結) | — |
| S3 (`SUPPORT_JA`) | 「温かみと親しみのあるニュースナレーターとして、落ち着いた、明瞭な声で伝えてください。…」(:152-、199字、2026-10-17正式承認) | Stdのみ(対象=preview・comment_1〜4。japanese_title・KP日本語意味は対象外 :199-204) |
| E1 (`PREVIEW`) | 「calm, composed news anchor; steady and unhurried, clear and natural.」(:96、68字) | Advのみ(Previewだけ。Commentは対象外) |
| K2 (`KP_EN`) | 「Say the phrase as one single, smoothly connected chunk of meaning…」(:126-、332字、Master Audio Store 2段key) | Std/Adv |
| P8-KP (`KP_JA_MEANING`) | 「落ち着いたニュースキャスターのように、明瞭で安定した声で読み上げてください。…」(:138-141、93字) | Stdのみ |
| P7 (`KP_EXPLANATION_EN`) | 「Speak clearly at a slightly relaxed, natural pace. Keep a steady rhythm…」(:117-120、136字) | Advのみ |
(全6roleのsha256・文字数は`fx_20261017`のoverrides実測=FULL_STORY 3a680861…/177、PREVIEW 8862317f…/68、KP_EXPLANATION_EN 05180006…/136、KP_EN 9d905cfe…/332、KP_JA_MEANING b12c8721…/93、SUPPORT_JA 060c08fd…/199)

## 3. Advanced(b1b)の部位別一覧(再生成要否は`REGEN_PLAN_01.md`)
| # | 部位(Y segment) | Voice | 適用する項目 | 適用しない項目 | 根拠 | 判定 |
|---|---|---|---|---|---|---|
| A1 | Welcome/Intro/番号/KP intro/full_story_intro/Outro(shell固定) | Charon | なし(既存Master/共有資産) | 全て | `INVENTORY_X_Z_SPEC_01.md`「shell固定英語」未override、`er121`でshared narration再利用 | 承認済み共通(非対象) |
| A2 | topic_intro | Charon | なし(基底`brief, clear, engaging news topic introduction…`) | PD06等 | `fx_20261017`はTOPIC_INTRO未override(`overrides`にroleなし) | 承認済み共通(非対象) |
| A3 | preview | Charon | **E1** | 基底`calm, conversational` | `ROLE_LEVELS[PREVIEW]=(b1b)`、DESIGN_01.md:84、YL-A01 | 承認済み共通 |
| A4 | KP英語 ×3(+repeat同一音源) | Aoede | **K2** | MINIMAL | `ROLE_LEVELS[KP_EN]=(a2,b1b)` | 承認済み共通 |
| A5 | KP解説 ×3 | Aoede | **P7** | `clear, precise, at a measured pace…` | `ROLE_LEVELS[KP_EXPLANATION_EN]=(b1b)` | 承認済み共通 |
| A6 | comment_1 / comment_3 | Charon | なし(基底`calm, conversational`) | E1(Previewのみ対象) | `ROLE_SEGMENTS[PREVIEW]=("preview",)`。Zの`E2_UPBEAT`はZ固有(`er063_family_z_audio_01.py:266-283`)でYに適用する承認なし | 承認済み共通(非対象) |
| A7 | comment_2 | — | — | — | 2026-10-26ユーザー決定でAdvから削除(`CURRENT_SPEC.md:3089-3091`) | Y固有承認(構成) |
| A8 | y_lead(リード) | Aoede(narrator) | **PD06** | 基底 | A19/T10、DEV Trial、YL-A01 | 承認済み共通 |
| A9 | y_intro_1/2/3(人物紹介リード) | Aoede(narrator) | **PD06** | 基底 | 同上(narrator役はFull Story role) | 承認済み共通 |
| A10 | y_voice_1(Voice 1) | Puck | **PD06**(判断候補V) | — | A19「Voice別Styleは設けない」、Voice割当は`CURRENT_SPEC.md:3098-3105` | 承認済み共通(S9未確認) |
| A11 | y_voice_2(Voice 2) | Zephyr | **PD06**(判断候補V) | — | 同上 | 同上 |
| A12 | y_voice_3(Voice 3) | Schedar | **PD06**(判断候補V) | — | 同上 | 同上 |
| A13 | y_closing(Tension+Closing) | Aoede(narrator) | **PD06** | 基底 | 同上 | 承認済み共通 |

## 4. Standard(a2)の部位別一覧
| # | 部位 | Voice | 適用する項目 | 適用しない項目 | 根拠 | 判定 |
|---|---|---|---|---|---|---|
| S1 | shell固定 | Charon/Aoede(既存) | なし | 全て | A1と同じ | 承認済み共通(非対象) |
| S2 | topic_intro | Aoede | なし(基底) | PD06等 | A2と同じ | 承認済み共通(非対象) |
| S3 | japanese_title | Aoede | なし(J3基底。2026-09-28承認) | S3(対象外と明記) | `er019_family_x_style_profile_01.py:203-204`(対象外: japanese_title・KP日本語意味)、`INVENTORY_X_Z_SPEC_01.md:56` | 承認済み共通(非対象) |
| S4 | preview(日本語) | Aoede | **S3** | 基底 | `ROLE_SEGMENTS[SUPPORT_JA]`に`preview`、`CURRENT_SPEC.md:1268` | 承認済み共通 |
| S5 | comment_1/2/3(日本語) | Aoede | **S3** | 基底 | 同上(comment_2はStdでは残る) | 承認済み共通 |
| S6 | y_lead / y_intro_1〜3 / y_closing | Aoede | **PD06**(逐語、減速指示は連結しない)+生成後**6%減速** | 基底+「slower」連結 | A19/T10、`std_append_slower_instruction=False` | 承認済み共通 |
| S7 | y_voice_1/2/3 | Puck/Zephyr/Schedar | **PD06**+6%減速(判断候補V) | — | A10〜A12と同じ | 承認済み共通(S9未確認) |
| S8 | KP英語 ×3 | Aoede | **K2** | MINIMAL | `ROLE_LEVELS[KP_EN]` | 承認済み共通 |
| S9 | KP日本語意味 ×3 | Aoede | **P8-KP** | 基底J3 | `ROLE_LEVELS[KP_JA_MEANING]=(a2)` | 承認済み共通 |
| S10 | In One Line | — | — | — | Yは生成しない(`DESIGN_01.md`4-5) | Y固有(構成) |

chunk: 段落分割された本文segmentはchunkごとに親と同じroleのStyleで生成し、profile記録はchunkごとに付ける(`er121_family_y_audio_01.py:488-538`)。親には写さない。現行の実記事は全segment単一段落(OPEN-527)でchunk発火なし。

## 5. 現行(default)との差分サマリ
- Adv: 変わる部位=preview(E1)/KP英語3(K2)/KP解説3(P7)/本文8(PD06)。変わらない=topic_intro/comment_1/comment_3/shell。
- Std: 変わる部位=preview+comment_1〜3(S3)/KP英語3(K2)/KP日本語意味3(P8-KP)/本文8(PD06・減速指示連結なし)。変わらない=topic_intro/japanese_title/shell。

## 6. Voice 1〜3 本文の扱い(根拠)
事実:
1. 現行Yコードも設計も、Voice 1〜3本文とnarratorを同じ`FULL_STORY`で解決する。人物別Style文字列は存在しない(上記3、`DESIGN_PROPOSAL_02.md:109`「Voice別Styleは設けない」、同:347「PD06が人物を『語り手』化・平板化させる可能性があり(S9)、Trialで…評価する。…Style変更(PD06除外等)が必要な場合は、結果を添えて再判断を求める」)。
2. 設計はPD06の影響を「Trial評価で確認する条件付き」とした。S9の評価結果を記録した文書は0件(Grep `S9|平板`: `TRIAL_01/{AUDIO_QA_01:86,PHASE3_PLAN_01:31,EN_COMPARISON_01:30}`が宣言/観察のみ。EN_COMPARISON_01は英訳の平板化で音声Styleの話ではない)。
3. ユーザーが聴いたY音声は2種: DEV Trial(`fx_20261017`=PD06をVoice 1〜3にも適用: `AUDIO_QA_01.md:24`)と、Production E-1(`default`)。後者の3 segment(a2 preview/b1b y_voice_1/a2 y_voice_1)は「問題ありません」(`…E1_APPROVAL.md`)。PD06への個別の否定評価の記録は0件。
4. ユーザー指示(`…USER_09.md:70`)「過剰な演技やニュースナレーター化は避ける」。現行default本文Styleは文言が`news narration`、PD06は`warmth…like a favorite morning radio host…keeping the news clear and credible`。どちらも語り手型で、人物別の演技指示ではない。
5. 個性の担い手: Persona/一人称の原稿(`DESIGN_01.md`4-5)、Voice名の割当(Puck=Voice 1、Zephyr=Voice 2、Schedar=Voice 3)。Style文字列は感情の起伏・口調を人物別に制御しない設計。
PD06と両立/しない項目(事実の範囲): 両立=一人称原稿・立場の違い・Voice名(PD06はdelivery指示で内容を拘束しない)。**未確認**=「迷い・ためらい・感情の起伏」の抑揚が`calm, steady and reassuring`で平板化しないか(耳でしか確認できない)。
所見: A19/T10に従い、**承認済みの既定=Voice本文にもPD06**。未承認の人物別Styleを追加すること、または一部をdefaultに残すことは新規Style(Y固有例外)で、ユーザー承認と記録(28-2運用6)が要る。

## 7. 判断候補(承認記録だけでは決められない項目)
**判断候補V: Voice 1〜3本文(Std/Adv 6 segment)にPD06を適用してよいか。** 区分(27-3)案=**B(承認範囲内で自己解決)または新規の例外ならD**。
- 根拠: 適用する側=A19/T10・DEV Trial・YL-A01・28-1運用7・USER_09:64「既存のStyleを継承」「未承認のStyle変更を追加しない」(:66)。懸念側=ユーザー§1B「PD06を一律適用して個性を失わせない」。S9評価は記録なし。
- 選択肢:
  - **V1(推奨)**: 承認済み既定(PD06をnarrator・Voice 1〜3とも)で再生成し、旧版`_02`(default)と新版`_03`を**並べて**ユーザー再試聴に提出。個性が損なわれたと判断されたら、その時点でY固有例外(Voice本文のみdefault維持、または人物別Styleのバリエーション)をTrial→ユーザー承認へ。品質影響=現状のdefaultより「温かみ・直接語りかけ」が増える方向。平板化リスクは未測定(試聴で確認)。費用影響=差戻し時のVoice本文6 segment再生成のみ約8円(REGEN_PLAN §5)。速度=最速。
  - V2: Voice 1〜3本文のみdefault維持(narrator・他roleはfx)。承認済みA19と矛盾する**新規のY固有例外**。同一記事内でnarratorとVoiceのStyle系統が混在(PD06のnarrator→default[news narration]のVoice)。承認が先に必要で、再生成は6 segment減(約-8円)だが、Gate設計(例外の記録・drift test)を追加で要する。
  - V3: 人物別Style(新Prompt)をTrial。未承認の新Style・新Promptで本委任の範囲外。
- 推奨=**V1**(理由: 承認済み仕様に従う不具合是正であり、ユーザー指示「承認済み仕様の配線漏れは自律的に是正」[§1B]に合致。個性毀損の懸念は再試聴で検証でき、差戻しコストは小さい)。ユーザー事前確認は、費用・速度の損失(待機)が品質向上より大きいため推奨しない(最終判断はFable)。
