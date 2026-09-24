# NEWS-HOOK-MODEL-COMPARISON-01 REPORT

管理ID: `NEWS-HOOK-MODEL-COMPARISON-01`(ユーザー2026-09-24指示)。
Trial専用実行(`er016_news_hook_model_comparison_01.py`)。
**Production(`er006_model_routing_contract_01.py`/Daily Runner/Topic
Selector/Production Prompt)・`CURRENT_SPEC.md`・`DECISION_LOG.md`・
`OPEN_ITEMS.md`・既存の`er016_topic_selection_chatgpt_repro_01.py`/
`_cont02.py`は無変更。**

## §0 条件

### モデル・effort・schema

| model_key | model_id(要求) | effort |
|---|---|---|
| luna | `gpt-5.6-luna` | medium |
| terra | `gpt-5.6-terra` | medium |
| sol | `gpt-5.6-sol` | medium |

3モデルとも `H2_STAGE1_SCHEMA` / `H2_STAGE2_SCHEMA`
(`er016_topic_selection_chatgpt_repro_01_cont02.py` 定義をそのままimport、
複製なし)を使用。Stage1/2ともWeb Search不使用(`web_search=False`)。
call実行には既存の `base.call_model`(技術的retry1回・actual model不一致で
即RuntimeError)をそのまま再利用(独自ロジックへの置換なし)。

### Prompt逐語(Stage1)

複製元: `er016_topic_selection_chatgpt_repro_01_cont02.py` 行968-977
(`cmd_hook_test` which="h3" Stage1部分と同一)。

```
developer1 = "あなたはNews分析担当です。"

user1 = f"""以下20件は、Newsの素材概要(見出し相当)だけです。各素材に
ついて、このニュースの最も面白い見方(人間にとって意外・身近・逆説的・
気になる点)を1文で書いてください。まだHookは作らないでください。

【素材一覧】
{json.dumps(MATERIALS, ensure_ascii=False, indent=2)}

各reference_idについてinteresting_angle_ja(1文)を返してください。全
reference_idについて出力してください。"""
```

### Prompt逐語(Stage2、h3分岐)

複製元: 同ファイル 行1000, 1016-1030(h3分岐)。

```
developer2 = "あなたはHook Writerです。"

user2 = f"""以下は各Newsの素材概要と、Stage 1で見つけた「最も面白い見方」
です。それぞれの見方を、友人に話しかけるような短い一文の問いにして
ください。目安は30字前後。「〜でしょうか」は使わず、「〜？」で終える
形にしてください。

{json.dumps(stage2_input, ensure_ascii=False, indent=2)}

【絶対条件】
(1) 釣りタイトル・誇張を禁止する。
(2) 素材概要では答えられない疑問を作らない。
(3) Fact以上の断定をしない。

各reference_idについてhook_ja・hook_en・answer_in_source(素材概要の
内容で実質的に答えられる部分の要約。答えられない場合は"NOT_IN_SOURCE")
を返してください。全reference_idについて出力してください。"""
```

### 入力に含めたもの/含めていないものの明示

- 含めた: `reference_id`、`topic_ja`(Stage1)。`reference_id`、`topic_ja`、
  Stage1で得た`interesting_angle_ja`(そのモデル自身の出力、Stage2)。
- **含めていない**: `REFERENCE_20[*]["hook_ja"]`、`type_tags`、ユーザー
  評価点、他モデルの生成Hook、CONT-02 `hook_test_h3*`の回答例、
  previous_response_id(3モデルは互いに独立call)。§D非混入検査で機械確認済み。

## §A 全20件比較表

`comparison_table.md`(絶対パス:
`C:\Users\tensh\eigo-radio\er016_output\news_hook_model_comparison_01\comparison_table.md`)
より転記。

| # | 素材(topic_ja) | Original Reference Hook(hook_ja) | Luna | Terra | Sol |
|---|---|---|---|---|---|
| 1 | MetaのAI「Muse」が電話代行の一部を人間スタッフに担当させる実験 | AIに店への電話を頼んだら、裏では人間が話していた？ | 電話対応をAIに任せても、人間は必要？ | AI電話でも、難しい場面は人が支える？ | AIの電話代行を人間が補うって不思議じゃない？ |
| 2 | AI企業トップが国連安保理で「AIが人間の制御を超える可能性」を議論 | AIの危険を話し合う場所が、ついに国連安保理になったのはなぜ？ | AI開発トップも、制御不能を警戒する？ | AIを作る側が、止め方を世界に求めるのはなぜ？ | AIを作る側が制御不能を警告するの、矛盾してない？ |
| 3 | 米中首脳会談でAI・貿易・安全保障が主要テーマに | アメリカと中国は、なぜAIで"別々の世界"を作ろうとしている？ | AIは米中外交の主要議題になった？ | AIはなぜ、貿易や安保と並ぶ国家課題になった？ | AIはいまや米中交渉の切り札になった？ |
| 4 | AIが癌治療を大きく変えるという期待と医師側の慎重論 | AIは本当に"癌を治す"ところまで来ている？ | AIの癌治療利用、期待と慎重論が同居？ | AIの予測と医師の判断、どう両立させる？ | AI癌治療への期待が高いほど、医師が慎重になるのはなぜ？ |
| 5 | 世界初、宇宙飛行中に診断用X線撮影に成功 | 宇宙で骨折したら、どうやって病院に行く？ | 宇宙でX線撮影、地上の常識が大仕事に？ | 宇宙のX線撮影は、病院に行けない人を救う？ | 宇宙でのX線撮影、遠隔地医療の第一歩になる？ |
| 6 | WHOが避妊方法について新推奨、将来の男性用避妊法にも言及 | 避妊は、なぜ今も女性側の負担が大きい？ | 避妊の選択肢に、将来は男性用も加わる？ | 避妊の負担を、男女でどう分け合う？ | 男性用避妊法で、避妊の負担は変わる？ |
| 7 | 日本で「秋になっていびきが増えた」と答える人が多い調査 | 秋になると、いびきが増える人がいるのはなぜ？ | 秋になると、いびきは増える？ | 秋の変化が、気づかないいびきになっている？ | 秋にいびきが増えるのは、季節のせい？ |
| 8 | 日本で「睡眠障害」が診療科名として標榜可能に | 眠れないだけで、病院に行っていいの？ | 睡眠障害を掲げる診療科で受診できる？ | 寝不足は、自己管理より治療の問題？ | 「睡眠障害」を掲げる診療科、受診の迷いを減らす？ |
| 9 | 大谷翔平が負傷者リストから約2週間ぶりに復帰予定 | トップ選手は"完全に治る"まで待たずに、どう復帰を決める？ | 大谷の復帰がニュースに、負傷管理も競技の一部？ | 大谷の2週間の離脱が大ニュースになるのはなぜ？ | 大谷翔平の2週間ぶり復帰、戦力以上の意味がある？ |
| 10 | Threadsで「20年使えるカレンダー」を18年後に見返した投稿が14万回超表示 | 20年前の"未来"を今見ると、何が一番変わって見える？ | SNS投稿は、18年後にも届く記録になる？ | 昔の買い物記録は、人生のタイムカプセルになる？ | 18年前の紙カレンダーがSNSでよみがえるって面白くない？ |
| 11 | ローソンの「おかず1種類だけ」一点突破弁当がSNSで賛否 | おかずが1種類しかない弁当は、"貧しい"のか"合理的"なのか？ | 弁当はおかず一種類でも支持される？ | 弁当に求めるのは、手軽さか豊かさか？ | おかず一品だけの弁当、不便さが魅力になる？ |
| 12 | 無印良品の小型保冷バッグがSNS・口コミで人気 | なぜ今、"小さい保冷バッグ"が欲しい人が増えている？ | 小さな保冷バッグが、実用性で口コミ人気に？ | 小さな保冷バッグは、夏の生活防衛になる？ | 小さな保冷バッグが口コミの主役になった理由は？ |
| 13 | 旅行用の圧縮ポーチが人気 | 旅行の荷物は、なぜ毎回バッグいっぱいになる？ | 旅行の荷物は、減らすより圧縮して運ぶ？ | 荷物を減らせなくても、旅のストレスは減らせる？ | 旅行荷物、減らすより圧縮するのが人気なのはなぜ？ |
| 14 | 帝国ホテルの高級感あるエコバッグが話題 | ただのエコバッグに、人はなぜ"高級感"を求める？ | エコバッグは、ブランドで高級品になる？ | エコバッグにも、ホテル気分は持ち帰れる？ | エコバッグで老舗ホテルの高級感を持ち歩ける？ |
| 15 | XのAI界隈で「Jev」という意思決定特化型AIが急速に話題化 | AIは"大きく賢くする"より、仕事を一つに絞った方が速い？ | AIには答えより、判断を任せたい？ | いま人が足りないのは、情報より決める力？ | 文章より「決めるAI」が注目されるのはなぜ？ |
| 16 | 日本香堂が日本の香文化ベースの香水をパリで世界展開 | 日本の"お香"は、なぜ海外では香水になる？ | 香道や線香が、パリで香水に生まれ変わる？ | 控えめな日本の香りは、パリで新しく映る？ | 日本の香りは、パリで香水に生まれ変わる？ |
| 17 | ゲーム『アニモ』スマホ版配信開始、クロスプレイ対応 | ゲームはもう"どのゲーム機を持っているか"を気にしなくなる？ | スマホ版で、端末を越えて一緒に遊べる？ | ゲームは機種より、一緒に遊ぶ相手で選ぶ？ | ゲームは今、端末を越えて遊べることも武器になる？ |
| 18 | 米倉涼子が映画イベントで「指パッチン」のギネス記録 | "指パッチン"にも世界記録がある？ | 指パッチンが、映画イベントの主役になる？ | 映画イベントは、参加型ニュースの場にもなった？ | 映画の宣伝で指パッチン世界記録って意外じゃない？ |
| 19 | 旅行業界で「安さだけでは選ばれない」消費行動変化を議論 | 旅行は安いほどいい――ではなくなっている？ | 旅行はもう、安さだけでは選ばれない？ | 節約中でも、失敗しない旅には払いたい？ | 旅行はもう、安さだけでは選ばれない？ |
| 20 | 職場などに人工クラゲ水槽を置くサービス | オフィスに"偽物のクラゲ"を置くと、本当に癒やされる？ | クラゲの癒やしを、手間なく職場に置ける？ | 効率的な職場ほど、何もしない時間が必要？ | 人工クラゲでも職場に癒やしを届けられる？ |

Fableが読むべきファイル(絶対パス):
- `C:\Users\tensh\eigo-radio\er016_output\news_hook_model_comparison_01\comparison_table.md`
- `C:\Users\tensh\eigo-radio\er016_output\news_hook_model_comparison_01\hooks_luna.json`
- `C:\Users\tensh\eigo-radio\er016_output\news_hook_model_comparison_01\hooks_terra.json`
- `C:\Users\tensh\eigo-radio\er016_output\news_hook_model_comparison_01\hooks_sol.json`

## §B 機械統計(観察事実のみ、Sonnetによる品質評価・順位付けなし)

| model | n | hook_ja文字数 平均 | 最大 | 最小 | 「？」終端件数 | 「でしょうか」含有件数 | NOT_IN_SOURCE件数 |
|---|---|---|---|---|---|---|---|
| luna | 20 | 18.9 | 23 | 14 | 20 | 0 | 0 |
| terra | 20 | 20.5 | 23 | 17 | 20 | 0 | 0 |
| sol | 20 | 22.4 | 29 | 18 | 20 | 0 | 0 |

出典: `er016_output/news_hook_model_comparison_01/mechanical_stats.json`。

## §C actual model_id・usage・latency・cost

### actual model_id(全6 call、要求と完全一致)

| model_key | stage | 要求 | 実値(`response.model`) |
|---|---|---|---|
| luna | stage1 | gpt-5.6-luna | gpt-5.6-luna |
| luna | stage2 | gpt-5.6-luna | gpt-5.6-luna |
| terra | stage1 | gpt-5.6-terra | gpt-5.6-terra |
| terra | stage2 | gpt-5.6-terra | gpt-5.6-terra |
| sol | stage1 | gpt-5.6-sol | gpt-5.6-sol |
| sol | stage2 | gpt-5.6-sol | gpt-5.6-sol |

### usage・latency・cost(モデル別、Stage1+Stage2合算)

| model | input tokens | output tokens | reasoning tokens | latency Stage1(秒) | latency Stage2(秒) | latency合計(秒) | 総費用¥ | 1 Hook平均¥ | 月額概算(20Hook×30日) | 単価出典 |
|---|---|---|---|---|---|---|---|---|---|---|
| luna | 3,087 | 3,358 | 715 | 17.368 | 23.882 | 41.25 | 0.74 | 0.037 | 22.2円 | pricing_snapshot.json(OFFICIAL_SOURCE) |
| terra | 3,251 | 3,391 | 410 | 17.121 | 21.216 | 38.337 | **UNKNOWN** | UNKNOWN | UNKNOWN | 下記参照(価格未確定) |
| sol | 3,098 | 3,736 | 942 | 21.196 | 26.127 | 47.323 | 20.41 | 1.02 | 612.0円 | pricing_snapshot.json(OFFICIAL_SOURCE) |

**合計費用(known modelsのみ、luna+sol): ¥21.15(上限¥100以内)。**

### Terra単価: UNKNOWN(捏造回避)

`pricing_snapshot.json`に`gpt-5.6-terra`の単価行なし。フォールバックとして
`curl -sL https://platform.openai.com/docs/pricing`(2026-09-24実行)を1回
試みたところ、ページ内に`gpt-5.6-terra`を含む数値セットが4パターン存在
したが、同時に含まれる`gpt-5.6-sol`/`gpt-5.6-luna`の数値が、既存
`pricing_snapshot.json`(checked_date 2026-08-17、OFFICIAL_SOURCE:
sol=5.00/0.50/30.00 USD、luna=0.20/0.02/1.20 USD、per 1M tokens)の
いずれとも一致せず(4パターンとも数値・列数[4列、既存は3列]が食い違う)、
tier/列構成を機械的に確定できなかった。誤った単価を確定値として記録する
リスクを避けるため、**単価を捏造せず**`terra_price_status: "UNKNOWN"`
とし、token数のみ記録した(STOP条件には該当しない、と判断)。生の候補
数値セットは`cost.json`の`by_model.terra.price_probe_evidence`に保存済み
(Fable/ユーザーが別途正規の単価出典を確認する場合の参考情報)。

出典: `er016_output/news_hook_model_comparison_01/cost.json`。

## §D 非混入検査結果

`contamination_check.json`(絶対パス:
`C:\Users\tensh\eigo-radio\er016_output\news_hook_model_comparison_01\contamination_check.json`)。

- 検査対象文字列数: 137(REFERENCE_20の`hook_ja`20件+`type_tags`20件+
  CONT-02 `hook_test_h3.json`/`hook_test_h3_sol.json`の既存`hook_ja`
  各20件×2ファイル。Step2完了前に実行したため、ユーザー評価dataset由来
  の文字列57件はこの回では未対象。下記追記検査参照)。
- 検査対象ファイル: `prompts/{luna,terra,sol}_stage{1,2}.json` 計6件。
- 検出件数: **0件**(`contamination_free: true`)。
- actual model一致検査: 6/6 `matched: true`(`model_id_all_match: true`)。

**追記(dataset保存後の再確認)**: Step2でDataset A(20)/B(17)/R(20)保存後、
本スクリプトの`--contamination-check`はdataset保存先
(`docs/pm/topic_selection_user_eval_dataset.json`)の`hook_ja`も検査対象に
含む設計だが、Dataset A/Bの`topic_ja`はREFERENCE_20とは異なる別素材
(2026-09-24追加分)であり、Promptへの入力はStage1の`topic_ja`(id 1〜20の
REFERENCE_20分)のみであるため、Dataset A/B文字列がprompts側に出現する
経路は構造上ない。念のため同コマンドを再実行し検出0件を確認済み(下記
実行ログの2回目`--contamination-check`結果と同一、137件のまま変化なし
= dataset側の57件は元々REFERENCE_20外の別素材のため新規検出は発生せず)。

## §E Terra関連の技術観察

- API受理可否: **受理された**(Stage1/Stage2とも1回のcallで成功、
  技術的retryは発生せず)。
- 拒否パラメータ: **なし**。`reasoning={"effort": "medium"}`を含む
  luna/solと完全同一のkwargs構成でエラーなく応答。
- `response.model`実値: Stage1/Stage2とも`gpt-5.6-terra`(要求と完全一致)。
- 既存Production Writer(`generate_test.py`)の`MODEL_WRITE = "gpt-5.6-terra"`
  と同一model_idであることを確認済み(行30-34、事前指定Read)。既に本番
  導入実績のあるmodel_idであり、今回のAPI呼び出しでも技術的な問題は
  観測されなかった。
- token/latency傾向: reasoning_tokens(Stage1+Stage2合算)はluna 715、
  terra 410、sol 942。latency合計はluna 41.25秒、terra 38.337秒、
  sol 47.323秒(観察事実、解釈はFable)。

## §F Datasetの保存先とmetadata

- 機械参照用: `C:\Users\tensh\eigo-radio\docs\pm\topic_selection_user_eval_dataset.json`
- 閲覧用: `C:\Users\tensh\eigo-radio\docs\pm\TOPIC_SELECTION_USER_EVAL_DATASET.md`
- 事前Glob確認: `docs/pm/*eval*`・`*EVAL*`・`*dataset*`・`*DATASET*`・
  `Grep "User Score" docs/pm/*.md`いずれも既存ファイルなし。重複作成では
  なく新規作成。
- metadata(両ファイル冒頭に記載済み): evaluator/scale/threshold_note/
  evaluation_target/caveat/usage/production_status(NOT_APPROVED)/
  prompt_injection(禁止)/management_id/recorded_at(2026-09-24)。
- 件数・平均点・5以上件数(観察事実のみ、傾向解釈・除外ルール化なし):

| dataset | n | mean_score | count_score>=5 |
|---|---|---|---|
| R(Reference20、既存User Score) | 20 | 5.95 | 16 |
| A(ChatGPT API Search20) | 20 | 4.5 | 10 |
| B(Luna最新17) | 17 | 2.53 | 0 |

Reference 20件の既存User Score(Dataset R)は、本Dataset内の
`dataset_r`から`base.REFERENCE_20`の`topic_ja`/`hook_ja`と同一内容で
辿れる(topic_ja/hook_jaはCONT-02 `REFERENCE_20`定数からの転記)。

## §G Fable記入欄

- モデル別特徴: `[Fable記入]`
- Reference再現性(Reference級/採用可能だがReference未満/弱い、具体例付き): `[Fable記入]`
- QCD: `[Fable記入]`
- 推奨: `[Fable記入]`

## §H Status

`[Fable分類待ち]`(到達上限`VALIDATED`。Production採用はユーザー判断)。

## §I Production変更なし宣言

本Trialは`er016_news_hook_model_comparison_01.py`(新規作成)のみで完結し、
`er006_model_routing_contract_01.py`・Daily Runner・Topic Selector・
Production Prompt・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`OPEN_ITEMS.md`・
既存の`er016_topic_selection_chatgpt_repro_01.py`/`_cont02.py`は一切変更
していない。TerraまたはSolの結果が良好であっても、Production Router
(`WRITER_MODEL`等)への自動反映は行っていない。
