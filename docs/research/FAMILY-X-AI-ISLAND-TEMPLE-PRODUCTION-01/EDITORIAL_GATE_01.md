# EDITORIAL_GATE_01 (委任_02, 2026-10-26) 判定=分岐B(再生成せずSTOP, API 0)

## 1. 事実(B3入力にユーザー方向性は渡っていたか)
- 正式経路の切り口入力手段は `--theme`(Research/B3のtopic)のみ。`--source-note`は記録専用(runner:481-482「Research promptには使わない」)。theme brief/user hint/angle引数は無い。
- 委任_01のB3は `{topic}`=`--theme`全文を受領(er019_family_x_storyline_b3_fact_selection_01.py:53-56 USER_PROMPT_TEMPLATE、runner:544 `run_storyline_b3(client, args.theme, ...)`)。theme.txt(sha256 22736ccd...)に、タイトル案(§1)、神殿/記念碑/大聖堂/巡礼のログ上の語、make-believe解釈の区別、プレプリント、断定禁止、「研究の本質は目標なしの探索や遊びが学習・課題遂行につながる可能性。意外性のあるストーリーとして楽しく」が既に入っている。
- Research ledgerにも神殿系Factは入っていた: F06記念碑(verified_fact_ledger.txt:34)、F07 Cathedral(:41)、F08「神殿を歩く/巡礼」(:49)。いずれVERIFIED。

## 2. B3の選択結果(旧版保全)
- B3採用: F03,F04,F07,F10,F11,F14,F19(selected_brief.md sha b00427b6...)。不採用: F06(記念碑)、F08(神殿を歩く/巡礼)。Storyline=「具体的な課題のない島でAIは『大聖堂』の周囲を跳ぶなど遊びのような活動を見せ、経験群は後の塔づくりで好成績…」。つまりB3自体は大聖堂を入口に置いたが、神殿/巡礼(F08)は落とした。
- Writer/R2が「攻略メモ(リセットされる島と引き継がれる記憶)」を主軸に再構成し、大聖堂は第3段落の例示1つに縮小(ARTICLE_JA_R2_01.md:7)。神殿/記念碑/儀式/30時間/プレプリントは本文0件。
- 旧版保全: a2 article sha 90c66293...、b1b article sha a2951b9b...、ARTICLE_JA_R2_01.md sha 6dd8973b...(ARTICLE_*_01.mdとして残置)。

## 3. 判定
- 入力手段はtopicのみで、方向性は既に渡されていた=分岐(B)。同じtopicで`--regenerate-stage storyline_b3`を再実行しても、B3は非決定的で同じ入力の再抽選に過ぎず、(a)F08を採るか (b)Writer/R2が主軸を保つかは保証できない。切り口の偏りの主因はB3単独ではなくB3後のWriter/R2段(主軸再構成)にも在る。
- 切り口入力を増やす手段は、topicへの追記(既存引数の内容変更なので再実行可否はFable判断)か、Prompt/B3選定ルール変更(ユーザー承認要)のどちらか。委任文の規則(Bは再生成せずSTOP)に従い実行しない。

## 4. 選択肢(推奨付き)
1. 現版でHR→完走し、最終試聴でユーザー判断。追加費用0(ただし切り口はユーザー意図とずれる)。
2. theme.txtに「神殿を歩く/巡礼(F08)・記念碑(F06)を事実とログ上の語として採用候補にし、最もユーザーが魅力とした展開を主軸にせよ」等の強調を足して`--regenerate-stage storyline_b3`+`--regenerate-stage writer`を再実行(約47円+writer段+scaffold、Cap内、音声前なので最安)。topic文字列の変更はPrompt本文編集ではなく既存入力の使い方の範囲と解釈できるが、B3/Writer非決定性のため成否保証なし。**推奨**(Fableが「topic追記は既存入力手段の範囲内」と判断する場合)。
3. B3選定Promptに「ユーザー指定の魅力を主軸に」ルールを加える→Prompt変更、ユーザー承認必須(非推奨、全記事へ波及)。
