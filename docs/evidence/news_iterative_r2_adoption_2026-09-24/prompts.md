# 使用Prompt逐語(NEWS-ITERATIVE-ENTERTAINMENT-TRIAL-01/02、Sonnet逐語転記・要約なし)

出典: `er015_news_original_baseline_repro_01.py`(Original Prompt本体・
developer message・model/effort定数の定義元、Production非該当のTrial
script)、`er015_news_iterative_entertainment_trial_01.py`(下水道テーマ・
Revision指示定数)、`er015_news_iterative_entertainment_trial_02.py`
(AI電話代行/旅行荷物テーマ・素材挿入方式)。いずれも本タスクで変更して
いない(読み取りのみ)。

## 1. Developer message(3テーマ共通、逐語)

```
あなたは日本語のニュースを分かりやすく面白く伝える書き手です。
```

## 2. Original Prompt(P7、3テーマ共通の本体部分。テーマ欄・[ニュース]欄のみ差し替え)

### 2-A. 下水道テーマ(`er015_news_iterative_entertainment_trial_01`、素材なし)

```
以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討

長さ：800～1000字

出力はタイトルと本文のみ。
```

(この版は[ニュース]欄なし。引き継ぎ資料§7逐語コピーであり、素材本文が
記録されていなかったため素材なしで生成した。)

### 2-B. Article A: Meta Muse AI電話代行「人間コンシェルジュ」実験(`er015_news_iterative_entertainment_trial_02`、素材あり)

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
Reuters(2026年9月22日、NEW YORK発)によると、Metaは個人向けAIエージェント「Muse」の電話代行機能について、一部の通話を人間の契約スタッフが裏で担当する「人間コンシェルジュ」の試験を社内で行っていたことが、Reutersが確認した社内投稿で判明した。従業員から通話内容の外部流出などプライバシー面の懸念が示され、Meta幹部はこの機能を一旦取りやめた(rolled back)と説明した。
```

### 2-C. Article B: 旅行用圧縮ポーチ(トラベルポーチ)人気ランキング(`er015_news_iterative_entertainment_trial_02`、素材あり)

```
以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：旅行用の圧縮ポーチが人気、荷物はなぜ毎回バッグいっぱいになるのか

長さ：800～1000字

出力はタイトルと本文のみ。

[ニュース]
「賢者のモノサシ」の旅行用圧縮ポーチ特集(2026年9月23日更新)によると、圧縮トラベルポーチを使うと衣類の厚みが1〜2段階薄くなり、スーツケースの容量を10〜20%削減できるとされる。圧縮方式にはファスナー式と真空圧縮袋式の2種類があり、楽天ランキング上位の売れ筋4点セットは700円〜1,190円前後で販売されている。
```

## 3. Revision指示(逐語、3テーマ共通、`REVISION_INSTRUCTIONS`定数)

R1・R2は**Production標準に含まれる修正指示**、R3は**Trial実施の事実として
保存するがProduction標準には含まれない**。

### R1(Entertainment revision、1回目)

```
この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。
```

### R2(Further entertainment revision、2回目。Production final)

```
この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。
```

### R3(3回目、Trial実施のみ。Production標準に含まれない)

```
この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。
```

(R2とR3は文言が完全に同一。Fable設計により追加条件[Hook・比喩等]は
一切付与せず、単純な同一指示文を連鎖させることで自然な変化を観察する
Trial設計だった。)

## 4. Model / Reasoning設定

- `WRITER_MODEL = "gpt-5.6-luna"`(`er015_news_original_baseline_repro_01.WRITER_MODEL`
  = `er003_v1_en_direct_vfl_01_generate.MODEL`。Production側`er006_model_routing_contract_01.WRITER_MODEL`
  も同一値`"gpt-5.6-luna"`、`B1_WRITER`/`A2_WRITER`に使用)
- `WRITER_EFFORT = "high"`(`er015_news_original_baseline_repro_01.WRITER_EFFORT`
  = `er003_v1_en_direct_vfl_01_generate.REASONING_EFFORT`)
- API: OpenAI Responses API(`client.responses.create`)、`reasoning={"effort": effort}`。
- schema/web_search: 未使用(schema=None、tools引数なし)。

## 5. 連鎖方式(previous_response_id、Trial-02 api_metaから実際のresponse_id連鎖を転記)

各段階は、直前応答の`response_id`を`previous_response_id`として渡し、
userメッセージとして修正指示文のみを送る(developerメッセージは会話文脈に
既に含まれるため再送しない)。`previous_response_id`が使えない場合のみ、
直前記事全文を「以下の記事」として同じ修正指示文の前に貼るフォールバック
方式に切り替え、`chain.json`へどちらを使ったか記録する仕様(3テーマとも
実際にはフォールバックは発生せず、全12段階が`previous_response_id`方式で
成功した)。

### 下水道テーマ(`chain.json`)

| stage | response_id | model | chain_method |
|---|---|---|---|
| original | resp_0ed6cb50bbb027a6006ab46b909ca487d0a55c2e43b5154b02 | gpt-5.6-luna | (新規) |
| r1 | resp_0ed6cb50bbb027a6006ab46ba2974487d08d9d5187d04f562f | gpt-5.6-luna | previous_response_id |
| r2 | resp_0ed6cb50bbb027a6006ab46bae8b5c87d0b6ddcd587ca900ae | gpt-5.6-luna | previous_response_id |
| r3 | resp_0ed6cb50bbb027a6006ab46bc29e3487d08effe7709932180f | gpt-5.6-luna | previous_response_id |

### Article A(AI電話代行、`chain.json`)

| stage | response_id | model | chain_method |
|---|---|---|---|
| original | resp_04020df138cfa5d1006ab47ee74a4087d084bd71c730cfe519 | gpt-5.6-luna | (新規) |
| r1 | resp_04020df138cfa5d1006ab47efb01e487d0970d151832e733bd | gpt-5.6-luna | previous_response_id |
| r2 | resp_04020df138cfa5d1006ab47f080abc87d0b978604a1444e679 | gpt-5.6-luna | previous_response_id |
| r3 | resp_04020df138cfa5d1006ab47f14817487d097bb6c1f31dcd299 | gpt-5.6-luna | previous_response_id |

### Article B(旅行荷物、`chain.json`)

| stage | response_id | model | chain_method |
|---|---|---|---|
| original | resp_079ebe74df78bedd006ab47f2997c087d09b788ba596c74d6c | gpt-5.6-luna | (新規) |
| r1 | resp_079ebe74df78bedd006ab47f35acb487d0a54944931a596823 | gpt-5.6-luna | previous_response_id |
| r2 | resp_079ebe74df78bedd006ab47f3f91c887d0a69e0f41ab0b2dbb | gpt-5.6-luna | previous_response_id |
| r3 | resp_079ebe74df78bedd006ab47f49bb2487d0a3d0c293ebcf1dcd | gpt-5.6-luna | previous_response_id |

## 6. Fallback有無

Trial中(12段階全て)、`previous_response_id`方式は一度も失敗せず、
フォールバック(直前記事全文貼り付け方式)は**未使用**。フォールバック
発生時の記録先(`chain.json`)は実装済みだが、実際に使われたケースは
Trial-01/02のいずれにも存在しない。
