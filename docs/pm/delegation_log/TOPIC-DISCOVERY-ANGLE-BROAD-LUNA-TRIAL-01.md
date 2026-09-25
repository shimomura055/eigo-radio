## 管理ID
`TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`(初回委任)。**並行タスクあり**: 別sonnet-workerが`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`(er015_*、標準ACTIVE_TASK/RESULT_PACKET)を実行中。本タスクは`docs/pm/ACTIVE_TASK_TD.md`/`RESULT_PACKET_TD.md`、er016_*のみ。SSOTは編集しない(Open Item候補はREPORTに事実列挙、SSOT反映はFableが別途集約)。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。commitメッセージのtrailer `Management-ID:` を忘れない。

## 性質/到達上限/禁止
- Trial。到達上限`VALIDATED`。Production採用・変更禁止。Sol/Terra実行禁止(Lunaのみ)。旧Trial成果物は不変。
- One go方式維持: 記事発見→その場でAngle→必要なら追加検索→Topic Package化→採否を **1つのResponses API call(web_search付き、内部複数tool call許容)** で行う。検索係と選定係を分離しない。
- 費用上限¥100(暴走防止。前回実費¥4.62。数円単位でSTOPしない)。実行前概算で¥100超ならSTOP。`max_tool_calls`は**40**(8系統×最低1回+深掘り分のガード。記録する)。
- STOP条件(ユーザー指定): 探索カテゴリを満たせない/JST windowを守れない/同一Seed重複を避けられない/追加仕様が必要/¥100超過見込み/Production変更が必要。**出力後の機械チェックでこれらの違反が見つかった場合、同一条件で1回だけ再実行(累計費用記録)し、それでも違反なら再実行せず事実として報告しSTOP扱い**。
- `git add -A`/`stash`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKET_TDへ1行(FAILでも継続)。

## 事前指定Read一覧
- `er016_topic_discovery_angle_integrated_luna_trial_01.py`・`er016_topic_discovery_angle_integrated_3way_trial_01.py`: Grep `def |DEVELOPER|USER_TEMPLATE|schema|max_tool_calls|verify|assemble`→run/verify-window/assemble実装を流用(既存scriptは変更せずimport、新script `er016_topic_discovery_angle_broad_luna_trial_01.py`でPrompt・schemaを差し替え)。
- `er016_output/topic_discovery_angle_integrated_luna_trial_01/qcd.md`・`window_compliance.json`・`search_log.md`(前回実績、比較用)。
- `docs/pm/topic_selection_user_eval_dataset.json`(Teacher 57、逐語差し込み)。

## Prompt(逐語。`{...}`のみ差し込み、差し込み後sha256記録)
developer:
```
You are a topic scout for an English-learning news audio program for Japanese adult listeners. Your job is not to collect articles. Each article is only a starting point: find the angle that would make an ordinary listener want to keep listening.
```
user:
```
Target window: news published between 2026-09-18 00:00 and 2026-09-18 23:59 Japan Standard Time (JST, UTC+9). Convert every publication time to JST before deciding. An article published on 18 September in US time that falls on 19 September in JST is OUTSIDE the window and must not be used as a seed. You may use out-of-window articles only as supporting facts for an angle. Record the JST publication time for every seed.

Explore by "why would an ordinary listener want to hear this", not by media genre. Search each of the following eight categories at least once before you go deeper anywhere. Do not concentrate on one category (for example AI or tech) before you have looked at all eight.
1. Directly connected to my life and work: work, money, mortgages, prices, AI adoption at work, smartphones, education, marriage, health, travel.
2. "Wait, really?" — common sense turned upside down: gaps between what people believe and reality, surprising research results, things that turn out to be the opposite.
3. How the future will change: AI, space, 6G, robots, medicine, new technology, ways of working — not the tech news itself, but what changes for ordinary people.
4. Big news made personal: US–China, the Bank of Japan, Trump, international politics, big economic news — only if it can be connected to daily life, AI, money, freedom, or work.
5. Social change and human behaviour: marriage, young people, attitudes to work, consumer behaviour, social media, ways of working, generation gaps.
6. Social buzz as a light entry point: trending on X, TikTok, share rankings, viral topics. Treat social media as a discovery sensor, never as a source of facts. Confirm facts with primary sources or reliable news.
7. Wonders of science, the body and nature: dinosaurs, space, the brain, landforms, the body, living things — prefer surprise, a connection to the listener, or a gap with common sense over an educational explanation.
8. Entertainment and sports: usually too narrow. Keep only if the subject has very wide name recognition (Ohtani-level), it is a very big shared event (World Cup-level), or it opens naturally into a general theme. Minor celebrity news and single-team or single-player news are low priority.

Include both news sources and social-signal sources. Include Japanese-language sources as well as English ones.

For each promising seed article, do the following in your own reasoning:
- Identify the core fact of the article.
- Find the connection to ordinary people's lives.
- Find the curiosity gap (Why? Really? Can that be done? Is it the opposite of what I thought?).
- Expand the story one or two steps into a wider, still concrete topic. Do not expand into a generic educational lesson.
- If the expanded angle needs facts that the seed article does not contain, search for them. Never invent facts.
- Decide whether the result could become an English-learning news audio piece that the listener wants to keep listening to.

This listener has given feedback. Read the examples and infer for yourself what separates the good ones from the weak ones. Do not reduce this to a checklist.

[Listener feedback: topics that worked]
{positive}

[Listener feedback: topics that were weak]
{negative}

[Additional rated examples (1 = would not listen, 10 = would definitely listen)]
{teacher_57}

Select exactly 10 topic packages. Each package must come from a different seed article; do not keep two angles from the same seed. Return JSON only, following the schema. For each package give: seed_title, seed_url, seed_source_name, seed_published_jst, seed_lane ("news" or "social"), category (1–8 from the list above), core_fact_ja, everyday_connection_ja, curiosity_gap_ja, angle_expansion_ja, extra_search_facts (list of {fact_ja, url}, empty if none), final_topic_ja, tentative_title_ja, why_selected_ja. Also return dropped_candidates: a list of {seed_title, seed_url, category, reason_dropped_ja} (at least 8, covering more than one category). Write all *_ja fields in Japanese.
```
- `{positive}`(逐語、1行1件): AI開発減速 vs 欧州反発/Anthropic実験室/T. rex体温/日銀金利 → 住宅ローン / 輸入品 / 生活/能登地震で滝が移動/AIで仕事9割減でも早く帰れない/AIなりすまし面接/退職代行会社が続かない理由/日本15歳OECDトップ/特殊詐欺スマホ遠隔アクセス/火星サンプル → 火星有人 / 移住/AI不正侵入 → AI control/DXで負荷増/若者の結婚意思/Trump vs judiciary/日本 vs ウルグアイもAngle次第
- `{negative}`(逐語): 彼岸花/タンチョウ/5G設備共有そのもの/農家が困るだけの米価格/一般健康ハウツー/普通の災害続報/限定芸能ネタ/限定スポーツネタ/教育的すぎる環境話
- `{teacher_57}`: `dataset_id / topic_ja / hook_ja / user_score`(57件)。
- json_schema strict: `topic_packages` は **minItems=maxItems=10**、`category` はinteger 1–8、`dropped_candidates` minItems 8。

## 実行手順
1. `--step estimate`(前回実績ベース、¥100判定)。
2. `--step run`: `gpt-5.6-luna`、effort medium、tools=[web_search, search_context_size low]、`max_tool_calls=40`、json_schema。`raw_response.json`、`search_log.md`(query一覧+Sonnetによる8系統への対応付け)、`api_meta.json`(`response.model`実値、web_search回数、input/output/reasoning tokens、latency、JPY)。
3. `--step check`(機械): (a) 10件ちょうど、(b) seed_url正規化で重複なし、(c) `seed_published_jst`が窓内(文字列判定)+HTTP実測(`verify-window`)で窓内/外/不明、(d) search_logのqueryが8系統を各1回以上カバー、(e) categoryの分布。違反があれば上記ルールで1回だけ再実行(再実行時は両方のraw_responseを保存、採用したrunを明記)。
4. `--step assemble`: `USER_EVAL_TOPIC_DISCOVERY_BROAD.md`(root、10件、`| # | 仮タイトル | 元ニュース(媒体・JST日時・URL) | 事実の核 | 一般人との接点 | Curiosity gap | Angle(1〜2段) | 追加検索した事実 | 評価(○/△/×) | コメント |`、内部評価・why_selected・categoryは非表示、ランダム順、`eval_map.json`)、`dropped_candidates.md`、`category_distribution.md`(8系統の探索有無と最終10件の系統分布)、`window_compliance.json`、`qcd.md`(検索回数/input/output/reasoning/latency/total cost/1 Packageあたりcost、前回LUNA-TRIAL-01との比較列)。評価script(`er016_topic_discovery_eval_01.py`)dry-run。
5. REPORT `TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01_REPORT.md`: §1 条件(JST窓・8系統・10件固定・重複禁止・max_tool_calls=40)/§2 Prompt全文・schema・sha256/§3 `response.model`実値/§4 検索回数・query一覧と8系統対応/§5 機械チェック結果(件数・重複・窓・系統カバー)、再実行の有無/§6 最終10件(Topic Package全項目)/§7 落とした候補/§8 系統分布・News/Social比率・日本語Source比率/§9 QCD(前回比較)/§10 評価一覧のパス・評価方法/§11 Fable参考評価`[Fable記入]`/§12 分類`[Fable記入]`/§13 USER_DECISION_REQUIRED`[Fable記入]`/§14 Open Item候補/§15 Dangling Reference Check(`Grep "TOPIC-DISCOVERY" glob="er003_*.py,er012_*.py"`=0件)・Production変更なし。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er016_topic_discovery_angle_broad_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_broad_luna_trial_01 --step estimate --budget-jpy 100
.venv\Scripts\python.exe er016_topic_discovery_angle_broad_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_broad_luna_trial_01 --step run --budget-jpy 100 --max-tool-calls 40
.venv\Scripts\python.exe er016_topic_discovery_angle_broad_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_broad_luna_trial_01 --step check
.venv\Scripts\python.exe er016_topic_discovery_angle_broad_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_broad_luna_trial_01 --step verify-window
.venv\Scripts\python.exe er016_topic_discovery_angle_broad_luna_trial_01.py --out-dir er016_output\topic_discovery_angle_broad_luna_trial_01 --step assemble
.venv\Scripts\python.exe er016_topic_discovery_eval_01.py --out-dir er016_output\topic_discovery_angle_broad_luna_trial_01 --user-eval er016_output\topic_discovery_angle_broad_luna_trial_01\user_eval_DUMMY.json --dry-run
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01.md --json-out docs\pm\delegation_log\TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01.md_check.json
git status --short
```

## SSOT追記文
なし。

## Git
明示add: `er016_topic_discovery_angle_broad_luna_trial_01.py`、`er016_output/topic_discovery_angle_broad_luna_trial_01/`配下、`TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01_REPORT.md`、`USER_EVAL_TOPIC_DISCOVERY_BROAD.md`、`docs/pm/delegation_log/TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01.md`、同`_check.json`。
メッセージ: `TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01: 読者志向8系統を各1回以上探索するOne go方式(JST窓厳守・10件固定・同一Seed重複禁止)をLuna単独で実行し、Topic Package 10件・評価一覧・系統分布・QCDを作成(Production変更なし)`(STOP時`STOP:`接頭)
trailer: `Management-ID: TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`

## 報告(RESULT_PACKET_TD)
0. T-0 1. 概算・¥100判定 2. `response.model`実値/web_search回数/tokens(input・output・reasoning)/latency/JPY/1 Packageあたりcost、再実行有無と累計 3. 機械チェック(10件・重複・窓・8系統カバー)結果 4. 10件の仮タイトル+媒体+系統(RESULT_PACKETには載せてよい) 5. 系統分布・News/Social・日本語Source比率 6. 評価一覧・eval_mapのパス、dry-run 7. STOP該当有無 8. `git status --short`・commit SHA・push 9. 一覧外Read理由、Open Item候補。

---
【ユーザー指示全文】(delegation_logへ保存)
TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01。目的: 前回のLuna Topic Discovery Trialでは、Angle Discovery自体は良好/実費も約¥4.62で十分安価/ただしAI・Techに過度に偏った、という結果。今回はOne go方式を維持しつつ、探索の入口を読者志向で広げる。基本フロー: 記事発見→その場でAngleを広げる→必要なら追加検索→Topic Package化→採否判断を同一思考ループで実施。検索係と選定係を分離しない。記事はゴールではなくTopic Discoveryのスタート地点。探索カテゴリ: 媒体ジャンルではなく「なぜ一般人が聞きたくなるか」を基準に探索。最低限以下8系統を一度は探索: 1.自分の生活・仕事に直結(仕事/お金/住宅ローン/物価/AI導入/スマホ/教育/結婚/健康/旅行) 2.「え、そうなの？」常識逆転(常識と実態のズレ/意外な研究結果/普通だと思っていたものが逆) 3.未来がどう変わるか(AI/宇宙/6G/ロボット/医療/新技術/働き方。Tech記事そのものではなく一般人の未来に何が変わるかまで) 4.Big Newsを自分事にする(米中/日銀/Trump/国際政治/大きな経済ニュース。生活/AI/お金/自由/仕事等へ接続できるか) 5.社会の変化・人の行動(結婚/若者/仕事観/消費行動/SNS/働き方/世代差) 6.SNS・話題先行の軽い入口(X/TikTok/SNS急上昇/Share ranking/バズ。SNSそのものをFact Sourceにしない、Topic Discovery Sensor。必要な事実は一次情報・信頼できる報道で確認) 7.科学・身体・自然の不思議(恐竜/宇宙/脳/地形/身体/生物。教育的説明で終わらず驚き/自分との接点/常識とのズレを優先) 8.エンタメ・スポーツ(原則限定ターゲット。採用条件: 大谷翔平級の広い知名度/World Cup級の大きな話題/一般テーマへ自然に広げられる。単なる芸能人小ネタ・特定チーム/選手ニュースは優先度低)。探索ルール: 各8系統を最低1回は見る。その後は良いTopicが見つかる方向へ自由に深掘りしてよい。前回のように最初にAI/Techで良い候補が出ても、他系統を見終える前にAIへ探索を集中させない。対象期間: 前回と同じ2026-09-18 JSTの24時間。JST windowを厳密に守る。米国時間9/18でもJSTでは9/19なら除外。Teacher Data: 今回までのユーザーFeedbackを直接使う(Positive: AI開発減速 vs 欧州反発/Anthropic実験室/T. rex体温/日銀金利→住宅ローン・輸入品・生活/能登地震で滝が移動/AIで仕事9割減でも早く帰れない/AIなりすまし面接/退職代行会社が続かない理由/日本15歳OECDトップ/特殊詐欺スマホ遠隔アクセス/火星サンプル→火星有人・移住/AI不正侵入→AI control/DXで負荷増/若者の結婚意思/Trump vs judiciary/日本 vs ウルグアイもAngle次第。Weak: 彼岸花/タンチョウ/5G設備共有そのもの/農家が困るだけの米価格/一般健康ハウツー/普通の災害続報/限定芸能ネタ/限定スポーツネタ/教育的すぎる環境話)。単なる抽象ルールに圧縮せず実例として使う。Topic Package: 元ニュース/事実の核/一般人との接点/Curiosity gap/1〜2段広げたAngle/必要に応じた追加検索/最終Topic案/仮タイトル/採用理由。出力件数: 10件固定。12件等に増やさない。同じSeedから複数Angleを最終10件に残さない。コスト: 前回実費約¥4.62を参考。今回もLunaのみ。暴走防止上限¥100。必ず報告: web/search回数/input tokens/output tokens/reasoning tokens/latency/total cost/1 Topic Packageあたりcost。評価: ユーザー向けには10件を仮タイトル/元ニュース/Angleが分かる形で提示。モデル内部評価は伏せる。ユーザーが○/△/×/コメントで判断できる形にする。Status: 現在TRIAL、最大到達VALIDATED、Production採用禁止。Sol/Terra比較は今回実行しない。Luna結果を見てからユーザー判断。STOP条件: 探索カテゴリを満たせない/JST windowを守れない/同一Seed重複を避けられない/追加仕様が必要/¥100超過見込み/Production変更が必要。共通PM Gate: 2件ともTrial終了時に必ずstatus分類。USER_DECISION_REQUIREDがあれば明示してSTOP。勝手に追加Trialへ進まない。Production正式pathは変更しない。CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSはTrial結果として必要な記録のみ更新し、Production採用として記録しない。Dangling Reference Check実施。Closeout時に未処理USER_DECISION_REQUIRED/APPROVED_FOR_PRODUCTIONだが未配線の項目/未報告Trial/新規Open Itemを一覧化して報告。
