# TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01 REPORT

管理ID: `TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01`
実行日: 2026-09-24(初回)/2026-09-24(修正1回目=再開、`.env`にJEV_API_KEY追加後)
/2026-09-24(修正2回目=再開、ユーザー提示のJev公式API仕様で接続実装)
Status: **USER_DECISION_REQUIRED**(修正2回目でJev接続自体には成功したが、
60件一括抽出が429/502で解決せずSTOP。加えてLuna/Terra/Sol rerankの
既存実装・既存Promptがrepo内に一切存在しないことが判明し、これも
Fable/ユーザー判断が必要なスコープ外事項としてSTOP。詳細は§5・§12参照)
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

**未実行、かつ実行不能(スコープ外)**。修正2回目の委任文は「前回設計どおり
`--step rerank --arms L,T,S`」「Luna/Terra/Sol部分は変更しない」と指示して
いるが、`er016_topic_selection_user_preference_rerank_trial_01.py`の
`cmd_rerank`は過去2commit(`ad33fc4e`/`df0140ec`)を含め一貫して
`arms[0]=="J"`のguardのみで、L/T/S用のPrompt文字列・rerank呼び出しロジックは
**一度も実装されたことがない**(機械確認: `git show <commit>:<file> | grep`
でL/T/S関連のPrompt定数・関数が存在しないことを確認)。「変更しない」対象と
なる既存実装が存在しないため、新規にPrompt設計・実装することは本委任で
指示された範囲(Jev client実装)を超える拡大と判断し、`cmd_rerank`は
arms=L/T/Sを検知した時点で明示的なSTOPメッセージを出して終了するよう実装
した(推測でPromptを新規作成することはしていない)。Fable/ユーザーの判断
(誰がL/T/S Promptを設計するか)を仰ぐ。

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

**未生成**(L/T/S/J全arm、`predictions.json`/`top20.json`ともに未生成)。
参考値としてJevのC001〜C005のみ実測済み(`predicted_score_1_10`):
C001=5.0, C002=5.19, C003=3.27, C004=3.88, C005=6.45(`jev_probe_batch5.json`)。
これは5件のみのTop20相当ではなく、60件中の一部の実測に過ぎない。

## §7 全件predicted score表

**未生成**(60件抽出が§5の理由でSTOPしたため)。

## §8 モデル間一致率

**未計算**(同上)。

## §9 cost・latency

- 開始前概算: Search≤¥30、Reranking主費用(Luna/Terra/Sol各1 call+Jev)を
  想定していたが、L/T/Sのスコープ問題とJevの60件抽出STOPによりreranking
  自体を完了できていない。
- OpenAI実績: pool step(Source Gate Luna分類4 call+contamination判定1
  call、計6 call、全てgpt-5.6-luna)のみで **¥2.93**(変更なし、今回追加
  call無し)。
- Jev実績: 合計3回のJev call成功(1件probe+5件probe+N=20 batch_00)+
  複数回の失敗call(429/502、課金対象か不明)。usage/costフィールドが
  応答に一切含まれないため **`jev_cost_status="Jev cost UNKNOWN"`**
  (`cost_estimate.json`)。合計費用は¥2.93(OpenAI分)+Jev分UNKNOWN。
  ¥150予算に対し、判明している範囲では大幅に余裕がある。
- latency実測(成功call): jev-probe 843.3ms、jev-probe-batch5 789.6ms
  (429×2の待機時間[計10秒]は別途)、rerank batch_00(N=20、1回目成功分)は
  429×2待機後success。失敗call(502)は500ms前後で即時応答(Cloudflareの
  ゲートウェイ層で拒否されているため)。

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
- **L/T/S(Luna/Terra/Sol)rerankの既存実装・既存Promptがrepo内に一切
  存在しない**ことが今回判明した。過去2commitとも`cmd_rerank`はJev arm用
  guardのみでL/T/S分岐が未実装であり、「前回設計どおり」という委任文の
  前提が事実と異なっていた。新規にPromptを設計することは本委任(Jev client
  実装)の指示範囲を超えるため実施していない。4-way比較を行うには、まず
  L/T/S用のrerank Prompt設計を別途Fable/ユーザーが決定する必要がある。
- **Jevの60件一括抽出(rerank --arms J)が429/502で完了しなかった**。
  単発・5件は成功したが、10件以上のquestionsをまとめて送るcallが
  Cloudflare層の502または429で繰り返し失敗した(N=20/N=10、計4回の
  独立試行、時間を空けた再試行を含む)。原因はコミュニティサイト側の
  レート制限・処理能力の可能性が高いが、docsに仕様記載が無いため確定
  できない。より小さいbatch(例: N=5、5件probeで実績あり)であれば成功
  する可能性が高いが、60÷5=12 callとなり、本委任のwarn基準
  (残りcall数<=15なら続行)は満たすため次回試行の選択肢になり得る
  (今回は独自判断で追加のbatch size変更試行を続けることはせず、
  USER_DECISION_REQUIREDとして報告する)。
- `www.jevai.org`は自称「community site、not the official product site」
  であることがページ自身の記述から判明した(§5参照)。ユーザー提示の
  接続仕様とdocs記載は完全一致しているため接続自体は継続したが、
  Jev/TypeSafe AI社の"公式"APIとして扱ってよいかはユーザー確認が望ましい
  (Open Item候補)。
- 上記2点(L/T/Sの未実装・Jev大量callの不安定性)により、4-way比較・
  モデル間一致率算出は本セッションでは完了していない。

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
