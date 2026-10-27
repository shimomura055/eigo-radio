# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `48fda7fcb93dedab` / 本文sha: `dc291d4af4f5` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): what疑似分裂文 [T1 / CLEFT] 段落P4  (評価順位1 / id: `gcc2541c879`)

> The island went back to how it was before, but what the AI had discovered was not erased.

- 教える価値: what節が主語となり、後ろのbe動詞以降がその内容を述べる形を読む。
- 読み違えやすい点: what節全体が主語なのに、had discoveredを主節の動詞と取り、was not erasedとのつながりを取り違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
島は以前の状態に戻ったが、AIが発見したことは消去されなかった。

【文法・構文の仕組み】
`what the AI had discovered` 全体が主語です。ここでの `what` は疑問の「何」ではなく、「AIが発見したこと・もの」を表します。`the AI had discovered` はその内容を示し、`had discovered` は過去完了形です。

主節の述語は `was not erased`（消去されなかった）です。つまり、「AIが発見したこと」が「消去されなかった」という文の組み立てです。

【通常の表現・語順との比較】
比較用：`The AI's discovery was not erased.`（AIの発見は消去されなかった。）

この比較用の文も近い意味ですが、本文の `what the AI had discovered` は「AIが発見した内容」を節の形で表し、それを文の主語にしています。

【意味・ニュアンス・表現効果】
`but` によって、「島が元に戻ったこと」と「AIが発見したことが残ったこと」が対比されています。島の状態はリセットされた一方で、AIが発見した内容は消去されなかった、という違いに焦点が置かれています。
=====

## Top2: that節を含む重い並列主語 [T1 / HEAVY] 段落P7  (評価順位2 / id: `g080d9d1a1f`)

> The fact that the experienced group did better and the fact that removing a particular memory lowered its score need to be looked at separately.

- 教える価値: that節を含む長い主語が続くとき、主語の範囲を確定してから主節の動詞を探す。
- 読み違えやすい点: 長い主語の中にあるloweredを主節の動詞と取り、主節の動詞needを見落とすことがある。

### 解説(学習ページに載る全文)

【日本語訳】
経験者グループの成績がよかったことと、特定の記憶を取り除くとそのグループの得点が下がったことは、分けて検討する必要があります。

【文法・構文の仕組み】
主語は、**the fact that the experienced group did better**（経験者グループの成績がよかったという事実）と、**the fact that removing a particular memory lowered its score**（特定の記憶を取り除くと得点が下がったという事実）の二つです。この二つが **and** で結ばれ、長い主語を作っています。

それぞれの **that** は「〜という事実」の内容を示しています。二つの事実を述べたあとに続く **need** が主節の動詞で、**to be looked at separately**（別々に検討される）と合わせて「別々に検討する必要がある」という意味になります。

【意味・ニュアンス・表現効果】
二つの結果を一つの結論にまとめず、別々に考える必要があると述べています。経験者グループの成績がよかったことと、特定の記憶を取り除いた後に得点が下がったことを区別することで、遊びそのものの効果を判断するには慎重な検討が必要だという流れにつながっています。
=====

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01 --level b1b --candidates-sha 48fda7fcb93dedab711cff1b8573757472970655cbbe1c7ed0a5d0a94db4d163 --by <名前> --choice pick --ids gcc2541c879 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01 --level b1b --candidates-sha 48fda7fcb93dedab711cff1b8573757472970655cbbe1c7ed0a5d0a94db4d163 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01 --level b1b --candidates-sha 48fda7fcb93dedab711cff1b8573757472970655cbbe1c7ed0a5d0a94db4d163 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01 --level b1b --candidates-sha 48fda7fcb93dedab711cff1b8573757472970655cbbe1c7ed0a5d0a94db4d163 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
