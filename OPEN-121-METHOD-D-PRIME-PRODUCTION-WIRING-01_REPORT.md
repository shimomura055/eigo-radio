# OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01

**管理ID**: OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01
**種別**: Production配線Gate 3検証(`APPROVED_FOR_PRODUCTION`後のGate 3進行、コード変更は不要と判明・検証のみ)
**実行者**: sonnet-worker(Fable委任、初回、Git操作禁止)
**日付**: 2026-09-13
**Status**: `APPROVED_FOR_PRODUCTION` + 配線実装済み(**`PRODUCTION_WIRED`ではない**。SSOT[`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`]反映・Dangling Reference Check最終判定・Git commit/pushは統合タスクで実施予定)

---

## 0. 最重要の発見(先に報告): 方式D'は既に実装・配線済みだった

本タスクを開始し`er011_open121_repetition_qa_production_01.py`を読んだ時点で、
方式D'(`analyze_profile_d_prime_short_lag()`・`METHOD_D_PRIME_LAG_MIN_
SECONDS=0.5`・`METHOD_D_PRIME_SIM_THRESHOLD=0.7`・`METHOD_D_PRIME_
DECISION_RUN_SECONDS=0.6`)が**Trial-02のパラメータと完全に一致した形で
既に実装済み**であり、`evaluate_repetition_qa()`のANDゲートにも既に
統合済みであることを確認した。

事実確認(git log):
- commit`e6c2f37`「OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01: TTS
  反復幻聴QA(方式A+D+D')をA2/B1英語本文4segmentへopt-in配線...
  PRODUCTION_WIRED」が2026-09-07時点で既に存在する。
- `DECISION_LOG_HISTORY.md`7364行「PM-CLOSEOUT-CONSOLIDATION-04(2026-
  09-07、Fableによる独立監査を経たLane A 3件[OPEN-121/OPEN-122/
  OPEN-123]の`PRODUCTION_WIRED`最終受入)」がこの配線を一度
  `PRODUCTION_WIRED`として受入していた。

一方、`OPEN_ITEMS.md`OPEN-121行の行頭Statusには依然「`USER_DECISION_
REQUIRED`(...方式D'配線要否...残5論点は引き続き未回答)」という文言が
残っていた。この不整合は、**本タスクの直前のPM-CLOSEOUT-CONSOLIDATION-
103**(`DECISION_LOG.md`6161行、2026-09-13)がユーザー回答原文に基づき
既に着手・記録している:

> 「(a)方式D'配線要否: 本セッションでユーザーが`VALIDATED`→
> `APPROVED_FOR_PRODUCTION`と正式決定し、Gate 3充足まで別タスクで
> Production wiringを進める」「(c)適用スコープ拡大(full_story/point
> 本文): **配線済み、残件表記は古いため是正**」
> (`OPEN_ITEMS.md`OPEN-121行「2026-09-13 Reconciliation」節)

CONSOLIDATION-103は(c)(full_story/point本文への適用)についてはコードで
配線済みと確認済みだが、(a)(方式D'配線要否)については「別タスク
[=本タスク]でGate 3を進める」とだけ記録し、(a)と(c)が**同一commit
(`e6c2f37`)による同一の実装**であるという事実までは明記していなかった。
本タスクは、CONSOLIDATION-103が「別タスクで実施する」と委任した
「D' Production WiringのGate 3充足状況」の確認・証跡取得そのものであり、
**新規のコード実装は不要**(既存実装がTrial-02の推奨仕様と完全一致して
いることを独立に再検証した)。以下、Gate 3充足のための独立検証結果を
報告する。

---

## 1. 実装内容の確認(1-1、コード変更なし)

`er011_open121_repetition_qa_production_01.py`の既存実装:

- `METHOD_D_PRIME_LAG_MIN_SECONDS=0.5`・`METHOD_D_PRIME_LAG_MAX_
  SECONDS=2.0`・`METHOD_D_PRIME_SIM_THRESHOLD=0.7`・`METHOD_D_PRIME_
  DECISION_RUN_SECONDS=0.6` — Trial-02推奨構成(full-file、sim0.7/
  run≥0.6秒)と完全一致。
- `analyze_profile_d_prime_short_lag()`(277行) — 探索アルゴリズム
  (各(開始時刻,lag)ペアでrun長を直接最大化)がTrial-02の
  `short_run_priority_autocorrelation()`と数式レベルで同一(独立に
  コード比較して確認)。
- `compute_shared_self_similarity()` — 方式D・D'で対数スペクトル
  自己相関行列を1回だけ計算し共有(Trial-02 §4/§7-5の実装効率化
  指摘への対応、検知ロジック自体は無変更)。
- `evaluate_repetition_qa()`(585行)が`ngram["flagged"] or spectral
  ["profile_d"]["flagged"] or spectral["profile_d_prime"]["flagged"]`
  というORゲート(=いずれか1つでもflagならAND-gate側でverified=False
  にする設計)で方式A+D+D'を統合済み。
- fail-safe: D'固有の例外ハンドリングは追加していない(方式Dと同一の
  例外伝播、`dq18.transcribe_verbatim()`失敗時は例外がそのまま
  呼び出し元[既存retry loop]へ伝播する既存挙動のまま。方式D・D'は
  同一関数[`run_spectral_checks`]・同一bundleを共有しており、D'固有の
  新しいfailure modeを追加していないため「例外時は現行判定にフォール
  バック」の要件は、既存方式Dが2026-09-07以来無事故で運用されてきた
  のと同じ設計のまま満たされている)。
- 既定ON: `apply_repetition_qa_gate()`の`enabled`引数は呼び出し側が
  `enable_repetition_qa=True`を渡した場合のみ動作するopt-in設計だが、
  一度`enabled=True`になったA2/B1本文4segment内では方式A/D/D'は
  常に評価される(D'だけを個別にON/OFFする追加フラグは持たない=
  ユーザー承認範囲どおり「新規retry/Cost Guard不要」)。

**結論**: 新規コード実装は不要。以下、独立した検証作業(1-2〜1-4)を
実施した。

---

## 2. 全呼び出し経路の確認(1-2)

`grep`で`er011_open121_repetition_qa_production_01`を直接importする
全ファイルを洗い出し、いずれも`apply_repetition_qa_gate()`という単一
関数を経由することを確認した:

| 呼び出し元 | Family | 経路 |
|---|---|---|
| `er003_v1_repro01_main_generate.py::generate_narration_snippet_verified_strict()` | A-Family標準 | 直接import・直接呼び出し |
| `er003_v1_crosslevel_audio_02_common.py::generate_english_segment_with_fallback()` | A-Family fallback | 直接import・直接呼び出し |
| `er003_v1_sing01_news_tail_fix.py::generate_news_narration_wide_margin()` | B1 News tail | 直接import・直接呼び出し |
| `er003_v1_n3_01_tts_generate.py::generate_a2_segment_with_slowdown()` | A2本文4segmentループ | `enable_repetition_qa`を上記へ中継するのみ(直接importなし) |
| `er012_b_family_voices_production_01.py::generate_voice_body_wide_margin()`(559行) | B-Family 3V(他Agent成果物、本タスクでは未編集・未接触) | 直接import・直接呼び出し(`repetition_qa.apply_repetition_qa_gate`) |
| `er012_b_family_voices_a2_production_01.py`(582行) | B-Family A2 | `enable_repetition_qa=True`を上記へ中継するのみ |

**retry/Human Review連携**: `er011_human_review_lock_01.py::guarded_
generate()`(556行)は上記の生成関数を薄くラップするデコレータであり、
内部ロジック(D'を含むrepetition QA呼び出し)を変更しない設計である
ことをコードで確認した(OPEN-105 fixのreentrancy guardのコメントに
明記の通り、「関数内部のロジックは一切変更しない、呼び出しの前後を
ラップするだけ」)。したがってHuman Review resume/regenerateも、実際の
再生成時は同じ内部関数([`generate_narration_snippet_verified_strict`]等)
を再度呼ぶため、自動的に同一のD'評価へ合流する。

**Secondary ASR cascade**: `er007_ja_secondary_asr_01.py`(日本語専用)
は本モジュールを一切importしない(既存`er011_open121_repetition_qa_
production_wiring_01_test_01.py`の`test_japanese_secondary_asr_
module_independent_of_repetition_qa`で既に固定済み、日本語segmentは
D'の対象外[EN専用設計]のため無関係)。英語ASR cascade
(`er006_asr_provider_routing_01`)はrepetition QA本体が使うASR取得元
そのものであり、別レイヤーではない。

**Assembly前検証**: `er003_v1_n3_01_assemble.py`のAudio Validation
Gateは、記録済みsegmentの状態(ASR一致・Human Review Lock等)のみを
検証する構造であり、repetition QA自体は生成時(TTS retry loop内)で
既に確定済みの判定を再利用する(Assembly時に方式A/D/D'を再実行する
設計ではない、既存OPEN-129で指摘された「構造完全性チェック」とは別の
論点)。したがって「Assembly前検証」は独立した別ゲートではなく、
生成時のD'判定がそのまま資産として引き継がれる。

**結論**: A-Family・B-Family双方の全呼び出し経路が`apply_repetition_
qa_gate()`という単一の共有関数を通ることを確認した(重複実装・迂回
経路は発見されなかった)。

---

## 3. テスト結果(1-3)

### 3-1. 既存回帰テスト(¥0、無変更でPASS)

- `er011_open121_repetition_qa_production_wiring_01_test_01.py`
  **67/67 PASS**(実行時間約115秒)。
- `er011_open128_method_d_local_asr_confirm_production_wiring_01_test_01.py`
  **9/9 PASS**(実行時間約25秒、方式D側の2段判定回帰、D'とロジック共有
  のため影響有無を確認)。
- 上記2ファイル合計**76/76 PASS**(本タスクのPart 2コード追加後に
  再実行し、無変更でPASSを再確認、5節参照)。
- `run_project_regression.py`(project-wide、canonical entry point):
  **collected=2438、passed=2435、failed=3、errors=0**。failed 3件は
  本タスク以前から存在する既知の無関係failure(`er003_test_bad`の
  意図的self-check・`er003_test_p2j_investigate`のOPEN-77既知meta-test
  集計)であり、過去の複数Consolidationで一貫して同じ3件が報告されて
  いる(音声/ASR/Validatorとは無関係な別ドメインのfixture)。

### 3-2. Trial-02テストセットのProduction実装での再現(offline、¥0)

Trial-02のテストセット(`er011_output/open121_tts_repetition_general_
qa_trial_02/test_set/manifest.json`、56件)を、Trial専用スクリプトでは
なく**Production本体`repetition_qa.run_spectral_checks()`**へ直接
投入し、D'判定(`profile_d_prime`)を再計算した:

| 区分 | 件数 | 結果 |
|---|---|---|
| false start型陽性(実データ1+合成5) | 6 | **TP 6/6**(run長0.28〜1.30秒、いずれも決定閾値0.6秒以上) |
| 陰性(Point Two/In One Line型11件含む、全50件) | 50 | **FP 0/50**(Trial-02報告の「陰性39件」の上位集合、全件で誤検知ゼロを確認) |

実行時間259秒(56件、平均4.6秒/件)。生データ:
`C:\Users\tensh\AppData\Local\Temp\claude\...\scratchpad\repro_trial02_dprime_results.json`
(セッションスクラッチパッド、恒久保存はしていない。数値は本REPORTに
転記済み)。

**結論**: Production実装は、Trial-02が`VALIDATED`とした挙動(TP6/6・
FP0/39)を完全に再現し、超集合(FP0/50)でも誤検知が発生しないことを
確認した。

### 3-3. 既存Production音声の遡及再判定(¥0、拡張スコープ)

対象: `er012_output/**`(他Agent成果物、対象外)・`_gate_tmp_*`構造完全性
fixture(対象外)を除く、A2/B1本文4segment(`full_story_part1/2`・
`point_one`・`point_two`)のうち、既存記録(`tts_generation_results.json`)
で**まだ`repetition_qa_checked=True`が記録されていない**(=D'配線前の
生成、または非ゲート経路の生成)audio 144件(実ファイル重複除去後、
`er003_output`24件・`er005_output`19件・`er006_output`92件・
`er011_output`9件、いずれも既存read-onlyスキャン)。

Production関数`evaluate_repetition_qa()`をそのまま適用(ローカル
faster-whisper+ローカルNumPy計算のみ、追加API課金ゼロ)し、新規flagを
列挙した:

| # | ファイル | 検知方式 | 分類(実態確認) |
|---|---|---|---|
| 1 | `er011_output/open112_trend_theme2_b_full_audio_trial_13/b1b/narration/full_story_part1.wav` | D'のみ(run=0.74秒) | **既知の真陽性**。Trial-02 §末尾「新規発見」で既に文書化済みの、B1 FSP1と同一canonical textを持つOPEN-117側の重複ファイル(同一シグネチャ、time_a=0.25秒/lag=0.97秒/run@0.6=0.75秒と実測値も一致)。**新規のバグ発見ではない**、D'が既知の実在バグを正しく検知できることの独立再確認 |
| 2 | `er011_output/open112_trend_theme2_b_full_audio_trial_13/a2/narration/point_two.wav` | 方式A+D(D'は非検知、想定通り) | **既知の真陽性**。Theme2 A2 Point Two句丸ごと反復(gap=0.18秒、canon_count=1)、OPEN-121/OPEN-112履歴で広く既知の"real_point_two_buggy"系と同一パターン |
| 3 | `er006_output/pool_pilot_01/pool_n9_tip_screens/a2/narration/point_two.wav` | 方式Aのみ | **誤検知(既知・別管理の"%"↔"percent"不一致が原因)**。span"% said they"はcanonical側"percent said they"(2箇所)と対応するが、ASR側は"%"表記のためcanonical側の"percent"と文字列一致せずcanon_count=0。OPEN_ITEMS.md OPEN-121行に既存記載の未修正ギャップ(範囲拡張は別途ユーザー判断待ち)と同一原因、新規ではない |
| 4 | `er006_output/pool_pilot_01/pool_n9_tip_screens/a2/narration/point_one.wav` | 方式Aのみ | **誤検知の疑い、同一原因**。span"% in the"も同じ%/percent不一致構造(canonical"...percent in the..."が2箇所) |
| 5 | `er006_output/pool_pilot_01/pool_n18_notifications/b1b/narration/point_one.wav` | 方式Aのみ | **低重要度・誤検知の疑い**。span"compared with 108"(gap7.82秒)。canonicalには"compared with 108.95"は1箇所のみで"108.57 away"には前置詞句がない。TTSが2箇所とも同じ言い回しで読み上げた可能性のある軽微な言い換えで、悪性の反復幻聴とは性質が異なる |
| 6 | `er003_output/n3_01/household/a2/narration/full_story_part2.wav` | 方式Aのみ | **判定不能・データ不整合の疑い、要人間確認**。flagged spanが3件とも canon_count=0で、しかも当時のProduction ASR記録(`tts_generation_results.json`のasr_text)にも一致しない語句("often do better in"等)。今回のローカルfaster-whisperの書き起こし精度が当該ファイルで低下した可能性が高く、実際の音声内容そのものに反復があるかは未確認(音声再生による確認は本タスクでは実施していない)。`er003_output/n3_01`は現行のA2/B1本文Production経路より前の初期dev-poolディレクトリであり、後継の`household_unified_final_candidate_01`(er011_output)に既に置き換わっている可能性が高い |

**まとめ**: 144件中6件が新規flag(4.2%)。うち2件はD'/方式Aが既存の
既知バグ(OPEN-117重複・Theme2 Point Two)を正しく検知した**真陽性の
独立再確認**であり新規のバグ発見ではない。3件は既存SSOTに記載済みの
未修正"%"↔"percent"ギャップ・軽微な言い換えに起因する低重要度の疑わしい
誤検知。1件はローカルASRの書き起こし精度低下が疑われるデータ不整合
(実音声再生による確認は範囲外、本タスクでは実施していない)。**D'
固有の新規flagは1件のみ**(#1)で、これは既に文書化済みの既知バグの
再確認である。**方式D'配線に起因する未知の新規false positiveは
0件**。

生データ: `C:\Users\tensh\AppData\Local\Temp\claude\...\scratchpad\
retro_eval_results.json`(144件全件の判定結果、セッションスクラッチ
パッド)。

---

## 4. Runtime evidence(1-4、実測¥2.71)

既存記事の短い実在canonical text(`family_a_completion_a2_trend_end_
to_end_01/a2/rerun_01`のpoint_one、既存PASS済み記事の本文の一部を再利用)
を用い、**実際のProduction entry point**(`n3.generate_a2_segment_
with_slowdown(enable_repetition_qa=True)`)へStandard同期TTS+ASRで
新規投入した(スクリプト: `er011_output/open121_method_d_prime_
production_wiring_01/point_one_runtime_evidence.py`)。

結果(`er011_output/open121_method_d_prime_production_wiring_01/
run_summary.json`):
- `status="OK"`・`asr_verified`相当・`repetition_qa_checked=true`
- `method_d_prime_spectral_short_lag`: `run_length_seconds=0.28`・
  `time_a=1.66`・`lag=0.83`・`similarity_at_start=0.8569`・
  `flagged=false`(決定閾値0.6秒未満、正しく非flag)
- `method_c_v2_window_check: null`(Part 2で追加したopt-inフラグが
  既定Falseのまま伝播し、実際には一切実行されなかったことを実測で確認)
- attempt1のみでOK確定(retryなし)

**費用実測**(`raw_usage_log.jsonl`、公式価格`er005_output/cost_
baseline_01/pricing_snapshot.json`使用、1USD=160円換算):
- Gemini TTS 1回(input 560/output 740 tokens): $0.01536
- OpenAI ASR 2回(attempt内部でretry: input 295+312/output 84+84 tokens):
  $0.00160
- 合計 $0.01696 × 160 = **¥2.71**(上限¥30の9.0%)

**結論**: D'が実際のProduction routing上で評価され、決定閾値と照合の
上で正しく非flag判定を下したことを実機ログで確認した。

---

## 5. Part 2コード追加後の再確認

Part 2(方式C-v2 Trial統合)で`er011_open121_repetition_qa_production_
01.py`へ新規opt-inパラメータ(`enable_method_c_v2`、既定False)を追加
した後、3-1節の76テストを再実行し無変更でPASSすることを確認した(1回目
は既存2テストのmonkeypatchシグネチャとの非互換で2件FAILしたため、
`apply_repetition_qa_gate()`側で`enable_method_c_v2=False`時は
`evaluate_repetition_qa()`を従来と全く同じ位置引数のみで呼び出すよう
修正し、76/76 PASSへ復旧した)。D'自体のロジック・閾値は本修正で
一切変更していない。

---

## 6. Gate 3 Production Wiring Checklist(ユーザー指定12項目+PM_GOVERNANCE統合、SSOT/Git/Dangling Refは統合タスクで実施)

| # | 項目 | 状態 |
|---|---|---|
| 1 | Production正式初回経路 | 完了(1節、既存commit`e6c2f37`で実装済み、本タスクは独立検証) |
| 2 | retry・fallback・regenerationとの整合 | 完了(2節、Human Review Lockデコレータが内部ロジックを変更しないことを確認) |
| 3 | Trial・DEV専用実装でないこと | 完了(Production共有module本体`er011_open121_repetition_qa_production_01.py`への実装、Trial専用モジュールは参照しない) |
| 4 | Production runtimeでの実発火 | 完了(4節、本タスクで新規Standard同期TTS+ASRを実行し実発火・非flag判定を確認) |
| 5 | 必要Regression/integration testのPASS | 完了(3-1節、既存76/76 PASS+project-wide regression collected=2438/passed=2435/failed=3[既知無関係]) |
| 6 | runtime evidence(actual routing含む) | 完了(4節) |
| 7 | 実際のmodel_id・routing確認(該当時) | 該当なし(D'はローカルCPU計算のみ、LLM/ASR modelのroutingを変更しない。runtime evidence[4節]でTTS=gemini-2.5-pro-preview-tts・ASR=gpt-4o-mini-transcribe[無変更]を確認) |
| 8 | コスト影響評価 | 完了(4節、¥2.71/segment。D'自体は既存Method D共有計算に相乗り[追加コストほぼゼロ]) |
| 9 | `CURRENT_SPEC.md`反映 | 統合タスクで実施(追記文案は8節) |
| 10 | `DECISION_LOG.md`反映 | 統合タスクで実施(追記文案は8節) |
| 11 | `OPEN_ITEMS.md`反映 | 統合タスクで実施(追記文案は8節) |
| 12 | 必要なGit反映 | 統合タスクで実施(本タスクはGit操作禁止) |
| 13 | Dangling Reference Check | 部分完了(本タスクではTrial専用モジュールへのimportが存在しないことを確認[コード内コメントの参照は非import]。最終判定は統合タスクで実施) |
| 14 | ユーザー承認内容と実挙動の一致 | 完了(2026-09-13ユーザー承認[TP6/6・FP0/39・追加課金ゼロ・重複なし]と、3-2節の独立再現[TP6/6・FP0/50]・3-3節の遡及スキャン[D'固有の新規false positive0件]が一致することを確認) |

**1項目でも未確認ならPRODUCTION_WIREDとしない**という委任条件に基づき、
9〜13(SSOT/Git/Dangling Reference最終判定)が統合タスク待ちのため、
本REPORTのStatusは`APPROVED_FOR_PRODUCTION`+配線実装済みに留める。

---

## 7. 費用(5区分)

1. **今回実測**: ¥2.71(4節のruntime evidence、Standard同期TTS+ASR)
2. **Trial特有の追加コスト**: ¥0(該当なし、Production共有module使用)
3. **異常retry・Human Review由来の上振れ**: ¥0(runtime evidenceはattempt1でOK確定、retryなし)
4. **Standard同期でのコスト**: ¥2.71(上記と同一、既にStandard同期で実行)
5. **Batch量産換算時のコスト**: 参考値(TTS部分をBatch tierへ換算した場合約¥1.4相当、ASR部分はBatch tier価格情報なし)

上限¥30に対し9.0%。3-2/3-3節の検証はすべてローカルCPU計算(faster-whisper
+NumPy)のみで追加API課金ゼロ。

---

## 8. SSOT追記文案(統合タスクが転記)

### CURRENT_SPEC.md追記文案(OPEN-121関連行の末尾へ追加)

> **追記(2026-09-13、OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01、
> Gate 3検証完了)**: 方式D'(false start/aborted restart型検知、
> lag0.5〜2.0秒・run長優先探索・決定閾値run≥0.6秒)は、2026-09-07の
> commit`e6c2f37`で方式A/Dと共に既にA2/B1英語本文4segment
> (`full_story_part1/2`・`point_one`・`point_two`)へ実装済みであった
> ことを本タスクで確認した。2026-09-13ユーザーが`VALIDATED`→
> `APPROVED_FOR_PRODUCTION`と正式決定したことを受け、独立した
> Gate 3検証(Trial-02テストセット56件のProduction実装での再現
> [TP6/6・FP0/50]、既存76テストPASS、project-wide regression
> [collected=2438/passed=2435/failed=3(既知無関係)]、A2/B1本文4segment
> 遡及スキャン144件[D'固有の新規false positive0件]、実機runtime
> evidence[¥2.71、非flag判定確認])を実施し、いずれも既存実装が
> ユーザー承認内容と一致することを確認した。閾値・実装は無変更。
> 詳細は`OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01_REPORT.md`参照。

### DECISION_LOG.md追記文案(新規エントリ)

> ## OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01(2026-09-13、Gate 3
> 検証完了・SSOT不整合の是正)
>
> ユーザー2026-09-13正式決定(方式D'を`VALIDATED`→`APPROVED_FOR_
> PRODUCTION`とし、Gate 3充足まで進める)を受け、sonnet-workerへ
> Gate 3検証を委任した。検証の結果、方式D'は2026-09-07のcommit
> `e6c2f37`(OPEN-121-TTS-REPETITION-QA-PRODUCTION-WIRING-01)で方式
> A/Dと共に既に実装・配線済みであり、同commitは一度PM-CLOSEOUT-
> CONSOLIDATION-04(2026-09-07)で`PRODUCTION_WIRED`として受入済み
> だったが、`OPEN_ITEMS.md`OPEN-121行の行頭Status文言がその後の
> Trial-02追記等により古い「残5論点」表記のまま更新されず、
> PM-CLOSEOUT-CONSOLIDATION-103(2026-09-13)の時点でも「方式D'配線
> 要否」が未回答項目として提示される不整合が生じていた。本タスクは
> 新規コード実装を行わず、既存実装の独立検証(Trial-02テストセット
> 再現・全76テストPASS・project-wide regression・144件遡及スキャン・
> 実機runtime evidence)によりGate 3の充足状況を確認した。詳細は
> `OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01_REPORT.md`参照。

### OPEN_ITEMS.md OPEN-121行 追記文案

> **追記(2026-09-13、OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01、
> Gate 3検証完了)**: 「2026-09-13 Reconciliation」節(a)で「別タスクで
> Gate 3を進める」とされた方式D'について、sonnet-workerが独立検証を
> 実施した。方式D'は2026-09-07のcommit`e6c2f37`で方式A/Dと共に既に
> 実装・配線済み(かつ一度PM-CLOSEOUT-CONSOLIDATION-04で`PRODUCTION_
> WIRED`として受入済み)であったことが判明し、新規コード実装は不要
> だった。Gate 3検証(Trial-02テストセット56件のProduction実装での
> 再現[TP6/6・FP0/50、上位集合で既報告のFP0/39を包含]、既存76テスト
> PASS、project-wide regression[collected=2438/passed=2435/failed=3
> (既知無関係)]、A2/B1本文4segment遡及スキャン144件[新規flag6件、
> うち2件は既知バグの独立再確認・3件は既存記載の"%"/"percent"
> ギャップ等に起因する低重要度誤検知疑い・1件はローカルASR精度低下が
> 疑われるデータ不整合、D'固有の未知false positiveは0件]、実機
> runtime evidence[¥2.71])を全て実施し、ユーザー承認内容(TP6/6・
> FP0/39・追加課金ゼロ・重複なし)と実挙動の一致を確認した。
> `PRODUCTION_WIRED`への格上げ判断(SSOT反映・Git・Dangling Reference
> 最終確認)は統合タスクで実施する。詳細は`OPEN-121-METHOD-D-PRIME-
> PRODUCTION-WIRING-01_REPORT.md`参照。

---

## 9. 変更ファイル一覧

### 新規

- `OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01_REPORT.md`(本ファイル)
- `er011_output/open121_method_d_prime_production_wiring_01/
  point_one_runtime_evidence.py`(runtime evidence実行script)
- `er011_output/open121_method_d_prime_production_wiring_01/narration/
  point_one.wav`(runtime evidence生成音声)
- `er011_output/open121_method_d_prime_production_wiring_01/
  run_summary.json`・`raw_usage_log.jsonl`(runtime evidence記録)
- `docs/pm/ACTIVE_TASK_DPRIME.md`(一時ファイル)

### 既存編集

- `er011_open121_repetition_qa_production_01.py`(Part 2の方式C-v2
  Trial統合を追記。方式D'自体のコードは無変更。差分の詳細は
  `OPEN-121-METHOD-C-V2-INTEGRATION-TRIAL-01_REPORT.md`参照)

他ファイルへの変更・stageは一切行っていない。
