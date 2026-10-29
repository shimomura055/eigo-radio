# Part 2 文法解説 Human Review 依頼(Standard) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `4fff2225e1640ed4` / 本文sha: `2c4b13c306f5` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑似分裂文（it-cleft） [T1 / CLEFT] 段落P3  (評価順位1 / id: `g6ca5a9eb3c`)

> But was it only the name change that I didn’t like?

- 教える価値: it-cleftでは、itの後の焦点部分とthat節を対応させて、何が焦点化されているかを読む。
- 読み違えやすい点: itを通常の主語と捉え、the name changeがthat以下で焦点化されている分裂文の構造を取り違えることがある。

### 解説(学習ページに載る全文)

【日本語訳】
でも、私が嫌だったのは名前が変わったことだけだったのだろうか？

【文法・構文の仕組み】
これは疑似分裂文（it-cleft）の疑問文です。疑問文なので、平叙文の *It was ...* にあたる部分が *Was it ...?* の語順になっています。

*the name change* が焦点部分で、「名前の変更」を指します。*only* はこの部分にかかり、「名前の変更だけ」という限定を表します。続く *that I didn’t like* は、何が嫌だったのかを説明する節です。つまり文全体は「私が嫌だったものは、名前の変更だけだったのか」と問いかけています。

【通常の表現・語順との比較】
比較用：*But did I dislike only the name change?*

この語順でも「名前の変更だけが嫌だったのか」と尋ねられます。一方、本文の形では *the name change* を焦点として前に出し、「嫌だったのはそれだけなのか」と対象を強調しています。

【意味・ニュアンス・表現効果】
前の文は *I got really upset.*（私はひどく動揺した）です。この疑問文は、その動揺の理由が名前の変更だけだったのかを話者が問い直すものです。*only* によって「ほかにも嫌だったことがあったのではないか」という可能性が示され、後の *I think I really wanted him to stay close.* へとつながります。=====

## Top2: 埋め込み節を含む動名詞句主語 [T1 / HEAVY] 段落P2  (評価順位2 / id: `g732a87bdfd`)

> But fitting in with what each family thought was normal was harder than changing my last name.

- 教える価値: 埋め込み節を含む長い動名詞句が主語となる文では、主語のまとまりを確定してから主節の動詞を探す。
- 読み違えやすい点: what節の中のwas normalを主節の述語と取り、後ろのwas harderを別の主節の動詞のように読んでしまうことがある。

### 解説(学習ページに載る全文)

【日本語訳】
それぞれの家族が普通だと思っていたことに合わせるのは、姓を変えることより難しかった。

【文法・構文の仕組み】
文の主語は、文頭の **fitting in with what each family thought was normal** 全体です。**fitting in** は動名詞で、「周囲に合わせること」という意味です。

その後ろの **with what each family thought was normal** は、「それぞれの家族が普通だと思っていたことに」という部分です。**what each family thought was normal** は「それぞれの家族が普通だと思っていたこと」を表します。ここで **what** は **was normal** の主語にあたります。

主語のあとに続く **was harder** が主節の動詞を含む部分で、「より難しかった」という意味です。**than changing my last name** は「姓を変えることよりも」と比較の基準を示しています。

【通常の表現・語順との比較】
比較用：**It was harder to fit in with what each family thought was normal than to change my last name.**

この形では、形式上の主語 **It** のあとに「何が難しかったか」を置いています。一方、本文では「家族に合わせること」を表す動名詞句そのものを主語にしています。

【意味・ニュアンス・表現効果】
「姓を変えること」と「それぞれの家族の普通に合わせること」を比べ、後者のほうが難しかったと述べています。動名詞句を主語にすることで、何が難しかったのか、つまり家族の考え方や習慣に合わせることが文の中心に置かれています。
=====

(他2件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice pick --ids g6ca5a9eb3c --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er121_output/family_y_production_01/surname_choice/run_01 --level a2 --candidates-sha 4fff2225e1640ed4a91956e4ec093f0e82b7fe1d8e66f423e8f372983507ab89 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er121_output/family_y_production_01/surname_choice/run_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er121_output/family_y_production_01/surname_choice/run_01 --level a2`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er121_output/family_y_production_01/surname_choice/run_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
