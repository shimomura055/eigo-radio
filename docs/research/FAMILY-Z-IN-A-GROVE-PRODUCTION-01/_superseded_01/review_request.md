# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## 文法(Part 2)
(個別の依頼書: er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/a2/study_text/grammar_human_review_request.md)

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

---
## KP(level=b1b)
(個別の依頼書: er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/key_phrases/b1b/kp_human_review_request.md)

# KP Human Review 依頼(b1b) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `941647eb453de90d` / 本文sha: `ee5433934163`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | cold contempt | 冷ややかな軽蔑 | But his eyes held nothing except cold contempt | 「冷ややかな軽蔑」を表す印象的な語の組み合わせ。 |  |
| 2 | KP | The thicket fell silent | 茂みが静まり返る | The thicket fell silent | 場所を主語にした、文学的な擬人表現。 |  |
| 3 | KP | on soft feet | 忍び足で | Then someone crept towards me on soft feet | 「足音を立てずに」を表す文学的な言い回し。 |  |
| 4 | 単語 | sink for ever | 永遠の眠りにつく | I sank for ever into the darkness | 「永遠に沈んだ」という余韻のある文学的表現。 |  |
| 5 | 単語 | trampled | 踏みつけられた | The broken bamboo and trampled earth showed a struggle | 踏み荒らす意味を持つ、描写に役立つ動詞です。 |  |
| 6 |  | constable | 警官 | I caught Tajomaru, the famous bandit, by the stone bridge," said the constable | 警察官を指す語で、英語圏の制度理解にも役立ちます。 |  |
| 7 |  | veiled | ベールで覆われた | His wife rode beside him, her face veiled | 「覆われた」から「隠された」まで表せる語です。 |  |
| 8 |  | seize | ぐっとつかむ | Then she seized my arm | 「つかむ・奪う」など幅広い場面で使われます。 |  |
| 9 |  | medium | 霊媒師 | I heard the bandit comforting her," said Takehiro's spirit through the medium | 霊媒を指す意味を含む、多義的で汎用性のある語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level b1b --accept-ai --candidates-sha 941647eb453de90d41fdced487cf47ed28a4065bb782f43dd206f75a0ad2bee4 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level b1b --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level b1b --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## KP(level=a2)
(個別の依頼書: er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/key_phrases/a2/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `761026a5e726ba64` / 本文sha: `6aa5c86dd0d6`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | through a medium | 霊媒を通して | I heard the bandit trying to comfort her," Takehiro's spirit said through a medium | mediumが霊媒を指す用法を学べる。 |  |
| 2 | KP | sink into darkness | 命が尽きる | Then I sank into darkness and stayed there for ever | 暗闇へ沈むという文学的な比喩表現。 |  |
| 3 | KP | couldn't bear | 我慢できなかった | I stabbed him because I couldn't bear those eyes | bearが「耐える」を表す自然な用法。 |  |
| 4 | 単語 | fight fairly | 正々堂々と戦う | I untied him, and we fought fairly with swords | fairlyが「正々堂々と」の意味で使われる。 |  |
| 5 |  | lasted twenty-three strokes | 二十三回の斬撃に耐え抜く | He lasted twenty-three strokes, but nobody else had reached twenty | lastが戦いの中で「持ちこたえる」を表す。 | 修正済み(元: lasted twenty-three strokes / REVERT_SURFACE) / AUTO対象外 |
| 6 | 単語 | constable | 警官 | I caught Tajomaru, the famous bandit," the constable said | 警察官を表すやや格式のある語で、報道や文学でも使われます。 |  |
| 7 |  | bandit | 盗賊 | I caught Tajomaru, the famous bandit," the constable said | 武装して人を襲う盗賊を指し、文学や歴史の文脈で役立ちます。 |  |
| 8 |  | dagger | 短刀 | She fought with her dagger, but I forced her to have sex with me | 短剣を意味し、物語や歴史の描写でよく使われます。 |  |
| 9 |  | veil | 顔や頭を覆う薄い布 | The wind lifted her veil, and I wanted her | ベールのほか、何かを覆い隠すものという比喩にも使われます。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --accept-ai --candidates-sha 761026a5e726ba644f4a89c4fc264b08b5f10719a6c7a5678f91615721c4c733 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

