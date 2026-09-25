# TOPIC-DISCOVERY-ANGLE-INTEGRATED-LUNA-TRIAL-01 REPORT

Trial。到達上限VALIDATED。ユーザー評価前にProduction採用しない。Production実装ではない。

## §1 条件

- 対象24時間: 2026-09-18 00:00〜23:59 JST(前TrialのTOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01と同一)。
- lane: News lane + Social-signal lane(SNSは事実Sourceではなく Topic Discovery Sensor として扱う)。
- Teacher Data: ユーザーFeedback(Positive/Negative逐語19+9件)+ `docs/pm/topic_selection_user_eval_dataset.json`の57件(dataset_r/a/b、score付き)。
- モデル: `gpt-5.6-luna`のみ(Sol/Terraは今回実行しない。ユーザー判断2026-09-25「3-wayは保留、まずLuna単独で方式の品質と実コストを測る」)。
- effort: medium。tools: web_search(`search_context_size: "low"`)。
- 暴走防止ガード: Responses APIのトップレベルパラメータ`max_tool_calls=30`(er003_output配下の既存raw_response.json群で`"max_tool_calls": null`が既定フィールドとして存在することを事前確認済み。設計変更ではなく暴走防止ガード)。実測`web_search_call`件数は8件で、ガード上限には到達しなかった。
- 検索と選定は分離しない(Candidate Poolを渡さない、1つのResponses API callで完結)。1 callは途中停止できない。
- **3-way保留の経緯**: 旧`TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01`はcost_estimate.json算出の結果、internal search 20〜30回想定でSol/Terraが1 call当たりLunaの実測25〜28倍(pricing_snapshot直接比25.0x、実測2件平均27.665x)となり、3シナリオ全て(合計見込み¥2,228.97〜3,337.55)が旧予算上限¥200を大幅超過(委任文に記載の「¥400変更」という事実は本タスクのSSOT・delegation_log上には確認できず、¥200での超過のみ確認)、Luna含めいずれのモデルも実行せずSTOP(API課金0円)。本Trialはユーザー判断によりSol/Terraを保留し、Luna単独(暴走防止上限¥100)で先行実行する。

## §2 Prompt全文・schema

developer/user messageは`er016_topic_discovery_angle_integrated_3way_trial_01.py`の`build_prompt()`をそのままimportして使用(逐語同一、本scriptは3WAY scriptを一切変更していない)。実際に送信したprompt全文は`er016_output/topic_discovery_angle_integrated_luna_trial_01/prompt.json`に保存済み。

- `prompt_sha256` = `91b8206d80c7fdb10bef2096716fd690914c46c59af055c15d47a72228fe9a35`(`er016_output/topic_discovery_angle_integrated_luna_trial_01/prompt.json`および`cost_estimate.json`)。これは旧`TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01`の`cost_estimate.json`の`prompt_sha256`と完全一致しており、Prompt本文が逐語同一であることを機械的に確認した。
- json_schema: `build_schema()`をそのままimportして使用(strict、`topic_packages`/`dropped_candidates`の2キー、各フィールドはer016_topic_discovery_angle_integrated_3way_trial_01.pyの`TOPIC_PACKAGE_SCHEMA`/`DROPPED_CANDIDATE_SCHEMA`と同一定義)。件数固定(exactly 10)はPrompt文言のみで、schemaにminItems/maxItemsは付与していない(3WAY設計を踏襲)。

## §3 `response.model`実値

`gpt-5.6-luna`(要求モデルと一致。`api_meta.json`の`response_model_actual`)。

## §4 検索回数・query一覧

- `response.output`中の`web_search_call`アイテム数(=`web_search_call_count`): **8件**(`api_meta.json`)。
- ただし`search_log.md`ではそのうち2件(4番目・5番目)が`action.query`/`action.queries`のいずれからも値を取得できず`None`表示(3WAY scriptの抽出ロジックをそのまま流用しており、複数query同時実行時などのaction構造差異に対応できていない可能性。既知の限界として記録、本Trialの結果自体には影響しない)。
- 一方、`r3.extract_web_search_usage(response)`(既存モジュール、変更なし)は**20件**のqueryを抽出している(`raw_response.json`の`web_search_usage.queries`)。2つの抽出方法で件数が一致しない(8 vs 20)ことを事実として記録する。query一覧全文は`er016_output/topic_discovery_angle_integrated_luna_trial_01/raw_response.json`の`web_search_usage.queries`、簡易ログは`search_log.md`参照。

## §5 最終件数・Topic Package全項目

- **12件**(Promptでは「exactly 10」を指示したが、schemaにminItems/maxItemsを付けていないため実際には12件返ってきた。事実として記録)。
- 全項目(seed_title/seed_url/seed_source_name/seed_published_jst/seed_lane/core_fact_ja/everyday_connection_ja/natural_question_ja/angle_expansion_ja/extra_search_facts/final_topic_ja/tentative_title_ja/why_listener_wants_more_ja/self_note_ja)は`er016_output/topic_discovery_angle_integrated_luna_trial_01/topic_packages.json`に全件保存。仮タイトルと元ニュース媒体の一覧は`USER_EVAL_TOPIC_DISCOVERY_LUNA.md`(self_note非表示)参照。

## §6 落とした候補

6件。`er016_output/topic_discovery_angle_integrated_luna_trial_01/dropped_candidates.md`。うち2件は「窓外(JST換算で対象日翌日)」を理由に明示的に落とされている(下記§8とも整合)。

## §7 News/Social比率・追加検索件数

`lane_ratio.md`: news=9 / social=3 / extra_search_facts非空=12/12(全件が追加検索事実を含む)。

## §8 window compliance

`window_compliance.json`(12件、HTTP実測、選定には使わない参考情報):
- within_window: 1件
- outside_window: 8件(いずれも米国太平洋時間の記事掲載日をJST換算すると対象日翌日早朝〈JST 2026-09-19 00時台〜08時台〉になっている。モデルは「2026-09-18」という米国日付表記のまま採用したとみられる)
- unreachable: 1件(techcrunch.comへのHTTP接続タイムアウト)
- unverifiable: 2件(いずれもHTTP 403、published_time metaタグ非検出)

**重要な事実**: 12件中1件のみが実測でwindow内に収まっており、Promptの「Target window: 2026-09-18 00:00-23:59 JST」という指示に対し、モデルが実際には米国日付ベースで多くの記事を拾っている可能性が高い。除外はしていない(フラグのみ)が、評価一覧には反映していないため、ユーザー評価時にはこの制約が事実上守られていない点に留意が必要。

## §9 QCD(1 Packageあたりcost含む)

`qcd.md`より:
- web_search_call_count: 8
- input_tokens: 80,825 / output_tokens: 10,588 / reasoning_tokens: 2,107 / total_tokens: 91,413
- elapsed_ms: 133,864.0(約134秒)
- total_jpy: **¥4.62**(実測。`cost.json`、pricing_snapshot.json基準)
- topic_packages_count: 12
- jpy_per_topic_package: **¥0.385**
- schema_retry_occurred: False(空出力・schema不一致による再実行なし)
- 実測は事前概算(low/mid/high = ¥39.57/¥49.41/¥59.25)より大幅に低い(内部web_search_call実測8件は、概算の前提〈内部検索20〜30回〉より少なかったため)。予算¥100は大幅に下回った。

## §10 評価一覧のパス・評価方法

- ユーザー評価一覧: `USER_EVAL_TOPIC_DISCOVERY_LUNA.md`(root、12件、ランダム順、10列: 仮タイトル/元ニュース(媒体・日付・URL)/事実の核/一般人との接点/疑問/Angle/追加検索した事実/評価/コメント。self_note・内部判断は非表示)。
- 対応表: `er016_output/topic_discovery_angle_integrated_luna_trial_01/eval_map.json`(#→topic_packages.jsonのindex)。既存評価script`er016_topic_discovery_eval_01.py`(3WAY用、未変更のロジックに小さな注記追加のみ)をそのまま単一arm(L)で流用できるよう、同形式の`blind_map.json`(arms=["L"]固定)も併せて保存。
- 評価script dry-run: 実データの`blind_map.json`(12件)に対し、動作確認用DUMMY評価(`user_eval_DUMMY.json`、実ユーザー評価ではない)を適用し、集計ロジックが単一arm(L)でも正しく動くことを確認した。○率=0.5、○+△率=0.75、×率=0.25、独自候補Hit率=0.5(いずれもDUMMY値、実際のモデル品質を示すものではない)。S/T armは0件でnull(独自候補Hit率は非該当)。結果は`eval_result_DUMMY.json`(is_dummy_data=trueのため)。
- **er016_topic_discovery_eval_01.pyへの変更点**: `note`欄が「blind_mapが無い(3WAYのSTOP)」場合の文言に固定されていたため、「blind_mapは実データだがuser_evalがDUMMY」という本Trialのケースを正しく表現できるよう、判定・文言のみ追加した(集計ロジック・スコア計算式は無変更)。3WAY側の既存動作(dry-run時のdummy blind_map自動生成)への影響がないことを再実行で確認済み。

## §11 Fable参考評価
### 11.1 方式(Angle Discovery統合)について
- 各Packageの構造(事実の核→一般人との接点→疑問→1〜2段の広げ方→追加検索した事実)は概ね成立しており、追加検索の事実にはURLが付き創作は見られない。Angleの質は、ユーザーの正例(火星→有人火星、5G→6G生活)に近い「記事をスタート地点にして広げる」形になっている(例: #4 AIロボット→権限設計、#9 10分配送→速さに払う消費者心理、#12 失敗公開→信頼の測り方)。
- 費用は¥4.62(1 Packageあたり¥0.39)で、事前概算(¥40〜59)の約1/10。方式のコストは問題にならない。

### 11.2 探索の幅(本Trialの主要な弱点)
- web_search回数は8回のみ(max_tool_calls=30に対し)。入力80,825 tokens、出力10,588、reasoning 2,107。
- 12件すべてが英語圏のTech系媒体(TechCrunch 8、Tom's Hardware、Axios、Google公式、OpenAI公式)で、日本の国内ニュース・経済・生活・科学など指定News laneの大半が未探索。テーマもAI関連が10/12に偏る。
- Social-signal laneは実質未実施(「SNS反応」枠3件も通常の記事)。
- 対象窓: 12件中1件のみが2026-09-18 JST内。8件は米国時間9/18(JSTでは9/19早朝)。モデルは「その日」を米国日付で解釈した。
- 件数は指示「exactly 10」に対し12件(schemaで固定していない)。同一seedの別Angleが2組(#1/#11 Google CC、#5/#6 Tilly Norwood)あり、実質ユニークseedは10件。
- ユーザーの正例(日銀金利・能登・退職代行・15歳OECD等)が示す国内・生活・社会の幅と比べ、今回の出力は明らかに狭い。これは方式そのものよりも、探索量(8検索)と探索対象の指定不足に起因すると見る。

### 11.3 Fable所見(参考、最終はユーザー評価)
Angle化の品質は期待できるが、「何を探すか」の幅が不足したため、方式の本来の力はまだ測れていない。次回は (a) 探索の最低要件(日本語Sourceを含む/指定laneを各1回以上検索/社会的話題の検索を実施)を明示、(b) JST窓の解釈を明示(公開日時をJSTで判定)、(c) schemaで10件固定、(d) 同一seedの重複を禁止、を入れた上で再実行するのが妥当。費用が¥5前後であれば、Sol(単価約25倍→約¥115見込み)を含む3-wayも¥400内に収まる可能性が高い。

## §12 分類
**USER_DECISION_REQUIRED**。Angle Discovery統合の方式自体は機能し費用も低いが、探索の幅(国内・Social lane・JST窓・件数固定)がユーザー指定条件を満たしておらず、この出力だけで方式をVALIDATEDとはしない。ユーザーの12件評価と、探索要件を明示した再実行の要否判断が必要。

## §13 USER_DECISION_REQUIRED
1. 12件の○/△/×評価(`USER_EVAL_TOPIC_DISCOVERY_LUNA.md`)を提出するか、探索の幅が不足しているため評価を省略して再実行へ進むか。
2. 再実行(Luna、概算¥5〜10)を承認するか。変更点: 探索の最低要件(日本語Source・指定laneごとの検索・社会的話題の検索)/JST窓の明示/schemaで10件固定/同一seed重複禁止。Prompt条件が変わるため新Trial IDとする。
3. 実測が安価だったため、再実行時にSol/Terraを同一条件で加える3-way(概算¥150〜250、Terra単価UNKNOWN)を同時に行うか、Luna再実行の結果を見てからにするか。

## §14 Open Item候補(事実列挙)

- window compliance実測で12件中1件のみが対象24時間(JST)内。米国メディア(TechCrunch等)中心の検索になり、米国日付とJST日付のズレをモデルが十分考慮していない可能性がある。
- 最終件数がPromptの「exactly 10」指示に反し12件になった(schemaでminItems/maxItems未設定のため)。
- lane判定(news/social)の精度: 「social」に分類された3件は、いずれも実体はTechCrunchの通常記事(AI女優インタビュー失敗動画・Google CC発表)であり、X/TikTokの実際のトレンドAPIやSNS投稿そのものを検索した形跡はsearch_log.md上では確認できない(query一覧に"X TikTok"等の文言はあるが、実際にSNS投稿自体をsourceとして引用した形跡はなし)。「Social-signal lane」の趣旨(SNSをDiscovery Sensorとして使う)が実際には機能していない可能性がある。
- 検索クエリ抽出方法により件数が一致しない(response.output由来=8 vs r3.extract_web_search_usage由来=20)。診断目的の記録上の不整合であり、Topic Package自体の内容には影響しないが、将来QCD比較の精度に関わる可能性がある。
- 実測費用(¥4.62)が事前概算(¥39.57〜59.25)より大幅に低く、線形回帰による概算式(REF_PROCESS_MARGINAL_JPY_PER_SEARCH等)は本方式(Angle Discovery一体型)には過大評価だった可能性がある。

## §15 Dangling Reference Check・Production変更なし確認

- `Grep "TOPIC-DISCOVERY" glob="er003_*.py,er012_*.py"` = 0件(確認済み、下記コマンド参照)。
- Production正式path(daily runner・er003_*/er012_*等)・SSOT(CURRENT_SPEC.md/DECISION_LOG.md/OPEN_ITEMS.md)は本Trialで一切変更していない。
