# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `53adab857b154529` / 本文sha: `165307a8e442` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): What節を用いた疑似分裂文 [T1 / CLEFT] 段落P11  (評価順位1 / id: `g6f66e2d3d5`)

> What’s more interesting is that the ad label and the effect of the conversation may work in different ways.

- 教える価値: What節の内部の動詞と主節の動詞を区別し、What節を主語として読む。
- 読み違えやすい点: What’sのisを主節の動詞と捉え、その後のisを見落とすおそれがある。

### 解説(学習ページに載る全文)

【日本語訳】
さらに興味深いのは、広告ラベルと会話の効果が異なる形で働く可能性があるという点だ。

【文法・構文の仕組み】
この文は、What節を主語にした疑似分裂文です。冒頭の「What’s more interesting」は「さらに興味深いこと」という意味のWhat節で、節の中の「’s」は「is」です。ここでの「is」は「more interesting」と結びつき、「何がさらに興味深いのか」を示しています。

主節の動詞は、その後にある二つ目の「is」です。「that the ad label and the effect of the conversation may work in different ways」はthat節で、この二つ目の「is」の補語になっています。つまり、「さらに興味深いことは何か」に対して、that節がその内容を説明しています。

【通常の表現・語順との比較】
比較用：It is more interesting that the ad label and the effect of the conversation may work in different ways.

この形では「It is ... that ...」で内容を述べています。一方、本文の文は「What’s more interesting」を先に置き、「何が興味深いのか」という話題を示してから、that節で答えています。

【意味・ニュアンス・表現効果】
「may work in different ways」は「異なる形で働く可能性がある」という意味で、断定を避けています。前の文では「差を確認できなかった」ことと「効果がない」ことは同じではないと述べられており、この文はさらに、広告ラベルと会話の効果も同じように働くとは限らない可能性に焦点を移しています。

## Top2: 並列した動名詞句を含む長い主語 [T1 / HEAVY] 段落P2  (評価順位2 / id: `g2981f58e59`)

> Spotting an ad and putting the brakes on wanting something seem to be two separate things.

- 教える価値: 複数の動名詞句がandで結ばれて主語となり、複数形の動詞に続くことを見分ける。
- 読み違えやすい点: 文頭の動名詞句を主語と取らず、somethingを主語と見てしまうおそれがある。

### 解説(学習ページに載る全文)

【日本語訳】
広告だと見抜くことと、何かを欲しいという気持ちにブレーキをかけることは、別々のことのようです。

【文法・構文の仕組み】
主語は、動名詞句の **Spotting an ad** と **putting the brakes on wanting something** を **and** で並べたものです。前者は「広告だと見抜くこと」、後者は「何かを欲しいという気持ちにブレーキをかけること」を表します。

主語が長くても、文の中心となる動詞は **seem** です。その後の **to be two separate things** が「別々の二つのことのようだ」という内容を示します。なお、**putting the brakes on** は「ブレーキをかける、抑える」という表現で、**on** の後ろの **wanting something** は「何かを欲しがること」です。

【意味・ニュアンス・表現効果】
この文は、広告だと気づくことと、その広告を見て生まれる「欲しい」という気持ちを抑えることを、別の働きとして示しています。**seem to be** を使っているため、「完全に別だ」と断定するより、「別々のことのように思える」という言い方になっています。

(他2件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 53adab857b1545293f05c2cfe77b301f8495b0745f8af70d480a8172b85d187b --by <名前> --choice pick --ids g6f66e2d3d5 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 53adab857b1545293f05c2cfe77b301f8495b0745f8af70d480a8172b85d187b --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 53adab857b1545293f05c2cfe77b301f8495b0745f8af70d480a8172b85d187b --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 53adab857b1545293f05c2cfe77b301f8495b0745f8af70d480a8172b85d187b --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
