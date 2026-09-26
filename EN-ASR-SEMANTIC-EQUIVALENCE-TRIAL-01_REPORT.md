# EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01_REPORT

管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01(Phase A+B)
日付: 2026-09-26
Status: VALIDATED(Trial止まり、Production採用ではない。人間ユーザーの
`APPROVED_FOR_PRODUCTION`承認が別途必要)
性質: Trial実装+検証(ユーザーTrial承認2026-09-26)

---

## §0 要約

`EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md` Part 2で承認された
Phase A(観測性修正+Tier 1数値等価)+Phase B(規則的複数形・固有名詞の
corroboration付き救済、`ASR_VALIDATION_UNCERTAIN`のsub-reason)を、
新規Trial module `er021_en_asr_semantic_equivalence_trial_01.py` として
実装・検証した。Production module(`er006_preprod_hardening_01_validation.py`
等)は無変更(sha256照合済み、§1)。

- corpus検証: POSITIVE 34/34救済・NEGATIVE false accept **0/34**。
- 既存OPEN-123 Regression fixture(59件、POSITIVE 29/AMBIGUOUS 2/NEGATIVE 28):
  無回帰0件・false accept **0/28**。
- 既存全体regression(`python -m unittest discover -s . -p "*_test_01.py"`、
  本Trial追加40件込み1,218件超): **無変化(OK)**。
- 実API(TTS_EXECUTION_MODE=STANDARD、6 probe): billion+decimal・年spelled
  読みで実際にbaselineが`TRUE_CONTENT_MISMATCH`となり、本moduleが
  `NUMERIC_EQUIVALENCE_MATCH`で正しく救済することを実測。既存の実本番
  false reject証跡(`comment_test2_probe.json`、$2.3 million、3回連続
  `TRUE_CONTENT_MISMATCH`→`HUMAN_REVIEW_LOCKED_RETTS_FAILED`)を**再生成
  せず再判定(¥0)し、本moduleがあれば1回目のattemptでPASSし
  cool-down 600秒+Local Rewrite Luna 2 callを回避できていたことを確認**。
- 実測費用: 約¥2.40(gemini TTS ¥2.30+openai_asr ¥0.10、guardrail ¥30以内)。

Fable/ユーザーの最終判断が必要な項目は無し(§7参照、VALIDATED)。
Production配線(`APPROVED_FOR_PRODUCTION`)は本Trialの範囲外。

---

## §1 実装概要(Production非配線の確認)

新規ファイル(すべてroot、Production moduleは一切変更なし):
- `er021_en_asr_semantic_equivalence_trial_01.py`: `classify_semantic_
  equivalence(canonical, asr, *, secondary_text=None, local_text=None)`
  本体。Tier 1数値/通貨/%/年/時刻/分数/ローマ数字/略語パーサ、
  `_classify_asr_match_core`ではなく既存`classify_asr_match()`をそのまま
  呼ぶStep 2、Tier 3 corroboration救済(Step 3)、sub_reason/観測性
  (Step 4)。
- `er021_en_asr_semantic_equivalence_trial_01_run.py`: corpus定義+
  オフライン検証+既存fixture regression+runtime計測+実API probe
  オーケストレーション。
- `er021_en_asr_semantic_equivalence_trial_01_test_01.py`: unittest 40件
  (Tier1 POSITIVE/NEGATIVE、Tier3 corroboration有無、sub_reason、
  Tier2対象外確認、既存59件fixtureの無回帰・false accept 0確認)。

対象Production moduleの無変更確認(sha256、本Trial実行直前時点):

| ファイル | sha256 |
|---|---|
| `er006_preprod_hardening_01_validation.py` | `469da7dd34f03d501ea38e44856eb93fd921498f67068176a7859273d6122ad3` |
| `er006_secondary_asr_01.py` | `bbd5d2518f9b042376fe435291fe30e8e800160897aa7d5cb4f8e745a79e3d9e` |
| `er020_tts_retry_local_rewrite_01.py` | `c8df5db60e9e3fb63fd28c56dd8fb5f23a2df372135f647336deae16d0d17dd1` |
| `er003_audio_tts_asr_safety.py` | `559f7291765ac96a1e777a0077f671d3d4cf64823d6dfc29d598c46e5baec28f` |
| `er011_connected_speech_equivalence_layer_production_01.py` | `d7d2fd40e8a2e66f80d4d305b329a473ad247d79cd0d77ed7233771bd53d100e` |

これらのファイルへの`git diff`はゼロ(本Trialはimportして呼び出すのみ)。

**Tier 1パーサの設計**: `fractions.Fraction`(`Decimal`由来の値から構築、
丸め誤差の無い厳密な有理数比較)を用いて、cardinal/ordinal語⇔算用数字・
桁区切り・小数・decimal×scale(hundred/thousand/million/billion/trillion)・
通貨($/£/€⇔dollars/pounds/euros、通貨の有無**および型**を保護)・
%⇔percent(percentage pointsは保護)・年のペア読み(nineteen ninety-nine/
twenty twenty-six/two thousand and six)・時刻(h:mm⇔語+am/pm必須)・
単純分数・ローマ数字(**安全のためII〜Xに限定、代名詞"I"と衝突する
単独の"I"は対象外**、下記§6参照)・`No.`⇔number・`&`⇔and・minus⇔-を
両側で値パースし、値列が完全一致した場合のみ`NUMERIC_EQUIVALENCE_MATCH`
とする。パース対象外の記号(上付き指数等)は黙って消さず1文字ずつの
literal atomとして残す(§3で実測発見・修正した回帰バグ、下記参照)。

**Tier 3 corroboration**: `baseline.classification=="ASR_VALIDATION_
UNCERTAIN"`かつdiffが「ちょうど1件の1トークン対1トークンreplace」で
規則的複数形(`_is_benign_plural_pair`相当の独立再実装)または固有名詞
(`capitalized_flags`由来のentity_like)のみの場合に限り、Secondary/Local
ASRがその位置でcanonical語を支持する(`_word_at_diff_matches_canonical`
相当の同型実装)ときのみ`SECONDARY_ASR_CORROBORATED_MATCH`
(should_pass=True)。homophone_onlyはTier3救済の対象外(spec通り)。
Tier2(wanna/gonna等)は実装していない(範囲外)。

---

## §2 corpus(全件表)

`er021_output/en_asr_semantic_equivalence_trial_01/corpus.jsonl`
(POSITIVE 34件・NEGATIVE 34件、各id/canonical/asr/expected/label_source/
evidence)。主要な実証跡付きケース:

| id | 内容 | 根拠 |
|---|---|---|
| P01 | $2.3 million(2026-09-26実probe逐語) | `er020_output/.../comment_test2_probe.json` |
| P02 | "two million three hundred thousand dollars"(Local Rewrite candidate_2) | `TTS-LOCAL-REWRITE-...REPORT.md` §12.3 |
| P25 | point/points(comment_4実本番、cool-down 600秒+Luna 2 call消費事例) | 同 §12.2 |
| P28/P29 | Ottoni/Otani・Triangeln/Triangle(固有名詞音訳差) | `recon_02.md` T3-1-d/e |
| N01〜N34 | 2.3M vs 2.5M・fifteen vs fifty・percent vs percentage points・
  時制/否定/値差9件(recon_02 T3-2逐語)・can't/can・will/won't・
  corroboration矛盾・7桁ID保護・date slash等 | `recon_01.md`/`recon_02.md`各所 |

全件はcorpus.jsonl参照(このREPORTには全文を複製しない)。

---

## §3 オフライン結果(¥0)

### corpus(自作、POSITIVE 34/NEGATIVE 34)

```
positive_count=34, positive_rescued_or_pass=34 (100%)
negative_count=34, negative_false_accept=0 (0%)
```

POSITIVE内訳(tier_applied): tier1_numeric=27件、tier3_corroboration=4件
(point/points, report/reports, Ottoni/Otani, Triangeln/Triangle)、
tier1_numeric_or_tier3(dollar/dollars、実際はTier1の通貨語suffix吸収で
救済、当初Tier3想定だったがTier1で解決)=1件、baseline_normalized_match
(既存Production側で既にPASS、無回帰確認用)=2件。

### 既存OPEN-123 Regression fixture(59件、`er006_preprod_hardening_01_
validation_test.py`)

```
total=59 (POSITIVE=29, NEGATIVE=28, AMBIGUOUS=2)
regressions=0 (POSITIVE fixtureの受入条件[should_pass=True または
  should_retry=False]を壊した件数)
false_accepts=0 (NEGATIVE fixtureが誤ってPASSした件数)
```

実測中に発見した回帰バグとその修正(既存fixtureで検出、production側の
問題ではなく本Trial moduleのTier1パーサ自体の不具合): 上付き指数記号
(`10¹⁶`)がtokenizerの正規表現でどの規則にも一致せず黙って消失し、
`"10¹⁶ combinations"`と`"10 combinations"`が誤って数値等価
(`NUMERIC_EQUIVALENCE_MATCH`)になっていた(fixture名"exponent value
missing"で実測発見)。対策: 認識できない文字を黙って捨てず、1文字ずつの
literal atomとして残すフォールバックトークン(`|[^\s]`)を追加。この際、
"twenty-eight"等の語間ハイフンが同じフォールバックで意図せず捕捉され
年のペア読み(nineteen ninety-nine等)が壊れる副作用が発生したため、
production側`_convert_cardinal_words()`と同型の「アルファベット間の
ハイフンは空白として扱う」前処理を追加して解消した(§6のリスクとして
再掲)。修正後は上記の通り59件全件OK・false accept 0で確定。

### 既存全体regression

`python -m unittest discover -s . -p "*_test_01.py"`(本Trial追加の
`er021_en_asr_semantic_equivalence_trial_01_test_01.py` 40件を含む)を
このディレクトリで直接実行した権威版: **Ran 1218 tests ... OK**
(エラー・失敗0件、実行時間約174秒)。

**透明性のための追記**: 本orchestrationスクリプト自身の中から
`subprocess`経由で同じdiscoverコマンドをもう一度呼んだ回(二重ネスト
subprocess)では、`er012_e_family_entertainment_two_level_runner_test_01.
TtsModeCliTests.test_batch_mode_without_reason_errors_via_subprocess`
(CLIサブプロセスの`stderr`を検証する既存テスト)が`result.stderr`が
`None`になり1件だけERRORになった。該当テストを単体で独立実行したところ
PASS(`OK`、3.623秒)であり、上記の直接実行(1218件OK)でも問題なく
含まれていた。二重にネストしたsubprocess呼び出し環境固有の一過性事象
(本Trialのer021側変更、Production module無変更[sha256確認済み]とは
無関係)と判断する。詳細は`er021_output/en_asr_semantic_equivalence_
trial_01/results/trial_results.json`の`python_unittest_regression`
キーに両方の実行結果を保存済み。

---

## §4 実API結果(実測費用 約¥2.40)

### 既存probe再判定(`comment_test2_probe.json`、再生成せず、¥0)

canonical: "The price rose to two point three million dollars, a fifteen
percent increase from last year."。3 attempt全ての実ASR逐語("The price
rose to $2.3 million, a 15% increase from last year.")を本moduleで再判定:

| attempt | 当時の判定(Production実測) | 本module判定 |
|---|---|---|
| standard 1 | `TRUE_CONTENT_MISMATCH` | `NUMERIC_EQUIVALENCE_MATCH`(should_pass=True) |
| standard 2 | `TRUE_CONTENT_MISMATCH` | `NUMERIC_EQUIVALENCE_MATCH`(should_pass=True) |
| fallback 1 | `TRUE_CONTENT_MISMATCH` | `NUMERIC_EQUIVALENCE_MATCH`(should_pass=True) |

`would_have_avoided_human_review_lock=True`。実際の当時のrunはcool-down
600.004秒+Local Rewrite(Luna 2 call)を消費した末に`HUMAN_REVIEW_LOCKED_
RETTS_FAILED`へ到達しており、本moduleがあればattempt 1の時点でPASSして
いた。

### 新規実TTS/ASR probe(6件、`TTS_EXECUTION_MODE=STANDARD`、専用out-dir
`er021_output/en_asr_semantic_equivalence_trial_01/audio/`、既存記事
artifact無変更)

| id | canonical | 実Primary ASR逐語 | baseline | 本module |
|---|---|---|---|---|
| probe_a_billion_decimal_currency | "...profits of four point seven billion dollars this quarter." | "...profits of $4.7 billion this quarter." | `TRUE_CONTENT_MISMATCH`(should_pass=False) | `NUMERIC_EQUIVALENCE_MATCH`(True) |
| probe_b_percent_decimal | "Growth came in at two point five percent this month." | "Growth came in at 2.5% this month." | `NORMALIZED_MATCH`(True、既存正常ケース) | `NUMERIC_EQUIVALENCE_MATCH`(True、無回帰) |
| probe_c_plural_regular_noun | "We identified one clear trend in the data." | (完全一致) | `EXACT_MATCH`(True) | `NUMERIC_EQUIVALENCE_MATCH`(True、無回帰。実ASRが誤らなかったためTier3経路は不発火) |
| probe_d_year_spelled | "The measure passed in twenty twenty-six." | "The measure passed in 2026." | `TRUE_CONTENT_MISMATCH`(False) | `NUMERIC_EQUIVALENCE_MATCH`(True) |
| probe_e_roman_numeral | "The report cites World War II casualties." | (完全一致) | `EXACT_MATCH`(True) | `NUMERIC_EQUIVALENCE_MATCH`(True、無回帰) |
| probe_f_currency_no_scale | "The kit costs one hundred twenty five dollars." | "The kit costs $125." | `NORMALIZED_MATCH`(True) | `NUMERIC_EQUIVALENCE_MATCH`(True、無回帰) |

6件中2件(probe_a、probe_d)で**実際にbaselineがTRUE_CONTENT_MISMATCH
だったものを本moduleが正しく救済**(billion decimal+currency、年のペア
読み)。残り4件はbaselineが既に正常PASSしており、本moduleへ切り替えても
should_passが変わらないこと(無回帰)を確認した。**いずれのprobeも
Primary ASRが最初から正確だったため、Secondary/Local ASR corroboration
(Tier3)を要する実NGは今回の6件では再現しなかった**(Tier3自体はcorpus
オフライン検証・unittestで別途、実本番証跡[point/points comment_4等]の
逐語を用いて検証済み、上記§2/§3参照)。cool-down/Local Rewriteはいずれの
probeでも発火させていない(判定層のみの検証、既存retryループには一切
配線していない)。

cost logger実測: gemini(TTS) ¥2.30、openai_asr(Primary ASR) ¥0.10、
合計 **¥2.40**(guardrail ¥30以内)。

---

## §5 runtime影響

代表ケース1,000回平均(`time.perf_counter`、決定論的Python処理のみ、
API呼び出しなし):

| ケース | baseline(`classify_asr_match`単独) | 本module | 差分 |
|---|---|---|---|
| Tier1が発火するケース($2.3M probe) | 0.584 ms | 0.090 ms | -0.494 ms(Tier1 early-exitがbaseline呼び出し自体をスキップするため高速) |
| Tier1が発火せずbaselineへフォールスルーするケース | 0.579 ms | 0.405 ms | -0.174 ms |

いずれのケースも本moduleはbaseline単独より遅くならない(Tier1の値
パース自体が軽量な正規表現+算術処理のみで、`connected_speech`分類器等
baseline内部の重い処理を経由しないため)。実運用のTTS/ASR API呼び出し
(数百ms〜数秒)と比較すれば無視できる水準。

---

## §6 false accept/false rejectの残存リスク

1. **ローマ数字"I"の意図的除外**: 代名詞"I"との衝突を避けるため、単独の
   "I"はローマ数字1として認識しない(II〜Xのみ)。spec原文は「I〜X」だが、
   これは安全側への縮小(false accept経路を1つ塞ぐ)であり、Production
   仕様変更ではない(§1参照)。
2. **通貨型も保護(spec原文は「有無」のみ言及)**: dollars/pounds/euros
   間の型違いも不一致として扱う設計(N31で確認)。これも安全側への
   上乗せであり、rescue率を下げる方向にのみ作用する。
3. **語間ハイフンの正規化前処理**(§3の回帰修正)により、"twenty-eight"
   のような複合語は空白同様に扱われる。将来的にハイフンで結合された
   非数値の固有名詞的複合語(例: "well-known"のような形容詞)が意図せず
   影響を受けないか、コード上は数値語彙(`_NUMBER_VOCAB`)に含まれる
   語のみが対象のため実質的な副作用は無いと考えられるが、追加corpusでの
   継続検証が望ましい。
4. **Tier3 corroborationの限界**(recon_02 T2-3(b)と同型): Secondary/
   Local ASRが両方ともPrimaryと同じ誤りをした場合は救済されない(安全側、
   false rejectのまま)。
5. **時刻の語形式認識はam/pm必須**: am/pmが無い場合は語形式時刻を
   認識しないため、救済されない(安全側、false rejectのまま残る)。
6. **実API 6probeではTier3(corroboration)の実NGケースを再現できな
   かった**: Primary ASRが数値以外で誤ることが今回は発生しなかったため。
   Tier3の実運用効果は既存の実本番証跡(comment_4等)の逐語再判定と
   unittestで担保しているが、新規の生きたSecondary/Local ASR経由の
   実測確認は今回追加されていない。

---

## §7 Sonnet仮分類

**VALIDATED**。理由: (a) POSITIVE 34/34救済、NEGATIVE false accept
0/34、(b) 既存OPEN-123 fixture 59件・既存全体regression 1,218件超で
無回帰・false accept 0、(c) 実本番false reject証跡の再判定で有効性を
確認、(d) 実API 6probeでbillion+decimal/年spelled読みの実NGを実際に
救済、(e) Production module無変更(sha256確認済み)、(f) runtime影響は
無視できる水準、(g) 予算実測¥2.40(guardrail ¥30以内)。

Production採用可否・配線範囲(role/segment適用範囲、既存retry/Local
Rewrite/Human Review Lockへの実配線方法)はユーザー判断事項であり、本
Reportでは推奨を書かない(指示通り)。USER_DECISION_REQUIRED項目は
無し(本Trial自体はユーザーの事前Trial承認範囲内で完結)。

---

## §8 参照

- `docs/pm/recon_en_asr_semantic_equivalence_01.md`
- `docs/pm/recon_en_asr_semantic_equivalence_02_tier2_tier3.md`
- `EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`(Part 2、Phase A/B
  承認範囲)
- `er021_en_asr_semantic_equivalence_trial_01.py` / `_run.py` /
  `_test_01.py`
- `er021_output/en_asr_semantic_equivalence_trial_01/`(corpus.jsonl、
  results/trial_results.json、audit/raw_usage_log.jsonl、
  audio/probe_*.wav)
- `er020_output/tts_local_rewrite_production_wiring_01/a2/
  comment_test2_probe.json`(既存probe、再生成せず再判定に利用)
- `er006_preprod_hardening_01_validation_test.py`(既存59件fixture)

---

Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-TRIAL-01
