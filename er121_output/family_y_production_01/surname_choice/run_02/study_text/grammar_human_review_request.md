# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `6df66842f0a53aac` / 本文sha: `975c98267084` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): It-cleft（強調構文） [T1 / CLEFT] 段落P2  (評価順位1 / id: `g0f6b706ff3`)

> It was my wife’s parents who worried, asking me again and again if I was really sure.

- 教える価値: It is/was ... whoの形では、who節の中の動詞と焦点となる人物を対応させる。
- 読み違えやすい点: Itを内容を指す主語と捉え、my wife’s parentsをworriedの主語ではなく補語のように読んでしまうことがある。

### 解説(学習ページに載る全文)

【日本語訳】
私が本当にそれでいいのかと何度も尋ねて心配していたのは、妻の両親だった。

【文法・構文の仕組み】
“It was my wife’s parents who worried” は、強調したい部分を “It was ... who ...” の形で示す強調構文です。ここでは “my wife’s parents” が強調されています。“who worried” は「心配していた人」を説明する部分で、“worried” の主語は “who” が指す “my wife’s parents” です。

文末の “asking me again and again if I was really sure” は、両親がどのように心配していたかを補足しています。“asking ...” の動作をするのも両親です。“if I was really sure” は「私が本当に確信しているのか」という内容を表します。

【通常の表現・語順との比較】
比較用：My wife’s parents worried, asking me again and again if I was really sure.

この語順でも「妻の両親が心配して、私に何度も尋ねた」という意味です。本文の文では “It was my wife’s parents who ...” とすることで、「心配していたのは誰か」に焦点を当てています。

【意味・ニュアンス・表現効果】
話し手は、自分の決断を心配して何度も確かめたのは妻の両親だった、と相手を特定しています。続く文では両方の親が決断を受け入れたと述べられており、この文は、その中でも妻の両親が心配していたことに焦点を当てています。
=====

## Top2: 疑問文のIt-cleft（強調構文） [T1 / CLEFT] 段落P3  (評価順位2 / id: `gfb5fe09043`)

> But was it only the change of last name that I didn’t like?

- 教える価値: 疑問文のIt-cleftでは、that節の中で焦点となる要素が何かを確かめる。
- 読み違えやすい点: itを通常の主語として読み、the change of last nameが強調される部分であることを捉え損ねることがある。

### 解説(学習ページに載る全文)

【日本語訳】
でも、私が嫌だったのは姓が変わることだけだったのだろうか。

【文法・構文の仕組み】
これは疑問文のIt-cleft（強調構文）です。`it` と `was` の後に置かれた `the change of last name` が、焦点として示されています。続く `that I didn’t like` は、そのことについて説明する節です。この節では `I` が主語で、`didn’t like` の目的語に当たる部分は、焦点の `the change of last name` と結びついています。

疑問文なので、`was` が主語の `it` の前に出て `was it` となっています。

【通常の表現・語順との比較】
比較用：`But did I dislike only the change of last name?`

こちらは「私は姓の変更だけを嫌ったのか」と直接尋ねる形です。元の文ではIt-cleftを使うことで、「嫌だったのは姓の変更だけなのか」という点に焦点が当たります。

【意味・ニュアンス・表現効果】
前の文では、息子も姓を変えると言ったとき、話し手は息子が遠ざかっていくように感じ、ひどく動揺したと述べています。この文では、話し手は自分が嫌だったのは姓の変更そのものだけだったのか、と問い直しています。後の文の「本当は息子に近くにいてほしかった」という気持ちへつながる問いです。
=====

(他1件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --candidates-sha 6df66842f0a53aac2a486d30e31c31352666e05b7abd9902b906aa4e24a0e6b7 --by <名前> --choice pick --ids g0f6b706ff3 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --candidates-sha 6df66842f0a53aac2a486d30e31c31352666e05b7abd9902b906aa4e24a0e6b7 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --candidates-sha 6df66842f0a53aac2a486d30e31c31352666e05b7abd9902b906aa4e24a0e6b7 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --candidates-sha 6df66842f0a53aac2a486d30e31c31352666e05b7abd9902b906aa4e24a0e6b7 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_02` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_02 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
