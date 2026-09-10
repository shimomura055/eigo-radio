# TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01 調査報告

読み取り専用分析(¥0、API呼び出し・TTS/ASR/LLM呼び出しなし、SSOT・docs/pm/・
Production Prompt/コード編集なし、Git操作なし)。先行2調査
(`TTS-RETRY-TIMING-OBSERVATION-MONITOR-01_REPORT.md`、
`TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md`)は「attempt番号
そのものが進むと通るか」を検証し「時間依存性なし〜判断材料不足」と結論した。
本調査はユーザーが2026-09-11に再定義した論点、すなわち**「連続NG後、時間を
空けたretryの方が、即時retryよりPASS率が高いか」(cool-down仮説)**を、
自然発生retryのみ(人工的なTTS生成なし)を対象に集計した。

## サマリー(5行、新規/再掲/未確定を明示)

1. **【新規】** cool-down仮説専用の集計script `er011_tts_retry_cooldown_monitor_01.py`
   を新規作成し、既存observations(443 attempt記録、339 segment系列)から
   NG直後の「次tryまでの間隔×次tryの結果」ペアを56件抽出した(種別B品質NG=53件、
   種別A infra疑い参考値=3件)。
2. **【新規】** 即時bucket(<150秒、同一run内自動retry相当、N=46)のPASS率は
   54.35%、非即時bucket(150秒以上、短時間+中+長を統合、N=7)のPASS率は
   71.43%。差は+17.1ポイントで非即時側が高いが、**両側Fisher正確検定の参考p値
   は0.6851**であり、統計的に意味のある差とは言えない(件数が極端に小さいため)。
3. **【新規・最重要の交絡発見】** 非即時7件のうち5件(71%)が、Human Review Lock
   解除後の`manual_regenerate_beyond_loop_cap`経路、または個別監査で判明した
   「機械的にはautomatic判定だが実際は別名management_idで明示的に再実行された
   deliberate regen」(point_two_heading、8357秒=2時間19分)であり、**「手動介入
   を伴わない自然発生の長間隔retry」は7件中わずか2件**(meaning_4@172秒NG、
   point_two@377秒PASS)しかない。長間隔サンプルのほとんどは「時間が経過した」
   だけでなく「人間またはHuman Review Lock解除フローが介入した」サンプルであり、
   時間経過そのものの効果と介入効果を現状のデータからは分離できない。
4. **【再掲、先行調査の結論を覆す材料なし】** 先行2調査の「attempt番号依存性
   なし」「時間依存性なし〜判断材料不足」という結論は、本調査でも覆っていない。
5. **【未確定/継続】** 事前定義した「傾向が十分出た」基準(3節参照)は**現時点で
   未達**(4bucket中最小N=1、基準N≥20に遠く及ばない)。cool-down仕様の
   Production採用判断はできる段階ではない。継続モニタリング手順を6節に提示。

## 1. 抽出方法と間隔bucket定義(データ分布に基づく境界、根拠付き)

- 入力: `er011_output/tts_retry_timing_monitor_01/observations.jsonl`
  (443 attempt記録、`is_retry_after_ng=true`かつ`gap_seconds_since_prev_
  attempt_in_group`が既知の行のみ抽出)。同一segment(同一`level_dir`+
  `segment_id`、フォルダ実体でグルーピング=別runの誤結合を防止)の連続NG列
  から、NGの直後tryの間隔と結果のペアを構成。
- 実測分布(2026-09-11時点、56件)を確認したところ、94秒と172秒の間、
  567秒と2350秒の間、8357秒と51635秒の間に、データ点が存在しない自然な
  間隙(それぞれ約1.8倍・4倍・6倍)がある。この間隙のどこに閾値を置いても
  分類結果は変わらないため、以下の4区分を採用した:
  - **即時 <150秒**(同一run内の自動retryループ相当。実測最大値94秒〜97秒圏に
    次の間隙があるため150秒で区切っても分類は変わらない)
  - **短時間 150秒〜30分(1800秒)**
  - **中 30分〜6時間(21600秒)**
  - **長 6時間以上(別日相当)**
- 種別分類(A=infra疑い/B=品質NG)は先行scriptと同じロジックを流用(文字列
  シグナル検索、限界は先行REPORTの通り)。

## 2. 集計表

出典: `er011_output/tts_retry_cooldown_analysis_01/summary.md`(自動生成)。

### 表1: 種別B(品質NG)— 間隔bucketのみ

| bucket | N | PASS | PASS率 |
|---|---|---|---|
| 即時<150秒 | 46 | 25 | 54.35% |
| 短時間150秒〜30分 | 4 | 3 | 75.0% |
| 中30分〜6時間 | 2 | 1 | 50.0% |
| 長6時間以上 | 1 | 1 | 100.0%(N=1) |

### 表2: 種別B — 連続NG回数×間隔bucket(交絡層別)

| 連続NG回数 | bucket | N | PASS | PASS率 |
|---|---|---|---|---|
| 1 | 即時<150秒 | 34 | 23 | 67.65% |
| 1 | 短時間 | 2 | 1 | 50.0% |
| 1 | 中 | 1 | 1 | 100.0%(N=1、point_two_heading、介入補正あり=表3参照) |
| 2 | 即時<150秒 | 10 | 2 | 20.0% |
| 3以上 | 即時<150秒 | 2 | 0 | 0.0% |
| 3以上 | 短時間 | 2 | 2 | 100.0%(N=2) |
| 3以上 | 中 | 1 | 0 | 0.0%(kp5_ja_charon、39.2分、失敗) |
| 3以上 | 長 | 1 | 1 | 100.0%(N=1、CAR-T、既知事例) |

### 表3: generation_path×手動介入補正×間隔bucket

| generation_path(機械判定) | 介入補正 | bucket | N | PASS率 |
|---|---|---|---|---|
| automatic_retry_within_loop_cap | なし | 即時 | 39 | 53.85% |
| automatic_retry_within_loop_cap | なし | 短時間 | 2 | 50.0% |
| automatic_retry_within_loop_cap | **あり(deliberate override)** | 中 | 1 | 100.0%(N=1) |
| manual_regenerate_beyond_loop_cap | なし | 即時 | 7 | 57.14% |
| manual_regenerate_beyond_loop_cap | なし | 短時間 | 2 | 100.0%(N=2) |
| manual_regenerate_beyond_loop_cap | なし | 中 | 1 | 0.0%(N=1) |
| manual_regenerate_beyond_loop_cap | なし | 長 | 1 | 100.0%(N=1) |

## 3. 交絡の扱い(本調査の中心的な新規発見)

### 3-1. per-attempt入力テキストのbyte同一性は直接検証不能(既知の限界、再掲)

先行2調査で指摘済みの通り、各attemptで実際にTTS APIへ渡した"text"引数は
per-attempt JSONに保存されていない(`missing_fields`に常時
`per_attempt_final_tts_input_text`として明示)。`canonical_text_final_state_
sha256`はsegmentの最終状態を表す値で、同一グループ内の全attemptに対して
1回だけ取得されるため、**attempt間でのテキスト変化を検出する材料にはならない
(構造的にできない)**。この限界は今回も解消しておらず、テキストhash完全一致
による機械的な同一条件フィルタリングは実施できなかった(データ不足による
制約であり、実施しなかったのではなく実施できなかった)。

### 3-2. 代理指標としての`generation_path`と、個別監査で判明した取りこぼし

上記の限界の代替として、`generation_path`フィールド(`attempt_number >
max_attempts`かどうかの機械判定)を「自動retry内か、Human Review Lock解除後の
手動再生成か」の代理指標として使用した。ただし本調査で**非即時7件全件を個別
監査した結果、この機械判定には取りこぼしが1件見つかった**:

- `er012_output/editorial_b_voices_trial_09_audio/b1b` `point_two_heading`
  (attempt1→2、間隔8357秒=2時間19分、PASS): `attempt_number(2) <=
  max_attempts(3)`のため`generation_path`は`automatic_retry_within_loop_cap`
  と機械判定されるが、実際の監査対象ファイル
  `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/heading_regen_03_
  result.json`には、当該attempt2が別名の管理ID
  `EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03`の
  もとで明示的に再実行(regen)されたことが記録されている。同一run内の受動的な
  自動retryではなく、**deliberate(意図的)な別run再実行**である。

### 3-3. 非即時7件の個別監査結果(全件記載、隠蔽なし)

| segment | 間隔 | bucket | 連続NG | 結果 | generation_path | 介入confound疑い |
|---|---|---|---|---|---|---|
| meaning_4 | 172秒 | 短時間 | 1 | NG | automatic | no |
| kp5_ja_charon | 282秒 | 短時間 | 6 | PASS | manual | **YES** |
| point_two | 377秒 | 短時間 | 1 | PASS | automatic | no |
| point_one(household) | 567秒 | 短時間 | 3 | PASS | manual | **YES** |
| kp5_ja_charon | 2350秒(39.2分) | 中 | 3 | NG | manual | **YES** |
| point_two_heading | 8357秒(2時間19分) | 中 | 1 | PASS | automatic(**誤判定、実際はdeliberate**) | **YES** |
| full_story_part1(CAR-T) | 51635秒(14時間21分) | 長 | 3 | PASS | manual | **YES** |

**結論: 非即時7件中5件(71%)が手動介入・deliberate別run再実行を伴う**。
「手動介入を伴わない自然発生の長間隔retry」は、meaning_4(172秒、NG)と
point_two(377秒、PASS)の**2件のみ**であり、いずれも「短時間」bucket
(150秒〜30分)にとどまる。「中」「長」bucketの自然発生・介入なしサンプルは
**現時点でゼロ**。これは「時間を置いたら直った」ように見えるサンプルの
大部分が、実際には「人間またはHuman Review Lockフローが介入した」サンプル
であり、時間経過そのものの効果と介入効果(テキスト微修正・別経路実行・
人手確認等)を今のデータからは分離できないことを意味する。先行調査の
「選択バイアス」の指摘(長間隔まで残るのは難しいsegmentだけ)を、個別ケース
監査によってさらに具体化した新規知見である。

## 4. 統計(参考値、件数極小の前提)

- 即時(<150秒) vs 非即時(150秒以上、短+中+長統合)、種別Bのみ:
  即時 N=46・PASS 25(54.35%)、非即時 N=7・PASS 5(71.43%)。
- 両側Fisher正確検定 p値 = **0.6851**(標準ライブラリ`math.comb`による自前実装、
  scipy不使用。周辺合計固定の超幾何分布に基づく全探索計算)。p値0.68は
  「差なし」を否定できないことを意味し、+17.1ポイントの差は現サンプルサイズ
  では偶然の範囲内と解釈するのが妥当。

## 5. 「傾向が十分出た」の事前定義基準と現時点の判定

決定はユーザー。本調査では以下を**分析開始前に(script内にハードコードする
形で)事前定義**し、現時点での到達可否を機械判定した:

- 基準: **(a)** 4つのbucket全てでN≥20、**かつ (b)** 即時binと非即時binの
  PASS率差が20ポイント以上、**かつ (c)** 非即時binに「手動介入を伴わない
  自然発生の長間隔retry」サンプルが最低5件以上含まれること
  (手動介入100%に近いサンプルでは時間経過そのものの効果と介入効果を分離
  できないため)。
- 現状(2026-09-11、56件時点):
  - (a) 4bucket中の最小N = **1**(中央値的にも短時間=4、中=2、長=1と
    軒並み基準未達)
  - (b) PASS率差 = **17.1ポイント**(基準20ポイント未達、僅差ではある)
  - (c) 手動介入なし非即時サンプル = **2件**(基準5件未達)
- **判定: 基準未到達(criteria_met=False)**。3つの条件いずれも満たしておらず、
  特に(c)「介入なし自然発生の長間隔サンプル」がボトルネックである
  (現状すべての「中」「長」bucketサンプルが介入confoundを伴う)。

## 6. 継続モニタリング設計(常駐なし、人工retryなし)

- 新規script: `er011_tts_retry_cooldown_monitor_01.py`(リポジトリroot直下)。
- 入力: `er011_output/tts_retry_timing_monitor_01/observations.jsonl`
  (既存script`er011_tts_retry_timing_monitor_01.py`の出力をそのまま読む、
  新規スキャンはしない=責務分離)。
- 出力: `er011_output/tts_retry_cooldown_analysis_01/{cooldown_pairs.jsonl,
  summary.json, summary.md}`(冪等、再実行のたびに全件再生成・上書き。本
  セッションで2回実行しsummary.jsonのMD5完全一致を確認済み)。
- 再実行コマンド(次回closeout consolidation時等にFableがSonnetへ委任):
  ```
  python3 er011_tts_retry_timing_monitor_01.py
  python3 er011_tts_retry_cooldown_monitor_01.py
  ```
  (両方とも¥0、API呼び出し・TTS生成なし。前者を先に実行して観測データを
  最新化してから後者を実行する。)
- **既知の限界**: `DELIBERATE_INTERVENTION_OVERRIDES`(3-2節のpoint_two_
  heading補正)は個別監査に基づく手動ハードコードのオーバーライド表であり、
  新規に同種の「機械判定漏れ」が発生しても自動検出はされない(per-attempt
  側に「同一run内か別run再実行か」を機械的に判定できるフィールドが存在
  しないため)。今後サンプルが増える際は、非即時bucketの新規行を都度
  個別監査し、該当すればoverride表に追記する運用を推奨する(提案のみ、
  実装判断はユーザー)。

## 7. cool-down retry仕様候補の素案(採用判断はしない、提示のみ)

**現時点でProduction retry仕様を変更する材料は全くない**(5節の通り基準
未達、かつ3節の交絡により「時間経過そのもの」の効果を「介入効果」から
分離できていない)。以下はあくまで「傾向が十分出た場合に提示する」ための
**素案**であり、本調査時点では採用判断もこれ以上の検討も行わない:

- 素案A: 連続NG2回以上に達した場合、即時retryを継続する代わりに、一定時間
  (例: 5〜10分)cool-downしてから次のretryを実行する。
- 素案B: 連続NG3回(既存max_attempts到達)後の自動エスカレーション先
  (Human Review Lock)に、「N分待って自動再試行」という中間ステップを
  追加する(現状はLock→人手介入のみ)。
- 素案C: cool-down自体ではなく、非即時retryで観測された「manual_
  regenerate経路(Human Review Lock解除後)のPASS率が相対的に高い」という
  観測(表3、N=7中5件manual・うちPASS3件)を踏まえ、**時間ではなく経路の
  違い**(Lock解除フローに伴う何らかの追加処理、例えば人間の目視確認や
  regen時の追加パラメータ)が効いている可能性を先に検証する対案。
- いずれも**N不足(5節)のため裏付けなし**。採用の是非はユーザー判断
  (`USER_DECISION_REQUIRED`)であり、本REPORTは提案のみに留める。

## 8. QCD

- Quality: 決定論的集計(LLM不使用)。冪等性を2回実行のsummary.json MD5完全
  一致で確認。非即時7件全件を個別に監査ファイルを直接読み込んで手動確認
  (隠蔽なし、全件記載)。統計計算(Fisher正確検定)は標準ライブラリ
  `math.comb`のみで自前実装(外部ライブラリ依存なし、scipy未インストール
  環境で動作確認済み)。
- Cost: ¥0(API呼び出し・TTS/ASR/LLM生成なし)。
- Duration: 本セッション内で完了(script作成・2回実行での冪等性確認・
  個別ケース監査・本REPORT作成)。

## 出典ファイル

- `er011_tts_retry_cooldown_monitor_01.py`(新規script、リポジトリroot)
- `er011_output/tts_retry_cooldown_analysis_01/cooldown_pairs.jsonl`(56行)
- `er011_output/tts_retry_cooldown_analysis_01/summary.json`
- `er011_output/tts_retry_cooldown_analysis_01/summary.md`
- `er011_output/tts_retry_timing_monitor_01/observations.jsonl`(443行、入力元)
- `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/heading_regen_03_result.json`
  (point_two_headingのdeliberate regen根拠)
- `TTS-RETRY-TIMING-OBSERVATION-MONITOR-01_REPORT.md`(先行調査1)
- `TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md`(先行調査2、
  CAR-T事例の起点)
