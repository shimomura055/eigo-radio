# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## 文法(Part 2)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_02/study_text/grammar_human_review_request.md)

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

---
## 文法(Part 2)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_02/a2/study_text/grammar_human_review_request.md)

# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `aaaf92601fb36b2b` / 本文sha: `4e31c2d63291` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 関係節を含む長い主語 [T1 / HEAVY] 段落P5  (評価順位1 / id: `g983a1a42cd`)

> The man who joined his wife’s family as an adopted son said he was thankful that both families accepted him.

- 教える価値: 関係節を含む長い主語では、主語の中心を確認してから主節の動詞を探す。
- 読み違えやすい点: 関係節内のjoinedを主節の動詞と捉え、主節の動詞saidを見落とす可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
妻の家に養子として入った男性は、両家が自分を受け入れてくれたことに感謝していると述べた。

【文法・構文の仕組み】
主語は **The man who joined his wife’s family as an adopted son** です。中心となる語は **The man**（その男性）で、**who joined his wife’s family as an adopted son**（妻の家に養子として入った）が関係節として **man** を修飾しています。関係節の **who** は **man** を指し、関係節の中では **joined** の主語です。

この長い主語のあとに、主節の動詞 **said** が続きます。さらに **said** の内容は **he was thankful that both families accepted him** で、**that both families accepted him** は「両家が自分を受け入れてくれたこと」という、感謝の理由を表しています。

【意味・ニュアンス・表現効果】
関係節によって、男性がどのような人物なのかを説明してから、主節の **said** で発言内容へ進んでいます。妻の家に養子として入ったことと、両家に受け入れられたことへの感謝が、一続きの文で結びつけられています。
=====

## Top2: 関係節を含む長い主語 [T1 / HEAVY] 段落P5  (評価順位2 / id: `g20b0a2fe81`)

> A parent who respects a son’s choice said they wanted the other parents to feel at least a little thankful to their son.

- 教える価値: 関係節を含む主語では、主語を修飾する動詞と主節の動詞を区別する。
- 読み違えやすい点: 主語内のrespectsを主節の動詞と捉え、主節の動詞saidを見つけにくくなる可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
息子の選択を尊重する親は、相手の親たちにも、自分の息子に少しでも感謝してほしいと述べた。

【文法・構文の仕組み】
主語は **A parent who respects a son’s choice** 全体です。この中の **who respects a son’s choice** は関係節で、直前の **parent** を「息子の選択を尊重する」と説明しています。主語の中心は **parent** で、主節の動詞は **said** です。

**said** の後ろには、何を述べたのかを示す内容が続きます。**they wanted the other parents to feel ...** では、**they** は **A parent** を指し、**want + 人 + to不定詞** の形で「人に〜してほしい」という意味です。つまり、**the other parents to feel** は「相手の親たちに感じてほしい」にあたります。**thankful to their son** は「自分たちの息子に感謝している」という意味です。

【意味・ニュアンス・表現効果】
関係節によって、誰が話したのかが「息子の選択を尊重する親」として示されています。その親は、自分の息子への感謝を相手の親たちにも感じてほしいと述べています。**at least a little** は「少しでも」という控えめな言い方で、感謝の気持ちがわずかでもあればよい、という願いを表しています。
=====

(他2件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level a2 --candidates-sha aaaf92601fb36b2bb942c81a5c2d4b7ec2fb771656b95a2984efbdd0c015907b --by <名前> --choice pick --ids g983a1a42cd --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level a2 --candidates-sha aaaf92601fb36b2bb942c81a5c2d4b7ec2fb771656b95a2984efbdd0c015907b --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level a2 --candidates-sha aaaf92601fb36b2bb942c81a5c2d4b7ec2fb771656b95a2984efbdd0c015907b --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_02 --level a2 --candidates-sha aaaf92601fb36b2bb942c81a5c2d4b7ec2fb771656b95a2984efbdd0c015907b --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_02` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er121_output/family_y_production_01/surname_choice/run_02 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_02 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。

---
## KP(level=b1b)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_02/key_phrases/b1b/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `df69c2469a1585cb` / 本文sha: `975c98267084`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 |  | taking offense | 気を悪くする | I was grateful that both sets of parents accepted my decision without taking offense | 「気分を害する」という意味の慣用表現。 | 修正済み(元: taking offense / REVERT_SURFACE) / AUTO対象外 |
| 2 | KP | let go of | 手放す | I need to let go of my son, don't I | 人や物への執着を手放す句動詞。 | 重複: 3,6 |
| 3 |  | hold one's son back | 人の息子の足を引っ張る | Even so, I don't want to hold my son back because of my feelings as a parent | 人の行動を妨げる句動詞の用例。 | 重複: 2 |
| 4 | KP | at ease | 気持ちが楽で | Once I could accept that of course we were different, I felt much more at ease | 安心してくつろいだ状態を表す表現。 |  |
| 5 | KP | way out in the country | かなり田舎のほうに | My parents accepted it easily, even though my hometown is way out in the country | 「かなり田舎に」を表す口語的な表現。 |  |
| 6 |  | give something up | 何かをあきらめる | In a conversation about last names, perhaps a person's own choice overlaps with the feeling that a parent is giving something up | 何かを手放すことを表す句動詞。 | 重複: 2 |
| 7 | 単語 | overlap with | 〜と重なり合う | In a conversation about last names, perhaps a person's own choice overlaps with the feeling that a parent is giving something up | 考えや感情が重なることを表す動詞表現。 |  |
| 8 | 単語 | registration | 届け出 | Whether a husband chooses his wife's last name on the marriage registration form or joins her family as an adopted son, he and each of their families have their own feelings | 公的な登録手続きに関わる語で、幅広く使えます。 |  |
| 9 |  | grateful | ありがたく思う | I was grateful that both sets of parents accepted my decision without taking offense | 感謝の気持ちを表す、汎用性の高い形容詞です。 |  |
| 10 |  | Alongside | 〜に加えて | Alongside the couple's decision about their last name, there are feelings that parents want to share with the other parents | 「〜と並んで」を表し、文章で使いやすい語です。 |  |
| 11 |  | adopted | 養子になった | Whether a husband chooses his wife's last name on the marriage registration form or joins her family as an adopted son, he and each of their families have their own feelings | 養子縁組など、文脈に応じた意味を学べます。 |  |
| 12 |  | adjust | 慣れる | I still find it a little hard that I don't get much time to myself while living at my wife's parents' home, but adjusting to the way each family does things was harder than changing my last name | 状況や環境に順応することを表す語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_02`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --accept-ai --candidates-sha df69c2469a1585cb5e532a8a8a7f9a745b26be29a60e3831149514f16c99a51f --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/surname_choice/run_02 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_02 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## KP(level=a2)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_02/key_phrases/a2/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `0e236adcd79e9820` / 本文sha: `4e31c2d63291`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | let one's son go | 自分の息子を手放す | I need to let my son go, don't I | 相手を引き止めずに手放す、比喩的な用法が学べる。 | 重複: 4 |
| 2 | KP | at ease | 気持ちが楽な | When I accepted that our families were different, I felt much more at ease | 「気持ちが楽な、安心した」を表す慣用表現。 |  |
| 3 | KP | only natural | 当たり前のこと | But if it were my son, I would still feel bothered if his partner's parents thought it was only natural | 「当然のことだ」という意味で使う自然な言い回し。 |  |
| 4 |  | give something up | 何かを手放す | In a talk about last names, perhaps a person's choice meets a parent's feeling that they are giving something up | 何かを犠牲にする、断念する意味の表現。 | 重複: 1 |
| 5 |  | old-fashioned about it | そのことについて考え方が古い | They were not old-fashioned about it | ある事柄について保守的だと表す言い回し。 | QA FAIL(採用には --accept-qa-fail) / AUTO対象外 |
| 6 | 単語 | far out in the country | 人里離れた田舎に | My parents accepted it easily, even though my hometown is far out in the country | 人里離れた田舎を表す語句のまとまり。 |  |
| 7 | 単語 | adopted | 養子になった | Or he may join her family as an adopted son | 養子縁組や政策採用など、幅広い文脈で使われる語です。 |  |
| 8 |  | relative | 親戚 | A relative took his wife's last name | 親族を表し、日常から公的な文脈まで使えます。 |  |
| 9 |  | bothered | 嫌な気持ちになる | But if it were my son, I would still feel bothered if his partner's parents thought it was only natural | 心を煩わせる状態を表し、感情描写に役立ちます。 |  |
| 10 |  | thankful | ありがたく思う | I was thankful that both families accepted my choice and were not upset | 感謝している状態を表す、汎用性の高い形容詞です。 |  |
| 11 |  | perhaps | もしかすると | In a talk about last names, perhaps a person's choice meets a parent's feeling that they are giving something up | 断定を避けて可能性を示す副詞です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_02`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_02 --level a2 --accept-ai --candidates-sha 0e236adcd79e982005bd72c66be7f667b260d7a047348d4796aae04d7844de17 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_02 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/surname_choice/run_02 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_02 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

