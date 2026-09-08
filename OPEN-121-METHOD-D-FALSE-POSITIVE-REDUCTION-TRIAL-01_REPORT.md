# OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01_REPORT

管理ID: OPEN-121-METHOD-D-FALSE-POSITIVE-REDUCTION-TRIAL-01(Fable委任、Sonnet
実行)。**Trial(Production変更なし)**。Gate 1判定: 詳細は末尾「Gate 1分類」。

## 1. 背景(ユーザー決定 2026-09-08)

OPEN-121方式D(スペクトル自己相関、Production既定閾値run長>=0.12秒、
sim閾値0.85)で既存PASS音声517件(en本文、既知事例除く)中23件がflag。
ユーザーが23件全件を実試聴し、真の重複8件(run長0.16〜0.32秒、既知バグ
「Point Two BUGGY」「In One Line BEFORE_FIX」の再現)と、正常音声への誤flag
15件(run長0.12〜0.16秒)に確定した(根拠:
`OPEN-121-METHOD-D-FLAG23-REVIEW-ARTIFACT-01_REPORT.md`、
`OPEN-121-METHOD-D-FLAG15-REVIEW-ARTIFACT-02_REPORT.md`)。Production閾値は
このTrial結果とユーザー判断が出るまで変更しない。

## 2. 目的

真の重複検知能力(TP8/8維持)を落とさず、方式D単体の誤flag(FP15件)を
減らす候補を比較する。単純な閾値引き上げのみを前提にせず、追加特徴量・
方式A/D'との役割分担も検討する。

## 3. データセット・方法(費用¥0、再利用の理由)

- **positive controls(TP=8)** / **negative controls(FP=15)**:
  `er011_output/method_d_flag23_review_01/classification_table.json`の
  `classification`を再利用(`真の重複(証拠あり)`=TP、それ以外=FP。
  「判断困難」1件を含む15件は2026-09-08にユーザーが全件false positiveと
  確定済み)。追加試聴・API呼び出しは行っていない。
- **background(517件)**: `er011_output/open121_existing_audio_dprime_sweep_01/
  results/production_params_reclassification_02.json`のmain_rows(既存sweep
  で計算済みのd_run_at_sim0.85・a_flagged等)をそのまま再利用。
- **計算コスト最小化の根拠(重要)**: 方式Dの候補ペア選定(top-k類似度)は
  sim閾値・run閾値に依存しない(`method_d.json`のtop_matchesのtime_a/
  time_b/lagをそのまま使える)。run長は対数スペクトル自己相関行列
  (`compute_shared_self_similarity()`、Production無変更import)さえあれば
  任意のsim閾値で高速に再計算できる。**スポットチェックで、この高速再計算
  値がProduction記録値と完全一致することを確認済み**(`candidate_b_...json`
  の`sanity_check_mismatches_vs_recorded_sim0.85`が空配列)。これにより
  O(n^2)の候補生成(23件の元計算で計185.96秒相当)をやり直さずにsim閾値
  スイープを行えた。
- **517件全件の重い再計算をしなかった理由**: 閾値を現状より「引き上げる」
  方向の候補(run閾値↑、sim閾値↑)は、現状flag対象の23件の**部分集合**しか
  生まないことが数学的に自明(判定条件がより厳しくなるだけなので、現状
  非flagの494件から新規flagが発生することはあり得ない)。この前提のもと、
  517件全件のO(n^2)再計算(推定合計約42分相当、元sweep実測値`elapsed_seconds`
  合計2518秒から外挿)を回避した。
- **候補(c)のみ新規ローカル計算**: 23件に対しfaster-whisper(ローカルCPU、
  `er008_disfluency_qa_18.transcribe_verbatim()`既存モジュール無変更import)
  でword-level timestampsを取得した(実測合計約116秒)。追加API課金なし。

## 4. 候補一覧と評価

### 候補(a): run閾値のみ変更(sim=0.85固定)

| run閾値(秒) | TP保持 | FP残存(誤検知) |
|---|---|---|
| 0.12(現状) | 8/8 | 15/15 |
| 0.14 | 8/8 | 9/15 |
| 0.16 | 8/8 | 2/15 |
| 0.17 | 6/8 | 1/15 |
| 0.18〜0.25 | 6/8 | 0/15 |
| 0.30 | 4/8 | 0/15 |

**TP8/FP0を同時に満たす行は存在しない**(0.16でFP2残存、0.17でTPが6に
低下)。既存artifactが指摘した「0.16秒付近の重なり」を定量的に再確認した。
単純な閾値引き上げのみでは分離不可能。

### 候補(b): sim閾値変更(run閾値も併せてスイープ)

| sim閾値 | run閾値(秒) | TP保持 | FP残存 |
|---|---|---|---|
| 0.85(現状) | 0.12(現状) | 8/8 | 15/15 |
| 0.90 | 0.16 | **8/8** | **0/15** |
| 0.95 | 0.12 | **8/8** | **0/15** |
| 0.95 | 0.14 | 4/8 | 0/15 |

sim閾値を引き上げるとTP8/FP0を満たす組合せが存在する。ただし**マージンが
非常に薄い**: sim=0.90/run=0.16では、TP最小run(0.16、2件)とFP最大run
(0.14)の差はわずか0.02秒。sim=0.95/run=0.12でもTP最小run(0.13、2件)と
FP最大run(0.10)の差は0.03秒。**23件という小標本への過学習(overfitting)
リスクが高く**、閾値変更(sim・run)はSSOT上「現状維持」がユーザー決定
済みであることとも整合しない(閾値変更そのものを推奨しない理由)。

### 候補(c): 局所ASR語句一致度による2段判定(推奨)

方式Dが検知した2箇所(flag_time_a/flag_time_b、既存記録値)の前後1.5秒
(空なら2.5→4.0秒まで拡張)をfaster-whisper word-level timestampsで切り出し、
2箇所のtoken列の一致度(difflib SequenceMatcher比率+最長連続一致語数)を
計算し、方式D flag(現状閾値、無変更)への**後段フィルタ**として使う。

| is_tp | overlap_ratio | lcs_words | 代表fragment(A/B) |
|---|---|---|---|
| TP(8件) | 0.6154〜0.7143 | 4〜5 | 例: "what young travelers want. The direction" / "what young travelers want, not proof" |
| FP(15件、最大2件) | 0.4444 | 2 | "muting is not the same as" / "same as absence."(意図的並行構文、真の重複ではない) |
| FP(残り13件) | 0.0〜0.25 | 0〜1 | 内容的に無関係な断片同士 |

閾値`overlap_ratio>=0.5 OR lcs_words>=3`で**TP8/8保持・FP0/15**を達成。
**マージンは候補(b)よりはるかに厚い**(overlap_ratioでTP最小0.6154と
FP最大0.4444の差0.17、lcs_wordsでTP最小4とFP最大2の差2語)。方式D自体の
acoustic閾値は一切変更していない(ユーザー決定「現状維持」と整合)。

重要な副次的発見: FP15件中1件(`er003_output/a2_audio_01::...::full_story_part1`)
は`main_rows`で`a_flagged: None`(canonical_text未取得のため方式A自体が
実行不可)だったが、候補(c)はcanonical_textに一切依存せず(音声+ASRのみ)
overlap_ratio=0.1176・lcs_words=1で正しく「非重複」と判定できた。

### 候補(d): 方式AとのAND合成(既存a_flagged値を再利用、追加計算なし)

`flagged = D flagged(現状) AND (a_flagged == True)`で**TP8/8・FP0/15**を
達成(既存sweep計算値のみで評価、追加wav計算なし)。ただし**設計上のリスク**:
`a_flagged`はcanonical_text未取得の98件(517件中)で`None`となり方式A自体が
実行不可能。AND合成はNoneをFalseとして扱うため、canonical_text欠落時は
方式Dが真の重複を検知しても常にAND条件が不成立になり、方式D単独の検知
能力を丸ごと失う(=方式Dが実質的に無意味化する)構造的欠陥がある。また
「方式Aが既に検知しているものだけを方式Dが後追い確認する」設計は、方式D
がそもそも「方式Aが見逃すケース(ASR完全一致に依存しない検知)」を狙って
導入された経緯(OPEN_ITEMS OPEN-121行のTrial-01/02参照)と矛盾し、方式D
の存在意義を実質的に消してしまう。

## 5. 推奨候補と根拠

**候補(c)(局所ASR語句一致度2段判定)を推奨する。**

根拠:
1. TP8/8・FP0/15を達成し、かつ候補(b)よりマージンが厚く23件への
   過学習リスクが低い。
2. 方式Dのacoustic閾値(sim/run)は一切変更しない(ユーザー決定「現状
   維持」と整合、Production変更ゼロで導入判断可能)。
3. canonical_text非依存(候補(d)の構造的欠陥を回避、98/517件の
   canonical欠落segmentでも機能する)。
4. 方式Aの既存`run_ngram_check()`は内部で`transcribe_verbatim()`(全文)を
   既に呼んでいるため、**Production配線時は同じtranscriptを候補(c)の
   局所判定に再利用でき、追加ASR呼び出しコストをほぼゼロにできる**
   (現在の`evaluate_repetition_qa()`は方式Aと方式D/D'をそれぞれ独立に
   実行しているため、この共有は新規の実装上の工夫が必要、詳細は§10)。
5. 方式D単独の存在意義(方式Aが見逃す非厳密一致ケースの検知)を壊さない
   (方式AはASR完全トークン一致を要求するが、候補(c)はdifflibの
   fuzzy比率を使うため1〜2語のASR表記ゆれに対して方式Aより頑健)。

## 6. false negativeリスク(定性評価)

- **短い(2語以下)真の反復**: 候補(c)の`lcs_words>=3`条件は、方式A既存の
  `min_words=3`設計判断(短い偶然一致による誤flagを避けるための意図的な
  下限)と同じ考え方であり、新規リスクではない。ただし、方式Dが将来
  「2語のみの短い真の反復」を検知した場合、候補(c)はそれを非確認と
  判定しうる(方式A自体も同じ理由で検知しない設計のため、新規に生じる
  リスクではなく既存の許容範囲内)。
- **方式D'(false start型)への影響なし**: 候補(c)は方式D'(短lag・
  run長優先、B1 FSP1型)には一切触れない。方式D'は既存のまま独立して
  動作し続ける(OR統合の一部として無変更)。
- **候補(b)(sim閾値変更)採用時の追加リスク**: マージンが薄い
  (0.02〜0.03秒)ため、23件以外の将来データでこの境界に近い真の重複が
  存在した場合、閾値変更により検知漏れ(false negative)が生じるリスクが
  候補(c)より高い(定量的な背景データでの追試はしていない、23件の
  小標本のみでの評価)。
- **候補(d)採用時の追加リスク**: canonical_text欠落時(98/517件)に方式D
  の検知能力を丸ごと失う構造的リスク(§4参照)。

## 7. retry・Human Reviewへの影響

現行Production配線(`er011_open121_repetition_qa_production_01.py`の
`apply_repetition_qa_gate()`)は`verified = verified and not flagged`という
ANDゲートで、flagged=Trueは既存の「TTS再生成retry loop」にそのまま合流する
(新規retry回数・新規Cost Guardは追加されない設計)。したがって、方式D単体の
FP率が本Trialの23件サンプルで15/23(65.2%)であることは、**現状のまま
新規segmentへ適用範囲を拡大した場合、方式Dのflagの約3分の2が不要な
TTS再生成・最悪Human Review Lockへの誤エスカレーションを引き起こす**
ことを意味する(推定であり、A2/B1英語本文4segmentへの現行配線範囲内では
既にPRODUCTION_WIREDだが、方式D自体は既知3件のみ検証済みで新規23件規模の
FP率検証は本Trialが初)。候補(c)導入によりこの誤retry率は本データセット上
0%に低減する(TP8件はA/D'/candidate-cいずれかで引き続き検知されるため
実質的な検知漏れは生じない)。

## 8. Cost・Latency

- 候補(a)(b)(d): 追加API課金ゼロ、追加計算はほぼゼロ(既存記録値の
  再利用または既存sim行列からの高速再計算)。
- 候補(c): 追加API課金ゼロ(faster-whisperローカルCPU実行のみ)。実測
  レイテンシ: 23件で約116秒(1件あたり平均約5秒、方式Dが実際にflagした
  場合のみ発生。本データセットでのflag率は517件中23件=4.4%であり、
  Production全体へのレイテンシ影響は限定的)。§5で述べた通り、方式A
  実行時の`transcribe_verbatim()`と共有できれば追加コストはさらに
  ほぼゼロになる(現状は独立実行のため今回は素朴に2重計算した)。

## 9. Maintainability

- 候補(c)は新規依存ライブラリを追加しない(既存`er008_disfluency_qa_18.
  transcribe_verbatim()`・標準ライブラリ`difflib`のみ)。
- 候補(c)のロジックは方式Aの`find_repeated_spans`/`_canonical_repeat_count`
  と概念的に類似するが、canonical_text非依存かつ局所探索(全文でなく
  flag位置周辺のみ)という点で明確に役割分担できる(コード重複の懸念は
  あるが、共有ヘルパー関数化で解消可能、実装時の設計課題として記録)。
- 候補(a)(b)(d)は既存コードの数値変更のみで実装は単純だが、§4で述べた
  通りマージン・堅牢性の観点で候補(c)に劣る。

## 10. Production初回・retry・regenerationとの将来整合性

現行の`evaluate_repetition_qa()`は方式A・D・D'を独立に実行し
`flagged = ngram["flagged"] or profile_d["flagged"] or profile_d_prime["flagged"]`
というOR統合を行っている。候補(c)を配線する場合、方式Dの`flagged`を
「D単独判定」ではなく「D flagged AND (局所ASR一致度で確認)」という
2段判定に置き換える形になる。既存のANDゲートパターン(disfluency QAと
同一の接続様式)自体は変更不要で、`profile_d`の`flagged`フィールドの
計算内部だけを拡張すればよい設計であり、既存のretry loop・Cost Guard・
Human Review Lock遷移ロジックへの影響はない(新規apply箇所は
`evaluate_repetition_qa()`内部の1関数のみ)。**この配線変更自体は本Trialの
スコープ外であり、実装していない**(ユーザー承認があれば別タスクで
Production配線)。

## 11. 既知failure mode照合(OPEN_ITEMS OPEN-121行、grepのみで全文読込せず)

- Point Two BUGGY/In One Line BEFORE_FIX(文単位反復、既知): 候補(c)で
  overlap_ratio 0.6154〜0.7143・lcs_words 4〜5と高い一致度で確認、
  false negativeなし。
- B1 FSP1 partial-word false start型(方式D'専用): 候補(c)は方式D'を
  変更しないため無関係、影響なし。
- 「showed/show」Connected Speech ASR不一致(分類B、既存個別承認): 本
  Trialの23件データセットには含まれない(既にHuman承認済みの別経路)。
  候補(c)がASR表記ゆれに対し方式Aより頑健(fuzzy比率)である設計は、
  この種の失敗モードへの一般的な対応方針(OPEN_ITEMS項番4、
  `USER_DECISION_REQUIRED`のまま)には踏み込んでいない(本Trialは方式D
  のFP低減のみが範囲)。
- FLAG_A誤検知メカニズム(%記号 vs percent表記不一致、No.9/No.18):
  方式A自体の問題であり本Trialの対象外(候補(c)(d)ともに方式Aの
  a_flagged値をそのまま利用するのみで、方式A自体は変更していない)。

## 12. 既存QAとの重複確認

候補(c)は既存`er008_disfluency_qa_18`の`detect_adjacent_word_repetition`
(直後同一token限定、意図的に狭い設計)とは検知範囲が異なる(候補(c)は
方式Dが既に検知した2箇所間の内容確認のみを行う後段フィルタであり、
新規の独立検知器ではない)。方式A(`find_repeated_spans`)とは目的が
一部重複するが、§5で述べた通り「canonical非依存」「局所探索」という
点で明確に異なる補完的役割を持つ。

## 13. Dangling Reference Check(Gate 4)

- 新規ファイルはすべて存在確認済み(下記「変更/新規ファイル」)。
- Production module(`er011_open121_repetition_qa_production_01.py`)・
  `er008_disfluency_qa_18.py`は`git diff --stat`で無変更を確認済み
  (読み取りimportのみ)。
- 参照した既存artifact(`method_d_flag23_review_01/classification_table.json`・
  `open121_existing_audio_dprime_sweep_01/results/*.json`)はすべて
  読み取りのみで上書きしていない。
- `er012_output`配下への書き込みは一切行っていない。

## 14. Production配線案(参考、実装はしていない)

- 配線先候補: `er011_open121_repetition_qa_production_01.py`の
  `analyze_profile_d_long_lag()`が返す`flagged`を、局所ASR一致度確認を
  経た2段判定に置き換える(新規関数`confirm_by_local_asr_overlap(bundle,
  words, time_a, time_b, ...)`を追加し、`run_spectral_checks()`または
  `evaluate_repetition_qa()`内で方式Aの`transcribe_verbatim()`結果を
  共有する設計に変更)。
- 引数候補: `overlap_ratio_threshold=0.5`, `lcs_words_threshold=3`,
  `window_half_seconds=1.5`(拡張1段階ごとに+1.0〜+1.5秒、上限4.0秒)。
- 回帰テスト案: 既知陽性3件(Point Two BUGGY/In One Line BEFORE_FIX/
  B1 FSP1)+本Trialの23件データセット全件を固定テストケースとして
  `scripts/run_ci_tests.py`相当の回帰スイートへ追加することを推奨
  (実装は別タスク)。
- 適用範囲: 現行`enable_repetition_qa`のopt-inスコープ(A2/B1英語本文
  4segment)をそのまま維持、拡大の要否は別途ユーザー判断。

## 15. Gate 1分類

**VALIDATED**(候補(c)についてTP8/8・FP0/15達成、既存23件データセット
全件での定量評価・sanity check・false negativeリスクの定性評価を完了。
ただしProduction採用は未実施、閾値変更を伴わないためSSOT「現状維持」
決定と非抵触)。

候補(a)(b)は`REJECTED`(候補a: TP8/FP0を同時に満たせない。候補b:
達成可能だがマージン過小・小標本過学習リスクが高くVALIDATEDと判定しない)。
候補(d)は`REJECTED`(canonical_text欠落時の構造的欠陥、方式D存在意義の
消失リスク)。

## 16. USER_DECISION_REQUIRED

1. 候補(c)をProduction配線対象として正式採用するか(閾値
   `overlap_ratio>=0.5 OR lcs_words>=3`、window±1.5秒拡張ロジックを含む)。
2. 配線時、方式Aの`transcribe_verbatim()`結果を候補(c)と共有する
   リファクタリングを許可するか(既存`evaluate_repetition_qa()`の
   内部構造変更を伴う、ロジック自体は無変更)。
3. 適用範囲をA2/B1英語本文4segment以外へ拡大するかは別途判断
   (本Trialは既存適用範囲内のデータのみで検証)。
4. 候補(b)(sim閾値変更)・候補(d)(AND合成)は明確なリスクがあるため
   不採用を提案するが、最終判断はユーザーに委ねる。

## 費用

¥0(TTS/ASR/LLM有料API呼び出しなし。faster-whisperはローカルCPU実行のみ、
実測合計約116秒)。

## 変更/新規ファイル

- 新規: `er011_open121_method_d_fp_reduction_trial_01.py`(root)
- 新規: `er011_output/method_d_fp_reduction_trial_01/controls_dataset.json`
- 新規: `er011_output/method_d_fp_reduction_trial_01/candidate_a_run_threshold_sweep.json`
- 新規: `er011_output/method_d_fp_reduction_trial_01/candidate_b_sim_threshold_sweep.json`
- 新規: `er011_output/method_d_fp_reduction_trial_01/candidate_c_fragment_overlap.json`
- 新規: `er011_output/method_d_fp_reduction_trial_01/candidate_d_and_with_method_a.json`
- 新規: `er011_output/method_d_fp_reduction_trial_01/summary.json`
- 新規: 本Report
- 変更・削除・Git操作: なし(Production module・閾値・SSOT・`docs/pm/
  ACTIVE_TASK.md`/`RESULT_PACKET.md`・`er012_*`は一切変更していない)
