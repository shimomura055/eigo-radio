# PROVENANCE_01 (委任_18 F: 実在意見ベースR0の出典対応表。内部記録・リスナーには見せない)

対象: `er110_output/family_y_opinion_based_01/sns_age_limit/run_01/article_ja.md`(確定稿)。書式は`PROVENANCE_TEMPLATE_01.md`+「TBSのみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_01.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全24文を読んで付けた列を結合。API 0)。
手順: (1)luna(gpt-6-luna)が各文に許可リストのIDまたは補った表現の種別を付番 → (2)機械照合(許可リスト外ID・IDも補いもない・出来事らしい文でE-IDなし[仮定形は除く]・出来事主張でIDなし=UNMAPPED)→ (3)UNMAPPEDのVoiceだけ各1回再生成 → (4)agentが全文を目視。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice **2文**、Another Voice **0文**、A Third Voice **1文**(計3文)。各Voiceの再生成は**1回まで**(One Voice 1回、A Third Voice 1回、Another Voice 0回)=計2回。再生成後の最終稿の機械照合UNMAPPEDは **0文**。
- 注記: 初回の3文は、agentの事後確認では出来事の捏造というより、lunaが「年代・立場の手がかり」や既出の経験を取りこぼした**偽陽性の疑いが強い**(例: 「わたしたち中学生にも…目安がほしい」)。ただし規則(UNMAPPEDは再生成)に従い再生成し、初回稿は`state.json`に保存。
- agent目視で付けた**要注意(UNMAPPEDではないが意味・文脈のずれの可能性)**: **6件**(下表の備考。TBSのみ根拠の4文は別枠で§3)。出来事・人物・会話の捏造は**0件**。
- 経験(出来事)として本文に出た内容はすべて経験欄(ONE_a/ONE_d)に由来。A Third Voiceには経験欄に出来事が無く、本文にも出来事は出ていない(意見・仮定のみ)。
- 判定の限界: lunaの付番はIDの付け間違いがある(例: Another Voice第2文のID)。機械照合は『許可リスト内か』を見るだけで、IDの正しさまでは保証しない。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 主張・経験・感情の要約 | 種別 | 経験欄ID(根拠の声ID) | 根拠URL | 編集・一般化 | 補った表現 | 機械判定 | agent判定 | 備考(要注意・TBSのみ) |
|---|---|---|---|---|---|---|---|---|---|---|
| One Voice | 第1文 | 子どもが刺激の強いものや課金を興味のままに選んでしまったことがある | 経験 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 子→「うちの小さい子」(役割の一般化) | 「うちの」(口調) / luna種別:年代・立場の手がかり | OK | OK | — |
| One Voice | 第2文 | 話をすると、じゃあやらない、となることも多い | 経験 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 括弧なしで地の文に | なし / luna種別:なし | OK | OK | — |
| One Voice | 第3文 | 年齢に応じた使い方の決まりがあってほしい | 主張 | (IDなし) |  | Personaの芯(ONE_e/ONE_fに基づく編集)。出来事なし | 「親が話すだけじゃなくて」(つなぎ) / luna種別:仮定・意見の言い換え | 補った表現のみ | OK(要注意) | 意味のずれ小: 出典ONE_aは『話せば止まることも多い』とあり、『話すだけじゃなくて』は出典の意図とずれる言い回し |
| One Voice | 第4文 | はっきりしているほうが安心できる | 感情 | (IDなし) |  | Personaの芯。出来事なし | 感情の言い方 / luna種別:感情の言い方 | 補った表現のみ | 補った表現のみ | — |
| One Voice | 第5文 | 静かにしてほしい長い移動の時に動画を見てくれると助かる | 経験 | ONE_d(TBS-07) | https://newsdig.tbs.co.jp/articles/-/2618789 | 「電車」→「長い移動」(一般化) | 「なんだ」(口調) / luna種別:聞き手への呼びかけ・つなぎ | OK | OK | TBSのみ根拠(TBS-07) |
| One Voice | 第6文 | 助かっている(正直な認め) | 感情 | ONE_d(TBS-07) | https://newsdig.tbs.co.jp/articles/-/2618789 | TBS-07の「正直助かる」 | なし / luna種別:なし | OK | OK | TBSのみ根拠(TBS-07) |
| One Voice | 第7文 | 制限がかかると親もしんどい時がある | 経験 | ONE_d(TBS-07) | https://newsdig.tbs.co.jp/articles/-/2618789 | そのまま(親→私) | なし / luna種別:なし | OK | OK | TBSのみ根拠(TBS-07) |
| One Voice | 第8文 | 子どものために制限してほしいが、自分の都合では見ていてほしい時もある | 矛盾 | ONE_d(TBS-07); ONE_e(MR-T015-10) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/874f031c-0680-4a45-b2ca-02a611c86aec; https://newsdig.tbs.co.jp/articles/-/2618789 | 前半=ONE_e/f(制限を望む)、後半=TBS-07(自分の都合) | 「いや、」(口調) / luna種別:口調・言い回し,仮定・意見の言い換え | OK | OK | 後半はTBSのみ根拠(TBS-07) |
| One Voice | 第9文 | 小さいうちは、はっきりした決まりがあってほしい | 主張 | (IDなし) |  | Personaの芯の再掲 | なし / luna種別:年代・立場の手がかり,仮定・意見の言い換え | 補った表現のみ | 補った表現のみ | — |
| Another Voice | 第1文 | 投稿まで親に見られるのは少し嫌 | 感情 | TWO_a(MR-T010-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 「少し嫌」→「正直ちょっと嫌だ」 | 「正直ちょっと」(口調) / luna種別:口調・言い回し | OK | OK | — |
| Another Voice | 第2文 | 友達との連絡にSNSを使う | 事情 | TWO_e(MR-T017-04); TWO_f(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/18f89fb2-f867-4ba5-9d2c-c5eef97343df; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | 「子ども同士」→「友達」。高校生の手がかり | 「高校生の僕には」(手がかり) / luna種別:なし | OK | OK | luna付番はTWO_e,TWO_fだが、agentはTWO_fのみと判断(TWO_eは模試) |
| Another Voice | 第3文 | 年齢で縛られるのも、アカウントを持てないのも困る | 意見 | TWO_e(MR-T017-04); TWO_f(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/18f89fb2-f867-4ba5-9d2c-c5eef97343df; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | TWO_f(年齢制限に反対)+TWO_e(作れないと困る)の合成 | なし / luna種別:なし | OK | OK | — |
| Another Voice | 第4文 | 見られるとSNSのよさが消えるが、悪口や脅しの時は大人につなげたい | 矛盾 | TWO_a(MR-T010-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 意味・立場は元の回答のまま | なし / luna種別:なし | OK | OK | — |
| Another Voice | 第5文 | 全部見せるのは違う | 意見 | TWO_a(MR-T010-02); TWO_b(MR-T033-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d3e75d20-6379-47ad-964d-f210777ba098 | TWO_b(知られたくない内容も)の軽い一般化 | 「やっぱり」(口調) / luna種別:なし | OK | OK | — |
| Another Voice | 第6文 | 安全フィルターなど別のやり方がいい | 意見 | TWO_f(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | TWO_fをそのまま | なし / luna種別:なし | OK | OK(要注意) | 文脈の移し替え: 元は『年齢制限の代わりの対策』で、ここでは『見守り(全部見せる)の代わり』として使われている |
| Another Voice | 第7文 | やめさせるより、困った時に頼れるよう細かく調整してほしい | 主張 | TWO_a(MR-T010-02); TWO_f(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | TWO_a(微調整が必要) | なし / luna種別:なし | OK | OK | — |
| A Third Voice | 第1文 | 判断できるようになってからアカウントを作れるように | 主張 | THREE_d(MR-T014-13) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/e8c7eb50-9bdd-487b-bfe5-a53e61d09e30 | THREE_dをほぼそのまま | なし / luna種別:なし | OK | OK | — |
| A Third Voice | 第2文 | 小学生や中学生にはDMのような機能は不安 | 意見 | THREE_c(MR-T158-01) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d0645b15-78ee-4982-a4b7-4f1d825ac155 | THREE_c(中学生本人の声) | 「わたしたち中学生や小学生には」 / luna種別:年代・立場の手がかり | OK | OK(要注意) | 「わたしたち…小学生」は V3が中学生のため言い過ぎ(出典は『小中学生だと不安』) |
| A Third Voice | 第3文 | 高校生くらいになればある程度は自分で考えて使える | 意見 | THREE_c(MR-T158-01) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d0645b15-78ee-4982-a4b7-4f1d825ac155 | THREE_c | なし / luna種別:なし | OK | OK | — |
| A Third Voice | 第4文 | 使っていい機能は年齢で分けたほうがいい | 主張 | THREE_c(MR-T158-01) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d0645b15-78ee-4982-a4b7-4f1d825ac155 | THREE_cの理由から導く解釈(topic_title/stanceは不使用) | 「だから」(つなぎ) / luna種別:仮定・意見の言い換え,聞き手への呼びかけ・つなぎ | OK | OK(要注意) | 結論はagentによる解釈。本文は機能の例示と理由のみ |
| A Third Voice | 第5文 | アカウントを作ることと、どの機能でも使えることは同じにしなくていい | 意見 | THREE_c(MR-T158-01); THREE_d(MR-T014-13) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d0645b15-78ee-4982-a4b7-4f1d825ac155; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/e8c7eb50-9bdd-487b-bfe5-a53e61d09e30 | THREE_c(機能の段階)とTHREE_d(作成の条件)の組合せで作られた区別 | 仮定・意見の言い換え / luna種別:仮定・意見の言い換え | OK | OK(要注意) | 出典に直接ない区別を新しく立てている。出来事ではないがUNMAPPEDではない境界例 |
| A Third Voice | 第6文 | 自分で決められないうちから何でもできるようにはしてほしくない | 意見 | THREE_c(MR-T158-01); THREE_d(MR-T014-13) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d0645b15-78ee-4982-a4b7-4f1d825ac155; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/e8c7eb50-9bdd-487b-bfe5-a53e61d09e30 | THREE_c/dの言い換え | なし / luna種別:仮定・意見の言い換え | OK | OK | — |
| A Third Voice | 第7文 | 良し悪しを考えられることが先 | 意見 | THREE_d(MR-T014-13) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/e8c7eb50-9bdd-487b-bfe5-a53e61d09e30 | THREE_dの言い換え | なし / luna種別:なし | OK | OK | — |
| A Third Voice | 第8文 | はっきり決めておくべき | 主張 | THREE_c(MR-T158-01); THREE_d(MR-T014-13) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d0645b15-78ee-4982-a4b7-4f1d825ac155; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/e8c7eb50-9bdd-487b-bfe5-a53e61d09e30 | THREE_c/d(共通の目安への言及は薄い。THREE_g由来の『最低ライン』は出ていない) | なし / luna種別:仮定・意見の言い換え,聞き手への呼びかけ・つなぎ | OK | OK | — |

## 3. TBSのみが根拠の文(公開前の権利確認の対象。OF-Y6-10)
| Voice | 位置 | 文 | 備考 |
|---|---|---|---|
| One Voice | 第5文 | ただ、長い移動で静かにしてほしい時、動画を見てくれると助かるんだ。 | TBSのみ根拠(TBS-07) |
| One Voice | 第6文 | 正直、助かっている。 | TBSのみ根拠(TBS-07) |
| One Voice | 第7文 | 制限がかかると、私もしんどい時がある。 | TBSのみ根拠(TBS-07) |
| One Voice | 第8文 | 子どものために制限してほしいと思っているけど、いや、私の都合では見ていてほしい時もある。 | 後半はTBSのみ根拠(TBS-07) |

- 上記以外の文は、みらい議会(CC BY 4.0)の本人回答、またはPersonaの芯・口調(補った表現)に対応する。
- TBS-10(番組出演者の発言)は、本稿のいかなる文の唯一の根拠にもしていない(反動のイライラはMR-T015-06が根拠)。TBS-02は経験欄(TWO_h)にあったが本文に使われなかった。
- 公開する場合: 上記TBS-07由来の4文(第5・6・7文と第8文の後半)について、TBS NEWS DIGの許諾要否を確認するか、MR由来の内容に差し替える(差し替えはユーザー判断の範囲外=Phase 2の対象外)。

## 4. 本稿に使われた出典IDの集計(経験欄ID→声ID)
- One Voice: ONE_a=MR-T010-05, ONE_b=MR-T015-06, ONE_c=MR-T003-09, ONE_d=TBS-07(TBSのみ), ONE_e=MR-T015-10, ONE_f=MR-T008-02
- Another Voice: TWO_a=MR-T010-02, TWO_b=MR-T033-02, TWO_c=MR-T041-03, TWO_d=MR-T019-03, TWO_e=MR-T017-04, TWO_f=MR-T101-02, TWO_g=MR-T010-17, TWO_h=TBS-02(TBSのみ)
- A Third Voice: THREE_a=MR-T157-01, THREE_b=MR-T026-01, THREE_c=MR-T158-01, THREE_d=MR-T014-13, THREE_e=MR-T049-02, THREE_f=MR-T058-01, THREE_g=MR-T020-05
