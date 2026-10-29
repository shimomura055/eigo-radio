# Part 2 文法解説 Human Review 依頼(Advanced) round 1

- 状態: PENDING_REVIEW / candidates_sha256: `2e0759223e893431` / 本文sha: `d1c87a38d469` / 再選定 0/2回・再抽出 0/1回
- あなたの作業: 下のTop1・Top2(AI評価順位・最大2件)の文法名と解説を読み、学習に載せる文法を**1件だけ**選びます(適切なものが無ければ0件=omit。2件同時選択は不可。AI推奨=Top1)。何もしなければ制作は止まったままです(自動確定は明示の不在宣言があるときだけで、その場合はAI推奨1件のみ)。

## AI推奨(Top1): 疑似分裂文 [T1 / CLEFT] 段落P6  (評価順位1 / id: `g169734270c`)

> But what stands out in this experiment is the guide’s task, not just its seat.

- 教える価値: What節が文の主語となり、be動詞の後ろに焦点となる内容が置かれる形を読み取る。
- 読み違えやすい点: what節を主語ではなくstand outの目的語のように捉え、isの後ろのthe guide’s taskを主語と取り違えるおそれがある。

### 解説(学習ページに載る全文)

【日本語訳】
しかし、この実験で目を引くのは、ガイドの席だけではなく、ガイドが担う仕事だ。

【文法・構文の仕組み】
この文は、**what節を主語にし、be動詞の後ろに焦点となる内容を置く疑似分裂文**です。

主語は **what stands out in this experiment**（この実験で目立つもの）です。ここでの **what** は「何」ではなく、「〜するもの・こと」という意味で、節全体が文の主語になっています。**is** の後ろにある **the guide’s task** が、その「目立つもの」の具体的な内容です。さらに **not just its seat** が続き、「ガイドの席だけではない」と補っています。

【通常の表現・語順との比較】
**比較用：** *The guide’s task, not just its seat, stands out in this experiment.*

こちらは「ガイドの仕事が目立つ」と先に述べる語順です。元の文では **what stands out in this experiment** を先に置き、「目立つものは何か」という問いかけの形を作ってから、**the guide’s task** を答えとして示しています。

【意味・ニュアンス・表現効果】
前の文では、広告をめぐる競争が掲載位置の争いとして描かれています。それを受けてこの文は、目立つ点は単にガイドの席の位置ではなく、ガイドが担う仕事だと焦点を移しています。疑似分裂文によって「この実験で何が重要なのか」を示す内容が、文の後半で明確に提示されています。

## Top2: 従属節内の疑似分裂文 [T1 / CLEFT] 段落P6  (評価順位2 / id: `g178b97cd7b`)

> It is as if we were looking at a map of a store’s layout, then realized that what we should be looking at was the work instructions given to the staff.

- 教える価値: 埋め込まれた疑似分裂文では、what節がbe動詞の前の主語となり、後ろに焦点となる名詞句が続く。
- 読み違えやすい点: what節をwasの後ろに続く補語のように捉え、実際にはその節がwasの主語であることを取り違えるおそれがある。

### 解説(学習ページに載る全文)

【日本語訳】
まるで、店の配置図を見ていた私たちが、そのあと、本当に見るべきなのはスタッフに渡された作業指示書だと気づいたかのようです。

【文法・構文の仕組み】
`realized that ...` の `that` 以下に、疑似分裂文 `what we should be looking at was the work instructions given to the staff` が入っています。

この部分では、`what we should be looking at`（私たちが見るべきもの）が `was` の主語、`the work instructions given to the staff`（スタッフに渡された作業指示書）が補語です。つまり、「私たちが見るべきものは、スタッフに渡された作業指示書だった」という形です。`given to the staff` は `the work instructions` を説明しています。

また、`as if` の後ろでは、`we were looking at ...` と `then realized ...` が `we` を主語として続いています。店の配置図を見ていた状態から、見るべきものに気づく、という流れを表しています。

【通常の表現・語順との比較】
比較用：`We should be looking at the work instructions given to the staff.`
こちらは「私たちはスタッフに渡された作業指示書を見るべきだ」と、主語 `we` から述べる通常の語順です。本文の文では `what we should be looking at` を先に置くことで、「見るべきものは何か」という枠を作り、その答えを `the work instructions` として示しています。

【意味・ニュアンス・表現効果】
この文は、店の配置図を見ることにたとえて、「注目すべきなのは配置ではなく、スタッフへの作業指示だ」と伝えています。疑似分裂文によって「見るべきものは何か」が前面に出て、答えにあたる `the work instructions` がはっきり示されています。直前の文の「ガイドの仕事が目立つのであって、座席だけではない」という趣旨を、配置図と指示書の対比で言い換えています。

(他1件は非表示: AI評価のTop1/Top2(先頭2件)だけを提示しています。reselectすると提示中の候補をNGにして次順位が新しいTop1/Top2になります)

## 操作(コマンド。`--by` は操作者名。`--level`は必須)

- AI推奨(候補1)だけを選ぶ(了承): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 2e0759223e893431398df585fbba23455631907bc396e97368154d5bdc7d9837 --by <名前> --choice pick --ids g169734270c --accept-ai`
- 1件を選ぶ(Top1以外は理由必須。2件同時選択は不可): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 2e0759223e893431398df585fbba23455631907bc396e97368154d5bdc7d9837 --by <名前> --choice pick --ids <id> --reason <理由>`
- 選び直し(提示中の候補をNGにして次順位へ。理由必須・上限あり): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 2e0759223e893431398df585fbba23455631907bc396e97368154d5bdc7d9837 --by <名前> --choice reselect --reason <理由>`
- 今回は文法解説を出さない(理由必須): `py er119_kp_human_review_cli_01.py grammar-select --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b --candidates-sha 2e0759223e893431398df585fbba23455631907bc396e97368154d5bdc7d9837 --by <名前> --choice omit --reason <理由>`
- 状況: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01` / 表示: `py er119_kp_human_review_cli_01.py grammar-show --run er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --level b1b`
- 不在として進める(明示宣言。このrun・この候補round限り。AI推奨1件のみ採用): `py er119_kp_human_review_cli_01.py declare-absent --runs er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01 --reason <理由> --by <名前> [--user-ref <ユーザー発言の参照>]`

再開: 上の操作の後、制作コマンドを**同じコマンドのまま**再実行してください(候補抽出・解説生成・supportの再生成は行われません)。
