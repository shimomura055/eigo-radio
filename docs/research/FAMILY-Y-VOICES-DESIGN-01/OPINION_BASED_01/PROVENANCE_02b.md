# PROVENANCE_02b (委任_21: 改善R0 run_02b の出典対応表。内部記録・リスナーには見せない)

対象: `er110_output/family_y_opinion_based_02/sns_age_limit/run_02b/article_ja.md`(確定稿)。書式は`PROVENANCE_TEMPLATE_01.md`+「TBSのみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_02.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全22文を読んで付けた列を結合。API 0)。
手順は`PROVENANCE_01.md`と同じ(luna付番 → 機械照合 → UNMAPPEDのVoiceだけ各1回再生成 → agent目視)。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice 0文 / Another Voice 0文 / A Third Voice 1文。UNMAPPED再生成: A Third Voice 1回(各Voice1回まで)。
- **再生成後の最終稿の機械照合UNMAPPED(final_map)**: One Voice 2文 / Another Voice 0文 / A Third Voice 2文。規則どおり再生成は各Voice1回までのため、最終稿のUNMAPPEDは記録のみ(再生成の追加・手作業修正はしていない)。
- agent目視: 機械判定の**偽陽性**と判断した文 **3件**(Personaの立場の手がかり、または経験欄の項目への対応をlunaが取りこぼした文)。**要注意**(意味・文脈のずれ、出典にない補い)は **4件**(下表の備考)。出来事・人物・会話の捏造は**0件**。
- 判定の限界: lunaの付番はIDの付け間違い・取りこぼしがある。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 文 | 経験欄ID(根拠の声ID) | 根拠URL | 補った表現(luna種別) | 機械判定 | agent判定 | 備考(要注意・偽陽性・TBSのみ) |
|---|---|---|---|---|---|---|---|---|
| One Voice | 第1文 | まだ小さいうちの子が、刺激の強い動画や、課金につながるものを、興味のままに選んでいた。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 年代・立場の手がかり | OK | OK | — |
| One Voice | 第2文 | 話をすると、じゃあやらない、となることも多い。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | なし | OK | OK | — |
| One Voice | 第3文 | でも、話せば済む、ということでもない気がする。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 仮定・意見の言い換え | OK | OK(要注意) | ONE_aと逆向きの留保『話せば済むということでもない』を足している。出典に直接ない解釈 |
| One Voice | 第4文 | 子どもが危ないと気づけなければ、助けてとも言えないかもしれない。 | ONE_f(MR-T008-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e | 仮定・意見の言い換え | OK | OK | ONE_f |
| One Voice | 第5文 | だから私は、SNSには年齢ごとに、ここまで使っていいという、はっきりした決まりがほしい。 | (IDなし) |  | なし | UNMAPPED | OK(機械判定は偽陽性) | Personaの芯(年齢に応じたはっきりした決まり)。出典IDのない主張・望みの文 |
| One Voice | 第6文 | アカウントを持たせないことと、使える機能を決めることは、分けて考えたい。 | (IDなし) |  | なし | UNMAPPED | 出典外の意見(要注意) | 『アカウントを持たせないことと、使える機能を決めることは、分けて考えたい』は世界設定の区別定義由来で、V1の経験欄にない意見。lunaのUNMAPPEDは妥当 |
| One Voice | 第7文 | ただ、長い移動で静かにしてほしい時は、動画を見てくれると私も助かる。 | ONE_d(TBS-07) | https://newsdig.tbs.co.jp/articles/-/2618789 | なし | OK | OK | TBSのみ根拠(TBS-07)。V1のTBS-07由来の文はこの1文のみ(次の文のluna付番ONE_dはAgent目視ではTBS由来でない) |
| One Voice | 第8文 | 守りたいのは本当なんだけど、どこまで使わせないのかとなると、まだ言葉がまとまらない。 | ONE_d(TBS-07); ONE_f(MR-T008-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e; https://newsdig.tbs.co.jp/articles/-/2618789 | 感情の言い方,仮定・意見の言い換え | OK | OK(要注意) | 『守りたいのは本当』(Personaの建前)+『まだ言葉がまとまらない』(葛藤を抱えた結び=補った表現)。lunaはONE_d/ONE_fと付番したが、TBS-07の内容ではない |
| Another Voice | 第1文 | 年齢だけでSNSを使えなくされるのは、僕は嫌だ。 | TWO_a(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | 感情の言い方 | OK | OK | — |
| Another Voice | 第2文 | 高校生の僕には、友達と連絡を取るためにも必要なんだ。 | TWO_a(MR-T101-02); TWO_e(MR-T017-04) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/18f89fb2-f867-4ba5-9d2c-c5eef97343df; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | 年代・立場の手がかり | OK | OK | — |
| Another Voice | 第3文 | アカウントを持つことまで禁止するのは反対だ。 | TWO_a(MR-T101-02); TWO_b(MR-T005-06) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | なし | OK | OK | — |
| Another Voice | 第4文 | 何を使って、どうやり取りするかは自分で考えたいし、何でも大人に決めてもらうのは違う気がするけど、悪口や脅しに遭った時には自分だけで何とかできるとも思えなくて、すぐ大人に頼れるようにはしておきたい。 | TWO_c(MR-T082-02); TWO_f(MR-T010-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/a7af865c-082c-473f-8de6-2f4edbcde02a; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | なし | OK | OK | 葛藤(自分で考えたい↔悪口や脅しの時は大人に頼りたい)は1か所。監視への言及なし |
| Another Voice | 第5文 | そこは、うまく言えないけど。 | (IDなし) |  | 口調・言い回し | 補った表現のみ | 補った表現のみ | 口調 |
| Another Voice | 第6文 | 使うなと決める前に、僕らが何に使っているかも考えてほしい。 | TWO_g(MR-T033-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/d3e75d20-6379-47ad-964d-f210777ba098 | なし | OK | OK | TWO_g(利用する側のことを考えないルール)の言い換え |
| Another Voice | 第7文 | 安全フィルターをかけるとか、使えるままで危ない目に遭いにくくするやり方に変えてほしい。 | TWO_a(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | なし | OK | OK | TWO_a |
| A Third Voice | 第1文 | 中学生の子にSNSをどこまで使わせるか、親として考えると、わたしは年齢だけで区切るのは違う気がする。 | (IDなし) |  | 年代・立場の手がかり | UNMAPPED | OK(機械判定は偽陽性) | 人物設定(中学生の子を持つ親)の描写。出典の経験ではなく立場の手がかり |
| A Third Voice | 第2文 | できれば、その子の力に合わせて、使える機能や範囲を少しずつ広げていきたい。 | THREE_b(MR-T003-03) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34 | なし | OK | OK | THREE_b |
| A Third Voice | 第3文 | アカウントを持つことまで禁止するより、使いながら身を守る準備ができるように、段階を分けるのがいいと思う。 | THREE_c(MR-T008-12); THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e | 仮定・意見の言い換え | OK | OK(要注意) | THREE_c/d。『アカウントを持つことまで禁止するより』は世界設定の区別定義由来 |
| A Third Voice | 第4文 | 海に出る前には、泳ぐ練習が要るのと同じなんだ。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | なし | OK | OK | THREE_dのたとえ |
| A Third Voice | 第5文 | もし、うちの子が禁止されていた年齢を過ぎて、何の準備もなくSNSを使い始めるなら、事故につながらないか心配になる。 | (IDなし) |  | 感情の言い方 | UNMAPPED | OK(機械判定は偽陽性) | THREE_d(禁止の年齢を過ぎて準備なしに触れると事故)を、仮定(もし〜)+『うちの子』(細部なし)で語る。Sheetの指示どおり |
| A Third Voice | 第6文 | 使える年齢になったことと、自分で身を守れることは、同じではないと思う。 | THREE_a(MR-T032-03); THREE_e(MR-T027-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/223214d4-ccb3-44a3-994d-864194776724; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/81be6f63-757a-4889-a6a1-560546f3f5fa | 仮定・意見の言い換え | OK | OK | THREE_a/d |
| A Third Voice | 第7文 | まだ泳ぐ練習をしていない子を、急に海へ送り出すようで、落ち着かないんだ。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 感情の言い方 | OK | OK | THREE_dのたとえ(心配の像)。結びの型=像 |

## 3. TBSのみが根拠の文(公開前の権利確認の対象。OF-Y6-10)
| Voice | 位置 | 文 |
|---|---|---|
| One Voice | 第7文 | ただ、長い移動で静かにしてほしい時は、動画を見てくれると私も助かる。 |

- 上記以外の文は、みらい議会(CC BY 4.0)の本人回答、Personaの立場・口調・芯(補った表現)、または世界設定の定義に対応する。TBS-10・TBS-02は本稿のいかなる文の根拠にもしていない。
