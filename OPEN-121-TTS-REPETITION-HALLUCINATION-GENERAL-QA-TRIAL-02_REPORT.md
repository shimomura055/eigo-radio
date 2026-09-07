# OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-02 レポート
(false start型+統合仕様)

管理ID: OPEN-121-TTS-REPETITION-HALLUCINATION-GENERAL-QA-TRIAL-02
Lane: A(隔離Trial、ユーザー判断2026-09-07: 方式A+Dは有力候補だが
`As of Septem… As of September…`型のfalse start/aborted restartを検知
できるまでOPEN-121は継続、A+Dだけを先行採用しない)。最大到達Status:
**`VALIDATED`**(方式ごとの有効性はデータで実証、Production採用は不可・
全てユーザー判断待ち)。Production Validator/QA/retry/Cost Guard/TTS
Prompt/適用範囲は**一切変更していない**。既存Production関数
(`er003_b1_p4_audio.get_full_text_via_azure_stt_continuous`・
`er006_asr_provider_routing_01.transcribe`・`er008_disfluency_qa_18`の
各関数)を無変更のまま呼び出すだけの独立Trialモジュール。Trial-01
(`er011_open121_tts_repetition_general_qa_trial_01.py`)も無変更のまま
(読み取りのみ、テストセット51件を読み取りコピーで再利用)。

書き込み: `er011_open121_tts_repetition_general_qa_trial_02.py`(root)、
`er011_output/open121_tts_repetition_general_qa_trial_02/`。

## 0. 既知failure mode照合(先に実施、結論: 重複追加なし)

CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS(OPEN-121行)・Trial-01
(方式A[min_words=3]・D[spectral self-similarity, min_lag=1.0秒]が
`VALIDATED`、Point Two/In One Line型に有効)・B1 FSP1特性解析
(`…/b1_fsp1_recheck/falsestart_characterization_evidence.json`)を確認。
特性解析の`short_run_rescan`(run長優先・短run・低lag再走査)が既に
「閾値0.6でrun長0.75秒・lag0.97秒」を発見していたが、これは1回限りの
個別診断スクリプトであり、テストセット全体での校正(false reject計測)・
一般detector化・player/Report化は未実施だった。本Trialはこの診断結果を
**Method D'として一般化・校正**し、既存disfluency QA/方式A/方式Dが
「なぜ」この型を検知できないかを機構的に説明した上で、3つの新方式
(onset二重化・A-ext参照corpus拡充・Secondary ASR窓検知)と比較する。
重複する新規仕様は追加していない。

## 1. false start型の追加方式(各設計)

### 方式D'(D拡張、**推奨**)
方式D(`spectral_self_similarity`)と同一の対数スペクトル自己相関を使うが、
(a)探索するlag範囲をD本体の`min_lag_s=1.0秒`(全体)ではなく**0.5〜2.0秒**
に制限、(b)top-k類似度優先ではなく**各(開始時刻,lag)ペアでrun長を直接
最大化**(run長優先探索)する点が異なる。lag範囲を固定幅に制限している
ため計算量はほぼ音声長に線形(全体スキャンでも1item平均1.3秒)。
`time_a_max`指定で先頭数秒限定(head6s)・無指定で全体スキャン(full)の
両方を実装・比較した。

### onset二重化検知
RMSエネルギー包絡(frame20ms/hop5ms)からonsetを検出し、lag0.4〜2.2秒の
onsetペアの間の最小RMSが前後onsetのピークに対してどれだけ落ち込むか
(dip_ratio)を検知指標とする。ASR非依存・軽量。

### A-ext v2(参照corpus拡充)
Trial-01の陰性26音声(rerun-02のEN分14)に加え、既存PASS済みaudio
(`tts_generation_results.json`でstatus=OK確認済み、他ERタスクの成果物)
106本を追加し、単語(正規化後)ごとのduration中央値参照を372語→**508語**
へ拡充した。汚染源(`open112_trend_theme2_b_full_audio_trial_13`
= Point Two/In One Lineバグの発生元そのもの)と、STOPPED記録のある
`open109…/full_story_part1`系は明示的に除外した。

### Secondary ASR(Azure)窓検知
先頭6秒の短窓を診断専用のAzure Speech STT呼び出し(English Primary経路
には未採用のまま)へ投入し、生transcript上のtext-only n-gram反復
(min_words=2/3、canonical crosscheck付き)を検出する。

## 2. `As of Septem… As of September…`を検知できたか(実データ+合成、方式別)

テストセットにB1 FSP1実データ(1件)に加え、**false start型合成陽性5件**
を新規に追加した(正常音声の先頭0.7/1.0/1.3/1.1秒[gapなし]+0.9秒[gap
0.15秒]を、語の途中で切って(全5件でmid_word_cut=True確認済み)元音声の
先頭へ前置。複数の元音声[A2 point_one/full_story_part1/part2/topic_intro、
B1B full_story_intro]・複数の切断長で検証)。

| 方式 | false start型 TP | 検知詳細 |
|---|---|---|
| 方式A(既存、min_words=3) | **0/6** | 全項目flagged=False(token完全一致前提のため構造的に検知不能、想定通り) |
| 方式D(既存、spectral、min_lag=1.0秒) | **4/6** | 実データ(lag=0.97秒)とcut0.7秒合成(lag=0.7秒)は`min_lag_s=1.0秒`未満のため**構造的に除外**され0.03秒しか検知できない。cut≥0.9秒の4件はlag≥0.9秒でmin_lag閾値を跨ぐため検知(0.8〜1.28秒run) |
| **方式D'(新、full-file、sim閾値0.7、run長判定≥0.6秒)** | **6/6** | 実データ0.74秒、合成5件全て切断秒数と一致するrun長(0.7〜1.3秒)を検知。lag=cut秒数とほぼ一致し、mid-word cutの構造を正確に捉えている |
| onset二重化検知 | 判定不能 | dip_ratio 0.0〜0.0003(陽性)vs 0.0001〜0.23(陰性、最小0.0001)で**分離不可能**。あらゆる文・句境界に自然な低dip_ratioが存在し、識別力なし |
| A-ext v2(ratio閾値2.5) | **6/6** | 全項目でword duration異常を検知(唯一Trial-01同様100%再現)。ただしFP 3/26(§5参照) |
| Secondary ASR(Azure、min_words=2) | **4/6** | 実データ・cut1.0/1.1/1.3秒を検知。cut0.7秒(1語のみ、"Slow, slow travel…")とcut0.9秒(gap版、"Today's top Today's topic…"で"top"≠"topic"のため2-gram一致せず)は原理的に検知漏れ |
| Secondary ASR(Azure、min_words=3) | **2/6** | min_words=2よりさらに厳しく、実データとcut1.3秒のみ |

**結論: 方式D'が唯一、実データ+全5合成パターンを完全検知(6/6)し、
かつ後述の通りfalse reject 0/39を達成した。**

### 方式Dが検知できない機構的理由(新規に特定)
方式Dの`min_lag_s=1.0秒`は、実データの反復lag(0.97秒)と本Trialの
最短合成陽性(cut0.7秒、lag0.7秒)の**両方を除外する境界値**に一致して
いた。方式D'はlag下限を0.5秒まで広げることでこの盲点を直接埋める設計。

## 3. 方式A+Dとの役割分担

| 対象failure mode | lag/gapの目安 | 担当方式 |
|---|---|---|
| Point Two/In One Line型(句・文まるごと反復) | 8〜10秒(離れた再読) | 方式A(min3、token一致)+方式D(spectral、min_lag=1.0秒) |
| 合成phrase/sentence型(gap>10秒) | 20秒超 | 同上 |
| **false start/aborted restart型**(語途中で切れて即再開) | **0.5〜2.0秒** | **方式D'(新)**。方式A/Dは構造的に検知不能(§2) |
| 即座の言い直し(gap<0.5秒) | <0.5秒 | Trial-01方式C-v2(窓内独立判定、本Trialでは再検証していない) |

方式D'は方式Dと**同一の対数スペクトル自己相関という計算primitiveを
共有**しつつ、探索するlag帯域とrun長最大化の探索戦略が異なるだけであり、
「別のdetectorを新設する」のではなく「既存detectorのパラメータ拡張」
として位置づけるのが最小実装で済む(§6参照)。

## 4. 重複・無駄なcheckの有無

- 方式D'は方式A/Dが担当するPoint Two/In One Line/phrase/sentence型
  (11件)を**一切flagしない**(run長@sim0.7はいずれも0.14〜0.44秒で、
  推奨判定閾値0.6秒を下回る)ことを実データで確認した。逆に方式A/Dは
  false start型6件を(方式Dが部分的に0.8〜1.28秒を検知する4件を除き)
  ほぼflagしない。**重複領域はゼロ、担当範囲は明確に分離している**。
- 実装上の無駄: 方式Dと方式D'は現状Trial-02内で独立に対数スペクトル・
  自己相関行列を計算しており、同一音声に対して同じFFTフレーム計算を
  2回行っている。Production配線時は「1回のスペクトル計算→2種類の
  lag/閾値プロファイル(既存D=min_lag1.0秒・top-k類似度優先、D'=
  lag0.5-2.0秒・run長優先)で同じ類似度行列を再利用」という統合実装に
  すべきという実装効率の指摘のみ(検知ロジック自体の重複ではない)。
- Secondary ASR(Azure)窓検知と方式A/D'は検知原理が異なる(text-token
  一致 vs 音響波形一致)ため、片方が原理的に検知できない事例をもう片方が
  拾う関係にあり、無駄な二重チェックではなく相互補完(§6のcorroboration
  設計)。

## 5. false reject/false negative(方式×テスト表)

テストセット: 陽性17件(実在3+合成9+false start合成5)、陰性39件
(既存PASS再利用27+意図的反復6+自然hallucination試行6、EN26/JA13)。

| 方式 | TP(false start 6件中) | FP(陰性中) | 備考 |
|---|---|---|---|
| **方式D'(full-file、sim0.7/run≥0.6秒)** | **6/6** | **0/39**(全負例、EN+JA) | 最大陰性run=0.5秒(a2_comment_3、JA)、最小陽性run=0.7秒。マージン0.2秒 |
| 方式D'(head6s、同閾値) | 6/6 | 0/39 | full-fileと同一結果(false start型は先頭付近発生のため差異なし)。計算コストはfull-fileの1/5程度 |
| onset二重化検知 | 判定不能 | 判定不能 | 閾値を作れない(§2) |
| A-ext v2(ratio閾値1.8、Trial-01と同一閾値) | 6/6 | **10/26(38.5%)** | **corpus拡充だけでは改善せず**(Trial-01 v1と同水準) |
| A-ext v2(ratio閾値2.5、再校正後) | 6/6 | **3/26(11.5%)** | 校正で改善(Trial-01比▲26.5pt)。FP: a2_point_one_clean("A"0.8秒/4.0倍、"about"0.82秒/2.93倍)・b1b_full_story_intro_charon("the"0.52秒/2.89倍)・intentional_three_hundred("for"0.74秒/2.85倍)。**依然auto-reject不適格** |
| Secondary ASR(Azure、min_words=2) | 4/6 | **0/26**(EN負例) | 意図的反復6件("No matter what, no matter when…"等)もcanonical crosscheckで正しく非flagged |
| Secondary ASR(Azure、min_words=3) | 2/6 | 0/26 | min_words=2よりTP低下、FPは変わらず0 |

生データ: `er011_output/open121_tts_repetition_general_qa_trial_02/results/`
(`method_d_prime_full.json`・`method_d_prime_head6s.json`・
`method_onset_dual_cluster.json`・`method_a_ext_v2_word_duration.json`・
`method_secondary_asr_azure_window.json`・`summary_table.json`)。

## 6. QCD(cost/latency/複雑度/保守性)

| 方式 | 追加cost/件 | 平均latency/件 | 複雑度 | 保守性 |
|---|---|---|---|---|
| 方式D'(full-file) | ¥0(ローカルCPU) | 平均0.4秒(最大1.6秒) | 低(既存方式Dの派生パラメータ) | 高(方式Dと実装統合可能、§4) |
| 方式D'(head6s) | ¥0 | 平均0.2秒(最大0.3秒) | 低 | 高。false start型は先頭発生前提のため実用上こちらで十分 |
| onset二重化検知 | ¥0 | 数十ms | 低 | N/A(識別力なし、不採用) |
| A-ext v2 | ¥0(参照corpus構築は初回のみ、120音声のローカルASR、約9分) | 方式A本体と共有(~3.5秒) | 中(参照corpus管理・定期更新が必要) | 中(汚染源除外リストの継続的メンテが必要、§8の新規発見が実例) |
| Secondary ASR(Azure窓) | 実測¥9.73/43件(≈¥0.23/件) | 平均4.5秒/件(Azure STT呼び出し) | 低 | 高(既存`er003_b1_p4_audio`関数を無変更で呼ぶだけ) |

総cost: **¥9.73**(Azure Speech STT、43件×先頭6秒窓、audio_hourメーター
$1.00/hour換算)。上限¥800に対し1.2%。生データ:
`er011_output/open121_tts_repetition_general_qa_trial_02/audit/raw_usage_log.jsonl`
(Production側・Trial-01側のraw_usage_log.jsonlには一切書き込んでいない)。

## 7. 推奨統合仕様(最小・安全)

**推奨: 方式D'(full-file、sim閾値0.7、run長判定≥0.6秒)を、方式A
(min_words=3)+方式D(既存)へ追加する第3の自動検知シグナルとして採用。**

1. **方式D'を単独のauto-reject候補として最有力視**: false start型6/6
   検知、陰性39/39で誤検知ゼロ、追加API課金ゼロ、方式Dとの実装統合で
   保守コストも低い。
2. **Secondary ASR(Azure、min_words=2)はcorroboration(補強証拠)として
   位置づけ**、単独のgateにはしない(TP 4/6と方式D'より弱く、Azure API
   依存が増える)。方式D'がflagした事例にAzure窓検知も同時にflagした
   場合は「独立2経路で確認済み」として人間レビューの優先度を上げる
   ソフトな重み付けに使うのが安全(OPEN-122のcorroboration設計と同じ
   思想)。
3. **A-ext v2はHuman Reviewソフトフラグ止まり**(Trial-01と同じ結論、
   FP改善はしたが11.5%は依然auto-reject不適格)。
4. **onset二重化検知は不採用**(識別力なし、実装をこれ以上維持する
   価値がない)。
5. 方式D・D'は実装統合(スペクトル計算の共通化)を推奨するが、これは
   効率化であり検知ロジックの削減ではない(§4)。

## 8. Trial status(方式別・統合)

| 方式 | 到達Status | 理由 |
|---|---|---|
| 方式D'(full-file、sim0.7/run≥0.6秒) | **`VALIDATED`** | TP 6/6・FP 0/39を実データ+合成で確認。方式A/Dとの重複ゼロを実証 |
| 方式D'(head6s) | `VALIDATED`(補助構成) | full-fileと同一結果、低latency構成として有効 |
| onset二重化検知 | **`REJECTED`** | 陽性・陰性のdip_ratio分布が重なり、閾値が原理的に作れない |
| A-ext v2 | `VALIDATED`(ただしNOT_RECOMMENDED as auto-reject) | TP 6/6だがFP 11.5%(閾値2.5)。Trial-01比改善はしたが不十分 |
| Secondary ASR(Azure窓、min2) | `VALIDATED`(corroboration用途のみ推奨) | TP 4/6・FP 0/26。単独主力には力不足、補強証拠として有効 |
| **統合(A+D+D')** | `VALIDATED`(Production採用は`USER_DECISION_REQUIRED`) | Point Two/In One Line型+false start型の両方を、既存retry/Cost Guard予算内でカバーできる設計を実データで確認 |

## 検知後flowの既存機構との接続案(更新、設計のみ・未実装)

Trial-01 §4の接続案(`verified = verified and not ngram_check["flagged"]`
という既存`dq18.apply_disfluency_gate()`と同一パターンのANDゲート)を、
方式D'についても同じ形で拡張できる:

```
verified = verified \
    and not ngram_check_A["flagged"] \
    and not spectral_check_D_longlag["flagged"] \
    and not spectral_check_D_prime_shortlag["flagged"]
```

新しいretry回数・新しいCost Guardは一切追加せず、既存
`PRODUCTION_MAX_TTS_ATTEMPTS`(3回)予算内でretryが自動発生し、上限到達後は
既存の`STOPPED`→`er011_human_review_lock_01`の`HUMAN_REVIEW_REQUIRED`
自動遷移にそのまま合流する(Trial-01で実証済みの経路を再利用するだけ)。
Secondary ASR(Azure)・A-ext v2は、方式D'がflagした場合にのみHuman
Review Queueへ追加のコンテキスト情報(corroboration有無・duration
異常語)として添付する**弱い接続**に留める(既存`is_duplicate_queue_
entry()`を流用、新規Validator原則の追加なし)。

## 既存disfluency QAとの役割分担(更新)

| 層 | 検知範囲 | 実装 |
|---|---|---|
| dq18 baseline(既存、Production配線済み) | 隣接1語のみ、heading/in_one_line限定 | 変更なし |
| 方式A(min3、Trial-01) | 非隣接句・文単位(token完全一致)、canonical-aware | 変更なし |
| 方式D(既存、Trial-01) | 音響長lag(≥1.0秒)の句・文単位反復 | 変更なし |
| **方式D'(新、本Trial)** | **音響短lag(0.5〜2.0秒)のfalse start/aborted restart** | 新規追加候補 |
| A-ext v2(新、本Trial) | 単語duration異常(token非依存) | Human Reviewソフトフラグのみ |
| Secondary ASR窓(新、本Trial) | 先頭6秒のtext-level反復(独立ASR経路) | corroborationのみ |

## 重要な新規発見(隠蔽せず記録): 参照corpus構築中に第2の実例を発見

A-ext v2の参照corpus拡充作業で追加した既存PASS済み音声のうち、
`er011_output/open117_keyphrase_display_tts_separation_trial_02/b1b/narration/full_story_part1.wav`
(OPEN-117のB1B `full_story_part1`)が、B1 FSP1と**全く同一のcanonical
テキスト**("As of September 2026, travel surveys in Japan tell a
story with two different speeds.")を持ち、方式D'で再解析したところ
**ほぼ同一の反復シグネチャ**(time_a=0.25秒、lag=0.97秒、run@0.6=0.75秒)
を示すことが判明した。これはB1 FSP1と全く同じ既知バグの、別タスク
(OPEN-117)の生成試行における再現であり、参照corpusの構築中に偶然
検出された(意図的な追加調査ではない)。この事実は:

1. false start失敗モードが同一script/promptに対し**再現性を持つ**
   ことを示す追加の実データ(既知1件→2件)。
2. 該当ファイルはA-ext v2の参照corpus(508語、"september"のn=4、median
   0.47秒)へ**意図せず混入していた**(median計算では外れ値1.36秒が
   1/4を占めるが、中央値は0.46〜0.48秒側の値のままで大きな影響はない
   ことを確認した)。将来この参照corpusを正式採用する場合は、この
   ファイルも`open112_trend_theme2_b_full_audio_trial_13`と同様に
   **除外対象へ追加すべき**(本Trialでは除外リストの更新のみ未実施、
   corpus自体の再構築はコスト対効果上見送った)。
3. `tts_generation_results.json`のstatus=OKは、この種のfalse start
   型を検出できていない(既存Validatorのスコープ外であることの追加
   傍証)。

このOPEN-117側の重複自体の修正・Production側の対応要否は本Trialの
範囲外であり、独自判断で修正していない。§9のUSER_DECISION_REQUIREDに
追記した。

## 9. USER_DECISION_REQUIRED(Production採用に必要な判断)

1. 方式D'(full-file、sim0.7/run≥0.6秒)を、方式A・D(Trial-01)と併せて
   実際にProduction配線するか(新規Validator原則の`APPROVED_FOR_
   PRODUCTION`が必要)。
2. Secondary ASR(Azure)窓検知をcorroboration用途として常設するか
   (追加API呼び出し・レイテンシを許容するか)。
3. A-ext v2を、現状のFP 11.5%のままHuman Reviewソフトフラグとして
   将来採用する方向性を維持するか、見送るか。
4. **新規発見**: OPEN-117 B1B `full_story_part1.wav`(同一script、別
   生成試行)に、B1 FSP1と同一のfalse startシグネチャが見つかった件
   について、(a)この既存出力ファイル自体への対応要否(Productionの
   ライブ経路ではなく旧タスクの出力ディレクトリのため実害は限定的と
   考えられるが未確認)、(b)将来のA-ext参照corpus構築時にこのファイルを
   除外リストへ追加するかの判断。
5. 方式D・D'の実装統合(スペクトル計算共通化、§4/§6)を、採用時に
   併せて行うか。
6. OPEN_ITEMS.md OPEN-121行の既存USER_DECISION_REQUIRED項目(Point Two
   残存重複の扱い等)は本Trialでは変更していない(引き続き判断待ち)。

## 10. Trial Closeout

本Trialは**完了**。方式D'(D拡張)が、false start/aborted restart型に
対する最小・安全な追加検知シグナルとして実データ+合成データの両方で
`VALIDATED`(TP 6/6、FP 0/39、追加課金ゼロ、既存方式A/Dとの重複ゼロ)
という結論に達した。Production採用判断(§9)が必要になった時点で、
本Reportとer011_open121_tts_repetition_general_qa_trial_01_REPORT.mdの
両方を提案として提示する。

## 試聴用ページ(file:///)

`file:///C:/Users/tensh/eigo-radio/er011_output/open121_tts_repetition_general_qa_trial_02/player.html`
(1. 陽性・実在確認済み3件[Point Two/In One Line/B1 FSP1 false start]、
2. 陽性・合成句/文単位反復9件、3. **陽性・合成false start型5件(新規)**、
4. 陰性・既存Production PASS再利用27件、5. 陰性・新規Standard TTS
[意図的反復6件+自然hallucination試行6件]。各行に方式A/D(既存)・
方式D'(full/head6s)・onset・A-ext v2・Azure窓検知の判定結果を併記)。
