# TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01_REPORT.md

管理ID: `TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01`
到達Status: `VALIDATED`(最終品質判定はユーザー。Production採用なし)
実行日: 2026-09-24
Artifact: `er016_output/topic_selection_reference_process_trial_01/`
Script: `er016_topic_selection_reference_process_trial_01.py`(新規、既存
scriptは一切変更していない)

---

## §1 Search期間・条件

- 対象窓(JST、固定): 2026-09-22 21:05 〜 実行開始時刻(Round1の
  `run_meta.json`作成時に凍結、`2026-09-24T15:39:48+09:00`)。
  Trial-03と同一の窓の考え方(公開日時2026-09-22 21:05 JSTを起点とする
  直近窓)。
- 検証方法: HTTPで記事本文を実取得し、`<meta property="article:
  published_time">`等のメタデータ・JSON-LD・`<time datetime>`から
  実測の公開時刻を取得し、対象窓内かどうかを機械判定(`--step verify`)。
  窓外・取得不能は除外対象。
- model: `gpt-5.6-luna`(全21 call、`response.model`が要求値と一致する
  ことを`call_model`内で強制検証、不一致ならSTOP例外)。
- `search_context_size`: `low`を全20 search callで指定し、**全call受理
  された**(`context_size_accepted=True`、拒否・fallbackは発生せず)。

## §2 初回Query全文(Round1、4本)

- 「今週 ちょっと変わった ニュース 話題」
- 「最近増えている 意外な理由 なぜ」
- 「海外 生活 変化 ちょっと驚いた 出来事」
- 「SNSで話題になった出来事を報じたニュース記事」

## §3 各探索ラウンド(全5ラウンド、要約。全文は`exploration_log.md`)

| Round | Query数 | 主な方向 | raw候補 | 主な棄却理由 |
|---|---|---|---|---|
| 1 | 4 | 広域探索(今週の話題/Everyday Why/海外生活/SNS発記事) | 12(重複除去後) | UGC(note個人投稿)2件、内輪ゴシップ2件、重い論説1件、一覧ページSource2件(数合わせ回避のためdrop) |
| 2 | 4 | Source差替え(NZ鳥/イチロー)+Personal/BigChange方向 | 8 | NZ鳥重複4件統合、イチローSource差替え失敗+センシティブ判断でdrop、大学広報ブログ1件 |
| 3 | 4 | 動物クラスタ回避→職場・消費・文化差・非動物Reversal | 8 | AI/Techクラスタ回避で2件drop、PR調査リリース2件、ad系コンテンツ1件 |
| 4 | 4 | Entertainment/Product/通勤移動/BigChange一文 | 6 | 定型季節ニュース2件、地域限定行政発表1件、PRリリース1件、センシティブ話題1件 |
| 5(最終、call上限到達) | 4 | Rubik's Cube Source差替え+Entertainment+Product+Health | 17 | 重複7件、事故・災害報道2件、低具体性AI統計1件、大学PR・企業コンテンツ2件 |

各ラウンドの「1.現在のPool 2.不足判断 3.次の探索方向 4.実際のQuery
5.新候補 6.棄却理由 7.方向転換」全文は`exploration_log.md`参照。

## §4 方向転換理由一覧

1. Round1→2: NZ鳥・イチローはTopicが強くSourceが弱い(一覧ページ/
   タブロイド)と判断し、Topicを捨てずSource差替え検索へ。
2. Round1→2: Personal Relevance(生活・仕事・消費)がほぼ0件だったため
   追加。
3. Round2→3: 途中レビューで動物クラスタが5件中3件(60%)と判明し、
   動物ネタを避け職場・消費・文化差・非動物Reversalへ転換。
4. Round2→3: SEARCH_DEVELOPERプロンプトに「個別記事permalinkのみ」を
   明記する変更を反映(Round1で一覧ページURLが複数発生したため。
   `ideas_tried.md` Idea1)。
5. Round3→4: AI/Techクラスタ過多を懸念し2件drop、Round4はEntertainment/
   Product/通勤移動へ転換。
6. Round4→5: 「新しいサービスが話題」クエリが0件だったため表現を
   「利用者が急増しているサービス」に変更。通勤・移動が定型ニュースに
   終始したため方向を打ち切り、健康・睡眠へ転換。
7. Round5(最終ラウンド内での判断修正): Round3でAI/Techクラスタ過多を
   懸念しdropしたR3_002について、Round5終了時点で最終Poolを確認すると
   Tech/AI型が実質0件だったため、判断を修正しkeepへ変更(逐次探索の
   `入替`の実例。ただし後述の通りverify stepで別理由により最終的に
   不採用)。

## §5 Candidate Pool推移(round別)

| Round | kept(累計) | dropped(累計) | replaced(累計) | total(累計) |
|---|---|---|---|---|
| 1 | 5 | 7 | 0 | 12 |
| 2 | 5 | 14 | 1 | 20 |
| 3 | 8 | 19 | 1 | 28 |
| 4 | 9 | 24 | 1 | 34 |
| 5(最終) | 13 | 36 | 2 | 51 |

Round5終了時点でPool管理上のkeptは13件。その後`--step verify`(公開
日時のHTTP実測検証)を実施した結果、**13件中4件が対象窓外と判定され
失格**し、最終的な検証済み候補は**9件**となった。

失格4件と理由:
- 保護猫10年目の話(livedoor): 対象窓開始(2026-09-22 21:05 JST)より
  前(2026-09-22 11:40 JST)に公開されていたと実測(`outside_window`)。
- Excel属人化(ITmedia): メタデータ実測で`2026-09-24T08:00:00+00:00`
  (UTC)= 17:00 JST公開と判明し、window_end(15:39 JST)より後(`outside_
  window`)。
- AI営業研修短縮(ITmedia、R3_002。§4-7で一度keepへ判断修正した候補):
  同様に実測`2026-09-24T07:00:00+00:00`UTC=16:00 JST公開でwindow_end
  より後。
- ルービックキューブ世界記録(AFPBB News、R5_001。R4_001からのSource
  差替え後の候補): 実測`2026-09-22T10:25:00+00:00`UTC=19:25 JST公開で
  window_start(21:05 JST)より前(記録樹立自体が窓より前の出来事)。

この4件はいずれも「Sourceが弱い/内容が悪い」ためではなく、**時刻検証
という別の独立したGate**で失格しており、Search call上限(20)に既に
到達していたため代替候補の追加探索はできなかった(詳細§16)。

## §6 Source差替え記録

| 元候補 | 差替え後候補 | 理由 | 結果 |
|---|---|---|---|
| R1_003 NZ鳥チャタムヒタキ(CNN.co.jp一覧ページ`/fringe/`) | R2_001(CNN.co.jp個別記事`/fringe/35252841.html`) | 個別記事URLが検索結果になかったため再検索 | 成功(最終候補に残存) |
| R1_011/R2_006 イチロー女子選抜完封(東スポWEB) | (差替え失敗) | Round2で主要媒体版を再検索したが同一記事(東スポ発)以外が見つからず | 差替え失敗。加えて内容が政治的にセンシティブなためTopic自体をdrop |
| R4_001 ルービックキューブ世界記録(ABC News動画ページ) | R5_001(AFPBB News個別記事) | 動画ページで詳細不確定だったため記事形式Sourceを再検索(7件ヒットからAFPBB Newsを主候補に採用) | Source差替えは成功したが、verify stepで窓外(記録自体が対象窓より前の出来事)のため最終的に不採用 |

## §7 最終候補一覧(9件、全項目)

`final_candidates.json`および`USER_EVAL_REFPROC_20.md`参照。要約:

| # | candidate_id | Topic | Source | round_found | source_replaced_from |
|---|---|---|---|---|---|
| 1 | R1_005 | 秋分の日の昼夜差(約8分) | FNNプライムオンライン | 1 | - |
| 2 | R1_012 | 謎の生き物(タヌキ?)がSNSで話題 | よろず~ニュース | 1 | - |
| 3 | R2_001 | NZ『今年の鳥』チャタムヒタキ回復 | CNN.co.jp | 2 | R1_003(一覧ページから差替え) |
| 4 | R2_008 | J:COM約9時間の通信障害 | J-CASTニュース | 2 | - |
| 5 | R3_003 | 職場断絶(世代間分断) | ITmedia ビジネスオンライン | 3 | - |
| 6 | R3_006 | 訪日客のレンタカー事故増加 | レスポンス | 3 | - |
| 7 | R5_009 | timelesz猪俣容疑者逮捕とメディア対応 | スポニチアネックス | 5 | - |
| 8 | R5_013 | レム睡眠と83疾患リスクの関連 | ニューズウィーク日本版 | 5 | - |
| 9 | R5_016 | 朝の早歩き20分と自律神経 | ライブドアニュース編集部 | 5 | - |

**公開日時検証結果**: 9件全て`window_classification=within_window`
(#3のR2_001のみ`unverifiable`。CNN.co.jpの記事本文取得はできたが機械
判定用のメタデータ形式が取得できなかったため`disqualified=False`扱い
[not_foundでもoutside_windowでもないため]。ただしモデルが報告した
`published_time_as_shown`は`2026-09-22T13:55:00+09:00`で対象窓内)。

**候補数がN=9(目標20件に対し11件不足)の理由**: (1)Pool管理上の品質
判断で51延べ候補中38件を機械/Sonnet判断でdrop(§5)、(2)残る13件の
うち4件が独立した公開日時検証で失格(§5)、(3)Search call上限(20)に
Round5で到達しており追加の代替探索ができなかった。数合わせのための
保持・padding的な入替は行っていない(§16でこの限界を明記)。

## §8 PR・UGC混入状況

- `gate_round{1-5}.json`(機械signalのみ、LLM call不使用)による
  `machine_exclude_recommended`合計: 6/51件(note.com UGC 2件、PR
  signal 4件[うち1件は'prd'文字列の偶然一致でSonnet目視により別理由
  でdrop])。
- Sonnet判断による追加除外(機械signalでは検出されなかったPR/PR的
  コンテンツ): PR TIMESリリース2件、企業自社プレスリリース2件
  (impact-h.co.jp、hokudai.ac.jp)、企業自社メディア1件(わかさ生活)、
  ad系コンテンツハブ1件(NTTドコモlifestyle、`.ad.`サブドメイン)。
  機械signalは`prtimes`等の明示的な語には強いが、企業自社ドメインの
  PR的コンテンツ(大学の研究広報、健康食品会社の自社メディア)は
  検出できず、Sonnetの目視判断が必要だった(§9・§16で詳述)。
- **最終候補9件にPR/UGC混入は0件**(全てニュース媒体の個別記事)。

## §9 5集合比較(Reference/A/B/Trial-03/RefProcess)

`comparison_sets.md`より抜粋(Luna 1 call、¥0.72、対象83件):

| 集合 | n | Everyday | Personal | Reversal | Talkability | HardSocial | Tech | Product | Entertainment | domestic/intl/unclear |
|---|---|---|---|---|---|---|---|---|---|---|
| Reference(R) | 20 | 15.0% | 10.0% | 0.0% | 35.0% | 30.0% | 40.0% | 40.0% | 15.0% | 12/8/0 |
| ChatGPT API-only(A) | 20 | 25.0% | 15.0% | 10.0% | 30.0% | 20.0% | 35.0% | 40.0% | 15.0% | 12/6/2 |
| Luna API(B) | 17 | 29.4% | 11.8% | 0.0% | 11.8% | 5.9% | 23.5% | 76.5% | 5.9% | 15/0/2 |
| Trial-03(T3) | 17 | 23.5% | 52.9% | 0.0% | 17.6% | 35.3% | 29.4% | 17.6% | 17.6% | 15/0/2 |
| RefProcess(今回) | 9 | 11.1% | 11.1% | 33.3% | 11.1% | **77.8%** | 11.1% | 0.0% | 11.1% | 7/2/0 |

観察(評価はFable/ユーザー):
- RefProcessはReversal比率(33.3%)がReference(0.0%)・他集合を大きく
  上回る。NZ鳥・謎の生き物・職場断絶など「予想と違う」型を意識的に
  探索した結果と考えられる。
- **RefProcessのHardSocial比率(77.8%)が突出して高く、他4集合
  (0〜35.3%)と大きく異なる**。これはSonnetが選定時に意図した
  「職場断絶」「通信障害」「訪日客事故」「逮捕報道」等を、分類モデルが
  「硬い社会・政治・国際ニュース」として広めに解釈した可能性がある
  (Sonnetの選定意図は「自分事性の強い身近な社会現象」だったが、
  分類定義上はHardSocialに入ってしまった)。件数が9件と少ないため
  1件のタグ付けが11.1ポイント分動く点にも留意が必要(観察のみ、
  Fable/ユーザー判断を推奨)。
- Product比率が0.0%(Reference40%、Luna API 76.5%)。今回は消費者
  調査・PR発表を意図的に除外し続けた結果、Product型が最終候補に
  残らなかった(§16の限界として記録)。
- 国内/海外比率は7/2/0とReference(12/8/0)よりやや国内偏重(N=9と
  母数が小さいため単純比較は注意)。
- Referenceとの話題重複(Jaccard>=0.3の機械ヒューリスティック): **0件**
  (Referenceを直接検索していないことの傍証)。

## §10 Search回数

- Round別call数: Round1=4、Round2=4、Round3=4、Round4=4、Round5=4、
  **合計20(call上限20に到達)**。
- 内部web_search実行回数(1 API callあたりモデルが自律的に行った検索
  回数): 合計55回、平均2.75回/call(Trial-03実績average 4.07回/call
  より約32%減、§14参照)。

## §11 model実値

- 全21 call(search20+compare1)で`response.model == "gpt-5.6-luna"`を
  `call_model`内で強制検証(不一致ならSTOP例外を送出する設計。今回は
  全call一致し、例外は発生していない)。

## §12 tokens

- input_tokens合計: 569,981 / output_tokens合計: 36,375 /
  合計606,356 tokens(21 call)。
- 1 callあたり平均input: 27,142 tokens、平均output: 1,732 tokens
  (`search_context_size=low`の影響でTrial-03[medium相当]より1 call
  あたりinput tokensが小さくなる傾向。Round1の広域4クエリでは平均
  34,415 tokens/callだったが、Round2以降は平均21,800〜29,400 tokens/
  callで安定)。

## §13 latency

- `raw_usage_log.jsonl`の`elapsed_seconds`より: 21 call合計487.85秒
  (約8.1分)、平均23.23秒/call、最小10.66秒、最大43.54秒。

## §14 cost(round別・合計)

| Round | calls | web_search内部回数 | JPY |
|---|---|---|---|
| 1 | 4 | 13 | 26.70 |
| 2 | 4 | 10 | 20.59 |
| 3 | 4 | 12 | 24.08 |
| 4 | 4 | 9 | 18.21 |
| 5 | 4 | 11 | 22.94 |
| compare(5集合比較、非search) | 1 | 0 | 0.72 |
| **合計** | **21** | **55** | **¥113.22** |

- 予算¥150に対し¥36.78の余裕を残した状態で、**総Search call上限20に
  到達したため探索終了**(予算超過が理由のSTOPではない)。
- Round1終了時点の実測: 4 calls / ¥26.70(1 callあたり¥6.675)、
  20 call換算の見込み総額¥133.5 <= 予算¥150のため継続と判断
  (`cost_projection.json`)。実際の最終per-call平均は¥5.626で、
  Round1時点の見積りよりやや低く着地した。
- Trial-03実績(参考、¥/call、search1のみ14 call・¥112.27、
  平均¥8.02/call、`search_context_size`未指定)と比較すると、
  本Trialは平均¥5.626/callで約30%低い。主因は(a)`search_context_size
  =low`の指定、(b)developer promptで内部web_search回数を「1〜2回」に
  明示的に制限したこと(内部検索回数平均2.75回/call、Trial-03実績
  4.07回/callから約32%減)。

## §15 逐次探索が効いた具体例(Sonnet観察、事実ベース)

1. **途中レビューによる動物クラスタの是正**: Round2終了時点でkept
   5件中3件(60%)が動物ネタに偏っていることに気づき、Round3で明示的に
   動物を避ける方向転換をした結果、Round3以降で動物系候補は0件になり、
   最終9件では動物系2/9(22%)まで低下した。固定Laneのquotaがない
   探索プロセスだからこそ、偏りに気づいた時点で即座に方向転換できた。
2. **Source差替えプロセスの実証**: NZ鳥(R1_003→R2_001)はTopicを維持
   したままSourceだけを差替えることに成功し、最終候補に残った。
   「Topicが良ければSourceだけ再探索する」という委任文の設計が実際に
   機能した実例。
3. **プロンプト調整の即時反映**: Round1で一覧ページURL問題(3/12件)を
   発見した直後にSEARCH_DEVELOPERへ制約を追記し、Round2以降(28件)で
   一覧ページURLの再発は0件だった。固定scriptではなく探索途中で
   プロンプト自体を調整できたことが効果につながった。
4. **判断の事後修正(入替)**: Round3の予防的drop(R3_002)を、Round5で
   最終Poolのクラスタ比率を確認した上で見直しkeepへ変更した(結果は
   verify stepで別理由により不採用だったが、判断プロセス自体は
   委任文が想定する「探索結果を見て判断を更新する」の実例になった)。

## §16 効かなかった点/まだ弱い部分(観察のみ、評価・提案はFable/ユーザー判断)

1. **公開日時検証(verify)による大きな取りこぼし(13→9、-31%)**。
   Trial-03と異なり、本Trialは「reserve(予備)」候補の仕組みを設計
   していなかった(Trial-03はSelection Gateで予備を確保していたが、
   本Trialは逐次探索の性質上、Selection Gateという単一ステップを
   持たない設計にしたため)。Search call上限(20)に到達済みで、
   失格4件の代替を探索する余地がなかった。次回同種のTrialを行う
   場合、後半ラウンドでcall予算の一部を意図的に「予備枠」として
   確保する設計が有効と考えられる(**これはClaude独自の追加提案
   であり、本Trialでは実施していない**)。
2. **window_end凍結タイミングの実務上の影響**: window_endはRound1の
   最初のAPI call時(15:39 JST)に凍結されたが、探索は複数ラウンドに
   わたり実施時間が延びた。Round3で見つかった記事(ITmedia、同日
   16:00〜17:00 JST公開)は、実際には「今日のニュース」の範疇だが、
   window_endを数十分〜1時間超過していたため機械的に失格した。
   Trial-03と同一の設計(window_endをタスク開始時に固定)を踏襲した
   結果であり、script側の不具合ではないが、逐次探索が複数時間帯に
   またがる場合の構造的な制約として記録する。
3. **モデル報告の公開時刻とHTTP実測の乖離が複数件確認された**。
   例: ITmedia記事でモデルが`published_time_as_shown`を「2026-09-24T
   08:00:00+09:00」(JST)と報告したが、実際のページのメタデータは
   UTC基準で「2026-09-24T08:00:00+00:00」(JST 17:00相当)だった
   可能性がある(9時間のズレ)。これはverify stepが存在する理由
   そのもの(モデルの自己申告だけでは信頼できない)を裏付ける実例。
4. **5集合比較でHardSocial比率が想定外に高く出た(§9)**。Sonnetの
   選定意図(自分事性の強い身近な社会現象)と、分類モデルの型判定
   (HardSocial=硬い社会・政治・国際ニュース)にズレがあった可能性が
   あり、原因は本Trialの観察だけでは特定できていない。
5. **Product型が最終候補に0件**。PRリリース・企業自社メディアを一貫
   して除外した結果、消費者トレンド系のTopicが最終候補に残らな
   かった。独立編集のProduct/Phenomenon記事(Reference型のPRODUCT_
   PHENOMENON、PRではない商品・消費者行動記事)を狙って探すラウンドを
   もう1本設けられればProduct比率を上げられた可能性があるが、
   Search call上限のため実施できなかった。
6. **1件(timelesz逮捕報道)がセンシティブ判断のグレーゾーン**。逮捕
   報道自体を含む候補で、Sonnetは「削除対応の速さ」という切り口で
   保持したが、最終採用可否はFable/ユーザー判断が必要(§7・
   USER_EVAL_REFPROC_20.md内に注記済み)。

## §17 Claude独自Idea

`ideas_tried.md`に3件を記録(Round1〜5の枠内で実施、別方式の大型
Trialの並行起票はしていない):
1. 検索結果URLに「個別記事permalinkのみ」を明示指示するプロンプト
   調整(Round1で発見した一覧ページURL問題への対応、追加費用なし)。
2. Source Gateを機械signalのみにしLLM分類callを省略(委任文の設計
   通りだが、スクリプト実装として毎回1 LLM callを使うTrial-03方式を
   採らず、Search callへ予算を優先配分)。
3. Round3の予防的drop(R3_002)をRound5で読み直しkeepへ判断修正
   (最終的にverify stepで不採用となったが、逐次探索の判断更新プロセス
   自体の実例として記録)。

## §18 Fable記入欄(分類・参考評価・USER_DECISION_REQUIRED)

`[Fable記入]`

## §19 Production変更なし

Production Search/Router/Prompt/Writer Prompt/Hook Writerは一切変更
していない。Audio生成・記事生成・Hook生成は実施していない。
CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSへの追記も行っていない(`git
status --short`参照)。既存script(`er016_topic_selection_search_
trial_03.py`、`er016_topic_selection_chatgpt_repro_01.py`含む)は
一切変更していない(import利用のみ)。本Trialは`er016_output/topic_
selection_reference_process_trial_01/`配下の独立したTrial artifact
である。
