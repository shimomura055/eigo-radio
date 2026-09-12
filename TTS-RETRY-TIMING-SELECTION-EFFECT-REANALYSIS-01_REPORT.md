# TTS-RETRY-TIMING-SELECTION-EFFECT-REANALYSIS-01

## 要点(5行)
1. 「最初の3回attemptが全てNGだった事例」に母集団を限定し、4回目attemptのPASS率を即時(<150秒, N=1)と非即時(>=150秒, N=7)で比較したが、当該母集団**8件全件(100%)が人的介入(明示的`approve_regenerate()`呼び出し7件・原稿差し替え1件)を伴う**ため、時間経過単独の効果を推定できない(構造的confound。自動retryはmax_attempts到達で必ず停止する実装のため、4回目以降は常に人間の明示的操作を要する)。
2. 数値上は非即時PASS率42.9%(3/7) vs 即時0%(0/1、N=1で無情報)、Fisher両側p=1.0で有意差なし。位置を限定しない副分析(連続NG>=3の全position、N=15)でも非即時36.4%(4/11) vs 即時0%(0/4)、p=0.5165、こちらも15件中15件(100%)が同じ介入confound。
3. 選別効果は確かに存在する(素朴集計: 1回NG後69%→2回NG後17%→3回以上NG後27%)が、位置を一意化(最初の3回全NG→4回目のみ)すると非即時群のPASS率(36-43%)は素朴3+バケツ値(27%)より高く、「連続NGが即座に悪化を意味する」という単純解釈は支持されない。
4. タオルB1 `full_story_part1`は今回のreanalysis対象母集団にも含まれる(gap=2716秒、4回目NG)。「2022 survey欠落」解消は既存報告で「時間経過ではなく`approve_regenerate()`人的介入」と既に分類済みであり、本reanalysisもこの結論を追認する(1事例での時間効果断定はしない)。
5. Closeout: **REJECTED**(「時間を空けるretry」をProduction仕様候補として今回採用しない。ただし「効果が存在しない」という意味のREJECTEDではなく、N不足[主分析N=8・副分析N=15、いずれも介入なしサンプル0件]と構造的confoundにより効果の有無自体が判定不能なため)。

---

## データ構築

- 入力: `er011_output/tts_retry_timing_monitor_01/observations.jsonl`(483件、既存script`er011_tts_retry_timing_monitor_01.py`を無改変で再実行し最新化)、`er011_output/tts_retry_cooldown_analysis_01/cooldown_pairs.jsonl`(74件、既存script`er011_tts_retry_cooldown_monitor_01.py`を無改変で再実行し最新化)。両scriptとも冪等・API呼び出し0円。実行結果は再実行前と同一件数で、新規Trialや追加attemptは発生していないことを確認した。
- 新規script`er011_tts_retry_selection_effect_reanalysis_01.py`(読み取り専用、API呼び出しなし)を作成し、`level_dir+segment_id`単位でsegmentをグループ化、`sequence_index_in_group`順にソートしてattempt系列を再構築した。
- 「最初の3回attemptが全てNG」母集団の抽出: グループ内で1,2,3番目のattemptが全て`verified=False`であり、かつ4回目attemptが存在しその直前gap_secondsが既知の事例を機械抽出。該当**8件**(全483 attempt・361 distinct segment groups中)。
- 4回目attempt前の人的介入判定:
  - 機械検出可能な信号: 3回目→4回目間のroute/voice/model変化。
  - 機械検出不能な信号(個別script監査で特定、`INTERVENTION_EVIDENCE`辞書にハードコード): `review_lock.approve_regenerate()`の明示的呼び出し(7件で確認)、原稿本文の差し替え(1件、`textfix.py`)。
  - 構造的事実: 本システムの自動retryループは`max_attempts`到達で必ず停止する実装のため(`generation_path`判定ロジック、既存script準拠)、4回目以降のattemptは**必ず**人間が別scriptを明示的に再実行して発生する。よってこの母集団では機械的にも`generation_path=manual_regenerate_beyond_loop_cap`が8/8件で成立する。

---

## 主分析: 「最初の3回全NG→4回目」母集団(N=8)

| 群 | N | PASS | PASS率 | Wilson 95%CI |
|---|---|---|---|---|
| 即時(<150秒) | 1 | 0 | 0.0 | [0.0, 0.7935] |
| 非即時(>=150秒) | 7 | 3 | 0.4286 | [0.1582, 0.7495] |

- 差: 42.9ポイント、Fisher両側検定 p=1.0、オッズ比0.4286(0セルありHaldane-Anscombe補正、参考値)。
- **N=1の即時群は本質的に無情報**(1件の結果だけで比率を語れない)。p=1.0はこのN=1に強く引きずられており、「有意差なし」は「効果がない」ことの証拠にはならない(指示どおり、有意差なし=効果なしとは断定しない)。

### 8件の内訳(全件記載、隠蔽なし)

| segment | gap | bucket | 4回目結果 | route変化(3→4) | 特定した介入 |
|---|---|---|---|---|---|
| kp_new_normal | 3s | 即時 | NG | なし | 意図的diagnostic parameter sweep(2種のroute設定を試す診断run) |
| point_one(household FACT-03) | 567s | 短 | PASS | なし | **原稿本文差し替え**(`textfix.py`、OPEN-138ユーザー決定に基づく) |
| kp5_ja_charon | 2350s | 中 | NG | あり(minimal_fallback→standard) | 明示的`approve_regenerate()`+route変更 |
| full_story_part2(タオルB1B) | 2466s | 中 | NG | なし | 明示的`approve_regenerate()` |
| full_story_part1(タオルB1B) | 2716s | 中 | NG | なし | 明示的`approve_regenerate()` |
| full_story_part1(news CAR-T) | 51635s | 長 | PASS | なし | 明示的`approve_regenerate()` |
| meaning_4 | 71819s | 長 | PASS | あり(minimal_fallback→standard) | 明示的`approve_regenerate()`+route変更 |
| comment_2 | 75332s | 長 | NG | あり(minimal_fallback→standard) | 明示的`approve_regenerate()`+route変更 |

**母集団8件中8件(100%)が人的介入を伴う。**「介入なし」副分析はN=0のため統計計算不能。指示4項が想定していた「非即時群だけが介入ありで比較不能」というケースよりも状況は厳しく、**即時群を含む全群が介入ありで比較不能**。

証拠ファイル(抜粋、詳細は`er011_output/tts_retry_selection_effect_reanalysis_01/strict_population_cases.jsonl`):
- `er011_output/open138_household_fact03_b1b_minimal_fix_02/textfix.py`(point_one本文差し替え)
- `er011_discovery_generalization_towels_trial_11_audio_02_resume_human_review.py`(comment_2/meaning_4のapprove_regenerate)
- `er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py`(full_story_part1/2のapprove_regenerate)
- `er011_family_a_completion_a2_trend_end_to_end_01_run.py`(kp5_ja_charonのapprove_regenerate)
- `er011_news_stage3_new_theme_ledger_trial_09_b1b_regen01_full_story_part1.py`(news CAR-Tのapprove_regenerate)
- `er011_output/tts_attempt_audio_retention_wiring_01/evidence01/a2/audit/review_lock_state.json`(kp_new_normalの診断run記述)

---

## 副分析

### 副分析1: 介入なしに限定
N=0(上記の通り、8件全件が介入あり)。統計計算不能。「時間効果単独」を主分析からは推定できない。

### 副分析2: 位置を4回目に限定しない広義母集団(連続NG回数>=3、全position、N=15)
既存`cooldown_pairs.jsonl`の`consecutive_ng_before_bucket=="3plus"`行(種別B品質NGのみ)をそのまま再利用。

| 群 | N | PASS | PASS率 |
|---|---|---|---|
| 即時 | 4 | 0 | 0.0 |
| 非即時 | 11 | 4 | 0.3636 |

Fisher両側p=0.5165。この15件も**15/15件(100%)がmanual_regenerate_beyond_loop_cap**であり、主分析と同一の構造的confoundを抱える(同一segmentの4,5,6回目attemptが重複計上されるため主分析ではないが、参考値として傾向は一致)。

### 副分析3: failure type別(参考値、N不足)
8件中6件の直前(3回目)ng_subtypeが`content_mismatch_or_word_omission`、1件が`repetition_or_disfluency_flagged`(full_story_part2の途中経過)、1件が`tts_generation_content_failure_non_infra`(kp_new_normal)。即時群がkp_new_normalの1件のみのため、failure type別の即時 vs 非即時比較はどのタイプでも成立しない(N<2)。統計化せず参考値扱いとする。

---

## 選別効果の可視化

| 連続NG回数 | N | PASS率 | Wilson 95%CI |
|---|---|---|---|
| 1回後 | 43 | 67.4% | [52.5%, 79.5%] |
| 2回後 | 12 | 16.7% | [4.7%, 44.8%] |
| 3回以上後(位置不問、素朴集計) | 15 | 26.7% | [10.9%, 52.0%] |

対して、母集団を一意化した主分析(最初の3回全NG→4回目のみ、N=8)の非即時群PASS率は**42.9%**であり、素朴な「3回以上後」集計値26.7%より高い。これは、素朴集計には同一の難しいsegment(例: comment_2は4・5・6回目全てNGでこのバケツに3回計上)が繰り返し出現し、真の困難度以上に見かけ上のPASS率を押し下げていることを示唆する。すなわち「連続NG回数が増えると次のPASS率が下がる」という素朴な傾向のうち、少なくとも一部は選別効果(同じ難しい事例の反復計上)で説明できる。ただし本reanalysisのN(8件・15件)自体も小さく、「選別効果が主要因である」と断定するにはこれも根拠不十分である。

---

## 観測例: タオルB1 `full_story_part1`

- take1〜3(N=3)連続NG、いずれも2022 survey文の丸ごと欠落(TRUE_CONTENT_MISMATCH)。
- take4(gap=2716秒=中bin)は結果NG。ただしtake4以降、survey文の欠落自体は解消し、take5で新たな別の残存差分(has→had、語差型TRUE_CONTENT_MISMATCH)が発生(既存`FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-RECONCILE-01_REPORT.md` Part A/B参照)。
- 既存報告で「時間経過ではなく`review_lock.approve_regenerate()`の明示的人的介入」と既に分類済み。本reanalysisもこの分類を追認する。1事例のみでの時間効果断定はしない。

---

## 最終回答

**A. 事例難易度を揃えた後でも、時間を空けた群の4回目PASS率は高いか**
数値上は高い(非即時42.9% vs 即時0%、副分析でも非即時36.4% vs 即時0%)。ただし即時群のNが極端に小さい(主分析N=1、副分析N=4)ため、この差が真の時間効果を反映しているのか単なる偶然かを判定できるだけの精度がない。

**B. 差は統計的に有意か**
いいえ。Fisher正確検定は主分析p=1.0、副分析p=0.5165で、いずれも有意水準に遠く及ばない。ただし指示のとおり、これを「効果なし」の証拠とは解釈しない(N不足で検出力がほぼゼロのため、有意差なしは無情報に近い)。

**C. 人的介入を除いた場合でも傾向は残るか**
検証不能。主分析母集団8件・副分析母集団15件のいずれも100%が人的介入(明示的`approve_regenerate()`または原稿差し替え)を伴い、介入なしの自然発生サンプルが即時・非即時のどちらの群にも1件も存在しない。

**D. 現時点で「時間を空けるretry」を正式仕様候補にするだけの根拠があるか**
ない。理由: (1)主分析N=8は極小、(2)母集団の100%が人的介入を伴い時間効果と介入効果が完全に交絡、(3)Fisher p値は有意水準に遠く及ばない、(4)本システムのアーキテクチャ上、`max_attempts`超のattemptは常に人間の明示的操作を要するため、この構造を変えない限り「介入なしで時間だけ空いた自然発生の4回目retry」は今後も自然には蓄積されにくい。

**E. 根拠不足なら、何件・どの条件の自然発生データが今後必要か**
検出力計算(alpha=0.05、power=0.80、非即時PASS率を現状データの中間的丸め値40%に固定、正規近似・参考値):

| 即時PASS率(仮定) | 非即時PASS率(仮定) | 差(ポイント) | 必要N/群 |
|---|---|---|---|
| 10% | 40% | 30 | 29 |
| 20% | 40% | 20 | 79 |
| 30% | 40% | 10 | 354 |

想定される効果量(20〜30ポイント差)であれば、各群29〜79件程度の「介入なし・自然発生」4回目観測が必要。現状は主分析・副分析とも介入なしサンプルが0件のため、この必要件数に対して現在の有効サンプルはゼロ。追加で必要な条件: (1) 人間がtext/設定を一切変えずに`approve_regenerate()`のみを実行する自然な運用ケースが、即時側・非即時側の両方で複数回発生すること、(2) それを人工的にサンプル数目的で増やすことは本タスクの「追加Trial禁止」原則の範囲外の運用変更でありPM/ユーザー決定が必要、(3) 人工的に増やさない場合は通常運用でのHUMAN_REVIEW_REQUIRED到達頻度に依存し、現在のペースでは目安件数への到達に相当の期間を要すると見込まれる(具体的月数の推定は本タスクの範囲外)。

---

## Closeout

- **判定: REJECTED**(「時間を空けるretry」をProduction仕様候補として今回採用しない、という意味。「時間経過に効果が存在しない」という主張ではない。N不足・構造的confoundにより効果の有無自体が判定不能なため、有意差なし=効果なしとは結論しない)。
- N不足: 主分析N=8(介入なし0件)、副分析N=15(介入なし0件)。
- 交絡: システム構造上(`max_attempts`到達で自動retry停止)、4回目以降のattemptは常に人的介入を伴う。現行ログに「介入なしで時間だけ空いた自然発生の4回目retry」は存在しない。
- 選別効果: 位置を一意化すると非即時群PASS率(36〜43%)は素朴な「3回以上後」集計値(27%)より高く、素朴集計の低下傾向の一部は同一困難segmentの重複計上(選別効果)で説明できる可能性が高いが、これもN不足のため断定はしない。

---

## 出力・証跡パス
- 新規script: `er011_tts_retry_selection_effect_reanalysis_01.py`(冪等・API呼び出しなし、2回連続実行で出力バイト同一を確認済み)
- 出力: `er011_output/tts_retry_selection_effect_reanalysis_01/strict_population_cases.jsonl`(8件)、`broader_3plus_cases.jsonl`(15件)、`summary.json`、`summary.md`
- 再実行して最新化した既存入力: `er011_output/tts_retry_timing_monitor_01/observations.jsonl`(483件、件数不変)、`er011_output/tts_retry_cooldown_analysis_01/cooldown_pairs.jsonl`(74件、件数不変)。両script本体は無改変。
- 参照した既存REPORT: `TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01_REPORT.md`、`FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-RECONCILE-01_REPORT.md`
- 本タスクでの変更: 上記1新規script・4新規出力ファイル・本REPORTのみ。SSOT(`CURRENT_SPEC.md`等)・`docs/pm/`・Production retry/QAコードは無変更。API呼び出し・TTS/ASR生成は0件(¥0)。
