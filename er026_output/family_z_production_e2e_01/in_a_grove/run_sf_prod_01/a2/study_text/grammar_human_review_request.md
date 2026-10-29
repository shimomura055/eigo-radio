# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `c9124ec57bc3a2fa` / 本文sha: `6aa5c86dd0d6` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 同格句 [T1 / APPOS] 段落P3  (評価順位1 / id: `gfc812ca542`)

> I caught Tajomaru, the famous bandit,” the constable said.

- 教える価値: コンマで補足される名詞句が、直前の名詞を言い換える同格句かどうかを見分ける。
- 読み違えやすい点: コンマ後の名詞句を独立した目的語のように読み、Tajomaruの言い換えとして結び付けないことがある。

### 解説(学習ページに載る全文)

【日本語訳】
「私は有名な盗賊タジョマルを捕らえた」と巡査は言った。

【文法・構文の仕組み】
「Tajomaru, the famous bandit」の「the famous bandit」は、「Tajomaru」と同じ人物を指し、その人物について補足する同格句です。つまり、「有名な盗賊」は別の人物ではなく、タジョマルがどんな人物かを説明しています。

文末の「the constable said」は、誰がその発言をしたのかを伝える部分です。「said」の前に発言内容が置かれています。

【意味・ニュアンス・表現効果】
巡査は、タジョマルを捕らえたと述べています。「the famous bandit」を添えることで、タジョマルが「有名な盗賊」であることも、名前と結びつけて伝えています。=====

## Top2: 同格句 [T1 / APPOS] 段落P4  (評価順位2 / id: `gebcce7c1c9`)

> Takehiro was my daughter’s husband, a kind samurai,” the old woman said.

- 教える価値: コンマ後の名詞句が、主語やその補語を補足する同格句として働くことを捉える。
- 読み違えやすい点: コンマ後の名詞句を前の内容から切り離し、Takehiroを補足説明する同格句として結び付けないことがある。

### 解説(学習ページに載る全文)

【日本語訳】
「タケヒロは私の娘の夫で、親切な侍でした」と老女は言った。

【文法・構文の仕組み】
文の骨格は、`Takehiro was my daughter’s husband`（タケヒロは私の娘の夫だった）です。`was` は「〜だった」という意味の be 動詞で、`my daughter’s husband` が主語 `Takehiro` について説明する補語です。

そのあとに続く `a kind samurai` は、直前の `my daughter’s husband` の説明をもう一つ加えているのではなく、`Takehiro` がどんな人物かを補足する同格句です。つまり、「タケヒロは親切な侍だった」という情報を付け加えています。

【意味・ニュアンス・表現効果】
まずタケヒロと老女の娘との関係を示し、続けて彼を「親切な侍」と説明しています。一つの文の中で、タケヒロが誰なのかと、どんな人物なのかが簡潔に伝わります。=====

(他1件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --candidates-sha c9124ec57bc3a2fa86e4a357078ca9a367cc043c692fa189c61a5310c42f7b6e --by <名前> --choice pick --ids gfc812ca542 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --candidates-sha c9124ec57bc3a2fa86e4a357078ca9a367cc043c692fa189c61a5310c42f7b6e --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --candidates-sha c9124ec57bc3a2fa86e4a357078ca9a367cc043c692fa189c61a5310c42f7b6e --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --candidates-sha c9124ec57bc3a2fa86e4a357078ca9a367cc043c692fa189c61a5310c42f7b6e --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
