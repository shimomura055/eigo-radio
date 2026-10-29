# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `5e67783cff9ce06f` / 本文sha: `6760244d1caa` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑似分裂文 [T1 / CLEFT] 段落P11  (評価順位1 / id: `g9053a0e595`)

> What is more interesting is that an ad label and the effect of a conversation may work in different ways.

- 教える価値: What で始まる名詞節が主語となり、後ろの be 動詞で説明内容につながる形を捉える。
- 読み違えやすい点: What で始まる節全体が主語ですが、What を疑問詞と取って文の構造を疑問文のように取り違える可能性があります。

### 解説(学習ページに載る全文)

【日本語訳】
さらに興味深いのは、広告ラベルと会話の効果が異なる仕方で働く可能性があるということだ。

【文法・構文の仕組み】
この文は疑似分裂文です。文頭の **What is more interesting** が主語となる名詞節で、「より興味深いことは」という意味です。ここでの **what** は疑問を表すのではなく、「〜すること・もの」という内容をまとめています。

**is** の後ろの **that an ad label and the effect of a conversation may work in different ways** は、何が興味深いのかを示す節です。**that** は節を導く語で、節全体が **is** の後ろに置かれています。

【通常の表現・語順との比較】
比較用：**It is more interesting that an ad label and the effect of a conversation may work in different ways.**

こちらも「広告ラベルと会話の効果が異なる仕方で働く可能性があるのは、より興味深い」という内容を表します。一方、本文の形では **What is more interesting** を先に置き、「興味深いことは何か」を示してから、その内容を **that** 節で説明しています。

【意味・ニュアンス・表現効果】
前の文では、「違いを確認できなかったこと」と「効果がないこと」は同じ意味ではないと述べています。続くこの文は、広告ラベルと会話の効果が異なる仕方で働く可能性に焦点を移しています。**may** があるため、異なる仕方で働くと断定せず、その可能性を示しています。

## Top2: 長い動名詞句を主語とする文 [T1 / HEAVY] 段落P2  (評価順位2 / id: `ga4a4325b64`)

> Noticing an ad and stopping yourself from wanting the product seem like two different things.

- 教える価値: 動名詞句が主語になる文では、主語の範囲を見極めてから動詞を探す。
- 読み違えやすい点: 長い動名詞句全体が主語ですが、「the product」を主語と取り、後ろの動詞とのつながりを取り違える可能性があります。

### 解説(学習ページに載る全文)

【日本語訳】
広告に気づくことと、その商品を欲しいと思う気持ちを自分で抑えることは、別々のことのように思えます。

【文法・構文の仕組み】
文の主語は、文頭の **Noticing an ad and stopping yourself from wanting the product** 全体です。**Noticing an ad**（広告に気づくこと）と **stopping yourself from wanting the product**（その商品を欲しいと思う気持ちを自分で抑えること）という、2つの動名詞句が **and** で結ばれています。

このように複数の行為を並べた主語を受けて、動詞は **seem** となっています。**like two different things** は「別々のことのように」という意味で、2つの行為がどのように見えるのかを示しています。

【意味・ニュアンス・表現効果】
広告に気づくことと、商品を欲しがる気持ちを抑えることは別の行為だ、という内容です。**seem** が使われているため、「別のことだ」と断定するよりも、「別のことのように思える」という捉え方になっています。本文では、広告に気づくことと欲求を抑えることを区別して述べています。

(他5件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 5e67783cff9ce06f0b1d6ba731b114b876da5cb400f78e7739b5518556a82c91 --by <名前> --choice pick --ids g9053a0e595 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 5e67783cff9ce06f0b1d6ba731b114b876da5cb400f78e7739b5518556a82c91 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 5e67783cff9ce06f0b1d6ba731b114b876da5cb400f78e7739b5518556a82c91 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 5e67783cff9ce06f0b1d6ba731b114b876da5cb400f78e7739b5518556a82c91 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
