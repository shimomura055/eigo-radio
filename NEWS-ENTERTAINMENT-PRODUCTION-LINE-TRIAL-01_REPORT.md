# NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 REPORT

Status: **Phase B VALIDATED(downstream一部到達、既存Audio Validation
Gateで安全側STOP)**。Phase Aは§A/§B参照(P1/P2不成立でPhase B着手を
一度STOPしたが、2026-09-24にユーザーがOption (a)[既存Production
Research/Verification正式利用]を承認しPhase Bへ進んだ)。Phase Bでは
Research→Verification→Ledger→Writer(Stage0/1/2)→既存Gate→downstream
(Scaffold/Key Phrase PASS、TTS実行、Assemblyは既存Audio Validation
Gateにより`full_story_part2`セグメントのASR検証3回不合格でBLOCKED)まで
到達した。Production code(er003_*/er006_*/er011_*/er012_*)は実行前後で
sha256完全一致(§9)。総費用¥42.50(上限¥250以内)。`PRODUCTION_WIRED`/
`APPROVED_FOR_PRODUCTION`にはしていない(委任文11節)。

## §A Phase A recon結果(P1〜P5)

### 前提: 通常NewsのProduction構造・入口(read-only確認)

- 正式Production入口: `er012_b_family_production_runner_01.py`
  (`main_b1_3v`/`main_b1_2v`/`main_a2`/`main_a2_2v`、L1119/1254/1626/1947)。
  同ファイルL50で`import er003_v1_n3_01_articles_generate as gen_articles`
  しており、News(B1/A2)の実Writer/Parser/Validator/Gate本体は
  `er003_v1_n3_01_articles_generate.py`側にある(CURRENT_SPEC.md L804-828
  「通常News(Major/Daily News)Reference仕様」節が同ファイルをHanshin
  referenceの実装として正式指定)。
- Structure Validator: `er002_ja_free_markdown_restore_r2.validate_point_structure()`
  (`er003_v1_n3_01_articles_generate.py` L692, L929でコメント参照)。
- 必須heading/構造(`er003_v1_n3_01_articles_generate.py` L157-166,
  L687-707): `# Title`+本文(Main Story)+Markdownの`###`見出しを
  ちょうど2つ(Point One相当/Point Two相当、見出し文字列に
  "Point One"/"Point 1"/「第一に」等の直書きは禁止、意味を表す独自見出しに
  すること)+`## In one line`(正確な文字列、小文字"one line"、L699の
  regex `^##\s+In one line`で検出)。
- Length Target(B1、`TOTAL_SOFT_LOWER`/`TOTAL_SOFT_UPPER` L62-63):
  総語数280〜420語(soft range、hard gateではなく記録のみ、
  `total_within_soft_range`フラグとしてmetricsに記録)。Point One/Two
  各30〜60語(許容25〜70語、hard capではない、L235)。
- Verified Fact Ledger入力形式: `verified_ledger_text`(プレーンテキスト、
  `Fact Ledger`形式。L264-269「以下のVerified Fact Ledgerだけを事実源
  として使用してください」)。
- 内蔵retry/Gate群(`er003_v1_n3_01_articles_generate.py`):
  - `vfl01.run_writer_with_technical_retry(max_attempts=2)`
    (`er003_v1_en_direct_vfl_01_generate.py` L378、技術的失敗のretry)。
  - `POINT_OVERLAP_ARTICLE_RETRY_MAX = 2`(L818、Point overlap NG時の
    記事全体retry)。
  - `run_point_overlap_qa_and_regenerate()`(L732、Full StoryとPoint
    One/Twoの語彙重複検査、**verified_ledger_text必須引数**)。
  - `local_rewrite.MAX_REWRITE_CYCLES`(L1115-1120、Ledger Deviation
    MAJOR項目に対するLocal Rewriteの上限サイクル、**verified_ledger_text
    必須**)。
  - `vfl01.run_deviation_check()`(`er003_v1_en_direct_vfl_01_generate.py`
    L603、Ledger Deviation Checker、**verified_ledger_text必須引数**)。
  - `canon_spelling.build_canonical_spelling_fact_check_block()`
    (`er011_open146_ledger_canonical_en_spelling_production_01.py`、
    Fact Check block、Ledgerに`canonical_en_spelling:`行がある場合のみ
    有効、**Ledger由来**)。

### P1: 既存Production Writer primitiveを、Editorial instructionだけ
差し替えてProduction codeを変更せず呼べるか

**不成立**。確認した2経路とも不可:
1. `er003_v1_n3_01_articles_generate.run_one_pattern()`
   (L866以降)は、Editorial instruction(`B1_B_DIRECT_INSTRUCTION`等)を
   `build_common_block()`(L520)が生成する`COMMON_BLOCK_TEMPLATE`
   (L120-491、Verified Fact Ledgerの使い方・Point Balance原則・
   数値精度原則等、Ledger運用と一体化したEditorial/技術指示が数百行)
   に埋め込んで送信する構造であり、「Editorial instructionだけ差し替え」
   が構造的に不可能(COMMON_BLOCK_TEMPLATE自体がLedger運用前提の
   Editorial内容を含むため、これをそのまま使うと「既存Editorial
   instructionを混ぜない」という委任条件に違反し、削ると
   Production codeの改変が必要になる)。
2. `er012_b_family_voices_writer_generic_01.run_writer_stage_generic()`
   (L2039、`instruction`引数を持つ唯一の既存汎用Writer関数)は、
   `theme_config["ledger_path"]`が存在しないと`SystemExit`する
   (L2054-2056)。さらにL2065-2073の分岐が示すとおり、この関数は
   B-Family Voices(2/3 Voice構成の会話体記事、Focus Module必須)専用
   であり、News(Title/Main Story/Point One/Point Two/In One Line)の
   単一Writer構造とは記事構造自体が異なる(会話体voice card構造)。
   `instruction`引数は既存Focus Module内の【難易度指示】節1箇所にのみ
   影響し、Editorial思想全体を置き換えるものではない(L2050-2053の
   docstringが明記)。

### P2: Verified Fact Ledgerを、TRIAL-02 Article Aの素材文だけから、
既存primitiveで新規Web検索なしに生成できるか

**不成立**。Ledger生成の既存primitive(`er003_v1_en_direct_vfl_01_generate.py`)
は2段階とも`tools=[{"type": "web_search"}]`を使用する設計:
- `run_researcher()`(L170-189、L175で`web_search`ツール指定、Responses
  API)。
- Verification stage(L248以降、`VERIFICATION_PROMPT_TEMPLATE`
  L224-245が「Ledger自身のsource_urlだけを鵜呑みにせず、独立してWeb
  検索により再照合してください」と明記、L258で`web_search`ツール指定)。

「与えられた素材テキストからだけ(新規Web検索なし)でLedgerを組む」
既存primitiveは調査範囲(`er0*.py`全130ファイルの`build_ledger`系
関数名グレップ)で発見できなかった。TRIAL-02自体(`er015_news_iterative_
entertainment_trial_02.py`)もVerified Fact Ledgerを使わない設計
(CURRENT_SPEC.md L828「Trial呼称...Ledgerなし・単純な修正指示連鎈」)
であり、素材文(`sources.md`Article A、Reuters記事1段落相当)を
Ledgerの粒度(fact_id/scope/numeric_value/causal_strength等の構造化
フィールド、L159-163)まで手作業で組み立てることは、委任文5節
「既存contractを推測で作らない」「手作りLedgerが必要な場合はP2不成立」
の条件に該当する。

### P3: Section構造・heading表記・Length Targetを一意に確定できるか

**成立**(§A冒頭の「前提」節に記載の内容で一意に確定できた。推測なし)。

### P4: Revision出力を同じparser/validatorで再検証できるか

**判定保留(P1/P2不成立により評価不能)**。技術的には`run_one_pattern()`
がverified_ledger_textを必須引数に取るため、P2が成立しない限りP4を
意味のある形で検証できない(Ledgerなしで同関数を呼べばLedger Deviation
Checker等が空/不正な入力で動作し、「既存Validatorを実際に使った」とは
言えない)。

### P5: 内蔵retryを変更せず使える、またはTrial側で「retryなし・1回生成」
にでき、retry/fallback仕様判断が発生しないか

**判定保留(P1/P2不成立により評価不能)**。`run_one_pattern()`内の
Point Overlap retry(最大2回)・Local Rewrite(`MAX_REWRITE_CYCLES`)は
いずれもLedger Deviation Check結果に条件分岐しており、Ledgerが存在
しない場合にこれらのretry/fallback分岐をどう扱うかは、それ自体が
「retry・fallback仕様判断」に該当し、委任文STOP条件
「retry・fallback仕様判断が必要」に直接抵触する。

### 判定まとめ

P1: 不成立 / P2: 不成立 / P3: 成立 / P4: 判定不能(P1/P2依存) /
P5: 判定不能(P1/P2依存)。**5項目中2項目が明確に不成立**のため、
委任文の規定どおりPhase Bを実行せずSTOPする。

## §B 必要となる仕様変更候補(提案ではなく事実列挙)

- 既存Newsの単一Writer呼び出し(`run_one_pattern`系)は、Editorial
  instructionとLedger運用手順(COMMON_BLOCK_TEMPLATE)が分離されて
  おらず、「Editorial思想だけ差し替え可能な汎用Writer入口」は現状
  存在しない。分離可能な形にするには`er003_v1_n3_01_articles_generate.py`
  側のprompt組み立て構造(Production code)への変更が要る。
- Verified Fact Ledgerを「与えられた素材文だけから新規Web検索なしに」
  生成する既存primitiveは存在しない。既存Researcher/Verification
  primitiveはいずれもWeb検索必須の設計。
- 上記2点は、2026-09-24付の別管理ID`NEWS-ITERATIVE-R2-PRODUCTION-
  WIRING-01`のPhase 0 reconでも同旨の指摘が既にCURRENT_SPEC.md L828
  へ記録されている(「配線先Production経路: 未確定」「新規Production
  module設計要否はFable/ユーザー判断待ち」)。本Trialのrecon結果は
  その既存指摘と整合する(矛盾なし、新規発見というより再確認)。

## §C〜§J

Phase B未実行のため該当なし(Stage 0/1/2生成・parser/validator実行・
downstream・api_meta・cost・Prompt echo観測・日本語対照はいずれも
未実施)。

## §K Production恒久変更なし宣言(Phase A時点)

Phase A時点ではProduction code(`er003_*`/`er006_*`/`er010_*`/`er011_*`/
`er012_*`等)を1行も変更していない(read-onlyのRead/Grepのみ、importも
実行もしていない——Phase Bを実行していないためAPI呼び出し自体が発生
していない)。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`も変更
していない。費用は¥0(recon作業のみ、API呼び出しなし)。

---

# Phase B(2026-09-24、ユーザーOption (a)承認後)

実装: `er017_news_entertainment_production_line_trial_01.py`(新規Trial
entry point、Production codeを1行も変更せずimportして呼ぶのみ)。
成果物: `er017_output/news_entertainment_production_line_trial_01/`
配下全て。回帰テスト: `er017_news_entertainment_production_line_trial_01_test_01.py`
(18件、API呼び出しなし、`run_project_regression.py --pattern
"er017*_test_*.py"` で全PASS)。

Phase Aで判明したP1(既存News Writer入口`run_one_pattern`はEditorial
instructionとLedger運用手順が分離不可能)への対応: `run_one_pattern`は
一切呼ばず、Trial専用の新規WriterループをResponses APIへ直接構築した
(既存`COMMON_BLOCK_TEMPLATE`/`B1_B_DIRECT_INSTRUCTION`は不使用、§3/§4)。
Gate検査は個別の既存関数(`validate_point_structure`/`run_deviation_check`/
`build_canonical_spelling_fact_check_block`/`run_point_overlap_qa_and_
regenerate`)を直接importして呼ぶことで実現した(§9/§10)。P2(Ledgerを
新規Web検索なしに作れない)は、ユーザーがOption (a)(正式Research/
Verificationで新規Ledgerを作ることを許容)を承認したことで解消した
(§1)。downstream(Key Phrase/TTS/Assembly)は、B-Family Voices専用の
`er012_b_family_production_runner_01.main_b1_2v`系ではなく、News単一
Writer構造(Title/Main Story/###×2/## In one line)に対応する
`er003_v1_n3_01_scaffold_generate.py`/`er003_v1_n3_01_tts_generate.py`/
`er003_v1_n3_01_assemble.py`(Hanshin等の既存News音声実装のreference、
`er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py`と
同型の呼び出し構造)を使用した(§11)。

## §1 Research / Verification結果

- 呼び出し関数: `run_researcher_for_topic(client, topic)`/
  `run_verification_for_topic(client, topic, ledger_parsed)`
  (`er017_news_entertainment_production_line_trial_01.py`内、
  `vfl01.build_researcher_prompt(topic=)`/`vfl01.build_verification_prompt(
  topic, ...)`というtopic引数を明示的に渡せる既存関数を使い、
  `vfl01.run_researcher()`/`run_verification()`と全く同じ呼び出し構造
  [model/reasoning/tools/text.format/developer+user message]を、topicだけ
  差し替えて再現。`vfl01.run_researcher()`自体はモジュール定数`TOPIC`
  [Hanshin固定]をデフォルト引数で暗黙に使う実装のため直接呼べない制約が
  あり、これは`er011_news_stage3_new_theme_ledger_trial_09.py`の既存
  precedentと同一の対応)。
- 引数: `model=vfl01.MODEL`("gpt-5.6-luna")、`reasoning={"effort":
  vfl01.REASONING_EFFORT}`("high")、`tools=[{"type":"web_search"}]`、
  `text.format=vfl01.FACT_LEDGER_JSON_SCHEMA`/`vfl01.VERIFICATION_JSON_SCHEMA`、
  developer message=`vfl01.RESEARCHER_DEVELOPER_MESSAGE`/
  `vfl01.VERIFICATION_DEVELOPER_MESSAGE`(いずれもProduction定数を無変更で
  使用)。
- テーマ: 「AIに店への電話を頼んだら、裏では人間が話していた（MetaのAI
  電話代行機能「Muse」の人間コンシェルジュ実験、Reuters 2026年9月22日
  報道）」。
- 実測: Researcher `model=gpt-5.6-luna`、`response_id=
  resp_075744fde9e2a230006ab49d7feb9087d092d686117ac3c4be`、web_search
  呼び出し5回、facts=18件、所要81.3秒、費用$0.0707(¥11.31)。
  Verification `model=gpt-5.6-luna`、`response_id=
  resp_0b348b53e66d1d48006ab49dd0527487d0abbae7df98b29279`、web_search
  呼び出し3回、所要45.5秒、費用$0.0446(¥7.14)。
  検証結果: VERIFIED=17、AMBIGUOUS=1、REJECTED=0(kept_facts=18)。
- Ledger保存先: `er017_output/news_entertainment_production_line_trial_01/
  ledger/verified_fact_ledger.txt`(Productionと同一形式、
  `vfl01.build_verified_ledger_text()`を無変更で使用)。下書き・検証結果は
  `ledger/fact_ledger_draft.json`/`ledger/fact_ledger_verification.json`、
  raw response/usage/sourcesは`ledger/audit/researcher_full_record.json`/
  `ledger/audit/verification_full_record.json`。
- Source一覧(fact_idが参照する一次/二次情報源): about.fb.com(Meta公式
  「Introducing Muse」発表)、marketscreener.com(Reuters配信記事
  「Meta testing a 'human concierge' for its new personal AI agent,
  Muse」)、404media.co(Meta社内投稿を確認した独立報道)。
- Productionと同一条件であることの根拠: 本節の呼び出し構造は
  `er011_news_stage3_new_theme_ledger_trial_09.py`
  (`run_researcher_for_topic`/`run_verification_for_topic`、L272-313)の
  既存precedentと同一パターンであり、同precedentは
  `docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-
  OBSERVATION-01_NEWS_R1.md`が「Hanshin以外の新規News Ledgerを既存
  Research正式経路で作成」した先例として明記する経路そのもの
  (DECISION_LOG L941系、費用単価は「量産時1記事単価」の「Research/
  Ledger生成」区分として計上済みの前例)。

## §2 使用Prompt全文 + P7対照表

### developer message(3 Stage共通)
```
You are a writer who explains the news clearly and makes it enjoyable to read.
```

### 英語Entertainment Prompt(骨子、P7対応)

| P7(日本語、`docs/evidence/news_iterative_r2_adoption_2026-09-24/prompts.md`) | 英語Entertainment Prompt(本Trial、逐語) |
|---|---|
| 以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。 | Turn the news below into a piece you might share with a friend, the way you'd say "Hey, isn't this kind of interesting?" |
| ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。 | From the news, pick not the most surprising fact but the single most interesting way of looking at it, and build the piece around that. Use mainly the facts needed for that viewpoint; do not try to cover the whole story. |
| 語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。 | Keep the tone natural and light. Do not write like a newspaper, a government document, or a school textbook. |
| 難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。 | Write so that a learner of English can understand it by listening to it once. |
| 遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。 | If the news might look like something specific to a distant place only, show its connection to the reader's own life or to a larger social change, just once. But you don't need to force the story to feel bigger than it is. |
| 事実関係は厳守し、架空の出来事や発言は加えません。 | Stick strictly to the facts. Do not add fictional events or quotes. |
| テーマ：〈今回のテーマ〉 | Theme: I asked an AI to call a store for me, and it turned out a human was secretly on the line (Meta's AI phone-calling feature, Muse, and its "human concierge" experiment, as reported by Reuters on September 22, 2026). |
| 長さ：800～1000字 / 出力はタイトルと本文のみ。 | (P7側のこの2行は日本語文字数指定・出力形式指定であり、英語B1版では下記
Production contractの`Length`/`Format`行に置き換えた。追加削除なし、
役割の対応関係のみ変更) |

### Production contract(追加部分、Stage0のみ)
```
Write in English.
Length: about 280–420 words in total.
Format (Markdown): start with "# " followed by the title; then the main story; then exactly two "### " subsections, each 30–60 words, with headings that describe their content in your own words (do not use labels like "Point One"); then a final section headed exactly "## In one line" containing one sentence.
```
(Phase A §A「前提」節で確定した既存構造contract[heading表記`# `/
`### `×2/`## In one line`、Length Target 280〜420語]と一致。実測は
`er017_news_entertainment_production_line_trial_01_test_01.py`の
`ContractMatchesPhaseAConfirmedContractTest`で機械的に検証、PASS)。

Stage0のuser messageは、上記Entertainment Prompt(7行)+空行+Production
contract(3行)+空行+`[News — Verified Fact Ledger]`+Ledger全文(§1参照)
を連結したもの(`STAGE0_USER_TEMPLATE`)。

### Stage1(R1)指示 + contract 1行
```
この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。

Keep the same Markdown structure (the "# " title, the main story, exactly two "### " subsections, and the "## In one line" section); do not add or remove sections. Write in English.
```

### Stage2(R2)指示 + contract 1行
```
この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。

Keep the same Markdown structure (the "# " title, the main story, exactly two "### " subsections, and the "## In one line" section); do not add or remove sections. Write in English.
```

Stage1/Stage2は`previous_response_id`で直前応答へ連鎖(userメッセージ
のみ送信、developerメッセージは再送しない。3テーマとも
`previous_response_id`方式が成功、フォールバック未使用の既存Trial-02
慣行と同じ挙動を確認)。web_searchは使用せず(tools引数省略)、schemaも
使用しない(プレーンMarkdown出力)。

## §3〜§4 Production contract(§2に統合、上記参照)

## §5 英語Original全文(Stage0)

```markdown
# The AI Phone Call That Needed a Human

The interesting part of Meta's new AI agent, Muse, is not simply that it can make phone calls. It is that, in some tests, the AI needed a human to make those calls work.

Meta introduced Muse in the United States on September 8, for iOS, Android, and the web. It is designed to handle tasks such as sending emails, booking travel, filling in forms, browsing websites, and negotiating for users. Reuters reported that Muse could also call American businesses to book a haircut, check store stock, or ask several companies for prices.

But during internal testing in August and September, some phone requests were passed to trained human agents. Those people made the calls instead. Internal messages described a system that would return a record and summary of the conversation to the user.

Why use a human? Reuters reported that some people ended calls after realizing they were speaking with an AI. In other words, the problem was not only whether Muse could speak clearly. It was whether the person on the other end would accept an AI as a caller. In some internal tests, calls handled by humans had a reported success rate of 95% to 98%; the AI-only rate was lower, though no exact figure was given.

That makes the experiment a neat picture of where automation gets difficult. A machine may be able to perform the task, but social trust is part of the task too.

### The human helper was meant to stay out of sight

The test covered about half of Meta's employees, with an opt-out group for people who did not want to join. The human helper was not supposed to be presented as the main feature. But Reuters reported that Meta later paused the system after recognizing that using contractors without proper disclosure was a problem.

### Convenience brought a privacy question

Some employees worried that personal or sensitive information could reach call-center workers. In one reported case, a worker found an inappropriate racial remark in a call record from a human contractor. Meta said the contractor would not handle its cases again, and said wider release would wait for better privacy and disclosure protections.

## In one line

Muse shows that the hardest part of an AI phone call may not be talking to a business, but getting the business to trust who—or what—is calling.
```
語数: 総377語(soft range 280-420内)、Point One 55語、Point Two 54語。
model実値=gpt-5.6-luna、response_id=
`resp_0cf00b77d9149ca3006ab49e19df7087d0bb7f25260e40124a`。

## §6 英語R1全文(Stage1)

```markdown
# Plot Twist: Meta's AI Caller Needed a Human

Meta's new AI agent, Muse, has a wonderfully modern problem: it can make a phone call, but people sometimes do not want to talk to it.

Meta introduced Muse in the United States on September 8, for iOS, Android, and the web. The agent is designed to send emails, book travel, fill in forms, browse websites, and negotiate for users. Reuters also reported that Muse could call American businesses to book a haircut, check whether a store had an item, or collect prices from several companies.

Then came the plot twist. During internal testing in August and September, some phone requests were handed to trained human agents. The humans made the calls instead. According to internal messages, the system was designed to give the user a record and summary of the conversation afterward.

The reason was surprisingly human: some people hung up when they realized that Muse was an AI. So the challenge was not just, "Can the machine speak?" It was also, "Will the other person stay on the line?"

In some internal tests, calls handled by humans had a reported success rate of 95% to 98%. Reuters said AI-only calls did worse, although it did not give an exact number. That makes the experiment feel less like a simple technology test and more like a test of social manners. The machine could do the job, but a human voice sometimes opened the door.

### The invisible helper was not ready for a public debut

The human-concierge test was turned on for about half of Meta's employees, while others could opt out. But Reuters reported that Meta temporarily rolled it back after recognizing that using contractors without proper disclosure was a problem. Meta said it would wait before wider release.

### The shortcut created a privacy problem

Some employees worried that personal or sensitive information might reach call-center workers. In one reported case, a call record included an inappropriate racial remark by a human contractor. Meta said that contractor would not handle its cases again and said better privacy and disclosure protections were needed.

## In one line

Muse discovered that the hardest part of an AI phone call may not be speaking like a human, but being trusted like one.
```
語数: 総352語、Point One 47語、Point Two 48語。model実値=gpt-5.6-luna、
response_id=`resp_0cf00b77d9149ca3006ab49e2cf7c087d096fda821a9350559`、
previous_response_id=Stage0のresponse_id。

## §7 英語R2全文(Stage2、Final article)

```markdown
# Muse, the AI Caller With a Human Plot Twist

Meet Muse, Meta's AI agent. It can send emails, book travel, fill in forms, browse websites, and negotiate for its users. It can also call American businesses to book a haircut, check store stock, or ask several companies for prices.

That sounds like a tidy little future: tell the AI what you want, and let it handle the boring phone call.

Then the script takes a sharp turn.

During internal testing in August and September, some requests made through Muse were passed to trained human agents. Those humans made the phone calls instead. Internal messages described a system that would later give the user a record and summary of the conversation.

Why bring a human into an AI phone call? Because some people hung up after realizing they were speaking with an AI. Muse could say the words, but the other person might refuse to stay for the conversation. The machine had learned an awkward lesson: sounding human is not the same as being welcomed as a caller.

In some internal tests, calls handled by humans had a reported success rate of 95% to 98%. Reuters said AI-only calls performed worse, but did not provide an exact number. So the experiment became more than a test of speech technology. It became a test of trust, with Muse giving instructions backstage while a human took the stage.

### The surprise co-star was not ready for opening night

The human-concierge test was enabled for about half of Meta's employees, and employees who did not want to take part could opt out. Reuters reported that Meta temporarily rolled the feature back after recognizing that contractor-made calls without proper disclosure were a problem. Meta said wider release would wait.

### The backstage helper raised privacy concerns

Some employees worried that personal or sensitive information could reach call-center workers. In one reported case, a call record contained an inappropriate racial remark by a human contractor. Meta said that contractor would not handle its cases again and said stronger privacy and disclosure protections were needed.

## In one line

Muse's big phone lesson was that an AI may need a human co-star when people refuse to listen to the machine.
```
語数: 総349語(soft range内)、Point One 52語、Point Two 48語(いずれも
目安30〜60語の範囲内)。model実値=gpt-5.6-luna、response_id=
`resp_0cf00b77d9149ca3006ab49e33928087d095bbee8fc8b10bcc`、
previous_response_id=Stage1のresponse_id。

## §8 Titleの変化

| Stage | Title |
|---|---|
| Stage0(Original) | The AI Phone Call That Needed a Human |
| Stage1(R1) | Plot Twist: Meta's AI Caller Needed a Human |
| Stage2(R2、Final) | Muse, the AI Caller With a Human Plot Twist |

Revisionを重ねるごとに「AI電話に人間が必要だった」という事実提示型の
Titleから、「Plot Twist」「co-star/opening night」という舞台・脚本の
比喩を使ったEntertainment色の強いTitleへ変化した(§17 Editorial
Quality評価は[Fable記入])。

## §9 parser / Structure Validator結果

`gen.split_common_sections_for_point_qa()`(parser)と
`restore_r2.validate_point_structure()`(Structure Validator)を各Stage
の記事全文へ実行(`gate_stage{0,1,2}.json`)。

| Stage | parser | structure.status | h3_count |
|---|---|---|---|
| 0 | PARSE_OK | STRUCTURE_PASS | 2 |
| 1 | PARSE_OK | STRUCTURE_PASS | 2 |
| 2 | PARSE_OK | STRUCTURE_PASS | 2 |

全Stageでparser/Structure Validatorともに構造崩れなし(`###`見出し
ちょうど2つ、`## In one line`検出、本文非空)。

## §10 Ledger Deviation / Fact Check結果

`vfl01.run_deviation_check(client, ledger_text, article_text)`(既存
Production関数、Ledger=§1)を各Stageへ実行。

| Stage | overall_status | MAJOR件数 | MINOR件数 |
|---|---|---|---|
| 0(Original) | LEDGER_DEVIATION | **1** | 0 |
| 1(R1) | LEDGER_COMPLIANT | 0 | 0 |
| 2(R2、Final) | LEDGER_COMPLIANT | 0 | 0 |

Stage0のMAJOR内容(`unsupported_new_claim`+`changed_fact`):
「The human helper was not supposed to be presented as the main
feature.」という一文が、Ledgerが保証していない「人間ヘルパーを目立た
せない意図があった」という新しい具体的主張を追加していると判定された
(`gate_stage0.json`の`deviation.major_items`に全文記録)。**この
MAJORはTrial側で書き換えず、既存Local Rewrite等も呼ばず**、そのまま
記録している(委任文の禁止事項どおり)。Stage1/Stage2は同じ論点を
「The human-concierge test was turned on for about half of Meta's
employees」等、Ledger(MUSE-007)が直接支持する表現へ書き換えており、
その結果MAJORが解消した(Writer側の自然な改善であり、Trial側の介入は
一切なし)。

Fact Check block(canonical spelling、`canon_spelling.build_canonical_
spelling_fact_check_block(ledger_text)`、ローカル検査・API呼び出し
なし): 全Stage共通で空文字(Ledgerに`canonical_en_spelling:`行が無い
ため。これは正常な既定挙動)。

Point Overlap QA(`gen.run_point_overlap_qa_and_regenerate()`、
`POINT_ONLY_REGENERATION_ENABLED=False`のProduction既定値のまま、
**検査のみで再生成は発生しない**ことを実行前に確認済み[Phase A時点の
P5判定はこの関数の存在で解消]): 全Stageで`status=OK`、Point One/Two
相互・Full Story対比ともにoverlap_ratioは0.22〜0.31で閾値0.40未満、
`flagged=false`(Stage2実測は`gate_stage2.json`参照)。

**Stage2(final)は全項目PASS**のため、委任文Step6の条件どおり
downstreamへ進めた。

## §11 downstream到達点

`er017_output/news_entertainment_production_line_trial_01/b1b/`配下。
Trial theme id=`entertainment_trial_meta_muse`(既存Production記事と
分離、theme config moduleは新規作成不要——`er003_v1_n3_01_scaffold_
generate.py`/`tts_generate.py`/`assemble.py`はtheme辞書
`{"theme_id":..., "out_dir":...}`とファイルパス規約[`{out_dir}/b1b/
article.md`等]だけで動作するため)。

| Stage | 結果 | 詳細 |
|---|---|---|
| article.md配置 | OK | Stage2全文をbyte-identicalコピー(sha256一致確認済み) |
| Scaffold(Preview/Comment1-4) | OK | 全5要素`status=OK`(`b1b/b1_support_texts.json`) |
| Key Phrase | PASS | selection=KEY_WORDS_STRUCTURE_PASS、canonicalization=CANONICALIZATION_PASS、redundancy_qa=REDUNDANCY_PASS(`b1b/key_phrases/`) |
| TTS(Standard同期) | 一部STOPPED | `full_story_part2`セグメントがASR検証3回とも不合格(`TRUE_CONTENT_MISMATCH`、句読点位置起因の軽微な書き起こし差異)で`status=STOPPED`。他セグメント(topic_intro/preview/comment1-4/point_one/point_two/headings/key phrase音声等)は生成済み(`b1b/narration/`) |
| Assembly | **BLOCKED(既存Audio Validation Gate)** | `asm.stage_assemble_b1()`が`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で例外(`['full_story_part2=STOPPED']`)。Gateは**overrideせず**そのまま記録して停止(委任文9節の禁止事項どおり) |
| Audio Validation Gate opt-in ON経路 | SKIPPED(gate_off_blocked) | Assembly自体が未完了のため未実行 |

生成物path: `er017_output/news_entertainment_production_line_trial_01/
b1b/{article.md,parts.json,b1_support_texts.json,key_phrases/,
narration/,audit/}`、`downstream_log.json`(全stage結果のraw)。
Human Review Lockは発生していない(Audio Validation Gateのみ)。theme
config moduleの新規作成は不要だった(Production codeが要求する入力は
theme辞書とファイルパス規約のみ)。

## §12 Audio生成有無

**部分生成のみ**。`topic_intro`/`preview`/`comment_1`〜`comment_4`/
`point_one`/`point_one_heading`/`point_two`/`point_two_heading`/
key phrase音声4件(en/ja)等は生成済み(wavファイル、
`b1b/narration/`)。しかし`full_story_part2`(Main Story後半)が
ASR検証3回不合格でSTOPPEDのため、**完成episode audio(assembled mp3/
player.html)は生成されていない**(Assembly BLOCKED、§11)。新しい
retry/fallback仕様(4回目の試行、閾値緩和等)は追加していない
(委任文の禁止事項・STOP条件どおり)。

## §13 R2 Title

**Muse, the AI Caller With a Human Plot Twist**
(今回の正式表示HookはこのR2 Titleそのもの。別Hook Generatorは合否に
使用していない)

## §14 比較観測用Luna Hook(合否に無関係、Side output)

`er016_news_r2_to_hook_trial_01.py`のPrompt逐語(developer/user
template/schema)をそのまま流用し、テーマ文(§1のTOPIC_JA)+Stage2全文
(英語)を入力にLuna・effort medium・1 callで生成。

- hook_ja: 「AIが店に電話するはずが、裏で人間が話していた？」
- used_angle_ja: 「Museの電話依頼が人間のコンシェルジュに渡され、代わり
  に電話していた場面を使いました。」
- model実値=gpt-5.6-luna、response_id=
  `resp_01b3ac2c9dc849c4006ab4a0faea2c87d0a54a7d89246bd270`、
  費用$0.00047(¥0.075)、所要3.6秒。

`R2 Title vs Luna Hook`比較表(`hook_comparison.md`と同内容):

| R2 Title(English、Production正式表示Hook) | Luna Hook(比較観測用、合否に無関係) |
|---|---|
| Muse, the AI Caller With a Human Plot Twist | AIが店に電話するはずが、裏で人間が話していた？ |

## §15 actual model_id(全call共通)

Research/Verification/Writer Stage0-2/Ledger Deviation Checker/Side
Hookのいずれも`response.model`実測値は**`gpt-5.6-luna`**
(要求モデルと完全一致、fallbackなし)。Scaffold/Key Phrase support call
もLuna(`routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)`
経由、既存Production挙動のまま)。TTS音声はGemini(`gemini-2.5-pro-
preview-tts`系、既存Production設定のまま)。

## §16 cost / latency

Step別費用(USD→JPY、レート160、`cost.json`+`raw_usage_log.jsonl`を
`er012_b_family_production_runner_01.compute_cost_jpy_so_far()`で
集計):

| Step | 費用(JPY概算) | 主な内訳 |
|---|---|---|
| Research(Researcher+Verification) | ¥18.45 | web_search計8回、gpt-5.6-luna high |
| Writer(Stage0/1/2) | ¥0.87 | previous_response_id連鎖、web_searchなし |
| Gates(Deviation Checker×3 + Point Overlap QA×3) | 上記raw_usage_log合算に含む | Deviation Checkerのみgpt-5.6-luna high、Point Overlap QAはローカル計算(API呼び出しなし) |
| Downstream(Scaffold+Key Phrase+TTS) | 差分約¥23 | openai(Scaffold/KP)+gemini(TTS、最大費目)+openai_asr(検証) |
| Side Hook | ¥0.075 | gpt-5.6-luna medium、1 call |
| **合計** | **¥42.50** | 内訳: openai ¥11.43 / gemini ¥29.54 / openai_asr ¥1.53 |

上限¥250に対し**¥42.50(16.8%)** で完了、超過なし。latencyはResearcher
81.3秒・Verification 45.5秒・Writer各Stage 6.5〜19.2秒・Side Hook
3.6秒(詳細は`api_meta_stage{0,1,2}.json`/`ledger/audit/*.json`/
`side_hook_luna.json`)。

## §17 Editorial Quality評価

[Fable記入]

## §18 日本語Trialとの比較

[Fable記入](参考: `comparison_ja_en.md`に日本語原文[Trial-02 A_original/
A_revision1/A_revision2]と英語Stage0/1/2の対応関係を機械的に並記)

## §19 Trial status分類

[Fable記入](Sonnet提案: 記事生成〜Gate PASSまでは`VALIDATED`、
downstreamはAudio Validation Gateにより`PARTIAL(audio incomplete、
既存安全機構により正常停止)`。最終分類はFable判断)

## §20 USER_DECISION_REQUIRED事項

[Fable記入](Sonnetからの技術的な論点提示: (a) `full_story_part2`の
ASR不一致は既存TTS retry/cooldown機構の範囲内で解消するか観測する
価値があるか、(b) 英語Entertainment Writer方式の他テーマへの展開要否、
(c) Stage0で検出されたMAJOR逸脱[§10]のような「Ledgerが直接支持しない
解釈の追加」を、Revision(R1/R2)が自然に解消する挙動を、正式Gate設計の
参考情報として扱うかどうか)

## §21 Production恒久変更なし宣言(Phase B)

Production code(`er003_v1_n3_01_articles_generate.py`/`er003_v1_en_
direct_vfl_01_generate.py`/`er002_ja_free_markdown_restore_r2.py`/
`er011_open146_ledger_canonical_en_spelling_production_01.py`/
`er012_b_family_production_runner_01.py`/`er006_model_routing_
contract_01.py`/`er003_v1_n3_01_scaffold_generate.py`/`er003_v1_n3_01_
tts_generate.py`/`er003_v1_n3_01_assemble.py`)は、Phase B実行前後で
sha256完全一致(全ファイル、全snapshotタグ`pre_research`〜
`post_side_hook`を通じて1種類のhash値のみ、
`production_code_sha256.json`)。`git status --short`で上記ファイルに
差分なし(§9のsha256一致と整合)。`CURRENT_SPEC.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`も本Phase Bでは変更していない(SSOT追記なし、委任文の
指示どおり並行タスクとの衝突を回避)。`PRODUCTION_WIRED`/
`APPROVED_FOR_PRODUCTION`への変更は行っていない(到達上限`VALIDATED`)。
