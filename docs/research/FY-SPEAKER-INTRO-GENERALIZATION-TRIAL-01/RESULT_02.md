# FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01 委任_02 結果(追加2記事Trial。DEV/Trial専用・Production未配線。到達Status上限=VALIDATED)

原文§3: `docs/pm/delegation_log/2026-10-29_FY-FZ-FEMALE-VOICE-RANK-01_USER.md`は作業時点では未保存だったため委任文§3要約を根拠とした(その後保存済み、逐語照合は未実施)。
証跡: `er121_output/family_y_intro_trial_01/{redelivery_fee,sns_age_limit}/`(`ja_candidates_AB.json`・`ja_candidates_E.json`=JA全候補+Production `check_intro`結果、`prompt_A/B/E.txt`、`en_preview.json`=Adv/Std英語化(既存英訳の紹介行を`baseline_en`に保存)、`cost_log*.jsonl`)。生成code=`er121_family_y_intro_trial2_01.py`・`er121_family_y_intro_trial2_en_01.py`(DEV専用。`er121_family_y_intro_trial_01.build`を再利用、Production Prompt/関数/runner/theme packageは無変更、音声生成0)。
使用モデル: 紹介文生成・英語化=gpt-6.1-sol(effort high。Production route `FAMILY_Y_PERSONA_INTRO`と同一かつ最新上位)。補助Gate(luna)は今回未実行(check_intro参考実行のみ)。

## 1. 選定2記事と理由
| 記事 | run(変更前の出典) | 属性と立場の関係 | 選定理由 |
|---|---|---|---|
| redelivery_fee(宅配の再配達) | `er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01`(intros_final.json、translate/b1b.md・a2.md) | 属性(職業・受取人)=そのまま立場。V1=宅配ドライバー、V2=共働きの受取人、V3=受取り方を工夫する受取人 | surname(属性『父親』が立場と乖離)の対極。属性名を**残すべき**例で、原則が過剰削除しないかを見る |
| sns_age_limit(子どものSNS年齢制限) | `er121_output/family_y_production_01/sns_age_limit/run_01` | 属性(親・高校生)が立場の一部。ただし同じ『親』でも子の年齢(幼児/中学生)で立場が異なり、高校生は規制の当事者 | 属性+関与の仕方(見守る/判断する/規制対象)で立場が決まる中間型。『親』属性の機械転記・使い分けを見る |

(他のY完成記事は上記2件とsurnameのみ。Theme Package sheets.role_ja / contact_point_ja: redelivery V1=現役の宅配ドライバー/再配達をする側、V2=共働き世帯の受取人/払う側にされうる、V3=再配達を出さないよう工夫している受取人/払わずに済むことが多い側。sns V1=小さい子どもを育てている親/見守り設定する立場、V2=高校生/年齢制限の対象になる側、V3=中学生の子どもを育てている親/いつ・どこまで使わせるか判断する立場。)

## 2. 比較表(変更前=現行intros_final+現行英訳。変更後=Trial候補。◎=推奨)
### redelivery_fee
| Voice | 変更前JA | 変更前EN(Adv / Std) | 変更後JA(候補) | 変更後EN(Adv / Std。preview) |
|---|---|---|---|---|
| 1 | 最初に話すのは、日々の配達で家々を回り、荷物を届けている宅配ドライバーだ。 | First to speak is a delivery driver who visits homes every day and delivers packages. / First, hear from a delivery driver who visits homes every day. | A1: …荷物を届けて回る仕事をしている人。配達する側の声だ。 / B1: …毎日荷物を届けて回るドライバー。留守だった家へ、もう一度向かうのも仕事だ。 / ◎E1: …毎日荷物を届けて回る宅配ドライバー。再配達も日々の仕事のひとつだ。 | A1 Adv: someone whose job is to go around delivering packages every day… / B1 Adv: a driver who goes around delivering packages every day. They also return to homes after finding no one there. / B1 Std: …They also return to homes where no one was in. |
| 2 | 次は、夫婦ともに仕事があって家を空けがちな、宅配便を受け取る側の人だ。 | Next is someone who receives packages and is often away from home because both she and her husband work. / Next, hear from a woman who gets packages and is often away. She and her husband both work. | B1: …夫婦ともに仕事があり、家を空けがちな人。家にいられる時間を考えながら、荷物を受け取っている。 / ◎E2: …夫婦ともに仕事で家を空けがちな受取人。家にいられる時間に合わせ、荷物を受け取ろうとしている。 | B1 Adv: someone who is often away from home because both they and their spouse work. They think about when they can be at home to receive packages. |
| 3 | 最後は、ロッカーでの受け取りなどを選び、再配達にならないよう工夫している人だ。 | Lastly, a person who chooses to pick up packages at a locker or another place and takes steps to avoid redelivery. / Lastly, hear from someone who picks up packages at a locker or another place to avoid another delivery. | B1: …ロッカーなどへ荷物を取りに行く人。再配達にならないよう、受け取り方を工夫している。 / ◎E2: …ロッカーなどを使って荷物を受け取る人。再配達にならないよう、受け取り方を工夫している。 | B1 Adv: someone who goes to lockers or other locations to collect packages. They plan how to receive their packages to avoid redelivery. |

### sns_age_limit
| Voice | 変更前JA | 変更前EN(Adv / Std) | 変更後JA(候補) | 変更後EN(Adv / Std。preview) |
|---|---|---|---|---|
| 1 | 最初に話すのは、小さい子どもを育てている親。子どもを見守る毎日の中で、SNSについて考える。 | First to speak is a parent raising a young child. They think about social media as they watch over their child each day. / First, a parent with a young child speaks. They think about social media while looking after their child each day. | A2: …小さい子どもを日々そばで見守り、子育ての中でSNSの利用を考える親。 / ◎E2: …小さい子の動画の利用を見守り、使い方を決める立場の親だ。 / B2: …小さい子どもが見る動画を確かめ、使い方に気を配っている親だ。 | B2 Adv: First to speak is a parent who checks the videos their young child watches and pays attention to the child's viewing habits. |
| 2 | 次は、友達とのやり取りにSNSが身近な高校生。子どもの利用をめぐる話題を、使う側から語る。 | Next is a high school student for whom social media is a familiar way to stay in touch with friends. He talks about the issue of children's use from the user's side. / Next, a high school student speaks. Social media is a normal way for him to keep in touch with friends. … | B1: …友達との連絡にSNSが身近な高校生。年齢による利用制限の対象になる立場だ。 / ◎E2: …友達との連絡にSNSが身近な高校生だ。年齢による制限の対象になる側から語る。 | B1 Adv: a high school student for whom social media is a familiar way to keep in touch with friends. They are among those subject to age-based restrictions on its use. |
| 3 | 最後は、中学生の子と暮らす親。子どものSNS利用について、家庭で判断する立場から語る。 | Last is a parent who lives with a middle school child. They speak as someone who has to decide at home how their child uses social media. / Last, a parent who lives with a middle school child speaks. They must decide at home… | A1: …中学生の子どもを育て、SNSの使わせ方を判断する立場にいる親だ(**check_intro NG: COPIES_VOICE_BODY_10CHARS**)。 / ◎E2: …中学生の子にSNSを使わせる時期や範囲を判断する立場の親だ。 | B1 Adv: a parent who considers when to let their middle school child start using social media and how much access to allow. |

全候補の生成物は上記JSON。E以外のA/B候補はcheck_intro全OK、例外はsns A1 V3の1件のみ。

## 3. 評価(5軸。○良好 △軽微な懸念 ×不可。推奨◎案)
| 記事・Voice | リアリティ | 自然さ | 経験・立場・主張の整合 | 属性の機械転記なし | 補完は合理的か(不自然な創作なし) | 理由 |
|---|---|---|---|---|---|---|
| redelivery V1 E1 | ○ | ○ | ○ | ○ | ○ | 『宅配ドライバー』(=立場そのもの)を残しつつ『再配達も日々の仕事』と話題との関わりを添えた。本人語りの不在票・持ち戻りと整合。補完は職務の一般的事実 |
| redelivery V2 E2 | ○ | ○ | ○ | ○ | ○ | 『受取人』+『家にいられる時間に合わせ』は本人語り(在宅できる日時を選んで時間指定)と一致。情報源にない出来事なし |
| redelivery V3 E2 | ○ | ○ | ○ | ○ | ○ | 現行とほぼ同情報。『受け取り方を工夫』で話題との関わりが明確 |
| sns V1 E2 | ○ | △ | ○ | ○ | ○ | 『動画の利用を見守り、使い方を決める立場』は本人語り(刺激の強い動画・課金)と整合。『使い方を決める』はやや硬い |
| sns V2 E2 | ○ | ○ | ○ | ○ | ○ | 『年齢による制限の対象になる側』=sheet contact_pointそのまま。主張(禁止反対)を先取りしない |
| sns V3 E2 | ○ | ○ | ○ | ○ | ○ | 『時期や範囲を判断する立場』は本人語りの論点と一致。『親』は立場に必要なので残るのは妥当 |
| 非推奨: redelivery A1 V1 | △ | △ | ○ | ○ | ○ | **A(原則のみ)は属性を削りすぎる**: 『荷物を届けて回る仕事をしている人。配達する側の声だ』と宅配ドライバーを省略し現行より曖昧(英訳も`someone whose job is…`)。属性=立場の記事で過剰削除。「〜の声だ」の型も機械的 |
| 非推奨: sns A1 V3 | ○ | ○ | ○ | ○ | ○ | 内容は良いが本人語りと10字一致で既存`check_intro` NG(surname MINと同様の相性問題) |

観察:
1. **時期語・きっかけの創作は今回の2記事では0件**(surnameで再発した『結婚を機に』型は、属性の経緯が焦点でない記事では出なかった)。補完は『再配達も仕事のひとつ』『家にいられる時間に合わせ』程度で、合理的補完の範囲。
2. 現行紹介は両記事とも既に立場中心で、一般化は「改善」より「同等維持+話題との関わりの明確化」。リスクはA(原則のみ)の過剰削除で、E(原則+話題との関わり行B+『属性がそのまま立場のときは属性名を使う』節)で解消。
3. EN previewはJAに性別手がかりがないとAdv/Stdとも`someone … they`となり、現行英訳の`she and her husband`/`He`(本文を見る英訳stageでは保たれる)より情報が減る。紹介行単独の英語化はpreviewの限界で、実運用の英訳は記事全体を見る(`stage_translate`)ため問題は小さい見込みだが、正式採用時に1記事で確認要。
4. `check_intro`はA/B/E全候補で通過(sns A1 V3のみ10字一致NG)。補助Gate(luna)は未実行。

## 4. 3記事総括(surname V1を含む)
| 記事 | 属性と立場 | 現行の問題 | 一般化の効果 | 判定 |
|---|---|---|---|---|
| surname | 乖離(父親だが立場は『妻の姓を選んだ人』) | 属性が主名詞→英訳で誤読 | 立場が主になり誤読解消。ただし時期語『結婚して』をモデルが毎回創作(RESULT_01) | 有効(V1限定)、創作は人手除去 |
| redelivery_fee | 一致(職業・受取人) | なし | A=過剰削除で劣化、B/E=同等以上(話題との関わりが明確)。創作なし | E/Bなら有効、Aは不可 |
| sns_age_limit | 中間(親/当事者) | なし | 同等維持。『親』は立場に必要なので残る。創作なし | 有効(同等) |

結論: 一般化原則は「属性が立場と乖離する記事を直す」「一致/中間の記事を壊さない」の両方を、**B(contact_point行)+E節**で満たす。A単体は一致型で劣化するため採用不可。時期語の創作は乖離型(surname)のみで再発(決定論検査は不採用方針のため、Lead/紹介補助Gateまたは人手/HR確認で担保)。

## 5. 改善案(1回のみ実施済み)
課題=Aの過剰削除(redelivery V1)。原因=原則が『属性を機械的に使わない』に偏り、属性=立場の場合の例外が曖昧。Prompt差分E(`er121_family_y_intro_trial2_01.py` `CLAUSE_E`、`prompt_E.txt`): 「職業・当事者の立場など、属性の名前そのものが今回の話題での立場を表す場合(例: 宅配ドライバー、高校生)は、その名前を省かず使い、続けて話題との関わりを添える。属性が話題での立場を表さない場合だけ、属性名を主にしない。」→両記事2sampleでV1『宅配ドライバー』が復活、check_intro全OK(再現2/2)。改善案はこれ以上繰り返さない。

## 6. Trial Closeout案
- **判定案: VALIDATED(可)**。理由: 属性乖離型(surname)・一致型(redelivery)・中間型(sns)の3型で、B+E構成が立場の明確化と非劣化を満たし、創作は乖離型の時期語に限られ(既知・対処案あり)、check_intro通過、Production未配線。限界=サンプルは3記事・各2sample、補助Gate未実行、EN性別情報はpreview限界。
- 正式採用時の実装範囲(ユーザー採用後・別委任):
  (a) `er121_prompts/persona_intro_01.txt`の【書き方】へ原則bullet+CLAUSE_Eを追加(Prompt sha更新)。
  (b) `er121_family_y_text_core_01.py:1650 person_block`へ`話題との関わり`(contact_point_ja)行を追加(現状はDEV内`person_block_b`が文字列置換)。全Theme Packageにcontact_point_jaがあることの確認要(redelivery/sns/surname=有)。
  (c) surname型(乖離)向けに`intro_checks.role_patterns`を立場語へ更新。
  (d) 時期・きっかけの創作は決定論検査にせず、Lead/紹介補助Gate(luna)のプロンプトまたはHR確認で扱う案を別途設計(ユーザー決定=時期語の機械NGは不採用)。
  (e) 回帰test・DefaultOffIsolation(11-7)。
  影響=紹介生成1call/記事のPrompt入力が約+200token・出力不変、費用増ほぼ0(¥0.1未満/記事)。英訳は記事全体を見るため性別情報は維持される見込み(要1記事確認)。
- 採用しない場合の現状: Production Promptは無変更で、属性が立場と乖離するTheme Package(surname型)ではrole_jaの属性が紹介の主名詞になり得る。当面は(a)Theme Package作成時にrole_jaを立場中心に書く、(b)個別是正(surname V1=04B)で運用。
- 一般化方式の正式採用=ユーザー判断(UDR新規。Fableが提示。本Workerは未提示)。

## 7. 費用
16 call(JA 12[A2+B2+E2×2記事]+EN 4[Adv/Std×2記事])、tokens 入力26,491/出力30,722(推論含む)。gpt-6.1-sol単価(input $2/M, output $10/M、`er006_model_routing_pricing_coverage_test_01.py:97-99`)で約**$0.36≒¥54〜58(為替150〜160円)**。**委任Cap¥30および¥40(理由記録で継続可)を超過**(Cap超過をFableへ報告)。原因=effort highの推論tokenが出力の大半を占めることをcall前に見積もらなかった(surname実績1call≈¥4から、16call≈¥60と見積もるべきだった)ことと、A/Bを両記事2sample・EN全候補・E案まで実施したこと。内訳: JA(A/B)$0.17、EN preview $0.10、E案$0.09。以後API 0。
