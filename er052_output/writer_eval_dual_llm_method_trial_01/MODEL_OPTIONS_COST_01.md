# MODEL_OPTIONS_COST_01: 評価LLM 2系統の候補と費用見積(委任_01、API支出¥0・未実行)

凡例: 【確認】=repo実物で確認 / 【見積】=下記前提による計算値 / 【推測】=未確認の推し量。**費用はすべて見積であり実測ではない。**

## 1. 「異なる2系統」の解釈(提案)
独立性には2段ある。
- 段1(最低条件): 本番Checkerのプロンプト・手順とは別の評価手順であること(本Trialのプロンプトで満たす)。
- 段2(望ましい条件): 評価モデルが、Writer・Checkerの基盤モデルと別の系統であること。【確認】本番のWriter・Fact Check・Support等は全て `gpt-6-luna`(`er006_model_routing_contract_01.py` L45-L51)。したがって `gpt-6-luna` を評価者にすると、Writerと同じ系統の癖(自己好意・同じ見落とし方)を共有しうる【推測】。
- 提案する解釈: 「2系統」=(a)互いに別vendorまたは別世代・別階層のモデルで、(b)少なくとも片方はWriter/Checkerと別系統。両方がOpenAIの場合は段2が弱い。

## 2. 本repoで利用可能なvendor・モデル(事実)
【確認】`.env` にキーが存在するvendor: OPENAI / GEMINI / DEEPSEEK / TAVILY / PERPLEXITY / JEV(用途は別)。ANTHROPIC_API_KEYは存在しない。キー値は読んでいない。
【確認】`er005_output/cost_baseline_01/pricing_snapshot.json` 登録済みのLLM単価(USD/100万token、Standard):
| モデル | input | cached input | output | 備考 |
|---|---|---|---|---|
| openai gpt-6-luna | 0.10 | 0.01 | 0.50 | Production配線済みの基盤モデル |
| openai gpt-5.6-luna | 0.20 | 0.02 | 1.20 | 旧世代 |
| openai gpt-5.6-sol | 5.0 | 0.5 | 30.0 | 上位階層 |
| openai gpt-6-astra | 10.0 | 1.0 | 50.0 | FACTLOCK-ASTRA-E2E-TRIAL-01用にTrial/DEVとして登録(Production採用ではない) |
【確認】gemini: 登録済みはTTSモデル(gemini-2.5-pro-preview-tts, gemini-3.1-flash-tts-preview, gemini-3.8-flash-lite-tts)のみ。**テキストLLM(判定用)の単価は未登録**。テキスト生成での利用実績をrepo内で確認できなかった。
【確認】deepseek: `deepseek-v4-flash` の実呼び出し実績あり(`er005_research_model_ab_01.py`、Chat Completions、base_url=api.deepseek.com)。**単価は `pricing_snapshot.json` に未登録**。`ER-005-RESEARCH-MODEL-AB-01_report.md` L113 に「output $0.66/1M(off-peak)」の記載があるが、2026-08時点の旧記述でありinput単価は記載なし。実行前に最新単価の確認と登録(ユーザー/Fable承認)が必要。
【確認】別vendorとして使えるAPIキーがあるのはDeepSeekとGemini。ただしGeminiは判定用モデル名・単価が未確定、DeepSeekは単価が未確定。**どちらも単価登録なしでは本repoの費用ガードに乗らない**。

## 3. 候補構成
### 構成P1(ユーザー例に最も近い。最安)
- 系統1 = OpenAI `gpt-6-luna`(登録済み単価。ただしWriter/Checker基盤と同系統のため段2は弱い)
- 系統2 = DeepSeek `deepseek-v4-flash`(別vendor、キー・実績あり。単価要登録)
### 構成P2(Writer/Checker基盤と別階層を入れる)
- 系統1 = OpenAI `gpt-6-astra`(登録済み、Trial用。Writerと同vendorだが別階層)
- 系統2 = DeepSeek `deepseek-v4-flash`
- 費用はP1より桁違いに高い。系統1だけで見積¥72〜344/1回(10ケース)。
### 構成P3(API費用ゼロの代替)
- 系統1 = OpenAI(P1またはP2の系統1)
- 系統2 = **Claude subagentを評価者Bとして使う**(Anthropic APIキーが無いため、API直叩きは不可。Claude Code上のsubagent経由のみ)
- 長所: API費用¥0(サブスクリプション枠内【推測】)。Writer/Checker/OpenAI系と完全に別vendorで、段2を最も強く満たす。判定の質は高いと見込める【推測】。
- 短所: (1)隔離: subagentはrepoを読めるツールを持ちうる。ツール無効・1ケース1呼び出し・入力は`eval_items_01.json`の1要素の文字列のみ、と指示しても、過去判定ファイルを自力で探しに行く余地を技術的には塞げない【推測】。(2)再現性: temperature/seed固定ができず、モデルのバージョン固定も保証できない。同じ入力で別結果になりうる。(3)起動はFable側が行う必要がある(Sonnet実行層は子Agentを起動できない)。(4)自己一致の測定(rep2)は可能だが、「同条件の再現」ではなく「再度聞く」になる。(5)Claude/Fable系は本プロジェクトのレビュー側と同系統で、PM判断との独立性は別途考慮が必要【推測】。
### 構成P4(参考)
- Gemini テキストモデル。判定用モデル名・単価が未確定のため、今回は見積対象外。採用するには単価の確認・登録が先。

## 4. 費用見積(10ケース×1repあたり)
前提【見積】: 為替 ¥160/USD(`er006_model_routing_contract_01_cost_recompute.py` L14 のUSD_JPY=160に合わせる)。1呼び出し=入力約1,500token(プロンプト約1,100+1ケース約400、日本語は1文字≈1〜1.5tokenで概算)。出力=可視JSON約120token+推論トークン。**推論トークン量は不明**で、【確認】過去の同型タスク(`er052_output/open243_translation_ng_analysis_01/trial_m123_01/v2/old/TOL_G09_so.json`、gpt-6-luna、入力5,250)で出力3,956(うち推論3,528)。本件は入力が小さいため、出力 低=600 / 高=4,000 token の幅で見積。キャッシュ割引は考慮しない(安全側)。

| モデル | 1呼び出し($) 低〜高 | 10ケース1rep(¥) 低〜高 | 2rep・10ケース(¥) 低〜高 | 備考 |
|---|---|---|---|---|
| gpt-6-luna | 0.00045〜0.00215 | 0.7〜3.4 | 1.4〜6.9 | 登録済み単価 |
| gpt-5.6-luna | 0.00102〜0.00510 | 1.6〜8.2 | 3.3〜16.3 | 登録済み単価 |
| gpt-5.6-sol | 0.0255〜0.1275 | 41〜204 | 82〜408 | 登録済み単価 |
| gpt-6-astra | 0.045〜0.215 | 72〜344 | 144〜688 | 登録済み単価(Trial用) |
| deepseek-v4-flash | 0.0014〜0.0036 | 2.2〜5.8 | 4.4〜11.6 | **単価未登録。input・outputとも$0.66/1Mと仮定した上限寄りの粗い値**【推測】 |
| Claude subagent | API費用0 | 0 | 0 | サブスク枠内。Fable/Sonnetのトークン消費はあるがAPI請求なし【推測】 |
| Gemini(テキスト) | - | - | - | 単価未登録のため見積不可 |

構成別の総額見積(1rep=各系統10件、2rep=各系統20件):
| 構成 | 1rep | 2rep(自己一致あり) |
|---|---|---|
| P1 luna+DeepSeek | ¥2.9〜9.2 | ¥5.8〜18.5 |
| P2 astra+DeepSeek | ¥74〜350 | ¥148〜700 |
| P3 luna(または5.6-luna)+Claude subagent | ¥0.7〜3.4 | ¥1.4〜6.9 |

## 5. 提案(最終判断はFable/ユーザー)
- 最小費用で方式の成否を見るなら P1(2rep)。総額は見積で高く見ても約¥20以内。ただし系統1がWriter/Checkerと同系統である点と、DeepSeek単価の登録が前提。
- 段2の独立性を重視するなら P3(Claude subagentをB)。ただし再現性・隔離の制約を結果解釈に明記する必要がある。
- P2は10ケースの判定に対して費用が大きい(見積¥148〜700/2rep)。まずP1かP3で方式の見込みを見て、必要ならastra追加を別判断にする案を推奨する。
- いずれも `docs/pm/PM_GOVERNANCE.md` の予算Guardrailに従い、実行前にFable/ユーザーの承認を得る。本委任では実行しない。
- 実行前に確認が必要な未確認事項: (1)DeepSeekの最新単価と登録 (2)各モデルのtemperature/seed/reasoning指定の可否 (3)推論トークン量の実測(¥0.1未満の1ケース試し呼び出しで確認可能。ただし実行は別委任)。
