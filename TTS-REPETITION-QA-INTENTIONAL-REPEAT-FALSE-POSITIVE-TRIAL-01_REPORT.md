# TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01

**管理ID**: TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01
**種別**: Trial(隔離、Production変更なし)
**実行者**: sonnet-worker(Fable委任、初回)
**日付**: 2026-09-08
**費用**: ¥0(新規TTS/ASR/API呼び出しなし、既存JSON/既存ASR結果のみ使用)

## 0. 背景(委任元記載の要約)

B-Family Phase 1でVoice B本文(`point_two`)の意図的並行構文
`"...the people I need—or do not need—around me."` が、共有Production
module `er011_open121_repetition_qa_production_01.py` の方式A
(`_canonical_repeat_count()`)により、canonical側で1回・実音声(ASR)側で
2回と誤カウントされ、TTS hallucinationの重複として3 attemptすべてが
`flagged=True`となりAssembly `GATE_BLOCKED`に至った(ユーザー試聴で正常な
音声と確定済み)。

## 1. 既知failure mode照合(Grep、全文読込なし)

- `OPEN_ITEMS.md` OPEN-121行: 既存の既知false positive機構は
  **「%記号 vs "percent"表記」「小数点付き数字(108.95 vs 108.57)」**の
  2種のみ記録されている(`FLAG_A誤検知メカニズムの特定`追記)。**em dash
  隣接tokenによる誤カウントは、OPEN-121行のどの追記にも記載が無い新規の
  failure modeである**(重複作業ではない)。
- `DECISION_LOG.md` PM-CLOSEOUT-CONSOLIDATION-09: 本件の根本原因
  (`_canonical_repeat_count()`がem dash隣接tokenを1語として誤カウント)
  が既に文言レベルで特定・記録済み(Sonnet実装は未着手のままFableへ
  `USER_DECISION_REQUIRED`選択肢a/b/cとして提示されていた)。本Trialは
  そのうち選択肢(b)「共有moduleのem dash tokenization改善」の評価に
  相当する。
- `CURRENT_SPEC.md` 該当行: 同じ根本原因の要約が反映済み、コード修正は
  未実施と明記。

## 2. 原因の特定(実データ再現)

`_normalize_tokens(text)`(該当module 240-241行)は`text.split()`
(空白のみ区切り)→ `dq18._normalize_token()`(`.,!?"'…`のみ除去、em
dashは対象外)という素朴な実装。Voice B canonical text(`b1b/parts.json`
`point_two_body`)の該当箇所は

```
...the people I need—or do not need—around me.
```

のようにem dash前後に空白が無い(米国式タイポグラフィ)。`text.split()`は
`"need—or"`・`"need—around"`を1つのtokenとして扱うため、3-gram
`["do","not","need"]`が完全一致するのは1箇所目(`"...I do not need one
fixed spot..."`)のみで、2箇所目は`"need—or"`が邪魔をして一致しない。
結果`canonical_repeat_count=1`(実際の意図的出現は2回)となり、
`intentional = (canon_count >= 2)`がFalseのままflagされる。

**実データでの再現確認**(新規ASR呼び出しなし、既存記録値をそのまま使用):
`er012_output/editorial_b_family_production_phase1_02/b1b/narration/
attempts/point_two_attempt{1,2,3}_*.json` の3attemptすべてで
`span_text=" do  not  need"`, `canonical_repeat_count=1`,
`intentional=false`, `flagged=true`を確認。さらに**同一bugがPhase 1より
前のtrial(`er012_output/editorial_b_voices_trial_08_audio/p1/b1b/
point_two`)でも既に発生していた**ことを`er011_output/
open121_existing_audio_dprime_sweep_01/results/classified_table.json`
から発見した(未報告のまま埋もれていた既存事例、隠蔽せず記録)。

## 3. 既存QAとの重複確認

- 方式A(n-gram、本Trialの対象)/方式D・D'(spectral self-similarity)は
  独立した検知原理であり、方式D/D'は今回の根本原因(canonical側token化)
  と無関係(影響なし、対象外)。
- disfluency QA(`er008_disfluency_qa_18`、隣接同一token限定)・secondary
  ASR(Azure窓検知)は句・文単位反復の検知範囲外またはcorroboration専用
  であり、本件のcanonical crosscheck機構とは別レイヤ。重複作業なし。

## 4. Trial実装(候補ロジック、`er011_repetition_qa_intentional_repeat_
trial_01.py`、新規・root)

Production module (`er011_open121_repetition_qa_production_01.py`) は
importして関数を読み取り専用で呼ぶのみ(編集・monkeypatchなし)。

| 候補 | 内容 |
|---|---|
| baseline | Production `_normalize_tokens`/`_canonical_repeat_count`をそのまま呼ぶ(比較基準) |
| **candidate1a_emdash_only_split(推奨)** | canonical分割前にem dash(—, U+2014)のみを空白へ置換。ハイフン(-)・en dash(–)は対象外 |
| candidate1b_em_en_dash_split(参考・非推奨) | em dash + en dash(–, U+2013)の両方を空白へ置換 |
| candidate2_regex_word(非推奨) | 全ての非英数字を区切りとみなす汎用regex tokenizer(`[a-z0-9']+`)、span側も同一tokenizerで再構成 |
| candidate3_naive_delete(比較用の悪い例) | em/en dashを空白ではなく単純delete(誤実装の実例として残す) |

## 5. コーパス評価(既存JSON/既存ASR結果のみ、API呼び出しなし)

- **positive controls(10件、必ずflagged維持)**: OPEN-121で
  「真の重複(証拠あり)」と確定済みの8件(`er011_output/method_d_flag23_
  review_01/classification_table.json` index0-7、Point Two BUGGY/In One
  Line BEFORE_FIX型の文単位まるごと逐語反復)+ 同一script別ファイルの
  known_case 2件(`point_two_BUGGY_UNFIXED_backup`・
  `in_one_line_BEFORE_FIX_buggy_backup`)。
- **negative controls(4件、必ずflagged解消)**: Voice B `point_two`の
  em dash並行構文。phase1_02の3 attempt全件 + trial_08の1件(新規発見の
  既存事例)。
- **regression controls(12件のspan、8 segment)**: em dashと無関係な
  既存flagged item(既にOPEN-121行で「%記号 vs percent表記」「小数点数字
  不一致」による誤flagと文書化済みの8 segment、`open121_existing_audio_
  dprime_sweep_01`の1654件中で方式Aがflagした19件のうち、上記10件を
  除いた残り)。canonical_textに`—`/`–`が含まれないことを機械的に確認
  済み(em dash非関与であることの裏付け)。**再現整合性チェック
  (`all_baseline_reproduced`)がTrueであることを確認済み**(baseline
  候補の再計算値がProduction記録値と完全一致、Trial側の再実装に誤りが
  ないことの検証)。

## 6. 結果表(TP/FP/FN、`er011_output/repetition_qa_intentional_repeat_
trial_01/evaluation_results.json`)

| 候補 | TP(真陽性維持) | FN(見逃し) | TN(誤検知の是正) | FP(誤検知のまま) | regression_ok | regression_break |
|---|---|---|---|---|---|---|
| baseline | 10/10 | 0 | 0/4 | **4/4** | 12/12 | 0 |
| **candidate1a(推奨)** | **10/10** | **0** | **4/4** | **0** | **12/12** | **0** |
| candidate1b | 10/10 | 0 | 4/4 | 0 | 12/12 | 0 |
| candidate2(非推奨) | 10/10 | 0 | 4/4 | 0 | **8/12** | **4/12** |
| candidate3(誤実装例) | 10/10 | 0 | 0/4 | 4/4(baselineと同一、修正効果なし) | 12/12 | 0 |

candidate1a/1bはこのコーパスでは同一結果。candidate2は`108.95`/`108.57`
を`108`+`95`/`108`+`57`へ分割してしまう副作用で、既存の別原因(数字
表記不一致)による誤flag 4件を偶然「is intentional」へ反転させてしまい
(false reject→false accept、意図しない挙動変化)、`regression_break`
として明示的にFAILとした。

## 7. false accept / false reject 分析

- candidate1a: false reject(意図的反復を誤flag)= 0/4(完全是正)。
  false accept(真の重複を見逃す)= 0/10(維持)。regressionへの副作用ゼロ。
- candidate2は「数字を含むspanなら何でも区切ってしまう」設計のため、
  今回のcorpus(N=12)ではたまたま既存の別バグ(%/小数点不一致)を隠す
  方向にしか作用しなかったが、将来別の数字絡み真陽性(例: 電話番号・
  日付の逐語反復)を誤ってintentional扱いする**false accept拡大リスク**
  が理論面からも実証面からも高いと判断し、非推奨とした。
- candidate1b(en dash込み)は本corpusでは無害だったが、リポジトリ全体
  grep(3197ファイル)でen dashが`1–1`のようなスコア表記(空白なし)に
  1267回使われていることを確認しており、**該当する数字range付き
  positive/negative controlが本corpusに実在しないため未検証**。理論上、
  candidate2と同種の副作用(数字token分割による誤intentional化)が
  起こり得る。em dashのみに絞るcandidate1aはこのリスクを構造的に回避
  する。

## 8. retry / Human Review への影響

現行(baseline)では、意図的な並行構文を含むsegmentは既存retry loop
(`apply_repetition_qa_gate`のANDゲート、既存`PRODUCTION_MAX_TTS_
ATTEMPTS`予算内)で毎回flagされ続け、上限到達後は既存のHuman Review Lock
自動遷移に落ちる(実例: Voice B `point_two`が3 attempt連続でflag→
`GATE_BLOCKED`)。candidate1aを配線した場合、この種の意図的並行構文は
初回attemptでflagged=Falseとなり、**不要なTTS再生成(1segmentあたり最大
3回)・不要なHuman Review発生を回避できる**。既存のretry上限・Cost
Guard・Human Review Lock機構自体には一切手を入れない(ANDゲートの入力
条件のみ変わる)。

## 9. Cost / latency

Trial自体の費用: ¥0(新規TTS/ASR呼び出しなし)。候補ロジックは
`text.split()`前に1回のregex置換を追加するだけで、計算量・実行時間は
baselineと同一オーダー(canonical文字列長に対して線形、無視できる
オーバーヘッド)。Production配線した場合の追加コストもゼロ(ローカル
文字列処理のみ、既存のAPI呼び出し回数・retry回数を増やさない。むしろ
上記8の通り誤flagによる不要retryを削減する方向)。

## 10. maintainability

- 変更点は`_normalize_tokens()`1関数(1行の正規表現置換追加)のみ。
  `_canonical_repeat_count()`・`detect_ngram_repetition()`・
  `run_ngram_check()`・`evaluate_repetition_qa()`・
  `apply_repetition_qa_gate()`は無変更で済む(呼び出し元シグネチャに
  影響なし)。
- 既存の`er011_open121_tts_repetition_general_qa_trial_01/02.py`にも
  同名`_normalize_tokens()`の類似実装が存在するが、これらは非Production
  (historical trial artifact)であり本件の対象外。将来これらを再利用する
  場合は同じ問題が再発しうる点を保守メモとして残す。

## 11. Production初回・retry・regenerationとの将来整合性

candidate1aは`apply_repetition_qa_gate(enabled=True)`が呼ばれる既存の
初回生成・retry・(将来の)regeneration経路すべてで同一関数
`_normalize_tokens()`を通るため、経路によって挙動が分岐することはない
(単一の共有関数を直す設計、A2/B1の適用範囲[`full_story_part1/2`・
`point_one`・`point_two`]・opt-inフラグ`enable_repetition_qa`の既存設計
とも矛盾しない)。

## 12. Dangling Reference Check(Gate 4)

- Production module importer(grep確認): `er003_v1_crosslevel_audio_02_
  common.py`・`er003_v1_repro01_main_generate.py`・`er003_v1_sing01_
  news_tail_fix.py`・`er011_open121_repetition_qa_production_wiring_01_
  test_01.py`・`er012_b_family_voices_production_01.py`。いずれも
  `_normalize_tokens`/`_canonical_repeat_count`を直接importしておらず、
  `apply_repetition_qa_gate`/`evaluate_repetition_qa`経由のみ(内部
  関数のシグネチャ変更なしのためこれらへの影響なし)。
- 既存回帰テストファイル`er011_open121_repetition_qa_production_wiring_
  01_test_01.py`内に`NgramRepetitionLogicTests`クラスが既に存在し、
  em dash regressionテストを追加する自然な配線先であることを確認した
  (実装はしない、案として次章に記載)。

## 13. Production配線案(未実装、承認前提の設計メモ)

- 変更対象: `er011_open121_repetition_qa_production_01.py` の
  `_normalize_tokens(text)`(240-241行)。
- 変更内容(案): 関数冒頭で`text = re.sub(r"—", " ", text)`(em dashのみ、
  U+2014)を追加してから既存の`text.split()`以降へ渡す。`import re`を
  module冒頭へ追加する必要がある(現状未import)。
- 引数・戻り値のシグネチャ変更なし。呼び出し元(`detect_ngram_
  repetition`等)は無変更。
- 回帰テスト案(実装しない、案のみ): `NgramRepetitionLogicTests`へ
  (a) Voice B実データ(`need—or do not need—around`相当の最小fixture)
  でintentional=Trueになることを確認するテスト、(b) 既存8件の真の重複
  fixture(またはその代表1-2件)がintentional=Falseのまま維持される
  ことを確認する回帰テストを追加。
- 実施タイミング: ユーザーが`APPROVED_FOR_PRODUCTION`を正式承認した後、
  別管理IDでのProduction実装タスクとして実施(本Trialでは一切実装しない)。

## 14. Gate 1分類

**VALIDATED**(Trial範囲、candidate1a_emdash_only_split)。
根拠: positive control 10/10維持(false accept増加ゼロ)、negative
control 4/4是正(false reject解消)、regression control 12/12無変化
(無関係な既存挙動への副作用ゼロ)、baseline再現性確認済み、費用¥0、
変更範囲は1関数・1行のregex追加のみで影響範囲を機械的に特定済み。

## 15. USER_DECISION_REQUIRED(Production採用の論点)

Trial自体はVALIDATEDだが、**Production module本体への実装・
`APPROVED_FOR_PRODUCTION`の可否は本Trialの権限外**であり、以下は
ユーザー判断が必要:

1. candidate1a(em dashのみ)をProduction `_normalize_tokens()`へ
   実装してよいか(推奨)。
2. `DECISION_LOG.md`記載の既存`USER_DECISION_REQUIRED`選択肢(a)
   (Voice B 3 attemptをユーザー試聴のうえ`record_human_approval()`で
   承認)は本件のロジック修正とは独立した経路であり、どちらか一方の
   採用で足りるか、両方(修正+今回3attemptの個別承認)を行うか。
3. en dash(–)を含む数字range(score等)の実例が将来出現した場合の
   candidate1b相当拡張の要否(現corpusには該当実例がなく未検証のまま)。
4. 実装する場合、回帰テスト追加(§13)・既存517/1654件規模の全件再
   スイープでの最終確認を、Production実装タスクの完了条件に含めるか。

## 16. 新規ファイル一覧

- `C:\Users\tensh\eigo-radio\er011_repetition_qa_intentional_repeat_trial_01.py`(Trial実装、候補ロジック+corpus評価ハーネス)
- `C:\Users\tensh\eigo-radio\er011_output\repetition_qa_intentional_repeat_trial_01\evaluation_results.json`(評価結果、詳細JSON)
- `C:\Users\tensh\eigo-radio\TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01_REPORT.md`(本Report)

Production module・既存er011_output/er012_output配下の既存ファイルは
一切編集・上書きしていない(git操作なし)。
