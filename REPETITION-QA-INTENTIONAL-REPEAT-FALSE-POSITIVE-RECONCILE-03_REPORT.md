# REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-03

**管理ID**: REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-03
**種別**: 原因調査 + offline最小修正prototype(隔離scratchpad、Production/repoコード変更なし)
**実行者**: sonnet-worker(Fable委任、初回)
**日付**: 2026-09-12
**費用**: ¥0(新規TTS/ASR/API呼び出しなし。既存音声・既存監査JSON・既存コードの読取専用解析、および隔離scratchpad上でのoffline python実行のみ)

---

## 1. Family

Discovery Generalization Trial-12(`FAMILY-A-DISCOVERY-GENERALIZATION-WAKE-BEFORE-ALARM-NPLUS1-TRIAL-12_REPORT.md`)、A2 `full_story_part1`。既存Production配線済みのRepetition QA(OPEN-121、`er011_open121_repetition_qa_production_01.py`)が対象。

## 2. 現象

`full_story_part1`が標準経路2回+fallback経路1回(合計上限3回)すべてNG→`STOPPED`。20分cool-down後の4回目観測(`TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01`)もNG。3回とも**同一のASRテキスト**(表記まで完全一致)であるにもかかわらず不合格になっており、TTS音声のばらつきではなく決定論的な誤判定が疑われた。

canonical_text(台本、正規に2回同じ句を含む意図的反復):
> "...Light helps this clock match the **twenty-four-hour day**. Regular sleep and wake times can also help. In a laboratory study, weak light and regular routines usually matched a **twenty-four-hour day**. They did not usually match shorter or longer days."

3attempt共通のASR書き起こし(faster-whisper、実際に確認された文字列。attempt1/2/fallback1で完全一致):
> "...Light helps this clock match the **24-hour day**. Regular sleep and wake times can also help. In a laboratory study, weak light and regular routines usually matched a **24-hour day**. They did not usually match shorter or longer days."

Repetition QA(方式A n-gram)が検知した反復span(3attemptとも同一パターン、`gap_seconds`のみ8.72〜8.92秒で微差):
```json
{
  "span_text": " 24 -hour  day.",
  "n_words": 3, "category": "phrase",
  "canonical_repeat_count": 0, "intentional": false, "flagged": true
}
```
方式D/D'(スペクトル自己相関)はいずれも`acoustic_flagged: false`/`flagged: false`(3attemptとも)。**不合格の原因は方式A(n-gram)のみ**であり、音声そのものの重複ではない。

## 3. 既存対策(reconcile対象)

- OPEN-121 intentional-repeat判定(`canonical_repeat_count>=2`で意図的反復とみなしAND-gateを通す)。
- OPEN-127(2026-09-08、`PRODUCTION_WIRED`): em dash前後無空白タイポによるtoken誤結合の修正。
- OPEN-121数字↔数詞同値化(2026-09-12ユーザー承認`APPROVED_FOR_PRODUCTION`、`REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-02_REPORT.md`): `two`〜`twelve`のみを対象に、canonical側・ASR側トークンへ`_NUM_WORD_TO_DIGIT_EN`辞書で同値変換(`er011_open121_repetition_qa_production_01.py` 379〜395行、`_normalize_token_numeric_equiv`)。
- 既知未対応: "%" vs "percent"表記不一致(`USER_DECISION_REQUIRED`のまま)。

## 4. 今回なぜ効かなかったか(根本原因、コード読解+offline再現で確定)

2026-09-12に承認・配線されたばかりの数字↔数詞同値化(上記)は、**今回のケースには構造的に無関係**であり、原因は2つの独立したギャップが重なったもの。

**(a) 数値レンジ外**: `_NUM_WORD_TO_DIGIT_EN`は`two`〜`twelve`(2〜12)のみが対象。"twenty-four"(24)はこの承認済みレンジの外。

**(b) トークン境界の非対称性(今回新たに特定、より根本的な原因)**: canonical側のtokenizer(`_normalize_tokens()`)は空白のみで分割する(`text.split()`)ため、ハイフン複合語"twenty-four-hour"は**1個のtoken**のまま残る。一方、実際のfaster-whisper word-level ASR出力は、発話された"24-hour"を**2個のtoken**("24"と、ハイフンが頭に付いたままの"-hour")に分割する(`_normalize_token()`は句読点`.,!?"'…`のみ除去し、ハイフンは対象外のため"-hour"のまま残る)。結果として、ASR側3-word span `["24","-hour","day"]`をcanonical側token列(1個の"twenty-four-hour"+"day")の中から完全一致検索しても**構造的に一致しえず**、`_canonical_repeat_count`が常に0になる。

offline再現(venvのpython、実モジュール`er011_open121_repetition_qa_production_01.py`をそのまま呼び出し、実際のcanonical_textを使用):
```
canonical token 37: 'twenty-four-hour'   (1トークンのまま、レンジ拡張だけでは解決しない)
canonical token 38: 'day'
canonical token 59: 'twenty-four-hour'   (正規の2回目)
canonical token 60: 'day'

ASR側 normalized tokens: ['match', 'the', '24', '-hour', 'day']
span = ['24', '-hour', 'day']
_canonical_repeat_count(span, canonical_tokens) = 0   ← 実際の監査記録と一致
```
すなわち、(a)だけを直しても(仮に24を辞書に追加しても)canonical側は依然として"twenty-four-hour"という1個の融合トークンのままなので一致しない。**数値↔数詞の同値化に加えて、ハイフン複合語のトークン分割対称性という別レイヤーの正規化が必要**、という点が新規の知見。

## 5. 一般化(既存flag記録の横断集計、¥0、offline)

`er011_output/**`・`er012_output/**`・`er003_output/**`・`er006_output/**`配下の全JSON(9,832ファイル)を走査し、Repetition QA方式A(`detect_ngram_repetition`と同一構造、`first_start_s`等のキーを持つ実データ)の`flagged=true`記録を重複排除して収集した(46件のユニークな過去flag)。

- 今回と同型(ASR側で数字+ハイフン付属語に分割される複合数詞パターン)の事例は、**今回の"24-hour day"1件のみ**(全記録中で他に0件)。過去のOPEN-121対応事例("after two months"・"After three months, sales")はいずれもハイフン複合語ではない単独の数詞であり、型としては別(2026-09-12承認済みの(a)レンジのみで解消済み)。
- 一方、真陽性(本物のTTS重複バグ、修正の影響を受けてはいけない事例)も複数確認: 例 `discovery_generalization_towels_trial_11/a2` `point_two`「A wash is not just clean or dirty.」(`canonical_repeat_count=1`、開始直後0.76秒間隔での再開=false-start型の実バグ)。
- 結論: 今回の型は**発生数としては現時点で単発**だが、原因が「ハイフン複合の綴り数詞(twenty-four-hour, thirty-minute, ten-year等の複合修飾語)」という一般的な英語表現パターンに起因するため、今後同種の記事テーマ(時間・期間・年齢等を複合修飾語で書く場合)で再発しうる、構造的に予見可能な failure mode である。

## 6. 結果(scratchpad prototypeによる検証、repoコード変更なし)

scratchpad上でのみ、次の狭い範囲の正規化を追加するprototypeを実装し検証した(判定閾値`canon_count>=2`自体は無変更):
- canonical側: token が`(twenty|thirty|...|ninety)-(one|...|nine)-(残り)`という3分割ハイフン複合パターンに一致する場合のみ、`["24"(算用数字), "残り"]`の2tokenへ分解する(例: "twenty-four-hour" → "24", "hour")。それ以外のハイフン複合語(例: "hobby-based", "self-directed")は一切変更しない。
- ASR側: token が単独の"-hour"のように先頭ハイフン+英字のみで構成される場合、先頭ハイフンのみを除去する(faster-whisperのtokenize artifact対策)。

検証結果(4テスト、すべて実モジュール関数・実データで確認):
1. 今回の誤flag事例: `canonical_repeat_count` 0→**2**(intentional=True、flagされなくなることを確認)。
2. 既知真陽性("A wash is not just clean or dirty.")への影響: token列・`canonical_repeat_count`とも**無変化**(=1のまま、真陽性は消えない)。
3. 無関係なハイフン複合語("hobby-based","self-directed"を含む文): token列が**完全に同一**(この修正の影響を一切受けないことを確認)。
4. `full_story_part1`全文相当のASR文字列を使った end-to-end simulation: 現行Production同一ロジックでは`flagged: true`(バグを再現)、prototypeでは`flagged: false`(解消)。

**scratchpad未実施・既知の限界(honest scope note)**: 本prototypeは「tens語-ones語-付属語」という3分割ハイフン複合パターンにのみ反応する狭い実装であり、付属語を伴わない単独の2語複合数詞(例: 本文中に"twenty-four"単体が現れる場合)や、13〜99の範囲全般・序数・"%"↔"percent"は依然として対象外(既存の`USER_DECISION_REQUIRED`のまま)。範囲拡張の要否は別途ユーザー判断が必要。

cool-down観測データ(`er011_output/tts_cooldown_observation_01/observations.jsonl`、`run_id: 771b0033-...`)への影響: 3attemptの`ng_category`はいずれも`NORMALIZED_MATCH`(音声classification自体は正常)であり、不合格の実体は本件のRepetition QA決定論的誤flagである。4回目(20分cool-down後)も同一canonical_textに対する再試行のため、TTS品質のばらつきではなく同一の決定論的誤判定が再発した可能性が高い(4回目単体のrepetition_qa_evidenceは別ファイルとして保存されていないため断定はできないが、`fourth_attempt_reason`が3attemptと同じ「ASR検証不合格」という一般記述であることと矛盾しない)。**観測記録自体(`observations.jsonl`)は改変していない**。今後この記録を時間効果(cool-down効果)の分析母集団に含める場合は、`failure_type=repetition_qa_deterministic`として他のTTS品質由来NGと層別することを推奨する(層別自体も本タスクでは実施していない、提案のみ)。

## 7. Production判断が必要か

**必要**。以下はいずれも人間ユーザーの承認なしに実装していない(Trial/prototypeのみ、`APPROVED_FOR_PRODUCTION`ではない):

1. 上記prototype(ハイフン複合数詞のトークン分割対称化)を`er011_open121_repetition_qa_production_01.py`へ実装するか。
2. 実装する場合、対象範囲を「tens-ones-付属語」の3分割パターンに限定するか、それとも単独の複合数詞(付属語なし)・13〜99全域まで広げるか。
3. 広げる場合、対象記事(A-Family既存Production経路`er003_v1_n3_01_tts_generate.py`も同一tokenizer関数`_normalize_tokens`を共有するため影響範囲を含む)への影響評価・試聴要否。
4. 直近の対応として、Human Reviewキューにある本件`full_story_part1`(STOPPED)を、(a)本prototypeをuser承認のうえ正式実装してから再生成する、(b)既存Human Review機構(`review_lock.approve_regenerate`)で人間が現在の音声を確認して承認する、のどちらの経路を取るか。

## 参照ファイル

- `er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/audit/tts_generation_results.json`(`full_story_part1`セクション、3attempt分のrepetition_qa_evidence)
- `er011_output/tts_cooldown_observation_01/observations.jsonl`(`run_id: 771b0033-0df6-45f0-8995-c1ac10e78485`)
- `er011_open121_repetition_qa_production_01.py`(345〜531行、方式A実装・既存コメント)
- `REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-02_REPORT.md`(前回reconcile、2026-09-12承認済み数字↔数詞同値化の経緯)

---

## 修正1回目: failure mode一般化

**実行者**: sonnet-worker(Fable委任1回目)。**費用**: ¥0(新規TTS/ASR/API呼び出しなし、venv上でのoffline python実行のみ、repoコード変更なし)。

### 1. failure modeの一般化定義

「Repetition QAの反復比較で、canonical(TTS前処理後)とローカルASR書き起こしの**トークン化・数表記が非対称**になる」クラスを、**対称正規化層**として設計した(canonical側・ASR側の両方に同一の正規化規則を適用、閾値`canon_count>=2`・判定意味は無変更)。

- **(i) dash統一**: em dash(—)・en dash(–)は既存OPEN-127のem dash処理と同じく、前後の空白有無を問わず常に空白へ置換(既存承認済み処理をen dashへ拡張)。ハイフン(-)は複合語(twenty-four-hour、hobby-based、10-minute、mid-2020s等)を作る用法が主のため、**英字/数字が隣接する境界のみ**空白化(`(?<=[A-Za-z])-(?=[A-Za-z]|[0-9])`・`(?<=[0-9])-(?=[A-Za-z])`)。**digit-digit境界(例: "10-15"という範囲表記)は明示的に除外**(無関係な数字対を誤結合するriskを避けるため。ユーザー例示[単独複合数詞・13〜99・10-minute nap・mid-2020s]はいずれもletter-digit/letter-letter境界のみで、digit-digit境界を含む実例は確認されていない)。
- **(ii) 数詞同値化の拡張(0〜999)**: 既存の専用辞書(two〜twelveのみ、`_NUM_WORD_TO_DIGIT_EN`)を廃止し、**Production既承認・稼働中のASR Validator側の実装**(`er006_preprod_hardening_01_validation.py`の`_ONES`/`_TENS`/`_SCALES`/`_words_to_number`/`_NUM_WORD_VOCAB`、`normalize_numeric()`内の`_convert_cardinal_words()`と同一アルゴリズム)をそのまま再利用する設計とした(重複実装によるバグ・語彙drift混入を避けるため)。canonical側は複数tokenの数詞列(例: "twenty four" → "24"、"one hundred twenty" → "120")を1つの算用数字tokenへ畳み込む。ASR側はタイムスタンプ保持のため複数token統合はせず、単一token単位での数詞→算用数字変換のみ(0〜99、"one"は代名詞曖昧性のため既存方針通り除外)。circular import: `er011_open121_repetition_qa_production_01.py`から`er006_preprod_hardening_01_validation`への直接importは、依存グラフを実地確認した結果**循環importなし**(既存コメントが懸念する循環は`er003_v1_n3_01_tts_generate`経由の別ルートであり、er006直接importとは無関係)。
- **(iii) %/percent**: 明示的に対象外のまま(ユーザー指示通り、範囲拡張しない)。
- **序数(first〜ninety-ninth)**: **今回は対象外と判断**。根拠: (a)実データの過去flag記録の再走査(下記4節)で序数起因の誤flag事例が1件も見つからなかった、(b)日付の序数読み上げは既存の別機構(ER-010日付safe-reading)でTTS入力段階から扱われており、Repetition QA側での序数正規化ニーズの実例的根拠が薄い、(c)含めると基数(three)と序数(third)の意味の違いを吸収してしまうリスク(既存`_convert_ordinal_words()`が基数と序数を明確に区別する設計思想と整合しなくなる)。実例が出た場合は別途reconcileすることを推奨(pinのみ、実装なし)。

### 2. scratchpad prototype検証結果(実データ・実モジュール関数を使用、venvのpython、repoコード変更なし)

**(a) 今回のTrial-12 4 attempt**: `full_story_part1`の実canonical_text・実asr_text(監査JSON記載どおり)を使い、記録されている「24」「-hour」の2トークン分割artifactを再現したword-level構造で3件(標準2回+fallback1回、監査JSONにevidenceが残る全件)を再判定。**3件ともcanon_count 0→2、flagged True→Falseに解消**。4回目(20分cool-down後観測)は per-segment repetition_qa_evidenceが別途保存されていないため直接の再判定はできないが、同一canonical_textに対する同一の決定論的バグのため同様に解消される見込み(前回報告時と同じ限界、断定はしない)。

**(b)(c) 過去flag記録・過去PASS記録の再判定**: `er011_output/**`・`er012_output/**`・`er003_output/**`・`er006_output/**`(7,202ファイル、初回報告の9,832件とは走査条件が異なるため単純比較不可、正直に別数として記載)を再走査し、方式Aの`flagged`付きmatchレコードを収集(79件、`span_text`+`category`でユニーク化すると**6パターン**に集約。初回報告の「46件」とは重複排除基準が異なるため直接比較不可)。各パターンについて、記録されているcanonical_text(または同一segmentの別ファイルから実際に取得したcanonical_text)を使い、現行Production関数(`prod._normalize_tokens`)とprototype関数の両方でcanonical_repeat_countを実際に計算し比較した:

| パターン | span_text(抜粋) | 現行Production | prototype | 判定 |
|---|---|---|---|---|
| 真陽性1(towels A2 point_two) | "A wash is not just clean or dirty." | count=1(flag) | count=1(flag) | **変化なし(真陽性維持)** |
| 真陽性2(known positive fixture) | "Young travelers are not one single market...famous tourist places." | count=1(flag) | count=1(flag) | **変化なし(真陽性維持)** |
| 真陽性3(known positive fixture) | "The direction is visible...travelers want." | count=1(flag) | count=1(flag) | **変化なし(真陽性維持)** |
| 既に解消済み1(RECONCILE-02適用後) | "after two months." | count=2(pass) | count=2(pass) | 変化なし |
| 既に解消済み2(OPEN-127適用後) | "do not need" | count=2(pass) | count=2(pass) | 変化なし |
| **今回の対象バグ** | "24 -hour day." | count=0(flag) | **count=2(pass)** | **解消** |

真陽性が1件も消えないこと・既存PASSが変化しないことを実データで確認した。

**(d) 負例テスト(自作23件、20件以上の要件を満たす)**: 数字を含まない無関係ハイフン複合語(hobby-based/self-directed/state-of-the-art)、桁が異なる数字の言い直し(24 vs 48)、序数の巻き込まれ確認、%/percent非同値化の確認、digit-digit範囲("10-15"・電話番号形式)の除外確認、hundred/thousand複合数詞の真陽性、em/en dash無関係箇所の真陽性、を含む23件すべてで**誤PASS 0件**(全件正しくflagged=Trueのまま)。

**(e) 既存Repetition QAテスト(35件)への影響**: 本番モジュールの2関数(`_normalize_tokens`・`_normalize_token_numeric_equiv`)をprototype版へ実行時差し替え(monkeypatch、repoファイル変更なし)して35件を再実行した結果、**33件PASS・2件FAIL**。FAILした2件は狭いスコープを固定するために意図的に書かれたpinテストであり、想定内・意図した帰結:
  - `test_c_hyphen_en_dash_percent_numeric_cases_unchanged`: "well-known"がハイフンで割れず1tokenのままであることをpinしている → 今回の(i)により2tokenへ分割されるため、この特定のアサーションはスコープ拡大の直接的な結果として更新が必要。
  - `test_e_range_boundary_one_twelve_thirteen`: "thirteen"が無変換のままであることをpinしている → 今回の(ii)の範囲拡張(2〜12 → 0〜999)により意図的に"13"へ変換されるため、同様に更新が必要。
  - 残り33件(em dashの意図的並行構文検知、二重ハイフン/%数値の他アサーション、方式D/D'、Gate接続、scope制限等)は無修正のままPASS。

### 3. 追加の発見(スコープ外、報告義務に基づき提示、実装はしていない)

corpus再走査中、実データ(`er011_open112_trend_theme2_b_final_audio_rerun_02`のASR生データ)で、**数字を含まないハイフン複合語("hobby-based")も、"24-hour"と全く同じ構造的バグ("hobby"と"-based"の2トークンへの分割、canonical側は1トークンのまま)を持つ**ことを確認した(7,781ファイルの実ASR word-level出力を走査し、ハイフンが1個のtoken内部に残るケースは0件、常に次tokenへの先頭ハイフンartifactとして現れることも確認)。これは今回ユーザーが提示した4類型([twenty-four単体]・[13〜99]・[10-minute nap]・[mid-2020s])よりもさらに広い「ハイフン複合語全般」に及ぶ根本原因であり、上記(i)の一般化案はこれも副次的に解消する(2節・4節(d)(e)で実証済み)。この追加スコープの是非(数字以外のハイフン複合語まで含めるべきか)は、狭い案では対応できない差分としてユーザー判断を仰ぐ。

### 4. 狭い案 vs 一般化案のQCD比較+推奨

| 観点 | 狭い案(初回prototype、tens-ones-付属語3分割のみ) | 一般化案(今回prototype) |
|---|---|---|
| Q(再発防止力) | 低い。今回の"24-hour"型のみに特化。単独複合数詞・13〜99単体・10-minute・mid-2020s・hobby-based型はいずれも未解消のまま再発しうる | 高い。ユーザー提示4類型+corpus実データで新規発見した非数字ハイフン複合語まで一括解消。既存2-12専用辞書の重複実装(将来drift risk)も解消 |
| C(実装コスト) | 低い。正規表現1つ追加のみ、既存35テストへの影響ゼロ(狭いスコープのため) | 中。既存2件のpinテスト更新が必要(スコープ拡大の直接的帰結)、新規23負例+8正例のテスト化、`er006`への新規import1行(循環なし確認済み) |
| D(納期・意思決定コスト) | 速い | やや長い(pinテスト2件の期待値更新方針についてユーザー判断が必要) |
| 誤PASSリスク | 低い(スコープが狭いため副作用面も少ない) | 実測0件(23負例)だが、対象範囲が広い分、本番全記事への適用前の追加試聴確認の要否は別途要検討 |

**推奨: 一般化案**。ユーザー方針(個別対応禁止・failure mode単位で閉じる)に直接合致し、実データで「狭い案では対応できない別のハイフン複合語バグ(hobby-based型)」の実在を確認済みのため、狭い案を採用すると近い将来RECONCILE-04・05という形で同種の差し戻しが繰り返される可能性が高いと判断する。

### 5. Production採用時の変更点候補(未実装、**採用判断はユーザー**)

対象ファイル: `er011_open121_repetition_qa_production_01.py`(345〜395行付近)。

1. `import er006_preprod_hardening_01_validation as en_validator` を追加(循環importなし、確認済み)。
2. `_NUM_WORD_TO_DIGIT_EN`(2〜12専用辞書)を廃止し、`en_validator._ONES`/`_TENS`/`_SCALES`/`_words_to_number`/`_NUM_WORD_VOCAB`を利用した`_fold_cardinal_words()`(canonical側、複数token統合、0〜999+対応)を追加。
3. `_normalize_tokens(text)`を「(i)em/en dash無条件空白化+hyphen境界(英字/数字隣接、digit-digit除く)空白化 → (ii)`_fold_cardinal_words()` → 既存`dq18._normalize_token`」の順に差し替え。
4. `_normalize_token_numeric_equiv(word)`(ASR単一token用)を「(a)先頭dash artifact除去 → (b)`dq18._normalize_token` → (c)単一token数詞→算用数字(0〜99、"one"除外)」へ拡張。
5. 既存2件のpinテスト(`test_c_hyphen_en_dash_percent_numeric_cases_unchanged`・`test_e_range_boundary_one_twelve_thirteen`)を新スコープの期待値へ更新。
6. 新規テスト追加(今回作成した23負例+8正例パターンをテストケース化)。
7. `CURRENT_SPEC.md`追記文(案): 「OPEN-121 Repetition QA: canonical/ASR双方のtoken正規化に、em/en/hyphen dash境界統一(複合語対応)+英語基数詞0〜999の算用数字同値化(既存2〜12域を拡張、`er006_preprod_hardening_01_validation.py`のcardinal word変換ロジックを再利用)を追加。%/percent同値化・序数(first〜ninety-ninth)は引き続き対象外(実例なし、別途判断待ち)」。

**採用判断が必要な理由**: (ii)の数値範囲拡張(2〜12→0〜999)は既承認(2026-09-12 RECONCILE-02)と同じ原理(表記ゆれの吸収、判定意味不変)の延長とみなせるが、既存pinテストの明示的な期待値変更を伴う。(i)のdash境界統一は、既承認のem-dash限定処理(OPEN-127、2026-09-08)を超えてハイフン・en-dashへ適用範囲を広げる**新規仕様**であり、単純な延長とは言えない。したがって(i)は新規承認、(ii)は範囲拡張として明示的承認が、それぞれ必要と判断する。

### 参照ファイル(追加)

- `er006_preprod_hardening_01_validation.py`(90〜316行、`_ONES`/`_TENS`/`_SCALES`/`_words_to_number`/`_convert_cardinal_words`、既存Production ASR Validator実装)
- `er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/point_two_showed_show_diag/diag_raw_evidence.json`(hobby-based型の実ASR word-level分割artifact、非数字ハイフン複合語の同型バグ発見箇所)
- `er011_output/discovery_generalization_towels_trial_11/a2/audit/tts_generation_results.json`・`.../b1b/audit/human_review_resume_04_results.json`(真陽性・既解消ケースのcanonical_text)
- `er011_open121_tts_repetition_general_qa_trial_01.py`(140〜154行、known positive fixture用canonical_text定義)
- `er011_open121_repetition_qa_production_wiring_01_test_01.py`(既存35テスト、監視対象)
