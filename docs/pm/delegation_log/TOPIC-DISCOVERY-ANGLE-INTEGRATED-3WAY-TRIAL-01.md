## 管理ID
`TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01`(er015_*、標準ACTIVE_TASK/RESULT_PACKET)を実行中。本タスクは`docs/pm/ACTIVE_TASK_TD.md`/`docs/pm/RESULT_PACKET_TD.md`を使い、er015_*・SSOT(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)に触らない。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。**モデル勝者を決めない**(ユーザー評価前)。Production採用・Production変更・SSOT変更禁止。旧`TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`の成果物は削除・変更しない(検証履歴として保持)。
- **設計の核心**: 「検索→Candidate Pool→別callでrerank」は禁止。各モデルに **Search + Angle Discovery + 追加検索 + Topic Package化 + Selection を1つのResponses API call(web_searchツール付き、内部の複数tool callは許容)** で行わせる。モデルごとにCandidate Poolを固定して渡す方式にしない。
- 3モデル同一条件: 同じ対象24時間(**2026-09-18 00:00〜23:59 JST**、第一候補)/同じSearch範囲(web_search、`search_context_size: "low"`)/同じTeacher Data/同じPrompt(逐語同一、sha256記録)/同じ最終出力件数(10件)/同じeffort(**medium**)/同じjson_schema。
- 費用上限**¥200**(3-way全体、暴走防止)。**実行前に概算**し¥200超過見込みならSTOP。実行順: Luna→(実測から Sol/Terra を外挿。Terra単価UNKNOWNならSolと同額と仮置きして安全側に判定)→Sol→Terra。途中で累計+次call見込みが¥200を超える見込みならその時点でSTOP。
- STOP条件(ユーザー指定): 3モデルで条件が揃わない/Search可能範囲に大きな差がある(例: あるモデルだけweb_search不可)/過去24時間を再現できない(検索結果の公開日時が対象窓に全く合わない等)/Teacher Dataの読み込み条件が揃わない/追加仕様が必要/¥200超過見込み/新しいProduction仕様を勝手に決める必要が出た。STOP時`stop_reason.json`、そこまでcommit(`STOP:`接頭)。
- `git add -A`/`stash`/`amend`禁止。

## 固定ブロック
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は`--short`/`--stat`。F-1: transcript退避不要。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_TDへ1行(FAILでも継続)。

## ユーザー指示要点(全文は末尾【ユーザー指示全文】としてdelegation_logへ保存)
記事はゴールではなくTopic Discoveryのスタート地点。記事発見→Angle Discovery→必要なら追加検索→Topic Package化→選定を同一思考ループで行う。Topic Package最低項目: Source article/Seed、元記事の事実上の核、一般人との接点、そこから自然に生まれる疑問、1〜2段広げられるAngle、必要なら追加検索した事実、最終Topic案、最終仮タイトル、採用/不採用理由。追加情報を創作しない(Angleに追加事実が必要ならそのCandidateについて追加Search可)。Search Sourceは最低2系統: News lane(Big News/国内/海外/経済/生活/Science/Tech/AI/その他)とSocial-signal lane(SNSは事実Sourceではなく Topic Discovery Sensor: Xトレンド/TikTokで話題/SNS急上昇ニュース/Share ranking/SNS反応を報じた記事。SNS起点Topicの事実確認は信頼できる報道または一次情報で)。Angle Discoveryの思考ガイド: Self relevance(仕事/AI/スマホ/お金/住宅ローン/結婚/酒/教育/旅行/健康/日常生活)/Curiosity gap(なぜ？本当に？そんなことできる？意外と逆？)/Expansion potential(1〜2段広げられるか、教育的一般論へ無理に広げない)/Story potential(続きを聞きたくなる流れ)。固定スコアの機械加算は不要。

## 事前指定Read一覧
- `er016_topic_selection_reference_process_trial_01.py`: Grep `web_search|search_context_size|def call_search|def verify|published|def _price|cost`→web_searchツール付きResponses呼び出し・公開日時検証(HTTP実測)・cost集計を流用。
- `er016_news_hook_model_comparison_01.py`: Grep `gpt-5.6-terra|gpt-5.6-sol|effort`→Terra/Sol呼び出しの書き方。
- `er016_topic_selection_user_preference_rerank_trial_01.py`: Grep `def _price|pricing|raw_usage_log|reasoning_tokens`→usage(reasoning tokens含む)の記録方法(前回修正済みのcost関数)。
- `docs/pm/topic_selection_user_eval_dataset.json`: 構造確認(dataset_id/topic_ja/hook_ja/user_score、57件)→Teacher Data副次分として逐語で渡す。
- `er005_output/cost_baseline_01/pricing_snapshot.json`: luna/sol/terra単価(terra UNKNOWN想定)、web_search呼び出し単価があれば。
- `er016_output/topic_selection_reference_process_trial_01/run_meta.json`・REPORT: Grep `window|per_call|¥|JPY`→1 search callあたりの実績費用(概算の根拠)。

## 共通Prompt(3モデル逐語同一。`{teacher_user_examples}`と`{teacher_57}`のみ差し込み、差し込み後の全文sha256を記録)
developer:
```
You are a topic scout for an English-learning news audio program for Japanese adult listeners. Your job is not to collect articles. Each article is only a starting point: find the angle that would make an ordinary listener want to keep listening.
```
user:
```
Target window: news published between 2026-09-18 00:00 and 2026-09-18 23:59 JST. Use web search to explore that day only. If a result is outside that day, do not use it as a seed (you may use it as supporting fact for an angle).

Explore at least two kinds of sources:
1. News lane: big news, Japan, world, economy, daily life, science, tech, AI, and others.
2. Social-signal lane: what people were talking about that day (trending on X, TikTok, share rankings, news reports about social media reactions). Treat social signals as a discovery sensor, not as a source of facts. If a topic starts from a social signal, confirm the facts with reliable news or primary sources.

For each promising seed article, do the following in your own reasoning:
- Identify the core fact of the article.
- Find the connection to ordinary people's lives (work, AI, smartphones, money, mortgages, marriage, alcohol, education, travel, health, daily life).
- Find the natural question that arises (Why? Really? Can that be done? Is it the opposite of what I thought?).
- Expand the story one or two steps into a wider, still concrete topic. Do not expand into a generic educational lesson.
- If the expanded angle needs facts that the seed article does not contain, search for them. Never invent facts.
- Decide whether the result could become an English-learning news audio piece that the listener wants to keep listening to.

This listener has given feedback. Read the examples and infer for yourself what separates the good ones from the weak ones. Do not reduce this to a checklist.

[Listener feedback: topics that worked]
{teacher_user_examples_positive}

[Listener feedback: topics that were weak]
{teacher_user_examples_negative}

[Additional rated examples (1 = would not listen, 10 = would definitely listen)]
{teacher_57}

Drop weak candidates. Then select exactly 10 topic packages. Return JSON only, following the schema. Every seed must have a real URL and its publication date/time. For each package give: seed_title, seed_url, seed_source_name, seed_published_jst, seed_lane ("news" or "social"), core_fact_ja, everyday_connection_ja, natural_question_ja, angle_expansion_ja, extra_search_facts (list of {fact_ja, url}, empty if none), final_topic_ja, tentative_title_ja, why_listener_wants_more_ja, and self_note_ja (why you kept it). Also return dropped_candidates: a list of {seed_title, seed_url, reason_dropped_ja} for candidates you considered but dropped (at least 5). Write all *_ja fields in Japanese.
```
- `{teacher_user_examples_positive}`(逐語、1行1件): AI開発を遅らせるべきか／欧州反発/Anthropicが実験室/T. rexの体温/日銀金利→住宅ローン・物価・生活/能登地震で滝が770m移動/AIで仕事9割減でも早く帰らない/AIなりすまし面接/米中会談→AIが国家間議題/退職代行会社が続かない理由/日本15歳OECDトップ/詐欺容疑者スマホへの遠隔アクセス/火星サンプル→有人火星・火星移住(元ニュース「2031年に火星衛星サンプルを地球へ」だけなら弱いが「月には行けたのに、なぜ火星にはまだ人間が行けない？」「火星有人着陸・火星移住まであと何が足りない？」まで広げると聞きたい)/AI不正侵入→AI control/DXで逆に負荷増/若者3人に1人結婚意思なし/Trump vs judiciary/日本vsウルグアイもAngle次第
- `{teacher_user_examples_negative}`(逐語): 彼岸花/タンチョウ/5G設備共有そのもの(「携帯4社が5G設備を共同利用」だけなら弱い。「5G→6Gになると、私たちの生活は何が変わる？」まで広げると可能性)/農家が困る、だけの米価格/一般的な健康ハウツー/芸能人小ネタ/限定スポーツ選手ニュース/普通の混雑・災害続報/教育的すぎる環境話
- `{teacher_57}`: `dataset_id / topic_ja / hook_ja / user_score`(57件、圧縮しない)。
- json_schema(strict): `{"topic_packages":[10件固定 or minItems 10/maxItems 10], "dropped_candidates":[...]}`。schema厳格化でモデルが失敗する場合は3モデル同一の緩和(minItemsのみ)にし記録。

## 実行手順
1. **概算**: REFERENCE-PROCESS実績(1 search call≈¥8、内部4検索)とRERANKのSol実績(Luna比≈6.6倍)から、1モデルあたり想定内部検索数(20〜30)で概算→`cost_estimate.json`。¥200超見込みならSTOP。
2. **Luna実行**(1 call、`gpt-5.6-luna`、effort medium、tools=[web_search(search_context_size low)]、json_schema)。responseの`output`全体を`arms/L/raw_response.json`に保存し、`web_search_call`アイテム数=検索回数、各検索queryを`arms/L/search_log.md`に抽出。usage(input/output/reasoning)・latency・JPY→`arms/L/api_meta.json`。`response.model`実値。**空出力・schema不一致時は同一条件で1回のみ再実行(記録)**。
3. Luna実測から Sol・Terra の見込みを再計算し、累計が¥200以内なら Sol→Terra を同一条件で実行。超える見込みならSTOP(`stop_reason.json`、Lunaまでの結果はcommit)。
4. **公開日時検証**(選定には使わない、報告用): 各モデル10件のseed_urlをHTTP実測(既存verify関数流用)し、対象窓内/外/不明を`window_compliance.json`に記録(窓外seedは除外せずフラグのみ。ブラインド一覧では表示しない)。
5. **重複統合ブラインド一覧** `USER_EVAL_TOPIC_DISCOVERY_3WAY.md`: 30件を「同一seed事象かつ同一Angle」なら統合(統合判定はURL正規化+タイトル類似[difflib≥0.6]+Sonnet目視、根拠を`merge_log.md`)。異なるAngleは別項目。ランダム順、列: `| # | 仮タイトル | 元ニュース(媒体・日付) | Angle(1〜2段の広げ方) | なぜ一般人が聞きたくなる可能性があるか | 評価(○/△/×) | コメント |`。モデル名・score・self_noteは載せない。対応表`blind_map.json`(#→{arm(s), package index})。
6. **集計資料**: `model_overlap.md`(3ペアのseed重複・Angle重複)、`lane_ratio.md`(News/Social比率、追加Search件数=extra_search_facts非空数と検索回数)、`qcd_comparison.md`(モデル別 total calls/web_search calls/input・output・reasoning tokens/latency/JPY[Terra UNKNOWNはtokensのみ]/1 Topic Packageあたり費用)。
7. 評価script `er016_topic_discovery_eval_01.py --user-eval <path>`: ユーザーの○△×(#→判定)を読み、モデル別に ○率/○+△率/×率/Top10重複/独自候補(他モデルに無いseed)のHit率(○) を算出(今回はdry-runのみ、ダミー入力)。
8. REPORT `TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01_REPORT.md`: §1 Trial条件・対象24時間/§2 共通Prompt全文・schema/§3 各`response.model`実値/§4 各モデル検索件数・query一覧/§5 各モデル最終10件(Topic Package全項目)/§6 ブラインド一覧のパス/§7 News/Social比率・追加Search件数/§8 window compliance/§9 QCD比較表(total calls/tokens/latency/cost/1候補あたりcost)/§10 モデル間重複/§11 評価方法(ユーザー評価後)/§12 Fable参考評価`[Fable記入]`/§13 分類`[Fable記入]`/§14 USER_DECISION_REQUIRED`[Fable記入]`/§15 新Open Item候補(事実列挙。旧Rerank設計「表面的Candidateの後段Rerank単独では品質不足」の知見を含む)/§16 Dangling Reference Check(Production code無変更、`Grep "TOPIC-DISCOVERY" glob="er003_*.py,er012_*.py"`=0件)/§17 Production変更なしの確認。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_3way_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_3way_trial_01 --step estimate --budget-jpy 200
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_3way_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_3way_trial_01 --step run --arm L --budget-jpy 200
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_3way_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_3way_trial_01 --step run --arm S --budget-jpy 200
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_3way_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_3way_trial_01 --step run --arm T --budget-jpy 200
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_3way_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_3way_trial_01 --step verify-window
.venv\Scripts\python.exe er016_topic_discovery_angle_integrated_3way_trial_01.py --out-dir er016_output\topic_discovery_angle_integrated_3way_trial_01 --step assemble
.venv\Scripts\python.exe er016_topic_discovery_eval_01.py --out-dir er016_output\topic_discovery_angle_integrated_3way_trial_01 --user-eval er016_output\topic_discovery_angle_integrated_3way_trial_01\user_eval_DUMMY.json --dry-run
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md --json-out docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし(Open Item候補はREPORT §15に事実列挙のみ)。

## Git
明示add: `er016_topic_discovery_angle_integrated_3way_trial_01.py`、`er016_topic_discovery_eval_01.py`、`er016_output/topic_discovery_angle_integrated_3way_trial_01/`配下、`TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01_REPORT.md`、`USER_EVAL_TOPIC_DISCOVERY_3WAY.md`(root)、`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01.md`、同`_check.json`。
メッセージ: `TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01: 2026-09-18 JSTの24時間を対象に、Search+Angle Discovery+追加検索+Topic Package化+選定を1 callで行う方式をLuna/Terra/Solで比較、重複統合ブラインド評価一覧・QCD比較・評価script作成(Production変更なし)`(STOP時`STOP:`接頭)
trailer: `Management-ID: TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01`

## 報告(RESULT_PACKET_TD)
0. T-0 1. 概算と¥200判定、実行順と各時点の累計 2. 各arm `response.model`実値/検索回数/tokens(input・output・reasoning)/latency/JPY(Terra UNKNOWN明記) 3. 各モデル10件の仮タイトルのみ(RESULT_PACKETには載せてよい。ブラインド一覧には載せない) 4. window compliance(窓内/外/不明件数) 5. News/Social比率、追加Search件数 6. 統合後件数・モデル間重複 7. `USER_EVAL_TOPIC_DISCOVERY_3WAY.md`/`blind_map.json`のパス、評価script dry-run 8. QCD表(1 Package当たり費用) 9. STOP該当有無、`git status --short`、commit SHA、push 10. 一覧外Read/Grep理由、Open Item候補(事実列挙)。

---
【ユーザー指示全文】(delegation_logへそのまま保存)
② TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01
目的: Topic Search/Selectionの基本設計を変更する。従来の「検索→Candidate Pool→別モデルでタイトル/Leadを評価」ではなく、「記事発見→Angle Discovery→必要なら追加検索→Topic Package化→選定」を同一思考ループ内で行う。重要な思想: 記事はゴールではなく、Topic Discoveryのスタート地点。
背景: 前回のRerank 3-wayでは、Luna/Terra/Solの順位相関が非常に高かった/ユーザー実評価ではTop候補も全体的に弱かった/原因として、Candidateを記事タイトル・Leadレベルで評価しており、記事から広げられる面白い切口を考える前に落としていた可能性が高い。今回のユーザーFeedbackでは、例えば、火星: 元ニュース「2031年に火星衛星サンプルを地球へ」だけなら弱い。しかし「月には行けたのに、なぜ火星にはまだ人間が行けない？」「火星有人着陸・火星移住まであと何が足りない？」まで広げると、聞きたいTopicになり得る。5G: 元ニュース「携帯4社が5G設備を共同利用」だけなら弱い。しかし「5G→6Gになると、私たちの生活は何が変わる？」まで広げると可能性がある。
新しい選定単位: Topic Package。各Candidateを単なる記事ではなく、最低限以下で保持する: Source article/Seed、元記事の事実上の核、一般人との接点、そこから自然に生まれる疑問、1〜2段広げられるAngle、必要なら追加検索した事実、最終Topic案、最終仮タイトル、採用/不採用理由。重要: 追加情報を勝手に創作しない。Angleを広げるため追加事実が必要なら、そのCandidateについて追加Searchしてよい。
Search Source: 最低2系統を含める。News lane(Big News/国内/海外/経済/生活/Science/Tech/AI/その他)。Social-signal lane(SNSは事実Sourceではなく Topic Discovery Sensor として使う。例: X等のトレンド/TikTokで話題/SNSで急上昇したニュース/Share ranking/SNS反応をニュース媒体が報じたもの)。SNS起点のTopicを採用する場合、事実確認は信頼できる報道または一次情報で行う。
Angle Discoveryで見ること: モデルに固定スコアを機械加算させる必要はない。思考ガイドとして最低限、Self relevance(多くの一般人が自分事にできるか。例: 仕事/AI/スマホ/お金/住宅ローン/結婚/酒/教育/旅行/健康/日常生活)、Curiosity gap(なぜ？/本当に？/そんなことできる？/意外と逆だった？が自然に立つか)、Expansion potential(その記事から1〜2段広い話へ自然に広げられるか。ただし教育的な一般論へ無理に広げない)、Story potential(英語学習News Audioとして続きを聞きたくなる流れを作れるか)。
ユーザーTeacher Data: 今回までのユーザーFeedbackを直接使う。抽象ルールだけに圧縮しない。特に以下をPositive/Negative例としてモデルに見せる。良かった例: AI開発を遅らせるべきか／欧州反発/Anthropicが実験室/T. rexの体温/日銀金利→住宅ローン・物価・生活/能登地震で滝が770m移動/AIで仕事9割減でも早く帰らない/AIなりすまし面接/米中会談→AIが国家間議題/退職代行会社が続かない理由/日本15歳OECDトップ/詐欺容疑者スマホへの遠隔アクセス/火星サンプル→有人火星・火星移住/AI不正侵入→AI control/DXで逆に負荷増/若者3人に1人結婚意思なし/Trump vs judiciary/日本vsウルグアイもAngle次第。弱かった例: 彼岸花/タンチョウ/5G設備共有そのもの/農家が困る、だけの米価格/一般的な健康ハウツー/芸能人小ネタ/限定スポーツ選手ニュース/普通の混雑・災害続報/教育的すぎる環境話。モデルに「なぜ良い/悪いか」をTeacher Dataから推論させる。
3-way比較: Luna/Terra/Sol。今回こそモデル差を見る。すべて同一条件: 同じ対象24時間/同じSearch範囲/同じTeacher Data/同じPrompt/同じ最終出力件数で実行。
対象期間: 過去の同一24時間を固定して使う。最新ニュースではなく、同じ過去24時間を3モデル共通条件にすること。再現性・公平性を優先。対象日は、今回の手動比較と近い2026-09-18 JSTの24時間を第一候補とする。既に取得済みデータが利用できるなら再利用してよいが、モデルごとにCandidate Poolを固定して渡す方式にはしない。今回は、各モデル自身がSearch+Angle Discovery+SelectionをOne goで行う能力を比較したい。
実行イメージ: 各モデルに、その24時間のNews/Social候補を探索/Seed記事を見る/Angleを1〜2段広げる/必要なら追加検索/Topic Package化/弱いものを落とす/最終10件を選ぶ、まで行わせる。単に100記事集めてから別callでrerank、は禁止。ただしAPI/検索仕様上、内部的に複数tool callになること自体は許容する。
最終出力: 各モデル10件。ユーザーに見せる際は、モデル名を伏せて重複統合したブラインド一覧を作る。各候補には最低限: 仮タイトル/元ニュース/Angle/なぜ一般人が聞きたくなる可能性があるか を表示。モデルのpredicted score等はユーザー評価前に見せない。
ユーザー評価: ユーザーが○/△/×または必要に応じてコメントで判定できる形にする。モデルごとに後から復元できるmappingを保存。評価後、○率/○+△率/×率/Top10重複/独自候補のHit率等を再集計する。今回、過去RerankのPearson/Spearmanは主指標にしなくてよい。
QCD/Cost比較: 今回は品質だけでなく、total calls/web・search calls/input tokens/output tokens/reasoning tokens等取得可能なもの/latency/model cost/1採用Topic Packageあたりの費用 を必ず比較する。品質差が小さいなら安いモデルを評価できる設計にする。
コスト: 今回は従来より思考量・検索量が増えるため、数円単位では止めない。3-way全体の暴走防止上限¥200。想定コストを実行前に概算し、¥200超過見込みなら実行前にSTOPして報告。通常範囲ならそのまま実行する。
旧Rerank Trialの扱い: TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01の結果は削除しない。Teacher 57/fixed Pool/3-way score等は検証履歴として保持。ただし今回のユーザー判断により、「表面的Candidateを後段Rerankする設計」単独では品質不足という知見として扱う。Production採用しない。新方式のTrial結果と混同しないこと。
Status: 今回TRIAL。最大到達VALIDATED。モデル勝者をClaude/Fableだけで決めない。ユーザー評価前にProduction採用しない。
STOP条件: 3モデルで条件が揃わない/Search可能範囲に大きな差がある/過去24時間を再現できない/Teacher Dataの読み込み条件が揃わない/追加仕様が必要/¥200超過見込み/新しいProduction仕様を勝手に決める必要が出た。
最終報告: Trial条件/対象24時間/共通Prompt全文/各model_id/各モデルのSearch件数/各モデル最終10件/重複統合後のブラインド評価一覧/News・Social比率/追加Search件数/total calls/tokens/latency/cost/1候補あたりcost/モデル間重複/Trial status/USER_DECISION_REQUIRED/新たなOpen Item/Dangling Reference Check/Production変更なしの確認。終了後STOP。
PM上の注意: 今回の2件はいずれもTrial。ユーザーが「この方向で良い」と言っているのはTrial実施方針への合意であり、まだProduction正式採用ではない。良好でも最大VALIDATED。APPROVED_FOR_PRODUCTIONへの変更はユーザーがTrial結果を確認して正式採用を判断した後のみ。過去のUSER_DECISION_REQUIREDが新方針でsuperseded/deferredになった場合は整理してよいが、未決の重要事項を黙ってcloseしないこと。
