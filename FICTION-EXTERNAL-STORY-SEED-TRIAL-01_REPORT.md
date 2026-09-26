# FICTION-EXTERNAL-STORY-SEED-TRIAL-01 REPORT

Status: **STOPPED (budget exhausted at S-1, USER_DECISION_REQUIRED)**.
Trial専用。Production Fiction仕様への反映は本タスクの対象外。到達可能上限は
VALIDATEDだったが、本Reportの時点ではS-3/S-4未実施のため、そこには到達
していない(詳細は§9)。

## §1 目的
完全創作方式(Story DNA / Coverage Run / Core Provocation、
`er018_fiction_story_dna_e_axis_redesign_01.py`等)とは別に、実在する
Public Domain / CC0 / 翻案可能ライセンスが確認できる外部ソース(実話・
人生談/実話・歴史的逸話/日本文学(青空文庫)/世界文学(Gutenberg等))を
出発点として、Seed化(抽象化・再構成)した英語学習用短編を試作する
Trial。予算上限¥30(候補探索+Seed化4call+Story生成4call以内)。

## §2 探索Sourceと権利確認
`er018_fiction_external_story_seed_trial_01.py --step search`(4系統、
系統ごとにOpenAI Responses `web_search`ツール付き1 call、
`search_context_size: "low"`、`max_tool_calls: 3`指定)で実行。

| 系統 | 主なSource | web_search_call実測 | 備考 |
|---|---|---|---|
| 01_life_history | loc.gov (American Life Histories, WPA Federal Writers' Project) | 4 | LOCの一般rights statement(政府職員著作物は著作権対象外)を各候補で確認 |
| 02_historical | gutenberg.org / en.wikisource.org | 4 | Gutenbergライセンス文言、Wikisourceの"published before 1931"/著者没後100年表示を確認 |
| 03_japanese_lit | aozora.gr.jp | 4 | 青空文庫の一般方針文(「著作権の切れている作品」は許諾不要)+各作家の没年を確認。**個別カードの「著作権なし」バッジそのものはこの1 callでは未確認**(懸念として記録、§8参照) |
| 04_world_lit | gutenberg.org | 3 | 各ebookページの"Public domain in the USA."表示を確認 |

**重要な観測**: `max_tool_calls=3`を指定したが、実測`web_search_call_count`は
4,4,4,3(4系統中3系統が指定上限を1回超過)。OpenAI側のmax_tool_callsは
厳密なhard capではない可能性がある(過去の`er016_topic_discovery_angle_
broad_luna_trial_01.py`等でも同種の観測があるか未確認、本Trial単独の
観測として記録)。

## §3 候補一覧(4系統、各3〜5件)
全文は以下に保存(URL・確認文言・理由・懸念を表形式で記録済み):
- `er018_output/fiction_external_story_seed_trial_01/stories/01_life_history/candidates.md`(4件)
- `er018_output/fiction_external_story_seed_trial_01/stories/02_historical/candidates.md`(3件)
- `er018_output/fiction_external_story_seed_trial_01/stories/03_japanese_lit/candidates.md`(4件)
- `er018_output/fiction_external_story_seed_trial_01/stories/04_world_lit/candidates.md`(5件)

候補の質的傾向(Sonnet所見、暫定):
- 01: LOC American Life Historiesの個人の具体的エピソード(牛の対決、床屋兼歯医者、移民一家の入植、鉄道労働者の遭遇)。権利根拠は明確(政府職員著作物)だが、各候補とも「具体的エピソードは原稿本文を精読して確認要」という懸念が共通して付いている。
- 02: Franklin自伝の一節、Wikisourceの南軍馬丁の寝返り回想録、ミズーリ日記。権利根拠は明確(Gutenberg/Wikisourceの明記)。
- 03: 芥川「羅生門」、太宰「走れメロス」、宮沢賢治「注文の多い料理店」、梶井基次郎の一編。没年ベースの推定は妥当だが、各カードの個別「著作権なし」バッジ自体は本callでは直接確認できていない(§8で追加検証要)。
- 04: チェーホフ「賭け」、O. Henry「賢者の贈り物」、ガルシン「信号」、モーパッサン「首飾り」、スティーヴンソン「マレトロワ卿の扉」。いずれもGutenbergの"Public domain in the USA."表示あり。「賢者の贈り物」「首飾り」は著名作のため、翻案時は独自性の確保が必要と候補自身が懸念として指摘。

## §4〜§7 (未実施)
S-2(代表4件選定+実URL再検証)・S-3(Seed化)・S-4(Story本文生成)・
評価・旧方式比較は、§9の予算超過のため**未実施**。

## §8 権利上の注意点(Sonnet所見、暫定)
- 「Web公開=自由利用」ではなく、各候補ともソース自身の権利表示(LOCの
  rights statement/Gutenbergのライセンス文言/Wikisourceの"published
  before 1931"表示/青空文庫の方針文)を確認できた候補のみ表に残した。
- ただし青空文庫の4候補は、政策文言(一般方針)と没年は確認できたが、
  各作品カード固有の「著作権なし」バッジ表示そのものは今回のsearch call
  内では直接確認できていない(検索結果のsnippetベース)。S-2で実施予定
  だった実URL fetch(`--step verify`、API課金なしのrequests直接取得)は
  未実施のため、この点は次回作業でのadditional確認が必須(現状のまま
  Seed化・Story生成に進めるべきではない)。
- 「賢者の贈り物」「首飾り」等の著名作は、翻案の独自性確保だけでなく、
  版元・翻訳者クレジット表記の要否についても、Production検討時には
  別途確認が必要(本Trialでは英語原文からの直接翻案を想定しており、
  日本語訳版は使わない)。

## §9 QCD(実績、STOP理由)
- 実行: `--step search`のみ完了(4 call、全て成功、技術的retry 0回)。
- 実測費用: **¥28.83**(内訳: `web_search_call`ツール手数料が主要因。
  4系統合計15 web_search_call × $10/1,000call ≈ $0.15、加えてLuna
  token費用。詳細は`raw_usage_log.jsonl`・`compute_cost_jpy()`実測)。
- 予算上限¥30に対し残り**¥1.17**。委任文が要求するS-3(Seed化4 call)+
  S-4(Story生成4 call)=最低8 call追加は、この残額では実行不可能
  (1 callあたり数円〜十数円規模の見積りに対し、残額が構造的に不足)。
- 委任文の禁止事項「超えそうなら実行前STOP」に従い、S-2以降を実行せず
  ここでSTOPした。API追加課金は発生させていない。
- 観測: `search_context_size: "low"`指定でも、`web_search_call`自体の
  ツール手数料(呼び出し1回ごとに定額)が支配的コスト要因だった(4系統
  合計15回で¥24相当)。今後この方式を使う場合、系統数または1系統あたりの
  `max_tool_calls`をさらに絞るか、予算をS-1側によりよく再配分する設計
  変更が必要(Sonnetの一存では変更せず、次のセクションで判断を仰ぐ)。

## §10 Sonnet仮分類
**STOPPED / USER_DECISION_REQUIRED**(VALIDATEDには未到達。S-1のみ完了、
S-2〜S-4は予算上限のため未実施)。

## §11 [Fable記入]

## §12 [Fable記入]
