# TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01 REPORT

管理ID: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`
実行日: 2026-09-24(初回)/2026-09-24(修正1回目=再開、`.env`にJEV_API_KEY追加後)
/2026-09-24(修正2回目=再開、ユーザー提示のJev公式API仕様で接続実装)
/2026-09-24〜25(修正3回目=最終、ユーザー方針変更でJev正式DEFERRED、
Luna/Terra/Sol 3-way rerankを新規実装・実行)
Status: **USER_DECISION_REQUIRED**(修正3回目でLuna/Terra/Sol 3-way rerankを
完了[全60件score取得・欠落なし・予算¥100内]。Jev armは公式access不可のため
DEFERREDのまま。ユーザーが`USER_EVAL_RERANK_POOL.md`へ実評価するまで、
どのモデルが最良かは判断しない。詳細は§4・§6〜§9・§12参照)
Production変更: なし

## §1 Teacher Data確認

SSOT: `docs/pm/topic_selection_user_eval_dataset.json`。機械確認結果は
`er016_output/topic_selection_user_preference_rerank_trial_01/teacher_check.json`。

- dataset_r(Reference): n=20、score欠落0、topic欠落0
- dataset_a(ChatGPT API-only): n=20、score欠落0、topic欠落0
- dataset_b(Luna API): n=17、score欠落0、topic欠落0
- 合計: 57件(委任文の想定どおり)
- topic_ja文字列の完全重複: 0件
- 判定: **完備**(補正不要、STOP条件「Teacher Dataが不完全」には該当しない)

## §2 Candidate Pool

詳細: `pool_pipeline_stats.json` / `gate_result.json` / `contamination_result.json`
(いずれも`er016_output/topic_selection_user_preference_rerank_trial_01/`配下)。

- 由来別raw件数合計: 264件
  - `topic_selection_search_trial_03/pool_final.json`(22件)
  - `topic_selection_reference_process_trial_01/pool.json`(kept 13件+
    drop理由がUGC/PR以外[DUPLICATE/SAME_ASを除く]の復帰候補)
  - `topic_selection_chatgpt_repro_01_cont02/pool_new.json`(97件)
  - `topic_selection_chatgpt_repro_01/candidates_raw.json`(114件)
- URL正規化重複排除後: 235件
- Source Gate:
  - 機械signal(UGCドメイン正規表現/既存source_gate_category/
    is_pr_or_ad)で確定: 除外55件、採用12件
  - 残り168件をLuna 1 call(バッチ4回、40件/batch)で分類
    (NEWS_FEATURE/PRODUCT_PHENOMENON/PR_ADVERTORIAL/AFFILIATE_RANKING/
    SALE_PRICE/UGC_PERSONAL/LISTING_PAGE/UNCLEAR): 除外50件、採用118件
  - Source Gate通過合計: 130件
- 既知評価Topic混入検査(difflib SequenceMatcher、topic_ja/hook_ja双方に対する
  最大類似度):
  - ratio>=0.65(自動除外): 0件
  - ratio 0.5-0.65(境界、Luna 1 callで「同一事象か」判定、6件をbatch判定):
    6件中6件を「同一事象」と判定し除外
  - 混入検査後: 124件
- 目標50件(40-60)に対し124件が超過したため、由来ごとラウンドロビンで
  60件(上限)にトリム
- **最終Candidate Pool: 60件**(追加Searchは不要、`needs_supplemental_search=false`)
- ファイル: `er016_output/topic_selection_user_preference_rerank_trial_01/candidate_pool.json`
- sha256: `fe39660b643f6081...`(全文は`candidate_pool_sha256.json`)

## §3 追加Searchの有無

なし(既存Search成果物のみで目標件数[40-60]に到達したため)。

## §4 Prompt全文・model実値(L/T/S)

修正3回目委任文(`_fix03.md`)は、初回委任文`docs/pm/delegation_log/
TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01.md`「STEP 3 Preference
Prompt」節のdeveloper文・user文・JSON schemaを**逐語で実装せよ**と明示的に
指示しており(§4で述べた過去の「既存実装が無いため新規設計はスコープ外」
というSTOP判断は、この修正3回目委任により解消された)、新規設計ではなく
既存の委任文本文をそのままコード化する作業として実装した。

- developer(L/T/S共通、一字一句同一):
  `You predict how much one specific listener would want to keep listening
  to an English-learning news audio piece about each topic.`
- user(L/T/S完全同一の1本のPromptを共有。地の文は委任文STEP 3を逐語転記し、
  `[Rated examples]`にTeacher Data 57件[dataset_id/topic_ja/hook_ja/
  user_scoreのJSON Lines]、`[Candidates]`にCandidate Pool 60件[id/topic_ja/
  summary_ja/media(=source_name)のJSON Lines]を埋め込んだもの)。全文:
  `er016_output/topic_selection_user_preference_rerank_trial_01/prompts/
  rerank_lts_shared_prompt.json`
- **3モデル入力文字列の完全同一性**: L/T/S各arm `api_meta.json`の
  `prompt_user_sha256`はいずれも
  `490c07d8f1c24a6f3b2a33e574178b1eb042c085728b53903ccdb91d984f7ddb`で一致
  (機械確認済み)。
- JSON schema(strict): `{"preference_summary": string, "predictions":
  [{"id": string, "predicted_score": number, "reason": string}]}`
  (`additionalProperties: false`、`required`全項目指定)
- effort: `medium`(EFFORT_DEFAULT、L/T/S共通)。web_search機能は`call_model()`
  に含めておらず未使用。
- 60件は3モデルとも1 callで収まり、分割は発生しなかった。
- `response.model`実値: L=`gpt-5.6-luna`、T=`gpt-5.6-terra`、S=`gpt-5.6-sol`
  (いずれも`model_requested`と完全一致、`call_model()`内で不一致時は例外を
  投げる設計のため不一致は発生し得ない)。
- 60件すべてにscoreがあるか検証: L/T/Sいずれも初回callで60/60件取得、
  欠落0件(再実行なし、`missing_ids_final=[]`)。
- 詳細api_meta: `arms/{L,T,S}/api_meta.json`(response_id/usage/latency等)。

## §5 Jev設定・decision schema・接続確認・rate limit状況

**修正3回目(2026-09-25)追記**: ユーザー方針変更により、Jev armは正式に
**DEFERRED**となった。理由: TypeSafe公式Jevは現在新規登録不可・公式API
access取得不可であり、非公式Jevサービス(`www.jevai.org`、下記参照)は
比較対象に使用しない(ユーザー決定)。本委任ではJevへの接続・呼び出しは
一切行っていない(`JEV_API_KEY`も読んでいない、`--env-file`未使用)。
既存Jev client実装(`cmd_rerank_jev`/`call_jev`等)は削除せず保持し、
`cmd_rerank`は`--arms`にJが含まれる場合、即座に`DEFERRED`メッセージを
出して終了するようguardを更新した(`JEV_DEFERRED_MSG`)。以下は前回まで
(修正2回目)のJev接続試行の履歴記録であり、Jev arm自体は今回未実施。
詳細: `er016_output/topic_selection_user_preference_rerank_trial_01/
jev_deferred.md`、`OPEN_ITEMS.md` OPEN-178。

### 初回実行時(key不在)
- `JEV_API_KEY`環境変数: **存在しない**(`bool(os.environ.get("JEV_API_KEY"))=False`。
  key本文は当然表示・保存していない)
- 接続確認: **未実施**(key不在のため最小requestを送信できる状態にない)

### 修正1回目=再開時(2026-09-24、ユーザーが`.env`にJEV_API_KEY追加後)
- `JEV_API_KEY`環境変数: **存在する**(`bool(os.environ.get("JEV_API_KEY"))=True`。
  key本文・値は表示・log・report・commitのいずれにも出力していない。
  `.env`は`.gitignore`1行目に登録済みでcommit対象外)
- endpoint/auth方式: `.env`内に`JEV_BASE_URL`/`JEV_ENDPOINT`/`JEV_MODEL`等の
  関連変数は**存在しない**(`.env`内のJEV_始まり変数は`JEV_API_KEY`のみ)。
- Repo内Jev統合: `Grep -i "jev"`でRepo全体を検索した結果、実在するのは
  `docs/pm/topic_selection_user_eval_dataset.json`のdataset_r item_no=15
  (「XのAI界隈で『Jev』という意思決定特化型AIが急速に話題化」という
  **ニューストピックとしての言及**)と、`er016_topic_selection_chatgpt_repro_01.py`の
  `REFERENCE_CONTAMINATION_KEYWORDS`内の同語のみ。実際のJev API client・
  環境変数例・接続仕様メモは一切存在しない。
- 公式ドキュメント調査(前回調査を再確認、今回新たな追加調査は行っていない):
  `jev.ai`はドメインパーキングページ(`<title>Parking Landing</title>`)であり、
  Jev社の公式API(endpoint/認証ヘッダ/request-response schema/料金/
  rate limit)は特定できなかった。
- 接続確認: **試行せず**(委任文の安全条項どおり、endpointが確定できない
  状態で鍵を推測hostへ送る接続試行は行っていない。鍵漏洩リスク回避のため)。
- decision schema: **未定義**(API仕様が特定できないため作成不能)
- rate limit状況: 接続試行なしのため該当なし。
- 結論: keyは存在するがendpoint/auth/schemaが依然不明のため、委任文STOP条件
  「Jevのendpoint/auth/schemaが依然として不明な場合はSTOP」に該当。
  `stop_reason.json`を更新し、STEP 2(cost-estimate)以降・Luna/Terra/Solの
  rerankは実行していない。
- 参照: `jev_probe.json`、`stop_reason.json`
  (`er016_output/topic_selection_user_preference_rerank_trial_01/`配下)

### 修正2回目=再開時(2026-09-24、ユーザーがJev公式API仕様を提示)

- docs調査: `https://www.jevai.org/docs`・`/jev-api`をcurlで取得(鍵不使用)。
  詳細・逐語引用は`jev_api_notes.md`参照。**重要な確認事実**: このサイト
  自身のページ内文言に「A community for Jev model playbooks and shared
  usage — not the official product site.」とあり、**`www.jevai.org`は
  Jev/TypeSafe AI社の公式サイトではなくコミュニティサイトである**ことが
  判明した(Open Item候補として§12・RESULT_PACKETへ記録。ユーザー提示の
  接続仕様[Base URL/Endpoint/Auth/Response形式/32 KiB上限]とdocs記載内容は
  完全一致したため、指示どおり接続試行自体は継続した)。
- rate limit/usage・課金情報: docs本文に記載なし(grep該当なし)。実接続の
  HTTPレスポンスヘッダにも`rate_limit_headers`は一度も含まれなかった
  (空dict、429/502応答時も含め全attemptsで確認)。502応答時のみ
  `Retry-After: 60`ヘッダを確認。
- **1件接続確認(jev-probe)**: 成功。`status_code=200`、`code=0`、
  `elapsed_ms=843.3`。応答schema実測(推測ではなく実測値):
  `data.answers.C001 = {type:"score", score:4.17, confidence:0.16,
  legend:{"0":"Level 1",...,"9":"Level 10"}, probabilities:{...}}`。
  `score`はdocs記載どおり0始まりのprobability-weighted average(0〜9連続値)
  であることを実測確認。`predicted_score_1_10 = score + 1`の線形変換を採用
  (5.17)。鍵混入なし(`key_leak_found_in_response=false`)。
- **5件probe(jev-probe-batch5、C001〜C005)**: 1 call・questions 5問方式を
  採用(理由: docsがquestions複数id可と明記、32 KiB内に収まる、委任のstep4
  『決定論的batch』方針と整合)。初回・2回目は`429`(`Retry-After`ヘッダ
  なし、既定5秒待機)、3回目`200`で成功(`waits_429=2`、`request_body_bytes=
  16061`、`elapsed_ms=789.6`)。usage/cost情報は応答に含まれず
  (`usage_status="Jev cost UNKNOWN"`)。想定残りcall数(N=20時3 call)が
  15以下のため続行方針とした。
- **60件抽出(rerank --arms J)**: **失敗・STOP**。N=20(3 batch、実測最大
  28,094 bytes<32,768 bytes)で開始したが、batch_00は429×2後200で成功する
  ものの直後のbatch_01が即座に`502`(Cloudflare "Bad Gateway"、
  `Retry-After:60`)。同ヘッダに従い60秒超待機後に最初から再試行しても
  batch_00から`502`、batch間隔を8秒→N=10(6 batch、実測最大20,411 bytes)へ
  縮小して再試行しても`429`が2回待機後も解消せず、さらに時間を空けて
  (leak確認・`.gitignore`確認等の実作業を挟んで数分後)再試行しても
  即座に`502`が再発した。single-probe/5-probeが成功する一方、より大きな
  batch(10件以上のquestions一括)が一貫して失敗するパターンを複数回
  (N=20で2回、N=10で2回、計4回の独立した試行)確認した。委任文STOP条件
  「429が解決しない(`Retry-After`に従い最大2回待機、連打禁止)」に該当する
  と判断し、これ以上の連続試行(hammering)は行わずSTOPした。
  `stop_reason.json`(`reason=JEV_RERANK_RATE_LIMITED_OR_UNSTABLE`)参照。
- 結論: Jev接続自体・schema・単発/少数件callは**成功**したが、60件抽出
  (Top20算出に必要な全件scoring)は本セッション内で完了できなかった。
  `arms/J/predictions.json`は生成されていない。
- 参照: `jev_probe.json`/`jev_probe_batch5.json`/`jev_api_notes.md`/
  `jev_decision_schema.md`/`stop_reason.json`/
  `arms/J/raw/batch_00.json`(直近の失敗試行、`er016_output/
  topic_selection_user_preference_rerank_trial_01/`配下)

## §6 各モデルTop20

`arms/{L,T,S}/top20.json`より転記(id / predicted_score、降順)。

**Arm L(Luna)Top20**: C028=8, C002=7, C005=7, C006=7, C009=7, C034=7,
C042=7, C048=7, C049=7, C055=7, C001=6, C013=6, C021=6, C029=6, C032=6,
C046=6, C052=6, C058=6, C010=5, C012=5

**Arm T(Terra)Top20**: C002=7, C005=7, C042=7, C001=6, C006=6, C009=6,
C021=6, C028=6, C029=6, C049=6, C052=6, C055=6, C003=5, C013=5, C018=5,
C032=5, C033=5, C034=5, C046=5, C048=5

**Arm S(Sol)Top20**: C042=7, C001=6, C002=6, C005=6, C009=6, C021=6,
C028=6, C029=6, C048=6, C049=6, C055=6, C003=5, C018=5, C030=5, C034=5,
C052=5, C006=4, C012=4, C013=4, C014=4

Top10は各Top20の先頭10件(`arms/{L,T,S}/top10.json`にも個別保存)。

## §7 全件predicted score表

60件全件×3モデル(L/T/S)のpredicted_score一覧表: `er016_output/
topic_selection_user_preference_rerank_trial_01/predicted_scores_all.md`
(`--step assemble`で生成、`cmd_assemble`)。各arm個別の全件データは
`arms/{L,T,S}/predictions.json`(id/predicted_score/reason)。

## §8 モデル間一致率

`model_agreement.md`より(3ペア、Top20/Top10重複数、全60件Spearman):

| ペア | Top20重複 | Top10重複 | Spearman(n=60) |
|---|---|---|---|
| L vs T | 17/20 | 7/10 | 0.9119 |
| L vs S | 16/20 | 7/10 | 0.8684 |
| T vs S | 17/20 | 9/10 | 0.9063 |

3モデルとも高い相関(Spearman 0.87〜0.91)・高いTop20重複(16〜17/20)を
示しており、L/T/S間でのモデル差は大きくない(ただしこれはモデル自身の
predicted_score同士の一致率であり、ユーザーの実評価との一致とは別。
モデル自身のscoreだけで勝敗を決めない設計、§11参照)。

## §9 cost・latency

- 開始前(本Trial全体の)概算: Search≤¥30、Reranking主費用(Luna/Terra/Sol
  各1 call+Jev)を想定。修正3回目ではJev armはDEFERREDのためL/T/S各1 call
  のみ実施。
- L/T/S実績(`arms/{L,T,S}/api_meta.json`、`response.model`実値は
  `model_requested`と完全一致):
  - L(`gpt-5.6-luna`): input=12,364 / output=2,669 / total=15,033 tokens、
    elapsed=24.453秒、response_id=`resp_086acac1bba50ec1006ab5a28a70fc87d0b7e55ec41bbad081`
  - T(`gpt-5.6-terra`): input=12,364 / output=2,941 / total=15,305 tokens、
    elapsed=34.775秒、response_id=`resp_0975e1a7bbd564cd006ab5a2a2069087d09e70ea5e2acdc7ce`。
    **Terra単価はpricing_snapshot.jsonにUNKNOWN**(`gpt-5.6-terra`の価格行が
    存在しない。過去のcurl調査[`er016_news_hook_model_comparison_01.py`
    `TERRA_PRICE_PROBE_EVIDENCE`]でも複数候補間の不一致により未確定)。
    JPY算出はできず、tokens実測のみ記録。
  - S(`gpt-5.6-sol`): input=12,364 / output=3,190 / total=15,554 tokens、
    elapsed=37.364秒、response_id=`resp_0f9e770a45b38e78006ab5a2c4dde087d0beba04245779f12e`
  - 3 arm入力token数が完全一致(12,364)している点は、§4の
    `prompt_user_sha256`一致(=入力文字列完全同一)と整合する。
- 費用(`cost_estimate.json`、known price modelsのみ合算): Luna実績合計
  ¥3.836352(pool step計6 call+rerank_L 1 call、計7 call)、Terra=1 call
  UNKNOWN_PRICING(合算対象外)、Sol実績合計¥25.2032(rerank_S 1 call)。
  **合計(known models)= ¥29.04**、予算¥100以内(within_budget=true)。
  Jev実績: 本Trialでは新規callなし(`jev_cost_status="Jev cost UNKNOWN"`
  のまま、前回までの履歴分のみ§5参照)。
- **修正3回目で発見・修正した集計バグ**: `cmd_cost_estimate`(旧実装)は
  `raw_usage_log.jsonl`の`model_id`フィールドではなく存在しない`model`
  フィールドを参照していたため、常に`None`→`MODEL_LUNA`へフォールバック
  し、Terra/Sol呼び出しの実績costをLuna単価で誤集計する潜在バグがあった
  (これまでLuna単発callのみで運用されていたため顕在化していなかった)。
  本Trial実行中に発覚し、`e.get("model_id") or e.get("model") or
  MODEL_LUNA`へ修正した上で全costを再計算した(上記数値は修正後の正しい値。
  budget-jpy STOPチェック自体は修正前でも実行時の合計¥100を超えておらず、
  実害[予算超過を見逃す等]は発生していない)。
- latency: L=24.5秒、T=34.8秒、S=37.4秒(いずれも1 callのみ、リトライなし)。

## §10 ブラインド一覧・評価scriptの所在

- ブラインド一覧: `C:\Users\tensh\eigo-radio\USER_EVAL_RERANK_POOL.md`
  (60件、ランダム順、モデルscore・順位・理由は含まない)。**修正3回目でも
  無変更**(commit差分なしをgit diffで確認)。
- 対応表: `C:\Users\tensh\eigo-radio\er016_output\topic_selection_user_preference_rerank_trial_01\user_eval_id_map.json`(無変更)
- 評価script: `C:\Users\tensh\eigo-radio\er016_rerank_eval_01.py`(**無変更**、
  委任文の「再作成禁止・そのまま使用」対象)
- dry-run再実行結果(ダミーuser_score、L/T/Sは今回生成した実predicted_score、
  Jは依然predictions.json未生成のためdummy predicted_scoreで動作確認のみ、
  Trial評価としては扱わない):
  `er016_output/topic_selection_user_preference_rerank_trial_01/eval_results_DRYRUN.md`
  でL/T/S/J全arm分のPearson/Spearman/Top20・Top10 5点以上率/Recall/Top20内
  3点以下件数が正しく計算され、スクリプトが無変更のまま動作することを確認済み。

## §11 評価方法(ユーザー評価取得後)

`er016_rerank_eval_01.py --out-dir <dir> --user-scores <id→scoreのjson>`
(dry-runなし)を実行し、各モデル(arms/{L,T,S,J}/predictions.jsonが存在する
場合のみ)についてPearson/Spearman相関、Top20内5点以上率、Top10内5点以上率、
ユーザー7点以上のRecall、Top20内3点以下件数を算出する。修正3回目時点で
`arms/L`・`arms/T`・`arms/S`のpredictions.jsonは生成済み(§4・§6・§7)。
`arms/J`は§5のとおりJev armがDEFERREDのため生成されていない
(4-way目のJ列は今後access取得時のみ追加可能)。ユーザーが
`USER_EVAL_RERANK_POOL.md`へ実評価するまで、上記コマンドの実評価(dry-run
なし)は実行していない。

## §12 Limitation

- Hook生成は今回実施していない。Topic単体で低評価でも、Hookの付け方で
  改善する可能性がある(Teacher Data自体のcaveatにも明記あり: 「score<5→
  当該Topic類型を検索除外、のような機械利用は禁止」「評価対象はTopic+Hook
  の総合」)。本Trialが測っているのは「Hook前のTopic Selectionとして、
  誰がユーザー嗜好を最も理解できるか」の一側面のみ。
- **モデル自身のpredicted_score同士の一致(§8)だけで勝敗を決めない**。
  L/T/S間のSpearman相関は0.87〜0.91と高いが、これは3モデルが互いに似た
  判断をしていることを示すのみで、実際のユーザー嗜好との一致度(§11、
  ユーザー評価取得後)とは独立した指標である。
- **Jev armはDEFERRED**(§5・OPEN-178)。TypeSafe公式Jevが新規登録不可の
  ため、公式Jevとの比較は今回実施できていない。非公式wrapperを比較対象に
  使わない方針のため、access取得までJevとの比較データは存在しない。
- 60件のCandidate Poolはユーザーの既存Search Trial成果物から構成されて
  おり(§2)、RERANK方式そのものの評価とは別に、Poolの元となったSearch
  品質自体の限界(OPEN-174の広告混入問題等)は本Trialの範囲外。
- §9で記録したとおり、Terra単価はpricing_snapshot.jsonにUNKNOWNのまま
  未確定であり、Terra分のJPYコストは今回もtokens実測のみで確定額を出せて
  いない。

## §13 Fable記入欄

`[Fable記入]`

## §14 Production変更なし

本Trialは`er016_topic_selection_user_preference_rerank_trial_01.py`
(既存Trialスクリプトへの追記。`verify-fixed`step追加、L/T/S rerank実装
`cmd_rerank_lts`追加、`cmd_assemble`をL/T/S 3arm対応へ更新、Jev arm
guardをDEFERRED即終了へ更新、cost集計の`model_id`フィールド参照バグ修正)、
`er016_rerank_eval_01.py`(無変更、再実行のみ)、`er016_output/
topic_selection_user_preference_rerank_trial_01/`配下の成果物のみを
生成・更新した。daily runner・er011_*/er014_*等のProduction正式pathは
一切変更していない。既存script(search_trial_03/reference_process_trial_01/
chatgpt_repro_01/chatgpt_repro_01_cont02)もimport/readのみで無変更。
SSOT追記は`OPEN_ITEMS.md`のみ(OPEN-178: Jev DEFERRED記録、OPEN-179: 旧Trial
USER_DECISION_REQUIRED整理)。`CURRENT_SPEC.md`/`DECISION_LOG.md`は無変更。
