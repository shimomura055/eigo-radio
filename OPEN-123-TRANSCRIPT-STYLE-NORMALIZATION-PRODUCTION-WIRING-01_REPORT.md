# OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01

管理ID: OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01。
Lane: Lane A。種別: Production配線(ユーザー2026-09-07正式決定:
(1)方式(i)標準contraction展開を`APPROVED_FOR_PRODUCTION`、範囲=**英語ASR
照合経路全体**[Key Phrase英語経路を含む、A2/B1本文に限定しない]。
(2)wanna系[方式iv]は**不採用**[現状維持、正規化しない])。
到達Status: **コード実装・Runtime evidence・回帰いずれも完了。Git操作は
未実施**(Fableの統合commit後に`PRODUCTION_WIRED`を正式宣言する)。

採用元: `OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md`§13
(`VALIDATED`)。判定ロジック(標準contraction展開後に既存Validatorが
実際にPASSと判定した場合のみ採用)はTrialから無変更で移植した。

---

## 1. 配線場所

`er006_preprod_hardening_01_validation.py::classify_asr_match()`自体を
薄いラッパーへ変更した。既存の分類本体(Trial時点まで無変更だった
`classify_asr_match()`の中身、`normalize_text()`/`tokenize()`/
`protected_check()`/homophone・数字ゲート・Connected Speech Validator
呼び出しを含む全ロジック)は、そのまま`_classify_asr_match_core()`という
名前へリネームしただけで**内容は一切変更していない**。公開関数
`classify_asr_match()`は以下の手順を踏む新規ラッパーとして追加した:

1. `_classify_asr_match_core()`をbaselineとして呼ぶ。
2. `baseline.should_pass`が`True`ならそのまま返す(介入しない)。
3. `False`の場合のみ、新規`expand_standard_contractions()`をcanonical_
   text/asr_text両方の生text段階へ適用する。
4. どちらの側も変化しなければ(元々contractionが無ければ)baselineを
   そのまま返す(無駄な再帰・無限再帰の防止)。
5. 展開後のtextで`_classify_asr_match_core()`を再度呼び(展開は1回で
   収束するテーブルのため、この再帰呼び出しは必ず1段で終わる)、その
   結果が`should_pass=True`であった場合のみ新規classification
   `TRANSCRIPT_STYLE_NORMALIZED_MATCH`(`VALID_CLASSIFICATIONS`へ追加、
   `should_pass=True`・`should_retry=False`)として採用する。それ以外は
   baseline(既存の分類・reason)をそのまま返す。

**新規opt-inフラグは追加していない**。OPEN-119/OPEN-122のような
`enable_*`フラグパターンではなく、`classify_asr_match()`という関数名
自体を変更せず内部だけを差し替えたため、この関数を呼ぶ既存の全経路
(`evaluate_attempt()`→A2/B1本文・Key Phrase英語経路[`generate_key_
phrase_component_verified()`]・homophone/数字ゲート・Connected Speech
Validator[3パターン]・OPEN-122 Connected Speech Equivalence Layer
[独立のopt-inフラグ]のいずれとも独立)へ、追加のコード変更無しで共通
適用される。これはユーザー決定の採用範囲が「英語の共通正規化」= A2/B1
本文に限らず英語ASR照合経路全体であるという指示に基づく意図的な設計
選択である。

---

## 2. 採用した集合(全リスト)

否定を保持したまま縮約⇔展開するペアのみ(否定反転・口語的縮約は一切
含まない、Trial §13どおり)。

**否定保持contraction(17語、`_NEGATION_CONTRACTIONS`)**:
`don't`→do not、`doesn't`→does not、`didn't`→did not、`isn't`→is not、
`aren't`→are not、`wasn't`→was not、`weren't`→were not、`hasn't`→has
not、`haven't`→have not、`hadn't`→had not、`can't`→cannot、`won't`→will
not、`wouldn't`→would not、`shouldn't`→should not、`couldn't`→could
not、`mustn't`→must not、`needn't`→need not、`shan't`→shall not。

**非否定contraction(24語、`_NON_NEGATION_CONTRACTIONS`)**:
`i'm`/`you're`/`we're`/`they're`/`he's`/`she's`/`it's`/`that's`/
`there's`/`who's`/`what's`/`here's`/`i've`/`you've`/`we've`/`they've`/
`i'll`/`you'll`/`he'll`/`she'll`/`we'll`/`they'll`/`it'll`/`i'd`/
`you'd`/`he'd`/`she'd`/`we'd`/`they'd`/`let's`(展開先はis/are/have/
will/would/us等の完全形)。

**含まれないもの(意図的に対象外)**: "can"⇔"can't"のような否定反転
(意味反転は絶対に含めない)、"want to"⇔"wanna"・"going to"⇔"gonna"・
"got to"⇔"gotta"のような口語的縮約(方式iv、ユーザー決定により不採用)。

's/'d(is/has・would/had)の曖昧性は、Trialの設計どおりテーブルに含めた
まま採用した(理由: 誤った解釈を選んでも「展開後に既存Validatorが実際に
PASSと判定した場合のみ採用」という設計により、単に展開後も一致しないまま
残るだけで安全側に倒れるため。§4のRuntime evidence(c)・新規単体テストで
構造的に確認済み)。

---

## 3. Runtime evidence表(a〜d)

| # | 内容 | 結果 | 証跡 |
|---|---|---|---|
| (a) 既知false reject | Trial-08 P3 point_two(3回STOPPED、do not/don't)の保全音声3件+実Primary ASR結果を、実Production関数(`classify_asr_match()`単体、`evaluate_attempt_with_cascade_detail()`実wav_path経由)へ投入 | **3/3救済**(`TRANSCRIPT_STYLE_NORMALIZED_MATCH`、`verified=True`)。Primary#1時点でPASSするためCascade層の追加ASR呼び出しは**0件**(`cascade_invoked=False`、追加コストなし) | `er011_output/open123_transcript_style_normalization_production_wiring_01/gate_a_trial08_p3_result.json`、実行script`gate_a_trial08_p3_runtime_evidence.py`(同ディレクトリ) |
| (b) 既存Regression fixture | POSITIVE29+AMBIGUOUS2+NEGATIVE28=57件を実際の`classify_asr_match()`へ通す | 全57件が期待通り。NEGATIVE28件は`TRUE_CONTENT_MISMATCH`のまま非救済(false accept 0)。POSITIVE中"they're"/"we're"2件が`ASR_VALIDATION_UNCERTAIN`→`TRANSCRIPT_STYLE_NORMALIZED_MATCH`へ改善 | `er006_preprod_hardening_01_validation_test.py`実行結果(本Report作成時に直接実行、全57件OK) |
| (c) Key Phrase英語経路 | 実preserved KP音声5件(`er003_output/b1_p9a/A02/key_phrase_components/`、opt out/covered apps/urge to watch/personalized feed/digital switch-off period、いずれもcontractionなし)をKey Phrase呼び出しと同じkwarg(`enable_non_latin_cascade=True`)で`evaluate_attempt_with_cascade_detail()`へ投入。加えて、contraction入りKey Phraseの実データが無いため、canonical/ASR textのみ合成(音声は実物preserved wav 1件を流用、合成であることを明記)した2件(救済されるべきケース1件・can/can't否定反転で救済されてはいけないケース1件)を追加確認 | 実データ5件は既存PASS(`verified=True`)が**一切変化しない**ことを確認(`part1_ok=True`)。合成2件は想定通り(救済/非救済とも正しい、`part2_ok=True`)。**想定外の挙動は0件**(STOPPは不要だった) | `er011_output/open123_transcript_style_normalization_production_wiring_01/gate_c_key_phrase_result.json`、実行script`gate_c_key_phrase_runtime_evidence.py`(同ディレクトリ) |
| (d) wanna系非救済 | OPEN-122 Trial-01の実測音声(P6_dont_you、"Don't you want to come with us?"の実発話、Primary ASRが実際に"wanna"と誤書き起こしした実データ)を、`classify_asr_match()`単体および`evaluate_attempt_with_cascade_detail()`(opt-inフラグ一切無し)へ投入 | **非救済のまま維持**(`classification=TRUE_CONTENT_MISMATCH`、`should_pass=False`、`verified=False`)。OPEN-122 Equivalence Layerで救済されるかは別層の話であり本層とは独立 | `er011_output/open123_transcript_style_normalization_production_wiring_01/gate_d_wanna_result.json`、実行script`gate_d_wanna_not_rescued_runtime_evidence.py`(同ディレクトリ) |

---

## 4. 回帰結果

`run_project_regression.py`(canonical entry point、venv `.venv/Scripts/
python.exe`使用): **collected=2157、passed=2154、failed=3、errors=0**。
failed 3件は本タスク以前から存在する既知の無関係failure
(`er003_test_bad`の意図的self-check・`er003_test_p2j_investigate`の
OPEN-77既知meta-test集計、いずれもASR/Validator/音声とは無関係な別
ドメインのfixtureであることをOPEN-122タスク時点で既にソース確認済み、
本タスクでも再確認)。新規テスト19件がglob patternに自動的に拾われ、
collected数が本タスク着手前(2138)から+19件増加している。

直接実行で確認した関連テスト(回帰globに含まれない`_test.py`終端の
ファイルを含む):

| ファイル | 件数 | 結果 |
|---|---|---|
| `er006_preprod_hardening_01_validation_test.py` | 57 | 全PASS |
| `er006_secondary_asr_01_test.py` | 29(訂正: 原記載「9」は転記ミス。`PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01_REPORT.md`で`def test_`実数29件・`__main__`呼び出し29件を確認、実行結果[全PASS]自体は正しい) | 全PASS |
| `er007_ja_secondary_asr_01_test.py` | 9 | 全PASS |
| `er011_no18_connected_speech_reading_resolver_wiring_08_test.py` | 15 | 全PASS |
| `er011_tts_attempt_audio_retention_wiring_01_test.py` | 9 | 全PASS |
| `er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py` | 5 | 全PASS |
| `er011_connected_speech_equivalence_layer_production_wiring_01_test_01.py` | 16(訂正: 原記載「8」は転記ミス。`PM-LANE-A-PRODUCTION-WIRED-FINAL-ACCEPTANCE-AUDIT-01_REPORT.md`で`def test_`実数16件・`__main__`呼び出し16件を確認、実行結果[全PASS]自体は正しい) | 全PASS |
| 新規`er011_transcript_style_normalization_production_wiring_01_test_01.py` | 19 | 全PASS |

**既存テストファイルのmock signature更新は一切不要だった**(`classify_
asr_match()`の呼び出しシグネチャ・引数を変更していないため、OPEN-119/
OPEN-122のような新規kwarg追加に伴う既存test修正は今回発生しなかった)。

新規19件の内訳: 救済確認5件(標準contraction・非否定contraction・
Trial-08実データ・介入しないケース2件)、安全性確認7件(否定反転can/
can't・will/won't・動詞屈折asked/asks・wanna・曖昧's/'dの誤解釈2件・
正しい解釈1件)、共通経路確認4件(`VALID_CLASSIFICATIONS`・`evaluate_
attempt()`wav非依存・Key Phrase呼び出しパターンでの救済/非救済各1件)、
日本語独立性確認3件(ソースレベルimport非存在の直接確認2件+モジュール
docstring確認1件)。

---

## 5. model/routing/cost

本タスクはローカル文字列処理(正規表現によるcontraction展開)のみで、
新規のTTS/ASR API呼び出しは一切行っていない。Runtime evidence(a)(c)(d)は
いずれも既存の保全済み音声・保存済みmanifest.json(Trial-08・Key Phrase
Production資産・OPEN-122 Trial-01)を再利用し、`classify_asr_match()`
または`evaluate_attempt_with_cascade_detail()`へ投入した際もPrimary#1
時点で判定が確定するため追加ASR呼び出しは発生しなかった(`cascade_
invoked=False`を全evidenceで確認)。

**cost実測: ¥0**(上限¥300、追加API課金なし)。TTS実行modeの指定は
不要だった(新規TTS生成を一切行っていないため)。

---

## 6. 未対応・USER_DECISION_REQUIRED

新規のUSER_DECISION_REQUIREDは発生していない。既存のOPEN-123行に記録
済みの未決事項を、Production wiring後の状態へ更新して維持した:

1. **Verb-Inflection Normalization("asked"↔"asks"型)は本層の対象外の
   まま**。動詞屈折はcontraction展開の対象外の別failure modeであり、
   本タスクでも意図的に混同していない(新規単体テストで非救済を確認)。
2. **P3 Voice B(point_two、三人称版)のHuman Review承認可否**は依然
   ユーザー試聴待ち(§3(a)で当該音声が本Production関数により3/3救済
   されることは確認済みだが、segment音声自体の最終採否はユーザー試聴に
   委ねる、overrideは実施していない)。
3. **b05型のSecondary/Local書き起こし非対称性**(Trial§8で発見、
   口語台本をSecondary/Local ASRが正書法へ書き換える現象)の独立調査は
   本タスクの範囲外のまま。
4. **Key Phrase経路での実データ自然発生contraction救済の実測はまだ0件**
   (母集団が無いため、今後の実記事生成を通じて継続観測)。

いずれもユーザー承認なしに実装しない。

---

## 7. Git

**未実施**。タスク仕様により、本タスクではコード変更・テスト追加・
Runtime evidence取得・SSOT更新のみを行い、commit/pushは一切行っていない。
Fableが統合commitを行った後に`PRODUCTION_WIRED`を正式宣言する。

### 変更ファイル一覧(新規)

- `er011_transcript_style_normalization_production_wiring_01_test_01.py`
  (新規、単体テスト19件)
- `er011_output/open123_transcript_style_normalization_production_
  wiring_01/`配下(Runtime evidence一式: 実行script3件・結果json3件)
- `OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01_
  REPORT.md`(本ファイル)

### 変更ファイル一覧(既存編集)

- `er006_preprod_hardening_01_validation.py`(Transcript Style
  Normalization配線本体: `_NEGATION_CONTRACTIONS`/`_NON_NEGATION_
  CONTRACTIONS`/`expand_standard_contractions()`を新規追加、既存の
  `classify_asr_match()`を`_classify_asr_match_core()`へリネーム[中身は
  無変更]、新規`classify_asr_match()`薄いラッパーを追加、
  `VALID_CLASSIFICATIONS`へ`TRANSCRIPT_STYLE_NORMALIZED_MATCH`追加)
- `CURRENT_SPEC.md`(最終更新ヘッダへ新規エントリ追加、「Audio
  Production Pipeline」節へ新規行「Transcript Style Normalization」
  追加)
- `DECISION_LOG.md`(新規セクション`## OPEN-123-TRANSCRIPT-STYLE-
  NORMALIZATION-PRODUCTION-WIRING-01`追加)
- `OPEN_ITEMS.md`(OPEN-123行を更新: Trial結果+Production wiring結果を
  追記、status`USER_DECISION_REQUIRED`→`CODE_COMPLETE_PENDING_COMMIT`)

**日本語経路(`er007_*`)・OPEN-121担当ファイル(`er011_open121_*`・
`er011_output/open121_*`・`er008_disfluency_qa_18.py`・`er003_v1_n3_
01_tts_generate.py`)は一切編集していない**(§1・新規テストのソース
レベル確認テストで証明済み)。
