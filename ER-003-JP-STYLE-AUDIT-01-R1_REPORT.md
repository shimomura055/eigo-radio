# ER-003-JP-STYLE-AUDIT-01-R1 実行報告(実プロンプト原文・阪神master投入方法の確定)

**管理ID: ER-003-JP-STYLE-AUDIT-01-R1**
**実施日: 2026-08-12**
**ステータス: `AUDIT COMPLETE`(read-only確認のみ。コード・prompt・文書・音声はいずれも変更していない)**

## 1. 結論(YES/NO)

| 質問 | 回答 |
|---|---|
| 新規記事は英語直接生成だったか | **NO** |
| 阪神master全文(または実体)を毎回モデルへ渡していたか | **YES** |
| 日本語記事は必須中間工程だったか | **YES** |

補足: 全バージョン(J1〜R4)とも、writerモデルが生成していたのは**常に日本語記事**
であり、英語化は一切行っていない。英語化(Natural English Source)は、
これとは別の**後発の独立した工程**(ER-003-P1B、2026-07-20、[前回報告](ER-003-JP-STYLE-AUDIT-01_REPORT.md)
5節)が担っている。7節で詳述する。

## 2. 実プロンプト原文

### 2-1. 初期版(J1、2026-07-15頃、7記事初回一括生成)

**実装**: `er002_ja_master_imitation.py`
**API**: OpenAI **Chat Completions** API(`client.chat.completions.create`)、
`response_format={"type": "json_schema", ...}` によるStructured Output
**モデル**: `gpt-5.6-terra`(`er002_script_adapter.MODEL_WRITE`。R1以降の
`gpt-5.6-sol`とは**異なるモデル**。証拠: `er002_output/v1_2m_j1/A01/input_manifest.json`
の`model_value`)
**Web検索ツール**: **使用なし**(tools引数自体が存在しない)

developer/system相当の指示は存在せず、user roleの単一メッセージのみ
(129-144行、`{}`は実際の埋め込み変数):

```
以下は、承認済みの記事(マスター)です。この記事の文体・語り口・構成の作り方を
参考にして、新しい記事を1本書いてください。マスターの題材(阪神・野球)や
マスター内の具体的な比喩・表現をそのまま使い回さないでください(今回は別の
トピックです)。

【マスター記事】
{master_full_text}

【マスターが評価された理由】
{evaluation_reasons_block}

【今回の対象記事の確認済み事実】
{facts_block}

【今回のトピック】
{target_topic}

【指示】
阪神固有の表現や野球の比喩をコピーするのではなく、記事全体の編集センスを
今回の題材へ応用してください。全体の概要を面白く展開し、二つのポイントでは
本文とは別の切り口を加え、一言で印象的にまとめてください。確認済み事実に
ない具体的内容を推測で加えないでください。
```

`{evaluation_reasons_block}`は固定4項目(コード内定数、依頼文からの
引き写し):「全体の概要を面白く展開」「今日の虎ポイントで、別切口でも解説」
「一言で表すなら、でサマリー」「聞き手があきない設計」。

**変数を埋めた実例(A01、`er002_output/v1_2m_j1/A01/input_manifest.json`より)**:
`{facts_block}`は以下の5件("F01"〜"F05"のfact ID形式)。

```
F01: Argentina defeated England 2-1 in the World Cup semifinal on July 15, 2026.
F02: Anthony Gordon scored England's opening goal.
F03: Enzo Fernandez equalized for Argentina, and Lautaro Martinez scored the
     winning goal in the 92nd minute.
F04: Argentina advanced to the World Cup final against Spain.
F05: Lionel Messi provided the assist for the equalizer and the cross leading
     to the winning goal, according to Reuters.
```

`{target_topic}`はA01の場合`"World Cup semifinal"`相当(`topic_label_en`)。

出力形式はJSON(`title`/`body`/`point_one`/`point_two`/`one_line_summary`の
5フィールド、strictスキーマ)。

### 2-2. 6トピック比較の初動修正版(R1、`writer_prompt_template.txt`)

J1がユーザー品質評価で不合格となったため(`er002_ja_free_markdown_restore.py`
冒頭コメント「ER-002-v1.2M-J1(Structured Output・完全fact registryをwriterへ
投入)がユーザー品質評価で不合格となったため」)、以下3点を変更:
①完全fact registryをやめ短い"concise brief"のみに②Structured Outputをやめ
自由Markdownに③モデルを`gpt-5.6-sol`へ変更。

**API**: OpenAI **Responses** API(`client.responses.create`)、
developer roleに固定文言、response_format等は一切指定しない(自由Markdown)
**モデル**: `gpt-5.6-sol`、reasoning effort `high`
**developer message(system相当、以降R4まで不変)**: `"日本語の記事を作成してください。"`
**Web検索ツール**: **使用なし**

```
以下は、私が良いと評価している日本語記事です。

【マスター記事】

{master_full_text}

【今回のニュース】

{concise_news_brief}

この阪神記事が良いのは、全体の概要を面白く展開し、ポイントでは本文とは
別の切り口から解説し、最後に一言でまとめることで、聞き手が飽きない設計に
なっている点です。

このセンスで、今回のニュースの記事を書いてください。

阪神や野球固有の表現をコピーするのではなく、今回の題材に合う表現を使って
ください。
```

`{concise_news_brief}`の実例(A01、`er002_v1_2m_restore_briefs/A01_concise_brief.txt`):
`「2026年7月15日のワールドカップ準決勝で、イングランドはアルゼンチンに1対2で
敗れた。イングランドが先制したが、アルゼンチンが追いつき、92分の決勝点で
逆転した。アルゼンチンはスペインとの決勝へ進んだ。」`(J1のF01〜F05相当を、
1段落・3文へ圧縮した短い要約)。

### 2-3. R2(構造制約追加)

R1と全く同じプロンプトの末尾へ1文だけ追加(`writer_prompt_template_r2.txt`):

```
ポイント部分には、Markdownの「###」見出しをちょうど2つ置いてください。
```

API・モデル・developer message・Web検索なしはR1から不変。

### 2-4. R3(6トピックから3トピックへ絞り込み後、Web検索を導入)

R1/R2の"concise brief"方式を完全に廃止し、**writerモデル自身に同一呼び出し
内でWeb検索させる**方式へ転換(`writer_prompt_template_r3.txt`)。

**API**: Responses API、`tools=[{"type": "web_search"}]`を追加
**developer message**: 不変(`"日本語の記事を作成してください。"`)

```
以下は、私が良いと評価している日本語記事です。

【マスター記事】

{hanshin_master_full_text}

【今回のテーマ】

{topic}

この阪神記事が良いのは、全体の概要を面白く展開し、ポイントでは本文とは
別の切り口から解説し、最後に一言でまとめることで、聞き手が飽きない設計に
なっている点です。

今回のテーマについて必要な情報をWebで調べてください。検索内容や検索回数、
何を記事の中心にするか、どの事実を本文と二つのポイントに使うかは、あなた
自身で判断してください。

調査から記事作成までを一つの作業として行い、このセンスで今回のテーマの
記事全文をMarkdownで書いてください。

阪神や野球固有の表現をコピーするのではなく、今回の題材に合う表現を使って
ください。

ポイント部分には、Markdownの「###」見出しをちょうど2つ置いてください。
```

`{topic}`はテーマ名の短い文字列のみ(concise briefのような事実要約は渡さない)。
生成後、writerとは別の独立したAPI呼び出しでWeb検索付きfact checkerが検証する
(6節)。

### 2-5. 最終採用版(R4「条件L」、`ER-002-v1.2M-R4-FINALIZE`で正式採用)

R3の本体プロンプトは**一切変更せず**、末尾へ長さ指示3文のみを追加
(`er002_ja_article_generation.py` `build_writer_user_message()`)。

```
記事本文は、引用表記を除き、阪神マスターの読み上げ対象本文と同程度の
分量にしてください。
目安は{master_count}字、許容範囲は{lower_bound}字から{upper_bound}字です。
調べた情報をすべて盛り込まず、記事の面白さに必要な情報だけを選んでください。
```

**変数を埋めた実際の呼び出し条件(A01、`er002_output/v1_2m_r4/condition_l/A01/writer_request_metadata.json`より、実測値)**:

```json
{
  "model": "gpt-5.6-sol",
  "reasoning_effort": "high",
  "developer_message": "日本語の記事を作成してください。",
  "api_endpoint": "responses.create",
  "response_format_used": false,
  "concise_brief_passed_to_writer": false,
  "full_fact_registry_passed_to_writer": false,
  "master_count": 697,
  "lower_bound": 592,
  "upper_bound": 802
}
```

`concise_brief_passed_to_writer: false`・`full_fact_registry_passed_to_writer: false`
は、この最終採用版ではJ1/R1/R2のような**事前収集済みFactsを一切渡していない**
ことの直接的な実測証拠である。

**なお条件LB(3記事同時生成、不採用)** は本体プロンプトが異なる
(`writer_prompt_template_r4_lb.txt`、3テーマを1回のwriter呼び出しへ
同時投入)。不採用理由は独立fact checkerがA01で事実矛盾を検出したため
(前回報告参照)。

## 3. 阪神masterの実体

- **ファイル名**: `hanshin_ja_master.txt`
- **path**: `er002_v1_2m_masters/hanshin_ja_master.txt`
- **sha256**: `5f4fe54f8a6b64fc80af5ed80e76fe0a9ccbbb1c082ef71f310b5303433abcb1`
  (`er002_v1_2m_masters/masters_sha256.json`で凍結・全実装が読み込み時に
  この値と照合するfail-closed設計。値が一致しなければAPIを呼ばずに停止する)
- **commit/history**: `masters_sha256.json`の`frozen_at_commit`フィールドが
  `71a20742203baf57a0bfc1826e194de7522ca4b5`を記録(このcommit時点で凍結)
- **masterとして使われていた根拠**: `original_request.txt`本文、および
  全5バージョン(J1〜R4)のプロンプトコード内で`master_full_text`/
  `hanshin_master_full_text`として直接埋め込まれる変数名そのもの

## 4. master投入方式

**A. 入力形式**: **阪神記事全文をuser prompt内へ直接埋め込み**(別ファイルは
読み込むが、それをそのままprompt文字列へテキスト展開する方式。厳密な
few-shot example形式(role分離)ではなく、1つのuser messageの中に
`【マスター記事】`という見出し付きで埋め込む)。system prompt自体は
存在しない(developer messageのみ、内容は本文と無関係な中立文言)。

**B. 入力範囲**: **阪神記事の全文**(見出し・本文・「今日の虎ポイント」2件・
「一言で表すなら」の結び、全構成を含む完全なテキスト)。要約や特徴抽出では
ない(3節参照)。抜粋も行っていない。

**C. 毎回渡していたか**: **毎回、新しいトピックの生成のたびに全文を渡していた**。
J1〜R4のいずれの実装も、`load_and_verify_masters()`/`load_text_file()`等で
都度ファイルを読み込み、プロンプト文字列へ都度embedする設計であり、
「途中でstyle ruleへ変換してmaster自体を渡さなくなった」時期は確認できな
かった。session/contextへの依存もない(1テーマ=1回の独立したAPI呼び出し
であり、会話履歴の継続利用は設計上ない)。

**D. 参照**: 3節のとおり。

## 5. 当時の実フロー(最終採用版=条件L、A01/A02/ADD03で実際に使われた経路)

```
[トピック名(人間が短い文字列で指定)]
        ↓
[writerモデル 1回のResponses API呼び出し]
   developer: "日本語の記事を作成してください。"
   user: 阪神master全文 + トピック名 + 短いinstruction + 長さ指示
   tools: web_search (writerモデル自身が検索クエリ・検索回数を判断)
   → 検索と執筆を同一呼び出し内で実施(中間のFacts確定ファイルは生成しない)
        ↓
[日本語記事(Markdown、raw_article.md)]
        ↓
[構造チェック(###見出しちょうど2つか、コードのみで判定)]
        ↓
[独立fact checker: 別の新規Responses API呼び出し(web_search + 構造化出力)]
   PASS / REVIEW_REQUIRED / FAIL を判定(writer本文は書き換えない)
        ↓
[reading_copy.md 確定](日本語のまま。英語化はまだ行われていない)
```

**注記**: J1/R1/R2は、上記の「writerモデル自身がWeb検索」の部分が
「事前に用意されたFacts(J1: fact ID付き検証済み事実5件/R1・R2: 短い
concise brief1段落)をuser promptへ埋め込む」に置き換わる。これらの
Factsが具体的にどの工程で収集されたか(人間の手作業か、別セッションでの
Claudeによる調査か)を示すコード・ログは見つからなかった(8節)。

## 6. Facts収集

| 項目 | J1 | R1・R2 | R3・R4(最終採用) |
|---|---|---|---|
| Factsの出所 | 事前収集済み(fact ID付きリスト、5件) | 事前収集済み(concise brief、1段落) | writerモデル自身のライブWeb検索 |
| writerモデル自身がWeb検索したか | **していない**(tools引数なし) | **していない**(tools引数なし) | **している**(`tools=[{"type":"web_search"}]`) |
| 検索結果を一度structured factsへ整理したか | している(fact_id_map、F01形式) | していない(自由文の短い要約のみ) | **していない**(検索から執筆までが不可分の1回の呼び出し) |
| Facts用の中間ファイルがあったか | あり(`input_manifest.json`の`fact_id_map_used`) | あり(`*_concise_brief.txt`) | **なし** |
| 中間ファイルを記事生成モデルへ渡していたか | 渡していた(prompt内へfacts_blockとして埋め込み) | 渡していた(prompt内へconcise_news_briefとして埋め込み) | 該当なし(中間ファイル自体が存在しない) |
| source URL/citationを保持していたか | 記録なし(fact_id_mapは文単位の事実のみ、URL無し) | 記録なし | **保持している**(`writer_sources.json`にtitle/urlのペアを記録。fact checkerも別途`sources`フィールドを持つ) |

**「検索しながらそのまま書いた」か「Factsを一旦確定してから書いた」か**:
**バージョンによって異なる。** J1・R1・R2は明確に**「Factsを一旦確定してから
書いた」**方式(ただし確定作業自体がどこで行われたかは不明、8節)。R3・R4
(最終採用・現行A01/A02/ADD03の実際の生成経路)は**「検索しながらそのまま
書いた」**方式であり、Factsを独立した中間成果物として確定する工程は
存在しない。

## 7. 現在ER-003との違い

前回報告(5節)で述べたとおり、条件Lの出力(`reading_copy.md`、日本語)は、
これとは**別の後発の独立した工程**(ER-003-P1B、2026-07-20、commit
`45c48ee`)によって英語化され、「Natural English Source」として確定する。

- **`reading_copy.md`は当時の阪神master方式(条件L)の出力そのもの**であり、
  阪神master方式の一部として作られたファイルである
- **「`reading_copy.md → Natural English Source`」という変換工程自体は、
  阪神master方式には含まれていない別系統**(ER-003-P1B)である。
  阪神master方式のどのプロンプト(J1〜R4のいずれも)にも、英訳指示・
  英語出力の指定は一切存在しない
- 実行日で見ても、条件L確定(2026-07-19)→P1B確定(2026-07-20)と、
  1日を空けて別の作業として追加されている

ユーザーが提示した候補A・候補Bのいずれとも一致しない(6節・5節参照)。
実際のフローを一言でまとめると:

```
Topic名(人間指定)
  → writerモデルが同一呼び出し内でWeb検索+執筆(日本語、Facts確定の
    中間工程なし)
  → 独立fact checkerが検証(日本語のまま)
  → reading_copy.md確定(★ここまでが阪神master方式)
  → (別の後発工程・翌日) ER-003-P1Bが英訳
  → Natural English Source確定
```

英語生成を伴わない点、Facts確定の中間工程がない点(R3/R4)の2点が、
候補A・候補Bのいずれとも異なる。

## 8. 不明点

- J1(初期版)で使われたFacts(fact_id_map、A01の5件等)が、具体的に
  どの工程・誰によって収集・確定されたかを示すコード・実行ログは
  見つからなかった。`gather_topic.py`のTOPIC_PACKAGE形式とは構造が
  異なり(fact_id_map: `{"F01": "文"}`形式、TOPIC_PACKAGE:
  `{'topic':..., 'facts':...}`形式)、直接の変換コードも存在しないため、
  **前回報告と同様、gather_topic.py由来である証拠はない**(推定するなら
  人間またはClaude Codeとの対話セッションでの手動調査だが、これも証拠
  不十分のため断定しない)
- R1・R2の`*_concise_brief.txt`(短い1段落要約)についても、同様に
  生成元のコード・ログは見つからなかった
- J1の実行日時("2026-07-15頃"としたのは`original_request.txt`の依頼文
  内容および周辺commitの日付からの**推定**であり、J1自体の実行ログに
  厳密なタイムスタンプは確認できなかった)

## 受入条件13項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | 実プロンプト原文を可能な限りそのまま提示している | PASS(2節、5バージョン全て原文) |
| 2 | 実プロンプトと推定を明確に区別している | PASS(8節に不明点を分離) |
| 3 | promptが複数世代ある場合は時系列整理している | PASS(2-1〜2-5、J1→R1→R2→R3→R4) |
| 4 | 阪神masterの正確なファイルを特定している | PASS(3節) |
| 5 | masterをモデルへ渡した方式を特定している | PASS(4節A) |
| 6 | masterのどの範囲を渡したか特定している | PASS(4節B、全文) |
| 7 | masterを毎回渡していたか確認している | PASS(4節C、毎回全文) |
| 8 | Topic→Facts→記事生成の実フローを提示している | PASS(5節・6節) |
| 9 | Facts収集と記事生成が分離されていたか確認している | PASS(6節表、バージョンで異なる) |
| 10 | 新規記事が英語直接生成だったかYES/NOで回答している | PASS(1節、NO) |
| 11 | 日本語記事が必須中間工程だったかYES/NOで回答している | PASS(1節、YES) |
| 12 | 現在のreading_copy.md → Natural English Sourceとの関係を説明している | PASS(7節) |
| 13 | コード・文書・音声を一切変更していない | PASS(本監査中、Write/Editしたのは本報告書のみ) |

## 今回行っていないこと

コード変更、prompt修正、新規記事生成、Web検索実行、E2E実行、B1/A2生成、
音声生成、Source of Truth更新、OPEN項目変更。
