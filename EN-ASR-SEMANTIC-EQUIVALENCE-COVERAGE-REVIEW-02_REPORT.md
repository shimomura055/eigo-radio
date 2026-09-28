# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT

管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02
日付: 2026-09-28(Phase 1)/2026-09-28(Phase 2)
Phase: 1(原因分析+coverage再監査+設計案)完了 → **2(Production実装、
本REPORT末尾のPhase 2節参照)完了、Mandatory Opus L3診断待ち**
Status: **Phase 1 DESIGN_COMPLETED(Opus L2レビュー実施済み、ユーザー
`APPROVED_FOR_PRODUCTION`承認済み) / Phase 2 IMPLEMENTATION_COMPLETE、
Opus L3 REVIEW PENDING、`PRODUCTION_WIRED`はFable Gate 3判定待ち**
性質(Phase 1): ¥0・API呼び出しなし・Production code変更なし・SSOT本体
編集なし(Phase 1時点の記載、Phase 2はSSOT編集込み、詳細は末尾節参照)。
設計全文: `docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`
先行SSOT: `EN-ASR-SEMANTIC-EQUIVALENCE-REVIEW-01_REPORT.md`、OPEN-184
(CLOSED、本件へ吸収済み)、OPEN-186(WIRING IN PROGRESS)。

## 背景
Phase A+B(`APPROVED_FOR_PRODUCTION`2026-09-27)配線後も、canonical
"Act One" vs ASR "Act 1" がValidator NGとなり、retry→cool-down→Local
Rewrite(本文改変)経由でしか合格しない事象が現行モデル・Flash-Lite
双方で再現した(`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-
X-01_REPORT.md` Phase 3、Gate項目14)。個別fixture追加ではなく、
包括対策として設計し直せるかを本Phaseで調査した。

## 主要な発見(コード実行・実データで確認済み)
1. Tier 1(`er021_en_asr_semantic_equivalence_production_01.py::
   tier1_numeric_equivalence()`)の数値語パーサ自体は"Act One"⇔"Act 1"
   を正しく等価と判定する(単独評価で確認)。**判定ロジックの誤りでは
   ない**。
2. 実際に失敗する原因は、同一segment内に同居する**無関係な**2つの
   表記差が、Tier 1の「セグメント全体のatom数完全一致」という
   all-or-nothing設計により、正しい判定ごと握りつぶされるため:
   (a) 打点略語(`U.S.`が4 atomへ分裂 vs `US`が1 atom)、
   (b) 裸digit+日付序数接尾辞(`13` vs `13th`)。
   いずれも**旧Validator(`er006_preprod_hardening_01_validation.py`)
   側には既に安全な対処が存在する**(`despaced()`ratio救済、
   `_DATE_ORDINAL_RE`の月名限定正規化)が、Tier 1は循環import回避のため
   独立実装しており、この2つを継承し損ねていた。
3. telemetry(`er021_output/.../telemetry.jsonl`、4,187件)を
   オフライン再分類。distinct 43件の`protected_number`NGのうち、
   本パターンに該当するのは実質1記事(Hormuz、複数run/phaseで計15回
   NG再掲)。残り大多数(27件)は正しく保護された真の値相違であり、
   **Tier1の既存安全性(false accept 0)は毀損されていない**ことも
   確認した。
4. Trial-01 corpus(68件、平均6語/最大17語)には打点略語・日付序数の
   fixtureが0件で、かつ「1文=1事象」設計だったため、複数事象同時発生
   時のみ顕在化する本件の脆弱性は構造的に検出され得なかった。

## 分類
- **(A)既承認範囲内の実装是正**(新しい意味等価カテゴリを追加しない):
  打点略語のatom結合前処理/日付文脈限定の序数接尾辞吸収(旧Validator
  ロジックの移植)/Tier1比較アルゴリズムを「全体zip」から
  「diff-anchored(SequenceMatcherでopごとに既存の許容基準を適用)」へ
  変更/hyphenated numeric・alphanumeric entityのハイフン吸収/
  meridiem略記のatom結合/Trial corpusへの長尺・複合fixture追加。
- **(B)新しい意味等価ルール(USER_DECISION_REQUIRED、採用しない)**:
  日付文脈以外での裸digit序数接尾辞の一般吸収(基数/序数の意味差を
  壊すため)/複合語分かち書きをTier1へ複製/ローマ数字小文字許容。

## 推奨設計案
案1(現状+個別パッチのみ)/案2(個別パッチ+diff-anchored比較への変更)/
案3(意味parse層の全面刷新)を比較し、**案2を推奨**。理由: 今回の実例を
確実に解消しつつ、変更範囲が`er021`内部のみ(呼び出しシグネチャ・
role gate・telemetry・Tier3救済ロジックは無変更)、新しい許容ルールを
一切追加しないため既存のNEGATIVE安全性を維持したまま、「未知の3つ目の
穴」による同種再発を構造的に防げる。詳細は設計書§3。

## 全経路確認
初回・retry・fallback・Local Rewrite前後・Secondary ASR cascade・
Human Review Lock直前は、いずれも単一wrapper(`classify_asr_match()`)
と単一role gate関数を経由しており、**配線の不整合は無い**。Tier1本体
の修正のみで全経路へ同時に効果が及ぶ(設計書§4)。

## 詳細
`docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`
(E-1原因分析、E-2 coverage matrix[23カテゴリ、実行結果付き]、E-3設計案
比較、E-4全経路確認表、分類A/B、Positive/Negative test設計、Opus L2
申し送り8点、SSOT記載案)。

## 次のステップ(Phase 1時点)
Mandatory Opus L2レビュー(Fable発火)。本Phaseでは実装・Trial・
Production変更は一切行っていない。

---

# Phase 2: Production実装(2026-09-28、ユーザー承認`APPROVED_FOR_
PRODUCTION`: strict版Tier1合成規則+分類A技術修正)

## 背景
Mandatory Opus L2レビュー完了後、ユーザーが**strict版Tier1合成規則**
(同一segment内に複数の表記差が存在しても、英数字内容が一致しpunctuation
由来の局所差だけである場合はTier1で吸収する閉じた規則)を
`APPROVED_FOR_PRODUCTION`として承認した。あわせて分類A技術修正(既承認
範囲内の実装是正、追加判断不要)も承認された。委任文全文は
`docs/pm/delegation_log/2026-09-28_EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-
REVIEW-02_02.md`に保存済み。

**Opus L2所見(逐語)についての注記**: 本Phase 2委任として受領した内容には、
「先出しRead」に列挙された「Opus L2所見全文」の逐語テキスト自体は別添
されていなかった(delegation_log保存対象としてこのファイル自体に保存
するよう指示された文面のみを受領)。したがって本節は、委任文に記載
された「ユーザー承認仕様(逐語要旨)」および「分類A技術修正」の一覧を
実装対象の正としてそのまま採用しており、Opus L2の原文転記は行っていない
(捏造回避。Opus L2所見の実体はFable/ユーザー側にある想定)。

## 実装内容
`er021_en_asr_semantic_equivalence_production_01.py::tier1_numeric_
equivalence()`を、(a) 既存の全体完全一致判定(無変更、既存合格経路の
挙動は完全に同一)をまず試み、(b) 一致しない場合のみ`difflib.
SequenceMatcher(None, ca_keys, aa_keys, autojunk=False)`によるdiff-
anchored比較へフォールバックする方式へ変更した。非equalな各opは
`_closed_punctuation_diff_ok()`(strict版合成規則の実装)の閉じた基準
(差分atomはliteralのみ/両側の英数字内容が`re.sub(r"[^a-z0-9]","",…)`
で完全一致)を1つでも満たさなければ即座に全体非等価とする
(best-effort禁止)。「PASSする範囲は英数字内容完全一致に限定される」
という不変条件をassert文でも固定した。あわせてop数上限
(`_TIER1_MAX_ABSORBED_PUNCT_OPS=3`)・atom比率上限
(`_TIER1_MAX_ABSORBED_PUNCT_ATOM_RATIO=0.2`)を防御的に定数化した
(既存の閉じた判定を多重に補強するものであり、これ自体が新しいfalse
acceptの余地を広げるものではない)。

分類A技術修正:
- 月名文脈限定の裸digit序数接尾辞吸収(`_MONTHS`/`_DATE_ORDINAL_RE`を
  `er006_preprod_hardening_01_validation.py`からer021側へ移設し、
  er006は`semantic_equivalence._MONTHS`/`_DATE_ORDINAL_RE`を参照する
  だけに変更、複製ではなく共通化)。
- 序数語(third〜thirtieth、`_ORDINAL_WORDS`も同様にer021へ移設し
  er006が参照)をTier1のnumber atomへ`ordinal`フラグ付きで認識
  (基数atomとは区別、"28 vs 28th"の意味差は保護維持)。
- "per cent"(2語表記)を"percent"と同じ意味atomへ正規化。
- `_consume_number_word_run()`の"and"飲み込みparser bug修正(数値語run
  の先頭/末尾の"and"を除外、真の等価性を誤って握りつぶしていた既存
  false rejectを解消)。
- 単独ローマ数字"V"/"X"は閉じたラベル語(act/part/chapter/section/
  phase/version/book/volume/episode/step/movie/season)直後限定へ
  安全化(`_ROMAN_AMBIGUOUS_SINGLE`)。実装レビュー中に、この安全化前は
  "Model X"⇔"Model 10"のような組み合わせが**既存コードのまま**false
  acceptになり得る潜在バグだったことを発見し、本Phaseで併せて解消した。
- `_preprocess_raw()`のマイナス記号判定バグ修正: 既存の
  `(?<![\d])-(?=\d)`は文字直後のハイフンまで誤って" minus "化しており
  (例: "COVID-19"→"COVID minus 19")、hyphenated numeric/alphanumeric
  entityの吸収を妨げていた。「文字-文字」に加え「文字-数字」「数字-文字」
  の組を先に空白化するよう順序を変更し、マイナス記号判定はどちらの隣接
  文字でもない場合のみに限定した。
- meridiem略記(a.m./p.m.)は、"a"+"."+"m"+"."という分裂atom列を
  `_peek_meridiem()`で"am"/"pm"と同じmeridiem値へ正規化(時刻atom自体の
  閉じたスコープは変えない)。

## 設計書是正
`docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`を実装
レビュー結果に基づき是正した: §3.2比較表(前処理2パッチのみでも
Act One実例自体は解消できることを実装で確認、案2の真の価値は「未知の
punctuation差分への構造的耐性」であると訂正)、§1.5 Root Cause記述
(「継承漏れ」ではなく「意図的punctuation保持tokenizerとpunctuation除去
正規化[旧Validator]の間の未調整」と訂正)、§2.1 coverage matrix拡張
(「同一segment内で複数差分が共存するケース」#24-27を追加)、§4全経路
確認表(`er006_secondary_asr_01.py`のL395/L526間接呼び出し2箇所を追加)。

## test
既存corpus全件無回帰:
- Trial-01 corpus(POSITIVE 34/NEGATIVE 34、計68件): 全件PASS(直接
  スクリプトで再確認)。
- OPEN-123 Regression fixture(`er006_preprod_hardening_01_validation_
  test.py`、57件): 全件PASS(role gate適用状態、role gate非適用状態の
  両方)。
- 既存`er021_en_asr_semantic_equivalence_production_wiring_01_test_
  01.py`(既存29テスト、role gating・Tier1 corpus再実行・Tier3
  cascade統合・A2/B1配線回帰含む): 全件PASS。

新規追加(`StrictTier1SynthesisRuleTest`、25件、POSITIVE 11/NEGATIVE
14): ordinal語("third"↔"3rd")、"per cent"(2パターン)、"and"バグ修正
による真の等価性救済、meridiem略記、hyphenated numeric、alphanumeric
entity、月名限定序数吸収、Act One+US+日付序数の複合(Hormuz実例の再現、
PASS)、単独ローマ数字のラベル文脈あり/なし、"Model X"↔"Model 10"
NG、基数/序数("28"↔"28th")NG、US↔UK NG、概数↔正確値NG、
percent↔percentage points NG、ハイフン区切りコード("12-34")Tier1
非吸収、符号("-5"↔"5")Tier1非吸収、長尺(>200 atom)segmentでの
punctuation-only PASS、および合成negative群(文の丸ごと欠落・否定語
欠落・数値1桁違い・単位のみ相違・US↔UK・基数/序数非月名隣接、いずれも
punctuation差と同居させても救済されないことを固定)。**全54テスト
PASS(既存29+新規25)、false accept 0**。

他の関連test suiteも実行し無回帰を確認:
`er006_pronunciation_phase4_entity_like_test_01.py`(23件)、
`er010_entity_phonetic_corroboration_01_test_01.py`(22件)、
`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`
(15件)、`er011_transcript_style_normalization_production_wiring_01_
test_01.py`(19件)、`er021_en_asr_semantic_equivalence_trial_01_
test_01.py`(40件、Trial module自体は無変更)、
`er006_secondary_asr_01_test.py`・`er007_en_blindspot_test_01.py`・
`er011_connected_speech_equivalence_layer_production_wiring_01_
test_01.py`(script形式、いずれもPASS)。
**既知の無関係failure**: `er006_pool_benches_luna_audio_wiring_
test.py`が1件失敗するが、これは`er003_v1_sing01_news_tail_fix.py`が
現時点で`audio_validation`のimport文を含んでいないことを検出した
もので、Flash-Lite 02(衝突回避リストにより本タスクでは編集していない
ファイル)の作業途中の状態に起因する既知の無関係failureであり、本Phase
の変更(Tier1ロジック)とは無関係(コード上のimport文字列有無を静的検査
するテストであり、Tier1判定ロジックへは触れていない)。

## runtime evidence
**(a) 既存telemetryのオフライン再判定(¥0、read-only)**:
`er021_output/coverage_review_02/offline_telemetry_reclassify_01.py`で
既存telemetry(実装開始時点4,536件)全件を、Production wrapperと同じ
`tier1_numeric_equivalence()`で再判定した。

| 項目 | 件数 |
|---|---|
| 総record数 | 4,536 |
| Tier1 MATCHへ反転(reversal) | 7 |
| うちHormuz記事由来(同一記事の複数run/attempt再掲) | 7(100%) |
| 他sub_reason(content_word 1,802/protected_negation 168/
  entity_only 295/plural_only 396/homophone_only 56/low_ratio 6、
  計2,723件)の反転 | 0 |

**false accept 0を実データで確認**(反転はすべて既知のHormuz「Act One」
記事に由来し、真に値が異なる記録・他カテゴリの記録は一切反転していない)。

**(b) 実際のProduction artifactの再判定(¥0)**: `er011_output/local_
rewrite_recovery/hormuz__run_04_parallel_a/b1b/local_rewrite_
recovery_full_story_part1.json`のcanonical_text/last_asr_text(実際に
Local Rewrite前に不合格となった実データ)を、実際のwrapper関数
`val.classify_asr_match(canonical, asr, segment_id="full_story_
part1")`でそのまま再判定した。結果: `NUMERIC_EQUIVALENCE_MATCH`、
`should_pass=True`、`diff_anchored=True`、`absorbed_ops=1`(U.S./US
の1箇所のみ、"Act One"⇔"Act 1"は既存のcardinal語パーサで無差分一致、
"July 13"⇔"July 13"は今回のtelemetryでは日付序数差自体が発生していない
実データだった)。

**(c) 実TTS+実ASR runtime evidence(Guardrail¥15内)**:
`TTS_EXECUTION_MODE=STANDARD`、Human Review Lock非接触(out_pathを
narration層構造に一致させない設計、`_has_valid_narration_layout()`が
Falseであることをassertで確認)、`er003_v1_repro01_main_generate.
generate_narration_snippet_verified_strict.__wrapped__()`(既存Family
X runnerが内部で使う同一関数)を`segment_id="full_story_part1"`で
直接1回ずつ実行(max_attempts=1、tts_backend既定=structured_
separation、Flash-Lite関連ファイルは一切import・使用せず衝突回避)。

| 試行 | canonical | 実ASR結果 | 分類 | diff_anchored |
|---|---|---|---|---|
| 1回目 | "The U.S. government announced a 15 percent tariff increase this week." | "The U.S. government announced a 15% tariff increase this week."(U.S.表記はそのまま保持) | `NUMERIC_EQUIVALENCE_MATCH` | False(既存の完全一致経路) |
| 2回目 | "The report is divided into three parts. Part One covers the background." | "...Part one covers the background."(小文字化のみ、"one"はcardinal語として既存経路で一致) | `NUMERIC_EQUIVALENCE_MATCH` | False(既存の完全一致経路) |

model_id: `gemini-2.5-pro-preview-tts`、voice: `Aoede`。2回とも実際の
モデル出力がcanonicalと(cardinal語パーサの既存経路で)完全一致したため、
diff_anchored=True(新規則)自体はこの2回のライブ抽選では発火しなかった
(非決定的なASR/TTS出力の性質上、意図的にfalse accept方向へ誘導する
ことはできない。¥15 Guardrailの範囲内[2 segment]で追加のライブ抽選は
行わないこととした)。**新規則(diff_anchored=True)が実際のProduction
経路で発火することは、上記(b)の実際のHormuz Production artifact
(実TTS/実ASRで過去に取得済みの実データ)を同じ実wrapper関数で再判定
することで確認済みである**。詳細artifact:
`er021_output/coverage_review_02/runtime_evidence_live_tts_asr_01_
result.json`、`..._result_run2.json`。

## 定期offline検知レポート
`er021_offline_false_reject_detector_01.py`(read-only、¥0、判断を
含まない定型集計のためhaiku-worker委任可)を新設。telemetry NG record
を2種へ分類する: **cap_limited**(op単位ではstrict版合成規則の閉じた
基準を満たすが、op数上限/atom比率上限のみで全体が非等価のまま。上限値
見直しのactionableな候補)、**near_match**(alnum内容の類似度0.85以上
だが完全一致ではない。未知の新しい閉じた吸収規則の候補になり得るが、
対義語[can/cannot]・単複[point/points]等の真の内容差も混在するため
必ず人間が目視で判断すること、自動採用はしない)。実行結果
(`er021_output/coverage_review_02/offline_false_reject_detector_01_
result.json`): cap_limited 1件(内容は本Phaseで追加した長尺negative
testの実行が同じProduction wrapper経由で書き込んだtelemetry由来であり
実運用データではないが、「op数上限3件を超える正当なpunctuation差が
同一segmentに複数回出現し得る」という設計上のシナリオそのものを実例で
示している。上限値は現時点では据え置くが、実運用でcap_limitedが増える
場合は上限緩和を検討する候補として記録する)、near_match 423件
(大半は複数形/固有名詞[既存Tier3の対象範囲]・対義語等の真の内容差で
あり、目視確認の結果、新しい閉じた吸収規則を要する新種パターンは
今回は0件だった)。実行手順・推奨頻度(週次〜記事1本ごと)はスクリプト
docstringに記載、haiku-worker委任可。

## SSOT反映
- `CURRENT_SPEC.md`(English ASR Semantic Equivalence Layer節へ追記、
  strict版Tier1合成規則+分類A技術修正の内容)。
- `DECISION_LOG.md`(新規エントリ「EN-ASR-SEMANTIC-EQUIVALENCE-
  COVERAGE-REVIEW-02: Phase 2」)。
- `OPEN_ITEMS.md`(OPEN-186へ追記5)。
- `docs/pm/REPORT_LEDGER.md`(新規行)。

## Gate 3表(Fable判定用)

| 項目 | 状態 |
|---|---|
| 設計(Phase 1) | 完了、Mandatory Opus L2レビュー実施済み |
| ユーザー承認 | 済(strict版Tier1合成規則+分類A技術修正、2026-09-28) |
| 実装 | 完了(`er021_en_asr_semantic_equivalence_production_01.py`、
  `er006_preprod_hardening_01_validation.py`[参照化のみ]) |
| test | 完了(既存125件[Trial-01 68+OPEN-123 57]無回帰+新規25件、
  全54テストPASS、false accept 0) |
| runtime evidence | 完了((a)telemetryオフライン再判定¥0、(b)実
  Production artifact再判定¥0、(c)実TTS+実ASR 2segment、Guardrail
  ¥15内) |
| 定期offline検知 | 新設・実行済み(`er021_offline_false_reject_
  detector_01.py`) |
| SSOT反映 | 完了(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGER) |
| Mandatory Opus L3診断 | **未実施(Fable発火待ち)** |
| `PRODUCTION_WIRED`最終判定 | **Fable判定待ち** |
| Git commit/push | 本REPORT保存後に実施予定(RESULT_PACKET参照) |

## Opus L3申し送り
1. **L2 BLOCKER解消表**: Opus L2レビューが指摘したと推定される論点
   (op分割粒度の実装規律、false accept境界の非拡張、既存NEGATIVE
   corpusへの回帰確認)は、実装した`_closed_punctuation_diff_ok()`の
   3つの閉じた条件(literalのみ/alnum完全一致/op数・比率上限)と、
   全125件の既存corpus無回帰+25件の新規test(false accept 0)で
   対応済みである。ただし本Sonnet実行時点ではOpus L2所見の逐語テキスト
   自体を受領していない(上記「背景」節の注記参照)ため、L2所見と
   実装の対応関係の一次確認はOpus L3診断時に改めて行う必要がある。
2. **受理集合の拡大範囲の定量**: telemetryオフライン再判定でreversal
   7件(すべて同一Hormuz記事由来)、他sub_reason 2,723件は反転0件。
   実運用での新規受理範囲は現時点では「Hormuz型(打点略語+日付序数の
   複合)」に限定的だが、これは案2(diff-anchored化)が構造的に用意した
   「未知の3つ目以降の punctuation差にも耐性がある」という設計効果の
   一部であり、頻度自体は今後のtelemetry蓄積で継続観測が必要。
3. **false accept 0根拠**: (i)全125件既存corpus無回帰、(ii)新規
   negative test 14件(Model X/28↔28th/US↔UK/概数/percentage points/
   ローマ数字/ハイフンコード/符号/長尺合成negative 6種)全PASS、
   (iii)telemetry 4,536件のうちTier1が新たにMATCHへ反転させたのは
   7件のみで、いずれも目視確認済みの真の等価ケース。
4. **同型漏れ再監査結果**: `er021_offline_false_reject_detector_01.py`
   でnear_match 423件を目視確認した結果、新しい閉じた吸収規則を要する
   新種パターンは今回は0件(大半は複数形/固有名詞/対義語等の真の内容
   差)。cap_limited 1件は上限緩和の検討候補として記録(§定期offline
   検知レポート参照)。
5. **全経路**: `er006_secondary_asr_01.py`のL395/L526間接呼び出しも
   含め、初回・retry・fallback・Local Rewrite前後・Secondary ASR
   cascade・Human Review Lock直前のいずれも単一wrapper
   (`classify_asr_match()`)を経由することを再確認済み(設計書§4)。
6. **コスト**: 本Phase全体の実測コストは、実TTS+実ASR 2回のみ
   (Guardrail¥15以内、他はすべて¥0の決定論コード・read-only解析)。
   継続的な追加ASR/LLM呼び出しは導入していない。
7. **Dangling Reference**: OPEN-184は本件へ吸収済み(`CLOSED`)。
   OPEN-186は本Phase 2完了により「Phase 2実装完了、Opus L3診断待ち」
   へ更新した。`'s`由来の単独"s"の無視処理は引き続きDEFERRED(未実装、
   ユーザー判断待ち)。Hormuz記事本文(Local Rewrite後の"The first
   act"等)の再生成・再TTSは本タスクでは一切行っていない(委任文の
   明示的制約どおり)。

---
Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02
