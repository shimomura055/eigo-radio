# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `cfa2cb087d888713` / 本文sha: `f1f800394584` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 強調構文（it-cleft） [T1 / CLEFT] 段落P3  (評価順位1 / id: `g3506499603`)

> This time, it’s adults who are being asked whether they want to welcome a pet.

- 教える価値: it is ... who の形では、who節で示される人や物が焦点になる。
- 読み違えやすい点: itをペットなどを指す普通の主語と捉え、成人に焦点を当てる強調構文だと見落とすことがある。

### 解説(学習ページに載る全文)

【日本語訳】
今回は、ペットを迎えたいかどうかを尋ねられているのは大人です。

【文法・構文の仕組み】
「it’s adults」が強調されている部分で、「大人こそが」という焦点を示しています。続く「who are being asked whether they want to welcome a pet」は、その大人たちがどんな人なのかを説明しています。「are being asked」は受け身で「尋ねられている」、「whether they want to welcome a pet」は「ペットを迎えたいかどうか」です。

【通常の表現・語順との比較】
比較用：This time, adults are being asked whether they want to welcome a pet.
通常の語順では「大人たちが尋ねられている」と述べます。元の文では「it’s adults who ...」の形にすることで、尋ねられているのが大人だという点を前面に出しています。

【意味・ニュアンス・表現効果】
この文は、ペットを迎えたいかどうかを尋ねられているのは大人だと示しています。前の文ではアプリストアの説明に「利用者は18歳以上でなければならない」とあるため、ここでは「誰が尋ねられているのか」に焦点を当てています。「This time」は「今回は」という意味です。

## Top2: 疑問詞節を主語にする構文 [T1 / HEAVY] 段落P7  (評価順位2 / id: `g2bce64b91a`)

> When it will become available in Japan and other places had not been announced by the time of reporting.

- 教える価値: whenで始まる節が名詞節として文の主語になり、後ろに主節の動詞が続くことがある。
- 読み違えやすい点: When節を時を表す副詞節と捉え、文全体の主語ではなく背景情報だと読み違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
日本やほかの地域でいつ利用可能になるのかは、報道時点までに発表されていなかった。

【文法・構文の仕組み】
文頭の **When it will become available in Japan and other places** が、文全体の主語です。**When** は「いつ」を表し、この部分は「いつ利用可能になるのか」という疑問の内容を表す節になっています。節の中は **it will become available** という語順で、直接の疑問文のように **will it** とはなっていません。

主節の動詞は **had not been announced** です。これは受け身の過去完了形で、「発表されていなかった」という意味です。**by the time of reporting** は「報道時点までに」を表し、発表されていない状態の期限を示しています。

【通常の表現・語順との比較】
比較用の直接疑問文なら、**When will it become available in Japan and other places?** となり、**will** が **it** の前に置かれます。一方、この英文では疑問の内容を表す節が主語になっているため、節の中は **When it will become available ...** の語順です。

【意味・ニュアンス・表現効果】
この文が伝えているのは、提供が始まること自体ではなく、「いつ始まるのか」が報道時点ではまだ公表されていなかったということです。疑問の内容を文頭に置くことで、発表されていなかった情報の焦点が提供開始時期に当たっています。

(他1件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b --candidates-sha cfa2cb087d8887131b3e487806987929daa42f60ac876b886083c7bea027c737 --by <名前> --choice pick --ids g3506499603 --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b --candidates-sha cfa2cb087d8887131b3e487806987929daa42f60ac876b886083c7bea027c737 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b --candidates-sha cfa2cb087d8887131b3e487806987929daa42f60ac876b886083c7bea027c737 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b --candidates-sha cfa2cb087d8887131b3e487806987929daa42f60ac876b886083c7bea027c737 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
