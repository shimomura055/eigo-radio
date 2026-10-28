# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `03d1c3937fd03ab9` / 本文sha: `b7562f850221` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑似分裂文 [T1 / CLEFT] 段落P4  (評価順位1 / id: `gd44f8c31a0`)

> What we are looking at is shrinkage in the later part of the Moon’s history, left by relatively recent faults.

- 教える価値: What節が主語になる疑似分裂文では、be動詞の前後の要素の役割を見分ける。
- 読み違えやすい点: What節が主語なのに、後ろの shrinkage を主語と取り違える可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
私たちが見ているのは、月の歴史の後半に比較的新しい断層によって残された収縮です。

【文法・構文の仕組み】
これは疑似分裂文で、文の主語にあたる **What we are looking at** が「私たちが見ているもの」を表し、**is** の後ろの **shrinkage ...** がその中身を説明しています。

What節の中では、前置詞 **at** の目的語が **What** です。つまり **we are looking at What**（私たちは何かを見ている）に相当する内容が、**What** を先頭に置いて表されています。

**in the later part of the Moon’s history** は「月の歴史の後半に」を表し、**left by relatively recent faults** は「比較的新しい断層によって残された」という説明を **shrinkage** に加えています。

【通常の表現・語順との比較】
比較用：**We are looking at shrinkage in the later part of the Moon’s history, left by relatively recent faults.**

この語順では「私たちは……を見ている」と述べます。一方、本文の形は **What we are looking at** を先に置き、「私たちが見ているものは何か」を示してから、その答えを **shrinkage** で明らかにしています。

【意味・ニュアンス・表現効果】
この文は、話題にしているものを「月の収縮」とだけ広く述べるのではなく、月の歴史の後半に、比較的新しい断層によって残された収縮だと特定しています。疑似分裂文によって、「ここで見ているものは何か」という点に焦点が当たります。
=====

## Top2: 疑似分裂文 [T1 / CLEFT] 段落P6  (評価順位2 / id: `g33c163c321`)

> Just hearing that might make your shoulders ache, but what matters is not its weight; it is how well it keeps heat in.

- 教える価値: What節を主語とする疑似分裂文では、be動詞の前後を区切って主語と補語を判別する。
- 読み違えやすい点: What matters が主語なのに、後ろの its weight を主語と取り違える可能性がある。

### 解説(学習ページに載る全文)

【日本語訳】
それを聞いただけで肩が痛くなりそうだが、大切なのはその重さではなく、どれだけ熱を内部に保てるかだ。

【文法・構文の仕組み】
「what matters」が「大切なこと」という意味で、最初の「is」の主語になっています。「what」はここでは「何」ではなく、「～すること・もの」を表します。そのため「what matters is not its weight」は「大切なのはその重さではない」という意味です。

セミコロンの後の「it is how well it keeps heat in」は、何が大切なのかを言い直して具体化しています。「how well it keeps heat in」は「どれだけ熱を内部に保てるか」という意味のまとまりで、後半の「is」の後に置かれています。

【通常の表現・語順との比較】
比較用：The thing that matters is not its weight but how well it keeps heat in.
このように言い換えると、「大切なこと」を「The thing that matters」と名詞句で表しています。元の文では「what matters」を主語にし、何が大切かを後ろで示しています。

【意味・ニュアンス・表現効果】
「not its weight; it is how well it keeps heat in」と、重さを否定したうえで、熱をどれだけ保てるかを重要な点として示しています。岩の層について、重さそのものではなく、熱を保つ働きが焦点だと読者に伝える形です。
=====

(他5件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b --candidates-sha 03d1c3937fd03ab960a644f574839db725dc6b94848c939d2c9844d285c23140 --by <名前> --choice pick --ids gd44f8c31a0 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b --candidates-sha 03d1c3937fd03ab960a644f574839db725dc6b94848c939d2c9844d285c23140 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b --candidates-sha 03d1c3937fd03ab960a644f574839db725dc6b94848c939d2c9844d285c23140 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b --candidates-sha 03d1c3937fd03ab960a644f574839db725dc6b94848c939d2c9844d285c23140 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
