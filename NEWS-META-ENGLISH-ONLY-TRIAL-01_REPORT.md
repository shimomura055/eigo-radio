# NEWS-META-ENGLISH-ONLY-TRIAL-01 REPORT

管理ID: `NEWS-META-ENGLISH-ONLY-TRIAL-01`(初回委任)。Production実装ではない。
目的: Meta Muse/AI電話記事のEntertainment性低下の主因が「英語化」なのか
「Production構造contract」なのかを切り分けるため、「英語化だけ」を単離した
Trial。到達Status: `TRIAL`実行完了、機械的検証は`VALIDATED`相当だが、
品質の最終判断はユーザーが行う(本ReportではFableの参考評価・原因仮説・
Trial分類・USER_DECISION_REQUIREDは`[Fable記入]`として空欄のまま提出)。

出力ディレクトリ: `er015_output/news_meta_english_only_trial_01/`
Script: `er015_news_meta_english_only_trial_01.py`(既存script無変更、import再利用のみ)

---

## §1 条件2素材(逐語使用)

出典: `er015_output/news_meta_source_volume_format_trial_01/inputs/cond2.md`
sha256: `4a2d9f899cc6083eb46cd006d8df1fdb02db10c23bdce020b7d6ee58bf903ecb`
(期待値・実測値ともに一致。`er015_output/news_meta_english_only_trial_01/input_cond2_sha256.json`に記録)

```
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
```

2文・209字。追加Source・追加Fact・Ledgerは一切使用していない(Web Search未使用、
全3 callで`web_search_call_count=0`を確認、`api_meta_stage{0,1,2}.json`参照)。

---

## §2 日本語Prompt(P7逐語、正本: `docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md`)

developer message:
```
あなたは日本語のニュースを分かりやすく面白く伝える書き手です。
```

Original Prompt本体(`[ニュース]`欄以外は既存Trialと完全同一):
```
以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：MetaのAI電話代行が、通話の一部を裏で人間スタッフに担当させる実験を行っている

長さ：800～1000字

出力はタイトルと本文のみ。

[ニュース]
(条件2素材、§1と同一)
```

R1指示(逐語): この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。
R2指示(逐語): この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。
model=`gpt-5.6-luna` / effort=`high` / previous_response_id連鎖 / schema=None / web_search=なし / R3なし。

---

## §3 英語Prompt全文

developer message(英語):
```
You are a writer who explains the news clearly and makes it enjoyable to read.
```

user message(Stage0、全文。`prompt_user_stage0.txt`と同一):
```
Turn the news below into a piece you might share with a friend, the way you'd say "Hey, isn't this kind of interesting?"

From the news, pick not the most surprising fact but the single most interesting way of looking at it, and build the piece around that. Use mainly the facts needed for that viewpoint; do not try to cover the whole story.

Keep the tone natural and light. Do not write like a newspaper, a government document, or a school textbook. Rephrase difficult content in short, simple English. Aim for a level that a learner of English can understand by listening to it once.

If the news might look like something specific to a distant place only, show its connection to the reader's own life or to a larger social change, just once. But you don't need to force the story to feel bigger than it is.

Stick strictly to the facts. Do not add fictional events or quotes.

Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line.

Length: about 350–450 words.

Output only the title and the body. Write in English.

[News]
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
```

注: `[News]`欄は日本語のまま逐語(翻訳しない、素材を変えない、委任文の明示指示)。
Production構造contract(Point One/Point Two/`### `/`## In one line`/280〜420語
target)は一切含まない。追加Editorial ruleも追加していない。

R1指示(英語、API送信文): `Revise this article to make it more entertaining, without changing the facts.`
R2指示(英語、API送信文): `Revise this article to make it even more entertaining, without changing the facts.`
(日本語参考文を`prompt_r1.txt`/`prompt_r2.txt`に併記。実際のAPI送信はR1/R2とも英語文のみ)

---

## §4 Prompt対照表(P7各文↔英訳、差異行の明示)

絶対パス: `er015_output/news_meta_english_only_trial_01/prompt_alignment.md`

| P7(日本語) | 英訳(本Trial) | 差異 |
|---|---|---|
| 以下のニュースを、友人に「これ、ちょっと面白くない？」と… | Turn the news below into a piece you might share with a friend… | 差異なし |
| ニュースの中から、最も意外な事実ではなく… | From the news, pick not the most surprising fact… | 差異なし |
| 語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。 | Keep the tone natural and light. Do not write like a newspaper… | 差異なし |
| 難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が… | Rephrase difficult content in short, simple English. Aim for a level that a learner of English can understand by listening to it once. | 対象言語を「日本語」→「English」に対応させた(情報量・目安は同一) |
| 遠い地域だけの特殊な話に見える場合は… | If the news might look like something specific to a distant place only… | 差異なし |
| 事実関係は厳守し、架空の出来事や発言は加えません。 | Stick strictly to the facts. Do not add fictional events or quotes. | 差異なし |
| テーマ：MetaのAI電話代行が… | Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line. | PRODUCTION-LINE-TRIAL-01のTheme英訳から括弧内補足(固有名詞・日付)を除去、前回日本語テーマ文と同一情報量にした |
| 長さ：800～1000字 | Length: about 350–450 words. | **[差異]** 文字数→語数換算(Fable判断、Production 280〜420語targetとは無関係) |
| 出力はタイトルと本文のみ。 | Output only the title and the body. Write in English. | **[差異]** 出力言語明示(Write in English)を追加、Production構造contract追加ではない |

---

## §5 English Original全文(Stage 0)

Title: **The AI Calling for You May Have Been a Human After All**

(全文は`er015_output/news_meta_english_only_trial_01/en_original.md`。383語・2184字。
RESULT_PACKETに全文転記済み)

---

## §6 English R1全文(Stage 1)

Title: **Plot Twist: The AI Calling the Store May Have Been a Person**

(全文は`er015_output/news_meta_english_only_trial_01/en_revision1.md`。396語・2226字。
RESULT_PACKETに全文転記済み)

---

## §7 English R2全文(Stage 2)

Title: **Your AI Assistant Has Put You on Hold—But a Human Is Listening**

(全文は`er015_output/news_meta_english_only_trial_01/en_revision2.md`。422語・2441字。
RESULT_PACKETに全文転記済み)

---

## §8 Title変化

```json
{
  "original": "The AI Calling for You May Have Been a Human After All",
  "r1": "Plot Twist: The AI Calling the Store May Have Been a Person",
  "r2": "Your AI Assistant Has Put You on Hold—But a Human Is Listening"
}
```
(`titles.json`より。R1で「Plot Twist」という強調語を追加、R2で読者向けの直接的な
呼びかけ「Your AI Assistant Has Put You on Hold」に変化。強弱の判断はユーザー。)

---

## §9 日本語条件2 R2との並置

日本語Baseline(`er015_output/news_meta_source_volume_format_trial_01/cond2_revision2.md`、
タイトル: 「AIに電話を頼んだら、舞台裏から「人間」が登場した」)を、本Trial
English Original/R1/R2とともに`comparison.md`へ並置済み。

---

## §10 (参考)PRODUCTION-LINE英語R2との並置

`er017_output/news_entertainment_production_line_trial_01/stage2_r2.md`
(Production構造contractあり、Point One/Point Two/`### `/`## In one line`/
280〜420語target付き)を`comparison.md`末尾に参考として並置。生成前には
参照させていない(生成完了後にのみ`--assemble-only`で読み込み)。

---

## §11 Fact観測・prompt echo観測・語数(機械観測、判定はFable)

絶対パス: `fact_diff_machine.json` / `prompt_echo.json` / `metrics.json`

語数(word_count、英語):
| stage | char_count | word_count | paragraph_count |
|---|---|---|---|
| original | 2184 | 383 | 11 |
| r1 | 2226 | 396 | 14 |
| r2 | 2441 | 422 | 15 |

数字(numbers): 全Stageで**0件**(元情報2文に数字がないことと整合)。

固有名詞(capitalized words)で事前承認済み対訳語(Meta/Muse/Reuters/Human/
Concierge/Contract/Staff/Privacy/Rolled/Back/New/York/September)**以外**に
検出された語: 全て文頭の一般語(A/AI/But/If/In/It/So/That/The/They/You等)
であり、固有名詞の新規追加は機械観測上ゼロ。詳細は`fact_diff_machine.json`。

引用符内テキスト(quoted_spans、curly quote含む再検出後):
- original: `"Call the store and ask if they have this jacket in my size."`(仮定の
  具体例、"For example:"文脈の直後に置かれた例示)/ `"AI"` / `"human concierge."`
  (原文「人間コンシェルジュ」の英訳語) / `"Was this AI really AI?"`(修辞疑問文)
- r1: `"Hi, do you have these shoes in size nine? And what time do you close?"`
  (仮定の具体例、"Imagine asking..."文脈の直後) / `"human concierge"` / `"really"`
- r2: `"AI"` / `"human concierge"` / `"real"`

いずれも実在の発言として提示された引用ではなく、(a)用語としての引用符、
(b)「Imagine...」等で明示された仮定・例示、(c)修辞疑問。実在人物・組織の
発言として断定的に提示された新規Factは機械観測上検出されなかった(最終判定は
Fable)。

Prompt echo観測: `original`で`kind of interesting`が1件ヒット(developer
指示中のTheme文脈をそのまま冒頭の呼びかけ"Hey, isn't this kind of
interesting?"として使ったため。日本語Baselineの一部条件でも同様のパターンが
過去観測されている)。R1/R2では0件。`Isn't this`/`Here's something
interesting`/日本語echo文言はいずれのStageでも0件。

---

## §12 model・cost・latency

| stage | response.model | response_id | previous_response_id | input_tokens | cached_input_tokens | output_tokens | elapsed_seconds |
|---|---|---|---|---|---|---|---|
| original | gpt-5.6-luna | resp_02afd6bc145fa44e006ab4c384ee0087d0a249eac7a16a5952 | null | 399 | 0 | 735 | 15.667 |
| r1 | gpt-5.6-luna | resp_02afd6bc145fa44e006ab4c393a25487d0879d2a6b7cf0c5e6 | resp_02afd6bc145fa44e006ab4c384ee0087d0a249eac7a16a5952 | 1155 | 0 | 650 | 13.451 |
| r2 | gpt-5.6-luna | resp_02afd6bc145fa44e006ab4c3a113bc87d0bf18351d262cfa1b | resp_02afd6bc145fa44e006ab4c393a25487d0879d2a6b7cf0c5e6 | 1827 | 1152 | 645 | 11.816 |

連鎖確認: r1.previous_response_id = original.response_id、r2.previous_response_id
= r1.response_id(いずれも一致、previous_response_id方式で成功、フォールバック
未発生)。`response.model`実値は3 callとも`gpt-5.6-luna`(要求モデルと一致)。

cost.json: total_usd=0.0029、**total_jpy=0.46**(予算¥10以内)。web_search
費用は発生していない(`web_search_call_count=0`)。

---

## §13 Fable参考評価
`[Fable記入]`

## §14 原因仮説
`[Fable記入]`

## §15 Trial分類
`[Fable分類待ち]`

## §16 USER_DECISION_REQUIRED
`[Fable記入]`

## §17 Production変更なし

- Production wiring/Production Prompt変更/Point One・Point Two・`### `・
  `## In one line`・280〜420語target・B1構造/Production Writer instruction/
  Verified Fact Ledger/Ledger Deviation Gate/Parser/Structure Validator/
  Key Phrase/Audio/Scaffold/TTS/Assembly/Web Search/Search改善/Hook改善/
  retry・fallback変更/英語Prompt追加改善Trialのいずれも実施していない。
- 既存script(`er015_news_meta_source_volume_format_trial_01.py`、
  `er015_news_iterative_entertainment_trial_02.py`、
  `er015_news_original_baseline_repro_01.py`、
  `er015_news_core_idea_editorial_trial_01.py`)は無変更、import再利用のみ。
  新規追加は`er015_news_meta_english_only_trial_01.py`のみ。
- SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)への追記なし。
