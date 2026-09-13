# OPEN-121-METHOD-C-V2-INTEGRATION-TRIAL-01

**管理ID**: OPEN-121-METHOD-C-V2-INTEGRATION-TRIAL-01
**種別**: 試作期統合Trial(**Production正式採用ではない**、opt-inフラグ既定OFF)
**実行者**: sonnet-worker(Fable委任、初回、Git操作禁止)
**日付**: 2026-09-13
**Status**: `EVALUATED`(統合実装+副作用洗い出し完了、Gate 1のStatus分類[REJECTED/VALIDATED/USER_DECISION_REQUIRED]はFableが判定)

---

## 0. 前提

ユーザー2026-09-13正式決定(`DECISION_LOG.md` PM-CLOSEOUT-CONSOLIDATION-
103エントリ、項目4):「方式C-v2(gap<0.5秒即時言い直し検知)は試作期に
統合して副作用・既存QAとの競合を洗い出す対象として扱う。ただしD'の
ようなProduction正式採用ではない。既存Trial結果を無駄に繰り返さず、
必要なのは統合時の副作用・回帰確認のみ」。本タスクはこの決定に従い、
既存Trial-01結果(TP2/12・FP0/26)の再Trialは行わず、**統合実装の
副作用・競合洗い出し**に専念した。

---

## 1. 統合実装(2-1)

対象: `er011_open121_repetition_qa_production_01.py`(D'と同一module、
Trial専用モジュール`er011_open121_tts_repetition_general_qa_trial_
01.py`は一切importしない)。

- `METHOD_C_V2_WINDOW_CONFIGS=((8.0,4.0),(12.0,6.0))`・
  `METHOD_C_V2_MIN_WORDS=3`(Trial-01と同一設定)。
- `_text_ngram_repetition_c_v2()`(新規): Trial-01の`_text_ngram_
  repetition()`と同一設計だが、本module既存の正規化関数
  (`_normalize_tokens`/`find_repeated_spans`/`_canonical_repeat_
  count`、ダッシュ境界統一・数詞↔算用数字同値化・em/en dash処理を
  含む対称正規化層[OPEN-127/RECONCILE-02/03で`PRODUCTION_WIRED`済み]
  を再利用)。Trial-01の素朴な実装より誤検知に強い版になっている。
- `run_method_c_v2_window_check()`(新規): 音声を window設定ごとに
  切り出し(`tempfile`で一時wav書き出し)、既存Production ASR経路
  `er006_asr_provider_routing_01.transcribe()`を各windowへ個別に
  呼び出す(連結しない、Trial-01のnaive連結v1のfalse reject 50%設計
  欠陥を回避)。いずれかのwindow・いずれかのconfigでflaggedなら全体
  flagged=True。
- `evaluate_repetition_qa()`・`apply_repetition_qa_gate()`へ新規kwarg
  `enable_method_c_v2`(既定`False`)を追加。**既存の4呼び出し元
  (`er003_v1_*.py`)はこの引数を一切渡していない**(コード上探索して
  ゼロ件を確認)ため、Production正式経路では常にFalseのまま、
  従来通り一切実行されない(D'と同じ既定OFF opt-inパターン、OPEN-122
  Connected Speech Equivalence Layerと同一設計思想)。
- 後方互換性: `enable_method_c_v2=False`(既定)の場合、
  `apply_repetition_qa_gate()`は`evaluate_repetition_qa()`を**従来と
  全く同じ位置引数のみ**で呼び出す(新kwargを渡さない)。既存テスト
  (`er011_open121_repetition_qa_production_wiring_01_test_01.py`)の
  2件が`evaluate_repetition_qa(path, canonical_text, language="en")`
  という固定シグネチャでmonkeypatchしていたため、これを壊さないための
  実装上の配慮(D'導入時にはなかった新しい後方互換性配慮点)。

**Production採用ではないことの担保**: `enable_method_c_v2`はコード上
どこからもTrueで呼ばれない(既存4呼び出し元・Human Review Lock
デコレータ・B-Family呼び出し元のいずれも本引数を渡していない)。実際に
動作させるには本タスクのテスト・オフライン検証スクリプトから明示的に
Trueを渡す必要がある。

---

## 2. 副作用・競合の洗い出し(2-2、¥0 offline)

### 2-1. Trial-01テストセットの再現(既存Azure/ASR呼び出し結果を再利用、¥0)

Trial-01の既存生データ`method_c_windowed_asr.json`(過去に実際の
Production ASR経路で取得済みのwindow別transcript)を読み取り専用で
再利用し、各windowのtranscriptを**本タスクで新規実装した
`_text_ngram_repetition_c_v2()`**へ独立に(連結せず)投入した。新規の
ASR API呼び出しは一切行っていない(¥0)。

| 区分 | 件数 | 結果 |
|---|---|---|
| 陽性(gap<0.5秒型、Point Two/In One Line) | 2 | **TP 2/2**(`real_point_two_buggy`・`real_in_one_line_buggy`、いずれもwin12s/hop6s configでflagged) |
| 陽性(gap>10秒型・word/phrase/sentence合成、C-v2の設計対象外) | 10 | 0/10(想定通り、C-v2は近接gapのみ対象) |
| 陰性(既存PASS再利用+意図的反復+自然hallucination試行) | 26 | **FP 0/26** |

Trial-01報告(TP2/12・FP0/26)と完全一致。本Production統合実装
(既存の対称正規化層を経由する新しい`_text_ngram_repetition_c_v2()`)
でも同一結果が再現され、対称正規化層の追加が既存の検知能力を損なって
いないことを確認した。

### 2-2. 遡及コーパスでの副作用分析(¥0 offline、近似手法・限界を明記)

**方法論上の重要な近似**: `run_method_c_v2_window_check()`本体は音声
clipごとに独立ASR呼び出しを行う設計(実際に動かせば追加API課金が
発生する)。¥0の制約下で「D'のGate 3検証(`OPEN-121-METHOD-D-PRIME-
PRODUCTION-WIRING-01_REPORT.md`3-3節)と同じ144件のコーパス」に対する
副作用を洗い出すため、本節では**既に無料で取得済みのfull-file
word-level ASR結果(`dq18.transcribe_verbatim()`、方式Aが使うものと
同一)を時間窓で分割し、各窓内のtoken列だけで独立にn-gram判定を行う
代理指標**を用いた。真のC-v2(window単位で独立に音声を切り出し
再ASRする)とは、window境界でのASR認識精度劣化(文脈喪失によるミス
書き起こし)を再現できない点で異なる**近似**であることを明記する。

対象: D'のGate 3検証と同一の144件(A2/B1本文4segment、`er012_output`・
`_gate_tmp_*`構造完全性fixtureを除く、`repetition_qa_checked=True`が
未記録の既存audio)。

| 指標 | 件数 |
|---|---|
| 対象総数 | 144 |
| C-v2代理指標でflagged | 3 |
| (参考)方式A(full-file、非window)でflagged | 5 |
| C-v2代理指標でflaggedだが方式A(full-file)ではflaggedでない**新規** | **0** |

C-v2代理指標がflagした3件はいずれも方式A(full-file)が既にflagして
いる集合の**部分集合**だった(`er011_output/open112_trend_theme2_b_
full_audio_trial_13/a2/point_two.wav`[Theme2 Point Two、gap=0.18秒、
既知バグ]・`er003_output/n3_01/household/a2/full_story_part2.wav`
[D'-Gate3 REPORT 3-3節#6、ローカルASR精度低下疑いのデータ不整合]・
`er006_output/pool_pilot_01/pool_n9_tip_screens/a2/point_one.wav`
[D'-Gate3 REPORT 3-3節#4、既存記載の"%"↔"percent"不一致])。

**方式A/D/D'との重複・競合**:
- C-v2は方式Aが検知する句・文単位反復のうち、gapが**window長以内
  (8秒または12秒)** に収まるサブセットのみを独立に再検知する構造の
  ため、原理的に方式A(full-file)の**部分集合**にしかなり得ない
  (本分析で実測した通り、新規flagは0件)。gapがwindow長を超える型
  (方式Aが主に対象とするPoint Two/In One Line型の一部、gap8〜10秒超)
  はC-v2の設計上の対象外。
- 方式D/D'(音響波形ベース)とは検知原理が異なる(text-token一致 vs
  音響類似度)ため、同一箇所を複数方式が独立に検知する場合はあるが
  (例: Theme2 Point Two、方式A・D・C-v2代理指標いずれもflag)、
  「判定順序依存の競合」は発生しない(`evaluate_repetition_qa()`は
  OR統合のため、いずれか1つでもflagすれば全体flagged=Trueとなり、
  判定順序に依存しない)。
- **処理時間増**: C-v2を有効化した場合、window数×config数
  (8秒/4秒hopで概ね音声長/4+1窓、12秒/6秒hopで音声長/6+1窓)だけ
  追加のASR API呼び出しが発生する(Trial-01実測: 平均約6.2秒/件の
  追加レイテンシ、既存ASR呼び出し約8倍)。既定Falseのため現状の
  Production latencyへの影響はゼロ。
- **既存QA(Human Review Lock 3回NG→STOPPED)への影響**: `enable_
  method_c_v2`は他の全ゲートと同じ`verified`変数への単純なAND追加
  であり、新規のretry回数・新規のCost Guard・新規のLock遷移ロジック
  を一切追加していない(D'と同一のANDゲート構造)。有効化した場合、
  C-v2がflagしたsegmentは既存の`PRODUCTION_MAX_TTS_ATTEMPTS`(3回)
  予算内でretryが発生し、上限到達後は既存のSTOPPED→Human Review Lock
  自動遷移にそのまま合流する(新しいSTOPPED経路を作っていない)。

生データ: `C:\Users\tensh\AppData\Local\Temp\claude\...\scratchpad\
retro_cv2_proxy_results.json`(144件全件、セッションスクラッチパッド)。

---

## 3. テスト・回帰確認

- 統合実装後、既存76テスト(`er011_open121_repetition_qa_production_
  wiring_01_test_01.py`67件+`er011_open128_method_d_local_asr_
  confirm_production_wiring_01_test_01.py`9件)を再実行し**76/76 PASS**
  (`OPEN-121-METHOD-D-PRIME-PRODUCTION-WIRING-01_REPORT.md`5節参照、
  同一実行)。
- `run_project_regression.py`: **collected=2438、passed=2435、
  failed=3(既知無関係)、errors=0**(D' Gate3検証と同一実行、C-v2
  追加コードを含めた状態でのproject-wide regression)。
- C-v2専用の新規テストファイルは追加していない(Production採用が
  未確定なTrial統合コードのため、正式なunittest.TestCase形式の
  回帰テストは、Production採用判断後に追加する方が適切と判断。
  代わりに本タスクの2-1/2-2節のオフライン再現・分析スクリプトで
  動作を直接検証した)。

---

## 4. Gate 1判定材料(判定語自体はFableへ)

| 観点 | 結果 |
|---|---|
| 有効性(gap<0.5秒型の検知) | TP 2/2(2-1節、Trial-01結果を完全再現) |
| 誤検知(既存陰性26件) | FP 0/26(2-1節) |
| 適用範囲の広さ | 狭い(gap>10秒型・false start型は非対象、Trial-01/02から変化なし) |
| 既存方式との重複 | 部分集合関係のみ(2-2節、新規flag0件、判定順序非依存) |
| 追加コスト・レイテンシ | 有効化時のみ発生(既定Falseで¥0、有効化するとwindow数×config数のASR呼び出し追加) |
| 既存retry/Cost Guard/Human Review Lockとの整合 | 整合(新規機構を追加していない、D'と同一ANDゲート構造) |
| Production採用に必要な追加確認 | (1) 実音声でのwindow単位ASR呼び出しによる真のruntime evidence(本Trialは¥0制約のためfull-file ASRからの代理指標のみ)、(2) Cost Guard会計(`asr_calls_this_call`カウント)がwindow分割分を正しく計上する拡張(Trial-01 §4で既に指摘済みの既知ギャップ、未着手)、(3) 適用範囲拡大の要否(現状D'と同じA2/B1本文4segment想定) |

---

## 5. 費用(5区分)

1. **今回実測**: ¥0(既存キャッシュ済みTrial-01 ASR結果の再利用+ローカルfaster-whisper計算のみ)
2. **Trial特有の追加コスト**: ¥0
3. **異常retry・Human Review由来の上振れ**: ¥0(該当なし、offline検証のみ)
4. **Standard同期でのコスト**: ¥0(実際にC-v2を有効化した実行は行っていない)
5. **Batch量産換算時のコスト**: 未評価(Production採用判断後、実際の有効化コスト[window数×config数のASR呼び出し]を実測する必要あり)

---

## 6. 変更ファイル一覧

### 新規

- `OPEN-121-METHOD-C-V2-INTEGRATION-TRIAL-01_REPORT.md`(本ファイル)

### 既存編集

- `er011_open121_repetition_qa_production_01.py`(方式C-v2 Trial統合。
  新規定数`METHOD_C_V2_WINDOW_CONFIGS`/`METHOD_C_V2_MIN_WORDS`、新規
  関数`_text_ngram_repetition_c_v2()`/`run_method_c_v2_window_
  check()`、`evaluate_repetition_qa()`/`apply_repetition_qa_gate()`
  への新規opt-in kwarg`enable_method_c_v2`[既定False]追加。既存
  呼び出し元4箇所は本引数を一切渡していない。新規import: `er006_asr_
  provider_routing_01 as asr_routing`・`os`・`tempfile`)

他ファイルへの変更・stageは一切行っていない。

---

## 7. USER_DECISION_REQUIRED(将来のProduction採用判断が必要な場合)

1. 方式C-v2をProduction正式採用するか(`APPROVED_FOR_PRODUCTION`)。
   採用する場合の適用範囲(D'と同じA2/B1本文4segmentか)。
2. 採用する場合、2-2節「(2)」のCost Guard会計拡張(window分割分の
   ASR呼び出し計上)を先に実施するか。
3. 採用する場合、真のwindow単位ASR呼び出しによる実機runtime evidence
   (少額のAPI課金を伴う)取得を別タスクで実施してよいか。

いずれも本タスクでは判断・実装していない(試作期統合・副作用洗い出し
のみが委任範囲)。
