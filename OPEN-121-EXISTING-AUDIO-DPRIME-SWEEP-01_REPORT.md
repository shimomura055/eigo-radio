# OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01 完了報告

管理ID: OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01(継続・完了確認)
実行日: 2026-09-07
性質: 読み取り専用の一括点検(ローカル計算のみ、API課金なし、音声再生成・修正は一切行っていない)

## 1. 引き継ぎ時点の状況

前sonnet-workerが残した `er011_output/open121_existing_audio_dprime_sweep_01/` には
`inventory.json`(1654件)と `audit_d_prime_run.log` のみが存在し、ログの最終行は
`run_d_prime: 1518 newly processed, 1518 total ... elapsed 356.3s` だった。

調査の結果、**処理は「中断」ではなく最後まで走っていたが、`item_id` の一意性に
バグがあり、実際には1654件中1518件しかカバーされていなかった**ことが判明した。

原因: `item_id` が `group::level::segment_id` だけで構成されており、同じ
group/levelの下に複数の記事(article)が存在するケース
(例: `er003_output/n3_01` 配下の `hanshin`/`health`/`household` の3記事、
`er012_laneb_trial08` 配下の `p1`/`p3` の2記事など)で `item_id` が衝突していた。
80組の衝突のうち49組は**実際には内容の異なる別音声ファイル**(sha256が異なる)
だったため、`run_d_prime` のresume処理(同一item_idは処理済みとしてskip)が
別ファイルを誤って読み飛ばしていた。

## 2. 実施した修正と再実行

- `er011_open121_existing_audio_dprime_sweep_01.py` の `item_id` 生成式に
  `article_dir` を追加し一意化(`group::article_dir::level::segment_id`)。
  スクリプト内にコメントで経緯を明記。
- 修正前の `inventory.json` / `audit_d_prime_run.log` / `method_d_prime.json` は
  `er011_output/open121_existing_audio_dprime_sweep_01/_pre_fix_backup/` へ退避。
- `build_inventory` を再実行 → 1654件、全item_idが一意であることを確認
  (dup groups = 0)。
- `run_d_prime` をフォアグラウンドで最初から再実行(resume用の古い結果は破棄)
  → **1654件中1654件を新規処理、1654件が最終結果に格納**(所要367.1秒、
  ローカル計算のみ)。
- `classify` を実行し `results/classified_table.json` / `results/summary_stats.json`
  を生成。

Method D'の仕様(スクリプトに実装済みのまま、無変更で適用):
short_run_priority_autocorrelation、スペクトルフレーム(25ms窓/10msホップ)の
コサイン類似度、lag探索範囲0.5〜2.0秒、閾値0.6でrun長を計測。
`FLAG_D_PRIME` は run@0.6 ≥ 0.7秒、`BOUNDARY_WATCH` は 0.5秒 ≤ run@0.6 < 0.7秒。
Method D(参考、spectral_self_similarity)・Method A(n-gram+canonical crosscheck、
faster-whisper使用)は今回のタスク範囲外(前workerもD'のみ実行しており、
faster-whisperの追加負荷を要するため対象外のまま維持)。

## 3. 結果サマリー

- 対象総数: 1654件(narration/配下の実ファイル1651件 + 既知事例検証用3件、
  うち一意音声content(sha256)は1201種類)
- カテゴリ内訳: en_body 520 / en_other_non_body 287 / ja_other 474 /
  keyphrase_en 235 / keyphrase_ja 138
- 主母集団(en_body、known_case_validationを除く517件)における判定:
  - FLAG_D_PRIME: **11件**
  - BOUNDARY_WATCH(0.5〜0.7秒境界域): 110件
  - CLEAN: 396件
- 全カテゴリ込みのFLAG_D_PRIME総数: 61件(en_body 12件[known_case含む]、
  en_other_non_body 26件、ja_other 19件、keyphrase_ja 4件)。
- 詳細一覧: `er011_output/open121_existing_audio_dprime_sweep_01/results/classified_table.json`

## 4. 既知の重複bug3件の検証結果(known_case_validation)

| 既知事例 | 判定 | run@0.6 | lag |
|---|---|---|---|
| Theme 2 A2 Point Two(`point_two_BUGGY_UNFIXED`、冒頭2文まるごと1回逐語反復) | **CLEAN(未検知)** | 0.4秒 | 1.21秒 |
| Theme 2 A2 In One Line(`in_one_line_BEFORE_FIX_buggy`、主節全体1回逐語反復) | **CLEAN(未検知)** | 0.43秒 | — |
| B1 FSP1 false start(冒頭の言い直し "As of Septem, As of September...") | **FLAG_D_PRIME(検知成功)** | 0.75秒 | 0.97秒 |

**重要な発見**: Method D'は3件の既知バグのうち1件(false start)しか検知できず、
逐語反復2件(Point Two/In One Line)は閾値未満(run 0.4〜0.43秒)で見逃した。
これはMethod D'が短いフレーズ反復よりも「発声のやり直し(false start)」型の
検知に強く、文単位の逐語反復検知には感度不足であることを示す既知の限界であり、
今回の一覧結果(FLAG_D_PRIME 11件・BOUNDARY_WATCH 110件)を「これで網羅的」と
解釈してはならない。特にBOUNDARY_WATCH域(0.5〜0.7秒)には、Point Two/In One
Lineと同種の実バグが埋もれている可能性がある。

なお、B1 FSP1 false startは主母集団側でも**同一音声(同一sha256)が
`open112_rerun02`/`open112_trial13`/`open117_trend...trial_02` の3箇所の
`b1b/narration/full_story_part1.wav`として現存し、いずれもFLAG_D_PRIME
(run=0.75秒, lag=0.97秒)として検知された**(既知事例クリップの検知結果と一致)。
これらの音声ファイル自体は今回変更していない。

## 5. 主母集団(en_body)FLAG_D_PRIME 11件の内訳

| item | run@0.6 | lag(秒) | 分類案 |
|---|---|---|---|
| open112_rerun02 b1b::full_story_part1 | 0.75s | 0.97 | 既知bug再現(B1 FSP1 false start、上記参照) |
| open112_trial13 b1b::full_story_part1 | 0.75s | 0.97 | 既知bug再現(同上、同一sha256) |
| open117_trial02_kp b1b::full_story_part1 | 0.75s | 0.97 | 既知bug再現(同上、同一sha256) |
| pool_pilot_01/pool_benches b1b::full_story_part1 | 0.74s | 1.05 | 未知(別音声、要人手確認) |
| pool_pilot_01/pool_n18_notifications b1b::in_one_line | 0.74s | 1.74 | 未知(要人手確認、In One Line系segmentのため要注意) |
| pool_pilot_01/pool_n4_supermarket a2::point_two | 0.79s | 1.84 | 未知(要人手確認、Point Two系segmentのため要注意) |
| pool_pilot_01/pool_n8_airport_line a2::full_story_part1 | 0.70s | 1.04 | 未知(境界ぎりぎり、偽陽性疑いも含め要確認) |
| pool_pilot_01/pool_startups a2::full_story_part1 | 0.73s | 1.03 | 未知(要人手確認) |
| er003_output/n3_01/hanshin b1b::point_one | 0.72s | 1.32 | 未知(要人手確認) |
| er003_output/novel_audio_02/IRAN01 a2_audio::in_one_line | 0.76s | 0.61 | 未知(In One Line系、要注意) |
| er003_output/novel_audio_02/IRAN01 a2_audio::point_two | 0.74s | 1.23 | 未知(Point Two系、要注意) |

「未知」の11件はMethod D'単体の自動検知結果であり、本タスクでは音声を
聴取・再生成していない(一覧化のみのLane A作業、承認範囲外の音声変更は
行っていない)。人手レビュー・Method A/D併用等の追加確認はOPEN-121の
別サブタスクでの判断を要する(`USER_DECISION_REQUIRED`扱い)。

## 6. 証跡パス

- スクリプト(item_id一意化fix適用済み):
  file:///C:/Users/tensh/eigo-radio/er011_open121_existing_audio_dprime_sweep_01.py
- 修正後inventory: file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/inventory.json
- 実行ログ: file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/audit_d_prime_run.log
- Method D'生結果(1654件): file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/results/method_d_prime.json
- 分類済み一覧(flags/judgement付き、1654行): file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/results/classified_table.json
- 集計サマリー: file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/results/summary_stats.json
- 修正前バックアップ(item_id衝突ありの旧inventory/旧結果、参考保存):
  file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/_pre_fix_backup/

## 7. 未実施(範囲外)

- Method D(spectral_self_similarity、参考)・Method A(n-gram+canonical、
  faster-whisper)は今回のタスク範囲外のため未実行(`run_d`/`run_method_a`は
  0件のまま)。
- 疑いのある区間の音声クリップ切り出し(`build_clips_and_player`)は未実行
  (テキストベースの一覧化のみで報告要件を満たすため、追加のローカル処理を
  今回は見送った)。必要であれば別サブタスクで実行可能。
- 音声の再生成・修正・Production反映は一切行っていない。
