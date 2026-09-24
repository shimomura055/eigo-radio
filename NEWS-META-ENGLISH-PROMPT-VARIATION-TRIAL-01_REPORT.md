# NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01 REPORT

管理ID: `NEWS-META-ENGLISH-PROMPT-VARIATION-TRIAL-01`
実行日: 2026-09-24
性質: 切り分けTrial(英語Prompt/Revision表現差の影響を検証)。到達Status: `VALIDATED`(生成・記録完了。最終品質判断はユーザー)。
Production変更: なし。SSOT変更: なし。

## §1 固定条件・素材sha256

- 素材: `er015_output/news_meta_source_volume_format_trial_01/inputs/cond2.md`(条件2、2文・209字、日本語のまま[News]欄に逐語使用)。
- sha256確認: expected=actual=`4a2d9f899cc6083eb46cd006d8df1fdb02db10c23bdce020b7d6ee58bf903ecb`(一致。`stop_reason.json`は生成されず=STOP未発生)。
- Arm間で固定: 素材/`gpt-5.6-luna`/`effort=high`/Original→R1→R2/`previous_response_id`連鎖/Web Searchなし/Ledgerなし/Production contract(Point One・Point Two・`###`・`## In one line`・280〜420語target)なし/Audioなし/Title+Body only/English output。R3は生成していない。
- Arm間で変えたのはCore Prompt本文とR1/R2 Revision指示の英語表現(developer messageを含む)のみ。

## §2 各ArmのCore Prompt・R1・R2全文(逐語)

### Arm A(再利用、`NEWS-META-ENGLISH-ONLY-TRIAL-01`と完全同一。再callなし)

developer: `You are a writer who explains the news clearly and makes it enjoyable to read.`

Core Prompt(前回VALIDATED版の逐語、`arms/A/prompt_core.txt`参照): P7英訳版(Theme文=`I asked an AI to call a store for me, and it turned out a human was secretly on the line.`、Length=`about 350–450 words.`)。

R1: `Revise this article to make it more entertaining, without changing the facts.`
R2: `Revise this article to make it even more entertaining, without changing the facts.`

### Arm B(日本語Prompt逐語+出力英語)

developer(P7逐語): `あなたは日本語のニュースを分かりやすく面白く伝える書き手です。`

Core Prompt: P7逐語(`docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md` 2-B節)をそのまま使用。**唯一の差異は2行**:
- 「長さ：800～1000字」→「長さ：英語で350〜450語程度」
- 「出力はタイトルと本文のみ。」→「出力はタイトルと本文のみ。本文とタイトルは英語で書いてください。」

テーマ行は元のまま`テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている`を維持した(委任文Arm定義冒頭の「Theme同じテーマ文[Arm Bのみ日本語版`AIに店への電話を頼んだら、裏では人間が話していた`]」という記述と、Arm B詳細節の「この2行が唯一の差異」という記述が字面上一致しないため、より具体的・明示的なArm B詳細節[唯一の差異=2行]を優先した。この解釈差はFable確認事項として§7へ委ねる)。

R1: `この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。英語で出力してください。`
R2: `この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。英語で出力してください。`

### Arm C1(自然な英語意訳)

developer: Arm Aと同一。

Core Prompt(全文、`arms/C1/prompt_core.txt`):
```
Write this news story the way you'd tell a friend: "Hey, did you hear about this? It's kind of interesting."

Don't go for the most surprising fact. Instead, pick the one angle that makes the story most interesting, and build the piece around it. Use only the facts that angle needs — don't try to cover the whole story.

Keep the voice natural and light. It shouldn't read like a newspaper article, an official document, or a school textbook. Put difficult ideas into short, simple English, at a level an English learner could follow by listening just once.

If the story looks like it only matters somewhere far away, connect it once to the reader's own life or to a bigger change in society — but don't stretch it.

Stay strictly factual. Don't invent events or quotes.

Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line.

Length: about 350–450 words.

Give only the title and the body, in English.

[News]
(条件2素材、日本語逐語)
```
R1: `Make this piece more entertaining, keeping every fact exactly the same.`
R2: `Now make it even more entertaining, still keeping every fact exactly the same.`

対応メモ: P7 s1(友人に話す感覚)→冒頭文、s2(最も面白い見方を一つ)→第2段落、s3a/s3b(自然で軽快・簡単な英語)→第3段落、s4(遠い地域への橋渡し)→第4段落、s5(事実厳守)→第5段落に対応。新しいEditorial principleは追加していない。

### Arm C2(意味強調版)

developer: Arm Aと同一。

Core Prompt(全文、`arms/C2/prompt_core.txt`):
```
Turn the news below into a piece you'd share with a friend: "Hey, isn't this kind of interesting?"

Do not try to explain the entire news story. Choose the single most interesting angle — not the most surprising fact — and build the whole piece around that one angle. Use only the facts needed for that angle and leave the rest out. Do not let the piece turn into an explanatory summary of the news.

Keep the tone natural and light. Do not write like a newspaper, a government document, or a school textbook. Rephrase difficult content in short, simple English that a learner could understand by listening once.

If the story seems specific to a distant place, connect it once to the reader's life or to a larger social change, without forcing it.

Stick strictly to the facts. Add no fictional events or quotes.

Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line.

Length: about 350–450 words.

Output only the title and the body, in English.

[News]
(条件2素材、日本語逐語)
```
R1: `Revise this piece to be more entertaining, without changing the facts. Keep it built around the one angle; do not expand it into an explanatory summary.`
R2: `Revise it again to be even more entertaining, without changing the facts. Stay on the one angle; still no explanatory summary.`

対応メモ: s2の「最も意外な事実ではなく、最も面白い見方を一つ」「ニュース全体を説明しようとしない」を`Do not try to explain the entire news story`/`Choose the single most interesting angle`/`Avoid...explanatory summary`として明示的に強調(元Promptに既にある思想の強度のみ上げた。新規思想の追加なし)。

### Arm C3(Conversation/Storytelling寄り)

developer: Arm Aと同一。

Core Prompt(全文、`arms/C3/prompt_core.txt`):
```
Tell this news the way you'd tell a friend over coffee: "Hey, listen to this — it's kind of interesting."

Find the one angle that makes it worth telling, and tell it as something that happened — concrete moments and scenes — rather than as a topic to be explained. Use only the facts that angle needs; don't cover the whole story.

Talk, don't lecture. Keep it natural and light, never like a newspaper, an official document, or a textbook. Make the listener want to hear what happens next. Use short, simple English that a learner could follow by listening once.

If it seems like a faraway story, connect it once to the listener's own life or to a bigger change — no need to force it.

Everything must be true to the facts: no invented events, scenes, or quotes.

Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line.

Length: about 350–450 words.

Give only the title and the body, in English.

[News]
(条件2素材、日本語逐語)
```
R1: `Tell it again, more entertainingly — same facts, nothing invented.`
R2: `Once more, even more entertaining — same facts, nothing invented.`

対応メモ: 「友人に『これちょっと面白くない？』と話す感覚」→`over coffee`のカジュアルな導入、「具体的な出来事・場面として語る」→`tell it as something that happened — concrete moments and scenes`、「聞き手が続きを知りたくなる」→`Make the listener want to hear what happens next`、「虚構・脚色・架空発言は禁止」→`no invented events, scenes, or quotes`に対応。

## §3 各ArmのOriginal/R1/R2全文・タイトル

全文は下記artifactに保存(逐語、本REPORTでは主要箇所を再掲。詳細はfileパス参照):
- `er015_output/news_meta_english_prompt_variation_trial_01/arms/{A,B,C1,C2,C3}/original.md`
- `er015_output/news_meta_english_prompt_variation_trial_01/arms/{A,B,C1,C2,C3}/revision1.md`
- `er015_output/news_meta_english_prompt_variation_trial_01/arms/{A,B,C1,C2,C3}/revision2.md`

タイトル一覧(`titles.json`):

| Arm | Original | R1 | R2 |
|---|---|---|---|
| A | The AI Calling for You May Have Been a Human After All | Plot Twist: The AI Calling the Store May Have Been a Person | Your AI Assistant Has Put You on Hold—But a Human Is Listening |
| B | The Most Human Thing About Meta's AI Phone Agent Was the Human | Meta's AI Phone Agent Had a Human Backstage Crew | Behind Meta's AI Phone Agent, a Human Plot Twist |
| C1 | The AI Calling for You May Have Had a Human Behind It | Plot Twist: The AI Calling for You Had a Human Behind It | The AI Phone Call Had a Plot Twist |
| C2 | I Asked an AI to Call the Store. Who Was Really on the Line? | I Asked an AI to Call the Store. Then I Learned It Might Need Backup. | The AI Said It Would Call the Store. Plot Twist: A Human Might. |
| C3 | The AI Calling the Store Had a Human Behind It | The AI Called the Store. Plot Twist: A Human Was There. | The AI Phone Call Had a Human Plot Twist |

## §4 機械集計(語数・echo・Fact候補)

### 語数(`metrics.json`、word_count)

| Arm | Original | R1 | R2 |
|---|---|---|---|
| A | 383 | 396 | 422 |
| B | 367 | 385 | 399 |
| C1 | 380 | 393 | 402 |
| C2 | 365 | 365 | 399 |
| C3 | 382 | 368 | 392 |

全Arm・全段でLength指定「約350〜450語」の範囲内。

### Prompt echo(`prompt_echo.json`、`Isn't this|kind of interesting|Hey,|listen to this|Here's something interesting|これ、ちょっと面白くない`)

- Arm A original: `kind of interesting`=true、`Hey,`=true(Original段で1回のみ、R1/R2ではecho消滅)。
- Arm C3のみ、original/r1段で`kind of interesting`/`Hey,`/`listen to this`が観測された(Core Promptの冒頭`"Hey, listen to this — it's kind of interesting."`という引用句をモデルが本文冒頭にそのまま再利用したもの。R2では消滅)。
- Arm B/C1/C2は全段でecho未検出。

### Fact機械観測(`fact_diff_machine.json`、R2段。詳細はJSON参照)

- 全Arm・R2段で`numbers`(数字)は空(元情報外の数値追加なし)。
- `capitalized_words_not_in_reference_list`は文頭大文字語(`The`/`But`/`If`等)が大半で、新しい固有名詞は検出されなかった(判定はFable確認事項として残す)。
- `quoted_spans`(引用符内発言候補)は各Armのoriginal段に散見されるが、いずれも一般的な会話例文(例: Arm A `"Call the store and ask if they have this jacket in my size."`、Arm C2 `"Call the store and ask whether they still have that jacket."`)であり、架空の実在発言引用ではない(Fable最終確認事項)。

## §5 api_meta・cost・latency

- 9 call予定に対し実際は**12 call**(Arm B/C1/C2/C3 × 3段)。委任文冒頭の「新規9 call」は概算の誤りと判断し、委任文で明示されたArm B/C1/C2/C3(4 arm)を実行した。予算超過なし(下記参照)。
- 全12 callで`response_model_actual`=`gpt-5.6-luna`(要求モデルと一致)。
- `previous_response_id`連鎖: 全Arm・全段で`chain_method`=`fresh`(stage0)/`previous_response_id`(stage1,2)、フォールバック未発生。
- usage/elapsed(`cost.json` per_call、詳細は同ファイル参照): 入力トークン合計15,161(cached込)、出力トークン合計9,491、elapsed_secondsは9.4〜17.3秒/call。
- cost(新規12 call): `total_usd_new_calls=0.0135`、`total_jpy_new_calls=2.15`円。Arm A再利用分(参考、新規課金なし): `arm_a_prior_cost_jpy_reference_only=0.46`円(前回Trialで既に計上済み)。
- `within_budget=true`(予算上限¥10に対し新規発生¥2.15、大幅に範囲内)。

## §6 比較表(日本語条件2 R2+5 arm R2)

全文は`er015_output/news_meta_english_prompt_variation_trial_01/comparison_all.md`(日本語Baseline+5 arm×Original/R1/R2全文)。ブラインド提示版は`blind_r2.md`(記号のみ、arm名なし)、対応表は`blind_key.json`(Fableはblind_r2.mdを先読みする想定)。

日本語Baseline(条件2 R2)タイトル: 「AIに電話を頼んだら、舞台裏から『人間』が登場した」(全文は`comparison_all.md`冒頭)。

## §7 Fable記入欄(参考評価・Status・UDR)

`[Fable記入]`

## §8 Production変更なし

- Production code(`er003_*`/`er005_*`/`er006_*`等の既存script)は無変更(import/参照のみ)。
- Production contract(Point One/Point Two/`###`/`## In one line`/280-420語target/B1構造/Verified Fact Ledger/Ledger Deviation Gate/Parser/Structure Validator/Key Phrase/Audio/Scaffold/TTS/Assembly)は一切未使用。
- SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)は無変更。
- 本Trialは`er015_output/news_meta_english_prompt_variation_trial_01/`配下にのみ影響し、Production側の量産経路には一切配線されていない。
