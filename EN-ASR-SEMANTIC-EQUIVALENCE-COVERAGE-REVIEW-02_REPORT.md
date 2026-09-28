# EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT

管理ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02
日付: 2026-09-28(Phase 1)/2026-09-28(Phase 2)
Phase: 1(原因分析+coverage再監査+設計案)完了 → 2(Production実装、
本REPORT末尾のPhase 2節参照)完了 → **修正1回目(Opus L3 BLOCKER-1反映、
本REPORT末尾「修正1回目」節参照)完了、Fable Gate 3再判定待ち**
Status: **Phase 1 DESIGN_COMPLETED(Opus L2レビュー実施済み、ユーザー
`APPROVED_FOR_PRODUCTION`承認済み) / Phase 2 IMPLEMENTATION_COMPLETE(Opus
L3診断によりBLOCKER 1件・SHOULD_FIX 5件検出) / 修正1回目 実装・テスト
完了、`PRODUCTION_WIRED`はFable Gate 3判定待ち(未宣言)**
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

## Opus L3診断所見(逐語、2026-09-28)

本節はFableが受領したOpus L3診断の逐語転記(Sonnetによる保存作業のみ、実装は未着手・ユーザー判断待ち)。

# Opus L3診断: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02(commit 3d9a28be)

前提: read-only。コード編集・テスト実行・API呼び出しは一切行っていない(判定はコード精読による静的追跡。反例は下記のとおり行単位で経路を追跡済みだが、¥0の決定論probeでの機械確認はFable/Sonnet側に委ねる)。

## 総括
- 承認仕様の**中核条件のうち1つが実装されていない**。すなわち「句読点atomを必ず含む差分のみ」という条件が`_closed_punctuation_diff_ok()`に存在せず、結果として**語境界(分かち書き)差とアポストロフィ差が吸収される**。この抜けにより「否定語の欠落」が吸収され得る具体的経路があり、かつDEFERRED扱いの`'s`処理が事実上実装されてしまっている。→ BLOCKER 1件。
- それ以外(数値/時刻atomの保護、op数・比率上限、月名限定序数、ローマ数字安全化、"and"バグ修正、`autojunk=False`、共通化)は設計どおりで、安全方向の締めも含め妥当。修正は**2行程度**で、既存54テスト・evidence(reversal 7件、Hormuz実artifact再判定)を壊さない(下記で個別に検証)。

---

## BLOCKER-1: 「句読点atomを必ず含む差分のみ」が未実装 → 分かち書き差・アポストロフィ差の吸収(否定語欠落・DEFERRED項目の暗黙実装を含む)

根拠(ファイル:行)
- `C:\Users\tensh\eigo-radio\er021_en_asr_semantic_equivalence_production_01.py:537-577` `_closed_punctuation_diff_ok()`。条件は (1) 両側literalのみ (2) `re.sub(r"[^a-z0-9]","",word)`連結の完全一致 (3) 両側非空、の3つだけ。**「差分opに句読点atom(alnumが空のatom)を含むこと」を要求していない**。
- 同関数docstring L550-554 の論拠「alnum内容が一致するならその差は必ずpunctuation由来である」は誤り。差は**空白(トークン境界)由来**でも成立する。alnum連結はatom境界情報を捨てるため、`["not","able"]`と`["notable"]`が等価判定される。
- 早期exitは`C:\Users\tensh\eigo-radio\er006_preprod_hardening_01_validation.py:1210-1222`で`_classify_asr_match_core()`より前に`ProtectedCheckResult(passed=True)`で即PASSするため、`protected_check()`(同ファイル:673-677の否定語チェック)は**実行されない**。つまりこの穴は否定保護を直接すり抜ける。

反例(role適用segment、`classify_asr_match(..., segment_id="full_story_part1")`経路。いずれも atom 17/16、absorbed_ops=1、absorbed_atom_total=3、3/17≈0.176 ≤ 0.2 のため上限では止まらない)

1. 否定の消滅(最重要)
   - canonical: `The findings are not able to explain the 20 percent drop recorded across the region this year.`
   - ASR: `The findings are notable to explain the 20 percent drop recorded across the region this year.`
   - 経路: 差分op = replace `[lit"not", lit"able"]` vs `[lit"notable"]` → 両側literal・alnum `notable` 一致 → 吸収 → `NUMERIC_EQUIVALENCE_MATCH`(`should_pass=True`)。承認仕様「否定の欠落は吸収しない」に反する。
2. 意味反転する分かち書き差
   - canonical: `Officials said the 2 islands remain a part of the territory, and the review will finish in 2027.`
   - ASR: `... remain apart of the territory, ...` → `["a","part"]` vs `["apart"]` を吸収。
   - 同型: `may be`↔`maybe` / `in to`↔`into` / `some time`↔`sometime` / `every one`↔`everyone`。
3. DEFERREDのはずの`'s`処理が発火
   - canonical: `Ottawa's mayor said the 20 percent plan would start in 2027 across the region this year.`
   - ASR: `Ottawa s mayor ...` → replace `[lit"ottawa's"]` vs `[lit"ottawa", lit"s"]` → alnum `ottawas` 一致 → 吸収。
   - REPORT「`'s`はDEFERRED(未実装)」(L338-339)は事実と不一致。
4. アポストロフィ単独差(1atom↔1atom)
   - canonical `We're seeing a 20 percent rise ...` / ASR `Were seeing ...` → alnum `were` 一致で吸収。逆方向(canonical `were` / ASR `we're`)も同様に吸収され、`its`↔`it's`、`he'll`↔`hell`、`she'd`↔`shed` も同じ経路。

緩和事情(重要、severity判断材料)
- 既存baselineの`despaced()`(`er006_...validation.py:986-989`)も**protected_checkより前に**空白除去一致でPASSするため、「分かち書き差だけ」の単独ケースは従来からPASSしていた。したがって本件はend-to-endで完全に新規の穴ではなく、**新規に拡大するのは「分かち書き/アポストロフィ差 × 数値表記差の同居」**(旧`despaced()`では救えなかった組合せ)。
- それでも(i)ユーザー承認仕様の明示条件(句読点atom必須/否定の非吸収)に反する、(ii)DEFERRED項目の暗黙実装、(iii)REPORTの「false accept 0」根拠testにこのクラスのnegativeが1件も無い、の3点から、`PRODUCTION_WIRED`宣言前に是正が必要と判断する。

最小修正案(er021側2行、`_closed_punctuation_diff_ok()`内)
```
punct_present = any(re.sub(r"[^a-z0-9]", "", a["word"]) == "" for a in (*canon_slice, *asr_slice))
if not punct_present:
    return False
```
影響確認(精読ベース、いずれも維持される)
- Hormuz型 `["us"]` vs `["u",".","s","."]`: `.`atomがあるためPASS維持 → 新規25テストのHormuz複合test・長尺punctuation-only test・evidence(b)(absorbed_ops=1)・offline再判定のreversal 7件(うち1件は`safe. But`↔`safe, but`の`.`↔`,` replaceでこれも句読点atomを含む)は**すべて不変**。
- 他のpositive test 8件(序数語/per cent/and/meridiem/hyphenated/COVID-19/月名序数/Section V)は差分opが発生しない(parser・前処理段で吸収)ため無影響。
- negative test 14件は元々rejectなので無影響。
- 副作用: `we're`↔`were`等がTier1で吸収されなくなるが、baseline側の既存正規化経路が従来どおり担うため実害はfalse rejectのみ(安全方向)。

任意の二重防御(推奨、er006側1箇所)
`er006_...validation.py:1211`で`tier1.get("diff_anchored")`がTrueのときのみ、`protected_check(tokenize(canonical_text), tokenize(asr_text)).negation_mismatches`が空であることを追加条件にする。Hormuz実データは両側とも`not`が同位置にあり否定差ゼロなので既存evidenceを壊さない。

残存リスク(修正後も理論上残る、要記録)
句読点atomと語境界ずれが**同一op内に同居**する場合(例: canonical `U.S. not able` vs ASR `US notable`)はalnum一致で吸収され得る。完全に閉じたいなら追加条件「句読点atomを除いた側のatom数の`min`が1(=片側が結合形の1語)」を入れる。Hormuz型は`min(1,2)=1`で通り、上記の混在型は`min(4,2)=2`で落ちる。

---

## SHOULD_FIX

- **SF-1(証拠の衛生): unit testがProductionのtelemetryへ書き込んでいる。** 新規テストは実配線`val.classify_asr_match(..., segment_id=APPLICABLE_SEGMENT_ID)`を使うため、NG時に`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`へ追記される(`er006_...validation.py:1263-1271`、書込先は`er021_...production_01.py:50`)。実測でも母数が4,187→4,536件、`protected_number`が1,672→1,813件へ増えており、合成fixtureが実運用ログに混入している。REPORT自身も「cap_limited 1件は本Phaseのtest実行由来」と認めている(REPORT L264-270)。修正案: テスト側で`TELEMETRY_LOG_PATH`を一時ディレクトリへ差し替える(monkeypatch)。既存混入分は「test由来期間」としてOPEN_ITEMSに明記。
- **SF-2(REPORTの過大主張1): 「assertで不変条件を固定」は実質無効。** `er021_...production_01.py:571-577`は`ok = (canon_alnum == asr_alnum)` の直後に`if ok: assert canon_alnum == asr_alnum`で恒真、かつ`python -O`で消える。削除するか、実効のある不変条件(非literal atom不在/句読点atom存在)をassertする。
- **SF-3(REPORTの過大主張2): 「既存合格経路の挙動は完全に同一」は不正確。** 比較アルゴリズム(全体zip)は保存されているが、atom化自体が変更されている(序数語/序数digit token/per cent/meridiem/月名序数/hyphen・minus順序/ローマ数字gate)。特にローマ数字安全化は**従来PASSしていた組合せを落とす**(安全方向だが挙動変化)。SSOT/Gate記述は「既存の比較方式は不変、atom化は分類A修正の範囲で変更」と書き分けるべき。
- **SF-4(test coverageの欠落): 分かち書き差・アポストロフィ差のnegative fixtureが0件。** BLOCKER-1の是非にかかわらず、`not able`/`notable`、`a part`/`apart`、`Ottawa's`/`Ottawa s`、`were`/`we're`をTier1直呼びのnegativeとして固定すべき(将来の再発防止)。
- **SF-5(Gate 3表の表現): 「runtime evidence 完了」は内訳の明示が必要。** 実TTS+実ASR 2 segment(c)は新規則を発火させていない(REPORT L246-250で自認)。新規則の実経路発火は(b)の実Production artifact再判定のみ。Gate表の行に「新規則の実経路発火は(b)の実データ再判定で確認、(c)は発火せず」と明記するのが安全(1記事ずつ完結原則・安全≠成功原則の観点)。

## NOTE

- N-1(論点1a): 数値・時刻atomは`_closed_punctuation_diff_ok()`の条件(1)(L567-568)で確実に非等価へ落ちる。`_atom_key()`(L514-525)がvalue/currency/percent/ordinal/meridiemをキーに含むため、値違いは`equal`になり得ない。ここは仕様等価で問題なし。7桁以上の裸digitのみ`kind="literal"`(L444-447)となり理論上alnum比較の対象になるが、区切りが入ると各片が数値atom化して弾かれるため実害なしと判断。
- N-2(論点2, 月名限定): `_DATE_ORDINAL_RE`(L97)は月名+空白+1〜2桁+接尾辞に限定され、`Act 13th`等の非月名文脈へは漏れない(`Act 13th`は`ordinal=True`のnumber atomとして`13`と非等価、長尺negative testでも固定済み)。残留は英語の`may`/`march`が月名と同綴りである点のみ(er006の既存承認ロジックと同一スコープ、実害は極小)。
- N-3(論点2, ローマ数字): `_ROMAN_AMBIGUOUS_SINGLE`ゲート(L459-461)は直前の生tokenを見るため、`Act: V`のように句読点が挟まると不発(false rejectのみ)。また閉じたラベル語リスト外(`Super Bowl V`、`Series X`等)は従来PASSしていたものが落ちる。いずれも安全方向。POSITIVE corpus 125件無回帰というREPORT主張と矛盾する箇所は精読では見つからなかった。
- N-4(論点2, "and"修正): `_consume_number_word_run()`(L263-283)の先頭/末尾"and"除外は、`one hundred and five`のscale経路(`_words_to_number_scale()`が"and"をskip)を壊さない。逆に従来の「`and five`→num(5)1 atom」による語落ち(false accept方向の副作用)も締まる。設計どおり。
- N-5(論点3): 新規則は`protected_check`より前でPASSを返す(`er006_...validation.py:1210-1222`)。これはPhase A承認済みの既存構造だが、受理集合が広がった分だけ保護層のバイパス範囲も広がっている。BLOCKER-1の修正+任意の否定二重防御でこの範囲を承認仕様の幅に戻せる。
- N-6(論点4, L2対応): 設計書§7-5が明示した「op分割粒度を誤ると意図しない範囲を1つのopとして許容する」という懸念は、**まさに今回の形(alnum連結によるatom境界情報の喪失)で現実化している**。また設計書§5(B)-2「複合語分かち書き吸収をTier1へ複製しない(推奨: 変更しない)」に対し、実装は事実上それを実装している。すなわちL2/設計書レベルの論点は**一部未対応**。既存NEGATIVE corpus回帰(125件)とop数・比率上限は対応済み。
- N-7(論点5の読み方): offline再判定はtelemetry=「過去にNGだった記録」のみを母数とするため、**false rejectの減少量**しか測れず、**false acceptの増加**は構造的に検出できない(従来PASSした記録はログに無い)。reversal 7件が全てHormuz由来という結果は「受理拡大が局所的」を示す弱い証拠にはなるが、「false accept 0」の根拠にはならない。加えて母数に自作test fixtureが混入(SF-1)。`near_match 423件`の目視は有用だが、これも「NG側」だけの視界である点を記録すべき。
- N-8(実務上のカバレッジの狭さ): 条件(3)によりinsert/delete(片側空)は不吸収なので、**ASRが最も頻繁に起こすcomma落ち等の句読点欠落は救われない**(Tier1は非等価→baselineへ)。加えてop上限3のため、打点略語が4箇所以上ある長尺segmentはcap_limitedで落ちる。SSOT側で「構造的耐性」を過大に書かないほうがよい。将来「alnumが空のatomのinsert/deleteのみ許容」へ広げる案は、`12-34`↔`12 34`のような区切り記号の意味差を含むためユーザー判断事項(現時点の据え置きは妥当)。
- N-9(共通化の検証残): `_MONTHS`/`_DATE_ORDINAL_RE`/`_ORDINAL_WORDS`はer021に一本化され、er006(`:124`,`:170-171`)は参照のみ。repo内に重複定義は無い(grep確認、`er003_audio_tts_asr_safety.py`は別目的の`_INTERNAL_LABEL_ORDINAL_WORDS`)。ただし「移設前後で集合が完全同一か」はgit diffでの1行確認を推奨(¥0)。er021の月名は標準12件のみで、旧実装と差異がある兆候は精読では見つからなかった。
- N-10(層間不整合、false rejectのみ): `July thirteenth`↔`July 13`はer006側では序数語→`13th`→月名限定吸収で一致するが、Tier1は`_preprocess_raw()`で序数語→digit変換を行わないため一致しない。安全方向のため対応は任意。

---

## 論点6: `PRODUCTION_WIRED`判定への所見(判定はFable/ユーザー)
- 採用可否は人間ユーザーのみが決定するもので、本診断は判断材料の提示に留める。
- 技術所見としては、**BLOCKER-1(2行の追加条件+SF-4のnegative test)を先に入れてから`PRODUCTION_WIRED`とするのが安全**。理由: (i)承認仕様の明示条件(句読点atom必須/否定非吸収)との不一致、(ii)DEFERRED項目(`'s`)の暗黙実装、(iii)修正コストが極小でevidence再取得も不要(既存evidence・54テストは修正後も成立する見込み)。
- もしユーザーが「分かち書き/アポストロフィ差の吸収も許容する」と判断するなら、それは**承認仕様の拡張**であり、Fable/Claude側で黙示的に確定せず、`USER_DECISION_REQUIRED`として明示の再承認を得る形が整合する。
- SF-1(telemetry汚染)は判定とは独立だが、今後のGate判断の一次データを汚すため早期に是正が望ましい。

参考にした主なファイル
- `C:\Users\tensh\eigo-radio\er021_en_asr_semantic_equivalence_production_01.py`
- `C:\Users\tensh\eigo-radio\er006_preprod_hardening_01_validation.py`
- `C:\Users\tensh\eigo-radio\er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`(L534-774)
- `C:\Users\tensh\eigo-radio\EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02_REPORT.md`
- `C:\Users\tensh\eigo-radio\docs\pm\design_en_asr_orthographic_equivalence_coverage_02.md`
- `C:\Users\tensh\eigo-radio\er021_output\coverage_review_02\offline_telemetry_reclassify_01_result.json`

入力範囲は十分だった(追加で必要なファイルは無い)。唯一、N-9の集合同一性のみgit diff未確認。

---

## 修正1回目(Opus L3 BLOCKER-1反映、2026-09-28、ユーザー承認済み)

性質: 承認済みstrict Tier 1仕様への**適合修正**(受理範囲を広げる追加仕様
ではない、決定論のみ・追加API呼び出しなし・費用¥0)。

### 対応表(Opus L3所見 → 対応)

| 所見 | 対応 | 状態 |
|---|---|---|
| BLOCKER-1(句読点atom必須が未実装) | `_closed_punctuation_diff_ok()`へ(4)句読点atom存在必須+(5)句読点atom除外後atom数minが1以下、を追加 | 反映済み |
| SF-1(telemetry汚染) | `er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`全体へ`setUpModule`/`tearDownModule`でtelemetry書込先を一時ディレクトリへ隔離 | 反映済み(既存混入分は削除せず`telemetry_contamination_note.json`へ記録) |
| SF-2(恒真assert) | `if ok: assert canon_alnum == asr_alnum`を削除し、独立した2つの不変条件(句読点atom存在/非literal atom不在)のassertへ置換 | 反映済み |
| SF-3(「既存合格経路の挙動は完全に同一」の過大表現) | 本節で「比較アルゴリズム[全体zip→diff-anchored]は保存されるが、atom化自体は分類A修正の範囲で変更され、特にローマ数字安全化は従来PASSしていた一部組合せを安全側に落とす」と訂正 | 反映済み(下記参照) |
| SF-4(negative fixture欠落) | `StrictTier1SynthesisRuleTest`へ6件追加(not able/notable、a part/apart、Ottawa's/Ottawa s、we're/were、may be/maybe、混在型U.S. not able/US notable)+positive維持2件、Tier1直呼び経路+`classify_asr_match(segment_id="full_story_part1")`経路の両方で固定 | 反映済み |
| SF-5(Gate 3表「runtime evidence完了」の内訳) | 下記Gate 3再確認表へ「新規則の実経路発火は(b)実Production artifact再判定でのみ確認、(c)実TTS+実ASR 2segmentでは発火せず」を明記 | 反映済み |
| N-6(設計書§5(B)-2/§7-5との対応) | `docs/pm/design_en_asr_orthographic_equivalence_coverage_02.md`へ対応表追記 | 反映済み(設計書側diff参照) |
| N-7(offline再判定はfalse reject減少のみ測定可) | 本節「オフライン再判定」項へ明記 | 反映済み |
| N-8(insert/delete不吸収・op上限3の実務上の狭さ) | 本節・SSOT文案で「構造的耐性」の過大表現を避け、範囲を明記 | 反映済み |
| N-9(移設前後の集合同一性) | `git show 3d9a28be`で`_MONTHS`/`_DATE_ORDINAL_RE`/`_ORDINAL_WORDS`のer006側削除内容とer021側追加内容が文字列単位で完全一致することを確認 | 確認済み(差分同一) |
| `'s`のDEFERRED記述 | BLOCKER-1修正により、`Ottawa's`/`Ottawa s`は句読点atomが存在しないため吸収されない。DEFERRED(未実装)の記載は事実として正しい状態に復帰した | 修正により整合 |

### 実装差分(要約)

- `er021_en_asr_semantic_equivalence_production_01.py::_closed_punctuation_diff_ok()`:
  句読点atom(alnum除去後が空のatom)の存在を必須化する条件(4)、および
  句読点atomを除いた側のatom数のminが1以下であることを要求する条件(5)を
  追加。これにより"not able"↔"notable"のような語境界(分かち書き)差のみの
  差分は吸収されなくなり(false accept防止)、Hormuz型("us"↔"u"+"."+"s"+".")
  は句読点atomが存在するため従来どおり吸収される。SF-2是正として、恒真
  assertを独立した2つの不変条件のassertへ置換。
- `er006_preprod_hardening_01_validation.py::classify_asr_match()`:
  Tier 1 early-exitのうち`tier1["diff_anchored"]`がTrueの場合のみ、
  `protected_check().negation_mismatches`が空であることを追加確認する
  否定語二重防御を追加(全体一致経路[diff_anchored=False]は無変更)。
  BLOCKER-1本体の修正により現状のnegative fixtureでは本guardが単独で
  発火する経路は確認されていない(実装バグ混入時の多重防御として保持)。
- `er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`:
  (1)ファイル全体共通の`setUpModule`/`tearDownModule`でtelemetry書込先を
  一時ディレクトリへ隔離(SF-1)。(2)`StrictTier1SynthesisRuleTest`へ
  SF-4のnegative test 6件+positive維持test 2件を追加(計8件、既存25件と
  合わせて33件、ファイル全体では62 unittest)。

### negative test結果(false accept 0)

Tier1直呼び経路(`semantic_equivalence.tier1_numeric_equivalence()`)、
実配線経路(`val.classify_asr_match(..., segment_id="full_story_part1")`)
の両方で以下を固定(全件PASS、詳細は
`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`
`StrictTier1SynthesisRuleTest`参照)。

| ペア | Tier1直呼び | 実配線経路(Tier1発火有無) |
|---|---|---|
| not able / notable | 非等価(None) | Tier1不発火(classification≠NUMERIC_EQUIVALENCE_MATCH。ただし既存baseline側の独立した`despaced()`正規化[本タスクの変更範囲外、Opus L3所見「緩和事情」]により最終的にはNORMALIZED_MATCHで別途PASSする。これは新規のfalse acceptではなく従来からの既存挙動) |
| a part / apart | 非等価(None) | Tier1不発火(同上) |
| Ottawa's / Ottawa s | 非等価(None、DEFERRED維持) | Tier1不発火(同上) |
| we're / were | 非等価(None) | Tier1不発火(同上) |
| may be / maybe | 非等価(None) | Tier1不発火(同上) |
| 混在型(U.S. not able / US notable) | 非等価(None、条件(5)で遮断) | Tier1不発火 |
| safe. But / safe, but(positive維持) | 等価(diff_anchored=True) | Tier1発火・PASS |
| Hormuz型 US/U.S.(positive維持) | 等価(diff_anchored=True) | (別途既存test群で確認済み) |

重要な注記(誤解防止): 上表の「Tier1不発火」6件について、実配線経路
(classify_asr_match)の**最終**should_passは、Tier1より後段の既存
baseline側の独立した`despaced()`正規化(空白除去一致でのPASS、本タスクの
変更範囲外、`er006_preprod_hardening_01_validation.py`の既存ロジック)に
より`True`になる場合がある(実測: `not able`/`notable`単独ケースは
`NORMALIZED_MATCH`でPASS)。これはBLOCKER-1が新たに開けた穴ではなく、
Opus L3所見「緩和事情」が指摘したとおり従来から存在する挙動であり、
本タスクの是正範囲(Tier1層のみ)の外にある。将来この経路自体の是非を
問う場合は別途ユーザー判断が必要な論点として`OPEN_ITEMS.md`側で扱う
(本タスクでは変更しない)。

既存NEGATIVE fixture全再実行: Trial-01 corpus(68件)+OPEN-123 Regression
fixture(57件)+既存StrictTier1SynthesisRuleTest(25件)+本修正で追加した
8件、計`er021_en_asr_semantic_equivalence_production_wiring_01_test_01.py`
62 unittest全件PASS(`.venv\Scripts\python.exe -m unittest
er021_en_asr_semantic_equivalence_production_wiring_01_test_01 -v`実行、
false accept 0)。

### オフライン再判定(reversal件数の前後比較)

`er021_output/coverage_review_02/offline_telemetry_reclassify_01.py`
(無変更、read-only)を修正後コードで再実行。

| | 修正前(`_01_result.json`) | 修正後(`_02_result.json`) |
|---|---|---|
| 総record数 | 4,536 | 4,977(SF-1隔離導入前の期間中に増加、`telemetry_contamination_note.json`参照) |
| reversal(Tier1 MATCHへ反転) | 7 | 7(不変、全件同一Hormuz記事由来) |
| 他sub_reasonの反転 | 0 | 0 |

Opus L3予測(「reversal 7件は不変」)どおり、BLOCKER-1修正はオフライン
telemetry上のfalse reject救済件数に影響しない(修正前後で件数・内訳とも
完全一致)。

### project-wide regression

`run_project_regression.py`実行(pattern既定`er0*_test_*.py`、全件)。
結果: `collected=3506 passed=3495 failed=9 errors=2`。個別に確認した
結果、9件のFAIL+2件のERRORはいずれも本タスクの変更(ASR/Tier1/
semantic_equivalence関連)とは無関係と確認した:
- 3件(`er003_test_p2j_investigate`): テスト総数の経年増加に対する
  ハードコード済み過去スナップショット値との突合せ(本タスクに限らず
  リポジトリ全体のtest追加で恒常的にドリフトする既知の性質)。
- 3件(`er011_open112_trend_synthesis_mode_production_wiring_01_test_01`
  ::TestBuildCommonBlockDefaultByteParity): プロンプトテンプレートの
  byte-parity差分(本タスクが触れていないファイル由来)。
- 2件(`er019_family_x_pointless_01_test_01`/
  `er020_tts_*_trial_*_test_01`::「no uncommitted diff」系): 並行して
  作業中の別Sonnetセッション(Flash-Lite family、`er003_v1_n3_01_
  scaffold_generate.py`/`er003_v1_sing01_voice01_generate.py`)の
  未commit差分を検出したもの(本委任文が明示する既知の並行衝突、本タスク
  では一切編集していないファイル)。
- 2件(ERROR、`er015_standard_a2_6000_generation_first_trial_01*`):
  `STANDARD_A2_PROMPT_V5`構文不一致によるProduction側import時の意図的
  `RuntimeError` STOP(本タスクが触れていないファイル由来)。

### Gate 3再確認表(ユーザー指定9項目、Fable判定用)

| 項目 | 状態(修正1回目時点) |
|---|---|
| 設計(Phase 1) | 完了、Mandatory Opus L2レビュー実施済み(無変更) |
| ユーザー承認 | 済(strict版Tier1合成規則+分類A技術修正、2026-09-28。かつ本修正1回目=BLOCKER-1反映もユーザー承認済み) |
| 実装 | 完了(BLOCKER-1修正+否定語二重防御+SF-2是正、上記「実装差分」参照) |
| test | 完了(既存125件+StrictTier1SynthesisRuleTest 33件[既存25+新規8]、ファイル全体62 unittest全件PASS、false accept 0を直接経路・実配線経路の両方で確認) |
| runtime evidence | (a)telemetryオフライン再判定¥0(reversal 7件、修正前後で不変)。(b)実Production artifact再判定¥0(Phase 2実施済み、BLOCKER-1修正はこの経路[Hormuz型、句読点atom有り]を変えない)。(c)実TTS+実ASR 2segment(Phase 2実施済み、Guardrail¥15内)。**新規則(diff_anchored=True)の実経路発火は(b)でのみ確認済みであり、(c)の2segmentでは発火していない**(Phase 2時点から変化なし、追加のTTS/ASR実行は本修正1回目では行っていない[Guardrail¥0]) |
| 定期offline検知 | Phase 2で新設済み(`er021_offline_false_reject_detector_01.py`)、本修正1回目での追加変更なし |
| SSOT反映 | 本修正1回目の文案を`RESULT_PACKET_ASR4.md`(一時ファイル)へ記載、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`本体への反映はFable/ユーザー側の作業(本Sonnetの担当範囲外、衝突回避のため無編集) |
| Mandatory Opus L3診断 | 実施済み(本REPORT前節「Opus L3診断所見」参照)、BLOCKER-1は本修正1回目で反映 |
| `PRODUCTION_WIRED`最終判定 | **Fable/ユーザー判定待ち(本Sonnetは宣言しない)** |

### telemetry隔離の確認

`er021_output/en_asr_semantic_equivalence_production_wiring_01/
telemetry.jsonl`の行数を、本タスクの修正・test実行の前後で確認
(`wc -l`)。前: 4,977件。本タスクの全unittest実行(複数回)後: 4,977件
(不変)。隔離fixture(`setUpModule`/`tearDownModule`)が機能していることを
実測で確認した。既存の混入分(4,187→4,977、詳細は
`telemetry_contamination_note.json`)は削除していない(read-only原則、
削除の要否は別途ユーザー判断事項)。

### Dangling Reference Check

`_closed_punctuation_diff_ok|diff_anchored|negation_mismatches|
TELEMETRY_LOG_PATH`をリポジトリ全体でGrep。本タスクの変更対象外で
この4語を参照する箇所(`er006_secondary_asr_01.py`の独立した
`negation_mismatches`アクセス、`er007_ja_asr_validator_01.py`の日本語ASR
用の同名フィールド等)はいずれも別モジュール・別management IDの独立した
既存フィールドであり、本修正による関数シグネチャ変更の影響は受けない
(`_closed_punctuation_diff_ok()`は本ファイル内でのみ呼ばれる private
関数、呼び出し箇所は1箇所のみ)。dangling referenceは検出されなかった。

### N-9確認結果

`git show 3d9a28be -- er006_preprod_hardening_01_validation.py
er021_en_asr_semantic_equivalence_production_01.py`のdiffを確認した
結果、er006側で削除された`_MONTHS`/`_DATE_ORDINAL_RE`/`_ORDINAL_WORDS`の
リテラル値と、er021側で新規追加された同名定義のリテラル値は文字列単位で
完全に一致していた(コピー&リネームであり、値の変更・欠落は無い)。

---
Management-ID: EN-ASR-SEMANTIC-EQUIVALENCE-COVERAGE-REVIEW-02
