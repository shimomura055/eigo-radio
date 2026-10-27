# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `c97b6c8f8ad76cd4` / 本文sha: `dc291d4af4f5` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下の全候補の文法名と解説を読み、学習に載せる文法を**最大2件**選びます(0件も可。AI推奨=候補1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨 1: what節主語 [T1 / HEAVY] 段落P4  (id: `gcc2541c879`)

> The island went back to how it was before, but what the AI had discovered was not erased.

- 教える価値: what節が主語になり、その後ろの動詞が主節の述語になると見分ける。
- 読み違えやすい点: what the AI had discovered全体が主語なのに、埋め込み節内のthe AIを主節の主語と取り違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
島は以前の状態に戻ったが、AIが発見したことは消去されなかった。

【文法・構文の仕組み】
この文の主語は **what the AI had discovered** 全体です。ここでの **what** は「AIが発見したこと」という意味で、後ろの **the AI had discovered** と合わせて、発見された内容を表しています。

主節の述語は **was not erased**（消去されなかった）です。つまり、「何が消去されなかったのか」を主語の **what the AI had discovered** が示しています。

【意味・ニュアンス・表現効果】
前半の **The island went back to how it was before** は、島が以前の状態に戻ったことを述べています。一方、後半では、AIが発見した内容は消去されなかったと対比しています。島の状態は元に戻っても、AIが得たものは残っていた、という点に焦点を置いた文です。=====

## 候補 2: 関係節を含む長い主語 [T1 / HEAVY] 段落P6  (id: `gfb83f65a2d`)

> After that, the average number of towers it could build fell.

- 教える価値: 長い主語の中にある関係節の動詞と、主節の動詞を区別する。
- 読み違えやすい点: it could buildを主節の動詞と取り違え、文の主動詞fellを見落とすことがある。

### 解説(学習ページに載る全文)

【日本語訳】
その後、そのAIが建てられる塔の平均数は減少した。

【文法・構文の仕組み】
主語は **the average number of towers it could build** 全体です。中の **it could build** は **towers** を説明する関係節で、「そのAIが建てられる塔」という意味です。ここでは **towers** が **build** の目的語にあたるため、関係代名詞は省略されています。

文の中心となる主語は **the average number ...** で、主節の動詞は **fell**（減少した）です。つまり、「そのAIが建てられる塔の平均数」が減少した、と述べています。

【意味・ニュアンス・表現効果】
関係節 **it could build** によって、どの塔の数を指しているのかが「そのAIが建てられる塔」と限定されています。前の文では、AIの記憶から「岩を投げてブロックを得る」技法の説明が取り除かれたと述べられており、この文はその後に建てられる塔の平均数が下がったことを伝えています。焦点は、個々の塔ではなく、建てられる数の平均がどう変化したかにあります。

## 候補 3: that節を含む複合主語 [T1 / HEAVY] 段落P7  (id: `g080d9d1a1f`)

> The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately.

- 教える価値: that節を含む二つの名詞句がandで結ばれ、ひとまとまりの複合主語を作ると見分ける。
- 読み違えやすい点: 二つ目のthe fact that以下も主語の一部なのに、最初のthe fact that以下だけを主語と捉えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
経験豊富なグループの成績がよかったという事実と、特定の記憶を取り除くとその得点が下がったという事実は、分けて検討する必要があります。

【文法・構文の仕組み】
主語は、`the fact that the experienced group did better` と `the fact that removing a particular memory lowered its score` の二つです。どちらも `the fact that ...` の形で、「……という事実」を表し、二つの主語が `and` で結ばれています。

主節の述語は `need to be looked at separately` です。`need to be looked at` は「検討される必要がある」という意味で、`separately` は「別々に」を表します。二つの事実が主語なので、動詞は複数形の `need` になっています。

【意味・ニュアンス・表現効果】
この文は、経験豊富なグループの成績がよかったことと、特定の記憶を取り除いた後に得点が下がったことを、同じ一つの結果としてまとめず、別々に検討するよう促しています。二つの事実を複合主語として並べたうえで、それぞれを `separately`、つまり個別に見る必要があると述べています。

## 操作(コマンド。`--by` は操作者名。CLIの`--level`/`--ids`は後続委任で配線)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out --level b1b --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice pick --ids gcc2541c879 --accept-ai`
- 1〜2件を選ぶ(AI推奨のみ以外は理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out --level b1b --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice pick --ids <id>[,<id>] --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out --level b1b --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out --level b1b --candidates-sha c97b6c8f8ad76cd44e5bba221646ab2c4237e485a55a984c5535508b9affaf69 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
