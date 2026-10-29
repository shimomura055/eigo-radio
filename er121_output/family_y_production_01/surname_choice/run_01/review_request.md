# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## 文法(Part 2)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_01/study_text/grammar_human_review_request.md)

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

---
## 文法(Part 2)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_01/a2/study_text/grammar_human_review_request.md)

# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `4fff2225e1640ed4` / 本文sha: `2c4b13c306f5` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑似分裂文（it-cleft） [T1 / CLEFT] 段落P3  (評価順位1 / id: `g6ca5a9eb3c`)

> But was it only the name change that I didn’t like?

- 教える価値: it-cleftでは、itの後の焦点部分とthat節を対応させて、何が焦点化されているかを読む。
- 読み違えやすい点: itを通常の主語と捉え、the name changeがthat以下で焦点化されている分裂文の構造を取り違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
でも、私が嫌だったのは名前が変わったことだけだったのだろうか？

【文法・構文の仕組み】
これは疑似分裂文（it-cleft）の疑問文です。疑問文なので、平叙文の *It was ...* にあたる部分が *Was it ...?* の語順になっています。

*the name change* が焦点部分で、「名前の変更」を指します。*only* はこの部分にかかり、「名前の変更だけ」という限定を表します。続く *that I didn’t like* は、何が嫌だったのかを説明する節です。つまり文全体は「私が嫌だったものは、名前の変更だけだったのか」と問いかけています。

【通常の表現・語順との比較】
比較用：*But did I dislike only the name change?*

この語順でも「名前の変更だけが嫌だったのか」と尋ねられます。一方、本文の形では *the name change* を焦点として前に出し、「嫌だったのはそれだけなのか」と対象を強調しています。

【意味・ニュアンス・表現効果】
前の文は *I got really upset.*（私はひどく動揺した）です。この疑問文は、その動揺の理由が名前の変更だけだったのかを話者が問い直すものです。*only* によって「ほかにも嫌だったことがあったのではないか」という可能性が示され、後の *I think I really wanted him to stay close.* へとつながります。=====

## Top2: 埋め込み節を含む動名詞句主語 [T1 / HEAVY] 段落P2  (評価順位2 / id: `g732a87bdfd`)

> But fitting in with what each family thought was normal was harder than changing my last name.

- 教える価値: 埋め込み節を含む長い動名詞句が主語となる文では、主語のまとまりを確定してから主節の動詞を探す。
- 読み違えやすい点: what節の中のwas normalを主節の述語と取り、後ろのwas harderを別の主節の動詞のように読んでしまうことがある。

### 解説(学習ページに載る全文)

【日本語訳】
それぞれの家族が普通だと思っていたことに合わせるのは、姓を変えることより難しかった。

【文法・構文の仕組み】
文の主語は、文頭の **fitting in with what each family thought was normal** 全体です。**fitting in** は動名詞で、「周囲に合わせること」という意味です。

その後ろの **with what each family thought was normal** は、「それぞれの家族が普通だと思っていたことに」という部分です。**what each family thought was normal** は「それぞれの家族が普通だと思っていたこと」を表します。ここで **what** は **was normal** の主語にあたります。

主語のあとに続く **was harder** が主節の動詞を含む部分で、「より難しかった」という意味です。**than changing my last name** は「姓を変えることよりも」と比較の基準を示しています。

【通常の表現・語順との比較】
比較用：**It was harder to fit in with what each family thought was normal than to change my last name.**

この形では、形式上の主語 **It** のあとに「何が難しかったか」を置いています。一方、本文では「家族に合わせること」を表す動名詞句そのものを主語にしています。

【意味・ニュアンス・表現効果】
「姓を変えること」と「それぞれの家族の普通に合わせること」を比べ、後者のほうが難しかったと述べています。動名詞句を主語にすることで、何が難しかったのか、つまり家族の考え方や習慣に合わせることが文の中心に置かれています。
=====

(他2件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice pick --ids g6ca5a9eb3c --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er121_output/family_y_production_01/surname_choice/run_01 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。

---
## KP(level=b1b)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_01/key_phrases/b1b/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `a891b830b2b97a04` / 本文sha: `821e940c2738`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | go in opposite directions | 正反対の方向を向いている | Thanks for accepting his decision and thanks for changing his last name go in opposite directions | 意見や利害が正反対であることを比喩的に表す。 |  |
| 2 | KP | hold one's son back | 人の息子の足を引っ張る | Even so, I don't want my feelings as a parent to hold my son back | 人の行動や前進を妨げる句動詞の用法を学べる。 |  |
| 3 | KP | talk it over | それについてよく話し合う | I know a relative who took his wife's last name without first talking it over with his parents | 相談して決めることを表す自然な口語表現。 |  |
| 4 | 単語 | time to oneself | 自分だけの時間 | Living at my wife's parents' home, I still find it a little hard that I have so little time to myself | 一人で過ごす時間を表す定着した言い回し。 |  |
| 5 | 単語 | only natural | ごく当然のこと | But if it were my son, it would still bother me if his partner's parents thought it was only natural | 「当然のこと」という意味になる自然な組み合わせ。 |  |
| 6 |  | at ease | 気が楽な | Once I could accept that it was normal for things to be different, I felt much more at ease | 安心してくつろいだ状態を表す慣用表現。 |  |
| 7 |  | hesitation | ためらい | I had no hesitation at all about changing my last name | ためらいや迷いを表す名詞で、幅広い場面で使えます。 |  |
| 8 |  | rural | 田舎の | My parents' home is in a pretty rural place, but they don't have old-fashioned views, and they accepted it easily | 「田舎の」を表す語で、地域や暮らしの描写に役立ちます。 |  |
| 9 |  | adoption | 養子縁組 | It does not involve adoption | 「養子縁組」を表す名詞で、制度や家族の話題で使えます。 |  |
| 10 |  | generation | 世代 | Last is someone from the parents' generation whose relative chose his wife's last name | 「世代」を表し、社会や家族の変化を論じる際に使えます。 |  |
| 11 |  | grateful | 感謝している | I was grateful that both sets of parents accepted my decision without being upset | 感謝している状態を表す形容詞で、気持ちを的確に伝えます。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --accept-ai --candidates-sha a891b830b2b97a040d1beb08c4f87227e5c4ffacf94249dfddc5097519f6940c --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/surname_choice/run_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## KP(level=a2)
(個別の依頼書: er121_output/family_y_production_01/surname_choice/run_01/key_phrases/a2/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `57b998cd0c3446db` / 本文sha: `2c4b13c306f5`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | hold someone's son back | 人の息子の足を引っ張る | Even so, I don't want my feelings as a parent to hold my son back | 「人の行動を妨げる」という意味の句動詞です。 | 重複: 7 |
| 2 | KP | fit in with | ～に合わせる | But fitting in with what each family thought was normal was harder than changing my last name | 周囲の考えや慣習に合わせる意味で使います。 |  |
| 3 | KP | go in opposite directions | 互いに相反している | Thanks for accepting his choice and thanks for changing his name go in opposite directions | 物事が正反対の方向を示す比喩表現です。 |  |
| 4 | 単語 | only natural | ごく自然なこと | But if it were my son, it would still bother me if his partner's parents thought it was only natural | 当然だ、自然なことだという意味の慣用表現です。 |  |
| 5 | 単語 | at ease | 気持ちが楽な | Once I accepted that things could be different, I felt much more at ease | 緊張や不安がなく、気楽な状態を表します。 |  |
| 6 |  | hesitate | ためらう | I did not hesitate at all about changing my last name | 判断をためらう意味で幅広く使える動詞。 |  |
| 7 |  | oppose | 反対する | If my son made that choice, I wouldn't oppose him | 意見や提案に反対することを表す動詞。 | 重複: 1 |
| 8 |  | grateful | 感謝している | I want them to feel at least a little grateful to my son | 感謝している気持ちを表す重要な形容詞。 |  |
| 9 |  | adoption | 養子縁組 | This does not mean adoption | 養子縁組などを表す汎用性のある名詞。 |  |
| 10 |  | relative | 親戚 | Last is someone from the parents' generation whose relative chose his wife's last name | 親族を意味し、日常的に使える名詞。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --accept-ai --candidates-sha 57b998cd0c3446db1abdfcf770e2d4b0be4eaba92b5a2203db4eba19d144a242 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

