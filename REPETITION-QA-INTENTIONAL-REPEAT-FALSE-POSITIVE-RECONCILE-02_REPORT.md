# REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-02

**管理ID**: REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-RECONCILE-02
**種別**: 原因調査 + offline最小修正Trial(隔離scratchpad、Production変更なし)
**実行者**: sonnet-worker(Fable委任、初回)
**日付**: 2026-09-12
**費用**: ¥0(新規TTS/ASR/API呼び出しなし、既存JSON・既存音声・既存コードの読取専用解析のみ)

## 冒頭要点(5行)

1. **根本原因を特定した**: `tts_safe_number_words_en()`(`er003_v1_n3_01_tts_generate.py`)が canonical_text 中の綴り小数(two〜twelve)を算用数字(2〜12)へ変換した**後**の文字列が、そのまま Repetition QA の `canonical_text` として渡される一方、Repetition QA 専用のローカル ASR(`dq18.transcribe_verbatim()`、faster-whisper)は発話された小さな数を綴り("two")のまま書き起こすため、`_canonical_repeat_count()` の完全一致比較が "two" vs "2" で失敗し、**正規に2回登場する語句でも常に`canonical_repeat_count: 0`になる**。
2. 2026-09-08の`point_two`事例(OPEN-127、em dash隣接token誤カウント)とは**別原因**であり、OPEN-121行に既存記録のある「%記号 vs "percent"表記」不一致(2026-09-07特定・未修正のまま`USER_DECISION_REQUIRED`)とも別原因。今回初めて特定した、3件目の独立した failure mode。
3. 一般化調査で、この数字語signatureを持つ誤flag事例をタオル以外にもう1テーマ(`pool_pilot_01/pool_n4_supermarket`のA2・B1B、既存Production経路の過去生成物)で確認し、**単発ではなく再現性のある系統的バグ**と確認した。
4. scratchpad上のoffline prototype(実コード・実canonical_textで再現、¥0)で、判定の**意味(閾値canon_count>=2)を変えない**トークン正規化の追加修正により、確認済み誤flag3件は解消し、既知true positive1件は引き続き正しくflagされたままであることを確認した(判定意味の変更ではないため今回はSTOPしていない)。
5. この修正は**Production/QAコードへは未実装**(prototype検証のみ、scratchpad限定)。A-Family既存Production経路(`er003_v1_n3_01_tts_generate.py`)も同一パターンで影響を受けるため、正式実装の要否・優先度・試聴要否はユーザー/Fable判断を仰ぐ。

---

## 1. 過去対策の特定(Grep、SSOT照合)

- `_canonical_repeat_count()` / `_normalize_tokens()` の実装箇所は `er011_open121_repetition_qa_production_01.py`(345〜398行)。導入経緯は OPEN-121(Trial-01の方式A、無変更移植)。
- 2026-09-08 の `point_two` 事例(`TTS-REPETITION-QA-INTENTIONAL-REPEAT-FALSE-POSITIVE-TRIAL-01_REPORT.md`)は、em dash(—)前後に空白がない場合に `text.split()` が2語を1 tokenへ誤結合する不具合であり、OPEN-127として**修正・Production配線済み**(commit `602f1f5`、Fable受入 `PRODUCTION_WIRED`)。**今回のタオル事例に em dash は無く、原因は別**(ユーザー指示どおり確認)。
- `OPEN_ITEMS_HISTORY.md`(OPEN-121行、2026-09-07 `OPEN-121-EXISTING-AUDIO-SWEEP-REVIEW-AND-CLIPS-02` 追記)に、**別の既知false positive機構**が既に記録されている: No.9/No.18の4件で、ASR側 "%" 記号表記と canonical 側 "percent" 綴りの不一致により `canonical_repeat_count` が機能しなかった疑い(**推定のまま未修正・未クローズ**、`USER_DECISION_REQUIRED`)。
- 結論: 今回のタオル事例は、上記いずれとも異なる**3件目の独立した failure mode**(綴り小数→算用数字変換による ASR/canonical 不一致)であり、既存の未決事項(1)〜(4)にも含まれていない新規発見(OPEN-121行 2026-09-11追記の所見どおり)。

## 2. 根本原因(コード読解 + offline再現、実測)

- `parts.json['part2']` の生テキストには `"after two months"` が正規に **2回**存在する(`... observed after two months. During...` / `... will smell after two months.`)。
- Production呼び出し経路(`er012_b_family_production_runner_01.py` 353〜379行、A-Familyでは `er003_v1_n3_01_tts_generate.py` 727〜748行と同一パターン)は、`news_tail_fix.generate_news_narration_wide_margin(tts_gen.tts_safe_news_en(text), ...)` のように **`tts_safe_news_en()` で変換した後のテキスト**を渡す。この関数内部の `tts_safe_number_words_en()`(`er003_v1_n3_01_tts_generate.py` 566〜589行)が "two"→"2" 等(2〜12)を変換する。
- この**変換後**のテキストがそのまま `apply_repetition_qa_gate(verified, out_path, text, ...)` の `canonical_text` 引数として渡される(`er003_v1_sing01_news_tail_fix.py` 129〜130行 / `er012_b_family_voices_production_01.py` 559〜560行)。
- 一方、Repetition QA 専用のローカルASR(`dq18.transcribe_verbatim()`、faster-whisper)は発話された "two" を綴りのまま書き起こす(実際の監査記録の `span_text` が `" after  two  months."` と綴りで残っていることで確認済み)。
- `_normalize_token()`(`.,!?"'…` 除去+小文字化のみ)はこの digit/word 差を吸収しないため、`_canonical_repeat_count(['after','two','months'], canonical_tokens)` が **0** を返す。
- **offline再現(venv python、実モジュール `er011_open121_repetition_qa_production_01.py` と実関数 `er003_v1_n3_01_tts_generate.tts_safe_news_en()` をそのまま呼び出し、¥0)**:
  - `tts_safe_news_en(生canonical_text)` → `"...after 2 months..."` (canonical_repeat_countの入力時点で既に "after two months" が本文中0回)
  - `_canonical_repeat_count(['after','two','months'], 変換後canonical_tokens)` = **0**(実際の監査記録`canonical_repeat_count: 0`と一致)
  - `_canonical_repeat_count(['after','2','months'], 変換後canonical_tokens)` = **2**(数字表記同士なら検出できることを確認、原因を裏付け)

## 3. 一般化(既存flag記録の横断集計、¥0)

`er011_output/**`・`er012_output/**`・`er003_output/**`・`er006_output/**` 配下の全 `canonical_repeat_count` 記録(監査JSON・attempt保存・review_lock等)を走査し、実際に`flagged=true`かつ`canonical_repeat_count==0`だった**重複排除後のイベント数**を集計した。

- 該当イベント: 23件(diagnostic Trial sweep由来の緩い閾値[`min_words=1`等、Production既定`min_words=3`と異なる研究用設定]・OPEN-127修正前の既知事例[`do not need`/`I choose a`、修正済み]を多数含む)
- そのうち、検知句に綴り小数(two〜twelve)を含むもの: **7件**、独立した記事・テーマは**2件**
  - タオル(Discovery Generalization Trial-11、B1B `full_story_part2`、"after two months")
  - `pool_pilot_01/pool_n4_supermarket`(A2・B1B双方、"After three months, sales..."。canonical本文に "After three months, sales rose by 1.71 standard deviations." / "After three months, sales fell by 1.05 standard deviations." の並行構文として正規に2回存在することを実データで確認済み)
- `pool_n4_supermarket` 側の生成呼び出しは既存の**A-Family正式Production経路**(`er003_v1_n3_01_tts_generate.py`と同一パターン)由来であり、**本バグはB-Family Trialに限らず、既にProduction配線済み(`PRODUCTION_WIRED`)のRepetition QAゲートで再現する**ことを確認した(単発のTrial限定事象ではない)。

## 4. 最小修正Trial(scratchpad prototype、offline・¥0・Production未変更)

- 提案: `er011_open121_repetition_qa_production_01.py` のトークン正規化層(`_normalize_token`/`_normalize_tokens`相当)に、`tts_safe_number_words_en()`と同じ対象語(two〜twelve、"one"は対象外=既存の代名詞曖昧性回避方針を踏襲)について、綴り⇔算用数字の同値変換を**ASR側span_tokensとcanonical側tokensの両方に一様に**適用する。
  - これは既存 Production の別モジュール `er006_preprod_hardening_01_validation.normalize_numeric()`/`_convert_cardinal_words()`(Primary/Secondary ASR Validator側で、同種の digit/word 差を吸収するために既に使われている仕組み)と**同一クラスの正規化**であり、OPEN-127(em dashトークナイズ)と同様「`_canonical_repeat_count()`への入力の表記ゆれ吸収」に限定した修正である。
  - **判定の意味(canon_count>=2なら意図的repeatとみなす、という閾値・ロジック自体)は変更しない**ため、今回はSTOPせずTrial設計まで実施した(コード変更は未実施、scratchpad限定)。
- 検証結果(scratchpad、実モジュール・実canonical_text使用、¥0):
  - タオル `after two months`: 修正前0 → 修正後**2**(誤flag解消)
  - `pool_n4_supermarket` A2 `After three months, sales`: 修正前0 → 修正後**2**
  - `pool_n4_supermarket` B1B `After three months,`: 修正前0 → 修正後**2**
  - 既知true positive(`real_point_two_buggy`、実際のTTS重複ハルシネーション、"Young travelers are not one single market..."): 修正前1 → 修正後**1**(変化なし、真陽性は消えない。span中の"one"は対象外語のため無変換、"29"は数字のまま無変換で安全)
  - 既知陰性10件中、綴り小数を含むcanonical_textは1件(`a2_full_story_part2_clean`)のみだが、この語群は本来「検出された反復span」に対してのみ適用される変換であり、反復span自体が検出されない限り分類へ影響しない(この修正はtoken同値性を"追加"するだけで既存の一致を壊さないため、既存の正しい分類を後退させる経路がないことをロジック上確認した)。
- 未実施: 実コードへの適用・test追加・Fable/ユーザー承認・commit。これらはProduction判断が必要。

## 5. 結論

| 項目 | 内容 |
|---|---|
| Family | Discovery Generalization Trial-11 B1B(タオル)、および既存Production経路の過去生成物(`pool_pilot_01/pool_n4_supermarket` A2/B1B)。A-Family・B-Family双方の共有Repetition QA module(`er011_open121_repetition_qa_production_01.py`)が対象。 |
| 現象 | canonical本文に正規に2回登場する語句("after two months"等、綴り小数2〜12を含む句)が、Repetition QAにより言い直し(TTSハルシネーション)として誤flagされる。 |
| 既存対策 | OPEN-127(em dash隣接token誤カウント、修正・Production配線済み)。OPEN-121行に記録済みの「%記号 vs "percent"」不一致(未修正のままUSER_DECISION_REQUIRED)。 |
| 今回なぜ効かなかったか | 上記いずれとも別原因。`tts_safe_number_words_en()`によるcanonical側の綴り→算用数字変換と、Repetition QA専用ローカルASR(faster-whisper)が発話小数を綴りのまま書き起こす挙動との不一致であり、既存のem dash対策・%対策のいずれの対象にも含まれない未対応のtoken正規化ギャップ。 |
| 追加Trial有無 | あり(scratchpad offline prototype、¥0)。 |
| 結果 | 確認済み誤flag3件(タオル1件・supermarket2件)は、綴り小数⇔算用数字の同値正規化追加により解消することを実データで確認。既知true positiveは維持されたまま(退行なし)。判定意味(閾値)は無変更。 |
| Production判断が必要か | **必要**。(a) 本修正を`er011_open121_repetition_qa_production_01.py`へ正式実装するかどうか、(b) 実装する場合の適用範囲(OPEN-121/OPEN-122承認済み4segment[full_story_part1/2・point_one・point_two]全体か)、(c) 既に`PRODUCTION_WIRED`のA-Family既存記事・過去生成物に遡って影響有無を点検するか、(d) タオルTrial-11 B1B `full_story_part2`のHuman Review(試聴)要否、をユーザー/Fableに判断いただく必要がある(いずれも本タスクの範囲外、実装・承認代行はしていない)。 |

## 付録: 参照ファイル

- `er011_open121_repetition_qa_production_01.py`(345〜398行: `_normalize_tokens`/`find_repeated_spans`/`_canonical_repeat_count`/`detect_ngram_repetition`)
- `er003_v1_n3_01_tts_generate.py`(549〜589行: `tts_safe_en`/`_EN_NUMBER_WORDS`/`tts_safe_number_words_en`、616〜617行: `tts_safe_news_en`、727〜748行: A-Family Production呼び出し)
- `er012_b_family_production_runner_01.py`(335〜379行: B-Family呼び出し)
- `er003_v1_sing01_news_tail_fix.py`(59〜148行: `generate_news_narration_wide_margin`)
- `er012_b_family_voices_production_01.py`(480〜561行: `generate_voice_body_wide_margin`)
- `er006_preprod_hardening_01_validation.py`(279〜334行: `_convert_cardinal_words`/`normalize_numeric`、既存の類似正規化の先例)
- `er011_output/discovery_generalization_towels_trial_11/b1b/audit/tts_generation_results.json`(実記録、`canonical_repeat_count: 0`)
- `er011_output/open121_existing_audio_dprime_sweep_01/results/method_a.json`(`pool_n4_supermarket`の一般化事例)
- `er006_output/pool_pilot_01/pool_n4_supermarket/{a2,b1b}/parts.json`(canonical本文、正規に2回出現することの確認)
- scratchpad: `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\scratchpad\repqa\`(`fix_prototype2.py`が最終検証スクリプト、`manifest_full.json`が既知陽性・陰性データの複製)
