# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `14ff473058f5b54c` / 本文sha: `0ef561d7afa7` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 比較級とwhen節による比較基準 [T1 / CMP] 段落P5  (評価順位1 / id: `geaa1c64605`)

> This was more often than when the book was only near the top of the search results.

- 教える価値: 比較級の後にwhen節が続く場合、何の頻度をどの条件下で比べているかを補って読む。
- 読み違えやすい点: than when以下を単なる時の比較と捉え、前半の選択頻度と別条件での選択頻度を比べていることを取り違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
この本が選ばれる頻度は、本が検索結果の上位付近に置かれているだけの場合よりも高かった。

【文法・構文の仕組み】
「more often」は「より頻繁に」という意味で、人々が本を選ぶ頻度を表しています。「than when ...」は、その頻度を比べる基準を示します。ここでは「when the book was only near the top of the search results」が、本が検索結果の上位付近に置かれていた別の条件を表しています。

「This」は、前の文で述べられた、このテストでの選択頻度を指しています。文の意味は「このテストでの選択頻度は、本が検索結果の上位付近に置かれていたときの選択頻度より高かった」ということです。

【通常の表現・語順との比較】
比較用：People chose the book more often than they did when it was only near the top of the search results.

比較用の文では「than they did」と、比較の基準となる「そのときに選んだ頻度」を明示しています。元の英文では、この部分を省いて「than when ...」と簡潔に表しています。

【意味・ニュアンス・表現効果】
「more often」によって、単に二つの条件を並べるのではなく、このテストでの選択頻度が、検索結果の上位付近に本が置かれた場合より高かったことに焦点が当たっています。前の文で示された選択頻度を、別の表示条件と比較する表現です。

## Top2: 比較級とwhen節による比較基準 [T1 / CMP] 段落P5  (評価順位2 / id: `gb73f6ff163`)

> It was also more often than when chat-based AI gave a neutral description.

- 教える価値: 比較級の後にwhen節が続く場合、何の頻度をどの条件下で比べているかを補って読む。
- 読み違えやすい点: than when以下を単なる時の比較と捉え、前半の選択頻度と別条件での選択頻度を比べていることを取り違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
その選択が起きた頻度も、チャット型AIが中立的な説明をした場合より高かった。

【文法・構文の仕組み】
“It was also more often” の “more often” は「より頻繁に」「起きる頻度がより高く」を表しています。ここで比べているのは、選択が行われた頻度です。

“than when chat-based AI gave a neutral description” は比較の基準を示し、「チャット型AIが中立的な説明をした場合よりも」という意味です。“than” の後ろに “when” で始まる節を置くことで、頻度を比べる条件を表しています。

【意味・ニュアンス・表現効果】
この文は、ある条件での選択頻度を、中立的な説明が提示された場合の頻度と比べています。“also” があるため、この比較は前の内容に加えて示されています。

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 14ff473058f5b54cd4562abbd4371a7ec856701ec8fdd91d124538b5c8c98e4f --by <名前> --choice pick --ids geaa1c64605 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 14ff473058f5b54cd4562abbd4371a7ec856701ec8fdd91d124538b5c8c98e4f --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 14ff473058f5b54cd4562abbd4371a7ec856701ec8fdd91d124538b5c8c98e4f --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2 --candidates-sha 14ff473058f5b54cd4562abbd4371a7ec856701ec8fdd91d124538b5c8c98e4f --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
