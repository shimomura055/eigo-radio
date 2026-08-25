# ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01 完了報告

## 概要

ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01のProduction配線完了後、
ユーザーからの確認依頼(ER-007-JA-ASR-TTS-RETRY-PATH-CHECK-01)で発見した
2件の問題を修正した。

- **経路A**: Cascadeが`stop_retrying=True`(これ以上retryしても解決しない
  という判定)を返した後も、一部Production経路でTTSが再生成され続ける
  bug
- **経路B**: 「頃→ころ/ごろ」のような濁点/半濁点の有無だけが異なる読み
  ゆれを`TRUE_CONTENT_MISMATCH`と誤分類し、即TTS再生成してしまう問題

いずれも修正し、fixture・mock test・regression・実音声smoke testで検証
した。**ASRで不確実なだけならTTSを作り直さない**という基本方針を満たす
状態にした。

## Part A: `stop_retrying`無視bugの修正

### 1. root cause

`er003_v1_repro01_main_generate.py`の`generate_narration_snippet_
verified_strict()`(JA分岐)は、Cascadeの戻り値`stop_retrying`を正しく
チェックして打ち切っていた(`if stop_retrying: return {...
ASR_VALIDATION_UNCERTAIN...}`)。しかし、ER-007-JA-ASR-VALIDATOR-
REDESIGN-AND-CASCADE-01でJA Cascade呼び出しを他の2箇所へ配線した際、
この短絡処理の移植が漏れていた。

- `er003_v1_sing01_voice01_generate.py`の`generate_charon_japanese()`
  (標準経路・フォールバック経路の両方)
- `er003_v1_n3_01_tts_generate.py`の`generate_a2_japanese_with_
  fallback()`のフォールバック経路(標準経路はrepro01経由のため無事)

この3箇所は`stop_retrying`変数を受け取るだけで一切参照しておらず、
`if verified:`だけで判定していたため、`stop_retrying=True`(Cascadeを
Primary#2→Secondary#1→#2まで尽くしても解決しなかった、Human Review
行き)になった後も、`for attempt in range(...)`ループが次のattemptへ
進み、無駄なTTS再生成(最大`max_attempts`回)を繰り返していた。

比較として、英語側の同種フォールバック
(`er003_v1_crosslevel_audio_02_common.py`の`generate_english_segment_
with_fallback()`)には既に`if stop_retrying:`の短絡処理があり、これを
参考にした。

### 2. 修正箇所

- [er003_v1_sing01_voice01_generate.py](er003_v1_sing01_voice01_generate.py) `generate_charon_japanese()`:
  標準経路(174行目付近)・フォールバック経路(220行目付近)の両方に
  `if stop_retrying:`を追加し、`status="ASR_VALIDATION_UNCERTAIN"`
  `asr_verified=False`で即座に返すようにした
- [er003_v1_n3_01_tts_generate.py](er003_v1_n3_01_tts_generate.py) `generate_a2_japanese_with_fallback()`:
  同様にフォールバック経路へ`if stop_retrying:`を追加した

### 3. `stop_retrying=True`後にTTS retryしない証拠

新規[er007_ja_tts_retry_path_fix_test_01.py](er007_ja_tts_retry_path_fix_test_01.py)で、実TTS/ASRを一切呼ばずmockで検証した(4テスト、全PASS)。

- `test_stop_retrying_true_tts_call_count_is_exactly_one`(voice01.py):
  `ja_secondary.evaluate_attempt_ja_with_cascade`を`(False, True,
  ASR_VALIDATION_UNCERTAIN)`固定でmockし、`common._call_tts_with_retry`
  (実際のTTS呼び出し単位)のcall_countが**1**であることを確認(修正前は
  `max_attempts`まで増え続けていたはず)
- `test_stop_retrying_true_minimal_instruction_called_exactly_once`
  (n3_01.py): 同様に`_generate_a2_japanese_minimal_instruction`の
  call_countが**1**であることを確認
- 回帰確認2件: `stop_retrying=False`(通常のTRUE_CONTENT_MISMATCH)では
  従来通りattempt 2以降へ進むことを確認(今回の修正が通常retryを壊して
  いないこと)

## Part B: 漢字読み揺れ/同音異字の分類改善

### 4. root cause

`er007_ja_asr_validator_01.py`の`is_entity_like_mismatch_ja()`
(Cascade対象かどうかの判定)は、カタカナ/英字acronymらしさ
(`_is_katakana_or_acronym()`)のみをCascade対象の基準にしていた。実際に
発生した実例(`verify_ja_cascade_production_on.py`のsmoke testで検出):
canonical「聞き終わる**ころ**には」/ASR「聞き終わる**頃**には」で、
kakasi(文脈なし・形態素解析なしの規則ベース読み変換ライブラリ)が「頃」
を(この文脈では不適切な)連濁形「ごろ」と読んでしまい、canonical側の
「ころ」と一致しなかった。「頃」はカタカナでも英字acronymでもないため
entity_like判定に一切かからず、`TRUE_CONTENT_MISMATCH`(即TTS retry
対象)へ直行していた。

### 5. 漢字読み揺れをASR uncertaintyへ分類するロジック

`_reading_equal_allowing_voicing(a, b)`([er007_ja_asr_validator_01.py](er007_ja_asr_validator_01.py))を新設した。

1. 両span(前後4文字の文脈込み)をpykakasiで**ひらがな読み**へ変換する
   (ローマ字hepburnは濁音行によって文字数が変わる[例: し→じは3文字→
   2文字]ため、1文字=1モーラで長さが揃うひらがなを使う)
2. Unicode NFD正規化で、濁点/半濁点付きかな(例: が)を基底文字+結合
   文字(濁点)へ分解し、結合文字だけを取り除いて「清音化」する
3. 清音化後の文字列同士が完全一致すれば、濁点/半濁点の有無だけが異なる
   読みゆれと判定する

判定順序: 数字/否定チェック(既存、最優先)→完全一致の読み(既存
`_reading_equal`)→**新設: 濁点/半濁点だけが異なる読み
(`phonetic_uncertain`)**→固有名詞らしさ(既存`entity_like`)。
`entity_like`・`phonetic_uncertain`いずれかがTrueなら`cascade_eligible
=True`とし、Cascade対象の`ASR_VALIDATION_UNCERTAIN`へ分類する(TTS即
retryにしない)。脱落(delete)・追加(insert)はentity_likeと同様に対象
外とする(既存方針を踏襲)。

**単純な「頃」専用whitelistではない**: `_reading_equal_allowing_voicing`
は文字列そのものを見ておらず、清音化した読み文字列の比較のみで動作する
一般的なメカニズムである(6参照)。

**安全性の数学的根拠**: `cascade_eligible`(entity_like・phonetic_
uncertainいずれか)になった場合でも、`classify_ja_asr_match()`は常に
`should_pass=False`を返す設計であり(Part Bはこの設計に一切手を入れて
いない)、`should_pass=True`になるのは既存の完全一致読み(`_reading_
equal`)経由のみである。したがって、たとえ`phonetic_uncertain`判定が
(まれに)意味の異なる語同士を拾ってしまっても、**それが直接TTSの誤PASS
を引き起こすことは構造的にありえない**(Cascadeを尽くしてもHuman
Reviewへ回るだけで、内容が誤ったまま採用されることはない)。

### 6. 「漢字なら全部Cascade」になっていない証拠

[er007_ja_asr_validator_01_test.py](er007_ja_asr_validator_01_test.py)の`NOT_PHONETIC_UNCERTAIN_FIXTURES`で確認した。
「月」は名詞としての「つき」と暦月接尾の「がつ」という、清音化しても
一致しない**別のモーラ構成**の読みを持つ(頃のような連濁関係ではなく、
本質的に異なる語)。実際に`classify_ja_asr_match("...丸いつきを...",
"...丸い月を...")`は`TRUE_CONTENT_MISMATCH`のままであり、Cascadeへ
回らないことを確認した。またvoicing許容メカニズム自体の一般性は、
「頃」を一切含まない5組の合成ペア(か/が、さ/ざ、た/だ、は/ば、は/ぱの
各行)全てで`_reading_equal_allowing_voicing()`が期待通り動作すること
を直接検証し、逆に無関係語(ねこ/いぬ、かける/とめる)ではFalseのままで
あることも確認した。

### 7-11. Fixture結果

[er007_ja_asr_validator_01_test.py](er007_ja_asr_validator_01_test.py)、全26件のfixture+voicingメカニズム一般性確認7項目が期待通り(全PASS)。

| # | 項目 | 結果 |
|---|---|---|
| 7 | 頃/ころ(実データ) | `ASR_VALIDATION_UNCERTAIN`・`cascade_eligible=True`(TTS retryしない) |
| 8 | 頃/ごろ(逆方向) | `PHONETIC_MATCH`(既存の完全一致読み経路で解決、新ロジック不要な確認ケース) |
| 9 | 漢字↔ひらがな表記差 | 既存POSITIVE fixture(いす/椅子等)は無影響で全PASS継続。voicingメカニズム単体テスト5組も全PASS |
| 10 | 否定/数字/content wordのnegative fixture | 既存9件+新規2件(増えた/減った、15/50、いずれもタスク仕様の明示ケース)、計11件全て`TRUE_CONTENT_MISMATCH`のまま(cascade_eligible=Falseを個別確認) |
| 11 | true mismatch誤PASS 0件 | 全negative fixture(11件)・境界fixture(柿/鍵、月)で`should_pass=False`を個別確認、0件が誤PASSした |

**既知のトレードオフ(disclosure)**: 「柿(kaki)/鍵(kagi)」のように、
清音化すると偶然一致してしまう**意味の異なる実在語**のペアが理論上
存在する(`KNOWN_TRADEOFF_FIXTURES`で実際に確認)。この場合`TRUE_
CONTENT_MISMATCH`ではなく`ASR_VALIDATION_UNCERTAIN`(Cascade対象)に
なるが、5で述べた通り`should_pass`は常に`False`のままであるため
**誤PASSは発生しない**。実運用への影響は「本来即TTS retryで済んだはず
の稀なケースが、Cascade(追加ASR確認)を経由してからHuman Reviewへ
到達する」というコスト・latency増にとどまる。日本語の清音/濁音ペアで
かつ意味が異なる実在語(かき/かぎ等)は語彙全体の中でも比較的少数の
既知の例外パターンであり、今回の実データ96 segment中では該当ゼロ件
だった(下記Part E参照)。

## Part D: 実音声再検証

`verify_ja_cascade_production_on.py`(既存No.6 Delivery A2 previewの
実音声、新規TTSは呼ばない)を再実行した。

- **12. 実「頃」音声でCascadeへ進む証拠**: `cascade_invoked: True`。
  `base classification: ASR_VALIDATION_UNCERTAIN`(修正前は`TRUE_
  CONTENT_MISMATCH`だった、前回のsmoke test記録と比較して確認)。
  Primary#1→Primary#2→Secondary#1(Azure)→Secondary#2(Azure)の4段階
  全てが実際に実行され、いずれも「頃」表記で一貫して書き起こされた
  (TTS音声自体は一貫して同じ内容を発話しており、ランダムなASRノイズ
  ではなく読み変換の構造的な差であることも確認できた)
- **13. 実「頃」音声でTTS retry 0の証拠**: 4段階いずれも解決せず
  `human_review_required: True`・`stop_retrying: True`となり、
  `TTS regenerations in this verification: 0`(スクリプト自体がTTSを
  呼ばない設計に加え、Part Aの修正によりProduction側のretry loopも
  ここで正しく打ち切られることをmock testで別途確認済み)

## 14. regression test結果

`run_project_regression.py`: **1756/1757 PASS**(1件は既知のharness
自己テスト失敗`er003_test_bad.FixtureTests.test_case_0`で、harnessが
故意に`assertTrue(False)`する検証用fixtureであり実際の回帰ではない)。

新規追加した[er007_ja_tts_retry_path_fix_test_01.py](er007_ja_tts_retry_path_fix_test_01.py)(4件)が`er0*_test_*.py`のunittest discoveryへ
初めて実質的なテストを追加したことで、無関係な既存テストファイル
[er003_test_p2j_investigate.py](er003_test_p2j_investigate.py)の2件
(`test_combined_equals_sum_of_er002_and_er003`、`test_per_file_counts_
sum_matches_pattern_discovery`)が一時的に失敗した。これは2026-08頃の
別タスク(ER-003-P2J)が「`er0*_test_*.py`全体の件数はer002+er003の
2プレフィックスの合計と一致する」という、当時は正しかった前提を
ハードコードしていたためで、今回er007プレフィックスに初めて実質的な
unittest.TestCaseが追加されたことで前提が崩れた。**過去の凍結値
(P2H:1032、P2I:660、P2J current_head:1117等)を検証する
`HistoricalRecordIntegrityTests`は無変更・無影響**(保存済みJSONを
読むだけで再計算しないため)。影響したのは「現在のlive件数」を検証する
`CollectionCountTests`/`PerFileCountsTests`のみで、決め打ちの2項合計を
実際に存在するprefix集合からの動的合計へ一般化する形で修正し、
regressionを1756/1757(既知の1件除き全PASS)へ復旧した。

## 15. 新規API Cost

新規TTS呼び出しは0件。実音声smoke test再実行で、既存WAVファイル8件に
対しASR呼び出しのみ実施(OpenAI Primary#1×8 + 「頃」segmentのCascade分
[Primary#2・Azure Secondary#1・#2]×3 = 計11回のASR呼び出し、数十円未満)。

## 16. 回避可能TTS Cost(counterfactual、[er007_ja_tts_retry_path_fix_cost_01.py](er007_ja_tts_retry_path_fix_cost_01.py))

No.1〜6の既存96 Japanese segment(実測ログの`asr_text`を再利用、新規
API呼び出しなし)で、経路A・経路Bそれぞれの影響を算出した。

**経路B(実測ベースの下限見積り)**: 旧分類では`TRUE_CONTENT_MISMATCH`
だったが新分類では`ASR_VALIDATION_UNCERTAIN`になったsegmentは
**2/96件**(No.5・No.6のA2 preview、いずれも同一の「ころ/頃」パターン)。
誤分類1件あたり平均1回の無駄なTTS+検証ASRが発生していたと仮定すると、
回避可能だったcostは TTS ¥0.032 + 検証ASR ¥0.433 = **¥0.465**(下限、
実際は同一誤分類が複数attemptで繰り返された可能性もあり、これより
大きい場合もある)。

**経路A(worst-case見積り、実測ではない)**: このbugは今Session内で
新規配線されたCascade呼び出しに内在しており、Production実運用ログには
まだ現れていない(配線直後に本タスクで発見・修正したため)。Cascade
対象(`ASR_VALIDATION_UNCERTAIN`)になるsegment2件全てが、修正前の
voice01.py/n3_01.pyの自前ループで`max_attempts`(既定6)回全てを無駄に
消費していたと仮定した上限見積りは、追加TTS再生成**最大10回**、
TTS cost上限¥0.158、検証ASR cost上限¥28.367。

**経路B修正による新規追加ASRコスト(Cascade起動分、worst-case)**:
2件がCascadeの4段階全てを消費したと仮定すると¥5.241。回避したTTS+
検証ASR cost(¥0.465)と比べると、**金額単体では純増**という結果に
なった。ただしこの比較はドル換算のみを見ており、Part Bが実際に守って
いる価値(すでに正しかった音声を、誤判定によって無駄に再生成・破棄
するリスクの回避、TTS Batch job 1回あたり実測91〜167秒の待ち時間削減)
は金額に現れない。今回の実データでは該当2件とも小さいkey/preview
segmentであり影響は軽微だが、方針としては「金額だけでなく、既に正しい
音声を無駄に壊さないこと」を優先する判断とした。

## 17. 残存Open Item

- 「かき/かぎ」のような、清音化後に偶然一致する意味の異なる実在語
  ペアが理論上Cascadeへ余分に回りうる(誤PASSはしない、5参照)。今回の
  実データ96segment中は該当なし
- 「頃/ころ」パターンは、No.5・No.6のA2 preview両方で同一の言い回し
  (「〜ころには」)から発生している。A2 previewのWriter Prompt自体が
  この言い回しを再利用しやすい構造の場合、今後の新規Topicでも同じ
  パターンが繰り返し出現する可能性がある(Writer側のspoken text自体を
  変更する対応はPart Bの非対象事項のため見送り)
- OpenAI mini日本語ASR品質確認のサンプル数(n=14、前タスクより継続)は
  引き続き小さく、より大規模なサンプルでの継続監視が望ましい

## 非対象・STOP条件

ASR provider変更、Cascade回数変更、Japanese TTS segment分割、TTS model
変更、English Validator変更、No.7生成、Evidence Compression変更、いずれも
実施していない。

STOP条件(読み揺れ判定を広げることでtrue content mismatchを誤PASSする/
否定・数字・重要語差がCascadeへ誤って流れる/修正後もstop_retrying=True
の後にTTSが再生成される/「頃」等のreading normalizationを安全に一般化
できない)はいずれも該当しなかった。

完了後STOPする。
