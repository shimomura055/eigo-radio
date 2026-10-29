# FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01 結果(Trial。Status=Trial実施済み、評価=VALIDATED候補。一般化方式の正式採用=ユーザー判断待ち)

証跡: `er121_output/family_y_intro_trial_01/surname/`(`ja_candidates_AB.json`/`ja_candidates_C.json`/`ja_candidates_D.json`=JA全候補+check_intro結果、`prompt_A.txt`/`prompt_B.txt`/`prompt_C.txt`/`prompt_D.txt`、`en_preview.json`、`v1_gate_result.json`+`gate_REC`/`gate_MIN`、cost_log*.jsonl)。設計=`TRIAL_DESIGN_01.md`。使用モデル: 紹介文生成・英語化=gpt-6.1-sol(effort high。Production routeと同一かつ最新上位)、補助Gate=gpt-6-luna(Production既定のLeakage判定model)。生成codeは`er121_family_y_intro_trial_01.py`/`_en_01.py`/`_gate_01.py`(DEV専用、Production未配線)。

## 1. 変更前(run_02 現行。Std/Adv英・日)
| Voice | JA(intros_final.json) | Adv EN(translate/b1b.md) | Std EN(translate/a2.md) |
|---|---|---|---|
| 1 | 最初に話すのは、婿養子として妻の姓を名乗る父親。妻の実家で、家族と暮らしている。 | The first speaker is a father who took his wife's last name when he joined her family as an adopted son. He lives with his family at his wife's parents' home. | The first speaker is a father. He took his wife's last name and joined her family as an adopted son. He lives with his family at his wife's parents' home. |
| 2 | 次は、来年結婚する息子がいる母親。息子が妻の姓を選ぶと聞いて、寂しさを感じた。 | The next speaker is a mother whose son is getting married next year. She felt sad when she heard he would take his wife's last name. | The next speaker is a mother. Her son will marry next year. She felt sad when she heard he would take his wife's last name. |
| 3 | 最後は、妻の姓を選んだ身内がいる親世代の人。子どもの結婚は、まだこれからのことだ。 | The last speaker is a parent whose relative took his wife's last name. Their own child has not married yet. | The last speaker is a parent. A relative took his wife's last name. The parent's own child is not married yet. |

## 2. 変更後候補(Trial出力。各Voice 1〜2案)
Production `check_intro`(決定論検査)の結果を併記。A1/A2=原則のみ、B1/B2=原則+話題との関わり、C1/C2=+事実範囲、D1=+時期表現禁止。
| Voice | 案 | JA | check_intro | 所見 |
|---|---|---|---|---|
| 1 | **REC(推奨・A1から時期語を除去)** | 最初に話すのは、妻の姓を名乗り、妻の実家で家族と暮らしている男性だ。 | OK(34字)+Lead/紹介補助Gate PASS(luna) | 立場(妻の姓を名乗る)が主、父親属性なし。事実はsheet(婿養子・妻の実家で同居)の範囲 |
| 1 | A1(生成そのまま) | 最初に話すのは、結婚して妻の姓を名乗り、妻の実家で家族と暮らしている男性だ。 | OK | 「結婚して」はsheetに無い時期(後述 発見事項1) |
| 1 | B1 | 最初に話すのは、結婚を機に妻の姓になった男性。妻や妻の家族と、同じ家で暮らしている。 | OK | 同上(「結婚を機に」) |
| 1 | MIN(対照: 「父親」→「男性」だけ) | 最初に話すのは、婿養子になって妻の姓を名乗っている男性。妻の実家で、家族と暮らしている。 | **NG COPIES_VOICE_BODY_10CHARS**(本人語りの文と10字連続一致) | 最小置換だと既存検査に落ちる(補助Gate自体はPASS) |
| 2 | B1(推奨候補) | 次は、結婚を控えた息子が、相手の姓を名乗ると決めたことを知らされた母親。 | OK | 現行の「寂しさを感じた」(感情の先取り)が消え、立場だけが残る。sheet contact_point(相手の親の希望を息子が受入れ、と知らされた側)と整合 |
| 2 | 現行維持 | 次は、来年結婚する息子がいる母親。息子が妻の姓を選ぶと聞いて、寂しさを感じた。 | (既承認) | 「母親」は『息子の結婚』という本テーマの立場そのもの。属性を前面に出す正当な例 |
| 3 | B1 | 最後は、妻の姓になった身内がいる親世代の人。子どもの結婚は、これからのこととして考えている。 | OK | 現行と情報同等 |
| 3 | 現行維持 | (上表) | (既承認) | **Std KP3(`A relative took his wife's last name`)とPart 1の出典文がStd V3紹介行そのものであり変更不可**(後述) |

英語化preview(`en_preview.json`、gpt-6.1-sol。記事未適用):
- V1 REC相当(A1由来)Std: `The first speaker is a man who took his wife's last name. He lives with his family at his wife's parents' home.` ← 「when they married」を含まない形。Adv A1: `...a man who took his wife's last name when they married. He lives with his family in his wife's family home.`(時期語を含むためREC=Std文をAdvにも使うことを推奨)
- V1 MIN Adv/Std: `a man who has been adopted into his wife's family and uses her last name` / `a man adopted into his wife's family. He took her last name and lives...`
- V2 B1 Adv: `The next speaker is a mother whose son is about to get married. She has been told that he has decided to take his partner's last name.` / Std: `...a mother whose son will marry soon. She learned he decided to take his partner's last name.`
- V3 B1 Adv/Std: `The last speaker is a parent whose relative took his wife's last name. They see their own child's marriage as something that lies ahead.` / `...Their own child's marriage is still something for the future.`

## 3. 評価
- **立場の明確さ・誤解の解消**: REC(V1)は「妻の姓を名乗る男性」が主語になり、「父親=息子の結婚を語る人」という誤読の原因(`father`を独立した第1文にした英訳)が構造的に消える。V2は母親属性を残した(テーマ本体が『息子の結婚』なので立場の理解に必要=原則の「重要な場合に使用」に整合)。**原則は『属性の全削除』ではなく『テーマ関連の立場を主、属性は従』として機能**。
- **発見事項1(事実性)**: 原則A/B/C/Dのどれでも、モデルは「結婚して/結婚を機に」という時期を足した(C・Dで禁止を明示しても発生)。sheet(`sheets.voice_1.experiences` ONE_a/ONE_h)は『4年前に婿養子に入った・同居は8年前から』で結婚時の改姓とは限らない。**ユーザー参考例「…when they got married」も同じ前提を含む**(参考例であり固定Promptではないとの指示)。⇒ 一般化仕様に『sheetに無い時期・きっかけを足さない』を決定論検査(時期語の禁止regex等)として入れない限り、Prompt指示だけでは再発する。RECは人手の最小修正(時期語除去)で、`check_intro`+補助Gateは通過。
- **発見事項2(既存検査との相性)**: MIN(最小置換)は`COPIES_VOICE_BODY_10CHARS`で既存検査に落ちる。`ROLE_NOT_CONVEYED`が出た候補もあり(A2 V3・D V3)、役割語を落とすと既存の`_role_hint_match`(role_ja+who_jaの2字連続)に抵触する。一般化を正式採用するなら`intro_checks`(theme_package)の`role_patterns`の役割語集合も立場語に更新が必要。
- **他Voiceの自然さ**: V2/V3のB1は現行と同程度に自然。V3は『親世代の人』の属性が立場そのもの(第三者)であり、一般化原則と矛盾しない。
- **創作なし**: REC・V2 B1・V3 B1とも、`role_ja`/`contact_point_ja`/`experiences`の範囲(REC=妻の姓・妻の実家で家族と同居)。
- **Status判定**: Trial。一般化原則+Prompt差分は候補として機能したが、時期の創作が再発する欠点があり、正式採用には(1)時期語の決定論検査追加 (2)role_patternsの更新 (3)他記事での検証が要る。**到達可能Status=VALIDATED(本記事のV1に限る有効性)**。一般化方式の正式採用はユーザー判断(UDR)。
- **本記事への反映の区別**: (a)ユーザーが指摘した誤紹介(V1の「父親」)の是正=ユーザー指示に基づく個別是正(推奨=REC)。(b)一般化方式のProduction採用=別(未承認。Productionの`persona_intro_01.txt`は不変更)。04Bで(a)のみ適用する。

## 4. 本記事への適用範囲の推奨(04B)
- 変更するのは**V1の紹介行のみ**(Std/Adv、JA+EN)。V2は現行で立場が明確。**V3はStd KP3`A relative took his wife's last name`(a2 keywords_canonicalized rank3)とStd Part 1の出典文がStd V3紹介行そのものなので変更不可**(変更するとKP再選定・HR再確認が必要)。
- V1の紹介文は、Std/Adv KP・Part 1・Part 2の確定項目の出典文には使われていない(確認: run_02のconfirmed系json[b1b/a2のkeywords_canonicalized・vocab_confirmed・part1_vocabulary_expressions・confirmed_grammar]に「first speaker」「joined her family」等のV1紹介文は無い。Grepで確認済み)。
