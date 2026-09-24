# TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01 REPORT

管理ID: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`
実行日: 2026-09-24(初回)/2026-09-24(修正1回目=再開、`.env`にJEV_API_KEY追加後)
Status: **USER_DECISION_REQUIRED**(再開後もJev arm実施不能によりSTOP継続。
Pool作成までは完了。詳細は§5参照)
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

**未実行**(§5参照のSTOP条件により、Luna/Terra/Sol armは呼び出していない)。
Prompt自体は委任文どおり固定して設計・保存済み(developer/user逐語)。
`response.model`実値は未取得(呼び出しなし)。

## §5 Jev設定・decision schema・接続確認・rate limit状況

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

## §6 各モデルTop20

**未生成**(L/T/S/J全arm未実行のため)。

## §7 全件predicted score表

**未生成**(同上)。

## §8 モデル間一致率

**未計算**(同上)。

## §9 cost・latency

- 開始前概算: Search≤¥30、Reranking主費用(Luna/Terra/Sol各1 call+Jev)を
  想定していたが、Jev STOPによりreranking自体を未実施。
- 実績: pool step(Source Gate Luna分類4 call+contamination判定1 call、
  計6 call、全てgpt-5.6-luna)のみで **¥2.93**(内訳: `cost_estimate.json`)。
- 予算¥150に対し大幅に余裕あり(reranking実行分は今回計上なし)。
- latency: 個別call実測値は`raw_responses/*.json`のusageに記録(集計表は
  未作成、reranking未実施のため優先度低)。

## §10 ブラインド一覧・評価scriptの所在

- ブラインド一覧: `C:\Users\tensh\eigo-radio\USER_EVAL_RERANK_POOL.md`
  (60件、ランダム順、モデルscore・順位・理由は含まない)
- 対応表: `C:\Users\tensh\eigo-radio\er016_output\topic_selection_user_preference_rerank_trial_01\user_eval_id_map.json`
- 評価script: `C:\Users\tensh\eigo-radio\er016_rerank_eval_01.py`
- dry-run結果(ダミーpredicted_score/user_scoreによる動作確認専用、
  Trial評価としては扱わない):
  `er016_output/topic_selection_user_preference_rerank_trial_01/eval_results_DRYRUN.md`
  でPearson/Spearman/Top20・Top10 5点以上率/Recall/Top20内3点以下件数が
  全arm分正しく計算されることを確認済み。

## §11 評価方法(ユーザー評価取得後)

`er016_rerank_eval_01.py --out-dir <dir> --user-scores <id→scoreのjson>`
(dry-runなし)を実行し、各モデル(arms/{L,T,S,J}/predictions.jsonが存在する
場合のみ)についてPearson/Spearman相関、Top20内5点以上率、Top10内5点以上率、
ユーザー7点以上のRecall、Top20内3点以下件数を算出する。ただし本Trialは
Jev arm実施不能によりSTOPしており、現時点でpredictions.jsonは1件も
存在しない(arms/フォルダ自体未作成)。

## §12 Limitation

- Hook生成は今回実施していない。Topic単体で低評価でも、Hookの付け方で
  改善する可能性がある(Teacher Data自体のcaveatにも明記あり: 「score<5→
  当該Topic類型を検索除外、のような機械利用は禁止」「評価対象はTopic+Hook
  の総合」)。本Trialが測っているのは「Hook前のTopic Selectionとして、
  誰がユーザー嗜好を最も理解できるか」の一側面のみ。
- Jev armが実施不能だったため、4-way比較そのものが未完了。

## §13 Fable記入欄

`[Fable記入]`

## §14 Production変更なし

本Trialは`er016_topic_selection_user_preference_rerank_trial_01.py`
(新規)、`er016_rerank_eval_01.py`(新規)、`er016_output/
topic_selection_user_preference_rerank_trial_01/`配下の成果物のみを
生成した。daily runner・er011_*/er014_*等のProduction正式pathは一切
変更していない。既存script(search_trial_03/reference_process_trial_01/
chatgpt_repro_01/chatgpt_repro_01_cont02)もimport/readのみで無変更。
SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)への追記なし。
