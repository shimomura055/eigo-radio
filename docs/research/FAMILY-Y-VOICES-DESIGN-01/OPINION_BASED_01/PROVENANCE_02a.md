# PROVENANCE_02a (委任_21: 改善R0 run_02a の出典対応表。内部記録・リスナーには見せない)

対象: `er110_output/family_y_opinion_based_02/sns_age_limit/run_02a/article_ja.md`(確定稿)。書式は`PROVENANCE_TEMPLATE_01.md`+「TBSのみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_02.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全22文を読んで付けた列を結合。API 0)。
手順は`PROVENANCE_01.md`と同じ(luna付番 → 機械照合 → UNMAPPEDのVoiceだけ各1回再生成 → agent目視)。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice 0文 / Another Voice 0文 / A Third Voice 1文。UNMAPPED再生成: A Third Voice 1回(各Voice1回まで)。
- **再生成後の最終稿の機械照合UNMAPPED(final_map)**: One Voice 0文 / Another Voice 1文 / A Third Voice 3文。規則どおり再生成は各Voice1回までのため、最終稿のUNMAPPEDは記録のみ(再生成の追加・手作業修正はしていない)。
- agent目視: 機械判定の**偽陽性**と判断した文 **3件**(Personaの立場の手がかり、または経験欄の項目への対応をlunaが取りこぼした文)。**要注意**(意味・文脈のずれ、出典にない補い)は **6件**(下表の備考)。出来事・人物・会話の捏造は**0件**。
- 判定の限界: lunaの付番はIDの付け間違い・取りこぼしがある。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 文 | 経験欄ID(根拠の声ID) | 根拠URL | 補った表現(luna種別) | 機械判定 | agent判定 | 備考(要注意・偽陽性・TBSのみ) |
|---|---|---|---|---|---|---|---|---|
| One Voice | 第1文 | 小さい子どもが、刺激の強いものや課金につながるものを、興味のままに選んでいた。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 年代・立場の手がかり | OK | OK | — |
| One Voice | 第2文 | 話すと、じゃあやらない、となることも多い。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | なし | OK | OK | — |
| One Voice | 第3文 | でも、本人には危ないものだと分かっていなかったのかな、と思う。 | ONE_f(MR-T008-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e | 仮定・意見の言い換え | OK | OK | ONE_fの『危険を危険と気づかない』を、子の様子への推測(〜のかな)として言い換え |
| One Voice | 第4文 | 私が話せば大丈夫、とも言い切れない。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 仮定・意見の言い換え | OK | OK(要注意) | ONE_a(話すと止まることも多い)と逆向きの留保『話せば大丈夫とも言い切れない』を足している。出典に直接ない解釈 |
| One Voice | 第5文 | SNSは、動画やメッセージのアプリも含めて、年齢ごとに使える機能をはっきり決めてほしい。 | (IDなし) |  | 仮定・意見の言い換え | 補った表現のみ | 補った表現のみ | Personaの芯(年齢に応じたはっきりした決まり)。『動画やメッセージのアプリも含めて』は世界設定の前提 |
| One Voice | 第6文 | そのたびに私が迷わずに済むように。 | (IDなし) |  | 仮定・意見の言い換え | 補った表現のみ | OK(要注意) | 『そのたびに私が迷わずに済むように』は出典にない気持ちの補い(ONE_cの見守り設定の面倒の言い換えに近いが、直接の対応はない) |
| One Voice | 第7文 | 成長に合わせて広げる形なら、と思う。 | (IDなし) |  | 仮定・意見の言い換え | 補った表現のみ | 出典外の意見(要注意) | 『成長に合わせて広げる形』は世界設定の『段階的な制限』の定義由来で、V1の経験欄にない(V3の主張に近い) |
| One Voice | 第8文 | ただ、長い移動で静かにしてほしい時は、子どもが見ていてくれると正直助かる。 | ONE_d(TBS-07) | https://newsdig.tbs.co.jp/articles/-/2618789 | なし | OK | OK | TBSのみ根拠(TBS-07)。V1のTBS-07由来はこの1文のみ |
| One Voice | 第9文 | アカウントを持つこと自体を禁止するとなると、守りたいから賛成、とすぐには言えない自分もいる。 | (IDなし) |  | 感情の言い方,仮定・意見の言い換え | 補った表現のみ | OK(要注意) | 『守りたいから賛成、とすぐには言えない自分もいる』は、TBS-07の『助かる』とは別の自己の迷いの補い(出典にない自己告白に近い)。『アカウントを持つこと自体を禁止』は世界設定の区別定義由来 |
| Another Voice | 第1文 | 年齢だけでSNSを使えなくなるのは、僕は嫌だ。 | TWO_a(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | 感情の言い方 | OK | OK | — |
| Another Voice | 第2文 | 高校生になってもアカウントを持てないとなると、友達と連絡を取るのに困る。 | (IDなし) |  | なし | UNMAPPED | OK(機械判定は偽陽性) | TWO_e(高校生でアカウントを作れないと困る)+TWO_a(子ども同士の連絡)に対応。lunaが付番を取りこぼした |
| Another Voice | 第3文 | だから、アカウントを作ることまで禁止するのには反対だ。 | TWO_a(MR-T101-02); TWO_b(MR-T005-06) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 聞き手への呼びかけ・つなぎ | OK | OK | — |
| Another Voice | 第4文 | 使うかどうかも、どう使うかも自分で考えたいし、年齢で決められると、僕が考えるところまで取り上げられた気がするんだけど、じゃあ全部自分で何とかできるかというと、悪口や脅しを受けた時には、すぐ大人に頼りたいとも思う。 | TWO_c(MR-T082-02); TWO_f(MR-T010-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/a7af865c-082c-473f-8de6-2f4edbcde02a; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 感情の言い方,仮定・意見の言い換え,聞き手への呼びかけ・つなぎ | OK | OK | 葛藤(自分で判断したい↔悪口や脅しの時は大人に頼りたい)は1か所。MR-T010-02の核心。監視への言及なし |
| Another Voice | 第5文 | そこは、うまく言えない。 | (IDなし) |  | 口調・言い回し | 補った表現のみ | 補った表現のみ | 口調 |
| Another Voice | 第6文 | 危ないものに触れないためのフィルターをかけるとか、使えなくする前に、使いながら危なくならないやり方に変えてほしい。 | TWO_a(MR-T101-02); TWO_b(MR-T005-06) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 仮定・意見の言い換え | OK | OK | TWO_a(安全フィルターなど別の対策) |
| A Third Voice | 第1文 | 中学生の子を育てているので、いつ、どこまでSNSを使わせるかは、わたしが考えないといけない。 | (IDなし) |  | なし | UNMAPPED | OK(機械判定は偽陽性) | 人物設定(中学生の子を育てている親=Sheetのrole)の描写。出典の経験ではなく立場の手がかり |
| A Third Voice | 第2文 | 年齢は大まかな目安にはなるけれど、それだけで、うちの子はもう大丈夫だとは思えない。 | (IDなし) |  | なし | UNMAPPED | OK(要注意) | THREE_a(年齢は大凡の目安)に対応。『うちの子はもう大丈夫だとは思えない』は仮定の外での『うちの子』(Sheetの指示は仮定の中のみ)。出来事ではないが境界 |
| A Third Voice | 第3文 | できれば、自分で何を判断できるかに合わせて、使える機能を少しずつ広げてやりたい。 | THREE_b(MR-T003-03) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34 | 仮定・意見の言い換え | OK | OK | THREE_b |
| A Third Voice | 第4文 | もしうちの子が、禁止されている間は何も使わず、使っていい年齢になった途端に何でも使えるようになったら、わたしは心配だ。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 感情の言い方,仮定・意見の言い換え | OK | OK | THREE_dを仮定(もし〜)で語る |
| A Third Voice | 第5文 | 触ったこともないのに、危ない時に自分を守れるだろうとは思えないから。 | (IDなし) |  | なし | UNMAPPED | OK(機械判定は偽陽性) | THREE_dの言い換え。『触ったこともない』は『何の準備もしていなかったら』の言い換えだが、事実の追加に近い言い方 |
| A Third Voice | 第6文 | だから、使える範囲には段階を設けて、その中で覚えていける形がいい。 | THREE_b(MR-T003-03); THREE_c(MR-T008-12) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e | 仮定・意見の言い換え | OK | OK | THREE_b/c |
| A Third Voice | 第7文 | 海に出る前に泳ぐ練習をするように、うちの子にも、少しずつ使い方を覚える時間が必要なんだと思う。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 仮定・意見の言い換え | OK | OK(要注意) | THREE_dのたとえ(泳ぐ練習)。『うちの子にも…時間が必要』は仮定の外の言い方 |

## 3. TBSのみが根拠の文(公開前の権利確認の対象。OF-Y6-10)
| Voice | 位置 | 文 |
|---|---|---|
| One Voice | 第8文 | ただ、長い移動で静かにしてほしい時は、子どもが見ていてくれると正直助かる。 |

- 上記以外の文は、みらい議会(CC BY 4.0)の本人回答、Personaの立場・口調・芯(補った表現)、または世界設定の定義に対応する。TBS-10・TBS-02は本稿のいかなる文の根拠にもしていない。
