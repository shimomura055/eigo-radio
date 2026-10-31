# COMPARISON_05 KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_05(2026-10-31) 現行N5(cap7)とA案(E2網羅抽出+A10区間分散+cap10)の最終Key Phrase比較

原文=`docs/pm/delegation_log/2026-10-31_KP-N5-TRIAL-05_FINAL_KP_COMPARISON_USER.md`。事前登録=`TRIAL_PLAN_05.md`。Trial・未承認・Production変更0・配線なし。**判定はせず、ユーザーが具体的なPhraseを見て採否を決めるための材料。** 使用モデル=GEN5 `gpt-6-luna`・VER5 `gemini-3.8-flash`・CHK5 `gpt-6.1-sol`(いずれもProduction既定=最新系。Prompt・閾値は正式採用済みのまま無変更)。

## 1. 記事別比較表(学習者が実際に見る「N5一般化後のKey Phrase」)

**凡例**
- 対象=Trialで実際に抽出・選定を回した**5セル**(委任文の「24セル」は想定違い): untidi_a2(Family X Std)・untidi_b1b(X Adv)・melos_a2(Z Std)・moon_b1b(X Adv)・surname_b1b(Y Adv)。全セル同一記事・同一レベル・同一本文(fixture `n5_trial_replay_fixture_01.json` の text)。
- **現行N5 cap7**の出所: 公開済みProduction出力(untidiness run_fx4_01等、生成2026-10-27〜29)はN5配線(2026-10-30/31)前でN5一般形を含まないため比較に使えない。よって**Trial03のN5正式出力**(同fixture `trial_items`、GEN5→VER5→CHK5通過後。配線時にProductionの記録応答replayで19ケースexact一致を確認済み)を使用。N5配線後のProduction実run(同一本文、3セル)は付録Bに併記。**現行N5の項目数はcap7に満たないことがある**(moon 4件・surname 6件。7件に届かない理由はTrial03時点のSEL/QA結果で、本Trialでは未調査)。
- **A案cap10**: 各repのE2プール(SELラベル保存済み)に `pick_A10(cap=10)` を再計算(決定論、API 0)。ここに表示するのは**代表rep**(同セル内の各repのcap10集合との平均Jaccardが最大のrep=medoid、同点は若い番号。事前登録)。repによる入替は§4・付録A。display_form・日本語の意味は**すべて正式N5(GEN5→VER5→CHK5+CMU・5語検査)の実出力**で、手作業の一般形は無い。現行N5と共通のspanはTrial03の出力をそのまま再利用、A案だけの候補は今回GEN5〜CHK5を実行(`ev05/gen_cache_05_*.json`)。
- **区分**: 共通=現行N5とspan/display_formが一致・包含、追加=現行N5に無い(A案で増える)、脱落=現行N5にあるがA案cap10に入らない、QA脱落=A案cap10候補だが下流で落ちた(段・理由を併記)。
- **価値(暫定)**=担当者(Sonnet)の主観評価(高=非自明な意味・用法の汎用表現で一般形が自然かつ正確 / 中=有用だが基礎的・場面限定・一般形が弱い / 低=基礎語の自由な組合せ・一般形が過度に一般的・記事固有)。**ユーザー判断の材料であり判定ではない。** `A→B`表記は現行N5側とA案側で同一spanのdisplay_formが異なる場合。

### untidi_a2 — Family X untidiness_family_resource(Std)(E2 11rep、代表rep=9)

| 区分 | 現行N5 cap7: source_span → display_form | 日本語の意味 | A案 cap10: source_span → display_form | 日本語の意味 | 価値(暫定) | cap10入り頻度 / SEL難易度・型 / CHK5 relation |
|---|---|---|---|---|---|---|
| 共通 | `take points away from` → `take something away from` | 〜から点数などを差し引く、取り去る | `take points away from` → `take something away from` | 〜から点数などを差し引く、取り去る | 中 | 10/11rep、upper_intermediate、phrasal_verb、GLOSS_MISMATCH |
| 共通 | `make life work` → `make something work` | 物事をうまく機能させる | `make life work` → `make something work` | 物事をうまく機能させる | 中 | 4/11rep、upper_intermediate、collocation、SAME |
| 共通 | `hear it out` → `hear someone out` | 相手の言い分を最後まで聞く | `hear it out` → `hear someone out` | 相手の言い分を最後まで聞く | 高 | 11/11rep、upper_intermediate、phrasal_verb、SAME |
| 追加 | — | — | `put it away` → `put something away` | 物を所定の場所にしまう | 高 | 9/11rep、easy、phrasal_verb、SAME |
| 追加 | — | — | `speak for it` → `speak for` | 人を代表して意見を述べる | 中 | 8/11rep、upper_intermediate、phrasal_verb、FRAME_SHIFT |
| 追加 | — | — | `comes from` → `come from` | 〜に由来する、〜から生じる | 低 | 7/11rep、easy、phrasal_verb、SAME |
| 追加 | — | — | `something in the way` → `something in the way` | 邪魔になるもの、妨げ | 中 | 5/11rep、upper_intermediate、fixed_phrase、 |
| 追加 | — | — | `gets heated` → `get heated` | （会話などが）感情的で激しくなる | 高 | 9/11rep、upper_intermediate、collocation、SAME |
| 追加 | — | — | `look at clutter` → `look at` | 〜を見る、検討する | 低 | 6/11rep、easy、phrasal_verb、SAME |
| 共通 | `turn the talk into` → `turn something into` | 〜を別のものへと変える | `turn the talk into` → `turn something into` | 〜を別のものへと変える | 中 | 10/11rep、upper_intermediate、phrasal_verb、SAME |
| 脱落(A案cap10に入らない) | `relied on` → `rely on` | 頼りにする | — | — | 中 | 現行N5のみ(upper_intermediate) |
| 脱落(A案cap10に入らない) | `in session` → `in session` | 裁判や会議が開催中である | — | — | 中 | 現行N5のみ(easy) |
| 脱落(A案cap10に入らない) | `Not so fast` → `not so fast` | 急ぐな、まだそう決めるな | — | — | 高 | 現行N5のみ(easy) |

### untidi_b1b — Family X untidiness_family_resource(Adv)(E2 13rep、代表rep=1)

| 区分 | 現行N5 cap7: source_span → display_form | 日本語の意味 | A案 cap10: source_span → display_form | 日本語の意味 | 価値(暫定) | cap10入り頻度 / SEL難易度・型 / CHK5 relation |
|---|---|---|---|---|---|---|
| 共通 | `Now in Session` → `in session` | 会議や裁判などが開会中である | `Now in Session` → `in session` | 会議や裁判などが開会中である | 中 | 12/13rep、upper_intermediate、fixed_phrase、SAME |
| 共通 | `turn into an interrogation` → `turn into` | 別の状態や性質へと変わる | `turn into an interrogation` → `turn into` | 別の状態や性質へと変わる | 中 | 13/13rep、upper_intermediate、phrasal_verb、SAME |
| 共通 | `hear it out` → `hear someone out` | 相手の話を最後まで聞く | `hear it out` → `hear someone out` | 相手の話を最後まで聞く | 高 | 13/13rep、upper_intermediate、phrasal_verb、SAME |
| 追加 | — | — | `speaking for` → `speak for` | ある立場を代表して発言する | 中 | 9/13rep、upper_intermediate、phrasal_verb、SAME |
| 追加 | — | — | `put away` → `put something away` | 物を片づけて収納する | 高 | 12/13rep、easy、phrasal_verb、FRAME_SHIFT |
| 追加 | — | — | `something in the way` → `something in the way` | 邪魔になるもの | 中 | 12/13rep、upper_intermediate、fixed_phrase、SAME |
| 共通 | `relied on` → `rely on` | 人や物を頼りにする | `relied on` → `rely on` | 人や物を頼りにする | 中 | 12/13rep、upper_intermediate、phrasal_verb、SAME |
| 共通 | `taking points away` → `take points away` | 〜の価値や良さを損なう、減点する | `end up taking points away` → `end up taking points away` | 評価を落とす、減点する | 中→低 | 6/13rep、upper_intermediate、phrasal_verb、 |
| 追加 | — | — | `leave it out` → `leave something out` | 何かを外に出したままにしておく | 中 | 9/13rep、upper_intermediate、phrasal_verb、SAME |
| 追加 | — | — | `in sight` → `in sight` | 見えるところにある | 中 | 12/13rep、easy、fixed_phrase、SAME |
| 脱落(A案cap10に入らない) | `gets heated` → `get heated` | 感情的になり、議論などが白熱する | — | — | 高 | 現行N5のみ(upper_intermediate) |
| 脱落(A案cap10に入らない) | `taking its job quite seriously` → `take something seriously` | 何かを重要なものとして真剣に扱う | — | — | 中 | 現行N5のみ(easy) |

### melos_a2 — Family Z 走れメロス(Std)(E2 2rep、代表rep=1)

| 区分 | 現行N5 cap7: source_span → display_form | 日本語の意味 | A案 cap10: source_span → display_form | 日本語の意味 | 価値(暫定) | cap10入り頻度 / SEL難易度・型 / CHK5 relation |
|---|---|---|---|---|---|---|
| 共通 | `pulled him under` → `pull someone under` | 水面下へ引き込む | `pulled him under` → `pull someone under` | 水面下へ引き込む | 中 | 2/2rep、upper_intermediate、phrasal_verb、SAME |
| 共通 | `lost my trust in you` → `lose one's trust in` | 信頼を失う | `lost my trust in you` → `lose one's trust in` | 信頼を失う | 中 | 2/2rep、upper_intermediate、collocation、SAME |
| 共通 | `win such trust` → `win trust` | 信頼を獲得する | `win such trust` → `win trust` | 信頼を獲得する | 中 | 2/2rep、upper_intermediate、collocation、MODIFIER_DROPPED_OK |
| 共通 | `in your place` → `in someone's place` | 身代わりの立場で | `in your place` → `in someone's place` | 身代わりの立場で | 高 | 2/2rep、upper_intermediate、fixed_phrase、SAME |
| 追加 | — | — | `come back` → `come back` | 戻ってくる | 低 | 2/2rep、easy、phrasal_verb、SAME |
| 追加 | — | — | `left for the city` → `leave for` | 〜へ向けて出発する | 中 | 1/2rep、upper_intermediate、phrasal_verb、SAME |
| 共通 | `lose his life instead` → `lose one's life` | 命を失う、死ぬ | `lose his life` → `lose one's life` | 命を失う | 中 | 2/2rep、upper_intermediate、idiom、SAME |
| 追加 | — | — | `stood up` → `stand up` | 立ち上がる | 低 | 2/2rep、easy、phrasal_verb、SAME |
| 追加 | — | — | `give them a chance` → `give someone a chance` | 人に機会を与える | 中 | 2/2rep、easy、collocation、SAME |
| 追加 | — | — | `walking stick` → `walking stick` | 歩行を助ける杖 | 低 | 1/2rep、easy、compound_noun、SAME |
| 脱落(A案cap10に入らない) | `rose above everyone’s voices` → `rise above something` | より大きく、または目立って聞こえる | — | — | 中 | 現行N5のみ(upper_intermediate) |
| 脱落(A案cap10に入らない) | `kept his eyes on them` → `keep one's eye on` | 視線を注ぎ続ける | — | — | 中 | 現行N5のみ(easy) |

### moon_b1b — Family X moon_shrinking(Adv)(E2 2rep、代表rep=1)

| 区分 | 現行N5 cap7: source_span → display_form | 日本語の意味 | A案 cap10: source_span → display_form | 日本語の意味 | 価値(暫定) | cap10入り頻度 / SEL難易度・型 / CHK5 relation |
|---|---|---|---|---|---|---|
| 追加 | — | — | `keeps heat from escaping` → `keep something from escaping` | 何かが逃げるのを防ぐ | 中 | 1/2rep、upper_intermediate、phrasal_verb、FRAME_SHIFT |
| 追加 | — | — | `offer clues to` → `offer clues to` | 〜への手掛かりを提供する | 中 | 2/2rep、upper_intermediate、collocation、SAME |
| 追加 | — | — | `a record of` → `a record of` | 〜の記録や痕跡である | 中 | 1/2rep、upper_intermediate、collocation、SAME |
| 共通 | `work out how much` → `work out how much` | 数量や程度を計算して明らかにする | `work out` → `work out` | 考えたり計算したりして答えを導く | 中 | 2/2rep、upper_intermediate、phrasal_verb、SAME |
| 追加 | — | — | `On the other hand` → `on the other hand` | 対比する別の側面を示す | 中 | 1/2rep、upper_intermediate、fixed_phrase、SAME |
| 追加 | — | — | `put on` → `put something on` | 何かを身につける | 低 | 2/2rep、easy、phrasal_verb、SAME |
| 追加 | — | — | `Taking the Moon's measurements` → `take measurements` | 測定を行う | 中 | 1/2rep、upper_intermediate、collocation、MODIFIER_DROPPED_OK |
| 共通 | `way off` → `way off` | 正確さや基準から大きく外れている | `way off` → `way off` | 正確さや基準から大きく外れている | 中 | 2/2rep、easy、fixed_phrase、SAME |
| 追加 | — | — | `up close` → `up close` | 近くで見ると | 中 | 2/2rep、easy、fixed_phrase、SAME |
| 追加 | — | — | `hold on a moment` → `hold on` | 少し待つよう求める | 低 | 2/2rep、easy、fixed_phrase、MODIFIER_DROPPED_OK |
| 脱落(A案cap10に入らない) | `shoving match` → `shoving match` | 強く押し合う激しい争い | — | — | 中 | 現行N5のみ(upper_intermediate) |
| 脱落(A案cap10に入らない) | `keeps heat in` → `keep something in` | 何かを内部に保つ | — | — | 低 | 現行N5のみ(easy) |

### surname_b1b — Family Y surname_choice(Adv)(E2 2rep、代表rep=1)

| 区分 | 現行N5 cap7: source_span → display_form | 日本語の意味 | A案 cap10: source_span → display_form | 日本語の意味 | 価値(暫定) | cap10入り頻度 / SEL難易度・型 / CHK5 relation |
|---|---|---|---|---|---|---|
| 共通 | `taking offense` → `take offense` | 気分を害する、腹を立てる | `taking offense` → `take offense` | 気分を害する、腹を立てる | 高 | 2/2rep、upper_intermediate、collocation、SAME |
| 共通 | `at ease` → `at ease` | 緊張や不安がなく、落ち着いている | `at ease` → `at ease` | 緊張や不安がなく、落ち着いている | 中 | 2/2rep、upper_intermediate、fixed_phrase、SAME |
| 追加 | — | — | `let go of` → `let go of` | 人への執着を手放し、自由にする | 高 | 2/2rep、upper_intermediate、phrasal_verb、SAME |
| 共通 | `hold my son back` → `hold someone back` | 進歩や行動を妨げる | `hold my son back` → `hold someone back` | 進歩や行動を妨げる | 高 | 2/2rep、upper_intermediate、phrasal_verb、SAME |
| 共通 | `giving something up` → `give something up` | 断念する、放棄する | `giving something up` → `give something up` | 断念する、放棄する | 中 | 2/2rep、easy、phrasal_verb、SAME |
| 追加 | — | — | `care about different things` → `care about` | 何かに関心を持ち、大切に思う | 低 | 2/2rep、easy、phrasal_verb、SAME |
| QA脱落(追加候補) | — | — | `get much time to myself` → (n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'myself'の語形違いでない) | — | — | 1/2rep、upper_intermediate、collocation、 |
| 追加 | — | — | `moving away` → `move away` | 離れていく、距離ができる | 低 | 1/2rep、easy、phrasal_verb、SAME |
| QA脱落(追加候補) | — | — | `decide for themselves` → (n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'themselves'の語形違いでない) | — | — | 1/2rep、upper_intermediate、fixed_phrase、 |
| 追加 | — | — | `had no problem at all` → `have no problem` | 問題や抵抗を感じない | 低 | 1/2rep、easy、collocation、MODIFIER_DROPPED_OK |
| 脱落(A案cap10に入らない) | `can’t help thinking` → `can't help thinking` | 考えることを止められない | — | — | 高 | 現行N5のみ(upper_intermediate) |
| 脱落(A案cap10に入らない) | `only natural` → `only natural` | 当然で、もっともだと思われる | — | — | 中 | 現行N5のみ(upper_intermediate) |

### セル別の区分集計(代表rep、上表の要約)

| セル | 現行N5件数 | A案cap10の内訳(代表rep) | 現行のみ(脱落) | 価値(暫定) 高/中/低: 現行 → A案 |
|---|---|---|---|---|
| untidi_a2 (X Std) | 7 | 共通4 / 追加6 / QA脱落0 | 3 | 2/5/0 → 3/5/2 |
| untidi_b1b (X Adv) | 7 | 共通5 / 追加5 / QA脱落0 | 2 | 2/5/0 → 2/7/1 |
| melos_a2 (Z Std) | 7 | 共通5 / 追加5 / QA脱落0 | 2 | 1/6/0 → 1/6/3 |
| moon_b1b (X Adv) | 4 | 共通2 / 追加8 / QA脱落0 | 2 | 0/3/1 → 0/8/2 |
| surname_b1b (Y Adv) | 6 | 共通4 / 追加4 / QA脱落2 | 2 | 3/3/0 → 3/2/3(+QA脱落2) |

## 2. 学習価値の比較(網羅性・汎用性・自然さ・難易度・重複・意味の正確性。件数増=品質向上とは判定しない)

数値は `ev05/stats_05.json`・`comparison_05.json`(全repの再計算)。「価値」は担当者の暫定評価で主観を含む。

1. **網羅性(入替であって単純な増分ではない)**: 同一rep内でA0(現行方式cap7、span単位)とA10(cap10)を比べると、A案に残る現行選定は a2 3.6/6.9件・b1b 3.8/6.9・melos 4.0/6.5・moon 2.0/5.0・surname 5.5/5.5件。**現行から消える選定は平均 3.3/3.2/2.5/3.0/0.0件**、A案だけの選定は 6.4/6.2/6.0/8.0/4.5件。枠が3件増える以上に入替が起きる(A10は記事を7区間に分け各区間の最良を採るため)。ユーザーの目標表現(`put away`+`in the way`)は現行0/24repに対しA案21/24rep(§4)。
2. **汎用性・価値**: 全repの平均件数(1記事あたり、高/中/低)は A案cap10 = a2 3.3/4.6/2.2、b1b 2.1/6.9/1.1、melos 1.0/5.5/3.5、moon 0.0/7.5/2.5、surname 3.0/3.0/2.5(+QA脱落1.5) に対し、現行方式A0(cap7) = a2 2.3/4.6/0.1、b1b 1.9/4.5/0.5、melos 0.5/5.5/0.5、moon 0.5/4.5/0.0、surname 3.0/2.5/0.0。**高評価はほぼ増えず(平均+0.2件/記事。a2 +1.0 は `put something away`・`get heated`)、増えた3〜4件の大半は中(+1.2件)と低(+2.1件)**。低評価の追加は基礎的な句動詞・基礎語の組合せ(`come from`・`look at`・`ask for`・`come back`・`stand up`・`put something on`・`hold on`・`care about`・`move away`・`have no problem`・`walking stick`)。
3. **自然さ(一般形・日本語)**: 追加候補のdisplay_formは概ね自然で、日本語の意味も正しいと読める(union 88spanのうちGEN5を通過した85件でCHK5 relationがSAME 74件=87%、FRAME_SHIFTはVER5/CHK5が修正採用、MODIFIER_DROPPED_OKは修飾語を落とした一般形)。問題の例: ①`end up taking points away`(VER5がrevert。5語で一般化されず、現行N5の`take points away`より悪い。b1bで6/13rep) ②`miss dose`(`missed doses`から。文法的に不自然。b1b 2/13rep) ③`something in the way`(VER5が`in the way`ではなく名詞付き形へrevert。見出し形ではない) ④`without getting too close`(日本語の意味が`without`を反映しない。surname) ⑤`look at`(`look at clutter`から。基礎語に潰れ、日本語『〜を見る、検討する』で学習項目として弱い)。
4. **難易度(SEL判定のeasy比率、cap10 vs cap7のrep平均)**: a2 39% vs 35%、b1b 15% vs 27%(A案が下がる唯一のセル)、melos 45% vs 31%、moon 35% vs 20%、surname 25% vs 18%。**b1b以外はA案の方が易しい表現の比率が高い**(A10がeasyな句動詞を昇格する設計のため)。
5. **重複**: 同一rep内でdisplay_formが重複する例は全30repで0件(span包含dedupeが効く。`in the way`と`something in the way`が同一repに併存する例も0)。意味が近い組(例: `put something away`と`leave something out`)は定量していない。
6. **意味の正確性**: 追加候補で日本語の意味が明確に誤るのは `without getting too close` の1件のみ(担当者が本文を読んで確認)。`oneself`再帰形を含む `decide for themselves`・`get much time to myself`・`time to myself`(surname)は正式GEN5が「lemma 'oneself'が本文の語形違いでない」で組立失敗し**QA脱落**(これはA案固有でなく正式GEN5の制約で、現行N5でも同じ候補が選ばれれば落ちる)。`take points away from`のGLOSS_MISMATCHはTrial03の現行出力側(gloss修正済み)で、A案と共通。

## 3. N5(現行cap7・A案cap10)から外れた表現の評価(付録C、display_formはGEN5〜CHK5の実出力)

- **学習価値が高いのに両方式で選ばれにくい表現**: ①`gets heated`→`get heated`(b1b: SEL keep 13/13repなのにA案cap10は0/13rep。**現行N5のTrial03出力には入っているので、A案は現行の良い選定を1件消す**。a2ではA案9/11repで入る=セルにより逆) ②`Not so fast`(a2: A案cap10は1/11rep、現行にはある) ③`decide for themselves`(surname: A案で選ばれてもGEN5組立失敗)。
- **談話標識・会話の固定表現はどちらの方式も選ばない傾向**: `In other words`(b1b 13/13 keep・cap10 0)・`No wonder`・`In a way`・`For now`・`too soon to say`・`again and again`・`For once`・`on the job`・`in sight`(a2)等は毎回プールでkeepされるのにcap10に入らない(A10の区間分散とR1d順でeasy固定表現は後順位)。学習価値は中で、基礎的なため『高』とまでは言えない。
- **QA脱落**: GEN5組立失敗3件(上記`oneself`)のみ。VER5/CHK5での脱落は0件(VER5のFIX→revertで形が悪化したものが `something in the way`・`end up taking points away`・`without getting too close`)。

## 4. `put away` / `in the way` の最終到達状況(untidi 2セル。pick→GEN5→VER5→CHK5通過後。canonicalization QA・人称整合・presentable filter・backfillは未適用)

| 方式 | put away系 | in the way系 | 両方 | 備考 |
|---|---|---|---|---|
| 現行N5 Trial03出力(cap7) | 0/2セル | 0/2セル | 0 | |
| 現行方式 新規B1 draw A0(cap7、rep) | 0/24rep | 5/24rep(a2のみ。b1b 0/13) | 0/24 | 委任_02と同値 |
| N5配線後Production実run(M10) | 0/4 | `something in the way` a2 2/2run、`in the way` b1b 1/2run(後者は補完経由) | 0/4 | 付録B |
| **A案(E2+A10 cap10)** | **21/24rep**(a2 9/11・b1b 12/13) | **24/24rep**(a2 11/11・b1b 13/13。`in the way` 7、`something in the way` 17) | **21/24rep** | CAP_SENSITIVITY_03の21/24と一致 |

A案の最終形(正式N5出力): `put it away`→`put something away`「物を所定の場所にしまう」(SAME)、`put away`→`put something away`「物を片づけて収納する」(CHK5=FRAME_SHIFT、修正採用)、`in the way`→`in the way`「邪魔になって」(SAME)、`something in the way`→`something in the way`「邪魔になるもの」(VER5=FIX→revert、CHK5 relationなし)。意味は全て正しい。脱落0。ただし`in the way`系の約7割は`in the way`ではなく`something in the way`の形で出る。

## 5. 再現性・候補の入れ替わり(全repの再計算。細目=付録A)

| セル | rep数 | A案cap10 rep間共通数(平均[最小-最大]/10) | 安定コア(80%以上のrepで選定) | 現行方式A0(cap7)の同指標 |
|---|---|---|---|---|
| untidi_a2 | 11 | 6.13 [4-9] | 5件 | 4.15 [3-6] / 約6.9件、コア3件 |
| untidi_b1b | 13 | 7.59 [5-10] | 7件 | 4.74 [3-7] / 約6.9件、コア4件 |
| melos_a2 | 2 | 8 | 8件 | 4 / 約6.5件 |
| moon_b1b | 2 | 6 | 6件 | 4 / 5件 |
| surname_b1b | 2 | 6 | 6件 | 5 / 5.5件 |

- 共通率はA案が a2 61%・b1b 76%・melos 80%・moon 60%・surname 60%、現行方式が 60%・69%・62%・80%・91%。**再現性は現行と同程度(a2・b1b・melosはA案が同等以上、moon・surnameは2repのみで現行より低い)**。入れ替わる枠は毎回2〜4件。
- 安定コア(例): a2=`hear someone out`(11/11)・`take something away from`(10)・`turn something into`(10)・`put something away`(9)・`get heated`(9)。b1b=`turn into`・`hear someone out`(13/13)・`in session`・`put something away`・`something in the way`・`rely on`・`in sight`(12/13)。
- 現行N5(Trial03出力)の項目がA案の安定コア(80%以上)に残る数: a2 3/7・b1b 4/7・melos 5/7・moon 1/4・surname 4/6。**moon_b1bは現行4件のうち3件がA案ではほぼ選ばれない**。
- 再現性用の追加抽出は不要(全セルrep>=2。メモ: melos/moon/surnameは2repのみのため粗い)。

## 6. 費用・条件

- 追加API費用(Phase 2)=**¥38.88**(見積約40円、Cap 52円、止め線47円。GEN5〜CHK5を16 batch・82候補[A案cap10の和集合56+現行方式A0の比較用11+N5外評価用15]、`ev05/cost_log_g5a/g5b/g5c.jsonl`、呼出ごとのledger)。再現性用の抽出は追加0。本日累計=約521円+38.88円=約560円(日次1,000円内)。
- 量産単価への影響の概算(採用した場合、実測の1候補あたり約¥0.4〜0.47に基づく): GEN5〜CHK5 +3候補/level≒+¥1.3、E2抽出 +¥0.4/level(RESULT_02)、計 約+¥1.7/level≒**+¥3.4/記事セット**(70円目標の約5%)。SEL入力の増加分は含まない概算。
- 条件: 同一記事・同一レベル・同一本文。GEN5/VER5/CHK5は正式採用済みN5のPrompt・モデル・閾値のまま(Production module無編集)。共通候補はTrial03出力を再利用、A案だけの候補を今回実行。≤7件batch。

## 7. 限界・注意

- 現行N5の主表は**Trial03のB1 draw 1回**(fixture)であり、B1のLLM非決定性により「脱落」の一部は現行側のdrawの揺れ(現行方式同士でも共通率は60〜91%)。同一rep内A0との入替(§2-1)を併せて読むこと。
- 付録B(N5配線後Production実run)は3セルのみ・各2run。公開済みProduction出力はN5配線前で比較不可。
- 下流の canonicalization QA・人称整合・presentable filter・重複QA・backfill は**両方式とも未適用**(`gets heated`はこのQAで過去に落ちた[OPEN-633で是正済み]。A案の追加候補がこれらで落ちる割合は未測定)。
- 価値評価は担当者の主観(基準は凡例)。5セル(X3・Y1・Z1、Std2・Adv3)、melos/moon/surnameは2repのみ。代表repはmedoid規則(事前登録)で、他repは付録A。
- SELの判定(keep/難易度)は各rep保存済みの結果を再利用(E2プール+SELを今回再実行していない)。

## 8. 判断候補(分類D=新規判断。Fableが整理)

観測された事実は次のとおり: (a)A案はユーザー指定の最低条件を満たす(`put away`+`in the way`が21/24rep、現行0/24、一般形・意味とも正式N5で正しい)。(b)ただしcap7→10の増分3〜4件の大半は価値が中〜低(基礎的な句動詞が平均+2.1件)、高評価は平均+0.2件/記事。(c)現行の選定が平均3件前後入れ替わり、`gets heated`(b1b)・`Not so fast`(a2)・moonの現行3件などが消える。(d)再現性は現行と同程度。(e)費用は概算+¥3.4/記事セット。
判断の選択肢(候補。推奨は付けない): ①A案をそのまま採用 ②A案を採用し、基礎的な易しい句動詞(SELがeasyの2語句動詞等)の扱いを同時に決める(新仕様候補・ユーザー判断) ③A案を採らず現行維持(目的表現は別の手段) ④E2抽出のみ採用しpick規則は変えない(RESULT_02では効果が限定的)。

## 付録A: セル別 A案cap10の候補別出現頻度(全rep、display_form単位)

### untidi_a2 — Family X untidiness_family_resource(Std)(11rep)

| 出現/rep | display_form(GEN5出力) | 代表source_span(出現数) | 日本語の意味 | relation | 価値(暫定) | 現行N5 |
|---|---|---|---|---|---|---|
| 11/11 | `hear someone out` | `hear it out`(11) | 相手の言い分を最後まで聞く | SAME | 高 | ✓ |
| 10/11 | `take something away from` | `take points away from`(10) | 〜から点数などを差し引く、取り去る | GLOSS_MISMATCH | 中 | ✓ |
| 10/11 | `turn something into` | `turn the talk into`(10) | 〜を別のものへと変える | SAME | 中 | ✓ |
| 9/11 | `put something away` | `put it away`(9) | 物を所定の場所にしまう | SAME | 高 |  |
| 9/11 | `get heated` | `gets heated`(9) | （会話などが）感情的で激しくなる | SAME | 高 |  |
| 8/11 | `speak for` | `speaks for`(6), `speak for it`(1), `speak for`(1) | 人を代表して発言する | SAME | 中 |  |
| 7/11 | `come from` | `comes from`(7) | 〜に由来する、〜から生じる | SAME | 低 |  |
| 6/11 | `ask for` | `ask for`(3), `ask for it`(3) | 〜を求める、依頼する | SAME | 低 |  |
| 6/11 | `look at` | `look at clutter`(6) | 〜を見る、検討する | SAME | 低 |  |
| 6/11 | `in the way` | `in the way`(6) | 邪魔になり、物事の進行を妨げて | SAME | 高 |  |
| 5/11 | `something in the way` | `something in the way`(5) | 邪魔になるもの、妨げ |  | 中 |  |
| 4/11 | `make something work` | `make life work`(4) | 物事をうまく機能させる | SAME | 中 | ✓ |
| 3/11 | `need another look` | `needs another look`(3) | 再検討を必要とする | SAME | 中 |  |
| 3/11 | `in a way` | `In a way`(3) | ある意味では、またはある点から見れば | SAME | 中 |  |
| 2/11 | `take up space` | `take up space`(2) | ある場所を占有して空間をふさぐ | SAME | 中 |  |
| 2/11 | `rely on` | `relied on`(2) | 頼りにする | SAME | 中 | ✓ |
| 2/11 | `in session` | `in Session`(2) | 裁判や会議が開催中である | SAME | 中 | ✓ |
| 2/11 | `miss something` | `missing doses`(2) | 予定されたことを逃す、またはし損なう | SAME | 低 |  |
| 1/11 | `keep something in sight` | `keeping supplements in sight`(1) | 物を見える状態にしておく | SAME | 中 |  |
| 1/11 | `live together` | `lived together`(1) | 同じ場所で生活を共にする | SAME | 低 |  |
| 1/11 | `help with` | `help with`(1) | 何かの作業や問題を手助けする | SAME | 低 |  |
| 1/11 | `not so fast` | `Not so fast`(1) | 急ぐな、まだそう決めるな | SAME | 高 | ✓ |
| 1/11 | `another way to look at` | `another way to look at`(1) | 別の観点から考える方法 | SAME | 低 |  |

### untidi_b1b — Family X untidiness_family_resource(Adv)(13rep)

| 出現/rep | display_form(GEN5出力) | 代表source_span(出現数) | 日本語の意味 | relation | 価値(暫定) | 現行N5 |
|---|---|---|---|---|---|---|
| 13/13 | `turn into` | `turn into an interrogation`(13) | 別の状態や性質へと変わる | SAME | 中 | ✓ |
| 13/13 | `hear someone out` | `hear it out`(13) | 相手の話を最後まで聞く | SAME | 高 | ✓ |
| 12/13 | `in session` | `Now in Session`(12) | 会議や裁判などが開会中である | SAME | 中 | ✓ |
| 12/13 | `put something away` | `put away`(9), `put it away`(3) | 物を片づけて収納する | FRAME_SHIFT | 高 |  |
| 12/13 | `something in the way` | `something in the way`(12) | 邪魔になるもの | SAME | 中 |  |
| 12/13 | `rely on` | `relied on`(12) | 人や物を頼りにする | SAME | 中 | ✓ |
| 12/13 | `in sight` | `in sight`(12) | 見えるところにある | SAME | 中 |  |
| 9/13 | `speak for` | `speaking for the side`(7), `speaking for`(2) | 誰かを代表して発言する | SAME | 中 |  |
| 9/13 | `leave something out` | `leave it out`(9) | 何かを外に出したままにしておく | SAME | 中 |  |
| 6/13 | `end up taking points away` | `end up taking points away`(6) | 評価を落とす、減点する |  | 低 | ✓ |
| 5/13 | `look at` | `look at clutter`(5) | 〜を検討する、捉え方を考える | SAME | 低 |  |
| 4/13 | `take up space` | `taking up space`(4) | 空間を占める | SAME | 中 |  |
| 2/13 | `make something work` | `make life work`(2) | 何かをうまく機能させる | SAME | 中 |  |
| 2/13 | `without question` | `without question`(2) | 疑問を差し挟まずに | SAME | 中 |  |
| 2/13 | `miss dose` | `missed doses`(2) | 予定された薬の服用をし損なう | SAME | 低 |  |
| 1/13 | `apply something to` | `applied to every household`(1) | 〜を〜に当てはめる、適用する | FRAME_SHIFT | 中 |  |
| 1/13 | `spoil the look` | `spoiling the look`(1) | 見た目を損ねる | SAME | 中 |  |
| 1/13 | `live together` | `lived together`(1) | 同じ場所で一緒に暮らす | SAME | 低 |  |
| 1/13 | `not so fast` | `Not so fast`(1) | ちょっと待て、そう急ぐな | SAME | 高 |  |
| 1/13 | `in the way` | `in the way`(1) | 邪魔になって | SAME | 高 |  |

### melos_a2 — Family Z 走れメロス(Std)(2rep)

| 出現/rep | display_form(GEN5出力) | 代表source_span(出現数) | 日本語の意味 | relation | 価値(暫定) | 現行N5 |
|---|---|---|---|---|---|---|
| 2/2 | `pull someone under` | `pulled him under`(2) | 水面下へ引き込む | SAME | 中 | ✓ |
| 2/2 | `lose one's trust in` | `lost my trust in you`(2) | 信頼を失う | SAME | 中 | ✓ |
| 2/2 | `win trust` | `win such trust`(2) | 信頼を獲得する | MODIFIER_DROPPED_OK | 中 | ✓ |
| 2/2 | `in someone's place` | `in your place`(2) | 身代わりの立場で | SAME | 高 | ✓ |
| 2/2 | `come back` | `come back`(2) | 戻ってくる | SAME | 低 |  |
| 2/2 | `lose one's life` | `lose his life`(2) | 命を失う | SAME | 中 | ✓ |
| 2/2 | `stand up` | `stood up`(2) | 立ち上がる | SAME | 低 |  |
| 2/2 | `give someone a chance` | `give them a chance`(2) | 人に機会を与える | SAME | 中 |  |
| 1/2 | `leave for` | `left for the city`(1) | 〜へ向けて出発する | SAME | 中 |  |
| 1/2 | `walking stick` | `walking stick`(1) | 歩行を助ける杖 | SAME | 低 |  |
| 1/2 | `step back` | `stepped back`(1) | 後ろへ下がる | SAME | 低 |  |
| 1/2 | `put something down` | `Put the sword down`(1) | 物を下ろして置く | SAME | 低 |  |

### moon_b1b — Family X moon_shrinking(Adv)(2rep)

| 出現/rep | display_form(GEN5出力) | 代表source_span(出現数) | 日本語の意味 | relation | 価値(暫定) | 現行N5 |
|---|---|---|---|---|---|---|
| 2/2 | `offer clues to` | `offer clues to`(2) | 〜への手掛かりを提供する | SAME | 中 |  |
| 2/2 | `work out` | `work out`(2) | 考えたり計算したりして答えを導く | SAME | 中 | ✓ |
| 2/2 | `put something on` | `put on`(2) | 何かを身につける | SAME | 低 |  |
| 2/2 | `way off` | `way off`(2) | 正確さや基準から大きく外れている | SAME | 中 | ✓ |
| 2/2 | `up close` | `up close`(2) | 近くで見ると | SAME | 中 |  |
| 2/2 | `hold on` | `hold on a moment`(2) | 少し待つよう求める | MODIFIER_DROPPED_OK | 低 |  |
| 1/2 | `keep something from escaping` | `keeps heat from escaping`(1) | 何かが逃げるのを防ぐ | FRAME_SHIFT | 中 |  |
| 1/2 | `a record of` | `a record of`(1) | 〜の記録や痕跡である | SAME | 中 |  |
| 1/2 | `on the other hand` | `On the other hand`(1) | 対比する別の側面を示す | SAME | 中 |  |
| 1/2 | `take measurements` | `Taking the Moon's measurements`(1) | 測定を行う | MODIFIER_DROPPED_OK | 中 |  |
| 1/2 | `shoving match` | `shoving match`(1) | 強く押し合う激しい争い | SAME | 中 | ✓ |
| 1/2 | `keep something in` | `keeps heat in`(1) | 何かを内部に保つ | SAME | 低 | ✓ |
| 1/2 | `lead to` | `led to`(1) | 〜へつながる、〜をもたらす | SAME | 中 |  |
| 1/2 | `as a result` | `As a result`(1) | その結果として | SAME | 中 |  |

### surname_b1b — Family Y surname_choice(Adv)(2rep)

| 出現/rep | display_form(GEN5出力) | 代表source_span(出現数) | 日本語の意味 | relation | 価値(暫定) | 現行N5 |
|---|---|---|---|---|---|---|
| 2/2 | `take offense` | `taking offense`(2) | 気分を害する、腹を立てる | SAME | 高 | ✓ |
| 2/2 | `at ease` | `at ease`(2) | 緊張や不安がなく、落ち着いている | SAME | 中 | ✓ |
| 2/2 | `let go of` | `let go of`(2) | 人への執着を手放し、自由にする | SAME | 高 |  |
| 2/2 | `hold someone back` | `hold my son back`(2) | 進歩や行動を妨げる | SAME | 高 | ✓ |
| 2/2 | `give something up` | `giving something up`(2) | 断念する、放棄する | SAME | 中 | ✓ |
| 2/2 | `care about` | `care about different things`(2) | 何かに関心を持ち、大切に思う | SAME | 低 |  |
| 1/2 | `(n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'myself'の語形違いでない)` | `get much time to myself`(1) | — |  | — |  |
| 1/2 | `move away` | `moving away`(1) | 離れていく、距離ができる | SAME | 低 |  |
| 1/2 | `(n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'themselves'の語形違いでない)` | `decide for themselves`(1) | — |  | — |  |
| 1/2 | `have no problem` | `had no problem at all`(1) | 問題や抵抗を感じない | MODIFIER_DROPPED_OK | 低 |  |
| 1/2 | `(n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'myself'の語形違いでない)` | `time to myself`(1) | — |  | — |  |
| 1/2 | `far from` | `far from us`(1) | 〜から遠く離れて | SAME | 中 |  |
| 1/2 | `only natural` | `only natural`(1) | 当然で、もっともだと思われる | SAME | 中 | ✓ |
| 1/2 | `no problem at all` | `no problem at all`(1) | まったく問題がないこと | SAME | 低 |  |

## 付録B: N5配線後のProduction実run(参考。同一本文、`KP-GENERALIZATION-N5-PRODUCTION-WIRING-01` M10、ev02/ev03)の phrase kind 最終候補

Production全工程(call1のP7＋B1 pool→SEL→pick cap7→GEN5/VER5/CHK5→救済→canonicalization QA→backfill)を通した実出力。比較の主表(Trial03のN5出力)とは別のB1抽出drawなので、**現行N5自体の実行間のばらつき**を示す。`origin=backfill`は補完工程で後から入った候補。

| run | 選定phrase → used_form | 日本語 | origin |
|---|---|---|---|
| untidi_a2/ev02 | `take points away from` → `take something away from` | 〜から何かを取り去る、差し引く | call1 |
| untidi_a2/ev02 | `hear it out` → `hear someone out` | 相手の言い分を最後まで聞く | call1 |
| untidi_a2/ev02 | `in Session` → `in session` | 会議や審理が開かれている | call1 |
| untidi_a2/ev02 | `something in the way` → `something in the way` | 邪魔になっているもの | call1 |
| untidi_a2/ev02 | `relied on` → `rely on` | 人や物を頼りにする | call1 |
| untidi_a2/ev02 | `turn the talk into` → `turn something into` | 何かを別の形や状態へ変える | call1 |
| untidi_a2/ev03 | `take points away from` → `take something away from` | 何かをあるものから取り除く、差し引く | call1 |
| untidi_a2/ev03 | `hear it out` → `hear someone out` | 人の話を最後まで聞く | call1 |
| untidi_a2/ev03 | `taking its job quite seriously` → `take something seriously` | 何かを重要なこととして真剣に扱う | call1 |
| untidi_a2/ev03 | `Not so fast` → `not so fast` | ちょっと待って、そう急ぐな | call1 |
| untidi_a2/ev03 | `take up space` → `take up space` | 場所を占める | call1 |
| untidi_a2/ev03 | `something in the way` → `something in the way` | 通行や行動の邪魔になっている状態 | call1 |
| untidi_a2/ev03 | `needs another look` → `need another look` | 改めて詳しく検討する必要がある | backfill |
| untidi_b1b/ev02 | `hear it out` → `hear someone out` | 相手の話を最後まで聞く | call1 |
| untidi_b1b/ev02 | `turn into an interrogation` → `turn into` | 別の状態や性質へと変わる | call1 |
| untidi_b1b/ev02 | `taking points away` → `take points away` | 点数を差し引いて評価を下げる | call1 |
| untidi_b1b/ev02 | `speaking for the side` → `speak for` | 人や集団を代表して意見を述べる | call1 |
| untidi_b1b/ev02 | `still on the job` → `on the job` | 勤務中で、仕事をしている状態 | call1 |
| untidi_b1b/ev02 | `relied on` → `rely on` | 人や物事を頼りにする | call1 |
| untidi_b1b/ev03 | `hear it out` → `hear someone out` | 人の話を最後まで聞く | call1 |
| untidi_b1b/ev03 | `turn into an interrogation` → `turn into` | 何か別のものへと変化する | call1 |
| untidi_b1b/ev03 | `end up taking points away` → `end up taking points away` | 最終的に点を差し引く | call1 |
| untidi_b1b/ev03 | `taking up space` → `take up space` | 空間を占める | call1 |
| untidi_b1b/ev03 | `still on the job` → `on the job` | 仕事中である | call1 |
| untidi_b1b/ev03 | `in Session` → `in session` | 裁判や会議などが開かれ、進行中である | backfill |
| untidi_b1b/ev03 | `in the way` → `in the way` | 邪魔になり、行動や進行を妨げる | backfill |
| melos_a2/ev02 | `in your place` → `in someone's place` | 人の代わりとして | call1 |
| melos_a2/ev02 | `pulled him under` → `pull someone under` | 人を水中へ引き込む | call1 |
| melos_a2/ev02 | `rose above everyone's voices` → `rise above something` | 音が他の音を上回って響く | call1 |
| melos_a2/ev02 | `lost my trust in you` → `lose one's trust in` | 人に対する信頼を失う | call1 |
| melos_a2/ev02 | `win such trust` → `win trust` | 信頼を得る | call1 |
| melos_a2/ev02 | `For once` → `for once` | 今回に限っては | call1 |
| melos_a2/ev02 | `lose his life instead` → `lose one's life` | 命を落とす | call1 |
| melos_a2/ev03 | `lost my trust in you` → `lose one's trust in` | 人への信頼を失う | call1 |
| melos_a2/ev03 | `pulled him under` → `pull someone under` | 人を水中へ引きずり込む | call1 |
| melos_a2/ev03 | `rose above everyone's voices` → `rise above something` | 〜より際立って聞こえる | call1 |
| melos_a2/ev03 | `lose his life` → `lose one's life` | 命を失う、死ぬ | call1 |
| melos_a2/ev03 | `kept his eyes on them` → `keep one's eyes on` | 人を見続け、注意を向けておく | call1 |
| melos_a2/ev03 | `win such trust` → `win trust` | 信頼を勝ち取る | call1 |
| melos_a2/ev03 | `in your place` → `in someone's place` | 人の代わりに、身代わりとして | call1 |

同runで落ちた候補(段・理由): 
- untidi_a2/ev02: `make life work`(n5_select) / `gets heated`(canonicalization_qa) / `did not test whether`(n5_select) / `make daily life work`(n5_select) / `rush to say`(n5_select)
- untidi_a2/ev03: `make life work`(n5_select) / `gets heated`(canonicalization_qa) / `relied`(canonicalization_qa) / `make daily life work`(n5_select)
- untidi_b1b/ev02: `cannot simply be applied`(n5_select) / `gets heated`(canonicalization_qa) / `did not test whether`(n5_select) / `prevents missed doses`(n5_select) / `participant's own explanation`(n5_select)
- untidi_b1b/ev03: `make life work`(n5_select) / `applied to every household`(n5_select) / `taking its job quite seriously`(n5_generalize) / `gets heated`(canonicalization_qa) / `cannot simply be applied to`(n5_select)
- melos_a2/ev02: `held out`(n5_select) / `blocked his way`(n5_select)
- melos_a2/ev03: `ordered his death`(n5_select) / `left you to die`(n5_select)

## 付録C: N5(現行cap7・A案cap10)から外れた表現の実測(display_formはGEN5→VER5→CHK5の実出力)

「pool/keep/cap10」=E2プールに出現したrep数 / SEL keepだったrep数 / A10 cap10に入ったrep数。価値は担当者の暫定評価。

| 記事 | source_span | display_form (GEN5出力) | 日本語の意味 | pool/keep/cap10 (rep数) | SEL多数ラベル | 価値(暫定)と所見 |
|---|---|---|---|---|---|---|
| untidi_b1b | `gets heated` | `get heated` | 感情的になり、議論などが白熱する | 13/13/0 (N=13) | C/collocation/upper_intermediate | 高: 議論が白熱するという会話・ニュースで頻出のcollocation。cap10では0/13repで入らない(現行N5のTrial03出力には入っている)。Production実runではcanonicalization QA再判定key不一致で落ちていた(OPEN-633で是正済み) |
| untidi_b1b | `In other words` | `in other words` | 言い換えると、つまり | 13/13/0 (N=13) | C/fixed_phrase/easy | 中: 談話標識。汎用性は高いが基礎的でSELはeasy判定。cap10では0/13rep |
| untidi_b1b | `No wonder` | `no wonder` | 当然だと思うこと、驚くにあたらないこと | 13/13/0 (N=13) | C/fixed_phrase/easy | 中: 会話表現として有用。cap10では0/13rep |
| untidi_b1b | `in a way` | `in a way` | ある意味では、ある点では | 13/13/0 (N=13) | C/fixed_phrase/easy | 中: 『ある意味では』。基礎的な固定表現。cap10では0/13rep |
| untidi_b1b | `on the job` | `on the job` | 勤務中で、仕事をしている状態で | 11/11/0 (N=13) | C/fixed_phrase/upper_intermediate | 中: 『勤務中』。cap10では0/13rep(現行N5は`still on the job`を選定する回がある) |
| untidi_b1b | `taking its job quite seriously` | `take something seriously` [MODIFIER_DROPPED_OK] | 何かを重要なものとして真剣に扱う | 9/9/0 (N=13) | C/collocation/upper_intermediate | 中: take something seriouslyの形で汎用。5語で本文形が長い |
| untidi_a2 | `Not so fast` | `not so fast` | 急ぐな、まだそう決めるな | 11/11/1 (N=11) | C/fixed_phrase/easy | 高: 会話の制止表現。cap10入りは1/11rep(現行N5のTrial03出力には入っている) |
| untidi_a2 | `take up space` | `take up space` | ある場所を占有して空間をふさぐ | 11/11/2 (N=11) | C/phrasal_verb/easy | 中: 場所を取るという汎用句動詞的表現。cap10入りは2/11rep |
| untidi_a2 | `No wonder` | `no wonder` | 〜なのも不思議ではない | 11/11/0 (N=11) | C/fixed_phrase/easy | 中: cap10入りは0/11rep |
| untidi_a2 | `In a way` | `in a way` | ある意味では、またはある点から見れば | 11/11/3 (N=11) | C/fixed_phrase/easy | 中: cap10入りは3/11rep |
| untidi_a2 | `in sight` | `in sight` | 視界に入って、見える状態に | 10/10/0 (N=11) | C/fixed_phrase/upper_intermediate | 中: 見える範囲にある。cap10入りは0/11rep(b1bでは12/13rep) |
| untidi_a2 | `leave it out` | `leave something out` | 物をしまわず外に出したままにする | 11/9/0 (N=11) | C/phrasal_verb/easy | 中: leave out系。cap10入りは0/11rep(b1bでは9/13rep)。記事主題の核(`Leaving Things Out`)に近い |
| melos_a2 | `waited for a reply` | `wait for` | 何かが来るのを待つ | 2/2/0 (N=2) | C/phrasal_verb/easy | 低: wait for。基礎語の自由な組合せに近い |
| melos_a2 | `blocked his way` | `block someone's way` | 人の進路をふさぐ | 2/1/0 (N=2) | C/collocation/upper_intermediate | 中: block someone's way。cap10入り0/2rep |
| melos_a2 | `turned around` | `turn around` | 向きを変えて後ろを向く | 1/1/0 (N=2) | C/phrasal_verb/easy | 低: turn around。基礎的な句動詞 |
| melos_a2 | `kept his eyes on them` | `keep one's eye on` | 視線を注ぎ続ける | 1/1/0 (N=2) | C/collocation/upper_intermediate | 中: keep one's eye on。現行N5のTrial03出力には入っている |
| melos_a2 | `For once` | `for once` | 今回に限って、いつもとは違い | 1/1/0 (N=2) | C/fixed_phrase/upper_intermediate | 中: 『今回に限って』。固定表現。cap10入り0/2rep |
| moon_b1b | `In other words` | `in other words` | 別の言い方を示し、前の内容を言い換える | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: 談話標識。cap10入り0/2rep |
| moon_b1b | `no need for` | `no need for` | 必要がないこと | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: no need for something。cap10入り0/2rep |
| moon_b1b | `For now` | `for now` | 今のところ、当面は | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: 『当面は』。cap10入り0/2rep |
| moon_b1b | `quite a lot of` | `quite a lot of` | かなり多くの量や数があること | 2/2/0 (N=2) | C/fixed_phrase/easy | 低: 量の基礎表現 |
| moon_b1b | `too soon to say` | `too soon to say` | 判断を下すにはまだ早い | 2/1/0 (N=2) | C/fixed_phrase/easy | 中: 『まだ何とも言えない』。記事の論調に関わる表現。cap10入り0/2rep |
| surname_b1b | `got married` | `get married` | 結婚して夫婦になる | 2/2/0 (N=2) | C/collocation/easy | 低: get married。基礎的 |
| surname_b1b | `again and again` | `again and again` | 何度も繰り返して | 2/2/0 (N=2) | C/fixed_phrase/easy | 中: 繰り返しを表す固定表現。cap10入り0/2rep |
| surname_b1b | `got very upset` | `get upset` [MODIFIER_DROPPED_OK] | 動揺したり腹を立てたりする | 2/1/0 (N=2) | C/collocation/easy | 低: get upset。基礎的 |
| surname_b1b | `without getting too close` | `without getting too close` | 深入りしすぎる、親しくなりすぎる | 2/1/0 (N=2) | C/collocation/upper_intermediate | 低: VER5でrevertされ汎用形にならず、日本語訳も`without`を反映しない(『深入りしすぎる』) |
| surname_b1b | `decide for themselves` | (脱落 n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'themselves'の語形違いでない) | — | 2/2/1 (N=2) | C/fixed_phrase/upper_intermediate | 高: decide for oneself。A案cap10に入った回でGEN5が`oneself`再帰形のlemma不一致で組立失敗(QA脱落)。現行N5でも同じGEN5で同様に落ちる |
| surname_b1b | `get much time to myself` | (脱落 n5_generalize: 一般形の組立に失敗: lemma'oneself'が本文の語'myself'の語形違いでない) | — | 1/1/1 (N=2) | C/collocation/upper_intermediate | 中: time to oneself。同様にGEN5組立失敗(QA脱落) |
