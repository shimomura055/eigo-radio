# DAY1_D 予算・量産単価の現状確認(管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 / Day 1 委任_01B)

日付2026-10-14。read-only、JPY0、機構は一切変更せず。区分: [実測]=ファイル/コード確認、[推定]、[未確認]。

## 1. 有料API費用を記録する既存機構

| 機構 | 所在 | 記録単位 | 通貨換算 | 横断集計 |
|---|---|---|---|---|
| Cost Logger `cl.install()` | `er005_cost_logger.py`(SDK monkeypatch: OpenAI Responses/ASR、Gemini、Azure STT) | 1 API call=1 JSONL行。tag=theme/stage/segment、UTC timestamp、provider/model/tokens、response_id | 記録はtoken等の生データ(換算なし) | 下記参照 |
| `raw_usage_log.jsonl` | 各run dir配下。リポジトリ内891ファイル[実測] | run dir単位(管理IDタグなし) | なし | 全ファイルglobで可能だが集計scriptなし |
| 単価表 `pricing_snapshot.json` | `er005_output/cost_baseline_01/` | モデル/meter別USD単価。公式取得日・URL付き | USD。JPY換算は各scriptが`USD_JPY=160`(259ファイルが独自に160を持つ) | 単価参照のみ |
| 集計script(個別) | `compute_topic_cost.py`、`er005_stage7_cost_compute.py`、`er014_output/.../aggregate_usage.py`、`er052_output/open233_kpi_recovery_02_offline_01/agg_production_set_cost_01.py`(Production 1セット、USD_JPY=160) | run/テーマ/管理ID単位。共通scriptではない | 160固定[実測] | run単位のみ |
| cost summary/報告 | `er005_output/cost_baseline_01/cost_summary.json`(旧2テーマのUSD実測、2026-08-17)、`cost_*.json`/`COST_*.md`等237ファイル[実測] | 管理ID/run毎の手書き・script出力。書式不統一 | 混在(USD/JPY) | 不可(書式不統一) |
| 予算ガード | `--budget-jpy`/`assert_budget_ok`。`--budget-jpy`を持つpyファイル205[実測](大半はTrial) | run単位 | 160固定 | 不可 |
| PM報告規則 | PM_GOVERNANCE §15(1記事総コスト、5区分)、§15-8(Production 1生成セット総原価)、§7-6(予算Cap=暴走防止Guardrail、自動STOPでない) | 報告単位 | — | — |

## 2. 並列タスクを跨ぐ費用集計
- **現状は手順化されていない(不可に近い)**。技術的には全`raw_usage_log.jsonl`をglobしtimestamp(UTC)で日次集計し単価表を掛けることは可能だが、次が不足[実測/推定]:
  1. 共通の集計script・管理ID↔run dirの対応表がない。
  2. ログ外の課金: Coffee N01の比較runは「run dir外(未ログ)」として概算記録(COST_03_actual.md)。Trial-16の事例でも`cl.install()`未実行によるusage未記録が発生(PM_GOVERNANCE §15-7)。
  3. 単価未収載の費目(azure/perplexity等)は旧集計でunpriced=0円計上され得た(DECISION_LOG内の事例)。
  4. 失敗callの扱い・web_search手数料の計上漏れ(下記)がscript間で不統一。
- 手動手順(現状): 各run dirの`raw_usage_log.jsonl`+該当scriptでrun単位に集計→手作業で合算。

## 3. 日本時間の日次1,000円上限の強制
- **現状の機構では不可能**[実測]。理由: (a)日次・複数run横断の合算を保持する共有ledgerがない、(b)ガードはrun単位(`--budget-jpy`)で、他runの消費を知らない、(c)ログのtimestampはUTC(JST変換は集計側で可能だが未実装)、(d)Cap運用は「暴走防止Guardrail」でありCap到達のみで自動STOPしないという正式決定(PM_GOVERNANCE §7-6)が既存。日次上限の機械的強制を導入する場合は§7-6との整合(ユーザー決定の追加)が必要。
- 不足するもの(Day 1は変更せず列挙のみ): 全runner共通の事前予約/累計ledger(JST日付キー)、runner起動時の日次残額チェック、ログ外課金(run dir外・未ログ)の排除、単価/換算の一元化、web_search等の計上統一。

## 4. run単位の異常費用・再試行暴走の防止(適用範囲)

| 対象 | `--budget-jpy` | STOP/RUN_LOCK/RESTART_STORM(§26-5) |
|---|---|---|
| Family Z: er026 fiction runner / er062 / er063 | `--approved-budget-jpy`(real必須、0既定。上限定数あり) | **有り**(er026・er062[structure含む]。er063はSTOP参照0[実測]、要確認) |
| Family X: er019 audio/entertainment/pointless runner | 有り(既定150/150/35) | **無し**(STOP_ALL等の参照0[実測]) |
| Family C: er013_family_c_production_runner | 有り(既定10) | 無し |
| er012_e entertainment two-level | 有り(既定300) | 無し |
| er052_open233 e2e/各trial | 有り(既定例98) | 無し |
| er072 Melos 3take | 有り(既定5) | STOP参照あり(1) |
| er077 OOV evidence runner | 有り(既定0=必須指定) | STOP参照あり(2) |
| er053 Family X runtime | grepで`budget`定義なし | 無し |

- §26-4: STOPセンチネルの他Family展開は「必要時に別途判断」で、未展開が現状[実測]。
- 既知ギャップ: OPEN-T-GAP-01で`--budget-jpy`のガードがweb_search課金を計上しなかった(実費19.48円に対しガード表示6.68円)ため、2026-10-08に`compute_cost_jpy_so_far`を修正済みと記録(Status=PRODUCTION_WIRED)。ただし対象は`er012_e...`系/ER-019 cost.json共通化で、全runnerに及ぶかは**未確認**。
- 文書規則のみ(機械的阻止なし)の項目: 有料run前のSTOP確認(§26-2)、再起動回数制限。

## 5. 量産単価70円/記事セットの既存算定方式
- `CURRENT_SPEC.md` 0件、`PM_GOVERNANCE.md` 0件、`PM_BRIEF.md` 0件、`DECISION_LOG.md`の「70円/JPY70/量産単価」ヒット12件は無関係な金額(例: gemini ¥70.85)、`OPEN_ITEMS.md`の4件は「量産単価: 未確定」「量産単価上振れ問題(retryなし約¥32.71→retryあり実測¥55.30/A2)」等の個別記述[実測]。**70円の上限を定義した既存SSOTは見つからなかった=「未定義(Day 2確定事項)」**(ユーザー合意は本Rolloutの基本方針のみ。DECISION_LOG未反映の可能性は未確認)。
- 既存の関連定義: §15-1(1記事一式=B1+A2、総コスト報告)、§15-5(5区分: 今回実測/Trial特有/異常retry・Human Review由来/Standard同期/Batch量産換算)、**§15-8(Production 1生成セット総原価を主指標。Family別の標準表。共通Research/Ledgerを恣意的に50:50配賦しない)**。TTSはStandard同期とBatchの単価差を分けて示す。
- 実測値(列挙): ①Coffee N01 run dir累計 ¥27.78→¥30.01(COST_03_actual.md、`--budget-jpy 62`以内。Standard未完了[運用STOP]を含む途中値で、完成した1セット原価ではない。run dir外の未ログ概算約¥2〜3を別計上)。②旧Family A A2量産単価: retryなし約¥32.71→retryあり実測¥55.30/A2(OPEN-148。Stage2-3全体retry起因)。③DECISION_LOG内の「Production 1生成セット総原価」は¥99.01〜¥840.74の範囲で複数(Family/時期により異なり、今回のCoffee系のStandard+Advanced+Preview+Commentとは別定義の可能性。個別確認は未実施)。④`er005_output/cost_baseline_01/cost_summary.json`は2026-08-17の旧ベースライン(USD: akb48 $4.295、parenting $3.943、うちretry overhead約59%/43%)で現行方式の70円判定には不適。
- Day 2で確定が必要な論点: (1)「記事セット」の範囲(Standard/Advanced/Preview/Comment/KP/音声/ASR検証のどこまで)。(2)共通Research/Ledgerの配賦(§15-8は恣意配賦を禁じるため「セット単位」で70円か)。(3)TTSはStandard同期かBatch換算か(§15-5の4/5)。(4)retry・rewrite・Human Review上振れを含めるか(平均か上限か)。(5)Trial特有コストの分離。(6)ASR検証(OpenAI ASR/Azure STT)の計上。(7)Family別の基準(News/Trend/Discovery/Voices/Fiction)。(8)判定タイミング(run単位か直近N件平均か)と為替(160固定を継続するか)。(9)恒久1〜2円増の検出に必要な測定粒度(現状は書式不統一のため比較困難)。

## 6. 開発コストと量産コストの区別
- **既存記録だけでは機械的に区別できない**。理由: run dirの`raw_usage_log.jsonl`にはTrial/Production/管理IDのタグがなく、stage/theme/segmentタグのみ。区別は報告(§15-5の2「Trial特有コスト」、§15-6)と手作業に依存。Production runnerのrun dirを量産とみなせるが、同じrun dirでの再生成・検証runや比較runは開発コスト混在になり得る。
- 必要になるもの(Day 2以降で検討): run起動時にpurpose(`DEV`/`PROD_UNIT`)と管理IDをログ行へ付与する仕組み(本Dayは設計変更しない)。

## 7. 未確認事項
1. 70円/記事セットのユーザー決定がDECISION_LOG等に既に存在するか(今回のgrepでは確認できず)。2. 日次1,000円の共有予算を既存の何かが参照しているか(参照は見つからず)。3. er063等一部runnerのSTOP/予算ガード詳細。4. T-GAP-01修正の全runnerへの適用範囲。5. 全`raw_usage_log.jsonl`の網羅率(未ログ課金の総量)。6. ¥99〜¥840「1生成セット」各値の対象範囲。7. Claude Code固定月額が従量でないこと(ユーザー申告ベース)。
