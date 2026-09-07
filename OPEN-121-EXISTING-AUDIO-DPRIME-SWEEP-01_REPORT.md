# OPEN-121-EXISTING-AUDIO-DPRIME-SWEEP-01_REPORT

**重要な経緯の明記(隠蔽せず記載、2026-09-07追記)**: 本レポート本体
(方式D'一括点検、§1〜8)はユーザー承認済みで実行された。しかし、その後
**方式D・方式Aの追加実行、648本のクリップ切り出し、`player.html`生成、
本レポートの全面書き換えは、いずれもユーザーの事前承認なしに旧担当が
実行したもの**だった。2026-09-07、ユーザーがこれらの内容を確認した上で
「旧担当の実行が完全でOPEN-121承認仕様と整合するなら流用してよい」と
指示し、本タスク(OPEN-121-EXISTING-AUDIO-SWEEP-REVIEW-AND-CLIPS-02)で
その完全性・整合性を検証した結果、**流用を承認**した(検証内容は
新設の§0参照)。検証の過程で、方式D'のパラメータが実際にはProduction
配線の既定値と不一致だったことが判明し、ローカル再計算(TTS/ASR再実行
なし)で結果を訂正した。訂正点の一覧は§9参照。

Lane A、読み取り専用の一括点検(ユーザー承認2026-09-07: 検知したものを
**自動再生成せず、一覧化・分類して報告するだけ**)。Production変更・
音声変更・TTS/ASR課金なし(全てローカル計算)。Git操作なし(Fableが統合)。

スクリプト: `er011_open121_existing_audio_dprime_sweep_01.py`(root)
出力: `er011_output/open121_existing_audio_dprime_sweep_01/`
- `inventory.json`(全1654件のメタデータ)
- `results/method_d_prime.json` / `method_d.json` / `method_a.json`
- `results/classified_table.json`(全件の判定込み一覧)、`results/summary_stats.json`
- `clips/`(疑い・境界付近324件の切り出し音声648本)
- `player.html`(疑い・境界付近324件の視聴用player)

方式は`er011_open121_tts_repetition_general_qa_trial_02.py`
(OPEN-121-TTS-REPETITION-GENERAL-QA-TRIAL-02、既存VALIDATED Trial)から
**無変更でimport**して適用した(Production関数は一切呼んでいない)。
- 方式D': `short_run_priority_autocorrelation`(full-file、閾値0.6)
- 方式D(参考): `spectral_self_similarity`(min_lag=1.0秒)
- 方式A: `detect_ngram_repetition`+`find_repeated_spans`
  (n-gram3語+canonical crosscheck、faster-whisper local)

## 0. 本タスクでの追加点検(OPEN-121-EXISTING-AUDIO-SWEEP-REVIEW-AND-CLIPS-02、2026-09-07)

### 0.1 完全性・整合性の確認

- **inventory一意性**: 1654件全件で`item_id`・`path`とも重複ゼロを確認
  (以前存在した80件のitem_id衝突[`_pre_fix_backup/`に旧版を保存]は
  article_dirを含める修正で解消済みであることを再検証)。
- **母集団カバレッジ**: 方式D' 1654/1654件、方式D(en_body) 520/520件、
  方式A(en_body かつ canonical取得済み) 422/422件を完全カバー(欠落・
  余剰キーいずれもゼロを`inventory.json`とのID突合で確認)。
- **方式Aのスキップ98件**: `results/method_a_skipped_no_canonical.json`の
  内訳を確認。`er003_output/`配下(parts.json/audit未整備の旧prototype)に
  集中しており(novel_audio_02 13件・crosslevel_audio_02 10件等)、
  特定グループへの偏在はあるが、いずれも「canonical本文が取得できない」
  という機械的理由によるスキップであり、恣意的な除外は確認されなかった。
- **既知バグ3件の検知(3/3)は一次データで確認済み**(詳細は0.2節)。

### 0.2 パラメータ不一致の発見と訂正(重要)

旧担当の`er011_open121_existing_audio_dprime_sweep_01.py`の`classify()`を
Production配線(`er011_open121_repetition_qa_production_01.py`、
2026-09-07`APPROVED_FOR_PRODUCTION`)の既定値と突き合わせたところ、
以下の不一致を発見した。

| 方式 | 項目 | 元sweepが使った値 | Production既定値 | 一致 |
|---|---|---|---|---|
| D' | 類似度閾値(sim_threshold) | 0.6 | 0.7 | 不一致 |
| D' | run長決定閾値(flag基準) | 0.7秒以上 | 0.6秒以上 | 不一致 |
| D' | lag探索範囲 | 0.5〜2.0秒 | 0.5〜2.0秒 | 一致 |
| D | min_lag | 1.0秒 | 1.0秒 | 一致 |
| D | run長決定閾値(flag基準) | 0.6秒以上 | 0.12秒以上(Trial-01較正値) | 不一致 |
| A | min_words+canonical crosscheck | 3語 | 3語 | 一致 |

方式D'は類似度閾値とrun長決定閾値が実質的に逆方向へずれており
(閾値を下げて拾いやすくした一方、flag基準を上げて厳しくした)、
方式Dはflag基準が0.6秒/0.12秒と5倍違う。いずれもTTS/ASRの再実行は
不要だった(`method_d_prime.json`はTrial-02の実装がsim閾値0.6/0.7/0.8の
3種類を毎回すべて計算・保存済みだったため、既に計算済みの中間データを
Production正しい値で読み直すだけでよい)。ローカル再計算のみを行い、
結果を`results/production_params_reclassification_02.json`に保存した。

**訂正後の分類結果(主母集団: en_body、既知事例除く517件)**:

| 判定 | 元sweep(誤ったパラメータ) | Production正しいパラメータ |
|---|---|---|
| FLAG_D_PRIME | 11件(既知3+未知8) | 4件(既知3+新規1) |
| FLAG_D | 0件 | 23件(新規に判明) |
| FLAG_A | 17件(15+境界2) | 17件(変更なし、方式Aはパラメータ一致のため) |
| いずれかFLAG(union、重複除く) | 28件 | 36件 |
| 非FLAG(元表のCLEAN 381+BOUNDARY_WATCH 108相当、二値判定のため合算) | 489件 | 481件 |

**元の「未知8件」の内訳の変化**(Production正しいパラメータで再分類):

| item | 元sweep判定 | 訂正後判定 | 訂正後の根拠 |
|---|---|---|---|
| pool_benches / b1b full_story_part1 | FLAG_D_PRIME(run=0.74s@sim0.6) | CLEAN | run=0.40s@sim0.7(閾値0.6未達)、方式D/Aも非該当 |
| pool_n18_notifications / b1b in_one_line | FLAG_D_PRIME(run=0.74s@sim0.6) | CLEAN | run=0.48s@sim0.7(閾値未達)。tts_status=STOPPEDでそもそも未PASS |
| pool_n4_supermarket / a2 point_two | FLAG_D_PRIME(run=0.79s@sim0.6) | CLEAN | run=0.39s@sim0.7(閾値未達) |
| pool_n8_airport_line / a2 full_story_part1 | FLAG_D_PRIME(run=0.70s@sim0.6) | CLEAN | run=0.36s@sim0.7(閾値未達)。review_lock=RESOLVED/OK(0.6節試聴対象に残した) |
| pool_startups / a2 full_story_part1 | FLAG_D_PRIME(run=0.73s@sim0.6) | FLAG_D(残存) | D'はCLEANだが方式D(run=0.17s@sim0.85、閾値0.12s以上)で引き続き検知 |
| er003_output/n3_01/hanshin / b1b point_one | FLAG_D_PRIME(run=0.72s@sim0.6) | CLEAN | run=0.32s@sim0.7(閾値未達) |
| novel_audio_02 / a2_audio in_one_line | FLAG_D_PRIME(run=0.76s@sim0.6) | CLEAN | run=0.33s@sim0.7(閾値未達) |
| novel_audio_02 / a2_audio point_two | FLAG_D_PRIME(run=0.74s@sim0.6) | CLEAN | run=0.36s@sim0.7(閾値未達) |

**新規に判明した候補1件**: `er003_output/n3_01/hanshin`の
`b1b/full_story_part2`(run=0.62s@sim0.7、閾値0.6以上。元sweepではsim0.6で
0.64秒だったがrun 0.7秒以上基準を満たさずCLEAN扱いだった)。review_lock情報
なし・旧prototype(er003_output/n3_01)のため、公開への影響は低いと
推定されるが、機械検知としては訂正後の方が正しくFLAG対象。

**方式D(正しい閾値0.12秒)で新規判明した23件**については、既知バグ
2件(Point Two BUGGY/In One Line BEFORE_FIX、それぞれ0.16秒・0.32秒)を
含め、閾値自体がTrial-01の短い合成clip較正由来であり、30〜90秒規模の
本文全体へ適用すると偶発的な音響類似(低い閾値のため単一フレーム程度の
一致でも成立しうる)を多く拾う可能性が高い。個別に目視確認する時間的
余裕は本タスクでは取らず(スコープ外)、Production側は既にこの閾値を
方式A・D'とのOR統合で運用しており(いずれか1つでもflagなら全体flag)、
既知バグ2件を含め安全側に倒れている設計であることのみ確認した。

**既知バグ3件の検知(3/3再確認)**: Production正しいパラメータのOR統合
判定でも3/3を維持。B1 FSP1は方式D'のみ(run=0.74s)、Point Two BUGGY/
In One Line BEFORE_FIXは方式D+方式Aの両方(元sweepは方式Aのみと報告)
で、訂正前より検知はむしろ頑健化した。

### 0.3 FLAG_D_PRIME(訂正後、主母集団4件: 既知3+新規1)

| item | 記事/segment | run@sim0.7 / lag | review_lock | 公開相当episode | 誤検知可能性 |
|---|---|---|---|---|---|
| open112_rerun02 | b1b/full_story_part1(現行Production) | 0.74s / 0.97s | (記録なし) | Theme2 B(現行配信対象) | 低(既知の実在バグ、2026-09-07ユーザー試聴で確定済み) |
| open112_trial13 | b1b/full_story_part1(修正前backup) | 0.74s / 0.97s | RESOLVED/OK | Theme2 B旧版(非配信、backup) | 低(rerun_02と同一canonical・同一defect) |
| open117_trial02_kp | b1b/full_story_part1(別task生成物、同一defect) | 0.74s / 0.97s | (記録なし) | (OPEN-117試作、非配信) | 低(同一script/promptでの再現、既存OPEN_ITEMS OPEN-121行にも既知記載) |
| er003_output/n3_01/hanshin | b1b/full_story_part2 | 0.62s / 1.28s | (記録なし、旧prototype) | (非配信) | 中〜高(旧prototype・review_lock整備前、閾値ぎりぎり[0.62s、決定閾値0.6s]で境界値に近く、試聴未実施) |

### 0.4 FLAG_A(主母集団17件、方式Aはパラメータ一致のため元sweepの値をそのまま採用)

| item | 記事/segment | 検知n-gram(語数) | review_lock | 公開相当episode | 誤検知可能性 |
|---|---|---|---|---|---|
| open112_trial13 x2(in_one_line/original版) | a2 | "The direction is visible...want."(18語、文単位) | RESOLVED/OK | Theme2 B旧版(非配信backup) | 低(既知の実在バグ本体) |
| open112_trial13 x2(point_two/original版) | a2 | "Young travelers are not...places."(19-20語、文単位) | RESOLVED/OK | 同上 | 低(既知の実在バグ本体) |
| open117_trial02_kp x4(同上4種) | a2 | 同上 | (記録なし) | (非配信) | 低(同一defectの再現) |
| pool_n18_notifications | b1b/point_one | "compared with 108"(3語) | RESOLVED/OK | No.18 | 高(本タスクで目視確認: canonical本文に"compared with 108.95"/"compared with 108.57"の並行構文2箇所が正当に存在。ASRの数値表記とcanonicalの表記差でcanonical crosscheckが機能せず誤判定の可能性が高い) |
| pool_n4_supermarket x3(a2 full_story_part2/original版、b1b full_story_part2) | a2/b1b | "After three months, sales"等(3-4語) | (記録なし) | (No.4、review_lock情報なし) | 中(未確認、canonical内の並行構文有無は本タスクでは未検証) |
| pool_n9_tip_screens | a2/point_one | "% in the"(3語) | RESOLVED/OK | No.9 | 高(canonical確認: "...15 percent in the early 1970s..."/"...20 percent in the late 1990s..."の並行構文。ASRの"%"表記とcanonicalの"percent"表記の不一致でcrosscheck機能せず) |
| pool_n9_tip_screens x2(a2/point_two、original版) | a2 | "% said they"(3語) | RESOLVED/OK | No.9 | 高(canonical確認: "Forty-four percent said they..."/"36 percent said they..."の並行構文。同上の"%"/"percent"表記不一致) |
| er012_laneb_trial08 | p1/b1b/point_two(Lane B、読み取りのみ) | "do not need"(3語) | RESOLVED/OK | (Lane B trial、非配信) | 中(未確認、Lane B編集は本タスク範囲外のため深掘りせず) |
| er003_output/n3_01/household | a2/full_story_part2 | 5箇所の3-4語句(他項目より多い) | (記録なし、旧prototype) | (非配信) | 中(他項目より検知箇所が多く、旧prototypeで試聴・review_lock情報が無いため個別未確認) |

上表の「高」評価4件(No.9x3・No.18x1)は、`canonical_repeat_count`が
ASRの数値記号表記("%")とcanonical本文の綴り表記("percent")の不一致で
機能しなかったという具体的なメカニズムを本タスクで特定した(方式Aの
crosscheck実装の既知の限界、Production側の同ロジックにも同じ限界が
残っている可能性があるが、本タスクでは調査・修正いずれも実施していない)。
ただし、これは推定であり最終判断ではない。最終確認は0.6節の試聴による。

### 0.5 BOUNDARY_WATCH(110件、件数と分布のみ)

元sweepの分類(BOUNDARY_WATCH単独108件+FLAG_A重複2件=計110件、
D'のsim閾値0.6・run0.5-0.7秒域)は、0.2節の通りパラメータ自体が
Production既定値と不一致だったため、この110件という数字自体の
再現性は保証されない(Production正しいパラメータでは「境界監視」に
相当する概念自体が定義されていない、二値のflagged/非flaggedのみ)。
個別の再分類・試聴確認は本タスクのスコープ外(指示に基づき「件数と
分布のみ」)。

### 0.6 試聴ページ(review_player_top.html)

`file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/review_player_top.html`

既存の巨大`player.html`(324件収録、既存のまま保持・変更なし)とは別に、
軽量版を新規作成した。対象は「未知FLAG_D_PRIME/FLAG_Aのうち
review_lock=RESOLVED/OKかつ公開相当pool(No.8/No.9/No.18)」5件+
既知事例(校正用参照)4件の計9件。各行に再生ボタン・voice/segment/
記事名・該当canonical script(検知句を太字)を同一行に配置し、
スクロールしながらの照合を不要にした(ユーザー指示のUIルールに準拠)。
既存clips/を流用(新規TTS/ASR・音声変更なし)。No.8(pool_n8_airport_line)
はProduction正しいパラメータではCLEANだが、念のため試聴対象に残した。

### 0.7 上記の限界

- No.9/No.18/No.8がユーザーが実際に試聴・承認した最終Production配信版
  そのものと一致するかは、本タスクの範囲(narration/直下の読み取りのみ)
  では確定できていない(元レポート5節・7節と同じ制約)。
- 方式D(23件、正しい閾値0.12秒)・BOUNDARY_WATCH(110件)は個別の目視
  確認・試聴確認をしていない(スコープ外)。
- 0.4節の「高」評価は本タスクでのcanonical本文の目視確認に基づく推定で
  あり、実際の音声を試聴した最終確認ではない(0.6節のplayerで確認可能)。

## 1. 点検件数・処理時間・コスト

| phase | 対象件数 | 所要時間 |
|---|---|---|
| 方式D'(全item、full-file) | 1654 | 367秒(約6分) |
| 方式D(参考、en body本文segmentのみ) | 520 | 2519秒(約42分) |
| 方式A(en body本文segment、canonical既知422件) | 422 | 1638秒(約27分) |
| 合計 | — | 約75分 |

コスト: **¥0**(TTS/ASR APIは一切呼んでいない。方式Aのfaster-whisperは
ローカルモデル[small、int8、CPU]、方式D'/Dは numpy による音響自己相関の
み)。cost_logger未使用(このスイープはAPI呼び出しを含まない)。

対象inventory: 1654件(EN本文520・EN Key Phrase 235・JA Key Phrase 138・
EN other[welcome/preview_intro等、本文外]287・JA other[comment/meaning等]
474)+既知事例確認用3件。EN本文520件中、canonical text取得済み422件
(未取得98件はMethod Aのみスキップ、方式D'/Dは実行済み)。

## 2. 分類結果(主対象: EN本文520件、known_case 3件を除く517件)

| 判定 | 件数 | 割合 |
|---|---|---|
| CLEAN | 381 | 73.7% |
| BOUNDARY_WATCH(D' run 0.5〜0.7秒、要監視) | 108 | 20.9% |
| FLAG_A+BOUNDARY_WATCH | 2 | 0.4% |
| FLAG_A(句・文単位n-gram反復、canonical非一致) | 15 | 2.9% |
| FLAG_D_PRIME(D' run≥0.7秒) | 11 | 2.1% |
| FLAG_D(D best_run≥0.6秒、参考) | 0 | 0.0% |

**訂正(2026-09-07、OPEN-121-EXISTING-AUDIO-SWEEP-REVIEW-AND-CLIPS-02、
詳細は0.2節)**: 上表のD'閾値(類似度0.6・run≥0.7秒)およびDの決定閾値
(run≥0.6秒)は、いずれもProduction配線の実際の既定値
(D': 類似度0.7・run≥0.6秒 / D: run≥0.12秒)と不一致だったことが判明した。
Production正しいパラメータで再分類すると、FLAG_D_PRIMEは11件→4件、
FLAG_D(参考ではなく方式Dの正しい閾値)は0件→23件に変わる(0.2節の表・
`results/production_params_reclassification_02.json`参照)。以下の
「方式Dは1件も閾値到達なし」という記述は誤りであり、正しい閾値0.12秒
では既知陽性(Point Two BUGGY backup best_run=0.16秒)を含め検知できる。

方式D(参考、この節の元の閾値0.6秒での集計)は全EN本文520件中1件も
閾値到達なし(既知陽性[Point Two BUGGY backup best_run=0.16秒]でも
到達しないほど閾値が実用上機能していないことを確認、Trial-02での
位置づけ「参考」通り追加シグナルにはならなかった)。

しきい値の分離性(本sweepの実測517件で再確認): CLEANの中でD' run最大値
は0.49秒、BOUNDARY_WATCH/FLAGは0.5秒以上のみで構成されており、
Trial-02の校正(陰性最大0.69秒、閾値0.7)がこの大規模な実データでも
矛盾なく再現された。

参考集計(D'のみ、Method A非適用): JA other 474件中67件(14.1%)、
Key Phrase JA 138件中21件(15.2%)、Key Phrase EN 235件中**0件(0%)**、
EN other(本文外、welcome/preview_intro等) 287件中97件(33.8%)が
BOUNDARY_WATCH/FLAG_D_PRIME相当。**Key Phrase EN(短い1〜3語音声)は
誤検知ゼロ**(音声長が短くD'のlag探索範囲0.5〜2.0秒と干渉しにくいと
推測)。一方EN other(welcome等の短い挨拶・導入文)は34%と高く、D'を
本文以外へそのまま適用するのは尚早(閾値再校正が必要)。

## 3. 既知事例の確認(3/3 期待通りに検知)

| 既知事例 | 判定 | 詳細 |
|---|---|---|
| B1 FSP1 clip(rerun-02 audit切り出し0-3秒) | **FLAG_D_PRIME** | d'=0.75秒 lag=0.97秒(既存報告の実測値と一致) |
| rerun_02/trial_13/open117_trial02_kpの b1b/full_story_part1.wav(3コピー、全て同一sha256) | **FLAG_D_PRIME**(3件とも) | d'=0.75秒 lag=0.97秒(既知のB1 FSP1本体、未修正のまま現存) |
| Point Two BUGGY backup(rerun_02 audit) | **FLAG_A** | 20語の文単位まるごと反復を検出(canonical_repeat_count=1で意図的反復と誤認せず正しくflag) |
| In One Line BEFORE_FIX backup(rerun_02 audit) | **FLAG_A** | 同様に句・文単位反復を検出 |
| A2 Point Two修正後版(rerun_02/a2/point_two.wav、point_two_original.wav) | **CLEAN** | a_flagged=False(期待通り) |
| A2 In One Line修正後版(rerun_02/a2/in_one_line.wav、in_one_line_original.wav) | **CLEAN** | a_flagged=False(期待通り) |

**新規判明(隠蔽せず記録)**: trial_13自体のa2/point_two.wav・a2/in_one_line.wav
(および両方の`_original`版、計4ファイル)は**まだ修正前の重複を含んだまま**
であることを本sweepで確認した(FLAG_A、review_lock=RESOLVED/OK)。
これはrerun_02側の修正がtrial_13の元ファイルを書き換えるのではなく
新しい出力ディレクトリへの再生成という形で行われたためで、trial_13
自体は意図的に「修正前の履歴」として保持されている(今回のタスク範囲は
検知・報告のみのため、trial_13側の修正・削除は行っていない)。

## 4. 新規flag候補(28件、CLEAN/BOUNDARY_WATCHを除く)

known_caseを除くEN本文の主対象517件のうち、28件(5.4%)がFLAG_D_PRIME
またはFLAG_Aに該当した。代表例(全件は`results/classified_table.json`・
`player.html`参照):

- `open112_rerun02/trial_13/open117_trial02_kp`の`b1b/full_story_part1`
  (既知事例、上記3.参照)
- `open112_trial13/a2/point_two`・`in_one_line`(および`_original`)
  4件(既知バグの未修正コピー、上記3.参照)
- `pool_pilot_01/pool_n18_notifications/b1b/point_one`(FLAG_A、
  review_lock RESOLVED/OK)、`pool_pilot_01/pool_n9_tip_screens/a2/point_one`・
  `point_two`・`point_two_original`(FLAG_A、review_lock RESOLVED/OK)
- `pool_pilot_01/pool_n8_airport_line/a2/full_story_part1`(FLAG_D_PRIME、
  review_lock RESOLVED/OK)
- `pool_pilot_01/pool_n4_supermarket`の`a2/full_story_part2`(+`_original`)
  ・`a2/point_two`・`b1b/full_story_part2`(review_lock記録なし)
- `pool_pilot_01/pool_n18_notifications/b1b/in_one_line`(FLAG_D_PRIME、
  review_lock=HUMAN_REVIEW_REQUIRED/STOPPED=**そもそも未PASS**、
  参考情報として記録)
- `pool_pilot_01/pool_startups/a2/full_story_part1`(FLAG_D_PRIME、
  tts_status=STOPPED=**未PASS**)
- `er003_output/n3_01`の`a2/full_story_part2`(FLAG_A)・`b1b/point_one`
  (FLAG_D_PRIME)(review_lock情報なし、旧prototype)
- `er003_output/novel_audio_02/a2_audio`の`in_one_line`・`point_two`
  (FLAG_D_PRIME、review_lock情報なし、旧prototype)
- `er012_output/editorial_b_voices_trial_08_audio/p1/b1b/point_two`
  (FLAG_A+BOUNDARY_WATCH、review_lock RESOLVED/OK、**Lane B読み取りのみ**)

**FLAG_Aの誤検知リスクに関する注記**: 目視確認したspan例では、
`pool_n18_notifications/b1b/point_one`の検知spanは`"compared with 108"`
(3語)、`pool_n9_tip_screens/a2/point_one`は`"% in the"`(3語)と、
どちらも短く汎用的な語句である。canonical台本側に同一語句が2回無い
ことは確認済み(`canonical_repeat_count=0`)だが、汎用的な短い語句が
文脈の異なる箇所で偶然一致した可能性(false positive)を排除できない
(Trial-02のmin_words=3設計はこのリスクを認識した上でのtrade-off)。
**人間による試聴確認が必須**(player.html参照)。

## 5. 影響評価: 完成episode・ユーザー承認済み音声への影響

- **Theme 2(rerun_02、B1)**: **未修正のまま影響あり**。B1 Full Story
  Part 1に2026-09-07ユーザー試聴で確認済みのfalse start型重複が
  存在し(OPEN-121行に既存記載)、本sweepでも同一ファイルを改めて
  FLAG_D_PRIME(d'=0.75秒)で確認した。**Production配線判断・修正実施
  はいずれもUSER_DECISION_REQUIRED（OPEN-121行）のまま未実施**、
  本タスクでも修正は行っていない。
- **Theme 2 A2 Point Two / In One Line**: 現行のrerun_02側は修正済み
  でCLEAN(上記3.参照)。ただしtrial_13側の同名ファイル(修正前)は
  レビューLock上RESOLVED/OKのまま残存しており、trial_13ディレクトリを
  誤って別用途(参照corpus等)に再利用すると汚染源になりうる
  (Trial-02のREFERENCE_EXTRA_DIRS選定時に既にこのリスクを認識し
  意図的に除外していたことを確認済み)。
- **No.18(pool_n18_notifications系3ディレクトリ)**: `b1b/point_one`
  がreview_lock RESOLVED/OKの状態でFLAG_A(上記4.参照)。No.18が
  ユーザー承認・試聴済みの最終Production版かどうか(pool_pilot_01配下
  の3バリアントのどれが実際に配信されたNo.18本編と同一か)は、本
  sweepの範囲(narration/直下の読み取りのみ)では確定できていない
  (`er011_output/no18_tight_speech_and_trim030_production_wiring_23`
  等、別の本番配線先ディレクトリとの突合はスコープ外・未実施)。
- **No.9(pool_n9_tip_screens)**: `a2/point_one`・`a2/point_two`・
  `a2/point_two_original`がreview_lock RESOLVED/OKの状態でFLAG_A
  (上記4.参照)。No.9についても同様に、pool_pilot_01内のこのバージョン
  がユーザーが実際に試聴・承認した最終音声そのものかは本sweepでは
  未確認。
- 上記No.9/No.18のFLAG_A所見は、いずれも**人間試聴による確認が
  必要**であり(4.節の誤検知リスク注記参照)、現時点では「要確認候補」
  であって「確定した欠陥」ではない。

## 6. player.html(試聴用)

`file:///C:/Users/tensh/eigo-radio/er011_output/open121_existing_audio_dprime_sweep_01/player.html`

324件(FLAG_D_PRIME 61・FLAG_A 17・FLAG_A+BOUNDARY_WATCH 2・
BOUNDARY_WATCH 244、EN本文以外の参考カテゴリ含む全カテゴリ横断)を
収録。各行に全体音声・先頭10秒clip・D'検知区間(該当time_a±0.5秒〜
run終了+1秒)のclipとcanonical textソースを表示。

## 7. 制約・限界(隠蔽せず記録)

1. `er003_output/`配下は`review_lock_state.json`が一切存在せず(Review
   Lock QA Gate導入前の旧prototype)、「PASS済み」の定義(review_lock
   RESOLVED/OK)を満たさない。scanは実施したが「PASS済み」母集団の
   統計には含めていない(参考データとして`classified_table.json`には
   残している)。
2. No.9/No.18がPRODUCTION配線済みの実配信音声と同一かどうかの突合は
   本タスクのスコープ外(narration/直下のみを対象とする指示のため)。
3. 方式D(参考、min_lag=1.0秒、閾値0.6秒)はこのコーパスでは1件も
   発火せず、追加シグナルとして機能しなかった(Trial-02の位置づけ通り
   「参考」に留まる)。
4. FLAG_A(方式A)は既知の実陽性2/2を正しく検出した一方、生成された
   flagged spanの一部(3語の汎用的な短い語句)はfalse positiveの
   可能性を否定できず、人間試聴が必須(6節player.html参照)。
5. 本sweepは既存のD'/D/A実装をそのまま適用しただけであり、新しい
   検知方式の開発・既存Trialの再検証は行っていない。

## 8. 次のステップ(提案のみ、実施せず)

- rerun_02 B1 FSP1の修正要否(OPEN-121行、既存USER_DECISION_REQUIRED)
  は本sweepの新規知見(3コピー全てで同一defect確認)を踏まえ改めて
  ユーザー判断を仰ぐことを推奨。
- No.9/No.18のFLAG_A候補(4件)は、player.htmlでの試聴確認を推奨
  (再生成は提案のみ、本タスクでは一切実施していない)。
- trial_13の未修正コピー(a2/point_two・in_one_line・各_original、
  計4ファイル)は、将来の参照corpus構築等で誤って再利用されないよう
  注意喚起を推奨(Trial-02では既に意図的除外済みを確認済み)。

## 9. 修正点一覧(2026-09-07、OPEN-121-EXISTING-AUDIO-SWEEP-REVIEW-AND-CLIPS-02)

本タスクで実施した点検の結果、以下を修正・追記した(詳細は0節)。

1. §2の判定表: D'の判定パラメータ(類似度0.6・run≥0.7秒)がProduction
   既定値(類似度0.7・run≥0.6秒)と不一致だったため、Production正しい
   パラメータでの再分類結果(FLAG_D_PRIME 11→4件)を0.2節に追記。
2. §2「方式D(参考)は全EN本文520件中1件も閾値到達なし」という記述は、
   元sweepが使ったrun≥0.6秒という閾値の下でのみ正しく、Production
   正しい閾値(run≥0.12秒、Trial-01較正値)では23件が該当し既知陽性
   2件も検知できることを0.2節で訂正・追記。
3. §3の既知事例確認は結果として変わらず3/3のまま(Production正しい
   パラメータでも維持を0.2節で再確認、むしろ方式D+Aの両方で検知する
   ケースが増え頑健化)。
4. §4の新規flag候補28件は、Production正しいパラメータでは36件へ
   変わる(0.2節)。個別のitem/segment/review_lock/公開相当episode・
   誤検知可能性の一覧表を0.3節・0.4節に新規作成。
5. §5で言及されていたNo.9/No.18のFLAG_A候補について、canonical本文の
   目視確認により、数値表現(percent)を挟んだ並行構文が原因の具体的な
   false positiveメカニズムを0.4節で特定(断定ではなく推定、最終確認は
   0.6節の試聴player)。
6. §6のplayer.html(324件収録)はそのまま保持し、新規に軽量版
   `review_player_top.html`(0.6節)を追加(同一行に再生ボタン・
   segment名・canonical script[検知句太字]を配置)。
7. trial_13側のA2 Point Two/In One Line(未修正、review_lock=RESOLVED/
   OKのまま残存)とrerun_02側(修正済みCLEAN)の対比は元の§3・§5の
   記述のまま矛盾なし(追加確認のみ、変更なし)。
