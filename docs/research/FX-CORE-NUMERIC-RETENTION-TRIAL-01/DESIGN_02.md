# DESIGN_02 (DESIGN_01 + Opus条件A必須修正M1〜M5・推奨R1〜R5の反映。2026-10-25、委任_02)

方式の骨格はDESIGN_01のO3(B3 Storylineに答えの数値<=2を入れさせ、E=中核∩Storyline、R0直後に決定論の保持Gate)のまま。DEV実装=`er115_fx_numeric_retention_trial_01.py`(Production非接続)、test=`er115_fx_numeric_retention_trial_01_test_01.py`(28 PASS)。

## 1. M1〜M5・R1〜R5の反映表
| ID | 内容 | 反映 | 実装/証跡 |
|---|---|---|---|
| M1 | Storyline数値の決定論検証(+違反時B3を1回だけ再実行) | B3直後に`derive_E`: Storylineの数値(年/序数/名称内番号=無視、単位なし小整数=無視[ambiguous]、それ以外)は全て、注記sidecarで`core`かつニュース欄に現れる同一概念に対応し、概念数<=2であること。違反(周辺数値・未対応・3個以上)=B3を`M1_RETRY_NOTE`付きで**1回**再実行(1回目artifactは`storyline_b3_attempt1/`へ退避)。再実行後も違反=`M1_VIOLATION`(chainへ進まない・記録・Fable報告)。Eの照合表記は**ニュース欄の表記**(Storylineの表記ゆれ`42〜46メートル`はニュース欄`約42〜46`へ写像) | `derive_E`/`run_b3_dev`、test: `test_derive_E_*`・`test_b3_dev_*` |
| M2 | Gate必須=「答えの数値」のみ。時間・前提(年単位)は観察のみ。ソフトWARNは誤解表現検出に変更 | `gate_required = kind in(magnitude,range) かつ 単位が年/年前/万年/億年/兆年でない`。年単位・日付は`observe_E`(Gateでブロックしない)。`scan_misreading`: 時間数値の前後40字に「今も/毎年/一定の速/ずっと/現在も…」、および本文に「月の誕生以来」等があればWARN(観察のみ)。事前登録A-3に『後期の縮み・開始時期は研究上の推定で未確定・誕生以来と書かない』を人手判定項目として固定 | `derive_E`/`scan_misreading`、PREREGISTERED A-3 |
| M3 | 再実行枠・判定表の明文化 | 下記§2。R0/R1/R2各最大2呼出。R1再実行は**新規**。R2は記号QAと保持で1回を共有 | `run_w1_dev`、test: `test_r0_*`・`test_r1_*`・`test_r2_*` |
| M4 | 照合の較正 | 人手blindラベル126件+単位言い換え表+単位なし一致の厳格化+英語単位hint。CALIBRATION_01.md | `match_core`/`en_present` |
| M5 | B3標本を増やす | 月B3x3(s1〜s3)。中断条件=PREREGISTERED | `er115 b3`コマンド |
| R1 | B3追記は「Storylineを決めた後」の手順。Storyline選択・Fact採否を数値の有無で変えない | `B3_ADDENDUM`冒頭に明記(Test4との整合)。追記は`extra_note`位置(user messageの末尾)にclientラッパで足す=B3 Promptファイル本体は不変 | `B3_ADDENDUM`(sha=証跡) |
| R2 | 数値でない記事を対照にB3のみ | uk_train_speaker_playback B3x1(約12円) | Phase 1 |
| R3 | 過剰掲載指標=「E以外の中核数値の掲載数」「周辺数値混入数」。coffee等は基準を複数 | PREREGISTERED A-2/B | `measure_run` |
| R4 | 範囲正規化=「数字〜数字」のみ、ニュース欄と『テーマ：』行のみ、概数注記挿入後、照合は〜とから両方 | `normalize_ranges`(日付範囲・ハイフン・R0_PROMPT本体[sha不変]には触れない。`news_field_for_writer`の後に適用) | test: `test_normalize_ranges_*`・`test_production_prompt_constants_unchanged` |
| R5 | Storyline方式不成立時の代替=B3 JSONに『答えの数値(中核数値の表記から2個以下)』欄 | **実装しない**。設計案として残す(§4)。M1検査で3標本中2以上がE=∅またはM1違反ならPhase 1を中断しFableへ報告 | 本書§4 |

## 2. 再実行枠・判定表(M3)
上限(記事1本・段ごと): R0 <=2呼出 / R1 <=2呼出(新規) / R2 <=2呼出。記号QAと保持は**1つの再実行枠を共有**する(最大2回の再実行にしない)。Gateは本文を書き換えない。STOP時は両方の本文を`ja_writer/audit/`に保存。
### R0(初回text0 -> 最大1回の再生成)
| 初回R0 | 再生成の内容 | 再生成後 | 結果 |
|---|---|---|---|
| 記号OK・保持OK | なし | - | 通過(1呼出) |
| 記号NGのみ | 既存の記号violation noteのみ(=Production記号QAと同一Prompt) | 記号OK かつ 保持OK | 通過(2呼出) |
| 記号NGのみ | 同上 | 記号NG または **Eが消えた** | STOP(`JANumericRetentionStopError`) |
| 保持NGのみ | 『次の数字が本文にありません: {表記}。…』 | 記号OK かつ 保持OK | 通過 |
| 保持NGのみ | 同上 | 記号NG または 保持NG | STOP |
| 両方NG | 記号note+保持noteを1つにまとめて1回 | 両方OK | 通過 |
| 両方NG | 同上 | いずれかNG | STOP |
注: 『初回が記号のみ不合格・Eあり』で再生成によりEが消えると、Production(記号QAのみ)ならSTOPしない場面でもSTOPが増える。この増分はPhase 1/2でSTOP率として実測する。
### R1 / R2
- R1: 直後に保持Gate(記号QAは従来どおりR1にはない)。不足=R0本文から同一入力で**1回だけ**再実行(新規仕組み)。再実行後も不足=STOP。
- R2: 直後に記号QA+保持を判定。どちらか不合格=同一R1生出力から**1回だけ**再実行(Productionの記号QA再実行と同じ枠を共有)。再実行後に記号NGまたは保持NG=STOP。
### 費用(M3更新)
- 最悪(R0再生成+R1再実行+R2再実行+M1のB3再実行)= R0 7.6 + R1 3.9 + R2 4.2 + B3 12.1 = **約28円/記事**(従来15.8円+M1分12円)。期待増分 = P(R0にE無し)x7.6 + P(R1/R2再実行)x(3.9〜4.2) + **P(B3再実行[M1違反])x12**。実測確率はPhase 1/2で確定(量産単価増分はTRIAL_RESULTで更新)。

## 3. E(必須集合)の定義(確定)
`E = ニュース欄で【中核数値】かつStorylineに現れる概念`(<=2個)。そのうち`gate_required`(= magnitude/range、かつ単位が年系でない)だけを保持Gateの対象とする。日付・年単位の前提数値・単位なし小整数は`observe_E`(計測のみ)。Eの表記はニュース欄の表記(単位hintはニュース欄で表記直後に付く単位=例『約42〜46【中核数値】 m』のm)。概数可の数値は概数表記も許容。

## 4. R5(代替案・未実装)
M1検査で方式が成立しない(3標本中2以上がE=∅またはM1違反)場合の代替は撤退でなく、B3の同じ呼び出しのJSON schemaに`answer_numbers`欄(中核数値の表記から<=2個)を足す案(B3自身の判断=重複システムでない、文章からの抽出より検証しやすい、schema変更が入る)。Fableが採否を決める(実装はFable Go後)。

## 5. Production不変の保証(確認項目)
- `grep -l "er115_\|JANumericRetentionStopError\|B3_ADDENDUM" *.py` はer115_*以外で0件(`test_isolation_no_production_reference`)。
- OFF時(range_norm=False, rule9=False)の`build_r0_prompt_dev`は`w1.build_r0_prompt`とバイト一致(`test_off_is_byte_identical_to_production`)。`jaw.R0_PROMPT`のsha256=`6108a7cd…8366`固定(`test_production_prompt_constants_unchanged`)。
- DEVモジュールに環境変数読取・CLI経由のON/OFFはない(`test_dev_flag_free_import`)。実行は`er115_fx_numeric_retention_trial_01.py b3|chain|measure`を明示起動したときのみ。出力は`er115_output/fx_numeric_retention_trial_01/`限定。
- B3: `er019_family_x_entertainment_production_runner_01.run_storyline_b3`/`run_annotation_producer`/`run_core_number_rounding`、`er053_family_x_factlock_ja_writer_01`の各関数、`er012...run_writer_stage`はimportして呼ぶだけ(編集0)。

## 6. Phase 1で追加した設計変更(M1〜M5/R1〜R5の外・実測で判明、Opus未レビュー)
**6-1 出力側の範囲正規化(R1/R2出力の「数字〜数字」→「数字から数字」、決定論)**: 実装=`make_astra`/`normalize_ranges_counted`、再開=`resume_w1_dev_from_r2`。
- 実測: R0は範囲正規化(R4)した入力に従い「約42から46 m」と書いたが、R1(Production逐語のAstra revise)が「約42〜46メートル」へ書き戻し(R1: 3/3標本)、R2も入力が「から」でも波ダッシュを出力(B/s1: 2箇所)。Productionと同じ記号QAではR2がSTOP(A/s1: 3箇所・A/s3: 1箇所、同一R1生出力での再実行でも解消せず)。波ダッシュのままでは音声が「約42なになに46メートル」になる(Normalizer実測)。
- 対策: Astra段(R1/R2)の出力にだけ、数字〜数字の波ダッシュを「から」へ戻す決定論処理を適用(数字以外の波ダッシュには触れず、既存の記号QAが従来どおり検出する=`test_non_numeric_wave_still_flagged_by_symbol_qa`)。LLM追加call 0。入力側R4(OpusはWriter入力側のみで十分と判断)に出力側を追加した形で、**Opusの設計レビュー範囲(J2=Writer入力側のみ)を超える**。Production採用時は条件A/Cの再レビュー対象。
- 位置づけ: C4(波ダッシュ衝突)の直接証拠。この衝突がある限り、範囲値を含む中核数値は「Writerが避ける」か「R2でSTOP」になる(Productionの月run_ms_01のR0が最初に波ダッシュで再生成された事実とも整合)。
**6-2 費用ガードの運用**: DEV runnerにper-run capとphase cap(`phase_spent_jpy`=er115_output配下の全`raw_usage_log.jsonl`合計)を実装。s5のB3呼出後にphase cap(120円)を0.12円超過して発火(B3単価の見積差)。
