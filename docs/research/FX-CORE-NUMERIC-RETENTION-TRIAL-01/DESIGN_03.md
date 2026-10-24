# DESIGN_03 (DESIGN_02 + Opus差分レビュー(条件A)必須修正M1〜M5の反映。2026-10-25、委任_03)

骨格はDESIGN_02(B3 Storylineに答えの数値<=2を入れさせ、E=中核∩Storyline、R0/R1/R2直後に決定論の保持Gate)のまま。追加分はすべてDEV専用(`er115_fx_numeric_retention_trial_01.py`、Production非接続・既定OFF)。test=`er115_fx_numeric_retention_trial_01_test_01.py`(46 PASS)。証跡=`OPUS_REVIEW_02.md`、基準=`PREREGISTERED_CRITERIA_02.md`。

## 1. M1〜M5の反映表
| ID | 内容 | 実装 | 証跡/test |
|---|---|---|---|
| M1-a (O-1') | B3追記ブロックを改訂(v2): Storylineに入れる数値は「問いへの答えそのものの値」に限る。予測値・別の推定・過去の値・基準値などの比較相手は、**比較そのものが答えの場合を除き**数値で入れず言葉で述べる(比較が答えなら比べる2値を入れてよい=合計最大2個)。v1(Phase 1)は不変で残す。B3 Prompt本体は不変(user message末尾へclientラッパで追記) | `B3_ADDENDUM_V2`/`B3_ADDENDA`/`run_b3_dev(addendum_version=)` | `test_b3_addendum_v2_text_and_v1_unchanged`、m1_result.json の`b3_addendum_version`/`b3_addendum_sha256` |
| M1-b (O-2') | **E(gate_required)と同じ単位系**の、E以外の中核数値だけを、Writer向けのニュース欄の印だけ【中核数値】→【周辺数値】へ付け替える。対象=magnitude/rangeでクラスcore・Eの概念でない・単位系が取れてEと同じ(長さ[m/km/cm/mm]、質量、%、通貨別。cm/100万年のような速度は先頭の単位で判定)。**残す**=年系・期間(年/か月等)、別の単位系、単位が取れない数値、単位なし小整数(<=31)、日付/序数、E自身。E空なら何も下げない。付け替えは契約検証後のメモリ上の`facts_text`/`news_field_text`にだけ行い、注記済みB3ファイル・sha・Production`derive_ranks`・規則5の文言は不変。付け替えた表記の【概数表記】行はWriter向けoverlay(メモリ上コピー)から外す | `dimension_of`/`plan_o2prime`/`swap_marks`/`filter_overlay`、`run_w1_dev(o2prime=True)` | `o2prime_plan.json`(付け替え対象・残した理由・news欄shaの前後)、`test_o2prime_*`(6本) |
| M2 | R1/R2出力の**新規数値検出**: 数値表記(magnitude/range、単位なし小整数除く)の数字が、R0本文+ニュース欄のどの数字とも一致しなければ新規数値。保持Gateと**同じ再実行枠**を共有(R1は1回再実行、R2は記号QA・保持と1回を共有)、解消しなければSTOP。決定論・追加LLM call 0(費用増は再実行時のみ)。R0はAstra段でないため対象外(R0本文が基準) | `new_numbers`/`_new_numbers_m2`/`run_w1_dev(m2=True)` | Phase 1の保存済みR1/R2で検証: A/s1・A/s3=新規0(誤検出0)、B/s1の約45=R1・R2で検出。`test_new_numbers_*`・`test_m2_*`(5本) |
| M3 | 出力側の範囲正規化(J2)の位置づけを明記: **Gateより前の決定論の後処理(既存`postprocess_ja`の延長)で、正本のR1/R2本文を書き換える**。TTSに渡す使い捨てコピーだけを変える`er003.normalize_tilde_placeholder_ja`とは異なる。対象=`surface_kind=="range"`の「数字〜数字」のみ(日付範囲・片側のみ『100円〜』は変換されず従来どおり記号QAでSTOP)。変換件数(`range_wave_normalized`)と変換前sha(`raw_sha256_before_norm`)を記録済み。A/s1・A/s3の初回R2 STOP(`stop_record_first_attempt_no_postnorm.json`)=『正規化なしならSTOP』の証拠として保存。範囲値の波ダッシュはProduction W-1にも存在する欠陥として`OPEN_ITEMS.md`に別件登録 | `normalize_ranges_counted`/`make_astra` | OPEN_ITEMS(別件)、各標本の`runtime_evidence.json` |
| M4 | 事前登録基準の改訂(A-2〜A-5) | - | `PREREGISTERED_CRITERIA_02.md`(生成前commit 25da62900) |
| M5 | 印の付け替えのtest | - | 年系は下げない/単位が取れない数値は下げない/別単位系は下げない/E空は下げない/E自身は下げない/周辺・日付は触れない/swap_marksが印以外不変/OFF(既定)でProduction DEV入力とバイト一致・ファイル0/ON時に契約済みファイルshaが不変(`test_o2prime_*`) |

## 2. 担当の分け方(Opus)
- B3追記(O-1')=「Eを正しくする」(答えの数値だけをStorylineへ)。
- 印の付け替え(O-2')=「Writerが使える範囲を正しくする」(Eと同じ量の別の値を使えなくする。使ってよいが必須でない数値[年系・別単位系]は中核のまま)。
- `derive_ranks`本体・規則5の文言・R0_PROMPT・R1/R2 Promptは不変(sha固定test)。

## 3. 再実行枠(M3の更新)
DESIGN_02 §2を継承し、**M2の新規数値検出がR1/R2の保持Gate・記号QAと同じ枠**に入る(R1: 保持不足or新規数値→同一入力で1回再実行、なお不足/新規ならSTOP。R2: 記号NG・保持不足・新規数値のどれかで同一R1生出力から1回再実行[共有]、なお残ればSTOP)。最悪費用はDESIGN_02と同じ約28円/記事(新規数値による再実行はR1 3.9円/R2 4.2円の範囲)。

## 4. 想定する失敗モードと扱い
- 比較そのものが答えの記事(例: コーヒー価格の前年同月比と過去値): StorylineにO-1'で比べる2値が入ればともにE(付け替え対象外)。O-1'のB3追記が効かず片方しか入らなかった場合、もう片方が同単位系なら付け替えられて必要数値を下げる→Phase 2のcoffeeで必須確認(合格条件⑥)。
- 750がEに入る標本(s2/s5型): O-2'は効かず、保持Gateが不要数値の掲載を強制し得る→O-1'(B3)で防ぐ。(ii)の基準でStoryline内の750を0/3とする。
- 長さ系の任意中核数値(例: 『長さ1km超』)が同単位系なら付け替えられる(任意扱いなので品質基準違反ではないが、O-2'は単位系で一律に下げる鈍い規則)。単位なし小整数(s3の『1』)は対象外のため実際には付け替わらない。

## 5. Production不変・採用時の必要作業
- `grep`: er115_*以外に`er115_`・`JANumericRetentionStopError`・`B3_ADDENDUM`の参照0(`test_isolation_no_production_reference`)。DEVに環境変数読取なし(`test_dev_flag_free_import`)。`run_w1_dev(o2prime=False, m2=False)`・`run_b3_dev(addendum_version="v1")`が既定(`test_isolation_phase1b_flags_have_no_env_or_default_on`)。CLIの`--o2prime`/`--m2`/`--b3-addendum v2`は手動指定したときのみ有効。
- 採用時の必要作業は`ADOPTION_NOTE_01.md`を参照(本委任で更新)。
