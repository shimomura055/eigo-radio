# FX-NEWS-SOURCE-LIST-CONFIRM-01 委任_01 確認結果(Read-only、2026-10-24)

範囲: 既存記録の確認のみ。API 0・SSOT/コード変更0・サイト追加/変更/新規探索なし。記録が無い項目は「記録なし」と記載(推測で補わない)。
原文: `docs/pm/delegation_log/2026-10-24_FX-NEWS-SOURCE-LIST-CONFIRM-01_USER.md`

## 結論(先出し)
- ユーザー合意済みのニュースソース一覧は **1件のみ記録あり**: 2026-09-25ユーザー正式決定 `TOPIC-DISCOVERY-MANUAL-SELECTION-OPERATING-POLICY-01` の「Sensorサイト候補」**13サイト**(海外6+国内7)+除外済み3サイト。
- 「10サイト前後」に当たる記録は上記13サイトのみ。他に合意済みの別リストはRepo内で見つからなかった。
- **URLの記録はどのSSOT・委任文にも無い**(サイト名のみ)。**サイトごとの個別選定理由の記録も無い**(共通の選定思想のみ。(a)注)。
- 直近性は「原則直近24時間中心」。ただし「厳格な24時間ルールをProduction仕様として固定しない」「24時間条件の厳密性は未決(OPEN-180項目8)」。
- 上記方針は `DECIDED / OPERATING_POLICY_ONLY`(運用方針の記録のみ。Production仕様[APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED]ではない)。「Poolは今後変更可、恒久固定仕様ではない」。

## (a) 合意済みサイト一覧(Sensorサイト候補、13サイト)
根拠: `CURRENT_SPEC.md:2722-2726`(節見出し L2704)/`DECISION_LOG.md:9578`(エントリ L9570-9590)。合意日: 2026-09-25。ユーザー承認: 「ユーザー正式決定」(`DECISION_LOG.md:9572` 区分欄)。承認記録の所在: DECISION_LOG当該エントリの「ユーザー指示原文(逐語要旨、11項目)」。**ユーザー原文そのものの逐語ファイルはdelegation_logに無い**(逐語「要旨」のみ。実行委任文=`docs/pm/delegation_log/PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01.md`の(B)は記録作業の指示で、原文逐語ではない)。

| # | 区分 | サイト名 | URL | 個別の選定理由 |
|---|---|---|---|---|
| 1 | 海外 | 404 Media | 記録なし | 記録なし |
| 2 | 海外 | Oddity Central | 記録なし | 記録なし |
| 3 | 海外 | PsyPost | 記録なし | 記録なし |
| 4 | 海外 | Axios | 記録なし | 記録なし |
| 5 | 海外 | Semafor | 記録なし | 記録なし |
| 6 | 海外 | Ars Technica | 記録なし | 記録なし |
| 7 | 国内 | GIGAZINE | 記録なし | 記録なし |
| 8 | 国内 | ナゾロジー | 記録なし | 記録なし |
| 9 | 国内 | デイリーポータルZ | 記録なし | 記録なし |
| 10 | 国内 | カラパイア | 記録なし | 記録なし |
| 11 | 国内 | Togetter | 記録なし | 記録なし |
| 12 | 国内 | ITmedia NEWS | 記録なし | 記録なし |
| 13 | 国内 | 東洋経済オンライン | 記録なし | 記録なし |

注(選定理由): サイト個別の理由は記録なし。一覧全体に関わる共通の記述のみ存在する。
- 「定点Sensorサイト」=話題の入口(Topic Sensor)。「記事は完成TopicではなくSeed」「SNS→Fact SourceではなくTopic Sensor」(`CURRENT_SPEC.md:2745-2749`)。
- 日本トップ3件+世界トップ3件は「Sensorサイトの取りこぼしを補完する」ため(`CURRENT_SPEC.md:2750-2752`)。

### 除外済みサイト(同決定、`CURRENT_SPEC.md:2725-2726`)
Know Your Meme / まいどなニュース / Jタウンネット。除外理由: 記録なし。

## (b) 候補として挙がったが正式合意の記録がないサイト(別表)
| サイト/情報源 | 出所(ファイル:行) | 性格 |
|---|---|---|
| Google Trends日本、Yahoo!リアルタイム検索、Togetter/ねとらぼ/ITmedia等のSNS話題まとめ、X/TikTok/Threadsの公開ページ | `docs/pm/delegation_log/TOPIC-SELECTION-LUNA-API-TRIAL-01.md:58` | Trial(2026-09)内の取得可否確認用Prompt要旨。合意リストではない |
| トレンドカレンダー、Twittrend、Google Trends日次(SNS/Trend Signal) | `docs/pm/delegation_log/TOPIC-SELECTION-CHATGPT-REPRO-01.md:77` | Trial再現条件。合意リストではない |
| Reuters, AP, AFP, Bloomberg, NYT, BBC, CNN, Guardian, WSJ, TechCrunch, The Verge, 朝日, 読売, 日経, NHK, ITmedia, Impress, GIGAZINE, ねとらぼ, Engadget 等 | `er016_topic_selection_luna_api_trial_01.py:864-880`(`SOURCE_CLASSIFICATION_RULES`) | Trial結果の**出典分類用キーワード**。探索対象リスト/allowlistではない |
| PsyPost(2026-10-20)、ITmedia NEWS(2026-10-20) | `docs/pm/delegation_log/2026-10-21_FAMILY-X-TWO-ARTICLES-PARALLEL-PRODUCTION-E2E_USER.md`(Source行) | ユーザーが記事単位で指定した出典。両者は(a)の13サイトに含まれる |
| GIGAZINE(2026-10-23記事) | `er019_output/word_gacha/theme.txt:1` | 「英単語ガチャ」記事の一次情報。(a)に含まれる |

コード・設定・JSONにRSS一覧/allowlist/`search_domain_filter`/`allowed_domains`等のFamily X候補探索用ソース設定は**見つからなかった**(Grep、`.venv`内ライブラリ定義を除く)。Perplexity経由の探索(PERPLEXITY-401-INVESTIGATION-01)やテーマ選定プロンプトのサイト指定の個別精査は**未確認**。

## (c) 現在の正式な記事候補探索ルール
### c-1 Topic Selection量産初期運用方針(2026-09-25、`DECIDED / OPERATING_POLICY_ONLY`)
出所: `CURRENT_SPEC.md:2704-2796`(項目番号は同節の番号)、`DECISION_LOG.md:9570-9590`。
1. 完全自動化は未実施。実運用で数百件規模のユーザー選定データを蓄積してから再検討(項1)。
2. 基本フロー: AIが定点Sensorサイトを巡回→各サイト原則3記事程度+日本トップ3件+世界トップ3件を候補へ→AIが候補ごとにHook/仮タイトル・概要・切口を提示→ユーザーがフォーム等で10記事程度を選定→AIが記事生成(項2、項9)。
3. 学習データ: 選択(Positive)と未選択(Negative)の両方を保存(項3)。
4. 候補抽出の優先順位: 優先1=サイト自身の人気・注目シグナル(24時間ランキング/Access Ranking/Most Read/Popular/Editor's Pick/Top Stories等)を入口。優先2=無ければAIが直近記事から判断(Hookの強さ/一般読者への広さ/Self relevance/「え、そうなの？」感/自然なAngle展開/話したくなるか/日本人読者との接点/教育的説明で終わらないか)。人気ランキングをそのまま採用せず、その中からeigo-radio向け候補を選ぶ(項5)。
5. **鮮度(直近性)**: 「原則直近24時間中心。更新頻度が低い媒体・Evergreen媒体・非常に強い題材の扱いは後日。厳格な24時間ルールをProduction仕様として固定しない」(項6、`CURRENT_SPEC.md:2733-2735`)。
6. タイトル/Hook: 不要な固有名詞を避ける(Trump/ChatGPT/iPhone/大谷翔平のように広い認知があれば可)(項7)。
7. 思想: 記事は完成TopicではなくSeed。記事タイトルをそのまま採用しない。Big News→自分事へ、Tech→生活変化へ等(項8)。Big Newsも「なぜ一般人に関係するのか」までAngle化(項9)。
8. 未決(勝手に仕様化しない、`OPEN_ITEMS.md:361` OPEN-180): フォーム設計/入力タイミング/候補件数の正式値/選定件数の正式値/自動選定fallback条件/完全自動化の基準/Sensor巡回頻度/24時間条件の厳密性/人気ランキング取得方式/保存schema/rerank実装方式(項11)。

### c-2 記事構成・Family X選定方式(2026-10-12、`TOPIC-SELECTION-FORM-AND-FAMILY-MIX-20261012-01`)
出所: `CURRENT_SPEC.md:2798-2810`、`DECISION_LOG.md:20670`、`docs/pm/delegation_log/2026-10-12_TOPIC-SELECTION-FORM-AND-FAMILY-MIX-20261012-01_01.md`。
- Family X 8記事選定のため**24候補**を提示。6ジャンル分類、各候補に時事型/準Pool型/Evergreen型を付与。面白さ優先でジャンル別件数は固定せず、8に満たなければ無理に選ばず追加候補を提示。選択・非選択・繰越の履歴を区別管理。
- 日本TOPニュース1+世界TOPニュース1を先に選定し、他記事から実質同一の出来事・内容の重複を除外(題名のみでなく内容重複も対象)。
- サイト一覧・鮮度条件への言及なし(サイトに関する新規決定は記録なし)。承認フォームはChatGPTライブラリ管理でRepo非保存。

### c-3 新規記事テーマ選定ルール(恒久、`docs/pm/PM_GOVERNANCE.md` 13節 L2846-2894)
- Fable/Claudeがテーマを勝手に決めない。複数候補(英語・日本語・短い選定理由付き)を提示→ユーザーが選択後に生成(13-2)。例外=ユーザーが「テーマ選定も任せる」と明示した場合のみ(13-3)。regen/retry/Local Rewrite/segment再生成は対象外(13-4)。13-6はc-2との整合を明記。

### c-4 除外条件・事実混同禁止
- 除外条件: 明示記録は除外サイト3件のみ。それ以外の汎用除外条件(分野・コンテンツ種別等)を探索ルールとして定めた記録は**見つからず(記録なし)**。
- 「事実混同禁止」は探索ルールの節としては記録なし。Trial委任文には「24時間より古い記事を混ぜて水増ししない」「アクセスできないSNSを推測で補わない」(`TOPIC-SELECTION-LUNA-API-TRIAL-01.md:14`)があるが、**Trial委任文の制約であり正式ルールではない**。

## (d) 見つからなかった項目(記録なし)
- 13サイトの**URL**(全て記録なし)。
- 13サイト個別の**選定理由**、除外3サイトの除外理由。
- 09-25決定の**ユーザー原文逐語ファイル**(delegation_logに無い。SSOTは逐語「要旨」)。
- 13サイト以外のユーザー合意済みニュースソース一覧(別の10サイト前後リスト、RSS一覧、allowlist)。
- 「直近24時間」を厳格なProduction仕様として固定する決定(逆に「固定しない」が記録されている)。
- Sensor巡回頻度、人気ランキング取得方式の決定(OPEN-180で未決)。
- 09-25以降にSensorサイトPoolを変更した決定。

## (e) 矛盾・重複・古い記録(併記)
1. **選定数の差**: 09-25=ユーザーが「10記事程度」選定(`CURRENT_SPEC.md:2713-2716`)。10-12=Family Xは「24候補から8記事」(`CURRENT_SPEC.md:2804`)。後者が新しい。10-12が09-25の件数を明示置換する記載は見つからず、候補件数/選定件数の正式値はOPEN-180で未決のまま。
2. **24時間条件**: 「原則直近24時間中心」と「固定しない」が同一項に併記。Trial(2026-09)は実行時から24時間やその固定窓を使用(`TOPIC-SELECTION-LUNA-API-TRIAL-01.md:14,40`、`TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md:7`)したが、Trial条件。
3. Togetter/ITmedia等はTrialのPrompt要旨(上記L58)にも「SNS話題まとめ」として出現。(a)での位置づけ(Sensorサイト候補)と同一かは記録なし。
4. 10-21のFamily X 2記事(PsyPost・ITmedia NEWS)は(a)に含まれるが、記録上は「ユーザー正式決定」による記事単位の指定で、(a)リスト巡回経由で選ばれたかは記録なし。
5. 09-25の「Poolは今後変更可」以降、Poolを変更した決定はなし。

## 調査範囲(Grep)
`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`HISTORY_INDEX.md`/`docs/pm/`(PM_GOVERNANCE 13節、USER_DECISION_REGISTER、delegation_log)/`docs/research/`/`er015_*.py`/`er016_*.py`/`er019_output/word_gacha`、およびRepo全体のmd/py/json/txtに対する固有サイト名検索(GIGAZINE, Oddity Central, ナゾロジー, デイリーポータルZ, カラパイア, PsyPost, 404 Media, Semafor)、`Sensor|定点|24時間|search_domain_filter|allowed_domains|rss_feeds`。`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS_HISTORY.md`/`ER-*_REPORT.md`は固有サイト名の全体検索でヒット無し(個別精読は未実施)。Perplexity経由の精査は未実施=未確認。
