# PROVENANCE_03 (委任_22: 是正Trial run_03 の出典対応表。内部記録・リスナーには見せない)

対象: `er110_output/family_y_opinion_based_02/sns_age_limit/run_03/article_ja.md`(確定稿)。書式は`PROVENANCE_TEMPLATE_01.md`+「TBSのみが根拠の文」欄+agent目視判定。生成: `scripts/build_provenance_03.py`(runの`state.json`のluna付番+機械照合の結果と、agentが全22文を読んで付けた列を結合。API 0)。
手順は`PROVENANCE_01.md`と同じ(luna付番 → 機械照合 → UNMAPPEDのVoiceだけ各1回再生成 → agent目視)。**手作業での本文修正は0**。

## 1. 件数
- 初回生成の機械照合UNMAPPED: One Voice 0文 / Another Voice 1文 / A Third Voice 2文。UNMAPPED再生成: Another Voice 1回, A Third Voice 1回(各Voice1回まで)。
- **再生成後の最終稿の機械照合UNMAPPED(final_map)**: One Voice 0文 / Another Voice 0文 / A Third Voice 0文。規則どおり再生成は各Voice1回までのため、最終稿のUNMAPPEDは記録のみ(再生成の追加・手作業修正はしていない)。
- agent目視: 機械判定の**偽陽性**と判断した文 **0件**(Personaの立場の手がかり、または経験欄の項目への対応をlunaが取りこぼした文)。**要注意**(意味・文脈のずれ、出典にない補い)は **5件**(下表の備考)。出来事・人物・会話の捏造は**0件**。
- **世界設定の定義由来の出典外意見: 0件**(V1に『段階的な制限』『アカウント禁止と機能制限の区別』に当たる文なし。V1第6文は経験欄ONE_c、第8文はSheetの矛盾欄に対応)。**Gate(Leakage判定)は費用が累計22円を超えたため`SKIPPED_BUDGET`で未実行**(01から続く歯止め)。
- 判定の限界: lunaの付番はIDの付け間違い・取りこぼしがある。IDの正しさはagent目視で補ったが、**1名(1agent)の目視であり、独立した第二者の確認ではない**。

## 2. 対応表(1行=1文)
| Voice | 位置 | 文 | 経験欄ID(根拠の声ID) | 根拠URL | 補った表現(luna種別) | 機械判定 | agent判定 | 備考(要注意・偽陽性・TBSのみ) |
|---|---|---|---|---|---|---|---|---|
| One Voice | 第1文 | うちの小さい子が、刺激の強い動画や課金のしくみを、興味のままに選んでいた。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 年代・立場の手がかり | OK | OK | ONE_a。『課金のしくみ』は経験欄の言い方 |
| One Voice | 第2文 | 話すと、じゃあやらないとなることも多い。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | なし | OK | OK | ONE_a |
| One Voice | 第3文 | 分かってくれるんだと思う。 | ONE_a(MR-T010-05) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 仮定・意見の言い換え | OK | OK(要注意) | 『分かってくれるんだと思う』はONE_a(話すと止まることも多い)の解釈の補い(感情・推測の言い換え。出来事の追加ではない) |
| One Voice | 第4文 | でも、自分で危ないと気づけなかったら、私に助けてとも言えないかもしれない。 | ONE_f(MR-T008-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e | 仮定・意見の言い換え | OK | OK | ONE_f(危険に気づけず助けも求められないかも) |
| One Voice | 第5文 | そこが怖い、というか、放っておけない。 | ONE_f(MR-T008-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e | 感情の言い方 | OK | OK | ONE_fへの感情の補い(怖い・放っておけない) |
| One Voice | 第6文 | 動画やメッセージのアプリにも、年齢に応じたはっきりした決まりがほしい。 | (IDなし) |  | 仮定・意見の言い換え | 補った表現のみ | 補った表現のみ | Personaの芯(年齢に応じたはっきりした決まり)。『動画やメッセージのアプリにも』は世界設定の前提。**定義由来の意見ではない**(段階的な制限・禁止と制限の区別の語なし) |
| One Voice | 第7文 | 見守りの設定も、もっと簡単だといい。 | ONE_c(MR-T003-09) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34 | なし | OK | OK | ONE_c(見守りの設定が面倒、もっと簡単に) |
| One Voice | 第8文 | ただ、長い移動で静かにしてほしい時には、子どもが見ていてくれると私も正直助かる。 | ONE_d(TBS-07) | https://newsdig.tbs.co.jp/articles/-/2618789 | なし | OK | OK | TBSのみ根拠(TBS-07)。V1のTBS-07由来の1文目 |
| One Voice | 第9文 | 子どもを守るためなら迷わず決められると思うのに、どこまでならいいのか、私もまだすぐには答えが出ない。 | ONE_c(MR-T003-09); ONE_d(TBS-07); ONE_f(MR-T008-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/fa6b9009-7f17-4a08-8886-0e5839e4994e; https://newsdig.tbs.co.jp/articles/-/2618789 | 仮定・意見の言い換え | OK | OK(要注意) | Sheetの『矛盾・弱さ』欄(葛藤1か所・解消しない)を結びにした文。『子どもを守るためなら迷わず決められると思うのに…私もまだすぐには答えが出ない』は出典にない自己の迷いの補い(感情の補いの範囲、捏造でない)。lunaがONE_c/d/fを付けたが、TBS-07の内容そのものではない |
| Another Voice | 第1文 | 年齢だけでSNSの使い方をまとめて決められるのは、正直、嫌だ。 | TWO_a(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | 感情の言い方 | OK | OK | TWO_a |
| Another Voice | 第2文 | 高校生でもアカウントを持てなくなったら、友達と連絡を取るのに困ると思う。 | TWO_a(MR-T101-02); TWO_e(MR-T017-04) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/18f89fb2-f867-4ba5-9d2c-c5eef97343df; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | 仮定・意見の言い換え | OK | OK | TWO_a+TWO_e |
| Another Voice | 第3文 | アカウントを持つことまで禁止するのには、僕は反対だ。 | TWO_a(MR-T101-02); TWO_b(MR-T005-06) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | なし | OK | OK | TWO_a/TWO_b。『アカウントを持つことまで禁止』はV2の主張(TWO_b: 極端な制限は控える)に対応し、世界設定の『利用禁止』語をV2が使うのは妥当 |
| Another Voice | 第4文 | 僕は自分で考えて使いたいし、何をしていいかを大人に決めてもらうばかりでは困ると思うけど、悪口や脅しに遭ったらすぐ大人に頼りたいとも思うから、そこは自分でも都合がいいのかもしれない。 | TWO_c(MR-T082-02); TWO_f(MR-T010-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/a7af865c-082c-473f-8de6-2f4edbcde02a; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c1f94e41-7e11-45a0-9575-c5db9c126af0 | 仮定・意見の言い換え | OK | OK(要注意) | 葛藤は1か所(自分で考えたい↔悪口や脅しの時は大人に頼りたい。TWO_c/TWO_f)。末尾『そこは自分でも都合がいいのかもしれない』は出典にない自己評価の補い(Sheetの感情の癖『自分で留保を足す』の範囲、出来事ではない)。監視への言及なし |
| Another Voice | 第5文 | 危ないことを知らないまま使いたいわけじゃない。 | TWO_b(MR-T005-06) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 仮定・意見の言い換え | OK | 補った表現のみ | TWO_b(講習・呼びかけ)の言い換えの否定形 |
| Another Voice | 第6文 | まずは安全フィルターをかけるとか、友達と連絡を取れるままで危ないものを避けられるように、使い方のほうを変えてほしい。 | TWO_a(MR-T101-02) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/9183b586-dca4-4653-b69a-2e1caead7d01 | 聞き手への呼びかけ・つなぎ | OK | OK | TWO_a(安全フィルター)。『友達と連絡を取れるまま』はTWO_a/e |
| A Third Voice | 第1文 | 中学生の子にSNSを使わせるなら、わたしは、その子の力に合うところから始めさせたい。 | THREE_b(MR-T003-03) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34 | 年代・立場の手がかり | OK | OK | THREE_b。立場(中学生の子)の手がかり |
| A Third Voice | 第2文 | 年齢だけで区切るより、できれば、使える機能を少しずつ広げられる形がいいと思う。 | THREE_b(MR-T003-03) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34 | なし | OK | OK | THREE_b |
| A Third Voice | 第3文 | まだ自分では扱いきれないことまで、急にできるようにしなくていいんだ。 | THREE_a(MR-T032-03); THREE_b(MR-T003-03) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/223214d4-ccb3-44a3-994d-864194776724; https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/820ea70c-aed1-4690-a725-257cf592ad34 | 仮定・意見の言い換え | OK | OK | THREE_a/b。『急にできるようにしなくていい』は『段階的に広げたい』の言い換え |
| A Third Voice | 第4文 | 気がかりなのは、禁止されていた年齢を過ぎれば、何の準備もなく使い始めることになるんじゃないか、ということだ。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 感情の言い方 | OK | OK | THREE_d(禁止の年齢を過ぎて準備なしに触れる) |
| A Third Voice | 第5文 | ただ触れずにいた間に、使える力までつくとは思えない。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 仮定・意見の言い換え | OK | OK(要注意) | 『触れずにいた間に、使える力までつくとは思えない』はTHREE_dの『何の準備もしていなかったら』の解釈の補い(事実の追加ではない) |
| A Third Voice | 第6文 | そうして急に使い始めれば、事故につながる気がする。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 感情の言い方 | OK | OK(要注意) | THREE_d(事故につながる)。第4・第6文と同じ心配(準備なしに急に使い始める)の言い換えで、**目視で軽い反復**(repetition_reportは0) |
| A Third Voice | 第7文 | 海に出る前には泳ぐ練習が要るし、準備のできていない子を送り出すのは、やっぱり心配なんだ。 | THREE_d(MR-T005-11) | https://gikai.team-mir.ai/bills/56c4edc9-55fc-4d7f-9dcd-b45dc0648dbe/topics/c43c004e-e475-42e1-8896-164298f2f88d | 感情の言い方,仮定・意見の言い換え | OK | OK | THREE_dのたとえ(泳ぐ練習。たとえは1回)。結びの型=たとえ・像 |

## 3. TBSのみが根拠の文(公開前の権利確認の対象。OF-Y6-10)
| Voice | 位置 | 文 |
|---|---|---|
| One Voice | 第8文 | ただ、長い移動で静かにしてほしい時には、子どもが見ていてくれると私も正直助かる。 |

- 上記以外の文は、みらい議会(CC BY 4.0)の本人回答、Personaの立場・口調・芯(補った表現)、または世界設定の定義に対応する。TBS-10・TBS-02は本稿のいかなる文の根拠にもしていない。
