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
