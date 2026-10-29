# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `b1070b97318a163f` / 本文sha: `821e940c2738` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑問文のit-cleft [T1 / CLEFT] 段落P3  (評価順位1 / id: `gfb5fe09043`)

> But was it only the change of last name that I didn’t like?

- 教える価値: 疑問文のit-cleftでは、it is/was X that ...の形から強調される要素Xを見つける。
- 読み違えやすい点: itを通常の主語として読み、that節が強調された要素を示す分裂文の一部だと見落とす可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
でも、私が嫌だったのは姓が変わることだけだったのだろうか。

【文法・構文の仕組み】
これは、**it + be動詞 + 強調したい部分 + that以下**の形を使った疑問文です。`was it only the change of last name that I didn’t like?`では、`only the change of last name`（姓が変わることだけ）が強調されています。`that I didn’t like`は「私が嫌だったもの」を表し、強調された部分と結びついています。

疑問文なので、`it was`ではなく`was it`の語順になっています。

【通常の表現・語順との比較】
比較用：`But did I dislike only the change of last name?`

こちらは「姓が変わることだけを嫌ったのだろうか」と、通常の語順で尋ねる表現です。元の文はit-cleftを使うことで、「嫌だったものは姓の変更だけなのか」という点に焦点を当てています。

【意味・ニュアンス・表現効果】
前の文の`I got really upset.`を受けて、話者は、自分が嫌だったのは姓が変わることだけだったのかと問い直しています。疑問の形にすることで、姓の変更だけでは気持ちを説明しきれない可能性が示されます。続く`I think what I really felt was that I wanted him to stay close.`では、話者が本当に感じていたことについて述べています。
=====

## Top2: 疑似分裂文 [T1 / CLEFT] 段落P3  (評価順位2 / id: `gb7c6a9b87f`)

> I think what I really felt was that I wanted him to stay close.

- 教える価値: What節が主語になる疑似分裂文では、what節を「私が感じていたこと」というまとまりで読む。
- 読み違えやすい点: what節を疑問の間接話法のように取り違え、文全体の主語にあたる名詞節として読めない可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
私が本当に感じていたのは、息子にそばにいてほしいということだったのだと思います。

【文法・構文の仕組み】
この文は、**what節を主語にし、be動詞の後ろでその内容を説明する「疑似分裂文」**です。

`what I really felt` が `was` の主語です。ここでの `what` は「私が感じていたこと」という意味で、`what I really felt` 全体が名詞のように働いています。`was` の後ろの `that I wanted him to stay close` は、その「感じていたこと」の内容を示します。

また、`I wanted him to stay close` では、`him` が `to stay close` の動作をする人です。つまり「彼に近くにいてほしい」という意味になります。

【通常の表現・語順との比較】
**比較用：** `I really felt that I wanted him to stay close.`  
こちらは「私は、彼に近くにいてほしいと本当に感じていた」という通常の語順です。元の文は「私が本当に感じていたのは何だったのか」を先に示し、`that`節で答える形になっています。

【意味・ニュアンス・表現効果】
前の文では、話者は嫌だったのが名字の変更だけだったのかと問いかけています。この文では、それだけでなく、本当に感じていたのは息子にそばにいてほしいということだったのだと振り返っています。疑似分裂文によって、「何を感じていたのか」という問いへの答えに焦点が当たっています。=====

(他6件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --candidates-sha b1070b97318a163fa9a970c9cd86c36b19c470c099a7769536b509e6444240a2 --by <名前> --choice pick --ids gfb5fe09043 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --candidates-sha b1070b97318a163fa9a970c9cd86c36b19c470c099a7769536b509e6444240a2 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --candidates-sha b1070b97318a163fa9a970c9cd86c36b19c470c099a7769536b509e6444240a2 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --candidates-sha b1070b97318a163fa9a970c9cd86c36b19c470c099a7769536b509e6444240a2 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
