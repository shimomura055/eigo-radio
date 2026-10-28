# Human Review 依頼(統合)

待機は1回です。下のKP(単語・表現)と文法(Part 2)の**すべて**に操作してから、制作コマンドを**同じまま1回だけ**再実行してください。
(不在なら明示宣言: `py er119_kp_human_review_cli_01.py declare-absent --runs <run> --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`。この宣言はKPと文法の両方に、このrunのこの候補roundだけ効きます)

---
## KP(level=a2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/key_phrases/kp_human_review_request.md)

# KP Human Review 依頼(a2) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `4514a7ce9ecc7106` / 本文sha: `f456110d37df`
- あなたの作業: KPに使う最大3件と、単語解説に使う最大5件(KP3件を含む)を選びます。
- 選ばない候補は『NG』にもできます(NGは以後の再生成でも復活しません)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけ)。

| 番号 | AI推奨 | 英語表現(used_form) | 本文中の意味 | 出典文 | AI理由 | 旗 |
|---|---|---|---|---|---|---|
| 1 | KP | shoving match | 激しい押し合い | The cliffs are a record of a huge "shoving match" cut into the Moon's surface | 押し合いの争いを表す、比喩的で生き生きした表現です。 |  |
| 2 | KP | under the same conditions | 同じ条件で | These numbers were not measured under the same conditions | 実験や比較で「同じ条件下で」を表す定型表現です。 |  |
| 3 | KP | hold heat in | 熱を逃がさない | What matters is how well it holds heat in | 熱を内部に保つ意味の句動詞表現です。 | 重複: 5 |
| 4 | 単語 | work out | 割り出す | Using the map, the team worked out how much the Moon had shrunk | 計算・検討して答えを導き出す句動詞です。 | 重複: 8 |
| 5 |  | insulation | 断熱材 | The team thinks a thick layer of rock with many gaps may have worked like insulation | 断熱材・断熱を表す、科学や建築で役立つ語です。 | 重複: 3 |
| 6 | 単語 | shrinkage | 縮み | The shrinkage we can see comes from the later part of the Moon's history | 縮小・収縮を表す名詞で、幅広い文脈で使えます。 |  |
| 7 |  | radius | 半径 | They estimated that its radius had become about 42 to 46 meters smaller | 半径を意味し、数学や科学の文脈で頻出します。 |  |
| 8 |  | estimate | だいたいの値を出す | They estimated that its radius had become about 42 to 46 meters smaller | 数値や規模を推定する際に使う学術的な語です。 | 重複: 4 |
| 9 |  | fault | 断層 | It was left by faults that formed fairly recently | 地質学の断層や一般的な欠陥を表す語です。 |  |

## 操作(コマンド)

- 状況確認: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01`
- AI推奨を了承: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --accept-ai --candidates-sha 4514a7ce9ecc7106775fd2dbf4390fdafda6095d41b5dd636c55ec71c7831008 --by <名前>`
- 選択: `py er119_kp_human_review_cli_01.py select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --kp 1,2,3 --vocab 1,2,3,4,5 [--ng 6:理由] --by <名前>`
- 選び直し(NG付き): `py er119_kp_human_review_cli_01.py reselect --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --ng 4:理由 --by <名前>`(上限2回)
- 不在として進める(明示宣言。このrun・この候補round限り): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(supportの再生成・再選定は行われません)。

---
## 文法(Part 2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/study_text/grammar_human_review_request.md)

# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `b6e0b8756cfb1a1d` / 本文sha: `c56cc8f2d39f` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑似分裂文 [T1 / CLEFT] 段落P6  (評価順位1 / id: `gfd3885578b`)

> What matters is how well it holds heat in.

- 教える価値: Whatで始まる節が主語となり、isの後にその内容を示す語句が続く形を読む。
- 読み違えやすい点: What mattersを疑問文の一部のように取り、文全体の主語として読まないことがある。

### 解説(学習ページに載る全文)

【日本語訳】
重要なのは、それがどれだけ熱を内部に閉じ込めるかだ。

【文法・構文の仕組み】
この文は疑似分裂文です。文頭の **What matters**（重要なこと）が主語に当たる節で、**is** の後ろに、その「重要なこと」の具体的な内容 **how well it holds heat in**（それがどれだけ熱を閉じ込めるか）が置かれています。

**how well** は「どれだけうまく・効果的に」という意味です。**hold heat in** は「熱を中に保つ、熱を外に逃がさない」という表現です。

【通常の表現・語順との比較】
比較用：**How well it holds heat in matters.**  
こちらは「それがどれだけ熱を閉じ込めるかが重要だ」と、重要なことを文頭に置いています。元の文は **What matters** を先に置き、「重要なのは何か」を示してから、その答えを続ける形です。

【意味・ニュアンス・表現効果】
前の文では、重さは重要ではないと述べています。この文は、それに続けて、重さではなく「どれだけ熱を閉じ込めるか」が重要だと焦点を絞っています。後の文では、すき間の多い厚い岩石層が断熱材のように働いた可能性が述べられ、熱を閉じ込めるという見方につながります。
=====

## Top2: 比較基準を含むmore ... than ...構文 [T1 / CMP] 段落P9  (評価順位2 / id: `g9713f5a27c`)

> There is more to the Moon’s way of dressing than you can see.

- 教える価値: more ... than ...では、than節が比較の基準として何を示すかを補って読む。
- 読み違えやすい点: than以下を単に「あなたが見られるもの」と読むだけでなく、何が比較されているのかを補わないと文の比較関係を取り違えうる。

### 解説(学習ページに載る全文)

【日本語訳】
月の「装い」には、目に見えるもの以上のものがあります。

【文法・構文の仕組み】
“There is more to A than B” は、「AにはBから分かる以上のものがある」という形です。この文の “more” は、月の “way of dressing”（装い方）に関わる事柄が、目に見える範囲だけに限られないことを表しています。

“than you can see” は、何と比べて「もっと」なのかを示す部分です。ここでは “you can see”（あなたに見える範囲）が比較の基準になっています。

【意味・ニュアンス・表現効果】
月の表面を眺めるだけでは分からないことにも目を向けるよう促す表現です。直前の文では、丸い姿の下にある「rock coat（岩石のコート）」を想像するよう述べています。この文も、月の見た目だけでなく、その下にある岩石層の働きにも注目させています。

(他3件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --candidates-sha b6e0b8756cfb1a1d110d00febefba9846e6c7231ceebce7a8d67c02c493486c6 --by <名前> --choice pick --ids gfd3885578b --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --candidates-sha b6e0b8756cfb1a1d110d00febefba9846e6c7231ceebce7a8d67c02c493486c6 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --candidates-sha b6e0b8756cfb1a1d110d00febefba9846e6c7231ceebce7a8d67c02c493486c6 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2 --candidates-sha b6e0b8756cfb1a1d110d00febefba9846e6c7231ceebce7a8d67c02c493486c6 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。

---
## 文法(Part 2)
(個別の依頼書: er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/b1b/study_text/grammar_human_review_request.md)

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

